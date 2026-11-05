#!/usr/bin/env python3
"""feeds-api MCP server — read RSS/Atom feeds and query any JSON API (no API key).

Great glue for automation agents. Tools: read_feed, fetch_json, json_path
Run:  python feeds_api.py
"""
import re
import json as _json
import requests
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("feeds-api")
UA = {"User-Agent": "mcp-feeds-api/1.0"}


@mcp.tool()
def read_feed(url: str, limit: int = 15) -> dict:
    """Read an RSS or Atom feed. Returns latest items (title, link, date, summary)."""
    try:
        xml = requests.get(url, headers=UA, timeout=25).text
    except Exception as e:
        return {"error": str(e)[:200], "url": url}
    items = []
    # RSS <item> or Atom <entry>
    blocks = re.findall(r"(?is)<(item|entry)>(.*?)</\1>", xml)
    for _, blk in blocks[:limit]:
        def tag(t):
            m = re.search(rf"(?is)<{t}[^>]*>(.*?)</{t}>", blk)
            v = m.group(1).strip() if m else ""
            v = re.sub(r"(?is)<!\[CDATA\[(.*?)\]\]>", r"\1", v)
            return re.sub(r"(?s)<[^>]+>", " ", v).strip()[:400]
        link = tag("link")
        if not link:
            m = re.search(r'(?is)<link[^>]+href="([^"]+)"', blk)
            link = m.group(1) if m else ""
        items.append({"title": tag("title"), "link": link,
                      "date": tag("pubDate") or tag("updated") or tag("published"),
                      "summary": tag("description") or tag("summary")})
    return {"url": url, "count": len(items), "items": items}


@mcp.tool()
def fetch_json(url: str, headers_json: str = "") -> dict:
    """GET any JSON API endpoint. Optional headers as a JSON string (e.g. auth)."""
    try:
        hdr = dict(UA)
        if headers_json:
            hdr.update(_json.loads(headers_json))
        r = requests.get(url, headers=hdr, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return {"error": str(e)[:250], "url": url}
    return {"url": url, "status": "ok", "data": data}


@mcp.tool()
def json_path(url: str, path: str) -> dict:
    """Fetch a JSON API then extract a dotted path, e.g. 'data.items.0.name'. Lists use numeric keys."""
    got = fetch_json(url)
    if "error" in got:
        return got
    cur = got["data"]
    try:
        for key in path.split("."):
            cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    except (KeyError, IndexError, ValueError, TypeError) as e:
        return {"error": f"path '{path}' not found: {e}", "url": url}
    return {"url": url, "path": path, "value": cur}


if __name__ == "__main__":
    mcp.run()
