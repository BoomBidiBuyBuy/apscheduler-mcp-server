# aspscheduler-mcp-server

MCP (Model Context Protocol) HTTP server implementation for the [apscheduler](https://github.com/agronholm/apscheduler).

## Installation

### Environment Variables / .env File

Set up environment variables or configure the `.env` file using the `.env.example` as a template.

## Development

### Setup

1. Clone the repository.
2. Install development dependencies:
   ```
   uv sync --dev
   ```
3. Create a `.env` file from `.env.example`.

### Running the MCP Service

To start the MCP service, run:
```
uv run src/main.py
```

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
