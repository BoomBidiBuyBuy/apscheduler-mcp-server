# aspscheduler-mcp-server

MCP (Model Context Protocol) HTTP server implementation for the [apscheduler](https://github.com/agronholm/apscheduler).

## Example / Events flow / scenario (Pizza Friday)

- **Context**: An agent is connected to this scheduler MCP service and to other MCP services:
  - **Pizza ordering MCP**: tool `order_pizza(type-of-pizza, "time to delivery today")`
  - **Email MCP**: tool `send_email(email, message)` to invite colleagues
  - **Bamboo MCP**: tool to retrieve birthdays, e.g. `get_birthdays(window)` where `window` can be `last_week`

- **User request to the agent**: "Every Friday, schedule a pizza order for delivery at 5:00 PM, and schedule an email at 4:45 PM inviting colleagues to Pizza Friday. Include in the invitation the people who had birthdays last week."

- **Agent behavior**:
  - Retrieves available MCP service endpoints and their tools
  - Builds an execution plan
  - Calls one of the scheduling tools in this service with the plan in JSON

- **Scheduler behavior**:
  - Accepts the schedule request and stores the cron triggers
  - When time matches, executes the plan

- **LLM-based worker behavior**:
  - A worker LLM connected to all the MCP services receives the plan at trigger time and executes each action by calling the referenced MCP tools, honoring each action's `condition` field to manage ordering and success dependencies.

There are two independent schedules below: (1) a single action to order pizza at 17:00 every Friday; (2) two actions at 16:45 every Friday — first get last week's birthdays, then send the email. The second action is conditioned on the first succeeding. The message shows a common placeholder pattern to include upstream results; actual interpolation depends on the worker/agent that executes the plan.

### Schedule 1: Order pizza every Friday at 17:00

Tool call input to `schedule_tool_call_by_cron`:

```json
{
  "execution_plan": {
    "order_pizza": {
      "mcp-service-endpoint": "http://pizza-mcp:3001",
      "mcp-tool-name": "order_pizza",
      "mcp-tool-arguments": {
        "type-of-pizza": "assorted",
        "time to delivery today": "17:00"
      }
    }
  },
  "day_of_week": "fri",
  "hour": "17",
  "minute": "00",
  "timezone": "America/Los_Angeles"
}
```

### Schedule 2: Fetch birthdays then send email every Friday at 16:45

Tool call input to `schedule_tool_call_by_cron`:

```json
{
  "execution_plan": {
    "fetch_birthdays": {
      "mcp-service-endpoint": "http://bamboo-mcp:3003",
      "mcp-tool-name": "get_birthdays",
      "mcp-tool-arguments": {
        "window": "last_week"
      },
      "condition": "executes first"
    },
    "send_email": {
      "mcp-service-endpoint": "http://email-mcp:3002",
      "mcp-tool-name": "send_email",
      "mcp-tool-arguments": {
        "email": "team@company.com",
        "message": "Welcome Pizza Friday in the kitchen at 4:45pm! Birthdays: ${fetch_birthdays.result.summary}"
      },
      "condition": "executes only if fetch_birthdays was successful"
    }
  },
  "day_of_week": "fri",
  "hour": "16",
  "minute": "45",
  "timezone": "America/Los_Angeles"
}
```

Notes:
- **Endpoints** are examples; use your actual MCP service URLs.
- If you enable the worker strategy, the plan is forwarded to the worker MCP tool and executed there; ensure that worker supports referencing previous action outputs if you rely on placeholders in later actions.

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
