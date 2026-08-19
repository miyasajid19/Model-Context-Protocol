"""
Tutorial 22: Error fallback.

Catch specific exception types raised by MCP tool execution and return a
useful message back to the agent instead of letting it bubble up.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()

MATH_SERVER = Path(__file__).parent / "04_math_server.py"


async def fallback_interceptor(request: MCPToolCallRequest, handler):
    """Return a fallback value if tool execution fails."""
    try:
        return await handler(request)
    except TimeoutError:
        return f"Tool {request.name} timed out. Please try again later."
    except ConnectionError:
        return f"Could not connect to {request.name} service. Using cached data."


async def main() -> None:
    client = MultiServerMCPClient(
        {"math": {"transport": "stdio", "command": "python", "args": [str(MATH_SERVER)]}},
        tool_interceptors=[fallback_interceptor],
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
        {"messages": [{"role": "user", "content": "what is 8 + 12?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())