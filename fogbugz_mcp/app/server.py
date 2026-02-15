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
    instructions=("This MCP server provides comprehensive access to IVP (Indus Valley Partners) Company's FogBugz system. "
        
        "**Documentation & Wiki Access:**\n"
        "- Use `list_wikis` to discover documentation spaces/wikis\n"
        "- Use `list_articles` to list articles within a specific wiki (requires wiki_id from list_wikis)\n"
        "- Use `view_article` to get detailed content for a specific article (requires article_id from list_articles)\n"
        
        "**Project & Organization:**\n"
        "- Use `list_projects` to get all active FogBugz projects\n"
        "- Use `list_areas` to get areas within a specific project (requires project_id)\n"
        "- Use `list_categories` to get all case categories (Bug, Feature, Task, etc.)\n"
        "- Use `list_priorities` to get all case priority levels (Blocker, Critical, Major, etc.)\n"
        "- Use `list_tags` to get all available tags with usage statistics, quick keyword based lookups\n"
        "- Use `list_people` to get all active users/people in the system (person_id, full_name, email)\n"
        "- Use `get_person_id_by_email` to lookup a person's ID by their email address\n"
        "- Use `list_filters` to get all saved project-based filters for querying specific case sets\n"
        
        "**Case Search & Investigation:**\n"
        "- Use `search_cases_by_project_and_area` to find cases using human-readable project and area names\n"
        "- Use `advanced_search` for complex queries using native FogBugz search syntax (supports query, max_results, cols parameters) - **RECOMMENDED PRIMARY APPROACH**\n"
        "- Use `list_cases` to retrieve all cases for a saved filter (max 10,000 cases, use with caution)\n"
        "- Use `get_events_of_a_case` to retrieve detailed event history and current status of a specific case (requires case_id)\n"
        
        "**Utilities:**\n"
        "- Use `ping` to test server connectivity\n"
        
        "**Advanced Search Syntax Reference:**\n"
        "FogBugz advanced_search supports powerful query construction. Key syntax:\n"
        "\n"
        "**Boolean Operators:**\n"
        "- AND (implicit): 'apple peach' finds cases with both terms\n"
        "- OR: 'apple OR peach' finds cases with either term\n"
        "- NOT: 'apple -peach' finds cases with apple but not peach\n"
        "- Phrases: '\"apple peach\"' finds exact phrase\n"
        "- Wildcards: 'pear*' finds words starting with pear (1+ chars)\n"
        "- Grouping: Use parentheses for complex logic\n"
        "\n"
        "**Common Search Axes (use axis:value format):**\n"
        "- Project:'Project Name' - cases in specific project\n"
        "- Area:'Area Name' - cases in specific area\n"
        "- AssignedTo:'user' - cases assigned to user\n"
        "- Status:'Active' or Status:'open' or Status:'closed'\n"
        "- Category:'Bug' or 'Feature' or 'Inquiry'\n"
        "- Priority:'Critical' or 'Major'\n"
        "- Title:'search terms' - search in case titles\n"
        "- Tag:'tag-name' - cases with specific tag\n"
        "- Opened:'date' - cases opened on date\n"
        "- Edited:'date' - cases modified on date\n"
        "- Due:'date' - cases due on date\n"
        "- OpenedBy:'user' - cases opened by user\n"
        "- EditedBy:'user' - cases edited by user\n"
        "- Milestone:'milestone name' - cases in milestone\n"
        "- Attachment:'filename' - cases with specific attachment\n"
        "\n"
        "**Date Syntax:**\n"
        "- Specific: 'edited:\"3/26/2007\"' or 'edited:\"March 2007\"'\n"
        "- Ranges: 'edited:\"3/26/2007..6/8/2007\"'\n"
        "- Relative: 'edited:\"today\"', 'edited:\"yesterday\"', 'edited:\"last week\"'\n"
        "- Open ranges: 'opened:\"1/14/2011..\"' (after date), 'due:\"..10/10/2012\"' (before date)\n"
        "- Time-relative: 'opened:\"-3w..-1w\"' (1-3 weeks ago), 'closed:\"-30m..now\"' (last 30 mins)\n"
        "\n"
        "**Wildcards & Negation:**\n"
        "- tag:* finds cases with any tags\n"
        "- -tag:* finds cases with no tags\n"
        "- -title:pear excludes cases with 'pear' in title\n"
        "\n"
        "**Important Notes:**\n"
        "- Stemming: 'hiking' matches 'hike', 'hiking', 'hiker'. Use wildcard to avoid: 'hikin*'\n"
        "- Quotes needed for phrases with spaces: Project:'400 Capital'\n"
        "- Substring matching: Project:Widget matches both 'Widget Factory' and 'Widget Distributor'\n"
        "- Exact ID match: Use := operator, e.g., project:=1 for exact project ID\n"
        "- OR has lower priority than AND: use parentheses for clarity\n"
        "\n"
        "**Example Queries:**\n"
        "- Project:'400 Capital' Status:open - all open cases in 400 Capital\n"
        "- Project:'Cerberus' Area:EDM Category:Bug Priority:Critical - critical EDM bugs\n"
        "- (AssignedTo:'John' OR AssignedTo:'Jane') Status:open - open cases for John or Jane\n"
        "- Project:'Varde' edited:\"last week\" -Status:closed - Varde cases edited last week that aren't closed\n"
        "- timeout error Project:'Cerberus' - cases mentioning timeout or error in Cerberus\n"
        "- Tag:'production-issue' opened:\"-7d..\" - production issues opened in last 7 days\n"
        "\n"
        "**Workflow Tips:**\n"
        "- For wikis: list_wikis → list_articles → view_article\n"
        "- For metadata: list_categories, list_priorities, list_tags, and list_people provide reference data\n"
        "- The get_events_of_a_case tool provides granular event history including who did what and when\n"
        "\n"
        "**Case Search Strategy - RECOMMENDED APPROACHES:**\n"
        "\n"
        "**Primary Approach: Advanced Search (FASTEST - Use When Possible):**\n"
        "When user query has clear search parameters (project, area, keywords, status, etc.), use advanced_search:\n"
        "1. Construct query using Project:, Area:, Status:, and other relevant axes from user query\n"
        "2. Add keywords or phrases from user's question\n"
        "3. Use advanced_search with constructed query\n"
        "4. Analyze results and identify relevant cases\n"
        "5. Use get_events_of_a_case for detailed investigation of promising cases\n"
        "\n"
        "Example: User asks 'Find open bugs in Cerberus EDM area about timeout issues'\n"
        "→ Query: 'Project:Cerberus Area:EDM Category:Bug Status:open timeout'\n"
        "→ Call: advanced_search(query='Project:Cerberus Area:EDM Category:Bug Status:open timeout')\n"
        "\n"
        "**Secondary Approach: Filter-Based Search (Use for Broad/Unclear Queries):**\n"
        "When query is vague or requires browsing all cases in a project:\n"
        "1. Call list_filters to get available filters\n"
        "2. Match filter name to project name (e.g., '400 Capital' filter for '400 Capital' project)\n"
        "3. Use list_cases with filter_id to get broad overview (max 10,000 cases)\n"
        "4. Analyze returned cases and narrow down based on:\n"
        "   - Title relevance to query\n"
        "   - Case attributes (status, category, area)\n"
        "   - Latest text summary information\n"
        "5. Use get_events_of_a_case for detailed investigation\n"
        "\n"
        "Example: User asks 'What's been happening with 400 Capital lately?'\n"
        "→ Call: list_filters() → find '400 Capital' filter\n"
        "→ Call: list_cases(filter_id=12345)\n"
        "→ Analyze and identify recent/relevant activity\n"
        "\n"
        "**Hybrid Approach: Combine Both Methods:**\n"
        "For complex queries requiring both broad context and specific filtering:\n"
        "1. Start with advanced_search using known parameters\n"
        "2. If results insufficient, use list_cases on relevant filter for broader view\n"
        "3. Cross-reference findings from both approaches\n"
        "4. Use get_events_of_a_case for deep investigation\n"
        "\n"
        "Example: User asks 'Are there any critical issues in Aflac that John worked on last month?'\n"
        "→ Try: advanced_search(query='Project:Aflac Priority:Critical EditedBy:John edited:\"last month\"')\n"
        "→ If needed: list_cases(filter_id for 'Aflac') and filter manually\n"
        "\n"
        "**Decision Tree:**\n"
        "- Query has clear Project + Area + specific criteria? → Use advanced_search\n"
        "- Query mentions specific keywords/terms + project? → Use advanced_search\n"
        "- Query is vague like 'tell me about Project X' or 'what's going on in Project Y'? → Use list_cases with filter\n"
        "- Query needs recent activity summary? → Use list_cases with filter\n"
        "- Query has partial info but unclear scope? → Try advanced_search first, fall back to list_cases if needed\n"
        "\n"
        "**Performance Note:** advanced_search is significantly faster than list_cases for targeted queries. Always prefer advanced_search when you can construct a specific query from user input."
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


@mcp.tool()
def list_tags():
    """
    List all tags in the FogBugz system.
    
    Returns:
      Dictionary with 'tags' key containing a list of tag objects:
      - tag_id: integer (unique identifier)
      - name: tag name
      - usage_count: number of times this tag is used across cases
    """
    return client.list_tags()

@mcp.tool()
def list_categories():
    """
    List all active categories in the FogBugz system.
    
    Returns:
      Dictionary with 'categories' key containing a list of category objects:
      - category_id: integer (unique identifier)
      - name: category name (e.g., "Bug", "Feature", "Task")
      - plural: plural form of the category name
      - is_schedule_item: boolean indicating if this is a schedule item
      - order: display order
      - icon_type: icon type identifier
    
    Note: Deleted categories are automatically filtered out.
    """
    return client.list_categories()


@mcp.tool()
def list_priorities():
    """
    List all priorities in the FogBugz system.
    
    Returns:
      Dictionary with 'priorities' key containing a list of priority objects:
      - priority_id: integer (unique identifier)
      - name: priority name (e.g., "Blocker", "Critical", "Major", "Minor")
      - is_default: boolean indicating if this is the default priority
    """
    return client.list_priorities()

@mcp.tool()
def list_people():
    """
    List all active people/users in the FogBugz system.
    
    Returns:
      Dictionary with 'people' key containing a list of person objects:
      - person_id: integer (unique identifier)
      - full_name: full name of the person
      - email: email address
    
    Note: Deleted users are automatically filtered out.
    """
    return {"people": client.list_people()}


@mcp.tool()
def get_person_id_by_email(email: str):
    """
    Get a person's ID by their email address.
    
    Input:
      - email: Email address of the person (case-insensitive)
    
    Returns:
      Dictionary containing:
      - email: the searched email
      - person_id: integer ID if found, null if not found
      - found: boolean indicating if the person was found
    
    Note: Search is case-insensitive and only matches active (non-deleted) users.
    """
    person_id = client.get_person_id_by_email(email)
    
    return {
        "email": email,
        "person_id": person_id,
        "found": person_id is not None
    }


# Commented Out because list_cases is too slow for some filters, they cannot be used as is, need to be split further or just removed i.e., for projects having cases > 10
@mcp.tool()
def list_filters():
    """
    List all saved filters in the FogBugz system.
    
    Returns:
      Dictionary with 'filters' key containing a list of filter objects:
      - filter_id: integer (unique identifier for the filter)
      - name: filter name (e.g., "400 Capital", "Aflac Support")
    
    Note: This returns all project-based filters.
          These filters can be used to query specific sets of cases based on 
          projects. 
          So all cases under a project are available under filter of same name as project name.
    """
    return {"filters": client.list_filters()}

@mcp.tool()
def list_cases(filter_id: int):
    """
    PURPOSE:
        Retrieve all cases associated with a specific saved filter.
        This is the primary and fastest method for retrieving case summaries
        for supported projects.

    PRECONDITIONS:
        1. You MUST first call `list_filters`.
        2. Identify the correct filter_id from the returned filters.
        3. Only then call `list_cases(filter_id=...)`.

    PROJECT RESTRICTION:
        DO NOT use this tool for the following projects:
            - AG Managed Services
            - DEG (Do not use)
            - EDM Client Services
            - HPS Managed Services
            - Sec Master Implementation Issues

        If the selected filter belongs to one of the above projects:
            → DO NOT call this tool.
            → Use alternative case retrieval tools instead.

        For all other projects returned by `list_projects`:
            → Exactly one saved filter should exist per project.
            → Use that filter_id with this function.

    INPUT:
        filter_id (int, required)
            The ID of a saved filter obtained from `list_filters`.

    RETURNS:
        dict containing:
            - description (str): Filter description
            - filter_id (int): The filter ID used
            - count (int): Number of cases returned in this response
            - total_hits (int): Total matching cases (may exceed count if > 10,000)
            - cases (list[dict]): List of case objects, each containing:
                * case_id (int): Unique case identifier
                * operations (list[str]): Allowed actions (edit, assign, resolve, etc.)
                * title (str): Case title
                * status (str): Current workflow status
                * is_open (bool): Whether the case is open
                * latest_text_summary (str): Summary of latest activity
                * project (str): Project name
                * area (str): Area name
                * email_assigned_to (str | None): Assigned user email
                * category (str): Case category (Bug, Feature, Inquiry, etc.)
                * related_bugs (list[int]): Related case IDs

    BEHAVIORAL NOTES FOR AGENTS:
        - This tool provides a summary-level view of cases.
        - It is optimized for fast retrieval.
        - Always rely on `list_filters` as the source of truth for valid filter IDs.
    """
    return client.list_cases(filter_id)

def main():
    # Run MCP server using stdio transport
    print("Starting FogBugz MCP server")
    mcp.run(transport="stdio")
    #print(client.list_cases(13524))



if __name__ == "__main__":
    main()


