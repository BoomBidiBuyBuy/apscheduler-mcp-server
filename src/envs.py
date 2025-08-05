import os

from fastmcp import settings


MCP_HOST = os.environ.get("MCP_HOST", settings.host)
MCP_PORT = int(os.environ.get("MCP_PORT", settings.port))
