"""
Tutorial 24: Logging notifications.

MCP servers can emit logging messages via the protocol. Subscribe to them
with the `Callbacks(on_logging_message=...)` hook. The notification payload
follows `mcp.types.LoggingMessageNotificationParams`.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from mcp.types import LoggingMessageNotificationParams
from rich import print

load_dotenv()


async def on_logging_message(
    params: LoggingMessageNotificationParams,
    context: CallbackContext,
):
    """Handle log messages from MCP servers."""
    print(f"[{context.server_name}] {params.level}: {params.data}")


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "noisy": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        callbacks=Callbacks(on_logging_message=on_logging_message),
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
        {"messages": [{"role": "user", "content": "do the noisy thing"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())