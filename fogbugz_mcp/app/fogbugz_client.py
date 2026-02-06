import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import re
from html import unescape
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import json
import ast
import time
import xmltodict


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def xml_to_dict(elem: ET.Element) -> Any:
    """
    Robust XML → Python converter for FogBugz payloads.

    Rules:
    - Attributes preserved with '@' prefix
    - Repeated child tags become lists
    - Empty tags preserved as empty strings
    - CDATA preserved verbatim
    """

    result: dict[str, Any] = {}

    # Attributes
    for k, v in elem.attrib.items():
        result[f"@{k}"] = v

    children = list(elem)

    # Leaf node
    if not children:
        text = elem.text or ""
        text = text.strip()
        if result:
            result["#text"] = text
            return result
        return text

    # Child nodes
    for child in children:
        value = xml_to_dict(child)
        tag = child.tag

        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value

    return result


def extract_collection(parsed: dict, container: str, item: str) -> Optional[list[dict]]:
    """
    Extracts repeating FogBugz collections:
    cases/case, projects/project, events/event, etc.
    """
    try:
        response = parsed.get("response", {})
        block = response.get(container)
        if not block:
            return None

        items = block.get(item)
        if not items:
            return None

        if isinstance(items, dict):
            return [items]

        return items
    except Exception:
        return None


def enrich_fogbugz(parsed: dict) -> dict:
    enriched: dict[str, Any] = {}

    collections = [
        ("cases", "case"),
        ("projects", "project"),
        ("areas", "area"),
        ("events", "event"),
        ("minievents", "event"),
        ("people", "person"),
        ("fixfors", "fixfor"),
        ("categories", "category"),
        ("priorities", "priority"),
        ("statuses", "status"),
        ("tags", "tag"),
        ("wikis", "wiki"),
        ("articles", "article"),
        ("filters", "filter"),
        ("mailboxes", "mailbox"),
        ("discussions", "discussion"),
        ("checkins", "checkin"),
    ]

    for container, item in collections:
        data = extract_collection(parsed, container, item)
        if data is not None:
            enriched[container] = data

    return enriched


def parse_fogbugz_xml(xml_text: str) -> dict:
    """
    Best-effort FogBugz XML handler.
    - Never throws
    - Always returns raw XML
    """

    result = {
        "parsed": None,
        "raw_xml": xml_text,
        "enriched": {},
        "warnings": [],
    }

    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        result["warnings"].append(f"Invalid XML: {e}")
        return result

    try:
        parsed = {root.tag: xml_to_dict(root)}
        result["parsed"] = parsed
    except Exception as e:
        result["warnings"].append(f"XML parse failure: {e}")
        return result

    try:
        result["enriched"] = enrich_fogbugz(parsed)
    except Exception as e:
        result["warnings"].append(f"Enrichment failed: {e}")

    return result


def _get_text(parent: ET.Element, tag: str) -> Optional[str]:
    """Safely extract text from a child tag."""
    el = parent.find(tag)
    # add custom handling for HTML with urls in images, they should be removed to avoid confusion in the LLM output, but we want to preserve the alt text if available
    if el is not None and el.text:
        # Remove image URLs but keep alt text if present
        el_text = el.text.strip()
        el_text = re.sub(
            r'<img([^>]*?)src=(["\']).*?\2',
            r"<img\1src=\2[image]\2",
            el_text,
            flags=re.IGNORECASE,
        )

        return el_text
    return None


class FogBugzClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        # Cache: List of all known articles
        self._all_articles: List[Dict[str, Any]] = []
        self._cache_built = False

    def _request(self, cmd: str, **params) -> str:
        params.update(
            {
                "cmd": cmd,
                "token": self.token,
            }
        )
        # remove params with None values to avoid confusion in the API
        params = {k: v for k, v in params.items() if v is not None}
        # large timeout for listing all wikis/articles if needed
        response = httpx.get(
            f"{self.base_url}/api.asp",
            params=params,
            timeout=120,
        )
        response.raise_for_status()
        return response.text

    # -----------------------------
    # Wikis
    # -----------------------------

    def list_wikis(self) -> List[Dict]:
        response_xml = self._request("listWikis")
        root = ET.fromstring(response_xml)
        wikis_node = root.find("wikis")
        if wikis_node is None:
            return []

        results = []
        for wiki in wikis_node.findall("wiki"):
            f_deleted = wiki.findtext("fDeleted", default="false")
            if parse_bool(f_deleted):
                continue

            results.append(
                {
                    "wiki_id": int(wiki.findtext("ixWiki")),
                    "name": wiki.findtext("sWiki", default="").strip(),
                    "tagline": wiki.findtext("sTagLineHTML", default="").strip(),
                    "root_page_id": int(wiki.findtext("ixWikiPageRoot")),
                }
            )
        return results

    # -----------------------------
    # Articles
    # -----------------------------

    def list_articles(self, wiki_id: int) -> List[Dict[str, Any]]:
        response_xml = self._request("listArticles", ixWiki=wiki_id)
        root = ET.fromstring(response_xml)
        articles_node = root.find("articles")
        if articles_node is None:
            return []

        articles = []
        for article in articles_node.findall("article"):
            ixWikiPage = article.findtext("ixWikiPage")
            sHeadline = article.findtext("sHeadline")
            if ixWikiPage and sHeadline:
                articles.append(
                    {
                        "article_id": int(ixWikiPage),
                        "title": sHeadline.strip(),
                    }
                )
        return articles

    def _clean_html_for_parsing(self, html_content: str) -> str:
        """Pre-process HTML to handle special cases before BeautifulSoup parsing."""
        # Remove display:none spans that wrap code snippets (they're just wrappers)
        html_content = re.sub(
            r'<span\s+style="display:\s*none">\s*&nbsp;\s*</span>', "", html_content
        )
        return html_content

    def _normalize_newlines(self, text: str) -> str:
        """Convert all newline variants to actual newlines."""
        # Handle literal \r\n, \r, \n strings
        text = text.replace("\\r\\n", "\n")
        text = text.replace("\\r", "\n")
        text = text.replace("\\n", "\n")
        # Handle actual carriage returns
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        return text

    def _parse_plugin_data(self, plugin_data_str: str) -> dict:
        """Parse plugin_data which can be in various formats."""
        # First, unescape HTML entities
        plugin_data_str = unescape(plugin_data_str)

        # Try standard JSON first
        try:
            return json.loads(plugin_data_str)
        except json.JSONDecodeError:
            pass

        # Try with ast.literal_eval for Python dict syntax
        try:
            return ast.literal_eval(plugin_data_str)
        except (ValueError, SyntaxError):
            pass

        # Last resort: manual regex extraction for sContent
        # This handles malformed JSON with escaped quotes and newlines
        match = re.search(
            r"['\"]sContent['\"]\s*:\s*['\"](.*)['\"]\s*[,}]",
            plugin_data_str,
            re.DOTALL,
        )
        if match:
            content = match.group(1)

            # Normalize newlines
            content = self._normalize_newlines(content)

            # Unescape common patterns
            content = content.replace(r"\"", '"')
            content = content.replace(r"\'", "'")
            content = content.replace("&quot;", '"')
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace("&amp;", "&")

            return {"sContent": content}

        return {}

    def _extract_code_snippets(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Extract code snippets from FogBugz plugin input tags."""
        input_tags = soup.find_all("input", {"plugin_type": "codesnippet"})

        for input_tag in input_tags:
            try:
                # Get the plugin_data attribute
                plugin_data_str = input_tag.get("plugin_data", "")
                if not plugin_data_str:
                    input_tag.decompose()
                    continue

                # Parse the plugin data
                plugin_data = self._parse_plugin_data(plugin_data_str)

                # Extract the code content
                code_content = plugin_data.get("sContent", "")
                if not code_content:
                    print(f"[SERVER] Warning: No sContent in plugin_data")
                    input_tag.decompose()
                    continue

                # Detect language from content
                code_language = self._detect_code_language(code_content)

                # Create a proper code block with language hint
                code_block = soup.new_tag("pre")
                code_tag = soup.new_tag("code")
                code_tag["class"] = f"language-{code_language}"
                code_tag.string = code_content
                code_block.append(code_tag)

                # Replace the input tag with the code block
                input_tag.replace_with(code_block)
                print(
                    f"[SERVER] ✓ Extracted code snippet ({code_language}, {len(code_content)} chars)"
                )

            except Exception as e:
                print(f"[SERVER] Warning: Failed to process code snippet: {e}")
                # Remove the problematic input tag
                input_tag.decompose()

        return soup

    def _detect_code_language(self, code: str) -> str:
        """Simple heuristic to detect code language."""
        code_lower = code.lower().strip()

        # Check for XML/SOAP
        if (
            code_lower.startswith("<?xml")
            or "<s:envelope" in code_lower
            or "<soap:" in code_lower
        ):
            return "xml"

        # Check for JSON
        if (code_lower.startswith("{") or code_lower.startswith("[")) and (
            '"' in code or "'" in code
        ):
            return "json"

        # Check for HTTP requests
        if (
            code_lower.startswith("post ")
            or code_lower.startswith("get ")
            or code_lower.startswith("put ")
            or code_lower.startswith("delete ")
        ):
            return "http"

        # Check for C#
        if any(
            keyword in code
            for keyword in [
                "using System",
                "namespace ",
                "class ",
                "new ",
                "//Instantiate",
                "List<",
                "Console.WriteLine",
            ]
        ):
            return "csharp"

        # Check for Python
        if any(
            keyword in code
            for keyword in ["import ", "def ", "class ", "print(", "from "]
        ):
            return "python"

        # Check for JavaScript
        if any(
            keyword in code
            for keyword in ["function ", "const ", "let ", "var ", "=>", "console.log"]
        ):
            return "javascript"

        # Check for SQL
        if any(
            keyword in code_lower
            for keyword in [
                "select ",
                "insert ",
                "update ",
                "delete from",
                "create table",
            ]
        ):
            return "sql"

        # Default
        return "text"

    def _clean_inline_styles(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove inline styles from span tags to clean up markdown conversion."""
        for span in soup.find_all("span"):
            # Remove style attribute
            if span.has_attr("style"):
                del span["style"]
            # Unwrap spans that have no other attributes
            if not span.attrs:
                span.unwrap()
        return soup

    def _convert_tables_to_markdown(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Convert HTML tables to Markdown tables."""
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            md_table = []

            for i, row in enumerate(rows):
                # Get all cells (both th and td)
                cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
                if not cols:
                    continue

                # Escape pipe characters in cell content
                cols = [col.replace("|", "\\|") for col in cols]

                # Create markdown row
                md_row = "| " + " | ".join(cols) + " |"
                md_table.append(md_row)

                # Add separator after first row (header)
                if i == 0:
                    md_table.append("| " + " | ".join(["---"] * len(cols)) + " |")

            # Replace table with markdown version
            if md_table:
                table.replace_with("\n\n" + "\n".join(md_table) + "\n\n")
            else:
                table.decompose()

        return soup

    def view_article(self, article_id: int) -> Dict:
        print(f"[SERVER] Fetching content for Article ID: {article_id}")
        try:
            response_xml = self._request("viewArticle", ixWikiPage=article_id)
            root = ET.fromstring(response_xml)
            page = root.find("wikipage")
            if page is None:
                raise RuntimeError(f"No wikipage found for article_id={article_id}")

            title = page.findtext("sHeadline", default="").strip()
            content_html = page.findtext("sBody", default="").strip()

            # Extract tags
            tags = []
            tags_node = page.find("tags")
            if tags_node:
                for tag in tags_node.findall("tag"):
                    if tag.text:
                        tags.append(tag.text.strip())

            # Pre-process HTML
            content_html = self._clean_html_for_parsing(content_html)

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content_html, "html.parser")

            # Extract code snippets from FogBugz plugin inputs FIRST
            # (do this before table conversion so code blocks don't interfere)
            soup = self._extract_code_snippets(soup)

            # Clean inline styles (font-size, etc.)
            soup = self._clean_inline_styles(soup)

            # Convert HTML tables to Markdown tables
            soup = self._convert_tables_to_markdown(soup)

            # Convert remaining HTML to Markdown
            content_md = md(str(soup), heading_style="ATX", strip=["span"])

            # Clean up excessive newlines and whitespace
            content_md = re.sub(r"\n{3,}", "\n\n", content_md)
            content_md = re.sub(
                r" +", " ", content_md
            )  # Multiple spaces to single space
            content_md = content_md.strip()

            return {
                "article_id": article_id,
                "title": title,
                "content": content_md,
                "tags": tags,
            }

        except Exception as e:
            print(f"[SERVER] Error viewing article {article_id}: {e}")
            import traceback

            traceback.print_exc()
            raise

    def list_projects(self) -> List[Dict[str, Any]]:
        response_xml = self._request("listProjects")
        root = ET.fromstring(response_xml)

        projects_node = root.find("projects")
        if projects_node is None:
            return []

        projects = []
        for project in projects_node.findall("project"):
            if project.findtext("fDeleted", "false").lower() == "true":
                continue

            projects.append(
                {
                    "project_id": int(project.findtext("ixProject")),
                    "name": project.findtext("sProject", "").strip(),
                }
            )

        return projects

    def list_areas(self, project_id: int) -> List[Dict[str, Any]]:
        response_xml = self._request("listAreas", q=project_id)
        root = ET.fromstring(response_xml)

        areas_node = root.find("areas")
        if areas_node is None:
            return []

        areas = []
        for area in areas_node.findall("area"):
            # Skip documentation-only areas (optional but recommended)
            if area.findtext("cDoc", "0") == "1":
                continue

            person_owner = area.findtext("sPersonOwner", "").strip()

            areas.append(
                {
                    "area_id": int(area.findtext("ixArea")),
                    "name": area.findtext("sArea", "").strip(),
                    "project_id": int(area.findtext("ixProject")),
                    "person_owner": person_owner or None,
                }
            )

        return areas

    def search_cases_by_project_and_area(
        self, project_name: str, area_name: str, max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Search FogBugz cases by project and area using search query.
        """

        query = f'Project:"{project_name}" Area:"{area_name}"'

        response_xml = self._request(
            "search",
            q=query,
            cols="ixBug,sTitle,sStatus,sPersonAssignedTo,sPriority,sProject,sCategory",
            # max=max_results
        )

        root = ET.fromstring(response_xml)
        cases_node = root.find("cases")

        if cases_node is None:
            return {"total_hits": 0, "cases": []}

        total_hits = int(cases_node.attrib.get("totalHits", "0"))

        cases = []
        for case in cases_node.findall("case"):
            cases.append(
                {
                    "case_id": int(case.attrib["ixBug"]),
                    "title": case.findtext("sTitle", "").strip(),
                    "status": case.findtext("sStatus", "").strip(),
                    "assigned_to": case.findtext("sPersonAssignedTo", "").strip()
                    or None,
                    "priority": case.findtext("sPriority", "").strip(),
                    "project": case.findtext("sProject", "").strip(),
                    "category": case.findtext("sCategory", "").strip(),
                }
            )

        return {"total_hits": total_hits, "cases": cases}

    def advanced_search(
        self,
        query: str,
        max_results: Optional[int] = None,
        cols: Optional[str] = None,
    ) -> dict:
        """
        Executes an advanced FogBugz search.

        Parameters:
        - query: Full FogBugz search string (axes, dates, ORs, wildcards, etc.)
        - max_results: Optional limit on number of cases returned
        - cols: Optional comma-separated list of columns to return (e.g., "sTitle,sStatus")

        Returns:
        - result_xml: Raw XML response from FogBugz (always returned, even on error)
        """

        try:
            xml = self._request("search", q=query, max=max_results, cols=cols)
            return xml
        except Exception as e:
            return {
                "parsed": None,
                "raw_xml": None,
                "enriched": {},
                "warnings": [f"Request failed: {e}"],
            }

    def parse_fogbugz_case_response(self, case_id: str) -> Dict[str, Any]:
        """
        Parse FogBugz case XML response into a structured dictionary.

        Returns:
            {
                "count": int,
                "total_hits": int,
                "cases": [
                    {
                        "ixBug": str,
                        "operations": List[str],
                        "title": str,
                        "status": str,
                        "assigned_to": str,
                        "priority": str,
                        "project": str,
                        "category": str,
                        "events": [
                            {
                                "ixBugEvent": str,
                                "event_type": int,
                                "verb": str,
                                "actor_person_id": str,
                                "assigned_to_person_id": str,
                                "datetime": str,
                                "text": str,
                                "html": str,
                                "description": str,
                                "actor_name": str,
                                "changes": str
                            }
                        ]
                    }
                ]
            }
        """

        xml_response = self._request(
            "search",
            q=f"ixBug:{case_id}",
            cols="sTitle,sStatus,sPersonAssignedTo,sPriority,sProject,sCategory,events",
        )
        root = ET.fromstring(xml_response)

        cases_node = root.find("cases")
        if cases_node is None:
            return {"count": 0, "total_hits": 0, "cases": []}

        cases = []
        for case in cases_node.findall("case"):
            case_data = {
                "ixBug": case.attrib.get("ixBug"),
                "operations": case.attrib.get("operations", "").split(","),
                "title": _get_text(case, "sTitle"),
                "status": _get_text(case, "sStatus"),
                "assigned_to": _get_text(case, "sPersonAssignedTo"),
                "priority": _get_text(case, "sPriority"),
                "project": _get_text(case, "sProject"),
                "category": _get_text(case, "sCategory"),
                "events": [],
            }

            events_node = case.find("events")
            if events_node is not None:
                for event in events_node.findall("event"):
                    event_data = {
                        "ixBugEvent": _get_text(event, "ixBugEvent"),
                        "event_type": int(_get_text(event, "evt") or 0),
                        "verb": _get_text(event, "sVerb"),
                        "actor_person_id": _get_text(event, "ixPerson"),
                        "assigned_to_person_id": _get_text(event, "ixPersonAssignedTo"),
                        "datetime": _get_text(event, "dt"),
                        "text": _get_text(event, "s"),
                        "html": _get_text(event, "sHtml"),
                        "description": _get_text(event, "evtDescription"),
                        "actor_name": _get_text(event, "sPerson"),
                        "changes": _get_text(event, "sChanges"),
                    }
                    case_data["events"].append(event_data)

            cases.append(case_data)

        return {
            "count": int(cases_node.attrib.get("count", 0)),
            "total_hits": int(cases_node.attrib.get("totalHits", 0)),
            "cases": cases,
        }
