import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
import os
from fogbugz_mcp.app.fogbugz_tools import FOGBUGZ_TOOLS,export_mcp_tools
import json
load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # self.llm = AzureOpenAI(
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        #     azure_deployment=os.getenv("AZURE_OPENAI_MODEL"),
        #     api_version="2024-06-30"
        # )
        self.llm = OpenAI(
            base_url=os.getenv("OPENAI_ENDPOINT"), 
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
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

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]
        model_name = os.getenv("OPENAI_MODEL") or "gpt-4.1"

        # Discover tools from MCP
        response = await self.session.list_tools()

        available_tools = export_mcp_tools(FOGBUGZ_TOOLS)

        final_text = []

        while True:
            response = self.llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=available_tools,
            )

            choice = response.choices[0]
            message = choice.message

            # 1️⃣ Normal assistant text
            if message.content:
                final_text.append(message.content)

            # 2️⃣ Tool calls (GPT-4.1 style)
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    final_text.append(
                        f"[Calling tool {tool_name} with args {tool_args}]"
                    )

                    # Execute tool via MCP
                    result = await self.session.call_tool(tool_name, tool_args)

                    # Add assistant tool call message
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                        ],
                    })

                    # Add tool result
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content,
                    })

                # Continue loop → model will consume tool result
                continue

            # 3️⃣ No tool calls → final answer reached
            break

        return "\n".join(final_text)

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")



async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("fogbugz_mcp/app/server.py")
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())