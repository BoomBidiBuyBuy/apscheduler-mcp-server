# aspscheduler-mcp-server

MCP (Model Context Protocol) HTTP server implementation for the [apscheduler](https://github.com/agronholm/apscheduler).

## Installation

### Environment Variables / .env File

Set up environment variables or configure the `.env` file using the `.env.example` as a template.

Common variables:

- `MCP_HOST` and `MCP_PORT`: Configure the HTTP host and port the service binds to and exposes. Examples are provided in `.env.example`.

## Execution strategies

This service supports two strategies for executing an `execution_plan`:

- **sequential (default)**: Executes each action one-by-one in this service process. Set with `EXECUTION_STRATEGY=sequential` (default when unset).
- **worker**: Forwards the whole plan to a worker MCP tool which then executes the actions. Enable with `EXECUTION_STRATEGY=worker`.

When using the worker strategy, configure both:

- `WORKER_ENDPOINT`: The worker MCP service endpoint
- `WORKER_TOOL_NAME`: The worker MCP tool name that accepts the plan (called with `{ "execution_plan": <plan> }`)

You can set these via environment variables (see `.env.example`) or at runtime via MCP tools tagged `admin`:

- `set_worker_endpoint(worker_endpoint)` — sets `WORKER_ENDPOINT`
- `set_worker_tool_name(worker_tool_name)` — sets `WORKER_TOOL_NAME`

## Execution plan schema

The `execution_plan` parameter annotation/schema is defined in `plan-schema.ann`. The format of this file is not fixed; it is used as a description shown to MCP agents so they can read and populate the plan. Minimum required fields for every action are:

- `mcp-service-endpoint`
- `mcp-tool-name`

Optional per-action field:

- `mcp-tool-arguments`

You can override the annotation file path using the `PLAN_SCHEMA_ANNOTATION_PATH` environment variable (defaults to `plan-schema.ann`).

## Docker

A `Dockerfile` is provided so you can build and run the service in a container.

Build the image:
```
docker build -t apscheduler-mcp-server:latest .
```

Run the container (example maps host port 3000 to container port 3000):
```
docker run --rm \
  -p 3000:3000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=3000 \
  --env-file .env \
  apscheduler-mcp-server:latest
```

Note: Ensure `MCP_HOST` is set to `0.0.0.0` in the container so the HTTP server is reachable from outside the container.

## Development

### Setup

1. Clone the repository.
2. Install development dependencies:
   ```
   uv sync --dev
   ```
3. Create a `.env` file from `.env.example`.

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to automatically check code style with `ruff` before each commit.

To set up pre-commit hooks, run:
```
uv run pre-commit install
```

This will ensure that `ruff` checks are run automatically before every commit.

### Running the MCP Service

To start the MCP service, run:
```
uv run --env-file .env src/main.py
```

### Available MCP tools

- `list_scheduled_jobs()` — Lists all scheduled jobs (new)
- `remove_scheduled_job(job_id)` — Removes a scheduled job by id
- `schedule_tool_call_by_cron(execution_plan, ...)` — Cron-style scheduling
- `schedule_tool_call_at_interval(execution_plan, ...)` — Fixed interval scheduling
- `schedule_tool_call_once_at_date(execution_plan, run_date)` — One-off scheduling
- `set_worker_endpoint(worker_endpoint)` — Admin tool to set `WORKER_ENDPOINT`
- `set_worker_tool_name(worker_tool_name)` — Admin tool to set `WORKER_TOOL_NAME`

### Running Tests

To run the test suite, use:
```
uv run --dev pytest
```

### Running Linters

This project uses the `ruff` tool as a linter.

To check code style and linting issues, run:
```
uv run ruff check
```

To automatically fix formatting issues, run:
```
uv run ruff format
```
