"""
Tutorial 12: Loading MCP resources.

Resources are server-side data (files, database records, API responses). The
adapter returns them as `Blob` objects, which expose both text and binary
content through a unified interface.
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.resources import load_mcp_resources
from rich import print

async def main() -> None:
    client = MultiServerMCPClient(
        {
            "docs": {
                "transport": "http",
                "url": "https://docs.langchain.com/mcp",
            }
        }
    )

    # Option 1: Convenience method on the client
    blobs = await client.get_resources("docs")
    for blob in blobs:
        print(f"URI: {blob.metadata['uri']}, MIME: {blob.mimetype}")
        print(blob.as_string())

    # Option 2: Explicit session for finer control
    async with client.session("docs") as session:
        # First, list/load all valid resources to check available URIs
        all_blobs = await load_mcp_resources(session)
        available_uris = [blob.metadata["uri"] for blob in all_blobs]
        print(f"[bold cyan]Available URIs:[/bold cyan] {available_uris}")

        # Then request only URIs that the server actually exposes.
        # Pick the first one from the listing — don't hardcode URLs.
        if available_uris:
            some_blobs = await load_mcp_resources(
                session, uris=[available_uris[0]]
            )
            for blob in some_blobs:
                print(f"[bold cyan]Loaded:[/bold cyan] {blob.metadata['uri']}")

if __name__ == "__main__":
    asyncio.run(main())