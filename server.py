from mcp.server.fastmcp import FastMCP

import capabilities.tools as mytools

server = FastMCP(
    name="My MCP Server",
    description="A server for my custom tools",
)

server.add_tool(mytools.add)
server.add_tool(mytools.subtract)
server.add_tool(mytools.multiply)
server.add_tool(mytools.divide)
