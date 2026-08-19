"""
Tutorial 03: Accessing multiple MCP servers from a single client.

Connects to:
  - A local "math" MCP server over stdio (spawned as a subprocess).
  - A local "weather" MCP server over HTTP at http://localhost:8000/mcp.

Run the weather server first:
    uv run python tutorials/05_weather_server.py
or
    uv run fastmcp run tutorials/05_weather_server.py --transport http --port 8000

Then run this client.
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

# Absolute path to the math server so stdio subprocess can find it regardless of CWD.
MATH_SERVER = Path(__file__).parent / "04_math_server.py"


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [str(MATH_SERVER)],
            },
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        }
    )

    tools = await client.get_tools()
    print(f"[bold cyan]Loaded {len(tools)} tools:[/bold cyan] {[t.name for t in tools]}")

    llm = ChatOpenAI(
        model="MiniMax-M3",
        api_key=os.getenv("MINIMAX_API_KEY"),
        base_url=os.getenv("MINIMAX_BASE_URL"),
    )
    agent = create_agent(llm, tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print("\n[bold green]Math response:[/bold green]", math_response)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print("\n[bold green]Weather response:[/bold green]", weather_response)


if __name__ == "__main__":
    asyncio.run(main())