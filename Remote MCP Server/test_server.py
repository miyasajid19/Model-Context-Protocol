import random


import json
from fastmcp import FastMCP

mcp= FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two integers and return the result.
    a: The first integer to add.
    b: The second integer to add.
    Returns the sum of a and b.
    """
    return a + b

@mcp.tool()
def length_of_string(s: str) -> int:
    """
    Calculate the length of a given string.
    s: The input string whose length is to be calculated.
    Returns the length of the input string.
    """
    return len(s)




if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=4320)
    