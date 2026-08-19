"""
Tutorial 17: Filter sensitive tools based on auth state.

`request.runtime.state` exposes the agent's current state. Use it to block
sensitive MCP tools when the user isn't authenticated.

This interceptor short-circuits the call by returning a `ToolMessage` with
an error message, so the agent can read it and try a different approach.
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


async def require_authentication(request: MCPToolCallRequest, handler):
    """Block sensitive MCP tools if user is not authenticated."""
    runtime = request.runtime
    state = runtime.state
    print(f"state ::    {state}")
    is_authenticated = state.get("authenticated", False)

    sensitive_tools = ["get_character", "update_settings", "export_data"]

    if request.name in sensitive_tools and not is_authenticated:
        return ToolMessage(
            content="Authentication required. Please log in first.",
            tool_call_id=runtime.tool_call_id,
        )

    return await handler(request)


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "files": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[require_authentication],
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

    # First call: not authenticated, sensitive tool will be blocked.
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "get the details of naruto"}]},
        # Seed initial state.
    )
    print(response)
    
    # Second call: authenticated, non-sensitive tool will be allowed.
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "use tool and tell me the weather of kathmandu"}]},
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())