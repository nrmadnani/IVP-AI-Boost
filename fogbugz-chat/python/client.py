import asyncio
import traceback
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
import os

from requests import session
from agent.graph import build_react_graph
from agent.utils import load_chat_model
import json
from langchain_core.messages import HumanMessage, SystemMessage
from agent.prompts import SYSTEM_PROMPT
from langchain_core.runnables import RunnableConfig
import sys
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.agent = None
        self.llm = load_chat_model()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        mcp_tools = await load_mcp_tools(self.session)

        self.llm = self.llm.bind_tools(mcp_tools)

        self.agent = build_react_graph()

    async def process_query(self, query: str) -> str:
        result = {}
        try: 
            initial_state = {
                "messages": [SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content=query)],
                "final_output": [],
            }
            config = RunnableConfig(configurable={"llm": self.llm, "session": self.session})
            result = await self.agent.ainvoke(initial_state, config)
        except Exception as e:
            print(f"Error during processing query: {str(e)}")
            print(traceback.format_exc(), flush=True)

        return "\n".join(result.get("final_output", []))

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def chat_loop(self):
        # print("MCP Client Ready", flush=True)

        while True:
            try:
                line = input()
            except EOFError:
                break  # VS Code closed stdin

            query = line.strip()
            if not query:
                continue

            if query.lower() == "quit":
                break

            try:
                response = await self.process_query(query)
                print(response, flush=True)
            except Exception as e:
                print(f"Error: {str(e)}", flush=True)


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("D:/IVP AI Boost/fogbugz_mcp/app/server.py")
        # ADD MORE MCP SERVERS IF NEEDED
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
