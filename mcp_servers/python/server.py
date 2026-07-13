"""
server.py — MCP GIS Hub (Python reference server)

Exposes two MCP tools — findLayer and queryFeatures — that make LIVE REST
calls to ArcGIS Online and/or ArcGIS Enterprise, depending on the
`environment` argument passed by the calling MCP client (e.g. Copilot Studio).

Run standalone over stdio:  python server.py
"""
import asyncio
import json
import os

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from arcgis_client import search_portal, query_layer

load_dotenv()

server = Server("mcp-gis-hub-python")

TOOLS = [
    Tool(
        name="findLayer",
        description="Resolve a human-readable layer name to a service URL in ArcGIS Online or ArcGIS Enterprise.",
        inputSchema={
            "type": "object",
            "required": ["environment", "query"],
            "properties": {
                "environment": {"type": "string", "enum": ["agol", "enterprise"]},
                "query": {"type": "string", "description": "Free-text title or keyword to search for."},
            },
        },
    ),
    Tool(
        name="queryFeatures",
        description="Query features from a layer using an ArcGIS-style where clause.",
        inputSchema={
            "type": "object",
            "required": ["environment", "layer"],
            "properties": {
                "environment": {"type": "string", "enum": ["agol", "enterprise"]},
                "layer": {"type": "string", "description": "Layer title (resolved via findLayer) or a direct service URL."},
                "where": {"type": "string", "default": "1=1"},
                "outFields": {"type": "array", "items": {"type": "string"}, "default": ["*"]},
                "resultRecordCount": {"type": "integer", "default": 1000},
            },
        },
    ),
]


@server.list_tools()
async def list_tools():
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "findLayer":
        return await handle_find_layer(arguments)
    if name == "queryFeatures":
        return await handle_query_features(arguments)
    raise ValueError(f"Unknown tool: {name}")


async def handle_find_layer(args: dict):
    environment = args["environment"]
    query = args["query"]
    results = search_portal(environment, query)
    if not results:
        return [TextContent(type="text", text=f'No items found matching "{query}" in {environment}.')]

    top = results[0]
    layer = {
        "itemId": top.get("id"),
        "title": top.get("title"),
        "serviceUrl": top.get("url"),
        "environment": environment,
    }
    return [TextContent(type="text", text=json.dumps(layer, indent=2))]


async def handle_query_features(args: dict):
    environment = args["environment"]
    layer = args["layer"]
    where = args.get("where", "1=1")
    out_fields = args.get("outFields", ["*"])
    result_record_count = args.get("resultRecordCount", 1000)

    service_url = layer
    if not layer.startswith("http"):
        results = search_portal(environment, layer)
        if not results:
            raise ValueError(f'Layer "{layer}" not found in {environment}.')
        service_url = results[0]["url"]

    fc = query_layer(environment, service_url, where=where, out_fields=out_fields, result_record_count=result_record_count)
    return [TextContent(type="text", text=json.dumps(fc, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
