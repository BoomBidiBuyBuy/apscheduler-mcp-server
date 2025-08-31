from fastmcp import Client
import pytest
from datetime import datetime
import pprint

from src.main import mcp_server


@pytest.mark.asyncio
async def test_list_jobs(mocker):
    get_jobs_mock = mocker.patch(
        "src.main.scheduler.get_jobs",
        return_value=[
            mocker.Mock(
                id="job_123",
                args=["arg1", "arg2"],
                kwargs={"user_id": "user_123", "description": "test_description"},
                next_run_time=datetime.strptime(
                    "2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"
                ),
            ),
            mocker.Mock(
                id="job_456",
                args=["arg3", "arg4"],
                kwargs={"user_id": "user_456", "description": "test_description_2"},
                next_run_time=datetime.strptime(
                    "2025-05-01 16:00:00", "%Y-%m-%d %H:%M:%S"
                ),
            ),
        ],
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "list_scheduled_jobs",
            arguments={"user_id": "user_123"},
        )

    get_jobs_mock.assert_called_once()
    assert result.content[0].text == pprint.pformat(
        {
            "job_123": {
                "args": ["arg1", "arg2"],
                "description": "test_description",
                "next_run_time": datetime.strptime(
                    "2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"
                ),
            }
        },
        indent=4,
    )
