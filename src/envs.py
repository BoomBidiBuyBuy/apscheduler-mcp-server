import os

from fastmcp import settings


MCP_HOST = os.environ.get("MCP_HOST", settings.host)
MCP_PORT = int(os.environ.get("MCP_PORT", settings.port))

PLAN_SCHEMA_ANNOTATION_PATH = os.environ.get(
    "PLAN_SCHEMA_ANNOTATION_PATH", "plan-schema.ann"
)

EXECUTION_STRATEGY = os.environ.get("EXECUTION_STRATEGY", "sequential")

WORKER_ENDPOINT = os.environ.get("WORKER_ENDPOINT")
WORKER_TOOL_NAME = os.environ.get("WORKER_TOOL_NAME")
