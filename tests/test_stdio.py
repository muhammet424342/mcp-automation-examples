"""Start selected example servers over stdio; list tools and call each one offline.
Run: python tests/test_stdio.py"""
import asyncio, os, sys
from pathlib import Path
from mcp import Client
from mcp.client.stdio import StdioServerParameters

ROOT = Path(__file__).resolve().parent.parent
RUNNER = str(ROOT / "tests" / "offline_runner.py")
CALLS = {
    "web3_utils.py": {
        "validate_address": {"address": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"},
        "is_scam_text": {"text": "Claim your airdrop now, DM me, last chance"},
        "scan_links": {"text": "go https://bit.ly/claim-x"},
        "keccak": {"text": ""},
    },
    "feeds_api.py": {
        "read_feed": {"url": "https://e.test/f.rss"},
        "fetch_json": {"url": "https://e.test/a.json"},
        "json_path": {"url": "https://e.test/a.json", "path": "data.items.0.name"},
    },
}
CHECKS = {
    "validate_address": '"checksum_ok": true',
    "keccak": "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
    "json_path": "first",
}

async def check(fname, calls):
    env = dict(os.environ)
    params = StdioServerParameters(command=sys.executable, args=[RUNNER, str(ROOT / "servers" / fname)], env=env)
    fails = 0
    async with Client(params) as c:
        tools = sorted(t.name for t in (await c.list_tools()).tools)
        ok = tools == sorted(calls)
        print(f"{fname}: tools/list {tools} {'OK' if ok else 'MISMATCH'}"); fails += not ok
        for name, args in calls.items():
            r = await c.call_tool(name, args)
            txt = " ".join(getattr(x, "text", "") for x in r.content)
            good = not r.is_error and "error\": \"" not in txt.replace("\"error\": null", "") and CHECKS.get(name, "") in txt
            print(f"  {name}: {'PASS' if good else 'FAIL'} {txt[:110]}"); fails += not good
    return fails

async def main():
    fails = 0
    for f, calls in CALLS.items():
        fails += await check(f, calls)
    print("RESULT:", "PASS" if fails == 0 else f"FAIL ({fails})")
    return fails

if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
