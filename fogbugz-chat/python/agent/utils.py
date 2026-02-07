import os
from langchain_openai import ChatOpenAI
from agent.graph import plan_steps, vfs_write

def load_chat_model():
    """
    Load chat model and bind FogBugz tools for LangGraph ReAct.
    """
    model_name = os.getenv("OPENAI_MODEL") or "gpt-4.1"

    llm = ChatOpenAI(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_ENDPOINT"),
        temperature=1
    )

    return llm
