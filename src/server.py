from fastmcp import FastMCP

import envs


mcp = FastMCP(
    name="apscheduler",
)


def main():
    mcp.run(transport="http", host=envs.MCP_HOST, port=envs.MCP_PORT)


if __name__ == "__main__":
    main()
