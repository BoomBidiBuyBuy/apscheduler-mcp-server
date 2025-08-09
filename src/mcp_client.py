from typing import Dict, Any

import mcp

from fastmcp.client import Client


async def call_tool(
    mcp_endpoint: str, mcp_tool_name: str, mcp_tool_args: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """Connect the http MCP server and call specified tool with args.

    mcp_point: url in format http://<ip>:<port>
    mcp_tool_name: name of the tool to call
    mcp_tool_args: arguments to pass to the tool
    """
    client = Client(f"{mcp_endpoint}/mcp/")

    async with client:
        return await client.call_tool_mcp(mcp_tool_name, mcp_tool_args)
