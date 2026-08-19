"""
Tutorial 20: Composing multiple interceptors.

Interceptors compose in "onion" order — the first interceptor in the list
is the outermost layer. Each layer wraps the next.

Output of the example below:
    outer: before
    inner: before
    (tool runs)
    inner: after
    outer: after
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


async def outer_interceptor(request: MCPToolCallRequest, handler):
    print("outer: before")
    result = await handler(request)
    print("outer: after")
    return result


async def inner_interceptor(request: MCPToolCallRequest, handler):
    print("inner: before")
    result = await handler(request)
    print("inner: after")
    return result


async def main() -> None:
    client = MultiServerMCPClient(
        {"math": {"transport": "stdio", "command": "python", "args": [str(MATH_SERVER)]}},
        tool_interceptors=[outer_interceptor, inner_interceptor],
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
        {"messages": [{"role": "user", "content": "what is 2 + 3?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())