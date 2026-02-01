from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    LangGraph state for MCP ReAct agent.
    """
    final_output: List[str]
    llm_with_tools: any
    session: any
