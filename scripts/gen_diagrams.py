#!/usr/bin/env python3
"""
Generates clean, consistent SVG architecture diagrams for the MCP GIS Hub site.
Pure-python SVG string templating (no external deps) so labels stay crisp/exact.
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "assets", "img")
os.makedirs(OUT_DIR, exist_ok=True)

BLUE = "#0079c1"
BLUE_DARK = "#005e96"
GREEN = "#2e8b57"
INK = "#14212b"
MUTED = "#5a6b78"
BORDER = "#dde3e8"
BG = "#f6f8fa"
SURFACE = "#ffffff"
AMBER = "#c17a00"

FONT = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"


def svg_header(w, h, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{title}">\n'
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{BG}"/>\n'
        f'<defs>\n'
        f'  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">\n'
        f'    <path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/>\n'
        f'  </marker>\n'
        f'  <marker id="arrowBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">\n'
        f'    <path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/>\n'
        f'  </marker>\n'
        f'  <marker id="arrowGreen" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">\n'
        f'    <path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/>\n'
        f'  </marker>\n'
        f'</defs>\n'
        f'<text x="24" y="34" font-family="{FONT}" font-size="20" font-weight="700" fill="{INK}">{title}</text>\n'
    )


def svg_footer():
    return "</svg>\n"


def box(x, y, w, h, label, sub=None, fill=SURFACE, stroke=BORDER, text_fill=INK, rx=12, bold=True, icon=None):
    fw = 700 if bold else 600
    s = f'<g>\n<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>\n'
    cx = x + w / 2
    ty = y + h / 2 - (6 if sub else -2)
    if icon:
        s += icon(cx, y + 26)
        ty += 14
    s += f'<text x="{cx}" y="{ty}" font-family="{FONT}" font-size="15" font-weight="{fw}" fill="{text_fill}" text-anchor="middle">{label}</text>\n'
    if sub:
        s += f'<text x="{cx}" y="{ty+20}" font-family="{FONT}" font-size="11.5" fill="{MUTED}" text-anchor="middle">{sub}</text>\n'
    s += "</g>\n"
    return s


def cloud_icon(cx, cy):
    return (
        f'<g transform="translate({cx-16},{cy-10})" fill="{BLUE}" opacity="0.85">'
        f'<circle cx="10" cy="12" r="9"/><circle cx="20" cy="8" r="11"/><circle cx="30" cy="13" r="8"/>'
        f'<rect x="6" y="12" width="28" height="10" rx="5"/></g>'
    )


def server_icon(cx, cy):
    return (
        f'<g transform="translate({cx-14},{cy-11})" fill="{GREEN}" opacity="0.9">'
        f'<rect x="0" y="0" width="28" height="8" rx="2"/>'
        f'<rect x="0" y="10" width="28" height="8" rx="2"/>'
        f'<rect x="0" y="20" width="28" height="8" rx="2"/>'
        f'<circle cx="24" cy="4" r="1.4" fill="white"/><circle cx="24" cy="14" r="1.4" fill="white"/><circle cx="24" cy="24" r="1.4" fill="white"/>'
        f'</g>'
    )


def user_icon(cx, cy):
    return (
        f'<g transform="translate({cx-8},{cy-12})" fill="{INK}" opacity="0.75">'
        f'<circle cx="8" cy="6" r="6"/><path d="M0,26 Q8,12 16,26 Z"/></g>'
    )


def hex_icon(cx, cy):
    return (
        f'<g transform="translate({cx-12},{cy-12})" fill="none" stroke="{BLUE_DARK}" stroke-width="2">'
        f'<polygon points="12,0 24,6 24,18 12,24 0,18 0,6"/></g>'
    )


def lock_icon(cx, cy):
    return (
        f'<g transform="translate({cx-9},{cy-10})" fill="none" stroke="{AMBER}" stroke-width="2">'
        f'<rect x="1" y="9" width="16" height="12" rx="2"/><path d="M4,9 V6 a5,5 0 0 1 10,0 v3"/></g>'
    )


def arrow(x1, y1, x2, y2, label=None, color=MUTED, marker="arrow", dash=False, curve=None, label_bg=BG):
    d = f'M{x1},{y1} '
    if curve:
        d += f'Q{curve[0]},{curve[1]} {x2},{y2}'
    else:
        d += f'L{x2},{y2}'
    dash_attr = ' stroke-dasharray="6,4"' if dash else ""
    s = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"{dash_attr} marker-end="url(#{marker})"/>\n'
    if label:
        mx = curve[0] if curve else (x1 + x2) / 2
        my = (curve[1] - 10) if curve else (y1 + y2) / 2 - 8
        s += f'<rect x="{mx-len(label)*3.6-6}" y="{my-13}" width="{len(label)*7.2+12}" height="18" fill="{label_bg}"/>\n'
        s += f'<text x="{mx}" y="{my}" font-family="{FONT}" font-size="12" fill="{color}" text-anchor="middle" font-weight="600">{label}</text>\n'
    return s


def wrap(body, w, h, title):
    return svg_header(w, h, title) + body + svg_footer()


def write(name, content):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path)


# ------------------------------------------------------------------
# 1. MCP Architecture Diagram
# ------------------------------------------------------------------
def diagram_1():
    w, h = 1040, 460
    b = ""
    b += box(40, 90, 190, 90, "Microsoft Copilot", "Natural-language client", icon=user_icon)
    b += box(280, 90, 190, 90, "Copilot Studio", "Orchestration / agent runtime", icon=hex_icon)
    b += box(520, 170, 220, 110, "MCP Server", "Node.js + Python tool host", fill="#eaf4fb", stroke=BLUE, icon=hex_icon)
    b += box(800, 90, 200, 90, "ArcGIS Online", "Cloud REST API", fill="#eaf4fb", stroke=BLUE, icon=cloud_icon)
    b += box(800, 260, 200, 90, "ArcGIS Enterprise", "On-prem REST API", fill="#eaf7f0", stroke=GREEN, icon=server_icon)

    b += arrow(230, 135, 280, 135, "NL request", BLUE, "arrowBlue")
    b += arrow(470, 135, 520, 200, "Tool invocation", BLUE, "arrowBlue", curve=(500, 150))
    b += arrow(740, 220, 800, 150, "REST call", BLUE, "arrowBlue", curve=(770, 170))
    b += arrow(740, 245, 800, 300, "REST call", GREEN, "arrowGreen", curve=(770, 260))
    b += arrow(800, 170, 745, 235, "JSON response", MUTED, "arrow", dash=True, curve=(775, 200))
    b += arrow(800, 320, 745, 260, "JSON response", MUTED, "arrow", dash=True, curve=(775, 300))

    b += f'<text x="40" y="410" font-family="{FONT}" font-size="12.5" fill="{MUTED}">Copilot Studio calls MCP tools (findLayer, queryFeatures) which route to the correct ArcGIS environment based on config.</text>'
    write("diagram-01-mcp-architecture.svg", wrap(b, w, h, "1 · MCP Architecture"))


# ------------------------------------------------------------------
# 2. Copilot Studio + MCP Workflow
# ------------------------------------------------------------------
def diagram_2():
    w, h = 1080, 360
    stages = ["User Prompt", "Copilot Studio\nTopic Match", "MCP Tool\nSelection", "REST API\nExecution", "Response\nFormatting", "Answer to User"]
    b = ""
    x = 30
    bw = 155
    gap = 20
    for i, s in enumerate(stages):
        label, sub = (s.split("\n") + [None])[:2]
        fill = "#eaf4fb" if i in (2, 3) else SURFACE
        stroke = BLUE if i in (2, 3) else BORDER
        b += box(x, 140, bw, 90, label, sub, fill=fill, stroke=stroke)
        if i < len(stages) - 1:
            b += arrow(x + bw, 185, x + bw + gap, 185, marker="arrowBlue", color=BLUE)
        x += bw + gap
    b += f'<text x="30" y="90" font-family="{FONT}" font-size="13" fill="{MUTED}">Sequential turn-by-turn flow inside a single Copilot Studio conversation turn.</text>'
    write("diagram-02-copilot-studio-workflow.svg", wrap(b, w, h, "2 · Copilot Studio + MCP Workflow"))


# ------------------------------------------------------------------
# 3. ArcGIS Online Integration Flow
# ------------------------------------------------------------------
def diagram_3():
    w, h = 1000, 420
    b = ""
    b += box(40, 60, 200, 80, "MCP Server", "Tool: findLayer / queryFeatures", fill="#eaf4fb", stroke=BLUE, icon=hex_icon)
    b += box(330, 40, 220, 70, "OAuth 2.0 Token", "www.arcgis.com/sharing/rest/oauth2/token", icon=lock_icon)
    b += box(330, 150, 220, 70, "Portal Search API", "/sharing/rest/search")
    b += box(330, 260, 220, 70, "Feature Service", "/FeatureServer/{id}/query")
    b += box(650, 150, 260, 90, "ArcGIS Online", "Hosted feature layers (cloud)", fill="#eaf4fb", stroke=BLUE, icon=cloud_icon)

    b += arrow(240, 90, 330, 75, "1. Authenticate", BLUE, "arrowBlue")
    b += arrow(240, 110, 330, 175, "2. Find item", BLUE, "arrowBlue", curve=(280, 150))
    b += arrow(240, 130, 330, 285, "3. Query features", BLUE, "arrowBlue", curve=(280, 230))
    b += arrow(550, 75, 650, 170, color=MUTED, dash=True, curve=(600, 110))
    b += arrow(550, 185, 650, 195, color=MUTED, dash=True)
    b += arrow(550, 295, 650, 220, color=MUTED, dash=True, curve=(600, 260))
    b += f'<text x="40" y="380" font-family="{FONT}" font-size="12.5" fill="{MUTED}">Token is cached and refreshed automatically by the MCP server before each downstream call.</text>'
    write("diagram-03-agol-integration-flow.svg", wrap(b, w, h, "3 · ArcGIS Online (AGOL) Integration Flow"))


# ------------------------------------------------------------------
# 4. ArcGIS Enterprise Integration Flow
# ------------------------------------------------------------------
def diagram_4():
    w, h = 1000, 420
    b = ""
    b += box(40, 60, 200, 80, "MCP Server", "Tool: findLayer / queryFeatures", fill="#eaf7f0", stroke=GREEN, icon=hex_icon)
    b += box(330, 40, 240, 70, "Portal Token (generateToken)", "/portal/sharing/rest/generateToken")
    b += box(330, 150, 240, 70, "Enterprise Portal Search", "/portal/sharing/rest/search")
    b += box(330, 260, 240, 70, "Hosted / Map Service", "/server/rest/services/.../query")
    b += box(670, 150, 260, 90, "ArcGIS Enterprise", "On-prem / VPC portal + server", fill="#eaf7f0", stroke=GREEN, icon=server_icon)

    b += arrow(240, 90, 330, 75, "1. Authenticate (SAML/Basic)", GREEN, "arrowGreen")
    b += arrow(240, 110, 330, 175, "2. Find item", GREEN, "arrowGreen", curve=(280, 150))
    b += arrow(240, 130, 330, 285, "3. Query features", GREEN, "arrowGreen", curve=(280, 230))
    b += arrow(570, 75, 670, 170, color=MUTED, dash=True, curve=(620, 110))
    b += arrow(570, 185, 670, 195, color=MUTED, dash=True)
    b += arrow(570, 295, 670, 220, color=MUTED, dash=True, curve=(620, 260))
    b += f'<text x="40" y="380" font-family="{FONT}" font-size="12.5" fill="{MUTED}">Requires VPN / private network reachability from the MCP host to the Enterprise portal + server.</text>'
    write("diagram-04-enterprise-integration-flow.svg", wrap(b, w, h, "4 · ArcGIS Enterprise Integration Flow"))


# ------------------------------------------------------------------
# 5. Dual-Environment Routing Diagram
# ------------------------------------------------------------------
def diagram_5():
    w, h = 900, 420
    b = ""
    b += box(40, 165, 200, 90, "MCP Router", "Reads ENV.target per request", fill="#fff7ea", stroke=AMBER, icon=hex_icon)
    b += box(330, 60, 220, 90, "AGOL Adapter", "OAuth2 · REST · cloud", fill="#eaf4fb", stroke=BLUE, icon=cloud_icon)
    b += box(330, 270, 220, 90, "Enterprise Adapter", "Token auth · REST · on-prem", fill="#eaf7f0", stroke=GREEN, icon=server_icon)
    b += box(630, 60, 220, 90, "ArcGIS Online", "org: sfgov.maps.arcgis.com")
    b += box(630, 270, 220, 90, "ArcGIS Enterprise", "internal portal")

    b += arrow(240, 190, 330, 110, "target=agol", BLUE, "arrowBlue", curve=(290, 140))
    b += arrow(240, 230, 330, 310, "target=enterprise", GREEN, "arrowGreen", curve=(290, 270))
    b += arrow(550, 105, 630, 105, color=BLUE, marker="arrowBlue")
    b += arrow(550, 315, 630, 315, color=GREEN, marker="arrowGreen")
    b += f'<text x="40" y="130" font-family="{FONT}" font-size="12.5" fill="{MUTED}">A single tool call fans out to the correct environment via a config flag or per-request parameter.</text>'
    write("diagram-05-dual-environment-routing.svg", wrap(b, w, h, "5 · Dual-Environment Routing (AGOL + Enterprise)"))


# ------------------------------------------------------------------
# 6. MCP Tool Execution Sequence Diagram
# ------------------------------------------------------------------
def diagram_6():
    w, h = 1000, 440
    lanes = ["Copilot Studio", "MCP Server", "Auth Provider", "ArcGIS REST API"]
    lane_x = [80, 340, 600, 860]
    b = ""
    for x, lane in zip(lane_x, lanes):
        b += f'<line x1="{x}" y1="70" x2="{x}" y2="400" stroke="{BORDER}" stroke-width="2"/>\n'
        b += box(x - 90, 30, 180, 44, lane, rx=8, fill="#eaf4fb", stroke=BLUE)
    steps = [
        (0, 1, 110, "call_tool(queryFeatures)"),
        (1, 2, 160, "get/validate token"),
        (2, 1, 200, "token OK"),
        (1, 3, 250, "GET /query?where=..."),
        (3, 1, 300, "GeoJSON / FeatureSet"),
        (1, 0, 350, "structured result"),
    ]
    for a, bnum, y, label in steps:
        x1, x2 = lane_x[a], lane_x[bnum]
        col = BLUE if x2 >= x1 else MUTED
        marker = "arrowBlue" if x2 >= x1 else "arrow"
        b += arrow(x1, y, x2, y, label, col, marker)
    write("diagram-06-tool-execution-sequence.svg", wrap(b, w, h, "6 · MCP Tool Execution Sequence"))


# ------------------------------------------------------------------
# 7. MCP Deployment Pipeline (CI/CD)
# ------------------------------------------------------------------
def diagram_7():
    w, h = 1080, 300
    stages = [
        ("Push to main", None),
        ("GitHub Actions\nTriggered", None),
        ("Install deps\n(Node + Python)", None),
        ("Run MCP\nserver smoke tests", None),
        ("Build static site\n(site/)", None),
        ("Deploy to\nGitHub Pages", None),
    ]
    b = ""
    x = 30; bw = 155; gap = 20
    for i, (label, sub) in enumerate(stages):
        l, s2 = (label.split("\n") + [None])[:2]
        fill = "#eaf4fb" if i == 1 else ("#eaf7f0" if i == 5 else SURFACE)
        stroke = BLUE if i == 1 else (GREEN if i == 5 else BORDER)
        b += box(x, 110, bw, 90, l, s2, fill=fill, stroke=stroke)
        if i < len(stages) - 1:
            b += arrow(x + bw, 155, x + bw + gap, 155, marker="arrowBlue", color=BLUE)
        x += bw + gap
    b += f'<text x="30" y="90" font-family="{FONT}" font-size="13" fill="{MUTED}">.github/workflows/deploy.yml — CI validates both MCP servers before publishing docs.</text>'
    write("diagram-07-deployment-pipeline.svg", wrap(b, w, h, "7 · MCP Deployment Pipeline (CI/CD)"))


# ------------------------------------------------------------------
# 8. GitHub Pages Website Structure Diagram
# ------------------------------------------------------------------
def diagram_8():
    w, h = 900, 480
    b = ""
    b += box(360, 30, 220, 60, "repo root /", bold=True, fill="#eaf4fb", stroke=BLUE)
    items = [
        (60, 130, "site/", "Published to GitHub Pages"),
        (60, 210, "├─ index.html, agol.html,\nenterprise.html, comparison.html", None),
        (60, 290, "└─ assets/css, assets/img,\nassets/js", None),
        (500, 130, "mcp_servers/", "Node + Python MCP tool hosts"),
        (500, 210, ".github/workflows/", "CI + Pages deploy"),
        (500, 290, "openapi/", "mcp.yaml (Swagger spec)"),
    ]
    for x, y, label, sub in items:
        l, s2 = (label.split("\n") + [None])[:2]
        b += box(x, y, 340, 65, l, sub or s2, fill=SURFACE)
    b += arrow(470, 90, 230, 130, color=MUTED, curve=(350, 100))
    b += arrow(470, 90, 670, 130, color=MUTED, curve=(580, 100))
    b += arrow(230, 195, 230, 210, color=MUTED)
    b += arrow(230, 275, 230, 290, color=MUTED)
    b += arrow(670, 195, 670, 210, color=MUTED)
    b += arrow(670, 275, 670, 290, color=MUTED)
    b += f'<text x="60" y="420" font-family="{FONT}" font-size="12.5" fill="{MUTED}">Only /site is served by GitHub Pages; server + spec folders are for local dev and CI.</text>'
    write("diagram-08-repo-site-structure.svg", wrap(b, w, h, "8 · GitHub Pages Repo &amp; Site Structure"))


# ------------------------------------------------------------------
# 9. Unified GIS Data Flow (AGOL <-> Enterprise <-> MCP <-> Copilot)
# ------------------------------------------------------------------
def diagram_9():
    w, h = 460, 460
    cx, cy = 230, 230
    b = box(cx - 90, cy - 40, 180, 80, "MCP Server", "Unified data layer", fill="#eaf4fb", stroke=BLUE, icon=hex_icon)
    nodes = [
        (cx, cy - 170, "Microsoft Copilot", user_icon),
        (cx + 170, cy - 60, "ArcGIS Online", cloud_icon),
        (cx + 170, cy + 100, "ArcGIS Enterprise", server_icon),
        (cx - 170, cy + 100, "webTMA / Snowflake", server_icon),
        (cx - 170, cy - 60, "Survey123 Data", user_icon),
    ]
    for nx, ny, label, icon in nodes:
        b += box(nx - 80, ny - 35, 160, 70, label, icon=icon)
    b += arrow(cx, cy - 100, cx, cy - 40, color=BLUE, marker="arrowBlue")
    b += arrow(cx + 90, cy - 20, cx + 100, cy - 20, color=BLUE, marker="arrowBlue")
    b += arrow(cx + 90, cy + 20, cx + 100, cy + 60, color=GREEN, marker="arrowGreen")
    b += arrow(cx - 90, cy + 20, cx - 100, cy + 60, color=GREEN, marker="arrowGreen")
    b += arrow(cx - 90, cy - 20, cx - 100, cy - 20, color=BLUE, marker="arrowBlue")
    b += f'<text x="20" y="440" font-family="{FONT}" font-size="12" fill="{MUTED}">MCP Server acts as the single integration point across cloud and on-prem GIS sources.</text>'
    write("diagram-09-unified-gis-data-flow.svg", wrap(b, w, h, "9 · Unified GIS Data Flow"))


# ------------------------------------------------------------------
# 10. Authentication & Token Flow Diagram
# ------------------------------------------------------------------
def diagram_10():
    w, h = 1000, 320
    b = ""
    b += box(30, 110, 190, 90, "MCP Server", "Requests + caches token", icon=hex_icon)
    b += box(280, 60, 210, 80, "AGOL OAuth2", "client_credentials grant", fill="#eaf4fb", stroke=BLUE, icon=lock_icon)
    b += box(280, 180, 210, 80, "Enterprise generateToken", "username/password or SAML", fill="#eaf7f0", stroke=GREEN, icon=lock_icon)
    b += box(560, 110, 190, 90, "Token Cache", "In-memory, TTL-based\nrefresh before expiry")
    b += box(810, 110, 160, 90, "REST Calls", "Authorization: Bearer {token}")

    b += arrow(220, 140, 280, 100, "request token", BLUE, "arrowBlue")
    b += arrow(220, 160, 280, 220, "request token", GREEN, "arrowGreen")
    b += arrow(490, 100, 560, 140, color=BLUE, dash=True)
    b += arrow(490, 220, 560, 170, color=GREEN, dash=True)
    b += arrow(750, 155, 810, 155, color=MUTED, marker="arrow")
    b += f'<text x="30" y="290" font-family="{FONT}" font-size="12.5" fill="{MUTED}">Tokens are never exposed to Copilot Studio — only the MCP server holds credentials.</text>'
    write("diagram-10-auth-token-flow.svg", wrap(b, w, h, "10 · Authentication &amp; Token Flow"))


# ------------------------------------------------------------------
# 11. ArcGIS REST API Interaction Model
# ------------------------------------------------------------------
def diagram_11():
    w, h = 1000, 360
    b = ""
    endpoints = [
        ("/sharing/rest/generateToken", "Auth"),
        ("/sharing/rest/search", "Discover items"),
        ("/rest/services/.../FeatureServer/{id}", "Layer metadata"),
        ("/FeatureServer/{id}/query", "Query features"),
        ("/FeatureServer/{id}/addFeatures", "Edit (optional)"),
    ]
    y = 70
    for ep, desc in endpoints:
        b += box(40, y, 380, 50, ep, None, rx=8, bold=False)
        b += box(460, y, 200, 50, desc, None, rx=8, fill="#eaf4fb", stroke=BLUE, bold=False)
        b += arrow(420, y + 25, 460, y + 25, color=BLUE, marker="arrowBlue")
        y += 62
    b += box(720, 70, 240, 250, "MCP Tool Layer", "findLayer()\nqueryFeatures()\n(future) editFeatures()", fill="#eaf7f0", stroke=GREEN)
    for i in range(len(endpoints)):
        b += arrow(660, 95 + i * 62, 720, 195, color=MUTED, dash=True, curve=(690, 150))
    write("diagram-11-rest-api-interaction-model.svg", wrap(b, w, h, "11 · ArcGIS REST API Interaction Model"))


# ------------------------------------------------------------------
# 12. MCP Server Internal Processing Pipeline
# ------------------------------------------------------------------
def diagram_12():
    w, h = 1080, 300
    stages = [
        ("Receive\ntool call", SURFACE, BORDER),
        ("Validate\nparams (schema)", SURFACE, BORDER),
        ("Resolve\nenvironment", "#fff7ea", AMBER),
        ("Auth /\ntoken cache", "#eaf4fb", BLUE),
        ("Execute\nREST request", "#eaf7f0", GREEN),
        ("Normalize +\nreturn JSON", SURFACE, BORDER),
    ]
    b = ""
    x = 30; bw = 155; gap = 20
    for i, (label, fill, stroke) in enumerate(stages):
        l, s2 = label.split("\n")
        b += box(x, 110, bw, 90, l, s2, fill=fill, stroke=stroke)
        if i < len(stages) - 1:
            b += arrow(x + bw, 155, x + bw + gap, 155, marker="arrowBlue", color=BLUE)
        x += bw + gap
    b += f'<text x="30" y="90" font-family="{FONT}" font-size="13" fill="{MUTED}">Internal function pipeline inside server.js / server.py for every incoming MCP tool call.</text>'
    write("diagram-12-server-internal-pipeline.svg", wrap(b, w, h, "12 · MCP Server Internal Processing Pipeline"))


if __name__ == "__main__":
    diagram_1(); diagram_2(); diagram_3(); diagram_4(); diagram_5(); diagram_6()
    diagram_7(); diagram_8(); diagram_9(); diagram_10(); diagram_11(); diagram_12()
    print("All 12 diagrams generated.")
