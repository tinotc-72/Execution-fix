#!/usr/bin/env python3
"""
Execution Coordinator - Handles all trading execution logic with token validation
This module contains ALL execution methods moved from main.py for clean separation
Enhanced with comprehensive token validation to prevent failed executions
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

# Set up logger for this module - DEEP DEBUG MODE
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level

from solders.keypair import Keypair
from solders.pubkey import Pubkey



# Canonical DEX normalization and routing

CANONICAL_DEX = {"jupiter", "pumpfun", "meteora", "raydium"}
DEX_ALIASES = {
    "jup": "jupiter", "jupiter_router": "jupiter",
    "pf": "pumpfun", "pump.fun": "pumpfun", "pumpfun_router": "pumpfun",
    "dbc": "meteora", "meteora_damm_v2": "meteora"
}
def normalize_dex(label: str) -> str:
    if not label:
        return "unknown"
    l = label.strip().lower()
    return l if l in CANONICAL_DEX else DEX_ALIASES.get(l, "unknown")
ROUTE_MAP = {
    "pumpfun":   ["pumpfun", "direct_copy", "jupiter", "raydium", "meteora"],
    "raydium":   ["raydium", "direct_copy", "jupiter", "meteora"],
    "jupiter":   ["jupiter", "raydium", "direct_copy", "meteora"],
    "meteora":   ["meteora", "raydium", "jupiter", "direct_copy"],
    "advanced_mev_bot": ["advanced_mev"],
    "unknown":   ["direct_copy", "jupiter", "raydium", "meteora"],
}


# Only import and use best-practice MEV executors and direct copy logic
 
from mev_direct_copy_executor import MEVDirectCopyExecutor, MEVDirectCopyConfig
from mev_jupiter_executor import MEVJupiterExecutor
from mev_direct_sell_executor import MEVDirectSellExecutor, DirectSellCopyConfig, try_mev_direct_copy_sell
from mev_raydium_executor import MEVRaydiumExecutor, try_raydium_buy, try_raydium_sell_all
from mev_meteora_executor import MEVMeteoraExecutor, MeteoraTradeParams, MeteoraTradeResult
from mev_advanced_bot_executor import MEVAdvancedBotExecutor, AdvancedMEVTradeParams, AdvancedMEVTradeResult


# Import logging utilities
from copy_trade_logger import log_successful_copy_trade, log_failed_copy_trade


# ================================
# EXECUTOR RESULT STANDARDIZATION
# ================================

def exec_ok(executor_name: str, signature: str, details: dict | None = None):
    """Standard success result for executors"""
    return {"ok": True, "executor": executor_name, "signature": signature, "details": details or {}}

def exec_err(executor_name: str, error: str, details: dict | None = None):
    """Standard error result for executors"""
    return {"ok": False, "executor": executor_name, "error": error, "details": details or {}}

def is_success(result: dict | None) -> bool:
    """Check if executor result indicates success"""
    return bool(result and isinstance(result, dict) and result.get("ok") is True and isinstance(result.get("signature"), str))


logger = logging.getLogger(__name__)
logger.info(f"[ROUTE_MAP LOADED] {ROUTE_MAP}")


async def maybe_execute(trade_info: dict, rpc_url: str, keypair: Keypair, fast_executor=None, jito_service=None) -> Optional[dict]:
    """
    Simplified execution coordinator that tries build_and_sign paths before falling back to clone.
    
    For dex=="jupiter" and use_universal_cloner=False: Try Jupiter build_and_sign → direct_copy fallback
    For dex=="meteora" and use_universal_cloner=False: Try Meteora build_and_sign → Jupiter → direct_copy
    For dex=="meteora" and use_universal_cloner=True: Try builders if mint exists, else direct_copy
    For dex=="unknown" with mint: Try Jupiter → direct_copy
    For dex=="unknown" with JUP6 in logs/meta: Treat as jupiter and try Jupiter build_and_sign → direct_copy
    
    Always logs sanity check messages even when fields are incomplete.
    
    Args:
        trade_info: Trade information dictionary
        rpc_url: RPC URL string
        keypair: Wallet keypair
        fast_executor: Optional FastExecutor instance for submission
        jito_service: Optional Jito service for MEV
        
    Returns:
        dict with success/signature on success, or None on failure
    """
    dex = (trade_info.get("dex") or "unknown").lower()
    prefer_clone = bool(trade_info.get("use_universal_cloner"))
    
    # Detect Jupiter from logs/meta if dex is unknown
    if dex == "unknown":
        logs = trade_info.get("logs", [])
        meta = trade_info.get("meta", {})
        log_text = " ".join(logs) if isinstance(logs, list) else str(logs)
        
        # Check for Jupiter program ID in logs or meta
        if "JUP6" in log_text or "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in log_text:
            logger.info("🧭 [COORDINATOR] Detected Jupiter from logs, treating as jupiter")
            dex = "jupiter"
        elif isinstance(meta, dict):
            meta_str = str(meta)
            if "JUP6" in meta_str or "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in meta_str:
                logger.info("🧭 [COORDINATOR] Detected Jupiter from meta, treating as jupiter")
                dex = "jupiter"
    
    logger.info("🧭 [COORDINATOR] route start: dex=%s, prefer_clone=%s", dex, prefer_clone)
    
    # Check if we have required fields for actual execution
    token_mint = trade_info.get("token_mint")
    if not token_mint or token_mint in ("UNKNOWN", "PENDING_ANALYSIS", "unknown", ""):
        logger.error("❌ [COORDINATOR] Missing or invalid token_mint, cannot execute")
        logger.info("🧭 [ROUTE] Skipped → missing token_mint")
        logger.error("❌ [EXECUTION] Failed: missing required fields")
        return None
    
    async def try_submit(vtx):
        if not vtx:
            return False
        try:
            # Use fast_executor if available, otherwise create temp one
            if fast_executor:
                sig = await fast_executor.submit_transaction(vtx)
            else:
                from fast_executor import FastExecutor
                temp_executor = FastExecutor(keypair=keypair, rpc_url=rpc_url, jito_service=jito_service)
                await temp_executor.initialize()
                sig = await temp_executor.submit_transaction(vtx)
                await temp_executor.close()
            
            if sig:
                logger.info(f"✅ [EXECUTION] submitted: {sig}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ [EXECUTION] submit failed: {e}", exc_info=True)
            return False
    
    async def execute_direct_copy(trade_info, rpc, keypair, jito):
        """Fall back to transaction cloning"""
        signature = trade_info.get("signature")
        if not signature:
            logger.error("❌ [DIRECT_COPY] No signature available for cloning")
            return None
            
        try:
            from transaction_cloner import clone_tx_from_signature
            vtx = await clone_tx_from_signature(rpc=rpc, signature=signature, new_payer=keypair)
            if vtx:
                if await try_submit(vtx):
                    return {"success": True, "signature": signature, "method": "direct_copy"}
            return None
        except Exception as e:
            logger.error(f"❌ [DIRECT_COPY] Clone failed: {e}", exc_info=True)
            return None
    
    if dex == "jupiter" and not prefer_clone:
        logger.info("🧭 [COORDINATOR] Route=jupiter")
        try:
            from mev_jupiter_executor import build_and_sign as jupiter_build_and_sign
            vtx = jupiter_build_and_sign(trade_info, rpc_url, keypair)
        except Exception as e:
            logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)
            vtx = None
        if await try_submit(vtx):
            return {"success": True, "method": "jupiter"}
        logger.warning("⚠️ Jupiter build failed — falling back to direct_copy")
        return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)
    
    if dex == "meteora":
        if not prefer_clone:
            logger.info("🧭 [ROUTE] Meteora → build_and_sign")
            vtx = None
            try:
                from mev_meteora_executor import build_and_sign as meteora_build_and_sign
                from mev_meteora_executor import SimpleRPC, RPCConfig
                rpc = SimpleRPC(RPCConfig(rpc_url))
                vtx = meteora_build_and_sign(trade_info, rpc, keypair)
            except Exception as e:
                logger.error(f"❌ [METEORA] build error: {e}", exc_info=True)
            if await try_submit(vtx): 
                return {"success": True, "method": "meteora"}
            logger.warning("⚠️ Meteora build failed → trying Jupiter")
            try:
                from mev_jupiter_executor import build_buy_tx as jupiter_build_buy_tx
                token_mint_str = trade_info.get("token_mint", "")
                amount_sol = trade_info.get("amount_sol", 0.001)
                vtx = jupiter_build_buy_tx(token_mint_str, amount_sol, keypair)
            except Exception as e:
                logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)
                vtx = None
            if await try_submit(vtx): 
                return {"success": True, "method": "jupiter"}
            logger.warning("⚠️ Builders failed → direct_copy fallback")
            return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)

        # prefer_clone path, still try builder first if we have a mint
        if trade_info.get("token_mint"):
            try:
                from mev_meteora_executor import build_and_sign as meteora_build_and_sign
                from mev_meteora_executor import SimpleRPC, RPCConfig
                rpc = SimpleRPC(RPCConfig(rpc_url))
                vtx = meteora_build_and_sign(trade_info, rpc, keypair)
                if await try_submit(vtx): 
                    return {"success": True, "method": "meteora"}
            except Exception:
                pass
        return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)

    # unknown with mint → Jupiter → copy
    if dex == "unknown" and trade_info.get("token_mint"):
        logger.info("🧭 [ROUTE] Unknown with mint → Jupiter → Clone")
        try:
            from mev_jupiter_executor import build_buy_tx as jupiter_build_buy_tx
            token_mint_str = trade_info.get("token_mint", "")
            amount_sol = trade_info.get("amount_sol", 0.001)
            vtx = jupiter_build_buy_tx(token_mint_str, amount_sol, keypair)
        except Exception as e:
            logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)
            vtx = None
        if await try_submit(vtx): 
            return {"success": True, "method": "jupiter"}
        return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)

    # last resort
    logger.info("🧭 [ROUTE] Fallback → direct_copy")
    return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)


@dataclass
class WalletPosition:
    """Track wallet positions"""
    token_mint: str
    initial_amount: float
    current_amount: float
    our_amount: float
    entry_price: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class ExecutionCoordinator:
    async def _run_executor(self, executor_name: str, method_name: str, *args, **kwargs) -> dict:
        """
        Centralized executor runner with standardized error handling
        
        Args:
            executor_name: Name of the executor (e.g., 'jupiter', 'raydium_mev')
            method_name: Method to call on the executor
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
            
        Returns:
            Standardized result dict with success/error status
        """
        try:
            executor = getattr(self, f"{executor_name}_executor", None)
            if not executor:
                logger.error(f"❌ Executor '{executor_name}' not found")
                return exec_err(executor_name, f"Executor '{executor_name}' not available")
            
            method = getattr(executor, method_name, None)
            if not method:
                logger.error(f"❌ Method '{method_name}' not found on {executor_name} executor")
                return exec_err(executor_name, f"Method '{method_name}' not available on {executor_name}")
            
            logger.debug(f"🔄 Running {executor_name}.{method_name} with args={args}, kwargs={kwargs}")
            result = await method(*args, **kwargs)
            
            # Standardize the result format
            if isinstance(result, dict):
                if 'success' in result:
                    return result  # Already standardized
                else:
                    # Legacy format - convert to standardized
                    return exec_ok(executor_name, data=result)
            else:
                # Non-dict result - wrap it
                return exec_ok(executor_name, data=result)
                
        except Exception as e:
            error_msg = f"Error running {executor_name}.{method_name}: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return exec_err(executor_name, error_msg)

    async def _execute_copy_buy(self, token_mint: str, source_wallet: str, *, amount_sol: float = 0.001, trade_info: dict = None, **kwargs) -> dict:
        """
        Canonical copy buy: route by normalized DEX and plan, try each executor in order.
        """
        import traceback
        import time
        
        start_time = time.time()
        
        # Debug logging controlled by config flags
        if getattr(self.config, "execution_debug", False):
            self.logger.debug(f"[COPY BUY] Input: token_mint={token_mint}, source_wallet={source_wallet}, amount_sol={amount_sol}, trade_info={trade_info}, kwargs={kwargs}")
        
        self.logger.info(f"[EXECUTION_START] 🚀 Starting copy buy execution...")
        
        trade_info = trade_info or {}
        dex_key = normalize_dex(trade_info.get("dex_type") or "unknown")
        route_hint = trade_info.get("route_hint", "").strip()
        retry_hint = trade_info.get("retry_hint", "").strip()
        source_tx_failed = trade_info.get("source_tx_failed", False)
        have_mint = bool(token_mint and token_mint != "UNKNOWN")
        
        # Log trade info summary for debugging
        self.logger.info(f"[EXECUTION_SUMMARY] 📊 Trade details:")
        self.logger.info(f"   - Token: {token_mint[:8] if token_mint else 'N/A'}...")
        self.logger.info(f"   - Signature: {trade_info.get('signature', 'N/A')[:12] if trade_info.get('signature') else 'N/A'}...")
        self.logger.info(f"   - DEX: {dex_key}")
        self.logger.info(f"   - Action: {trade_info.get('action', 'N/A')}")
        self.logger.info(f"   - Amount: {amount_sol} SOL")
        self.logger.info(f"   - Source wallet: {source_wallet[:12] if source_wallet else 'N/A'}...")
        if route_hint:
            self.logger.info(f"   - Route hint: {route_hint}")
        if retry_hint:
            self.logger.info(f"   - Retry hint: {retry_hint}")
        if source_tx_failed:
            self.logger.info(f"   - Source TX failed: {source_tx_failed}")
        
        # Enhanced routing logic with route_hint priority
        signature = (trade_info.get("signature") or "").strip()
        
        # NEW ROUTING LOGIC: Handle special cases first
        # 1) Meteora path with retry support
        if dex_key == "meteora":
            self.logger.info("🧭 [COORDINATOR] Route=meteora")
            plan = ["meteora", "jupiter", "direct_copy"]
            self.logger.info(f"[ROUTING] Meteora detected - plan: {plan}")
            if retry_hint == "requote":
                self.logger.info(f"[ROUTING] ⚡ retry_hint='requote' - will force fresh quote/wider slippage for Meteora")
        # 2) Unknown but mint present → Jupiter first
        elif dex_key == "unknown" and have_mint:
            self.logger.info("🧭 [COORDINATOR] Route=unknown; mint present → Jupiter → Meteora → Clone")
            plan = ["jupiter", "meteora", "direct_copy"]
        # 3) Unknown and no mint → if source failed, avoid clone first
        elif dex_key == "unknown" and not have_mint:
            if source_tx_failed:
                self.logger.info("🧭 [COORDINATOR] Source failed → avoid clone; try builders first")
                plan = ["jupiter", "meteora", "direct_copy"]
            else:
                # Use existing logic for unknown without mint
                plan = ROUTE_MAP.get(dex_key, ROUTE_MAP["unknown"])
        # Priority 1: Check for route_hint == 'direct_copy' (from validation when mint is unresolved)
        elif route_hint == "direct_copy":
            plan = ["direct_copy", "jupiter", "raydium", "meteora"]
            self.logger.info(f"[ROUTING] ✅ route_hint='direct_copy' detected - prioritizing direct_copy executor")
        # Priority 2: Check for signature presence
        elif signature and not source_tx_failed:  # Don't prioritize direct_copy if source failed
            plan = ["direct_copy", "jupiter", "raydium", "meteora"]
            self.logger.info(f"[ROUTING] ✅ Signature present - using signature plan: {signature[:12]}...")
        # Priority 3: Use DEX-specific routing from ROUTE_MAP
        else:
            plan = ROUTE_MAP.get(dex_key, ROUTE_MAP["unknown"])
            self.logger.info(f"[ROUTING] Using ROUTE_MAP for dex='{dex_key}': {plan}")
        
        if getattr(self.config, "execution_debug", False):
            self.logger.debug(f"[COPY BUY] Plan: {plan}")
        self.logger.info(f"[ROUTING] Execution plan: {plan}")
        
        executors_attempted = []
        last_error = None
        
        for idx, label in enumerate(plan, 1):
            self.logger.info(f"[EXECUTOR_ATTEMPT] 🎯 [{idx}/{len(plan)}] Attempting: {label}")
            executors_attempted.append(label)
            
            try:
                # Use standardized executor routing
                result = None
                if label == "jupiter":
                    self.logger.info(f"[EXECUTOR_ATTEMPT] → Calling Jupiter executor...")
                    result = await self._execute_jupiter_buy(token_mint, amount_sol, trade_info)
                elif label == "direct_copy":
                    self.logger.info(f"[EXECUTOR_ATTEMPT] → Calling Direct Copy executor...")
                    result = await self._execute_direct_copy_buy(token_mint, source_wallet, amount_sol=amount_sol, trade_info=trade_info, **kwargs)
                elif label == "raydium":
                    self.logger.info(f"[EXECUTOR_ATTEMPT] → Calling Raydium executor...")
                    result = await self._execute_raydium_mev_buy(token_mint, source_wallet, amount_sol=amount_sol, trade_info=trade_info, **kwargs)
                elif label == "meteora":
                    self.logger.info("🧭 [COORDINATOR] Route=meteora → trying Meteora executor")
                    try:
                        # Pass force_requote flag if retry_hint == "requote"
                        force_requote = retry_hint == "requote"
                        if force_requote:
                            self.logger.info("⚡ [METEORA] force_requote=True - requesting fresh quote with wider slippage")
                        result = await self._execute_meteora_buy(
                            token_mint, source_wallet, 
                            amount_sol=amount_sol, 
                            trade_info=trade_info, 
                            force_requote=force_requote,
                            **kwargs
                        )
                    except Exception as e:
                        self.logger.error(f"❌ [METEORA] Build failed: {e}")
                        result = None
                    
                    # Meteora executor is standalone now, no immediate fallback to direct_copy
                    # Let the routing plan continue to next executor
                elif label == "advanced_mev":
                    self.logger.info(f"[EXECUTOR_ATTEMPT] → Calling Advanced MEV executor...")
                    result = await self._execute_advanced_mev_buy(token_mint, source_wallet, amount_sol=amount_sol, trade_info=trade_info, **kwargs)
                else:
                    self.logger.warning(f"[EXECUTOR_ATTEMPT] ⚠️ Unknown executor: {label}")
                    continue
                
                # Use standardized success check - support both "ok" and "success" formats
                if result and (result.get("ok") or result.get("success")) and isinstance(result.get("signature"), str):
                    execution_time = time.time() - start_time
                    self.logger.info(f"[EXECUTION_SUCCESS] ✅ EXECUTED via {label}")
                    self.logger.info(f"   - Signature: {result['signature']}")
                    self.logger.info(f"   - Execution time: {execution_time:.2f}s")
                    self.logger.info(f"   - Executors attempted: {', '.join(executors_attempted)}")
                    return result
                    
                error_msg = result.get("error") if result else "No result returned"
                last_error = error_msg
                self.logger.warning(f"[EXECUTOR_ATTEMPT] ⏭️ Skipped {label}: {error_msg}")
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"[EXECUTOR_ATTEMPT] ❌ Exception in {label}: {e}")
                self.logger.error(traceback.format_exc())
        
        execution_time = time.time() - start_time
        logger.error(f"[EXECUTION_FAILED] ❌ All executors failed")
        logger.error(f"   - Executors attempted: {', '.join(executors_attempted)}")
        logger.error(f"   - Last error: {last_error}")
        logger.error(f"   - Total execution time: {execution_time:.2f}s")
        return exec_err("all_executors", f"All executors failed. Last error: {last_error}")

    
    async def _preflight_check(self, transaction):
        """Simulate transaction and check account status before submission."""
        try:
            if self.rpc_client:
                sim_result = await self.rpc_client.simulate_transaction(transaction)
                if sim_result.value and sim_result.value.err is None:
                    logger.info("[PREFLIGHT] Simulation passed.")
                    return True
                else:
                    logger.warning(f"[PREFLIGHT] Simulation failed: {sim_result.value.err}")
                    return False
            logger.warning("[PREFLIGHT] No RPC client for simulation.")
            return True
        except Exception as e:
            logger.error(f"[PREFLIGHT] Exception: {e}")
            return False

    async def _confirm_transaction(self, signature, max_wait=30):
        """Wait for transaction confirmation, retry if not confirmed."""
        try:
            if self.rpc_client:
                for i in range(max_wait):
                    resp = await self.rpc_client.get_confirmed_transaction(signature)
                    if resp.value:
                        logger.info(f"[CONFIRM] Transaction {signature} confirmed.")
                        return True
                    await asyncio.sleep(1)
                logger.warning(f"[CONFIRM] Transaction {signature} not confirmed after {max_wait}s.")
                return False
            logger.warning("[CONFIRM] No RPC client for confirmation.")
            return False
        except Exception as e:
            logger.error(f"[CONFIRM] Exception: {e}")
            return False

    async def _execute_copy_sell(self, token_mint: str, trade_info: dict = None, source_wallet: str = None, detected_dex: str = None, **kwargs):
        """
        Execute SELL using the same method that worked for buying this token
        """
        # Use parsed transaction context if available
        parsed_tx = None
        if trade_info and 'parsed_tx' in trade_info:
            parsed_tx = trade_info['parsed_tx']
            self.logger.info(f"[COPIER] Using parsed_tx for transaction reconstruction: {parsed_tx.get('dex') if parsed_tx else 'unknown'}")
            required_accounts = parsed_tx.get('swap_info', {}) if parsed_tx.get('dex') == 'Jupiter' else parsed_tx.get('raydium_info', {})
            if parsed_tx.get('dex') == 'Pump.fun':
                required_accounts = parsed_tx.get('pumpfun_info', {})
            if parsed_tx.get('dex') == 'ALT':
                required_accounts = parsed_tx.get('alt_info', {})
            if required_accounts:
                required_accounts['payer'] = str(self._get_wallet_pubkey())
                required_accounts['user_wallet'] = str(self._get_wallet_pubkey())
            kwargs['required_accounts'] = required_accounts
            if parsed_tx.get('dex') == 'ALT':
                kwargs['addressTableLookups'] = required_accounts.get('lookup_tables', [])
                kwargs['resolvedAccounts'] = required_accounts.get('resolved_accounts', [])
        # Log all input parameters for debugging
        logger.debug(f"🔍 [COPY_SELL] Input parameters:")
        logger.debug(f"   Token Mint: {token_mint}")
        logger.debug(f"   Trade Info: {trade_info}")
        logger.debug(f"   Source Wallet: {source_wallet}")
        logger.debug(f"   Detected DEX: {detected_dex}")
        logger.debug(f"   Additional kwargs: {kwargs}")
        
        logger.info(f"🎯 [SMART SELL] Executing SELL for {str(token_mint)[:8]} from {str(source_wallet)[:8] if source_wallet else 'unknown'}")
        
        try:
            # Only use best-practice MEV-protected logic
            pre_balance = await self._get_our_token_balance(token_mint)
            logger.info(f"[WALLET] Pre-sell token balance for {str(token_mint)[:8]}: {pre_balance}")
            
            # Configure for maximum speed and success
            config = DirectSellCopyConfig(
                priority_fee=getattr(self.config, 'priority_fee', 2_000_000),
                compute_limit=getattr(self.config, 'compute_limit', 400_000),
                use_jito_bundles=self.jito_service is not None,
                max_copy_time_ms=getattr(self.config, 'max_copy_time_ms', 500.0),
                jito_tip_amount=getattr(self.config, 'jito_tip_amount', 100_000),
                slippage_tolerance=getattr(self.config, 'slippage_tolerance', 0.05)
            )
            import env_keys
            env = env_keys.EnvKeys()
            private_key = env.PHANTOM_PRIVATE_KEY
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            signature = None
            if source_wallet and trade_info and trade_info.get('signature'):
                from mev_direct_sell_executor import copy_specific_sell_transaction
                signature = await copy_specific_sell_transaction(
                    wallet_private_key=private_key,
                    sell_transaction_signature=trade_info['signature'],
                    token_mint=token_mint,
                    sell_percentage=sell_percentage,
                    config=config
                )
            elif source_wallet:
                from mev_direct_sell_executor import execute_direct_sell_copy
                signature = await execute_direct_sell_copy(
                    wallet_private_key=private_key,
                    target_wallet=source_wallet,
                    token_mint=token_mint,
                    sell_percentage=sell_percentage,
                    config=config
                )
            if signature:
                logger.info(f"✅ [DIRECT SELL COPY] SUCCESS: {signature}")
                # Confirmation and retry logic after signature
                confirmed = await self._confirm_transaction(signature)
                retry_count = 0
                max_retries = getattr(self.config, 'max_retries', 3)
                priority_fee = getattr(self.config, 'priority_fee', 2_000_000)
                while not confirmed and retry_count < max_retries:
                    retry_count += 1
                    priority_fee = int(priority_fee * getattr(self.config, 'priority_fee_increase_factor', 1.5))  # Configurable increase factor
                    logger.warning(f"[RETRY] Sell transaction {signature} not confirmed, retrying with priority_fee={priority_fee} (attempt {retry_count})")
                    # Re-submit transaction with higher priority fee
                    try:
                        signature = await copy_specific_sell_transaction(
                            wallet_private_key=private_key,
                            sell_transaction_signature=trade_info['signature'],
                            token_mint=token_mint,
                            sell_percentage=sell_percentage,
                            config=DirectSellCopyConfig(
                                priority_fee=priority_fee,
                                compute_limit=getattr(self.config, 'compute_limit', 400_000),
                                use_jito_bundles=getattr(self.config, 'use_jito_bundles', False),
                                max_copy_time_ms=getattr(self.config, 'max_copy_time_ms', 500.0),
                                jito_tip_amount=getattr(self.config, 'jito_tip_amount', 100_000),
                                slippage_tolerance=getattr(self.config, 'slippage_tolerance', 0.05)
                            )
                        )
                        confirmed = await self._confirm_transaction(signature)
                    except Exception as e:
                        logger.error(f"[RETRY] Exception during sell retry: {e}", exc_info=True)
                        logger.error(f"   Retry attempt: {retry_count}, Priority fee: {priority_fee}")
                        break
                post_balance = await self._get_our_token_balance(token_mint)
                logger.info(f"[WALLET] Post-sell token balance for {str(token_mint)[:8]}: {post_balance}")
                logger.debug(f"✅ [COPY_SELL] Successfully completed sell with signature: {signature}")
                # Audit log for position change
                log_successful_copy_trade({
                    'action': 'sell',
                    'token_mint': token_mint,
                    'signature': signature,
                    'pre_balance': pre_balance,
                    'post_balance': post_balance,
                    'balance_change': post_balance - pre_balance,
                    'sell_percentage': sell_percentage,
                    'retries': retry_count,
                    'success': confirmed
                })
                return {
                    'success': confirmed,
                    'signature': signature,
                    'method': 'direct_instruction_copy',
                    'dex': detected_dex or 'copied_from_source',
                    'pre_balance': pre_balance,
                    'post_balance': post_balance,
                    'balance_change': post_balance - pre_balance,
                    'sell_percentage': sell_percentage,
                    'retries': retry_count
                }
            else:
                logger.error(f"❌ [COPY_SELL] Failed to execute sell for token {str(token_mint)[:8]}")
                logger.error(f"   Input params: token_mint={token_mint}, source_wallet={source_wallet}, trade_info={trade_info}")
                log_failed_copy_trade(
                    source_wallet or 'unknown',
                    'sell', 
                    token_mint,
                    0.0,  # amount_sol unknown for sell
                    'direct_sell_executor',
                    'Direct SELL copy failed'
                )
                return {'success': False, 'error': 'Direct SELL copy failed'}
            
        except Exception as e:
            logger.error(f"❌ [COPY_SELL] Exception in _execute_copy_sell: {e}", exc_info=True)
            logger.error(f"   Input params: token_mint={token_mint}, trade_info={trade_info}, source_wallet={source_wallet}, detected_dex={detected_dex}, kwargs={kwargs}")
            logger.error(f"   Exception type: {type(e).__name__}")
            return {'success': False, 'error': f'Copy sell exception: {str(e)}'}
    
    async def _detect_token_platform(self, token_mint: str, trade_info: dict = None) -> str:
        """
        Detect which platform/DEX the token is traded on.
        
        Args:
            token_mint: Token mint address
            trade_info: Optional trade information from transaction analysis
            
        Returns:
            Platform name: 'pumpfun', 'raydium_cpmm', 'meteora_damm_v2', 'advanced_mev_bot', or 'unknown'
        """
        try:
            # Log what coordinator receives for debugging
            logger.info(f"[EXEC] dex_hint={trade_info.get('dex_type') if trade_info else None} router={trade_info.get('router_program_id') if trade_info else None}")
            # DEBUGGING: Log what we receive in trade_info
            logger.info(f"🔍 Platform detection for {str(token_mint)[:8]} - trade_info keys: {list(trade_info.keys()) if trade_info else 'None'}")
            if trade_info and 'router_program_id' in trade_info:
                logger.info(f"🔍 Router program ID found: {trade_info['router_program_id']}")
            
            # PRIORITY 0: Check router program ID FIRST (most reliable for Jupiter routing)
            router_program_id = None
            if trade_info:
                router_program_id = trade_info.get('router_program_id')
                # Jupiter router gets HIGHEST priority to fix routing issue
                if router_program_id == "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4":
                    logger.info(f"🪐 Detected Jupiter from router program ID - using Jupiter Copy executor")
                    return normalize_dex('jupiter')
            
            # Check other router program IDs
            known_dex_programs = {
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun
                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium CPMM
                "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Pump.fun AMM
                "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",  # Raydium CPMM v2
            }
            
            if router_program_id and router_program_id in known_dex_programs:
                if router_program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    logger.info(f"🚀 Detected Pump.fun from router program ID")
                    return normalize_dex('pumpfun')
                elif router_program_id in ["675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"]:
                    logger.info(f"🎯 Detected Raydium CPMM from router program ID")
                    return normalize_dex('mev_raydium')
                elif router_program_id == "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA":
                    logger.info(f"🚀 Detected Pump.fun AMM from router program ID")
                    return normalize_dex('pumpfun')
            
            # PRIORITY 1: Check basic_analysis detected_dex from websocket handler (NEW ADDITION)
            if trade_info and 'basic_analysis' in trade_info:
                basic_analysis = trade_info['basic_analysis']
                detected_dex = basic_analysis.get('detected_dex', 'unknown')
                
                if detected_dex != 'unknown':
                    logger.info(f"🎯 Using DEX detection from basic_analysis: {detected_dex}")
                    
                    return normalize_dex(detected_dex)
            
            # PRIORITY 2: Check program IDs from logs (most reliable)
            if trade_info and 'logs' in trade_info:
                logs = trade_info['logs']
                log_text = ' '.join(logs) if isinstance(logs, list) else str(logs)
                
                # Check for Jupiter router programs FIRST (CRITICAL FIX)
                if ('JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4' in log_text or
                    'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB' in log_text):
                    logger.info(f"🪐 Detected Jupiter router from transaction logs - routing to Jupiter Copy")
                    return normalize_dex('jupiter')
                
                # Check for Raydium CPMM program (HIGHEST PRIORITY)
                if 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C' in log_text:
                    logger.info(f"🎯 Detected Raydium CPMM from transaction logs - routing to Raydium")
                    return 'raydium'

                # Check for the ACTUAL program ID found in your trades (CRITICAL FIX)
                if 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj' in log_text:
                    logger.info(f"🎯 Detected LanMV9s DEX from transaction logs - routing to Advanced MEV")
                    return 'advanced'

                # Check for Pump.fun programs (BOTH active program IDs)
                if ('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' in log_text or 
                    '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC' in log_text or
                    'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq' in log_text):
                    logger.info(f"🚀 Detected Pump.fun from transaction logs")
                    return 'pumpfun'

                # Check for Meteora DAMM v2
                if 'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN' in log_text:
                    logger.info(f"🎯 Detected Meteora DAMM v2 from transaction logs")
                    return 'meteora'
            
            # Check if we have program information from trade analysis
            if trade_info and 'programs_used' in trade_info:
                programs = trade_info['programs_used']
                
                # Check for Pump.fun programs (HIGHEST PRIORITY - REAL EXECUTOR)
                pumpfun_direct = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
                pumpfun_router = "F5tfvbLog9VdGUPqBDTT8rgXvTcq7e5UiGnupL1zvBq"
                pumpfun_amm = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
                if (pumpfun_direct in str(programs) or 
                    pumpfun_router in str(programs) or 
                    pumpfun_amm in str(programs)):
                    logger.info(f"🚀 Detected Pump.fun from transaction programs - using REAL MEV executor")
                    return 'pumpfun'
                

                # Check for Raydium CPMM program (REAL EXECUTOR)
                raydium_cpmm_program = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
                if raydium_cpmm_program in str(programs):
                    logger.info(f"🎯 Detected Raydium CPMM from transaction programs - using REAL MEV Raydium")
                    return 'raydium'

                # Check for Meteora DAMM v2 (REAL EXECUTOR)
                meteora_damm_v2_id = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
                if meteora_damm_v2_id in str(programs):
                    logger.info(f"🎯 Detected Meteora DAMM v2 from transaction programs - using REAL MEV Meteora")
                    return 'meteora'
                
                # Jupiter router detection (route to Jupiter executor)
                jupiter_program = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
                if jupiter_program in str(programs):
                    logger.info(f"🪐 Detected Jupiter routing - using Jupiter Copy executor")
                    return 'jupiter'
            
            # Priority 2: Check if trade_info has dex_type or dex from transaction analyzer (fallback)
            dex_type = None
            if trade_info and 'dex_type' in trade_info:
                dex_type = trade_info['dex_type']
            elif trade_info and 'dex' in trade_info:
                dex_type = trade_info['dex']
            
            if dex_type and dex_type != 'unknown':  # Skip 'unknown' dex_type as it's not informative
                logger.info(f"🎯 Using detected DEX from trade analysis: {dex_type}")
                
                if dex_type == 'raydium_cpmm':
                    logger.info(f"🎯 Detected Raydium CPMM from trade analysis - using REAL MEV Raydium")
                    return 'raydium'
                elif dex_type == 'pumpfun':
                    logger.info(f"🚀 Detected Pump.fun from trade analysis - using REAL MEV Pump.fun")
                    return 'pumpfun'
                elif dex_type in ['raydium_v4', 'raydium_clmm']:
                    logger.info(f"🎯 Detected Raydium ({dex_type}) - using REAL MEV Raydium")
                    return 'raydium'
                elif dex_type == 'meteora_damm_v2':
                    logger.info(f"🎯 Detected Meteora DAMM v2 - using REAL MEV Meteora")
                    return 'meteora'
                elif dex_type in ['jupiter', 'orca']:
                    logger.info(f"🪐 Detected {dex_type} - using Jupiter Copy executor")
                    return 'jupiter'
            
            # TODO: Add additional detection methods:
            # - Check token metadata  
            # - Query pool existence on different platforms
            # - Use pattern analysis from successful wallets
            
            # If no valid router found, don't execute on non-trading transactions
            if not router_program_id or router_program_id not in known_dex_programs:
                if not dex_type or dex_type == 'unknown':
                    logger.warning(f"❌ Skipping execution - no valid DEX router found")
                    logger.warning(f"   Router: {router_program_id}, DEX: {dex_type}")
                    logger.warning(f"   This appears to be a non-trading transaction (system transfer, etc.)")
                    return None  # Don't execute on non-trading transactions
            
            # Check for valid instruction data on the router program
            if trade_info and 'transaction' in trade_info and router_program_id:
                tx_data = trade_info['transaction']
                if 'instructions' in tx_data:
                    for instruction in tx_data['instructions']:
                        if instruction.get('programId') == router_program_id:
                            # Check if instruction data is valid (not empty or all zeros)
                            instruction_data = instruction.get('data', '')
                            if not instruction_data or instruction_data == '0000000000000000' or instruction_data == '00' * 8:
                                logger.warning(f"❌ Skipping execution - invalid instruction data for {router_program_id}")
                                logger.warning(f"   Instruction data: {instruction_data}")
                                logger.warning(f"   This appears to be a failed/invalid trading transaction")
                                return None
            
            # If we reach here, no supported DEX/platform detected
            logger.warning(f"Mint extraction failed for trade {trade_info.get('signature', 'unknown') if trade_info else 'no_trade_info'}, trade_info: {trade_info}")
            logger.warning(f"❌ No supported DEX/platform detected for token {str(token_mint)[:8]}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error detecting token platform: {e}")
            return None  # Do not fallback, skip execution
    
    async def _execute_direct_copy_buy(self, token_mint: str, source_wallet: str, *, amount_sol: float = 0.001, trade_info: dict = None, **kwargs):
        """Execute direct copy buy using transaction cloner"""
        from transaction_cloner import clone_tx_from_signature
        
        # Guard: Skip cloning slippage-failed source transactions
        if trade_info and trade_info.get("retry_hint") == "requote":
            logger.info("ℹ️ [CLONE] Skipping clone of a slippage-failed source — using builders first")
            return None
        
        # Get signature from trade_info
        sig = trade_info.get("signature") if trade_info else None
        if not sig:
            logger.error("❌ [COORDINATOR] direct_copy requested but no signature present")
            return {'success': False, 'error': 'No signature for direct_copy'}
        
        logger.info(f"🚀 [COORDINATOR] Executing via direct_copy for signature {sig[:12]}...")
        
        try:
            # Get RPC URL and keypair
            import env_keys
            env = env_keys.EnvKeys()
            rpc_url = env.HELIUS_RPC_URL
            
            # Get keypair for new payer - explicit validation, no fallback
            keypair = self._require_keypair()
            
            # Call the cloner
            vtx = await clone_tx_from_signature(
                rpc=rpc_url,
                signature=sig,
                new_payer=keypair
            )
        except Exception as e:
            logger.error(f"❌ [COORDINATOR] Cloner failed: {e}")
            return {'success': False, 'error': f'Cloner exception: {str(e)}'}
        
        if not vtx:
            logger.error("❌ [PREFLIGHT] No valid VersionedTransaction from cloner — skipping execution")
            return {'success': False, 'error': 'Cloner returned None'}
        
        # Submit using existing executor path (Jito first, fallback RPC)
        try:
            # Use fast_executor if available for submission
            if self.fast_executor:
                tx_sig = await self.fast_executor.submit_transaction(vtx)
            else:
                # Fallback: create a temporary fast executor
                from fast_executor import FastExecutor
                temp_executor = FastExecutor(
                    keypair=keypair,
                    rpc_url=rpc_url,
                    jito_service=self.jito_service
                )
                await temp_executor.initialize()
                tx_sig = await temp_executor.submit_transaction(vtx)
                await temp_executor.close()
            
            if tx_sig:
                logger.info(f"✅ [EXECUTION] direct_copy submitted: {tx_sig}")
                return {'success': True, 'signature': tx_sig, 'method': 'direct_copy'}
            else:
                logger.error("❌ [EXECUTION] Submission returned no signature")
                return {'success': False, 'error': 'Submission failed - no signature'}
        except Exception as e:
            logger.error(f"❌ [EXECUTION] Submission failed: {e}")
            return {'success': False, 'error': f'Submission exception: {str(e)}'}
    
    async def _execute_raydium_mev_buy(self, token_mint: str, source_wallet: str, **kwargs):
        """Execute Raydium CPMM buy using dedicated Raydium MEV executor"""
        try:
            # Removed undefined flag MEV_RAYDIUM_AVAILABLE
            self.logger.info(f"🎯 Executing Raydium MEV buy for {token_mint[:8]}...")
            # Use the same interface as other MEV executors
            buy_executor = try_raydium_buy
            dex_name = 'mev_raydium'
            logger.debug(f"[DEBUG] Calling Raydium MEV executor for {token_mint[:8]}...")
            # Remove trade_info from kwargs to avoid duplicate parameter
            executor_kwargs = {k: v for k, v in kwargs.items() if k != 'trade_info'}
            result = await self._submit_with_retries(
                self._try_single_executor_buy,
                dex_name, buy_executor, token_mint, source_wallet,
                trade_info=kwargs.get('trade_info'),
                routing_instructions=kwargs.get('routing_instructions'),
                detected_dex=dex_name,
                **executor_kwargs
            )
            logger.debug(f"[DEBUG] Raydium MEV executor result: {result}")
            if result and result.get('success'):
                logger.info(f"✅ Raydium MEV buy executed successfully for token {token_mint[:8]}...")
                return result
            else:
                logger.error(f"❌ Raydium MEV buy execution failed for token {token_mint[:8]}: {result.get('error') if result else 'Unknown error'}")
                logger.info(f"🔄 Falling back to Advanced MEV executor...")
                return await self._execute_advanced_mev_buy(token_mint, source_wallet, **kwargs)
        except Exception as e:
            logger.error(f"❌ Exception during Raydium MEV buy execution for token {token_mint[:8]}: {e}")
            logger.info(f"🔄 Exception fallback to Advanced MEV...")
            return await self._execute_advanced_mev_buy(token_mint, source_wallet, **kwargs)
    
    async def _submit_with_retries(self, executor_func, *args, max_retries=3, retry_delay=1.0, **kwargs):
        """
        Submit transaction with retry logic and error handling
        
        Args:
            executor_func: The executor function to call
            *args: Positional arguments for executor_func
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Keyword arguments for executor_func
            
        Returns:
            Result dict from executor or error result
        """
        last_error = None
        
        # Get retries from config if available
        if self.config:
            max_retries = getattr(self.config, 'max_retries', max_retries)
            retry_delay = getattr(self.config, 'retry_delay', retry_delay)
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 Attempt {attempt + 1}/{max_retries} for executor")
                result = await executor_func(*args, **kwargs)
                
                # Check if result indicates success
                if result and result.get('success'):
                    logger.debug(f"✅ Executor succeeded on attempt {attempt + 1}")
                    return result
                
                # Result indicates failure, but might be retryable
                last_error = result.get('error', 'Unknown error') if result else 'No result returned'
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {last_error}")
                
                # Don't retry on last attempt
                if attempt < max_retries - 1:
                    logger.debug(f"⏳ Waiting {retry_delay}s before retry...")
                    await asyncio.sleep(retry_delay)
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Exception on attempt {attempt + 1}: {e}")
                
                # Don't retry on last attempt
                if attempt < max_retries - 1:
                    logger.debug(f"⏳ Waiting {retry_delay}s before retry...")
                    await asyncio.sleep(retry_delay)
        
        # All retries exhausted
        logger.error(f"❌ All {max_retries} retry attempts failed. Last error: {last_error}")
        return {
            'success': False,
            'error': f'All retry attempts failed: {last_error}',
            'retries': max_retries
        }
    
    
    async def _execute_advanced_mev_buy(self, token_mint: str, source_wallet: str, **kwargs):
        """Execute Advanced MEV Bot buy using reverse-engineered patterns"""
        try:
            logger.info(f"🚀 Executing Advanced MEV Bot buy for {token_mint[:8]}...")
            # Use the existing Advanced MEV executor
            if not self.advanced_mev_executor:
                logger.warning(f"⚠️ Advanced MEV executor not initialized - falling back to direct copy")
                return await self._execute_direct_copy_buy(token_mint, source_wallet, **kwargs)
            # Execute the buy with proper parameter object
            amount_sol = kwargs.get('amount_sol', 0.001)  # Default amount matches MEV minimum
            trade_info = kwargs.get('trade_info', {})
            from mev_advanced_bot_executor import AdvancedMEVTradeParams
            params = AdvancedMEVTradeParams(
                token_mint=token_mint,
                amount_sol=amount_sol,
                slippage_percent=trade_info.get("slippage_tolerance", 1.0),
                # Add other params from trade_info or kwargs as needed
            )
            result = await self.advanced_mev_executor.execute_buy(params)
            if result and result.success:  # Use dot notation for dataclass
                logger.info(f"✅ Advanced MEV Bot buy executed successfully for token {token_mint[:8]}...")
                return {
                    'success': True,
                    'signature': result.signature,
                    'dex': 'advanced_mev'
                }
            else:
                logger.error(f"❌ Advanced MEV Bot buy execution failed for token {token_mint[:8]}: {result.error if result else 'Unknown error'}")
                # Fallback to direct copy if Advanced MEV Bot fails
                logger.info(f"🔄 Falling back to direct copy for token {token_mint[:8]}...")
                return await self._execute_direct_copy_buy(token_mint, source_wallet, **kwargs)
        except Exception as e:
            logger.error(f"❌ Exception during Advanced MEV Bot buy execution for token {token_mint[:8]}: {e}")
            # Fallback to direct copy on exception
            logger.info(f"🔄 Exception fallback to direct copy for token {token_mint[:8]}...")
            return await self._execute_direct_copy_buy(token_mint, source_wallet, **kwargs)
    
    async def _execute_advanced_mev_sell(self, token_mint: str, source_wallet: str = None, **kwargs):
        """Execute Advanced MEV Bot sell using reverse-engineered patterns"""
        try:
            logger.info(f"🚀 Executing Advanced MEV Bot sell for {token_mint[:8]}...")
            
            # Use the existing Advanced MEV executor
            if not self.advanced_mev_executor:
                logger.warning(f"⚠️ Advanced MEV executor not initialized - using generic sell")
                return await self._execute_copy_sell(token_mint, source_wallet=source_wallet, **kwargs)
            
            # Execute the sell with proper parameter object
            trade_info = kwargs.get('trade_info', {})
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            
            from mev_advanced_bot_executor import AdvancedMEVTradeParams
            params = AdvancedMEVTradeParams(
                token_mint=token_mint,
                sell_percentage=sell_percentage,
                slippage_percent=trade_info.get("slippage_tolerance", 1.0),
                # Add other params from trade_info or kwargs as needed
            )
            
            result = await self.advanced_mev_executor.execute_sell_all(params)
            
            if result and result.success:  # Use dot notation for dataclass
                logger.info(f"✅ Advanced MEV Bot sell executed successfully for token {token_mint[:8]}...")
                return {
                    'success': True,
                    'signature': result.signature,
                    'dex': 'advanced_mev'
                }
            else:
                logger.error(f"❌ Advanced MEV Bot sell execution failed for token {token_mint[:8]}: {result.error if result else 'Unknown error'}")
                # Fallback to generic sell if Advanced MEV Bot fails
                logger.info(f"🔄 Falling back to generic sell for token {token_mint[:8]}...")
                return await self._execute_copy_sell(token_mint, source_wallet=source_wallet, **kwargs)
                
        except Exception as e:
            logger.error(f"❌ Exception during Advanced MEV Bot sell execution for token {token_mint[:8]}: {e}")
            # Fallback to generic sell on exception
            logger.info(f"🔄 Exception fallback to generic sell for token {token_mint[:8]}...")
            return await self._execute_copy_sell(token_mint, source_wallet=source_wallet, **kwargs)
    
    async def _execute_meteora_buy(self, token_mint: str, source_wallet: str, **kwargs):
        """Execute Meteora DAMM v2 buy using MEV executor with smart error handling"""
        # Log all input parameters for debugging
        logger.debug(f"🔍 [METEORA_BUY] Input parameters:")
        logger.debug(f"   Token Mint: {token_mint}")
        logger.debug(f"   Source Wallet: {source_wallet}")
        logger.debug(f"   Additional kwargs: {kwargs}")
        
        force_requote = kwargs.get('force_requote', False)
        if force_requote:
            logger.info(f"⚡ [METEORA_BUY] force_requote=True - will request fresh quote with wider slippage")
        
        try:
            logger.info(f"🎯 Executing MEV Meteora DAMM v2 buy for {token_mint[:8]}...")
            # Use new MEV wrapper function for compatibility
            from mev_meteora_executor import mev_meteora_copy_trade
            # Execute the MEV-protected buy
            amount_sol = kwargs.get('amount_sol', 0.001)  # Default amount matches MEV minimum
            
            # Extract source transaction signature from trade_info or kwargs
            trade_info = kwargs.get('trade_info', {})
            original_signature = trade_info.get('signature') if trade_info else kwargs.get('original_signature', '')
            
            if not original_signature:
                logger.warning(f"⚠️ [METEORA_BUY] No source transaction signature provided - may affect execution")
            
            # Extract keypair with proper validation - explicit validation, no fallback
            wallet_keypair = self._require_keypair()
            self.logger.info(f"Using wallet keypair for mev_meteora_copy_trade: {type(wallet_keypair)}")
            result = await mev_meteora_copy_trade(
                wallet_keypair=wallet_keypair,
                fast_executor=self.fast_executor,  # ✅ FIXED: Use initialized fast_executor
                source_tx_signature=original_signature,
                source_wallet=source_wallet,
                token_mint=token_mint,
                amount_sol=amount_sol,
                detected_action="buy",
                jito_service=self.jito_service,
                force_requote=force_requote  # Pass force_requote flag
            )
            logger.debug(f"🚀 [METEORA_BUY] Executing mev_meteora_copy_trade with parameters:")
            logger.debug(f"   wallet_keypair: {type(wallet_keypair)}")
            logger.debug(f"   fast_executor: {self.fast_executor}")
            logger.debug(f"   source_tx_signature: {original_signature}")
            logger.debug(f"   source_wallet: {source_wallet}")
            logger.debug(f"   token_mint: {token_mint}")
            logger.debug(f"   amount_sol: {amount_sol}")
            logger.debug(f"   force_requote: {force_requote}")
            
            if result:
                logger.info(f"✅ [METEORA_BUY] MEV Meteora DAMM v2 buy executed successfully: {result}")
                logger.debug(f"   Full result: {result}")
                return {'success': True, 'signature': result}
            else:
                logger.error(f"❌ [METEORA_BUY] MEV Meteora DAMM v2 buy execution failed for token {token_mint[:8]}")
                logger.error(f"   Result was None or falsy: {result}")
                logger.error(f"   Input params: token_mint={token_mint}, source_wallet={source_wallet}, amount_sol={amount_sol}")
                return {'success': False, 'error': 'Meteora executor not available'}
        except Exception as e:
            logger.error(f"❌ [METEORA_BUY] Exception during Meteora DAMM v2 buy execution for token {token_mint[:8]}: {e}", exc_info=True)
            logger.error(f"   Input params: token_mint={token_mint}, source_wallet={source_wallet}, kwargs={kwargs}")
            logger.error(f"   Exception type: {type(e).__name__}")
            return {'success': False, 'error': str(e)}


    def _record_successful_execution_method(self, token_mint: str, action: str, method: str):
        """Record which execution method worked for a token"""
        if token_mint not in self.token_execution_methods:
            self.token_execution_methods[token_mint] = {}
        
        self.token_execution_methods[token_mint][f'{action}_method'] = method
        self.logger.info(f"📝 [EXECUTION TRACKING] Recorded {action.upper()} method '{method}' for token {token_mint[:8]}...")

    async def _execute_jupiter_buy(self, token_mint: str, amount_sol: float, trade_info: dict) -> dict:
        if getattr(self.config, "execution_debug", False):
            self.logger.debug(f"[JUPITER_BUY] Input: token_mint={token_mint}, amount_sol={amount_sol}, trade_info={trade_info}")
        try:
            if getattr(self.config, "deep_debug", False):
                logger.debug(f"🚀 [JUPITER_BUY] Starting MEV + fresh build path")
            # MEV + fresh build path (no cloning)
            from mev_jupiter_executor import MEVJupiterExecutor

            # Use proper wallet validation for MEVJupiterExecutor - explicit validation, no fallback
            wallet_keypair = self._require_keypair()
            if getattr(self.config, "deep_debug", False):
                self.logger.debug(f"Creating MEVJupiterExecutor with wallet type: {type(wallet_keypair)}")
            
            # Validate and convert config for executor compatibility
            if hasattr(self.config, 'validate_executor_config'):
                config_valid = self.config.validate_executor_config()
                if getattr(self.config, "debug", False):
                    self.logger.debug(f"Config validation result: {config_valid}")
                if not config_valid:
                    self.logger.warning("⚠️ Config validation failed, using defaults")
            
            # Convert to SolanaExecutorConfig if method exists
            executor_config = self.config
            if hasattr(self.config, 'to_solana_executor_config'):
                try:
                    executor_config = self.config.to_solana_executor_config()
                    if getattr(self.config, "debug", False):
                        self.logger.debug("✅ Successfully converted config to SolanaExecutorConfig")
                except Exception as e:
                    self.logger.warning(f"⚠️ Config conversion failed, using original: {e}")
                    executor_config = self.config
            
            if getattr(self.config, "deep_debug", False):
                self.logger.debug(f"Creating MEVJupiterExecutor with config: {type(executor_config)}")
            executor = MEVJupiterExecutor(
                wallet_keypair=wallet_keypair,
                rpc_url=self.rpc_client.endpoint_uri if hasattr(self.rpc_client, 'endpoint_uri') else self.config.rpc_url,
                config=executor_config,
                jito_service=self.jito_service
            )

            # Use the actual execute_buy method signature
            self.logger.debug(f"Calling executor.execute_buy with slippage_bps=300")
            res = await executor.execute_buy(
                token_mint=token_mint,
                amount_sol=amount_sol,
                trade_info=trade_info,
                slippage_bps=300
            )
            
            self.logger.debug(f"[JUPITER_BUY] Result: {res}")
            if res and res.get("success"):
                self.logger.debug(f"Jupiter buy success details: {res}")
                return {"success": True, "signature": res["signature"], "dex": "jupiter"}
            else:
                self.logger.warning(f"[JUPITER_BUY] Failure details: {res}")
                return {"success": False, "error": res.get("error", "Jupiter buy failed"), "dex": "jupiter"}
        except Exception as e:
            self.logger.exception(f"[JUPITER_BUY] Exception: {e}")
            return {"success": False, "error": str(e), "dex": "jupiter"}

    async def _execute_jupiter_sell(self, token_mint: str, source_wallet: str, trade_info: dict = None, **kwargs):
        """Execute Jupiter sell using similar approach to Jupiter buy"""
        # Log all input parameters for debugging
        logger.debug(f"🔍 [JUPITER_SELL] Input parameters:")
        logger.debug(f"   Token Mint: {token_mint}")
        logger.debug(f"   Source Wallet: {source_wallet}")
        logger.debug(f"   Trade Info: {trade_info}")
        logger.debug(f"   Additional kwargs: {kwargs}")
        
        try:
            logger.info(f"🪐 [JUPITER SELL] Executing Jupiter sell for {token_mint[:8]}...")
            
            # Import Jupiter sell executor
            try:
                from jupiter_copy_executor import execute_jupiter_sell_copy
                
                # Get wallet private key
                import env_keys
                env = env_keys.EnvKeys()
                private_key = env.PHANTOM_PRIVATE_KEY
                
                logger.debug(f"🚀 [JUPITER_SELL] Executing execute_jupiter_sell_copy with parameters:")
                logger.debug(f"   token_mint: {token_mint}")
                logger.debug(f"   private_key_bytes: [REDACTED]")
                logger.debug(f"   trade_info: {trade_info}")
                logger.debug(f"   source_wallet: {source_wallet}")
                
                # Execute Jupiter sell with copy strategy
                result = await execute_jupiter_sell_copy(
                    token_mint=token_mint,
                    private_key_bytes=bytes.fromhex(private_key),
                    trade_info=trade_info,
                    source_wallet=source_wallet,
                    **kwargs
                )
                
                logger.debug(f"✅ [JUPITER_SELL] Execution result: {result}")
                
                if result and result.get('success'):
                    logger.info(f"✅ [JUPITER_SELL] Success: {result.get('signature')[:12]}...")
                    logger.debug(f"   Full success result: {result}")
                    return {
                        'success': True,
                        'signature': result.get('signature'),
                        'method': 'jupiter_sell_copy'
                    }
                else:
                    logger.error(f"❌ [JUPITER_SELL] Failed: {result.get('error') if result else 'No result'}")
                    logger.error(f"   Full failure result: {result}")
                    logger.error(f"   Input params: token_mint={token_mint}, source_wallet={source_wallet}, trade_info={trade_info}")
                    return {'success': False, 'error': result.get('error') if result else 'Jupiter sell failed'}
                    
            except ImportError as import_e:
                logger.error(f"❌ [JUPITER_SELL] Jupiter sell executor not available: {import_e}", exc_info=True)
                return {'success': False, 'error': 'Jupiter sell executor not available'}
                
        except Exception as e:
            logger.error(f"❌ [JUPITER_SELL] Exception during Jupiter sell for {token_mint[:8]}: {e}", exc_info=True)
            logger.error(f"   Input params: token_mint={token_mint}, source_wallet={source_wallet}, trade_info={trade_info}, kwargs={kwargs}")
            logger.error(f"   Exception type: {type(e).__name__}")
            return {'success': False, 'error': str(e)}


    async def _get_our_token_balance(self, token_mint: str) -> float:
        try:
            # Debug logging for token mint type and value
            logger.debug(f"_get_our_token_balance called with type: {type(token_mint)}, value: {token_mint}")
            
            if hasattr(self.wallet, 'get_token_balance'):
                return await self.wallet.get_token_balance(token_mint)
            if self.rpc_client:
                from solders.pubkey import Pubkey
                from utils import get_associated_token_address
                wallet_pubkey = self._get_wallet_pubkey()
                
                # Handle both string and Pubkey inputs with proper type conversion
                try:
                    if isinstance(token_mint, Pubkey):
                        logger.debug(f"Token mint is already a Pubkey: {token_mint}")
                        mint_pubkey = token_mint
                    elif isinstance(token_mint, str):
                        logger.debug(f"Converting string token mint to Pubkey: {token_mint}")
                        mint_pubkey = Pubkey.from_string(token_mint)
                    else:
                        # Try to convert to string first, then to Pubkey
                        token_mint_str = str(token_mint)
                        logger.debug(f"Converting {type(token_mint)} to string then Pubkey: {token_mint_str}")
                        mint_pubkey = Pubkey.from_string(token_mint_str)
                        
                except Exception as conversion_error:
                    logger.error(f"Failed to convert token_mint to Pubkey - type: {type(token_mint)}, value: {token_mint}, error: {conversion_error}")
                    raise ValueError(f"Invalid token_mint format: {type(token_mint)} - {token_mint}")
                
                token_account = get_associated_token_address(wallet_pubkey, mint_pubkey)
                logger.debug(f"Token account address: {token_account} (type: {type(token_account)})")
                response = await self.rpc_client.get_token_account_balance(token_account)
                if response and hasattr(response, 'value') and response.value:
                    if hasattr(response.value, 'ui_amount'):
                        return float(response.value.ui_amount)
                    if isinstance(response.value, dict) and 'uiAmount' in response.value:
                        return float(response.value['uiAmount'])
                return 0.0
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching token balance for {token_mint} (type: {type(token_mint)}): {e}")
            return 0.0

    def __init__(self, wallet, rpc_client=None, jito_service=None, config=None):
        self.wallet = wallet
        self.rpc_client = rpc_client
        self.jito_service = jito_service
        self.config = config
        self.logger = logging.getLogger(__name__)  # Add instance logger
        self.execution_history = []  # Initialize execution history
        self.token_execution_methods = defaultdict(dict)  # Track execution methods per token
        
        # Validate config for executor compatibility
        if self.config and hasattr(self.config, 'validate_executor_config'):
            try:
                config_valid = self.config.validate_executor_config()
                if config_valid:
                    self.logger.info("✅ Executor config validation passed")
                else:
                    self.logger.warning("⚠️ Executor config validation failed - some executors may fail")
            except Exception as e:
                self.logger.error(f"❌ Config validation error: {e}")
        
        # Initialize executors
        self.fast_executor = self._initialize_fast_executor()
        # Note: direct_pumpfun_executor removed - now using MEVDirectCopyExecutor via ROUTE_MAP routing
        self.direct_pumpfun_executor = None
            
        try:
            from mev_advanced_bot_executor import MEVAdvancedBotExecutor
            # MEVAdvancedBotExecutor requires a proper Keypair - explicit validation, no fallback
            wallet_keypair = self._require_keypair()
            self.logger.info(f"Initializing MEVAdvancedBotExecutor with wallet type: {type(wallet_keypair)}")
            self.advanced_mev_executor = MEVAdvancedBotExecutor(wallet_keypair, self.rpc_client, self.jito_service)
        except ImportError:
            self.logger.warning("⚠️ MEVAdvancedBotExecutor not available")
            self.advanced_mev_executor = None
            
        try:
            from mev_meteora_executor import MEVMeteoraExecutor
            # MEVMeteoraExecutor requires a proper Keypair - explicit validation, no fallback
            wallet_keypair = self._require_keypair()
            self.logger.info(f"Initializing MEVMeteoraExecutor with wallet type: {type(wallet_keypair)}")
            self.meteora_executor = MEVMeteoraExecutor(wallet_keypair, self.rpc_client, jito_service=self.jito_service)
        except ImportError:
            self.logger.warning("⚠️ MEVMeteoraExecutor not available")
            self.meteora_executor = None
            
        self.logger.info(f"✅ Execution Coordinator initialized with wallet {self.wallet}")

    def _require_keypair(self):
        """
        Fetch and validate the real Keypair from wallet configuration.
        
        Never fabricates a random keypair. If the configured wallet isn't loaded or 
        is not a valid Keypair, raises TypeError.
        
        Returns:
            solders.keypair.Keypair: The raw keypair object
            
        Raises:
            TypeError: If wallet is not loaded or not a valid Keypair
        """
        if hasattr(self.wallet, 'keypair'):
            keypair = self.wallet.keypair
            # Assert the extracted keypair is actually a Keypair instance
            if not isinstance(keypair, Keypair):
                error_msg = f"Wallet.keypair is not a Keypair instance: {type(keypair)}"
                self.logger.error(error_msg)
                raise TypeError(error_msg)
            self.logger.info(f"Extracted keypair from wallet wrapper: {type(self.wallet)} -> {type(keypair)}")
            return keypair
        elif isinstance(self.wallet, Keypair):
            self.logger.info(f"Wallet is already a Keypair: {type(self.wallet)}")
            return self.wallet
        else:
            error_msg = f"Configured wallet not loaded or invalid: {type(self.wallet)}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
    
    def _get_keypair(self):
        """
        DEPRECATED: Use _require_keypair() instead for explicit validation.
        
        This method is retained only for backward compatibility.
        All new code should use _require_keypair() directly.
        """
        import warnings
        warnings.warn(
            "_get_keypair() is deprecated, use _require_keypair() instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self._require_keypair()

    def _get_wallet_pubkey(self):
        """Extract public key from wallet with proper type validation"""
        if hasattr(self.wallet, 'pubkey'):
            pubkey = self.wallet.pubkey()
            self.logger.debug(f"Extracted pubkey from wallet: {type(self.wallet)} -> {pubkey}")
            return pubkey
        elif hasattr(self.wallet, 'public_key'):
            pubkey = self.wallet.public_key
            self.logger.debug(f"Extracted public_key from wallet: {type(self.wallet)} -> {pubkey}")
            return pubkey
        elif isinstance(self.wallet, Keypair):
            pubkey = self.wallet.pubkey()
            self.logger.debug(f"Extracted pubkey from Keypair: {pubkey}")
            return pubkey
        else:
            error_msg = f"Cannot extract public key from wallet type {type(self.wallet)}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)

    def _initialize_fast_executor(self):
        """Initialize fast executor for Meteora operations"""
        try:
            # Import and initialize the fast executor if available
            try:
                from mev_meteora_executor import MeteoraFastExecutor
                wallet_keypair = self.wallet.keypair if hasattr(self.wallet, 'keypair') else self.wallet
                fast_executor = MeteoraFastExecutor(
                    wallet=wallet_keypair,
                    rpc_client=self.rpc_client,
                    jito_service=self.jito_service
                )
                logger.info("✅ Fast executor initialized successfully")
                return fast_executor
            except Exception:
                logger.info("⚠️ MeteoraFastExecutor not available - using fallback")
                return None
        except Exception as e:
            logger.error(f"❌ Error initializing fast executor: {e}")
            return None

    async def _try_single_executor_buy(self, dex_name: str, buy_executor, token_mint: str, source_wallet: str, **kwargs):
        """Try a single executor with timeout and error handling. Forwards all kwargs to executor.
        This method handles the logic for executing a buy on the specified DEX using the provided executor.
        """
        # Log all input parameters for debugging
        logger.debug(f"🔍 [EXECUTOR_BUY] Input parameters for {dex_name.upper()}:")
        logger.debug(f"   DEX Name: {dex_name}")
        logger.debug(f"   Executor: {buy_executor}")
        logger.debug(f"   Token Mint: {token_mint}")
        logger.debug(f"   Source Wallet: {source_wallet}")
        logger.debug(f"   Additional kwargs: {kwargs}")
        
        try:
            logger.debug(f"   🎯 Trying {dex_name.upper()} for {token_mint[:8]}... (buy_executor={buy_executor})")
            # Robust context validation - NEVER fabricate random keypair
            config = getattr(self, 'config', None)
            
            # Use _require_keypair() to get validated keypair - raises if wallet not loaded
            try:
                wallet_keypair = self._require_keypair()
            except TypeError as e:
                logger.error(f"[CONTEXT] Cannot execute without valid wallet: {e}")
                return {'success': False, 'error': f'Wallet not loaded: {e}'}
            
            investment_amount_sol = None
            if config and hasattr(config, 'investment_amount_sol'):
                investment_amount_sol = config.investment_amount_sol
            else:
                logger.warning("[CONTEXT] Missing config or investment_amount_sol, using default 0.001 SOL")
                investment_amount_sol = 0.001
            
            # Check if this is the MEV Pump.fun executor that needs different parameter names
            if dex_name.lower() == "pump.fun" or "pumpfun" in dex_name.lower():
                buy_args = dict(
                    mint_str=token_mint,
                    sol_amount=investment_amount_sol,
                    wallet=wallet_keypair
                )
                if 'transaction_logs' in kwargs:
                    buy_args['transaction_logs'] = kwargs['transaction_logs']
                if 'trade_info' in kwargs:
                    buy_args['trade_info'] = kwargs['trade_info']
            elif dex_name.lower() == "mev_raydium" or "raydium" in dex_name.lower():
                buy_args = {
                    'token_mint': token_mint,
                    'source_wallet': source_wallet,
                    'amount_sol': investment_amount_sol,
                    'trade_info': kwargs.get('trade_info'),
                    'slippage': kwargs.get('slippage'),
                    'priority_fee': kwargs.get('priority_fee'),
                    'jito_service': self.jito_service
                }
            else:
                buy_args = dict(
                    wallet_keypair=wallet_keypair,
                    token_mint=token_mint,
                    amount_sol=investment_amount_sol
                )
                if 'trade_info' in kwargs:
                    buy_args['trade_info'] = kwargs['trade_info']
                for k, v in kwargs.items():
                    if k not in ['routing_instructions', 'detected_dex']:
                        if k not in buy_args:
                            buy_args[k] = v
            # Timeout and error handling
            try:
                logger.debug(f"   🚀 [EXECUTOR_BUY] Executing {dex_name.upper()} with args: {buy_args}")
                result = await asyncio.wait_for(buy_executor(**buy_args), timeout=10)
                logger.debug(f"   ✅ [EXECUTOR_BUY] {dex_name.upper()} result: {result}")
                return result
            except asyncio.TimeoutError:
                logger.error(f"   ⏰ [EXECUTOR_BUY] {dex_name.upper()} timeout after 10 seconds")
                logger.error(f"   Input params: dex_name={dex_name}, token_mint={token_mint}, source_wallet={source_wallet}")
                logger.error(f"   Buy args: {buy_args}")
                return {'success': False, 'error': 'timeout'}
            except Exception as e:
                logger.error(f"   ❌ [EXECUTOR_BUY] {dex_name.upper()} exception: {e}", exc_info=True)
                logger.error(f"   Input params: dex_name={dex_name}, token_mint={token_mint}, source_wallet={source_wallet}")
                logger.error(f"   Buy args: {buy_args}")
                logger.error(f"   Exception type: {type(e).__name__}")
                return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"❌ [EXECUTOR_BUY] Outer exception in _try_single_executor_buy: {e}", exc_info=True)
            logger.error(f"Input params: dex_name={dex_name}, buy_executor={buy_executor}, token_mint={token_mint}, source_wallet={source_wallet}, kwargs={kwargs}")
            return {'success': False, 'error': str(e)}

    async def _calculate_precise_sell_percentage(self, token_mint: str, trade_info: Dict[str, Any] = None, source_wallet: str = None) -> float:
        """Calculate sell percentage based on trade info"""
        # Default to 100% sell for MEV execution
        return 100.0

    # Removed deprecated _try_direct_pumpfun_buy method - use ROUTE_MAP routing via _execute_direct_copy_buy instead
    # Removed deprecated _try_direct_pumpfun_sell method - use ROUTE_MAP routing instead

    def _track_new_position(self, token_mint: str, amount_sol: float, dex_name: str):
        """Track new position or add to existing position"""
        if token_mint not in self.positions:
            self.positions[token_mint] = WalletPosition(
                token_mint=token_mint,
                initial_amount=amount_sol,
                current_amount=amount_sol,
                our_amount=amount_sol
            )
            logger.info(f"📊 NEW POSITION: {token_mint[:8]}... - {amount_sol:.6f} SOL via {dex_name}")
        else:
            # Add to existing position
            position = self.positions[token_mint]
            position.current_amount += amount_sol
            position.our_amount += amount_sol
            position.last_updated = datetime.now()
            logger.info(f"📊 ADDED TO POSITION: {token_mint[:8]}... - total: {position.current_amount:.6f} SOL")

    async def liquidate_all_positions(self):
        """Emergency liquidation of all positions"""
        try:
            if not self.positions:
                logger.info("💸 No positions to liquidate")
                return
            
            logger.info(f"💸 EMERGENCY LIQUIDATION: Selling all {len(self.positions)} positions")
            
            liquidation_results = []
            successful_sales = 0
            failed_sales = 0
            
            # Create a copy to avoid modification during iteration
            positions_to_sell = dict(self.positions)
            
            for token_mint, position in positions_to_sell.items():
                logger.info(f"💸 Liquidating: {token_mint[:8]}... ({position.current_amount:.6f} SOL)")
                
                try:
                    success = await self._execute_copy_sell(
                        token_mint, 
                        {"action": "sell"}, 
                        "emergency_liquidation"
                    )
                    
                    if success:
                        successful_sales += 1
                        logger.info(f"✅ Liquidated {token_mint[:8]}...")
                    else:
                        failed_sales += 1
                        logger.warning(f"⚠️ Failed to liquidate {token_mint[:8]}...")
                        
                except Exception as e:
                    failed_sales += 1
                    logger.error(f"❌ Error liquidating {token_mint[:8]}...: {e}")
            
            logger.info(f"💸 LIQUIDATION COMPLETE: {successful_sales} successful, {failed_sales} failed")
            return {'successful': successful_sales, 'failed': failed_sales}
            
        except Exception as e:
            logger.error(f"❌ Error in liquidate_all_positions: {e}")
            return {'successful': 0, 'failed': len(self.positions)}

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        try:
            total_executions = len(self.execution_history)
            successful_executions = sum(1 for exec in self.execution_history if exec['success'])
            failed_executions = total_executions - successful_executions
            # Calculate success rate
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            # Get DEX usage stats
            dex_stats = defaultdict(int)
            for exec in self.execution_history:
                dex = exec.get("dex")
                if dex:
                    dex_stats[dex] += 1
            return {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': success_rate,
                'dex_stats': dict(dex_stats)
            }
        except Exception as e:
            logger.error(f"❌ Error getting execution stats: {e}")
            return {}
