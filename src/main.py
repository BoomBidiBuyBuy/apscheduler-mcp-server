import asyncio
import json
import pprint
from datetime import datetime
from typing import Annotated

from fastmcp import FastMCP
import logging

import envs
import mcp_client

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# In a real app, you might configure this in your main entry point
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get a logger for the module where the client is used
logger = logging.getLogger(__name__)


mcp_server = FastMCP(
    name="apscheduler",
)


scheduler = AsyncIOScheduler()


PLAN_SCHEMA_ANNOTATION = (
    "Execution plan in JSON format with the following structure: "
    + open(envs.PLAN_SCHEMA_ANNOTATION_PATH).read()
)


def validate_plan(plan: Annotated[str, PLAN_SCHEMA_ANNOTATION]):

    logger.info(f"Validate plan: {plan}")

    try:
        json_plan = json.loads(plan)
    except json.JSONDecodeError as e:
        logger.error(f"Plan is not a valid JSON: {e}")
        raise ValueError(f"Plan is not a valid JSON: {e}")

    if len(json_plan) == 0:
        logger.error("Plan is empty")
        raise ValueError("Plan is empty")

    for action_id, action in json_plan.items():
        if "mcp-service-endpoint" not in action:
            logger.error(
                f"Action {action_id} is missing the mcp-service-endpoint field"
            )
            raise ValueError(
                f"Action {action_id} is missing the 'mcp-service-endpoint' field"
            )
        if "mcp-tool-name" not in action:
            logger.error(f"Action {action_id} is missing the mcp-tool-name field")
            raise ValueError(f"Action {action_id} is missing the 'mcp-tool-name' field")

        # optional part in case if no parameters are needed for the tool
        # if "mcp-tool-arguments" not in action:
        #    logger.error(f"Action {action_id} is missing the mcp-tool-arguments field")
        #    raise ValueError(f"Action {action_id} is missing the 'mcp-tool-arguments' field")


async def execute_plan(plan: Annotated[str, PLAN_SCHEMA_ANNOTATION]):
    if envs.EXECUTION_STRATEGY == "sequential":
        logger.info("Executing plan sequentially")
        json_plan = json.loads(plan)

        for action_id, action in json_plan.items():
            logger.info(f"Executing action {action_id}")

            mcp_endpoint = action["mcp-service-endpoint"]
            mcp_tool_name = action["mcp-tool-name"]
            mcp_tool_args = action.get("mcp-tool-arguments", {})

            logger.info(
                f"Calling tool {mcp_tool_name} at {mcp_endpoint} with args: {mcp_tool_args}"
            )
            await mcp_client.call_tool(mcp_endpoint, mcp_tool_name, mcp_tool_args)
    elif envs.EXECUTION_STRATEGY == "worker":
        logger.info("Executing plan in a worker")
        # execute plan in a worker
        await mcp_client.call_tool(
            envs.WORKER_ENDPOINT, envs.WORKER_TOOL_NAME, {"str_json_plan": plan}
        )
    else:
        raise ValueError(
            f"Invalid execution strategy: {envs.EXECUTION_STRATEGY}. Scheduler is misconfigured."
        )


@mcp_server.tool
def list_scheduled_jobs() -> Annotated[str, "JSON-formatted list of scheduled jobs"]:
    """List all scheduled jobs."""
    try:
        jobs = scheduler.get_jobs()
        # no need to print the `func` because they all call the same -- MCP tool
        result = {
            job.id: {"args:": job.args, "next_run_time": job.next_run_time}
            for job in jobs
        }
        return pprint.pformat(result, indent=4)
    except Exception as e:
        logger.error(f"Error listing scheduled jobs: {e}")
        return f"Error listing scheduled jobs: {e}"


@mcp_server.tool
def remove_scheduled_job(job_id: Annotated[str, "The id of the job to remove"]):
    """
    Remove a scheduled job by its id.
    """
    logger.info(f"Removing job {job_id}")
    try:
        scheduler.remove_job(job_id)
    except KeyError:
        logger.error(f"Job {job_id} not found")
        return f"Job {job_id} not found"
    except Exception as e:
        logger.error(f"Error removing job {job_id}: {e}")
        return f"Error removing job {job_id}: {e}"
    return "Job removed"


@mcp_server.tool
def schedule_tool_call_by_cron(
    execution_plan: Annotated[str, PLAN_SCHEMA_ANNOTATION],
    year: Annotated[str, "Year to schedule the job at"] = None,
    month: Annotated[str, "Month to schedule the job at"] = None,
    day: Annotated[str, "Day to schedule the job at"] = None,
    week: Annotated[str, "Week to schedule the job at"] = None,
    day_of_week: Annotated[str, "Day of week to schedule the job at"] = None,
    hour: Annotated[str, "Hour to schedule the job at"] = None,
    minute: Annotated[str, "Minute to schedule the job at"] = None,
    second: Annotated[str, "Second to schedule the job at"] = None,
    start_date: Annotated[str, "Start date to schedule the job at"] = None,
    end_date: Annotated[str, "End date to schedule the job at"] = None,
    timezone: Annotated[str, "Timezone to schedule the job at"] = None,
) -> Annotated[str, "Job id of the scheduled job"]:
    """
    Triggers when current time matches all specified time constraints,
    similarly to how the UNIX cron scheduler works.
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

    if len(cron_params) == 0:
        return "Error: all schedule paramers are empty. Need to specfy cron params"

    logger.info(f"Scheduling job by cron with params: {cron_params}")
    try:
        validate_plan(execution_plan)
        job = scheduler.add_job(
            execute_plan, "cron", **cron_params, args=[execution_plan]
        )
        logger.info(f"Scheduled job {job.id}")
        return job.id
    except Exception as e:
        logger.error(f"Error scheduling job by cron: {e}")
        return f"Error scheduling job by cron: {e}"


@mcp_server.tool
def schedule_tool_call_at_interval(
    execution_plan: Annotated[str, PLAN_SCHEMA_ANNOTATION],
    weeks: Annotated[int, "Number of weeks to wait"] = None,
    days: Annotated[int, "Number of days to wait"] = None,
    hours: Annotated[int, "Number of hours to wait"] = None,
    minutes: Annotated[int, "Number of minutes to wait"] = None,
    seconds: Annotated[int, "Number of seconds to wait"] = None,
    start_date: Annotated[
        str, "The date/time to start the job at in %Y-%m-%d format"
    ] = None,
    end_date: Annotated[
        str, "The date/time to end the job at in %Y-%m-%d format"
    ] = None,
    timezone: Annotated[str, "The timezone to use for the job"] = None,
) -> Annotated[str, "Job id of the scheduled job"]:
    """
    Schedule remote MCP call on specified intervals, starting on `start_date` if specified,
    `datetime.now()` + interval otherwise.
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

    if len(interval_params) == 0:
        return "Error: schedule parameters are empty, specify parameters of schedule"

    logger.info(f"Scheduling job by interval with params: {interval_params}")
    try:
        validate_plan(execution_plan)
        job = scheduler.add_job(
            execute_plan, "interval", **interval_params, args=[execution_plan]
        )
        logger.info(f"Scheduled job {job.id}")
        return job.id
    except Exception as e:
        logger.error(f"Error scheduling job by interval: {e}")
        return f"Error scheduling job by interval: {e}"


@mcp_server.tool
def schedule_tool_call_once_at_date(
    execution_plan: Annotated[str, PLAN_SCHEMA_ANNOTATION],
    run_date: Annotated[
        str, "The date/time to run the job at in %Y-%m-%d %H:%M:%S format"
    ],
) -> Annotated[str, "Job id of the scheduled job"]:
    """
    Schedule remote MCP call once at a certain point of time.
    """

    logger.info(f"Scheduling job by date with params: {run_date}")
    try:
        validate_plan(execution_plan)
        job = scheduler.add_job(
            execute_plan,
            "date",
            run_date=datetime.strptime(run_date, "%Y-%m-%d %H:%M:%S"),
            args=[execution_plan],
        )
        logger.info(f"Scheduled job {job.id}")
        return job.id
    except Exception as e:
        logger.error(f"Error scheduling job by date: {e}")
        return f"Error scheduling job by date: {e}"


@mcp_server.tool
def current_datetime() -> Annotated[
    str, "Current date and time with timezone in format %Y/%m/%d %H:%M:%S %Z%z"
]:
    """Returns current date and time with timezone in format %Y/%m/%d %H:%M:%S %Z%z"""
    datetime_now = datetime.now()
    return datetime_now.strftime("%Y/%m/%d %H:%M:%S %Z%z")


@mcp_server.tool(tags=["admin"])
def set_worker_endpoint(worker_endpoint: Annotated[str, "Worker endpoint"]):
    """Sets the worker endpoint"""
    envs.WORKER_ENDPOINT = worker_endpoint
    return "Worker endpoint set"


@mcp_server.tool(tags=["admin"])
def set_worker_tool_name(worker_tool_name: Annotated[str, "Worker tool name"]):
    """Sets the worker tool name"""
    envs.WORKER_TOOL_NAME = worker_tool_name
    return "Worker tool name set"


async def main():
    scheduler.start()

    await mcp_server.run_async(transport="http", host=envs.MCP_HOST, port=envs.MCP_PORT)


if __name__ == "__main__":
    asyncio.run(main())
