"""
Tutorial 19: State updates and commands from an interceptor.

Interceptors can return `Command` objects to update agent state, hand off
to another node, or end execution early. Useful for marking tasks complete,
transitioning between sub-agents, or short-circuiting a long agent loop.

This example targets the Weather FastMCP server (tutorials/05_weather_server.py)
which exposes two tools:

    get_weather(location)  -> "It's always sunny in <location>"
    get_character(name)    -> dict of character details

We use those two tools to demonstrate the two `Command` patterns:
  - When `get_character` returns successfully, we treat the lookup as
    "task complete" and short-circuit the run with `goto="__end__"`.
  - When `get_weather` runs, we simply mark the request in state and pass
    through (showing a Command that *does not* change routing).

Start the weather server first:
    uv run fastmcp run tutorials/05_weather_server.py --transport http --port 8000
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from rich import print

load_dotenv()


def as_tool_message(result, tool_call_id: str) -> ToolMessage:
    """Coerce an interceptor result into a ToolMessage.

    MCP tools can return plain text strings (get_weather) or dicts
    (get_character returns structured content). langgraph requires that
    every AI tool call in the message history has a matching ToolMessage,
    so anything we put in `Command.update` must be one.
    """
    if isinstance(result, ToolMessage):
        return result
    return ToolMessage(content=str(result), tool_call_id=tool_call_id)


async def handle_character_lookup(request: MCPToolCallRequest, handler):
    """End the agent run as soon as `get_character` succeeds.

    The character lookup is treated as the "task" — once we have the
    character's details, there's nothing else to do, so we use `goto="__end__"`
    to short-circuit the loop.
    """
    result = await handler(request)
    tool_call_id = request.runtime.tool_call_id
    print(f"[bold green]Tool call {tool_call_id} ({request.name}) succeeded[/bold green]")
    if request.name == "get_character":
        return Command(
            update={
                "messages": [as_tool_message(result, tool_call_id)],
                "task_status": "verified",
                "last_tool": "get_character",
            },
            goto="__end__",
        )
    return result


async def mark_weather_lookup(request: MCPToolCallRequest, handler):
    """After `get_weather` succeeds, mark the request in state but keep going.

    This shows a Command that updates state without changing routing — useful
    when you want to track progress but still let the agent respond to the
    user normally.
    """
    result = await handler(request)
    tool_call_id = request.runtime.tool_call_id

    if request.name == "get_weather":
        return Command(
            update={
                "messages": [as_tool_message(result, tool_call_id)],
                "last_tool": "get_weather",
                "weather_checked": True,
            },
            # No `goto` → graph stays on the model node and continues normally.
        )
    return result


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[handle_character_lookup, mark_weather_lookup],
    )

    tools = await client.get_tools()
    print(f"[bold cyan]Loaded tools:[/bold cyan] {[t.name for t in tools]}")

    agent: AgentState = create_agent(  # type: ignore[assignment]
        ChatOpenAI(
            model="MiniMax-M3",
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url=os.getenv("MINIMAX_BASE_URL"),
        ),
        tools,
    )

    # The character lookup will trigger the short-circuit Command.
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "look up naruto"}]}
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())