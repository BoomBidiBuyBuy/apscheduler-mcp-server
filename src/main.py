import asyncio

from datetime import datetime
from typing import Dict, Any

from fastmcp import FastMCP
import logging

import envs
import client

from apscheduler.schedulers.asyncio import AsyncIOScheduler

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


scheduler = AsyncIOScheduler()

"""
@mcp.tool
def schedule_tool_call_by_cron(
    mcp_endpoint: str,
    tool_name: str,
    tool_args: Dict[str, Any],
):
 
@mcp.tool
def schedule_tool_call_at_interval(
    mcp_endpoint: str,
    tool_name: str,
    tool_args: Dict[str, Any],
    trigger: str,
    run_date: datetime = None,
    weeks: int = None,
    days: int = None,
    hours: int = None,
    minutes: int = None,
    seconds: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    timezone: str = None
):
    scheduler.add_job(
        client.call_tool,
        "date",
        run_date=datetime.strptime(run_date, "%Y-%m-%d %H:%M:%S"),
        kwargs={
            "mcp_endpoint": mcp_endpoint,
            "tool_name": tool_name,
            "params": params
        }
    )
"""

 
@mcp.tool
def schedule_tool_call_once_at_date(
    mcp_endpoint: str,
    tool_name: str,
    tool_args: Dict[str, Any],
    run_date: str,
):
    """
    Schedule remote MCP call once at a certain point of time.

    Args:
        mcp_endpoint: endpoint in http://<ip>:<port> format
        tool_name: mcp tool name to call
        tool_args: arguments to pass to the tool
        run_date: the date/time to run the job at in "%Y-%m-%d %H:%M:%S" format
    """
    scheduler.add_job(
        client.call_tool,
        "date",
        run_date=datetime.strptime(run_date, "%Y-%m-%d %H:%M:%S"),
        kwargs={
            "mcp_endpoint": mcp_endpoint,
            "tool_name": tool_name,
            "params": params
        }
    )


@mcp.tool
def current_datetime():
    """Returns current date and time with timezone in format %Y/%m/%d %H:%M:%S %Z%z"""
    datetime_now = datetime.now()
    return datetime_now.strftime("%Y/%m/%d %H:%M:%S %Z%z")


async def main():
    scheduler.start()

    await mcp.run_async(transport="http", host=envs.MCP_HOST, port=envs.MCP_PORT)


if __name__ == "__main__":
    asyncio.run(main())
