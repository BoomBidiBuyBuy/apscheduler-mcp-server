from fastmcp import FastMCP
import logging

import envs
from scheduler import scheduler

# In a real app, you might configure this in your main entry point
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a logger for the module where the client is used
logger = logging.getLogger(__name__)


mcp = FastMCP(
    name="apscheduler",
)


@mcp.tool
def current_datetime():
    """Returns current date and time with timezone in format %Y/%m/%d %H:%M:%S %Z%z"""
    datetime_now = datetime.now()
    return datetime_now.strftime("%Y/%m/%d %H:%M:%S %Z%z")


def main():
    scheduler.start()

    mcp.run(transport="http", host=envs.MCP_HOST, port=envs.MCP_PORT)


if __name__ == "__main__":
    main()
