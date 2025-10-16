# fast_executor.py - Jito JSON-RPC Client Integration

import pathlib
print(f"[FAST_EXECUTOR] using: {pathlib.Path(__file__).resolve()}")

import httpx
import asyncio
import aiohttp
import base64
import json
import traceback
import uuid
from typing import Optional, List
from solders.keypair import Keypair
from solders.transaction import Transaction, VersionedTransaction
from solders.message import MessageV0
from solders.instruction import CompiledInstruction, Instruction
from solders.hash import Hash

# Make Jito imports optional - never fail at import time
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
except ImportError:
    JITO_AVAILABLE = False
    JitoClient = None

from env_keys import EnvKeys

from config import (
    HELIUS_RPC_URL,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE
)

class FastExecutor:
    def __init__(self, keypair: Keypair, rpc_url: str = None, jito_client=None, preferred_region: str = "london", logger=None):
        self.keypair = keypair
        self.session = None
        self.helius_url = rpc_url if rpc_url else HELIUS_RPC_URL
        self.logger = logger or self._get_default_logger()
        
        # Use EnvKeys for Jito configuration
        env_keys = EnvKeys()
        
        # Store RPC URL for confirmation calls
        self._rpc_url = getattr(env_keys, "HELIUS_RPC_URL", None)
        
        # Initialize Jito client with auth from env_keys
        if JITO_AVAILABLE:
            auth_token = env_keys.JITO_UUID or env_keys.JITO_AUTH_TOKEN
            region_url = env_keys.JITO_BUNDLE_ENDPOINT
            self.jito = jito_client if jito_client else JitoClient(auth_token=auth_token, block_engine_base=region_url)
            self.use_jito = True
            self._jito_region_url = region_url
        else:
            self.jito = None
            self.use_jito = False
            self._jito_region_url = None
        
        print(f"🔐 Initializing FastExecutor with wallet: {keypair.pubkey()}")
        if self.use_jito:
            print(f"🌍 Using Jito endpoint: {self._jito_region_url}")
            print("💫 MEV Protection: Enabled via JitoClient")
        else:
            print("📡 Jito not available - using pure RPC path")
            print(f"🔗 RPC URL: {self.helius_url}")
    
    def _get_default_logger(self):
        """Create a default logger if none provided"""
        import logging
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def initialize_session(self):
        """Initialize HTTP session for Jito communication"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
    async def initialize(self):
        """Initialize the FastExecutor - required by execution components"""
        await self.initialize_session()
        print("✅ FastExecutor initialization complete")

    async def _submit_via_jito(self, vtx) -> str | None:
        """Submit transaction via Jito using JitoClient.send_transaction"""
        if not self.use_jito:
            return None
        raw = bytes(vtx)
        try:
            resp = await self.jito.send_transaction(raw)
            sig = (resp or {}).get("result")
            if sig:
                self.logger.info(f"[SUBMIT_JITO] region={self._jito_region_url} sig={sig}")
                return sig
            self.logger.error(f"[SUBMIT_JITO] no result: {resp}")
            return None
        except Exception as e:
            self.logger.error(f"[SUBMIT_JITO] error: {e}")
            return None
    
    async def submit_transaction(self, vtx: VersionedTransaction) -> Optional[str]:
        """Submit transaction via Jito or RPC fallback"""
        try:
            if not self.session:
                await self.initialize()

            if not isinstance(vtx, VersionedTransaction):
                self.logger.error(f"Invalid transaction type: {type(vtx)}")
                return None

            # Try Jito first
            sig = await self._submit_via_jito(vtx)
            if sig:
                return sig
            
            # Fallback to RPC
            return await self._submit_via_rpc(vtx)

        except Exception as e:
            self.logger.error(f"Transaction submission error: {e}")
            traceback.print_exc()
            return None
    
    async def _submit_via_rpc(self, vtx) -> str | None:
        """Submit transaction via RPC - parses signature from JSON-RPC 'result' field"""
        try:
            raw = bytes(vtx)
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [base64.b64encode(raw).decode(), {"encoding": "base64"}]
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(self._rpc_url, json=payload)
                r.raise_for_status()
                data = r.json()
            sig = (data or {}).get("result")
            if sig:
                self.logger.info(f"[SUBMIT_RPC] sig={sig}")
                return sig
            self.logger.error(f"[SUBMIT_RPC] no result: {data}")
            return None
        except Exception as e:
            self.logger.error(f"[SUBMIT_RPC] error: {e}")
            return None

    async def _confirm_once(self, sig: str) -> dict | None:
        if not self._rpc_url:
            self.logger.warning("[CONFIRM] no RPC url configured")
            return None
        payload = {"jsonrpc":"2.0","id":1,"method":"getSignatureStatuses","params":[[sig], {"searchTransactionHistory": True}]}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(self._rpc_url, json=payload)
            r.raise_for_status()
            return r.json()

    async def _confirm_with_retries(self, sig: str, attempts: int = 5, delay_s: float = 0.8) -> dict | None:
        for i in range(attempts):
            data = await self._confirm_once(sig)
            try:
                value = ((data or {}).get("result") or {}).get("value") or []
                status = value[0] if value else None
                self.logger.info(f"[CONFIRM] attempt={i+1}/{attempts} status={status}")
                if status:  # seen by cluster (err could be None or object)
                    return status
            except Exception:
                pass
            await asyncio.sleep(delay_s)
        return None

    async def close(self):
        """Close the sessions"""
        if self.session:
            await self.session.close()
            if self.jito and hasattr(self.jito, 'close'):
                await self.jito.close()
            self.session = None
            print("👋 FastExecutor session closed")

    async def send_and_confirm(self, vtx: VersionedTransaction) -> Optional[str]:
        """
        Unified submit logic: tries Jito first, then RPC fallback.
        This is the main method for submitting transactions.
        """
        sig = await self._submit_via_jito(vtx)
        if not sig:
            self.logger.warning("[EXECUTOR] Falling back to RPC submission")
            sig = await self._submit_via_rpc(vtx)
        if not sig:
            self.logger.error("[EXECUTOR] submission failed (Jito and RPC)")
            return None
        status = await self._confirm_with_retries(sig)
        self.logger.info(f"[CONFIRM][FINAL] sig={sig} status={status}")
        return sig