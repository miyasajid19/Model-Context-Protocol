from fastmcp.server import create_proxy

mcp = create_proxy(
    "https://temp-test-server.fastmcp.app/mcp",
    name="Proxy Server"
)

if __name__ == "__main__":
    mcp.run()