import traceback
from langgraph.graph import StateGraph, END
from mcp import ClientSession
from agent.state import AgentState
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig 

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
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})

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

