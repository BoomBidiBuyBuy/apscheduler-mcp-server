from fastmcp import Client

from src.main import mcp_server


class TestRemove:
    async def test_remove_scheduled_job(self, mocker):
        remove_job_mock = mocker.patch("src.main.scheduler.remove_job")

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "remove_scheduled_job", arguments={"job_id": "job_123"}
            )

            assert result.content[0].text == "Job removed"

            remove_job_mock.assert_called_once_with("job_123")

    async def test_remove_scheduled_job_not_found(self, mocker):
        remove_job_mock = mocker.patch(
            "src.main.scheduler.remove_job", side_effect=KeyError("Job not found")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "remove_scheduled_job", arguments={"job_id": "job_123"}
            )

            assert result.content[0].text == "Job job_123 not found"

            remove_job_mock.assert_called_once_with("job_123")

    async def test_remove_scheduled_job_error(self, mocker):
        remove_job_mock = mocker.patch(
            "src.main.scheduler.remove_job", side_effect=Exception("Error removing job")
        )

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "remove_scheduled_job", arguments={"job_id": "job_123"}
            )

            assert (
                result.content[0].text
                == "Error removing job job_123: Error removing job"
            )

            remove_job_mock.assert_called_once_with("job_123")
