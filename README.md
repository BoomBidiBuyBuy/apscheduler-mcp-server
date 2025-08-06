# aspscheduler-mcp-server

MCP (Model Context Protocol) HTTP server implementation for the [apscheduler](https://github.com/agronholm/apscheduler)

## Install

### Env variables / .env file

Setup environment variables or configure the `.env` file from the `.env.example`

## Development

### Setup

1. Clone repo
2. Install development dependencies:
`uv sync --dev`
3. Create `.env` from `.env.example`

### Running MCP service

```
uv run src/main.py
```

### Running linters

The project uses the `ruff` tool as a linter.

The following command allows to run linter

```
uv run ruff check
```

and this command allow to fix formatting

```
uv run ruff format
```
