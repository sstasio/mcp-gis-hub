"""
Lightweight smoke test — verifies the module loads and tool schema is well-formed.
Does NOT hit live ArcGIS endpoints in CI (no credentials available there).
"""
from server import TOOLS

def test_tool_count():
    assert len(TOOLS) == 2

def test_tool_names():
    names = {t.name for t in TOOLS}
    assert names == {"findLayer", "queryFeatures"}

if __name__ == "__main__":
    test_tool_count()
    test_tool_names()
    print("Python MCP server smoke test passed:", [t.name for t in TOOLS])
