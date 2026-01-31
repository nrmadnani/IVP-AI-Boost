from .tool_spec import ToolSpec, ToolInput
from .fogbugz_tool_inputs import (
    ListArticlesInput,
    SearchArticlesInput,
    ViewArticleInput,
)
from typing import List, Dict, Any


class EmptyInput(ToolInput):
    pass


FOGBUGZ_TOOLS = [
    ToolSpec(
        name="list_wikis",
        description="List all active FogBugz wiki spaces.",
        input_model=EmptyInput,
        returns="List of wiki objects with wiki_id, name, tagline, root_page_id",
    ),
    ToolSpec(
        name="list_articles",
        description="List articles within a specific wiki.",
        input_model=ListArticlesInput,
        returns="List of articles with article_id and title",
    ),
    ToolSpec(
        name="search_articles",
        description="Search FogBugz articles by keyword.",
        input_model=SearchArticlesInput,
        returns="Ranked list of matching articles",
    ),
    ToolSpec(
        name="view_article",
        description="Retrieve the full content of a FogBugz article.",
        input_model=ViewArticleInput,
        returns="Article content in Markdown with tags",
    ),
    ToolSpec(
        name="ping",
        description="Connectivity test.",
        input_model=EmptyInput,
        returns="pong",
    ),
]




def export_mcp_tools(tools: List[ToolSpec]) -> List[Dict[str, Any]]:
    """
    Export tools in MCP-compatible JSON format.
    """
    return [tool.to_mcp_tool() for tool in tools]
