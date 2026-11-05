#!/usr/bin/env python3
"""web3-utils MCP server — address validation, checksums & anti-scam scanning (no API key).

Built from real Web3 community-security work. Tools: validate_address, is_scam_text,
scan_links, keccak. Great for moderation bots and wallet UIs.
Run:  python web3_utils.py
"""
import re
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("web3-utils")

# --- minimal keccak-256 (for EIP-55 checksum, no external deps) ---
_KECCAK_RC = [1, 0x8082, 0x800000000000808a, 0x8000000080008000, 0x808b, 0x80000001,
              0x8000000080008081, 0x8000000000008009, 0x8a, 0x88, 0x80008009, 0x8000000a,
              0x8000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003,
              0x8000000000008002, 0x8000000000000080, 0x800a, 0x800000008000000a,
              0x8000000080008081, 0x8000000000008080, 0x80000001, 0x8000000080008008]
_KECCAK_ROT = [0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15,
               21, 8, 18, 2, 61, 56, 14]


def _keccak256(msg: bytes) -> bytes:
    R, W = 1088, 64
    M = (0xFFFFFFFFFFFFFFFF)
    st = [0] * 25
    pad = msg + b"\x01" + b"\x00" * ((-len(msg) - 1) % (R // 8))
    pad = bytearray(pad); pad[-1] |= 0x80
    def rol(x, n): return ((x << n) | (x >> (W - n))) & M
    for off in range(0, len(pad), R // 8):
        blk = pad[off:off + R // 8]
        for i in range(R // 64):
            st[i] ^= int.from_bytes(blk[i * 8:i * 8 + 8], "little")
        for rnd in range(24):
            C = [st[x] ^ st[x + 5] ^ st[x + 10] ^ st[x + 15] ^ st[x + 20] for x in range(5)]
            D = [C[(x + 4) % 5] ^ rol(C[(x + 1) % 5], 1) for x in range(5)]
            for x in range(5):
                for y in range(5):
                    st[x + 5 * y] ^= D[x]
            B = [0] * 25
            for x in range(5):
                for y in range(5):
                    B[y + 5 * ((2 * x + 3 * y) % 5)] = rol(st[x + 5 * y], _KECCAK_ROT[x + 5 * y])
            for x in range(5):
                for y in range(5):
                    st[x + 5 * y] = B[x + 5 * y] ^ ((~B[(x + 1) % 5 + 5 * y]) & B[(x + 2) % 5 + 5 * y])
            st[0] ^= _KECCAK_RC[rnd]
    return b"".join(int(st[i]).to_bytes(8, "little") for i in range(25))[:32]


DRAINER_HINTS = ("connect wallet", "claim", "airdrop", "mint now", "verify your wallet",
                 "seed phrase", "sync your wallet", "validate", "double your")
SHORTENERS = ("bit.ly", "tinyurl", "cutt.ly", "t.co", "is.gd", "rebrand.ly")


@mcp.tool()
def validate_address(address: str) -> dict:
    """Validate an EVM (0x…) or Bitcoin address; for EVM also do EIP-55 checksum check."""
    a = address.strip()
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", a):
        low = a[2:].lower()
        h = _keccak256(low.encode()).hex()
        checksummed = "0x" + "".join(c.upper() if int(h[i], 16) >= 8 else c
                                     for i, c in enumerate(low))
        return {"type": "evm", "valid": True, "checksum_address": checksummed,
                "checksum_ok": (a == checksummed) if a != a.lower() and a != a.upper() else None}
    if re.fullmatch(r"(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}", a):
        return {"type": "bitcoin", "valid": True, "address": a}
    return {"type": "unknown", "valid": False}


@mcp.tool()
def is_scam_text(text: str) -> dict:
    """Score a message for crypto-scam/drainer signals (for moderation bots)."""
    t = text.lower()
    hits = [k for k in DRAINER_HINTS if k in t]
    dm = bool(re.search(r"dm|direct message|message me|pm me", t))
    urgent = bool(re.search(r"limited|hurry|last chance|expires|only \d+ left|24 ?h", t))
    score = min(100, len(hits) * 30 + (20 if dm else 0) + (15 if urgent else 0))
    return {"scam_score": score, "verdict": "high" if score >= 60 else "medium" if score >= 30 else "low",
            "signals": hits, "dm_bait": dm, "urgency": urgent}


@mcp.tool()
def scan_links(text: str) -> dict:
    """Extract URLs from text and flag shorteners / suspicious drainer-style domains."""
    urls = re.findall(r"https?://[^\s)>\]]+", text)
    flagged = []
    for u in urls:
        low = u.lower()
        reasons = []
        if any(s in low for s in SHORTENERS):
            reasons.append("url_shortener")
        if re.search(r"claim|airdrop|mint|connect|wallet|verify", low):
            reasons.append("scam_keyword_in_url")
        if reasons:
            flagged.append({"url": u, "reasons": reasons})
    return {"url_count": len(urls), "flagged": flagged,
            "safe": len(flagged) == 0}


@mcp.tool()
def keccak(text: str) -> dict:
    """keccak-256 hash of a UTF-8 string (Ethereum's hash function)."""
    return {"input": text, "keccak256": "0x" + _keccak256(text.encode()).hex()}


if __name__ == "__main__":
    mcp.run()
