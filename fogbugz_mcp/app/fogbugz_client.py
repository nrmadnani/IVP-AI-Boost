import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import re
from html import unescape
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import json
import ast
import time

def parse_bool(value: str) -> bool:
    return value.lower() == "true"

class FogBugzClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        # Cache: List of all known articles
        self._all_articles: List[Dict[str, Any]] = []
        self._cache_built = False

    def _request(self, cmd: str, **params) -> str:
        params.update({
            "cmd": cmd,
            "token": self.token,
        })
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
        if wikis_node is None: return []

        results = []
        for wiki in wikis_node.findall("wiki"):
            f_deleted = wiki.findtext("fDeleted", default="false")
            if parse_bool(f_deleted): continue

            results.append({
                "wiki_id": int(wiki.findtext("ixWiki")),
                "name": wiki.findtext("sWiki", default="").strip(),
                "tagline": wiki.findtext("sTagLineHTML", default="").strip(),
                "root_page_id": int(wiki.findtext("ixWikiPageRoot")),
            })
        return results

    # -----------------------------
    # Articles
    # -----------------------------

    def list_articles(self, wiki_id: int) -> List[Dict[str, Any]]:
        response_xml = self._request("listArticles", ixWiki=wiki_id)
        root = ET.fromstring(response_xml)
        articles_node = root.find("articles")
        if articles_node is None: return []

        articles = []
        for article in articles_node.findall("article"):
            ixWikiPage = article.findtext("ixWikiPage")
            sHeadline = article.findtext("sHeadline")
            if ixWikiPage and sHeadline:
                articles.append({
                    "article_id": int(ixWikiPage),
                    "title": sHeadline.strip(),
                })
        return articles


    def _clean_html_for_parsing(self, html_content: str) -> str:
        """Pre-process HTML to handle special cases before BeautifulSoup parsing."""
        # Remove display:none spans that wrap code snippets (they're just wrappers)
        html_content = re.sub(r'<span\s+style="display:\s*none">\s*&nbsp;\s*</span>', '', html_content)
        return html_content

    def _normalize_newlines(self, text: str) -> str:
        """Convert all newline variants to actual newlines."""
        # Handle literal \r\n, \r, \n strings
        text = text.replace('\\r\\n', '\n')
        text = text.replace('\\r', '\n')
        text = text.replace('\\n', '\n')
        # Handle actual carriage returns
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
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
        match = re.search(r"['\"]sContent['\"]\s*:\s*['\"](.*)['\"]\s*[,}]", plugin_data_str, re.DOTALL)
        if match:
            content = match.group(1)
            
            # Normalize newlines
            content = self._normalize_newlines(content)
            
            # Unescape common patterns
            content = content.replace(r'\"', '"')
            content = content.replace(r"\'", "'")
            content = content.replace('&quot;', '"')
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace('&amp;', '&')
            
            return {'sContent': content}
        
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
                code_tag['class'] = f'language-{code_language}'
                code_tag.string = code_content
                code_block.append(code_tag)
                
                # Replace the input tag with the code block
                input_tag.replace_with(code_block)
                print(f"[SERVER] ✓ Extracted code snippet ({code_language}, {len(code_content)} chars)")
                
            except Exception as e:
                print(f"[SERVER] Warning: Failed to process code snippet: {e}")
                # Remove the problematic input tag
                input_tag.decompose()
        
        return soup

    def _detect_code_language(self, code: str) -> str:
        """Simple heuristic to detect code language."""
        code_lower = code.lower().strip()
        
        # Check for XML/SOAP
        if code_lower.startswith('<?xml') or '<s:envelope' in code_lower or '<soap:' in code_lower:
            return 'xml'
        
        # Check for JSON
        if (code_lower.startswith('{') or code_lower.startswith('[')) and ('"' in code or "'" in code):
            return 'json'
        
        # Check for HTTP requests
        if code_lower.startswith('post ') or code_lower.startswith('get ') or code_lower.startswith('put ') or code_lower.startswith('delete '):
            return 'http'
        
        # Check for C#
        if any(keyword in code for keyword in ['using System', 'namespace ', 'class ', 'new ', '//Instantiate', 'List<', 'Console.WriteLine']):
            return 'csharp'
        
        # Check for Python
        if any(keyword in code for keyword in ['import ', 'def ', 'class ', 'print(', 'from ']):
            return 'python'
        
        # Check for JavaScript
        if any(keyword in code for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            return 'javascript'
        
        # Check for SQL
        if any(keyword in code_lower for keyword in ['select ', 'insert ', 'update ', 'delete from', 'create table']):
            return 'sql'
        
        # Default
        return 'text'

    def _clean_inline_styles(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove inline styles from span tags to clean up markdown conversion."""
        for span in soup.find_all('span'):
            # Remove style attribute
            if span.has_attr('style'):
                del span['style']
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
                cols = [col.replace('|', '\\|') for col in cols]
                
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
            content_md = md(str(soup), heading_style="ATX", strip=['span'])
            
            # Clean up excessive newlines and whitespace
            content_md = re.sub(r'\n{3,}', '\n\n', content_md)
            content_md = re.sub(r' +', ' ', content_md)  # Multiple spaces to single space
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