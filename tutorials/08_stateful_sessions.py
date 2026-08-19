"""
Tutorial 08: Stateful sessions.

By default, `MultiServerMCPClient` is stateless: each tool invocation creates a
fresh MCP session, executes the tool, then cleans up. For stateful servers
that need to retain context across calls, open an explicit session with
`client.session("server_name")` and pass it to `load_mcp_tools`.

Useful when the server is keeping conversation context, holds a long-lived
connection, or exposes tools whose effects should accumulate.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()

MATH_SERVER = Path(__file__).parent / "04_math_server.py"


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [str(MATH_SERVER)],
            }
        }
    )

    # Open a session explicitly and load tools bound to that session.
    async with client.session("math") as session:
        tools = await load_mcp_tools(session)
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
            {"messages": [{"role": "user", "content": "what's 11 + 4?"}]}
        )
        print(response)
        


if __name__ == "__main__":
    asyncio.run(main())