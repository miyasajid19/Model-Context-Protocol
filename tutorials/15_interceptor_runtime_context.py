"""
Tutorial 15: Inject runtime context into MCP tool calls.

Interceptors receive `request.runtime`, which exposes the `ToolRuntime`
context — user IDs, API keys, permissions — passed at invocation time.
This lets MCP tools (running in a separate process) access the same
per-user data the LangChain agent has.
"""

import asyncio
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


@dataclass
class Context:
    user_id: str
    api_key: str


async def inject_user_context(request: MCPToolCallRequest, handler):
    """Inject user credentials into MCP tool calls."""
    runtime = request.runtime
    user_id = runtime.context.user_id
    api_key = runtime.context.api_key

    modified_request = request.override(args={**request.args, "user_id": user_id})
    # api_key isn't sent to the tool — it's available for downstream auth in headers.
    modified_request = modified_request.override(
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return await handler(modified_request)


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "orders": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[inject_user_context],
    )

    tools = await client.get_tools()
    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
        context_schema=Context,
    )

    # Pass per-user context at invocation time.
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Search my orders"}]},
        context={"user_id": "user_123", "api_key": "sk-demo"},
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())