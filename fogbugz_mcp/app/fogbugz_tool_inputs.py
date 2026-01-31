from pydantic import Field
from .tool_spec import ToolInput


class ListArticlesInput(ToolInput):
    wiki_id: int = Field(..., description="Wiki ID from list_wikis")


class SearchArticlesInput(ToolInput):
    query: str = Field(..., description="Search query")


class ViewArticleInput(ToolInput):
    article_id: int = Field(..., description="Article ID from list_articles")
