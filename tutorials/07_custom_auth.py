"""
Tutorial 07: Custom authentication over HTTP.

`langchain-mcp-adapters` uses the official MCP Python SDK, which accepts any object
implementing the `httpx.Auth` interface for the `auth` field of a server config.

This tutorial shows a minimal bearer-token auth class. In real use, replace the
hardcoded token with an OAuth flow, JWT exchange, vault lookup, etc.

Reference implementation:
    https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/clients/simple-auth-client/mcp_simple_auth_client/main.py
"""

import asyncio
import os
from collections.abc import Generator

import httpx
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


class BearerAuth(httpx.Auth):
    """Attaches `Authorization: Bearer <token>` to every outgoing request."""

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


async def main() -> None:
    auth = BearerAuth(token=os.getenv("MY_MCP_TOKEN", "demo-token"))

    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
                "auth": auth,
            }
        }
    )

    tools = await client.get_tools()
    print(f"[bold cyan]Loaded tools:[/bold cyan] {[t.name for t in tools]}")

    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in tokyo?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())