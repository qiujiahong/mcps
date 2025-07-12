# weather_server.py
# from typing import List
# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    request: Request = get_http_request()
    user_agent = request.headers.get("user-agent", "Unknown")
    Authorization = request.headers.get("Authorization", "Unknown")
    XCustomHeader = request.headers.get("X-Custom-Header", "Unknown")
    print(f"user_agent = {user_agent}")
    print(f"Authorization = {Authorization}")
    print(f"XCustomHeader = {XCustomHeader}")
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")