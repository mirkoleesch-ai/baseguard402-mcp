# BaseGuard402 — x402 v2 Base Mainnet API Suite & MCP Server

[![x402 v2](https://img.shields.io/badge/x402-v2%20Base%20USDC-0052FF)](https://x402.baseguard402.xyz/.well-known/x402.json)
[![MCP Ready](https://img.shields.io/badge/MCP-stdio%20Server-10B981)](https://github.com/mirkoleesch-ai/baseguard402-mcp)
[![Zero Dependencies](https://img.shields.io/badge/Python-Zero%20Deps-3776AB)](https://github.com/mirkoleesch-ai/baseguard402-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**BaseGuard402** (`https://x402.baseguard402.xyz`) is a live, pay-per-call **x402 v2** microservice suite on **Base Mainnet (`eip155:8453`)** settled in **USDC** via the official Coinbase CDP Facilitator — **no API keys, no signup, no subscriptions**.

This repository provides a **zero-dependency Model Context Protocol (MCP) server** and client reference so Claude Desktop, Cursor, Antigravity, and autonomous AI agents can discover and call all 5 BaseGuard402 endpoints out of the box.

---

## Live Discovery & Endpoints

- **Base URL:** `https://x402.baseguard402.xyz`
- **x402 Discovery Manifest:** [`/.well-known/x402`](https://x402.baseguard402.xyz/.well-known/x402) · [`/.well-known/x402.json`](https://x402.baseguard402.xyz/.well-known/x402.json)
- **LLM Guide (`llms.txt`):** [`/llms.txt`](https://x402.baseguard402.xyz/llms.txt)
- **OpenAPI Spec:** [`/openapi.json`](https://x402.baseguard402.xyz/openapi.json)
- **A2A Agent Card:** [`/.well-known/agent-card.json`](https://x402.baseguard402.xyz/.well-known/agent-card.json)
- **Health Check:** [`/health`](https://x402.baseguard402.xyz/health)

| Endpoint | Method | Price (Base USDC) | MCP Tool | What It Does |
| :--- | :---: | :---: | :--- | :--- |
| `/api/v1/url-clean` | `POST` | **`$0.01`** | `baseguard402_url_clean` | Strips HTML, ads, scripts & cookie banners into clean Markdown with token-savings metrics. |
| `/api/v1/token-audit` | `POST` | **`$0.02`** | `baseguard402_token_audit` | Inspects live Base ERC-20 bytecode + Uniswap V3 liquidity for honeypots, mint traps & blacklist selectors (`0-100` risk score). |
| `/api/v1/nft-alpha` | `GET` | **`$0.03`** | `baseguard402_nft_alpha` | Live Base NFT arbitrage spreads (OpenSea, Blur, Magic Eden) & undervalued rare-trait listings. |
| `/api/v1/nft-valuation` | `POST` | **`$0.02`** | `baseguard402_nft_valuation` | Deterministic Base NFT fair-minimum valuation & real WETH bid-liquidity depth oracle. |
| `/api/v1/deep-research` | `POST` | **`$0.05`** | `baseguard402_deep_research` | Real-time fact-checked technical/DeFi research synthesis with primary source citations. |
| `/.well-known/x402.json` | `GET` | **FREE** | `baseguard402_discover` | Machine-readable x402 v2 catalog, pricing, and JSON schemas. |

> **Payment Details:** Network `eip155:8453` (Base Mainnet) · Asset `USDC` (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`) · Scheme `exact` (EIP-3009) · Facilitator `https://api.cdp.coinbase.com/platform/v2/x402` · 60-minute cache & strict replay protection · Failed requests are never settled.

---

## Quick Start: MCP Server Setup (Claude Desktop / Cursor / Antigravity)

No third-party Python packages required (`Python >= 3.10` standard library only).

```bash
git clone https://github.com/mirkoleesch-ai/baseguard402-mcp.git
cd baseguard402-mcp
pip install -e .
```

Add to your MCP config (`claude_desktop_config.json`, Cursor MCP, or Antigravity MCP):

```json
{
  "mcpServers": {
    "baseguard402": {
      "command": "python3",
      "args": ["-m", "baseguard402_mcp.server"],
      "env": {
        "BASEGUARD402_BASE_URL": "https://x402.baseguard402.xyz"
      }
    }
  }
}
```

Or run directly with `uvx` once installed:
```bash
python3 -m baseguard402_mcp.server --list-tools
```

---

## Direct HTTP / `curl` Usage (x402 v2)

### 1. Probe Any Endpoint for an HTTP 402 Payment Quote (Free)
```bash
curl -i -X POST https://x402.baseguard402.xyz/api/v1/token-audit \
  -H "Content-Type: application/json" \
  -d '{"token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}'
```

The server responds with `HTTP/2 402 Payment Required` plus the `PAYMENT-REQUIRED` header containing the exact Base USDC EIP-3009 payment requirements and Bazaar schema.

### 2. Retry with a Signed `PAYMENT-SIGNATURE` Header
```bash
curl -s -X POST https://x402.baseguard402.xyz/api/v1/token-audit \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <base64-x402-v2-payment-payload>" \
  -d '{"token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}'
```

---

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT License — see [LICENSE](LICENSE).
