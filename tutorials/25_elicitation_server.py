"""
Tutorial 25: MCP server with elicitation.

Elicitation lets a tool ask the user for additional structured input mid-call
instead of requiring everything upfront. The tool uses `ctx.elicit(...)`,
and the client decides how to gather that input (a UI prompt, stdin, a
mock for testing, etc.).

Run with:
    uv run fastmcp run tutorials/25_elicitation_server.py --transport http --port 8000
"""

from pydantic import BaseModel
from mcp.server.fastmcp import Context, FastMCP

server = FastMCP("Profile")


class UserDetails(BaseModel):
    email: str
    age: int


@server.tool()
async def create_profile(name: str, ctx: Context) -> str:
    """Create a user profile, requesting details via elicitation."""
    result = await ctx.elicit(
        message=f"Please provide details for {name}'s profile:",
        schema=UserDetails,
    )

    if result.action == "accept" and result.data:
        return (
            f"Created profile for {name}: "
            f"email={result.data.email}, age={result.data.age}"
        )
    if result.action == "decline":
        return f"User declined. Created minimal profile for {name}."
    return "Profile creation cancelled."


if __name__ == "__main__":
    server.run(transport="http")