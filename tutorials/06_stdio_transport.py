"""
Tutorial 06: stdio transport.

Connect to a local MCP server that the client launches as a subprocess.
Communication happens over stdin/stdout — no network involved.

Use this for local tools where spawning a child process is acceptable.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
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
        {"messages": [{"role": "user", "content": "what's 7 multiplied by 6?"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())