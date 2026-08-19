"""
Tutorial 26: Handling elicitation requests on the client.

Pairs with `25_elicitation_server.py`. When the server calls
`ctx.elicit(...)`, the client receives an `ElicitRequestParams` and must
return an `ElicitResult` describing how the user responded.

Response actions:
  - accept   — user provided data; include it in `content`.
  - decline  — user chose not to answer; no data required.
  - cancel   — user aborted the whole operation.

In a real app, replace the hardcoded values with a UI prompt.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import CallbackContext, Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult
from rich import print

load_dotenv()


async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """Handle elicitation requests from MCP servers.

    In a real application you would prompt the user for input based on
    params.message and params.requestedSchema, then return their answer.
    Here we return a fixed payload so the example is self-contained.
    """
    print(
        f"[{context.server_name}] Elicitation requested: "
        f"{params.message} (schema={params.requestedSchema})"
    )
    return ElicitResult(
        action="accept",
        content={"email": "user@example.com", "age": 25},
    )


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "profile": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            }
        },
        callbacks=Callbacks(on_elicitation=on_elicitation),
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
        {"messages": [{"role": "user", "content": "Create a profile for Alice"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())