import os
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from fogbugz_mcp.app.fogbugz_client import FogBugzClient

load_dotenv()

FOGBUGZ_URL = os.getenv("FOGBUGZ_URL")
FOGBUGZ_TOKEN = os.getenv("FOGBUGZ_TOKEN")

if not FOGBUGZ_URL or not FOGBUGZ_TOKEN:
    raise RuntimeError("FOGBUGZ_URL and FOGBUGZ_TOKEN must be set")

client = FogBugzClient(
    base_url=FOGBUGZ_URL,
    token=FOGBUGZ_TOKEN,
)

mcp = FastMCP(
    name="FogBugz Documentation MCP",
    instructions=(
        "This MCP server provides comprehensive access to IVP (Indus Valley Partners) Company's FogBugz system. "
        
        "**Documentation & Wiki Access:**\n"
        "- Use `list_wikis` to discover documentation spaces/wikis\n"
        "- Use `list_articles` to list articles within a specific wiki (requires wiki_id from list_wikis)\n"
        "- Use `view_article` to get detailed content for a specific article (requires article_id from list_articles)\n"
        
        "**Project & Organization:**\n"
        "- Use `list_projects` to get all active FogBugz projects\n"
        "- Use `list_areas` to get areas within a specific project (requires project_id)\n"
        
        "**Case Search & Investigation:**\n"
        "- Use `search_cases_by_project_and_area` to find cases using human-readable project and area names\n"
        "- Use `advanced_search` for complex queries using native FogBugz search syntax (supports query, max_results, cols parameters)\n"
        "- Use `get_events_of_a_case` to retrieve detailed event history and current status of a specific case (requires case_id)\n"
        
        "**Utilities:**\n"
        "- Use `ping` to test server connectivity\n"
        
        "**Workflow Tips:**\n"
        "- For wikis: list_wikis → list_articles → view_article\n"
        "- For cases: list_projects → list_areas → search_cases_by_project_and_area or advanced_search → get_events_of_a_case\n"
        "- The get_events_of_a_case tool provides granular event history including who did what and when, useful for understanding case context and progression"
    ),
)

# -----------------------------
# Tools
# -----------------------------

@mcp.tool()
def list_wikis():
    """
    List all active FogBugz wiki spaces.
    Returns:
      - wiki_id
      - name
      - tagline
      - root_page_id
    """
    return client.list_wikis()


@mcp.tool()
def ping():
    """
    Simple connectivity test.
    """
    return "pong"


@mcp.tool()
def list_articles(wiki_id: int):

    """
    List articles within a specific wiki.
    
    Input:
      - wiki_id: integer (from list_wikis)
    
    Returns:
      - article_id (used for view_article)
      - article_description
      - wiki_page
    """
    return client.list_articles(wiki_id)


@mcp.tool()
def view_article(article_id: int):

    """
    Retrieve the full content of a FogBugz article.
    
    Input:
      - article_id: integer (from list_articles)
    
    Returns:
      - article_id
      - title
      - content
      - revision
      - tags
    """
    return client.view_article(article_id)

@mcp.tool()
def list_projects():
    """
    List all active FogBugz projects.

    Returns:
      - project_id: integer
      - name: project name
    """
    return client.list_projects()


@mcp.tool()
def list_areas(project_id: int):
    """
    List all areas for a given FogBugz project.

    Args:
      project_id: FogBugz project ID

    Returns:
      Areas belonging to the project, including ownership metadata.
    """
    return {
        "project_id": project_id,
        "areas": client.list_areas(project_id),
    }


@mcp.tool()
def search_cases_by_project_and_area(project_name: str, area_name: str):
    """
    List FogBugz cases for a given project and area using search.

    Args:
      project_name: Project name (human readable)
      area_name: Area name (human readable)

    Returns:
      Matching cases with metadata for relevance ranking.
    """
    result = client.search_cases_by_project_and_area(project_name, area_name)
    return {
        "project": project_name,
        "area": area_name,
        "total_hits": result["total_hits"],
        "cases": result["cases"],
    }


@mcp.tool()
def advanced_search(
    query: str,
    max_results: Optional[int] = None,
    cols: Optional[str] = None
):
    """
    Execute a FogBugz advanced search using native FogBugz search syntax.

    Input:
      - query: Raw FogBugz advanced search query (passed verbatim)
      - max_results: Optional limit on number of cases returned
      - cols: Optional comma-separated list of columns to return (e.g., "sTitle,sStatus")

    Returns:
      - raw_xml: FogBugz XML response (always returned, even on error)
      - query: The original query string (for reference)
    """
    try:
        xml_response = client.advanced_search(
            query=query,
            max_results=max_results,
            cols=cols
        )
        return {
            "query": query,
            "raw_xml": xml_response,
        }
    except Exception as e:
        # Absolute fallback: never lose FogBugz output
        return {
            "query": query,
            "error": str(e),
        }



@mcp.tool()
def get_events_of_a_case(case_id: str):
    """
    Returns granular information of what happened within a case, i.e., all events and current status of the case. 
    This is useful for understanding the history and context of a case.


    Input:
      - case_id: str (FogBugz case ID)

    Returns:
      - Parsed structure:
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
    try:
        parsed_data = client.parse_fogbugz_case_response(case_id)
        print(type(parsed_data))
        return parsed_data
    except Exception as e:
        return {"error": f"Failed to parse FogBugz XML: {str(e)}"}

def main():
    # Run MCP server using stdio transport
    print("Starting FogBugz MCP server")
    mcp.run(transport="stdio")



if __name__ == "__main__":
    main()


