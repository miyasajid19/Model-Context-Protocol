"""
Tutorial 10: Appending structured content via an interceptor.

If you want `structuredContent` to be visible in the conversation history
(so the model can see the JSON, not just the human-readable text), use an
interceptor to append it to the tool result automatically.
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from mcp.types import TextContent
from rich import print

load_dotenv()


async def append_structured_content(
    request: MCPToolCallRequest,
    handler,
):
    """Append structured content from artifact to the tool message text."""
    result = await handler(request)
    if result.structuredContent:
        result.content += [
            TextContent(type="text", text=json.dumps(result.structuredContent)),
        ]
    return result


async def main() -> None:
    client = MultiServerMCPClient(
        {"data": {"transport": "http", "url": "http://localhost:8000/mcp"}},
        tool_interceptors=[append_structured_content],
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

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Get character details of naruto"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())