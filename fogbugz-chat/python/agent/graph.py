import traceback
from langgraph.graph import StateGraph, END
from mcp import ClientSession
from agent.state import AgentState
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig 
from langchain.agents import create_agent

from langchain_core.tools import tool



@tool
def plan_steps(objective: str) -> str:
    """Create a step-by-step plan to achieve an objective."""
    return f"Plan:\n1. Analyze objective\n2. Break into steps\n3. Execute\nObjective: {objective}"


@tool
def vfs_write(path: str, content: str) -> str:
    """Write content to a virtual file system."""
    # in-memory or real FS
    return f"Wrote {len(content)} chars to {path}"


def agent_node(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    final_output = state.get("final_output", [])
    try: 
        
        llm = config.get("configurable", {}).get("llm")
        response = llm.invoke(messages)

        if response.content:
            final_output.append(response.content)

    except Exception as e:
        print(f"Error in agent_node: {str(e)}")
        print(traceback.format_exc(), flush=True)
        response = ToolMessage(content=f"Error: {str(e)}")
    
    return {
        "messages": messages + [response],
        "final_output": final_output,
    }



async def tool_node(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    last_message = messages[-1]

    session: ClientSession = config.get("configurable", {}).get("session")
    local_tools = config.get("configurable", {}).get("local_tools", {})
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})

        # ---------- LOCAL TOOL ----------
        if tool_name in local_tools:
            result = local_tools[tool_name].invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=result,
                )
            )
            continue
        
        # ---------- MCP TOOL ----------
        result = await session.call_tool(tool_name, tool_args)
        tool_messages.append(
            ToolMessage(
                tool_call_id=tool_call["id"],
                content=result.content[0].text if result.content else "",
            )
        )

    return {
        "messages": messages + tool_messages
    }

def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END


def build_react_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "agent")

    return graph.compile()

