/**
 * server.js — MCP GIS Hub (Node.js reference server)
 *
 * Exposes two MCP tools — findLayer and queryFeatures — that make LIVE REST
 * calls to ArcGIS Online and/or ArcGIS Enterprise, depending on the
 * `environment` argument passed by the calling MCP client (e.g. Copilot Studio).
 *
 * Run standalone over stdio:   node server.js
 */
require("dotenv").config();
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { searchPortal, queryLayer } = require("./arcgis");

const TOOLS = [
  {
    name: "findLayer",
    description: "Resolve a human-readable layer name to a service URL in ArcGIS Online or ArcGIS Enterprise.",
    inputSchema: {
      type: "object",
      required: ["environment", "query"],
      properties: {
        environment: { type: "string", enum: ["agol", "enterprise"] },
        query: { type: "string", description: "Free-text title or keyword to search for." },
      },
    },
  },
  {
    name: "queryFeatures",
    description: "Query features from a layer using an ArcGIS-style where clause.",
    inputSchema: {
      type: "object",
      required: ["environment", "layer"],
      properties: {
        environment: { type: "string", enum: ["agol", "enterprise"] },
        layer: { type: "string", description: "Layer title (resolved via findLayer) or a direct service URL." },
        where: { type: "string", default: "1=1" },
        outFields: { type: "array", items: { type: "string" }, default: ["*"] },
        resultRecordCount: { type: "integer", default: 1000 },
      },
    },
  },
];

async function handleFindLayer({ environment, query }) {
  const results = await searchPortal(environment, query);
  if (!results.length) {
    return { content: [{ type: "text", text: `No items found matching "${query}" in ${environment}.` }] };
  }
  const top = results[0];
  const layer = {
    itemId: top.id,
    title: top.title,
    serviceUrl: top.url,
    environment,
  };
  return { content: [{ type: "text", text: JSON.stringify(layer, null, 2) }] };
}

async function handleQueryFeatures({ environment, layer, where, outFields, resultRecordCount }) {
  let serviceUrl = layer;
  if (!/^https?:\/\//.test(layer)) {
    const results = await searchPortal(environment, layer);
    if (!results.length) throw new Error(`Layer "${layer}" not found in ${environment}.`);
    serviceUrl = results[0].url;
  }
  const fc = await queryLayer(environment, serviceUrl, { where, outFields, resultRecordCount });
  return { content: [{ type: "text", text: JSON.stringify(fc, null, 2) }] };
}

async function main() {
  const server = new Server(
    { name: "mcp-gis-hub-node", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler({ method: "tools/list" }, async () => ({ tools: TOOLS }));

  server.setRequestHandler({ method: "tools/call" }, async (req) => {
    const { name, arguments: args } = req.params;
    if (name === "findLayer") return handleFindLayer(args);
    if (name === "queryFeatures") return handleQueryFeatures(args);
    throw new Error(`Unknown tool: ${name}`);
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP GIS Hub (Node) server running over stdio.");
}

if (require.main === module) {
  main().catch((err) => {
    console.error("Fatal error starting server:", err);
    process.exit(1);
  });
}

module.exports = { TOOLS, handleFindLayer, handleQueryFeatures };
