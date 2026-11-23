#!/usr/bin/env python3
"""Unit tests for baseguard402_mcp.server."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from baseguard402_mcp import server


class BaseGuard402McpTests(unittest.TestCase):
    def test_initialize_and_tools_list(self) -> None:
        init_res = server.handle_jsonrpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertIsNotNone(init_res)
        assert init_res is not None
        self.assertEqual(init_res["result"]["serverInfo"]["name"], "baseguard402-mcp")

        list_res = server.handle_jsonrpc_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert list_res is not None
        names = [t["name"] for t in list_res["result"]["tools"]]
        self.assertEqual(
            names,
            [
                "baseguard402_discover",
                "baseguard402_url_clean",
                "baseguard402_token_audit",
                "baseguard402_nft_alpha",
                "baseguard402_nft_valuation",
                "baseguard402_deep_research",
            ],
        )

    def test_402_quote_and_paid_retry_pass_through(self) -> None:
        with patch.object(
            server,
            "_http_call",
            return_value=(402, {"payment-required": "eyJ4NDAyVmVyc2lvbiI6Mn0="}, {"status": 402, "x402Version": 2}),
        ) as mock_call:
            res = server.invoke_tool(
                "baseguard402_token_audit",
                {"token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
            )
        self.assertEqual(res["http_status"], 402)
        self.assertTrue(res["x402_payment_required"])
        self.assertIn("payment_required_header", res)
        self.assertTrue(mock_call.called)

        rpc_reply = server.handle_jsonrpc_message(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "baseguard402_discover", "arguments": {}},
            }
        )
        assert rpc_reply is not None
        self.assertFalse(rpc_reply["result"]["isError"])
        parsed_text = json.loads(rpc_reply["result"]["content"][0]["text"])
        self.assertIn("http_status", parsed_text)


if __name__ == "__main__":
    unittest.main()
