from datetime import datetime
import pytest

from fastmcp import Client
from unittest.mock import ANY

from src.main import mcp_server, validate_plan, execute_plan


class TestCreate:
    async def test_schedule_once_at_date(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_once_at_date",
                arguments={
                    "execution_plan": '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}',
                    "run_date": "2025-01-01 12:00:00",
                },
            )

            assert result.content[0].text == "job_123"

            add_job_mock.assert_called_once_with(
                ANY,  # to get rid of checking function references
                "date",
                run_date=datetime.strptime("2025-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
                args=[
                    '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
                ],
            )

    async def test_schedule_at_interval(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_at_interval",
                arguments={
                    "execution_plan": '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}',
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
                ANY,
                "interval",
                weeks=1,
                days=2,
                hours=3,
                minutes=4,
                seconds=5,
                start_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2025-01-02", "%Y-%m-%d"),
                timezone="UTC",
                args=[
                    '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
                ],
            )

    async def test_schedule_by_cron(self, mocker):
        add_job_mock = mocker.patch(
            "src.main.scheduler.add_job", return_value=mocker.Mock(id="job_123")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "schedule_tool_call_by_cron",
                arguments={
                    "execution_plan": '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}',
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
                ANY,
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
                args=[
                    '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
                ],
            )


class TestValidatePlan:
    def test_validate_plan_valid(self):
        validate_plan(
            '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
        )

    def test_validate_plan_valid_no_arguments(self):
        validate_plan(
            '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool"}}'
        )

    def test_invalid_json(self):
        with pytest.raises(ValueError):
            validate_plan('[{"action_1":}]')

    def test_validate_plan_empty(self):
        with pytest.raises(ValueError):
            validate_plan("{}")

    def test_validate_plan_missing_mcp_service_endpoint(self):
        with pytest.raises(ValueError):
            validate_plan(
                '{"action_1": {"mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
            )

    def test_validate_plan_missing_mcp_tool_name(self):
        with pytest.raises(ValueError):
            validate_plan(
                '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-arguments": {"arg1": "value1"}}}'
            )

    def test_validate_plan_process_mcp(self):
        """Test validation of plan with process-based MCP server"""
        validate_plan(
            '{"action_1": {"mcp-service-endpoint": "command:uvx:[\'mcp-server-reddit\']", "mcp-tool-name": "mcp_reddit_get_frontpage_posts", "mcp-tool-arguments": {"limit": 5}}}'
        )


class TestExecutePlan:
    @pytest.mark.asyncio
    async def test_execute_plan_sequential_single_action(self, mocker):
        execute_plan_mock = mocker.patch("mcp_client.call_tool")

        await execute_plan(
            '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
        )

        execute_plan_mock.assert_called_once_with(
            "http://localhost:8000", "test_tool", {"arg1": "value1"}
        )

    @pytest.mark.asyncio
    async def test_execute_plan_sequential_multiple_actions(self, mocker):
        execute_plan_mock = mocker.patch("mcp_client.call_tool")

        await execute_plan(
            '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}, "action_2": {"mcp-service-endpoint": "http://localhost:8001", "mcp-tool-name": "test_tool_2", "mcp-tool-arguments": {"arg2": "value2"}}}'
        )

        execute_plan_mock.assert_has_calls(
            [
                mocker.call("http://localhost:8000", "test_tool", {"arg1": "value1"}),
                mocker.call("http://localhost:8001", "test_tool_2", {"arg2": "value2"}),
            ]
        )

    @pytest.mark.asyncio
    async def test_execute_plan_with_worker(self, mocker):
        mocker.patch("src.main.envs.EXECUTION_STRATEGY", "worker")
        mocker.patch("src.main.envs.WORKER_ENDPOINT", "http://localhost:8000")
        mocker.patch("src.main.envs.WORKER_TOOL_NAME", "worker_tool")

        execute_plan_mock = mocker.patch("mcp_client.call_tool")

        await execute_plan(
            '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
        )

        execute_plan_mock.assert_called_once_with(
            "http://localhost:8000",
            "worker_tool",
            {
                "execution_plan": '{"action_1": {"mcp-service-endpoint": "http://localhost:8000", "mcp-tool-name": "test_tool", "mcp-tool-arguments": {"arg1": "value1"}}}'
            },
        )

    @pytest.mark.asyncio
    async def test_execute_plan_process_mcp(self, mocker):
        """Test execution of plan with process-based MCP server"""
        execute_plan_mock = mocker.patch("mcp_client.call_tool")

        await execute_plan(
            '{"action_1": {"mcp-service-endpoint": "command:uvx:[\'mcp-server-reddit\']", "mcp-tool-name": "mcp_reddit_get_frontpage_posts", "mcp-tool-arguments": {"limit": 5}}}'
        )

        execute_plan_mock.assert_called_once_with(
            "command:uvx:['mcp-server-reddit']", 
            "mcp_reddit_get_frontpage_posts", 
            {"limit": 5}
        )
