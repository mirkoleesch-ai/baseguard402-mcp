#!/usr/bin/env python3
"""BaseGuard402 MCP Server (stdio JSON-RPC 2.0, zero third-party dependencies).

Wraps the live BaseGuard402 x402 v2 API Suite (https://x402.baseguard402.xyz) as native
Model Context Protocol (MCP) tools for Claude Desktop, Cursor, Antigravity, and autonomous agents:
  - baseguard402_discover       (FREE)       Live x402 v2 manifest & pricing
  - baseguard402_url_clean      ($0.01 USDC) Clean Web-to-Markdown Extractor
  - baseguard402_token_audit    ($0.02 USDC) Base ERC-20 Smart-Contract & Honeypot Auditor
  - baseguard402_nft_alpha      ($0.03 USDC) Base NFT Arbitrage Spreads & Undervalued Traits
  - baseguard402_nft_valuation  ($0.02 USDC) Base NFT Fair-Value & Liquidity Pricing Oracle
  - baseguard402_deep_research  ($0.05 USDC) Real-Time Deep Research with Verified Citations

All paid tools settle natively in Base Mainnet USDC (eip155:8453) via the Coinbase CDP x402 v2
facilitator. When called without a `payment_signature` / `x_payment` header, the tool returns the
exact HTTP 402 Payment Required challenge and EIP-3009 parameters so x402-enabled wallets/agents
can sign and retry immediately.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = os.getenv("BASEGUARD402_BASE_URL", "https://x402.baseguard402.xyz").rstrip("/")
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "baseguard402-mcp", "version": "1.0.0"}

PAYMENT_PROP = {
    "payment_signature": {
        "type": "string",
        "description": "Optional Base64 x402 v2 PAYMENT-SIGNATURE header (EIP-3009 USDC authorization on Base). Omit first to receive the exact HTTP 402 payment quote.",
    },
    "x_payment": {
        "type": "string",
        "description": "Optional legacy X-Payment header or Base Mainnet USDC tx hash.",
    },
}

TOOLS: list[dict[str, Any]] = [
    {
        "name": "baseguard402_discover",
        "description": "FREE. Fetch the live BaseGuard402 x402 v2 discovery manifest, endpoint pricing (Base USDC), and schemas.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "baseguard402_url_clean",
        "description": "$0.01 USDC on Base (x402 v2). Extract any public webpage into clean, token-efficient Markdown with token-savings stats.",
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "Public http:// or https:// URL to clean into Markdown."},
                "max_chars": {"type": "integer", "default": 15000, "minimum": 500, "maximum": 50000},
                **PAYMENT_PROP,
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "baseguard402_token_audit",
        "description": "$0.02 USDC on Base (x402 v2). Live Base ERC-20 bytecode & Uniswap V3 liquidity risk/honeypot audit (0-100 risk score).",
        "inputSchema": {
            "type": "object",
            "required": ["token_address"],
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "42-character hexadecimal Base ERC-20 contract address (0x...).",
                },
                **PAYMENT_PROP,
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "baseguard402_nft_alpha",
        "description": "$0.03 USDC on Base (x402 v2). Live Base NFT arbitrage spreads (OpenSea, Blur, Magic Eden) and undervalued rare-trait feed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_spread_pct": {"type": "number", "default": 5.0, "minimum": 0.0, "maximum": 50.0},
                "limit": {"type": "integer", "default": 15, "minimum": 1, "maximum": 50},
                "strategy": {"type": "string", "enum": ["ALL", "FLOOR_FLIP", "CROSS_MARKET", "TRAIT_ARBITRAGE"], "default": "ALL"},
                **PAYMENT_PROP,
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "baseguard402_nft_valuation",
        "description": "$0.02 USDC on Base (x402 v2). Deterministic Base NFT fair-minimum valuation & WETH bid-liquidity depth oracle.",
        "inputSchema": {
            "type": "object",
            "required": ["contract_address", "token_id"],
            "properties": {
                "contract_address": {"type": "string", "description": "42-char Base NFT contract address (0x...)."},
                "token_id": {"type": "string", "description": "Token ID of the NFT to value."},
                "traits": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"trait_type": {"type": "string"}, "value": {"type": "string"}},
                    },
                },
                **PAYMENT_PROP,
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "baseguard402_deep_research",
        "description": "$0.05 USDC on Base (x402 v2). Real-time fact-checked deep research synthesis backed by primary source URLs.",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Research question or topic to investigate."},
                "max_sources": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                **PAYMENT_PROP,
            },
            "additionalProperties": False,
        },
    },
]


def _http_call(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    payment_signature: str = "",
    x_payment: str = "",
    timeout: float = 90.0,
) -> tuple[int, dict[str, str], Any]:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "baseguard402-mcp/1.0.0",
    }
    raw_body: bytes | None = None
    if body is not None:
        raw_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if payment_signature:
        headers["PAYMENT-SIGNATURE"] = payment_signature.strip()
    if x_payment:
        headers["X-Payment"] = x_payment.strip()

    req = urllib.request.Request(url, data=raw_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200))
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        resp_headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        text = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 503, {}, {"error": f"Network error calling BaseGuard402: {exc.reason}"}

    try:
        parsed: Any = json.loads(text)
    except json.JSONDecodeError:
        parsed = {"raw_text": text[:4000]}
    return status, resp_headers, parsed


def invoke_tool(name: str, arguments: dict[str, Any] | None = None, *, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    args = dict(arguments or {})
    pay_sig = str(args.pop("payment_signature", "") or "").strip()
    x_pay = str(args.pop("x_payment", "") or "").strip()
    base = base_url.rstrip("/")

    if name == "baseguard402_discover":
        code, _hdrs, data = _http_call(f"{base}/.well-known/x402.json", method="GET", timeout=15.0)
        return {"http_status": code, "data": data}

    if name == "baseguard402_url_clean":
        payload = {"url": str(args.get("url") or "").strip()}
        if args.get("max_chars") is not None:
            payload["max_chars"] = int(args["max_chars"])
        code, hdrs, data = _http_call(
            f"{base}/api/v1/url-clean", method="POST", body=payload, payment_signature=pay_sig, x_payment=x_pay
        )
    elif name == "baseguard402_token_audit":
        payload = {"token_address": str(args.get("token_address") or "").strip()}
        code, hdrs, data = _http_call(
            f"{base}/api/v1/token-audit", method="POST", body=payload, payment_signature=pay_sig, x_payment=x_pay
        )
    elif name == "baseguard402_nft_alpha":
        qs = urllib.parse.urlencode(
            {
                "min_spread_pct": float(args.get("min_spread_pct", 5.0)),
                "limit": int(args.get("limit", 15)),
                "strategy": str(args.get("strategy", "ALL")),
            }
        )
        code, hdrs, data = _http_call(
            f"{base}/api/v1/nft-alpha?{qs}", method="GET", payment_signature=pay_sig, x_payment=x_pay
        )
    elif name == "baseguard402_nft_valuation":
        payload = {
            "contract_address": str(args.get("contract_address") or "").strip(),
            "token_id": str(args.get("token_id") or "").strip(),
        }
        if args.get("traits") is not None:
            payload["traits"] = args["traits"]
        code, hdrs, data = _http_call(
            f"{base}/api/v1/nft-valuation", method="POST", body=payload, payment_signature=pay_sig, x_payment=x_pay
        )
    elif name == "baseguard402_deep_research":
        payload = {"query": str(args.get("query") or "").strip()}
        if args.get("max_sources") is not None:
            payload["max_sources"] = int(args["max_sources"])
        code, hdrs, data = _http_call(
            f"{base}/api/v1/deep-research",
            method="POST",
            body=payload,
            payment_signature=pay_sig,
            x_payment=x_pay,
            timeout=100.0,
        )
    else:
        return {"error": f"Unknown tool: {name}"}

    out: dict[str, Any] = {"http_status": code, "data": data}
    if code == 402:
        out["x402_payment_required"] = True
        if "payment-required" in hdrs:
            out["payment_required_header"] = hdrs["payment-required"]
        out["instructions"] = (
            "HTTP 402 Payment Required (x402 v2, Base Mainnet USDC). Sign an EIP-3009 authorization "
            "for the quoted micro-USDC amount and re-call this tool with `payment_signature`."
        )
    return out


def handle_jsonrpc_message(msg: dict[str, Any], *, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any] | None:
    req_id = msg.get("id")
    method = str(msg.get("method") or "")
    params = msg.get("params") if isinstance(msg.get("params"), dict) else {}

    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        tool_name = str(params.get("name") or "")
        tool_args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        res = invoke_tool(tool_name, tool_args, base_url=base_url)
        is_err = "error" in res and "http_status" not in res
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(res, indent=2, ensure_ascii=False)}],
                "isError": is_err,
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def serve_stdio() -> int:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        reply = handle_jsonrpc_message(msg)
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        print(json.dumps({"server": SERVER_INFO, "base_url": DEFAULT_BASE_URL, "tools": [t["name"] for t in TOOLS]}, indent=2))
        return 0
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
