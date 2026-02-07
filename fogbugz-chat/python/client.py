import asyncio
import traceback
from typing import Optional
from contextlib import AsyncExitStack
from pathlib import Path

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
from agent.prompts import SYSTEM_PROMPT, FOGBUGZ_ADV_SEARCH_AGENT_PROMPT
from langchain_core.runnables import RunnableConfig
import sys
from langchain_mcp_adapters.tools import load_mcp_tools
from deepagents import create_deep_agent, MemoryMiddleware
from deepagents.backends.filesystem import FilesystemBackend
from agent.filesystem_tools import (
    read_from_file,
    write_to_file,
    append_line,
    write_block,
    write_block_function,
)
from agent.case_tools import create_fogbugz_case
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

FOGBUGZ_MEMORY_DIR = "D:/IVP AI Boost/fogbugz-chat/python/agent_memory"
ROOT_DIR = "D:/D:/IVP AI Boost/fogbugz-chat/python"
FOGBUGZ_ADV_MEMORY_FILES = [
    f"{FOGBUGZ_MEMORY_DIR}/AGENTS.md",
    f"{FOGBUGZ_MEMORY_DIR}/QUERY_HISTORY.md",
]
FILESYSTEM_BACKEND = FilesystemBackend(root_dir=ROOT_DIR)
MAX_TURNS = 6   # 6 user+assistant pairs


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.agent = None
        self.llm = load_chat_model()
        self.summarize_llm = load_chat_model()
        self.messages = []
        self.checkpointer = MemorySaver()


    def _turn_count(self) -> int:
        return sum(1 for m in self.messages if m["role"] == "user")

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
        tools = [read_from_file, write_to_file, append_line, write_block] + mcp_tools
        self.llm = self.llm.bind_tools(tools)

        memory_middleware = MemoryMiddleware(
            backend=FILESYSTEM_BACKEND,
            sources=FOGBUGZ_ADV_MEMORY_FILES,
        )

        # self.agent = build_react_graph()
        fogbugz_advanced_search_agent = {
            "name": "Fogbugz Advanced Search Agent",
            "description": (
                "Planner + specialist for complex FogBugz case searches using advanced search syntax, "
                "memory-aware query planning, filesystem-backed recall, and concise result summarization."
            ),
            "system_prompt": FOGBUGZ_ADV_SEARCH_AGENT_PROMPT,
            "tools": tools,
            "middleware": [memory_middleware],
            "backend": FILESYSTEM_BACKEND,
        }


        self.agent = create_deep_agent(
            model=self.llm,
            tools=tools + [create_fogbugz_case],
            system_prompt=SYSTEM_PROMPT,
            skills=["./agent/skills/"],
            checkpointer=self.checkpointer,
            subagents=[fogbugz_advanced_search_agent],
            backend=FILESYSTEM_BACKEND,
            
        )
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    async def process_query(self, query: str) -> str:
        try:
            if query.strip().lower() == "/new":
                self.messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    }
                ]
                return "\n🧹 New conversation started. (long-term memory preserved)."

            # ✅ Append user message
            self.messages.append(
                {
                    "role": "user",
                    "content": query,
                }
            )

            result = await self.agent.ainvoke(
                {
                    "messages": self.messages
                },
                config={"configurable": {"thread_id": "12345"}},

            )

            # ✅ Append assistant response
            assistant_msg = result["messages"][-1]
            self.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_msg.content,
                }
            )

            # 🔹 Summarize & store if needed
            await self.summarize_and_store()

            return "\n" + assistant_msg.content

        except Exception as e:
            print(f"Error during processing query: {str(e)}")
            print(traceback.format_exc(), flush=True)
            return "\n❌ Error processing request."

    async def summarize_and_store(self):
        """
        Summarizes the current conversation buffer and writes structured memory
        into filesystem-backed memory files.
        """

        # Do not summarize trivial conversations
        if self._turn_count() <= MAX_TURNS:
            return

        conversation_json = json.dumps(self.messages, indent=2)

        summary_prompt = [
            {
                "role": "system",
                 "content": (
            "You are a memory distillation engine.\n"
            "Your job is to extract durable, reusable information from a conversation\n"
            "and map it into THREE authoritative memory files.\n\n"

            "You DO NOT write files yourself.\n"
            "You ONLY return structured JSON that will be written verbatim by the system.\n\n"

            "The memory files and their purposes are:\n\n"

            "1) AGENT_MEMORY.md\n"
            "Purpose:\n"
            "- Durable agent knowledge across sessions.\n"
            "- Tracks what the agent has learned from FogBugz cases, wikis, and investigations.\n\n"
            "Populate ONLY factual, stable information that belongs in one of these sections:\n"
            "- Summary (high-level agent objectives or conclusions)\n"
            "- Case references (FogBugz case IDs with brief takeaway)\n"
            "- Wiki references (title + 1–2 line gist)\n"
            "- Known issues / workarounds\n"
            "- Actions / To-dos (unfinished investigations)\n\n"

            "2) QUERY_HISTORY.md\n"
            "Purpose:\n"
            "- Audit trail of user search intent and executed searches.\n"
            "- Prevent repeated or redundant queries.\n\n"
            "Capture each user query as a structured audit entry including:\n"
            "- User intent\n"
            "- Subqueries (if any)\n"
            "- Executed queries (filters, columns, date ranges)\n"
            "- Result summary\n"
            "- Follow-ups or assumptions\n\n"

            "3) USER_PREFERENCES.md\n"
            "Purpose:\n"
            "- Durable user preferences for retrieval, filtering, or summarization.\n\n"
            "ONLY extract preferences that are:\n"
            "- Explicitly stated by the user, OR\n"
            "- Repeated consistently across multiple turns.\n\n"
            "Do NOT include transient, one-off, or session-specific instructions.\n\n"

            "Return JSON with EXACTLY these top-level keys:\n"
            "- agent_memory: array of bullet-point entries suitable for AGENT_MEMORY.md\n"
            "- query_history: array of structured query summaries\n"
            "- user_preferences: array of explicit preference statements\n\n"

            "Rules:\n"
            "- Do NOT hallucinate.\n"
            "- If a category has no valid entries, return an empty array.\n"
            "- Be concise, factual, and non-redundant.\n" )
            },
            {
                "role": "user",
                "content": conversation_json,
            },
        ]

        result = await self.summarize_llm.ainvoke(summary_prompt)

        try:
            distilled = json.loads(result.content)
        except Exception:
            # Hard failure protection — never corrupt memory
            return

        # ---- Write AGENT_MEMORY.md ----
        if distilled.get("agent_memory"):
            write_block_function(
                filepath="AGENT_MEMORY.md",
                block_title="Agent Memory Update",
                content="\n".join(f"- {item}" for item in distilled["agent_memory"]),
            )

        # ---- Write USER_PREFERENCES.md ----
        if distilled.get("user_preferences"):
            write_block_function(
                filepath="USER_PREFERENCES.md",
                block_title="User Preferences Update",
                content="\n".join(f"- {item}" for item in distilled["user_preferences"]),
            )

        # ---- Write QUERY_HISTORY.md (always append) ----
        if distilled.get("query_history"):
            write_block_function(
                filepath="QUERY_HISTORY.md",
                block_title="Query Batch",
                content="\n".join(f"- {item}" for item in distilled["query_history"]),
            )

        # ---- Compact short-term memory ----
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": (
                    "Conversation so far has been summarized into long-term memory. "
                    "Continue based on stored context."
                ),
            },
        ]

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def chat_loop(self):
        while True:
            try:
                line = input()
            except EOFError:
                break

            query = line.strip()
            if not query:
                continue

            # ---- control commands (never reach agent) ----
            if query.lower() == "/quit":
                break

            if query.lower() == "/new":
                self.messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    }
                ]
                print("\n🧹 New conversation started (long-term memory preserved).", flush=True)
                continue

            # ---- normal user turn ----
            try:
                response = await self.process_query(query)
                print(response, flush=True)
            except Exception as e:
                print(f"Error: {str(e)}", flush=True)

                # 🔒 rollback safety
                self.messages = self.messages[:1]



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
