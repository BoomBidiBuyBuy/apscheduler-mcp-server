import logging
from typing import Dict, Any

import mcp

from fastmcp.client import Client


logger = logging.getLogger(__name__)


async def call_tool(
    mcp_endpoint: str, mcp_tool_name: str, mcp_tool_args: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """Connect the http MCP server and call specified tool with args.

    mcp_point: url in format http://<ip>:<port>
    mcp_tool_name: name of the tool to call
    mcp_tool_args: arguments to pass to the tool
    """
    logger.info(
        f"Calling tool {mcp_tool_name} at {mcp_endpoint} with args: {mcp_tool_args}"
    )
    client = Client(f"{mcp_endpoint}/mcp/")

    async with client:
        result = await client.call_tool_mcp(mcp_tool_name, mcp_tool_args)
        logger.info(f"Tool {mcp_tool_name} called with result: {result}")
        return result
