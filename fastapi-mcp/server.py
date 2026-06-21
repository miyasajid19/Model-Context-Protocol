from fastmcp import FastMCP
from backend.app import app


mcp=FastMCP.from_fastapi(app=app,
                         name="Portfolio-backend")
# mcp=FastMCP(name="Portfolio-backend")
# @mcp.tool()
# def say_hello(name: str):
#     """
#     A simple tool that takes a name as input and returns a greeting message.
#     name: The name of the person to greet.
#     Returns a greeting message in the format "Hello, {name}!".
#     """
#     return f"Hello,Muhammad {name}!"

# @mcp.tool()
# def add_numbers(a: int, b: int):
#     """
#     A simple tool that takes two integers as input and returns their sum.
#     a: The first integer.
#     b: The second integer.
#     Returns the sum of a and b.
#     """
#     return a * b
if __name__ == "__main__":
    mcp.run()