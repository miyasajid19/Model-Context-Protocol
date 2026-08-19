"""
Tutorial 11: Multimodal tool content.

When an MCP tool returns content with multiple parts (e.g. text + an image),
the adapter converts them to LangChain's standard content blocks. You can
access them via `ToolMessage.content_blocks` — a provider-agnostic shape that
works regardless of how the underlying MCP server formats the response.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


async def access_multimodal_tool_content() -> None:
    client = MultiServerMCPClient({})
    tools = await client.get_tools()

    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Take a screenshot of the current page",
                }
            ]
        }
    )

    for message in result["messages"]:
        if message.type == "tool":
            print(f"[bold cyan]Raw content:[/bold cyan] {message.content}")

            # Standardized content blocks — provider-agnostic.
            for block in message.content_blocks:
                if block["type"] == "text":
                    print(f"  Text: {block['text']}")
                elif block["type"] == "image":
                    print(f"  Image URL: {block.get('url')}")
                    print(f"  Image base64 (truncated): {block.get('base64', '')[:50]}...")


if __name__ == "__main__":
    asyncio.run(access_multimodal_tool_content())