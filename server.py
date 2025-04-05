import logging

from mcp.server.fastmcp import FastMCP

import capabilities.tools as mytools

logging.basicConfig(level=logging.INFO)

server = FastMCP(
    name="My MCP Server",
    description="A server for my custom tools",
)


server.add_tool(mytools.retrieve_augmented_generation)
server.add_tool(mytools.add_information_to_vectorstore)
server.add_tool(mytools.search_web)
server.add_tool(mytools.crawl_url)