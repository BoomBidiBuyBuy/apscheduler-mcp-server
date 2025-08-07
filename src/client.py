import asyncio

from fastmcp.client import Client


async def main():
    client = Client("http://0.0.0.0:8000/mcp/")

    async with client:

        tools = await client.list_tools()

        print(tools)


if __name__ == "__main__":
    asyncio.run(main())
