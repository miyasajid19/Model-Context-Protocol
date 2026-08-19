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

@mcp.tool()
async def get_character(character: str) -> dict:
    """this tool return the character details"""
    if not "naruto" in character.lower() :
        return {"error": "Character not found"}
    return {
        "name": "Naruto Uzumaki",
        "age": 17,
        "village": "Konohagakure",
        "rank": "Genin",
        "jutsu": ["Shadow Clone Jutsu", "Rasengan", "Sage Mode"],
    }


# -------------------------
# Resources
# -------------------------

@mcp.resource("weather://locations")
async def available_locations() -> str:
    """Return the locations supported by the weather server."""
    return """
    Available locations:
    - London
    - New York
    - Tokyo
    - Delhi
    - Mumbai
    """


@mcp.resource("character://naruto")
async def naruto_resource() -> dict:
    """Return Naruto's character information."""
    return {
        "name": "Naruto Uzumaki",
        "age": 17,
        "village": "Konohagakure",
        "rank": "Genin",
        "jutsu": [
            "Shadow Clone Jutsu",
            "Rasengan",
            "Sage Mode",
        ],
    }


# -------------------------
# Prompts
# -------------------------

@mcp.prompt()
def weather_report(location: str) -> str:
    """Create a prompt for generating a weather report."""
    return f"""
    Give me a concise weather report for {location}.

    Include:
    - Current conditions
    - Temperature
    - General recommendation
    """


@mcp.prompt()
def character_analysis(character: str) -> str:
    """Create a prompt for analyzing an anime character."""
    return f"""
    Analyze the character "{character}".

    Include:
    - Background
    - Personality
    - Abilities
    - Strengths
    - Weaknesses
    """


if __name__ == "__main__":
    mcp.run(transport="streamable-http")