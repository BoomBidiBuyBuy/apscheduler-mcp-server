import ast
import logging
from typing import Dict, Any

import mcp

from fastmcp.client import Client
from fastmcp.client.transports import StdioTransport


logger = logging.getLogger(__name__)


async def call_tool(
    mcp_endpoint: str, mcp_tool_name: str, mcp_tool_args: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """Connect to MCP server and call specified tool with args.

    Args:
    mcp_endpoint: either HTTP URL or process config (command:args)
        Examples:
        - HTTP-based MCP server: http://email-mcp:3002/mcp/
        - Process-based MCP server: command:python:['-m', 'mcp-server-email']
    mcp_tool_name: name of the tool to call
    mcp_tool_args: arguments to pass to the tool
    """
    logger.info(
        f"Calling tool {mcp_tool_name} at {mcp_endpoint} with args: {mcp_tool_args}"
    )
    
    # Check if it's a process-based MCP server
    if mcp_endpoint.startswith("command:"):
        return await _call_process_mcp(mcp_endpoint, mcp_tool_name, mcp_tool_args)
    else:
        # HTTP-based MCP server
        return await _call_http_mcp(mcp_endpoint, mcp_tool_name, mcp_tool_args)


async def _call_http_mcp(
    mcp_endpoint: str, mcp_tool_name: str, mcp_tool_args: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """Call HTTP-based MCP server."""
    client = Client(f"{mcp_endpoint}")

    async with client:
        result = await client.call_tool_mcp(mcp_tool_name, mcp_tool_args)
        logger.info(f"Tool {mcp_tool_name} called with result: {result}")
        return result


def _parse_process_endpoint(mcp_endpoint: str) -> tuple[str, list[str]]:
    """Parse process endpoint format (command:args)"""
    parts = mcp_endpoint.split(":", 2)
    if len(parts) != 3:
        raise ValueError(
            f"Invalid process endpoint format: {mcp_endpoint}. "
            "Expected format: command:python:['-m', 'mcp-server-email']"
        )

    command = parts[1]
    args_str = parts[2]

    try:
        args = ast.literal_eval(args_str)
        if not isinstance(args, list):
            raise ValueError(f"Args must be a list, got {type(args)}")
        return command, args
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid args format '{args_str}': {e}")


async def _call_process_mcp(
    mcp_endpoint: str, mcp_tool_name: str, mcp_tool_args: Dict[str, Any]
) -> mcp.types.CallToolResult:
    """Call process-based MCP server."""
    command, args = _parse_process_endpoint(mcp_endpoint)
    
    logger.info(f"Executing process command: {command} with args: {args}")

    transport = StdioTransport(command=command, args=args)
    client = Client(transport)

    async with client:
        result = await client.call_tool_mcp(mcp_tool_name, mcp_tool_args)
        logger.info(f"Tool {mcp_tool_name} called with result: {result}")
        return result
