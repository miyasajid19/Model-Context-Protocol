"""
Tutorial 21: Retry with exponential backoff.

Catch exceptions raised by MCP tool execution and retry with growing delays.

Note: this only catches transport / runtime / content-conversion failures.
MCP tool execution errors (CallToolResult(isError=True)) come back as a
ToolMessage and do NOT raise — to make those raise instead, pass
`handle_tool_errors=False` to MultiServerMCPClient / load_mcp_tools.
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


async def retry_interceptor(
    request: MCPToolCallRequest,
    handler,
    max_retries: int = 3,
    delay: float = 1.0,
):
    """Retry failed tool calls with exponential backoff."""
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return await handler(request)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                print(
                    f"Tool {request.name} failed (attempt {attempt + 1}), "
                    f"retrying in {wait_time:.1f}s..."
                )
                await asyncio.sleep(wait_time)
    raise last_error  # type: ignore[misc]


async def main() -> None:
    client = MultiServerMCPClient(
        {"math": {"transport": "stdio", "command": "python", "args": [str(MATH_SERVER)]}},
        tool_interceptors=[retry_interceptor],
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
        {"messages": [{"role": "user", "content": "what is 9 x 7?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())