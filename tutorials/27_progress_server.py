"""
Tutorial 27: A server that emits MCP progress notifications.

Pairs with tutorials/23_progress_callbacks.py.

The client-side `Callbacks(on_progress=...)` hook is *passive* — it only fires
when the server actively sends `notifications/progress` messages. This server
demonstrates how to do that from a FastMCP tool using `ctx.report_progress()`.

Run with:
    uv run fastmcp run tutorials/27_progress_server.py --transport http --port 8000
"""

import asyncio

from fastmcp import Context, FastMCP

mcp = FastMCP("LongJobs")


@mcp.tool()
async def long_task(steps: int = 5, ctx: Context = None) -> str:  # type: ignore[assignment]
    """Run a long task that reports progress as it works.

    Args:
        steps: Number of sub-steps to simulate. Each step sleeps ~1 second
            so the client has time to receive progress events.
    """
    if ctx is None:
        # FastMCP injects the Context automatically when the tool is invoked
        # over MCP; the default None is just here so the signature stays valid
        # when called directly from a Python script.
        raise RuntimeError("Context is required when running over MCP.")

    for i in range(1, steps + 1):
        # Yield to the event loop so the notification actually gets flushed.
        await asyncio.sleep(1)

        # Send a progress notification to the client.
        # progress: how much work has been done so far
        # total:    the denominator (None if unknown)
        # message:  optional human-readable status string
        await ctx.report_progress(
            progress=i,
            total=steps,
            message=f"Working on step {i} of {steps}…",
        )

    return "Long task completed"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")