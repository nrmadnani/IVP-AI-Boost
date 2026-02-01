import os
from langchain_openai import ChatOpenAI
from fogbugz_mcp.app.fogbugz_tools import FOGBUGZ_TOOLS, export_mcp_tools

def load_chat_model():
    """
    Load chat model and bind FogBugz tools for LangGraph ReAct.
    """
    model_name = os.getenv("OPENAI_MODEL") or "gpt-4.1"

    llm = ChatOpenAI(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_ENDPOINT"),
        temperature=0
    )

    fogbugz_tools = export_mcp_tools(FOGBUGZ_TOOLS)
    llm_with_tools = llm.bind_tools(fogbugz_tools)

    return llm_with_tools
