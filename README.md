# MCP automation examples

Two small **stdio MCP servers** in Python for clients that launch local stdio servers (for example Claude Desktop or Cursor).

This is a public subset of a larger personal toolkit. It is **not** a claim of production use, customer results, or live Claude/Cursor verification.

| Server | Tools | API key? |
|---|---|---|
| **web3-utils** | `validate_address` (EIP-55), `is_scam_text`, `scan_links`, `keccak` | none (fully offline) |
| **feeds-api** | `read_feed` (RSS/Atom), `fetch_json`, `json_path` | none |

- `web3-utils` is pure Python (keccak-256 / EIP-55). `is_scam_text` / `scan_links` are simple keyword heuristics, **not** a security guarantee.
- `feeds-api` uses HTTP for live feeds/APIs. Respect each site's terms and rate limits. Offline tests replace network calls with fakes.

## Requirements

- Python 3.10+
- `mcp==2.3.0`, `requests` (see `requirements.txt`)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Servers use the mcp 2.x API (`from mcp.server.mcpserver import MCPServer`). mcp 1.x (`fastmcp`) will not import on 2.x.

## Offline tests

```bash
python tests/test_stdio.py
```

Starts each example server over stdio with the official MCP client, runs `tools/list`, and calls every tool once. Network calls are faked; no internet is required for the test run.

## Run a server

```bash
python servers/web3_utils.py
python servers/feeds_api.py
```

## Client config example (not verified live)

Replace `/ABSOLUTE/PATH` with the full path to this repo's `servers/` folder. Use your venv's Python as `command` if needed. **This config was not tested against a real Claude Desktop or Cursor session.**

```json
{
  "mcpServers": {
    "web3-utils": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/servers/web3_utils.py"]
    },
    "feeds-api": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/servers/feeds_api.py"]
    }
  }
}
```

Typical config file locations:

- Claude Desktop (macOS): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Desktop (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Cursor: `~/.cursor/mcp.json` or project `.cursor/mcp.json`

## Limitations

- Offline tests prove tool listing and mocked call shapes; they do not prove live API behaviour.
- Live HTTP tools depend on remote sites and can fail on rate limits, blocks, or HTML/XML changes.
- No Telegram, no bot tokens, no paid API keys in this example set.

## License

MIT — see `LICENSE`. Copyright (c) 2026 Muhammet Karakurt.

## Full pack

For the full pack (more servers), contact via the GitHub profile.
