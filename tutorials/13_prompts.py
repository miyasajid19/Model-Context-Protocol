"""
Tutorial 13: Loading MCP prompts.

Loads prompts exposed by the Weather FastMCP server
and converts them into LangChain messages.
"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.prompts import load_mcp_prompt
from rich import print


async def main() -> None:

    # Connect to our Weather MCP server
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    # ─────────────────────────────────────────────────────────────
    # Load weather_report prompt
    # ─────────────────────────────────────────────────────────────

    messages = await client.get_prompt(
        "weather",
        "weather_report",
        arguments={
            "location": "Delhi"
        },
    )

    print("\n[bold green]Weather Report Prompt:[/bold green]")
    print(messages)

    # ─────────────────────────────────────────────────────────────
    # Load character_analysis prompt
    # ─────────────────────────────────────────────────────────────

    messages = await client.get_prompt(
        "weather",
        "character_analysis",
        arguments={
            "character": "Naruto"
        },
    )

    print("\n[bold green]Character Analysis Prompt:[/bold green]")
    print(messages)

    # ─────────────────────────────────────────────────────────────
    # Print the LangChain messages
    # ─────────────────────────────────────────────────────────────

    print("\n[bold cyan]Messages:[/bold cyan]")

    for message in messages:
        print(f"\nType: {message.type}")
        print(f"Content: {message.content}")

    # ─────────────────────────────────────────────────────────────
    # Explicit session example
    # ─────────────────────────────────────────────────────────────

    async with client.session("weather") as session:

        msgs = await load_mcp_prompt(
            session,
            "weather_report",
            arguments={
                "location": "Mumbai"
            },
        )

        print("\n[bold yellow]Explicit Session Prompt:[/bold yellow]")

        for message in msgs:
            print(f"{message.type}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())