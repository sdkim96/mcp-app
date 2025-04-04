import logging

from mcp.server.fastmcp import FastMCP

import capabilities.tools as mytools

logging.basicConfig(level=logging.INFO)

server = FastMCP(
    name="My MCP Server",
    description="A server for my custom tools",
)

server.add_tool(mytools.add)
server.add_tool(mytools.subtract)
server.add_tool(mytools.multiply)
server.add_tool(mytools.divide)

server.add_tool(mytools.retrieve_augmented_generation_of_me)
server.add_tool(mytools.add_information_to_vectorstore)