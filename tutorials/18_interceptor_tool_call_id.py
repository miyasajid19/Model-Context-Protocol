"""
Tutorial 18: Rate limiting with the tool call ID.

`request.runtime.tool_call_id` gives every tool invocation a unique
identifier. Use it for logging, tracing, or short-circuiting calls that
exceed a rate limit.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()

# Toy in-memory counter. In production use Redis or similar.
_call_counts: dict[str, int] = {}


def is_rate_limited(tool_name: str, max_per_minute: int = 1) -> bool:
    _call_counts[tool_name] = _call_counts.get(tool_name, 0) + 1
    return _call_counts[tool_name] > max_per_minute


async def rate_limit_interceptor(request: MCPToolCallRequest, handler):
    """Block expensive MCP tool calls when over the limit."""
    runtime = request.runtime
    tool_call_id = runtime.tool_call_id

    if is_rate_limited(request.name):
        return ToolMessage(
            content="Rate limit exceeded. Please try again later.",
            tool_call_id=tool_call_id,
        )

    result = await handler(request)
    print(f"[bold green]Tool call {tool_call_id} ({request.name}) succeeded[/bold green]")
    return result


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "search": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[rate_limit_interceptor],
    )

    tools = await client.get_tools()
    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "use tool to get info about naruto"}]}
    )
    print(response)
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "use tool to get info about naruto"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())