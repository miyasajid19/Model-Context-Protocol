"""
Tutorial 23: Progress notifications.

Subscribe to progress updates emitted by an MCP server during long-running
tool executions via the `Callbacks` class. Each notification carries the
progress ratio, an optional message, and a `CallbackContext` identifying
the server and tool.

IMPORTANT: progress notifications are **server-driven**. The MCP server has
to actively send `notifications/progress` messages via `ctx.report_progress()`
during the tool call. The client's `on_progress` callback is passive — it
only fires when the server emits one. If the server doesn't report
progress, the callback never runs.

Pairs with tutorials/27_progress_server.py — start it before running this:
    uv run fastmcp run tutorials/27_progress_server.py --transport http --port 8000
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
    """Handle progress updates from MCP servers."""
    percent = (progress / total * 100) if total else progress
    tool_info = f" ({context.tool_name})" if context.tool_name else ""
    print(
        f"[{context.server_name}{tool_info}] "
        f"Progress: {percent:.1f}% - {message}"
    )


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "longjobs": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        callbacks=Callbacks(on_progress=on_progress),
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

    # 27_progress_server.py's `long_task` accepts a `steps` arg. Telling the
    # model to use 5 steps gives us ~5 progress notifications to observe.
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "start the long task with 5 steps"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())