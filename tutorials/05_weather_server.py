"""
Tutorial 05: Weather server (streamable HTTP transport).

A FastMCP server exposing an async get_weather tool over HTTP.
Start this before running tutorials that connect to it (e.g. tutorials/03_multiple_servers.py).

To run:
    uv run fastmcp run tutorials/05_weather_server.py --transport http --port 8000

or directly:
    uv run python tutorials/05_weather_server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"It's always sunny in {location}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")