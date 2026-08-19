"""
Tutorial 09: Structured content from MCP tool artifacts.

When an MCP server returns `structuredContent` alongside text, the adapter
wraps it in an `MCPToolArtifact` and exposes it via `ToolMessage.artifact`.

This tutorial walks the agent conversation after the run and prints the
structured content the agent received.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


async def main() -> None:
    # Replace with your server URL once you have a tool that returns structuredContent.
    client = MultiServerMCPClient(
        {
            "data": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    tools = await client.get_tools()
    for tool in tools:
        print(f"[bold cyan]Loaded tool:[/bold cyan] {tool.name}")
        print(f"[bold cyan]Tool description:[/bold cyan] {tool.description}")
        print(f"[bold cyan]=[/bold cyan]"*20)
    agent = create_agent(
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "can you find the weather of capital city of nepal"}]}
    )

    # Walk the conversation and pull structured content out of tool messages.
    for message in result["messages"]:
        if isinstance(message, ToolMessage) and message.artifact:
            structured = message.artifact["structured_content"]
            print(f"[bold cyan]Tool {message.name} returned:[/bold cyan] {structured}")



    print(f"[bold cyan]=[/bold cyan]"*20)
    print(result)
    print(f"[bold cyan]=[/bold cyan]"*20)
if __name__ == "__main__":
    asyncio.run(main())