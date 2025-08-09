import asyncio

from datetime import datetime
from typing import Dict, Any

from fastmcp import FastMCP
import logging

import src.envs as envs
import src.mcp_client as mcp_client

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# In a real app, you might configure this in your main entry point
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a logger for the module where the client is used
logger = logging.getLogger(__name__)


mcp_server = FastMCP(
    name="apscheduler",
)


scheduler = AsyncIOScheduler()


@mcp_server.tool
def remove_scheduled_job(job_id: str):
    """
    Remove a scheduled job by its id.

    Args:
        job_id: the id of the job to remove

    Returns:
        "Job removed"
    """
    scheduler.remove_job(job_id)
    return "Job removed"


@mcp_server.tool
def schedule_tool_call_by_cron(
    mcp_endpoint: str,
    mcp_tool_name: str,
    mcp_tool_args: Dict[str, Any],
    year: str = None,
    month: str = None,
    day: str = None,
    week: str = None,
    day_of_week: str = None,
    hour: str = None,
    minute: str = None,
    second: str = None,
    start_date: str = None,
    end_date: str = None,
    timezone: str = None,
) -> str:
    """
    Triggers when current time matches all specified time constraints,
    similarly to how the UNIX cron scheduler works.

    Args:
        mcp_endpoint: endpoint in http://<ip>:<port> format
        mcp_tool_name: mcp tool name to call
        mcp_tool_args: arguments to pass to the tool
        year: year to schedule the job at
        month: month to schedule the job at
        day: day to schedule the job at
        week: week to schedule the job at
        day_of_week: day of week to schedule the job at
        hour: hour to schedule the job at
        minute: minute to schedule the job at
        second: second to schedule the job at
        start_date: the date/time to start the job at in "%Y-%m-%d" format
        end_date: the date/time to end the job at in "%Y-%m-%d" format
        timezone: the timezone to use for the job

    Returns:
        The job id of the scheduled job
    """

    cron_params = {}
    if year is not None:
        cron_params["year"] = year
    if month is not None:
        cron_params["month"] = month
    if day is not None:
        cron_params["day"] = day 
    if week is not None:
        cron_params["week"] = week
    if day_of_week is not None:
        cron_params["day_of_week"] = day_of_week
    if hour is not None:
        cron_params["hour"] = hour   
    if minute is not None:
        cron_params["minute"] = minute
    if second is not None:
        cron_params["second"] = second
    if start_date is not None:
        cron_params["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is not None:
        cron_params["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")
    if timezone is not None:
        cron_params["timezone"] = timezone

    job = scheduler.add_job(
        mcp_client.call_tool,
        "cron",
        **cron_params,
        kwargs={
            "mcp_endpoint": mcp_endpoint,
            "mcp_tool_name": mcp_tool_name,
            "mcp_tool_args": mcp_tool_args
        }
    )

    return job.id


@mcp_server.tool
def schedule_tool_call_at_interval(
    mcp_endpoint: str,
    mcp_tool_name: str,
    mcp_tool_args: Dict[str, Any],
    weeks: int = None,
    days: int = None,
    hours: int = None,
    minutes: int = None,
    seconds: int = None,
    start_date: str = None,
    end_date: str = None,
    timezone: str = None
) -> str:
    """
    Schedule remote MCP call on specified intervals, starting on `start_date` if specified,
    `datetime.now()` + interval otherwise.

    Args:
        mcp_endpoint: endpoint in http://<ip>:<port> format
        mcp_tool_name: mcp tool name to call
        mcp_tool_args: arguments to pass to the tool
        weeks: number of weeks to wait
        days: number of days to wait
        hours: number of hours to wait
        minutes: number of minutes to wait 
        seconds: number of seconds to wait
        start_date: the date/time to start the job at in "%Y-%m-%d" format
        end_date: the date/time to end the job at in "%Y-%m-%d" format
        timezone: the timezone to use for the job

    Returns:
        The job id of the scheduled job
    """

    interval_params = {}
    if weeks is not None:
        interval_params["weeks"] = weeks
    if days is not None:
        interval_params["days"] = days
    if hours is not None:
        interval_params["hours"] = hours
    if minutes is not None:
        interval_params["minutes"] = minutes
    if seconds is not None:
        interval_params["seconds"] = seconds
    if start_date is not None:
        interval_params["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is not None:
        interval_params["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")
    if timezone is not None:
        interval_params["timezone"] = timezone

    job = scheduler.add_job(
        mcp_client.call_tool,
        "interval",
        **interval_params,
        kwargs={
            "mcp_endpoint": mcp_endpoint,
            "mcp_tool_name": mcp_tool_name,
            "mcp_tool_args": mcp_tool_args
        }
    )

    return job.id


@mcp_server.tool
def schedule_tool_call_once_at_date(
    mcp_endpoint: str,
    mcp_tool_name: str,
    mcp_tool_args: Dict[str, Any],
    run_date: str,
) -> str:
    """
    Schedule remote MCP call once at a certain point of time.

    Args:
        mcp_endpoint: endpoint in http://<ip>:<port> format
        mcp_tool_name: mcp tool name to call
        mcp_tool_args: arguments to pass to the tool
        run_date: the date/time to run the job at in "%Y-%m-%d %H:%M:%S" format

    Returns:
        The job id of the scheduled job
    """
    job = scheduler.add_job(
        mcp_client.call_tool,
        "date",
        run_date=datetime.strptime(run_date, "%Y-%m-%d %H:%M:%S"),
        kwargs={
            "mcp_endpoint": mcp_endpoint,
            "mcp_tool_name": mcp_tool_name,
            "mcp_tool_args": mcp_tool_args
        }
    )

    return job.id


@mcp_server.tool
def current_datetime():
    """Returns current date and time with timezone in format %Y/%m/%d %H:%M:%S %Z%z"""
    datetime_now = datetime.now()
    return datetime_now.strftime("%Y/%m/%d %H:%M:%S %Z%z")


async def main():
    scheduler.start()

    await mcp_server.run_async(transport="http", host=envs.MCP_HOST, port=envs.MCP_PORT)


if __name__ == "__main__":
    asyncio.run(main())