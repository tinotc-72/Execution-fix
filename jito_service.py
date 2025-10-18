import base64
import httpx
from typing import List, Optional

# Copilot TODO: Import retry utilities for wrapping Jito RPC calls with bounded attempts
from utils.health import async_with_retries

class JitoClient:
    """
    Thin JSON-RPC client for Jito Block Engine:
      - send_transaction (single tx): /api/v1/transactions, method=sendTransaction
      - send_bundle (1..5 txs): /api/v1/bundles, method=sendBundle
      - get_tip_accounts: /api/v1/bundles, method=getTipAccounts
    """
    def __init__(self, auth_token: Optional[str] = None, block_engine_base: str = "https://mainnet.block-engine.jito.wtf"):
        # auth_token is your UUID (x-jito-auth). It may be optional under default rate limits.
        self.auth_token = auth_token
        self.base = block_engine_base.rstrip("/")
        self.tx_url = f"{self.base}/api/v1/transactions"
        self.bundle_url = f"{self.base}/api/v1/bundles"
        self.headers = {"Content-Type": "application/json"}
        if self.auth_token:
            self.headers["x-jito-auth"] = self.auth_token

    async def send_transaction(self, signed_tx: bytes, encoding: str = "base64") -> dict:
        # Copilot TODO: Wrap Jito transaction submission with retries to handle transient failures
        async def _send_tx():
            tx = base64.b64encode(signed_tx).decode() if encoding == "base64" else signed_tx
            payload = {"jsonrpc": "2.0", "id": 1, "method": "sendTransaction", "params": [tx, {"encoding": "base64"}]}
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(self.tx_url, headers=self.headers, json=payload)
                r.raise_for_status()
                return r.json()
        
        return await async_with_retries(_send_tx, attempts=3, base_sleep=0.5)

    async def send_bundle(self, signed_txs: List[bytes]) -> dict:
        # Copilot TODO: Wrap Jito bundle submission with retries to handle transient failures
        async def _send_bundle():
            txs_b64 = [base64.b64encode(tx).decode() for tx in signed_txs]
            payload = {"jsonrpc": "2.0", "id": 1, "method": "sendBundle", "params": [txs_b64]}
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(self.bundle_url, headers=self.headers, json=payload)
                r.raise_for_status()
                return r.json()
        
        return await async_with_retries(_send_bundle, attempts=3, base_sleep=0.5)

    async def get_tip_accounts(self) -> dict:
        # Copilot TODO: Wrap Jito tip accounts query with retries to handle transient failures
        async def _get_tips():
            payload = {"jsonrpc": "2.0", "id": 1, "method": "getTipAccounts", "params": []}
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(self.bundle_url, headers=self.headers, json=payload)
                r.raise_for_status()
                return r.json()
        
        return await async_with_retries(_get_tips, attempts=3, base_sleep=0.5)

    def is_configured(self) -> bool:
        # True if we at least have a base URL; auth may be optional in default rate limits.
        return bool(self.base)