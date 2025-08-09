from datetime import datetime

from fastmcp import Client

import src.mcp_client as mcp_client
from src.main import mcp_server


class TestCreate:
    async def test_schedule_once_at_date(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_once_at_date",
                arguments={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                    "run_date": "2025-01-01 12:00:00",
                },
            )

            assert result.content[0].text == "job_123"

            add_job_mock.assert_called_once_with(
                mcp_client.call_tool,
                "date",
                run_date=datetime.strptime("2025-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
                kwargs={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                },
            )

    async def test_schedule_at_interval(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_at_interval",
                arguments={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                    "weeks": 1,
                    "days": 2,
                    "hours": 3,
                    "minutes": 4,
                    "seconds": 5,
                    "start_date": "2025-01-01",
                    "end_date": "2025-01-02",
                    "timezone": "UTC",
                },
            )

            assert result.content[0].text == "job_123"

            add_job_mock.assert_called_once_with(
                mcp_client.call_tool,
                "interval",
                weeks=1,
                days=2,
                hours=3,
                minutes=4,
                seconds=5,
                start_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2025-01-02", "%Y-%m-%d"),
                timezone="UTC",
                kwargs={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                },
            )

    async def test_schedule_by_cron(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_by_cron",
                arguments={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                    "year": "2025",
                    "month": "1",
                    "day": "1",
                    "week": "1",
                    "day_of_week": "1",
                    "hour": "12",
                    "minute": "0",
                    "second": "0",
                    "start_date": "2025-01-01",
                    "end_date": "2025-01-02",
                    "timezone": "UTC",
                },
            )

            assert result.content[0].text == "job_123"

            add_job_mock.assert_called_once_with(
                mcp_client.call_tool,
                "cron",
                year="2025",
                month="1",
                day="1",
                week="1",
                day_of_week="1",
                hour="12",
                minute="0",
                second="0",
                start_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2025-01-02", "%Y-%m-%d"),
                timezone="UTC",
                kwargs={
                    "mcp_endpoint": "http://localhost:8000",
                    "mcp_tool_name": "test_tool",
                    "mcp_tool_args": {"arg1": "value1"},
                },
            )
