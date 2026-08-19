"""
Tutorial 23: Progress notifications.

Subscribe to progress updates for long-running MCP tool executions via the
`Callbacks` class. Each notification carries the progress ratio, an optional
message, and a `CallbackContext` identifying the server and tool.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from rich import print

load_dotenv()


async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context: CallbackContext,
):
    percent = (progress / total * 100) if total else progress
    tool_info = f" ({context.tool_name})" if context.tool_name else ""
    print(
        f"[{context.server_name}{tool_info}] "
        f"Progress: {percent:.1f}% - {message}"
    )


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "jobs": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        callbacks=Callbacks(on_progress=on_progress),
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
        {"messages": [{"role": "user", "content": "start the long job"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())