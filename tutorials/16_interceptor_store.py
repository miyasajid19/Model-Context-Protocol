"""
Tutorial 16: Read user preferences from a store.

`request.runtime.store` gives the interceptor access to long-term memory.
Use it to personalize MCP tool calls with stored user preferences — language,
result limits, default filters, etc.
"""

import asyncio
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore
from rich import print

load_dotenv()


@dataclass
class Context:
    user_id: str


async def personalize_search(request: MCPToolCallRequest, handler):
    """Apply user's preferred language and result limit to the search tool."""
    print(f"Personalizing search for user: {request.runtime.context.user_id}")
    runtime = request.runtime
    user_id = runtime.context.user_id
    store = runtime.store
    prefs = store.get(("preferences",), user_id)
    print(f"request ::: {request.args}")
    print(f"prefs ::: {prefs}")
    print(f"request.name ::: {request.name}")
    if prefs and request.name == "get_character":
        modified_args = {
            "character": "naruto",
        }
        request = request.override(args=modified_args)
    print(f"request ::: {request.args}")
    return await handler(request)


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "search": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[personalize_search],
    )

    tools = await client.get_tools()
    store=InMemoryStore()
    # getting character name  for store
    store.put(("preferences",), "user_123", {"character": "naruto"})
    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
        context_schema=Context,
        store=store,
    )

    # In a real app, you'd seed the store with the user's preferences first.
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "find the details of boruto"}]},
        context={"user_id": "user_123"},
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())