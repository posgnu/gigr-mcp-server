"""GIGR MCP Server - Model Context Protocol server implementation."""

from typing import Any

from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("GIGR MCP Server")


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """A simple greeting tool.

    Args:
        name: The name to greet (default: "World")

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


@mcp.tool()
async def get_server_info() -> dict[str, Any]:
    """Get information about this MCP server.

    Returns:
        Server information including name, version, and capabilities
    """
    return {
        "name": "GIGR MCP Server",
        "version": "0.1.0",
        "description": "A Model Context Protocol server for GIGR",
        "capabilities": ["tools", "resources"],
        "tools": ["hello_world", "get_server_info"],
    }


@mcp.resource("gigr://status")
def server_status() -> str:
    """Get the current server status.

    Returns:
        Current server status information
    """
    return "Server is running and ready to handle requests"


def main() -> None:
    """Main function to run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
