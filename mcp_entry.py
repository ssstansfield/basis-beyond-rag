"""Absolute-path entry point, independent of the Codex session working directory."""
from src.mcp_server import server

if __name__ == "__main__":
    server.run(transport="stdio")
