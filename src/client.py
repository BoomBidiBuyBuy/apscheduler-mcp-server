import asyncio

from typing import Dict, Any

import mcp

from fastmcp.client import Client


async def call_tool(
    mcp_endpoint: str,
    tool_name: str,
    params: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """ Connect the http MCP server and call specified tool with params.
    
    mcp_point: url in format http://<ip>:<port>
    """
    client = Client(f"{mcp_endpoint}/mcp/")

    async with client:
        return await client.call_tool_mcp(tool_name, params)
