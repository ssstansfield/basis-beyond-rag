"""Protocol integration smoke check; run from project root."""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp_entry.py")])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            names = {t.name for t in (await client.list_tools()).tools}
            assert names == {"list_books", "search_books", "get_chunk"}, names
            result = await client.call_tool("list_books", {})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert len(data["books"]) == 2
            result = await client.call_tool("search_books", {"query": "cheapest to deliver", "top_k": 3})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert len(data["results"]) == 3
            chunk = await client.call_tool("get_chunk", {"chunk_id": data["results"][0]["chunk_id"]})
            assert not chunk.isError
            print("MCP initialize / list_tools / list_books / search_books / get_chunk: PASS")


if __name__ == "__main__":
    asyncio.run(main())
