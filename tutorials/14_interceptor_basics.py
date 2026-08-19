"""
Tutorial 14: Basic interceptor patterns.

An interceptor is an async function `(request, handler) -> result` that wraps
tool execution. It can mutate the request before calling `handler`, mutate
the response after, or skip `handler` entirely and return its own value.

Three patterns in one file:
  1. Logging            — observe without modifying.
  2. Modifying args     — use `request.override(args=...)`.
  3. Modifying headers  — use `request.override(headers=...)` per-call.
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


# 1. Logging interceptor — observe, do not mutate.
async def logging_interceptor(request: MCPToolCallRequest, handler):
    print(f"Calling tool: {request.name} with args: {request.args}")
    result = await handler(request)
    print(f"Tool {request.name} returned: {result}")
    return result


# 2. Modifying args — double every numeric argument before execution.
async def double_args_interceptor(request: MCPToolCallRequest, handler):
    print(f"Doubling numeric args for tool: {request.name}")
    print(f"Original args: {request.args}")
    modified_args = {k: v * 2 for k, v in request.args.items() if isinstance(v, (int, float))}
    print(f"Modified args: {modified_args}")
    modified_request = request.override(args=modified_args)
    return await handler(modified_request)


# 3. Dynamic header injection — pick a token per tool.
async def auth_header_interceptor(request: MCPToolCallRequest, handler):
    token = os.getenv("MY_MCP_TOKEN", "demo-token")
    print(f"Using token: {token}")
    modified_request = request.override(
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Injected Authorization header for tool: {request.name}")
    return await handler(modified_request)


async def main() -> None:
    client = MultiServerMCPClient(
        {"math": {"transport": "stdio", "command": "python", "args": [str(MATH_SERVER)]}},
        tool_interceptors=[logging_interceptor, double_args_interceptor,auth_header_interceptor],
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

    # add(2, 3) becomes add(4, 6) thanks to the double-args interceptor.
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's 2 + 3?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())