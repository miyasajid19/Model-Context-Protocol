"""
Tutorial 04: Math server (stdio transport).

A minimal FastMCP server that exposes two simple tools over stdio.
Run this as a subprocess from an MCP client (e.g. tutorials/03_multiple_servers.py).

To run standalone for testing:
    uv run fastmcp run tutorials/04_math_server.py --transport stdio
"""

from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")