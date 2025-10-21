#!/usr/bin/env python3
"""
Pump.fun Copy Executor - Designed to copy Pump.fun trades from detected transactions
Handles both traditional CC trades and router-based trades
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

import asyncio
import logging
from typing import Dict, Any, Optional
from solders.keypair import Keypair

logger = logging.getLogger(__name__)

class PumpfunCopyExecutor:
    """Copy executor for Pump.fun trades"""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        
    async def copy_pumpfun_trade(
        self, wallet_keypair: Keypair, signature: str, 
        trade_info: Dict[str, Any], amount_override: Optional[float] = None
    ) -> BuildResult:
        """Copy a Pump.fun trade with the specified parameters"""
        try:
            logger.info(f"🔄 [PUMPFUN COPY] Copying trade: {signature[:8]}...")
            
            # Extract trade details
            action = trade_info.get("action", "buy")
            token_mint = trade_info.get("token_mint")
            if not token_mint:
                return BuildResult(ok=False, tx=None, reason="Missing token mint")
            
            # Get amount to trade
            amount = amount_override or trade_info.get("amount", 0.01)
            
            if action == "buy":
                result = await self._execute_pumpfun_buy(wallet_keypair, token_mint, amount, trade_info)
            else:
                result = await self._execute_pumpfun_sell(wallet_keypair, token_mint, amount, trade_info)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN COPY] Error: {e}")
            return BuildResult(ok=False, tx=None, reason=f"pumpfun copy failed: {e}")

    async def _execute_pumpfun_buy(
        self, wallet: Keypair, token_mint: str, sol_amount: float, trade_info: Dict[str, Any]
    ) -> BuildResult:
        """Execute a Pump.fun buy transaction"""
        try:
            # Build Pump.fun swap instruction (placeholder)
            ixs = []  # Would contain actual Pump.fun instructions
            
            # PR-02 Pattern: Apply compute budget before compile
            ixs = with_compute_budget(ixs)
            
            # Prepare variables for ATA enforcement
            payer = wallet.pubkey()
            owner = wallet.pubkey()
            out_mint = Pubkey.from_string(token_mint)
            
            # Ensure ATA instructions
            ixs = ensure_ata_ixs(self.rpc_url, payer, owner, out_mint, create_associated_token_account) + ixs
            
            # Build ALTs
            table_pubkeys = trade_info.get("lookup_tables", [])
            alts = build_alts_from_tables(self.rpc_url, table_pubkeys) if table_pubkeys else []
            
            # Compile v0 message with ALT support
            msg = MessageV0.compile(
                instructions=ixs,
                payer=payer,
                address_lookup_tables=alts,
                recent_blockhash=get_recent_blockhash(self.rpc_url),
            )
            tx = VersionedTransaction(msg, [wallet])
            
            # Submit + log
            res = send_and_confirm_v0_tx(self.rpc_url, tx)
            log_submit_result("pumpfun", trade_info.get("action","buy"), trade_info.get("token_mint","?"), res)
            
            if res and res.get("success"):
                return BuildResult(ok=True, tx=res.get("signature"), dex="pumpfun", action="buy")
            else:
                return BuildResult(ok=False, tx=None, reason=f"submit failed: {res}")
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN BUY] Error: {e}")
            return BuildResult(ok=False, tx=None, reason=f"pumpfun buy failed: {e}")

    async def _execute_pumpfun_sell(
        self, wallet: Keypair, token_mint: str, token_amount: float, trade_info: Dict[str, Any]
    ) -> BuildResult:
        """Execute a Pump.fun sell transaction"""
        try:
            # Build Pump.fun swap instruction (placeholder)
            ixs = []  # Would contain actual Pump.fun instructions
            
            # PR-02 Pattern: Apply compute budget before compile
            ixs = with_compute_budget(ixs)
            
            # Prepare variables for ATA enforcement
            payer = wallet.pubkey()
            owner = wallet.pubkey()
            out_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")  # SOL mint for sell
            
            # Ensure ATA instructions
            ixs = ensure_ata_ixs(self.rpc_url, payer, owner, out_mint, create_associated_token_account) + ixs
            
            # Build ALTs
            table_pubkeys = trade_info.get("lookup_tables", [])
            alts = build_alts_from_tables(self.rpc_url, table_pubkeys) if table_pubkeys else []
            
            # Compile v0 message with ALT support
            msg = MessageV0.compile(
                instructions=ixs,
                payer=payer,
                address_lookup_tables=alts,
                recent_blockhash=get_recent_blockhash(self.rpc_url),
            )
            tx = VersionedTransaction(msg, [wallet])
            
            # Submit + log
            res = send_and_confirm_v0_tx(self.rpc_url, tx)
            log_submit_result("pumpfun", trade_info.get("action","sell"), trade_info.get("token_mint","?"), res)
            
            if res and res.get("success"):
                return BuildResult(ok=True, tx=res.get("signature"), dex="pumpfun", action="sell")
            else:
                return BuildResult(ok=False, tx=None, reason=f"submit failed: {res}")
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN SELL] Error: {e}")
            return BuildResult(ok=False, tx=None, reason=f"pumpfun sell failed: {e}")
