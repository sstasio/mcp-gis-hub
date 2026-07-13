/**
 * Lightweight smoke test — verifies the module loads and tool schema is well-formed.
 * Does NOT hit live ArcGIS endpoints in CI (no credentials available there).
 */
const assert = require("assert");
const { TOOLS } = require("../server");

assert.strictEqual(TOOLS.length, 2, "expected exactly 2 MCP tools");
assert.ok(TOOLS.find((t) => t.name === "findLayer"), "findLayer tool missing");
assert.ok(TOOLS.find((t) => t.name === "queryFeatures"), "queryFeatures tool missing");

console.log("Node MCP server smoke test passed:", TOOLS.map((t) => t.name).join(", "));
