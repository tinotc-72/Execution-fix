#!/usr/bin/env python3
"""
Simple Copy Trading Bot - Essential functionality only
"""

import asyncio
import json
import logging
import signal
import sys
import traceback
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from solders.pubkey import Pubkey
from config import WALLET
from solana.rpc.async_api import AsyncClient

# Import utilities
from utils import get_transaction_with_logs, load_keypair

# Import specialized modules
from copy_trade_logger import get_copy_trade_logger

# Import execution coordinator for trading
from execution_coordinator import ExecutionCoordinator
from transaction_cloner import TransactionCloner

# Import trade processor for clean logic separation

from trade_processor import TradeProcessor
from wallet_tx_parser import WalletTransactionParser

# Import core services


try:
    from env_keys import EnvKeys
    ENV_KEYS_AVAILABLE = True
except ImportError:
    class EnvKeys:
        def __init__(self):
            self.HELIUS_RPC_URL = "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"
            self.HELIUS_WS_URL = "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"
    ENV_KEYS_AVAILABLE = False

# Import WebSocket handler
try:
    from websocket_handler import WebSocketHandler, create_websocket_handler
    WEBSOCKET_AVAILABLE = True
except ImportError:
    class WebSocketHandler:
        def __init__(self, *args, **kwargs):
            pass
        async def start_monitoring(self):
            pass
        async def stop(self):
            pass
    async def create_websocket_handler(*args, **kwargs):
        return WebSocketHandler()
    WEBSOCKET_AVAILABLE = False

from config import CopyTradeConfig
# Setup DEEP DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for deeper logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level

def validate_runtime_env(logger):
    """Validate required environment variables and fail fast with clear message if missing"""
    import os
    import sys
    
    missing = []
    
    # Check for RPC URL (either HELIUS_RPC_URL or RPC_URL)
    if not (os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")):
        missing.append("HELIUS_RPC_URL or RPC_URL")
    
    # Check for wallet private key (any of the three formats)
    if not (os.getenv("PRIVATE_KEY") or os.getenv("PHANTOM_PRIVATE_KEY") or os.getenv("WALLET_SECRET")):
        missing.append("PRIVATE_KEY or PHANTOM_PRIVATE_KEY or WALLET_SECRET")
    
    # Log status
    if missing:
        logger.error("")
        logger.error("=" * 60)
        logger.error("❌ STARTUP VALIDATION FAILED")
        logger.error("=" * 60)
        logger.error("Missing required environment variables:")
        for var in missing:
            logger.error(f"  • {var}")
        logger.error("")
        logger.error("Please set the required environment variables and restart.")
        logger.error("Jito configuration is optional but recommended for MEV protection.")
        logger.error("=" * 60)
        sys.exit(1)
    else:
        logger.info("✅ Runtime environment validation passed")
        # Check optional Jito configuration
        jito_configured = bool(os.getenv("JITO_AUTH_TOKEN") and os.getenv("JITO_BLOCK_ENGINE_URL"))
        if jito_configured:
            logger.info("✅ Jito MEV protection configured")
        else:
            logger.info("ℹ️  Jito MEV protection not configured (optional)")

def log_failed_trade_analysis(trade_info, failure_reason="unknown", retry_count=0, routing_data=None):
    """Log failed trade analysis for offline debugging and pattern analysis."""
    import json
    from datetime import datetime
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "failure_reason": failure_reason,
        "retry_count": retry_count,
        "trade_info": trade_info,
        "routing_data": routing_data,
        "signature": trade_info.get("signature", "unknown"),
        "wallet_address": trade_info.get("wallet_address", "unknown"),
        "dex_type": trade_info.get("dex_type", "unknown"),
        "program_id": trade_info.get("program_id", "unknown")
    }
    
    try:
        with open("failed_trade_analysis.log", "a") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")
        logger.debug(f"📝 Logged failed trade analysis: {failure_reason} - {trade_info.get('signature', 'unknown')[:12]}...")
    except Exception as e:
        logger.error(f"❌ Failed to log trade analysis: {e}")

# 🚀 JITO SERVICE IMPORT - Activate MEV protection
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
    logger.info("✅ Jito service available - MEV protection ready")
except ImportError:
    logger.warning("⚠️ Jito service not available - will use RPC fallback")
    JITO_AVAILABLE = False

# Global bot instance for signal handlers
bot_instance = None


from execution_coordinator import normalize_dex, ROUTE_MAP


class SimpleCopyTradingBot:
    async def _process_detected_trade(self, trade_info: Dict[str, Any]):
        """
        Canonical per-trade handler:
        - accepts trades with or without signatures (warns for account-change stubs)
        - derives source_wallet
        - runs analyze_and_route_trade(trade_info, source_wallet)
        - dispatches to coordinator for buy/sell
        """
        sig = (trade_info.get("signature") or "").strip()
        if not sig or sig == "unknown":
            self.logger.warning("[DETECT] No on-chain signature provided (account-change stub). Proceeding based on parsed DEX/mint/action.")
            # Optionally: try to resolve recent signature for this slot/wallet here.
        # Do NOT return/skip here — continue to analyze_and_route_trade

        # Prefer the wallet from the event; otherwise fall back to config/wallet
        source_wallet = (
            trade_info.get("wallet_address")
            or (self.target_wallets[0] if self.target_wallets else None)
            or str(self.wallet_pubkey)
        )

        logger.info("🔍 Running router detection for detected trade.")
        routing = await self._resilient_async_call(
            self.trade_processor.analyze_and_route_trade,
            trade_info,
            source_wallet,        # ← REQUIRED
        )
        if not routing:
            logger.error("❌ No routing instructions returned.")
            return

        action = routing.get("action", "unknown")
        enriched = routing.get("trade_info", trade_info)  # carries program IDs / router info
        token_mint = routing.get("token_mint") or enriched.get("token_mint")
        dex = normalize_dex(
            enriched.get("dex_type") or routing.get("dex") or "unknown"
        )

        # Log trade detection with key details
        amount = enriched.get("amount") or enriched.get("sol_amount") or "unknown"
        logger.info(f"🎯 TRADE DETECTED — Mint: {token_mint} | Action: {action} | DEX: {dex} | Amount: {amount} | Source: {source_wallet}")

                # === RETRY LOGIC FOR UNCERTAIN TRADES ===
        if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
            for retry in range(3):
                logger.warning(f"Uncertain action or token mint detected (attempt {retry+1}/3). Retrying analysis...")
                await asyncio.sleep(0.2)  # Fast retry for copy trading speed
                routing = await self._resilient_async_call(
                    self.trade_processor.analyze_and_route_trade,
                    trade_info,
                    source_wallet,
                )
                action = routing.get("action", "unknown")
                token_mint = routing.get("token_mint") or enriched.get("token_mint")
                if action != 'unknown' and token_mint not in ['UNKNOWN', 'PENDING_ANALYSIS']:
                    break
            if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.error(f"Uncertain action or token mint after retries: action={action}, token_mint={token_mint}")
                log_failed_trade_analysis(
                    trade_info, 
                    failure_reason=f"failed_after_retries_action_{action}_mint_{token_mint}",
                    retry_count=3,
                    routing_data=routing
                )
                return

        # === MINT/ACTION UNCERTAINTY DEBUGGING IN MAIN ===
        if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
            logger.error(f"Uncertain action or token mint detected in main: action={action}, token_mint={token_mint}, trade_info={enriched}")
            logger.error(f"   Original routing: {routing}")
            logger.error(f"   Signature: {enriched.get('signature', 'missing') if enriched else 'no_enriched_data'}")
            logger.error(f"   Source wallet: {source_wallet}")
            log_failed_trade_analysis(
                enriched or trade_info, 
                failure_reason=f"uncertain_after_successful_retries_action_{action}_mint_{token_mint}",
                retry_count=0,
                routing_data=routing
            )

        # === TOKEN BALANCE CHANGE REQUIREMENT FOR ALL MONITORED WALLETS ===
        # Check EVERY monitored wallet for token balance changes
        meta = enriched.get('meta') or trade_info.get('meta')
        if meta:
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            # Build mapping from (owner, mint) -> amount for efficient lookup
            pre_map = {}
            post_map = {}
            
            for balance in pre_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    pre_map[(owner, mint)] = amount
                    
            for balance in post_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    post_map[(owner, mint)] = amount
            
            # Check ALL monitored wallets for balance changes
            detected_trades = []
            for wallet in self.target_wallets:  # Loop through ALL monitored wallets
                logger.debug(f"🔍 Checking wallet {wallet[:8]}... for balance changes")
                
                # Get all (wallet, mint) pairs for this wallet
                wallet_keys = set()
                for (owner, mint) in pre_map.keys():
                    if owner == wallet:
                        wallet_keys.add((owner, mint))
                for (owner, mint) in post_map.keys():
                    if owner == wallet:
                        wallet_keys.add((owner, mint))
                
                # Check for balance changes for this wallet
                for (owner, mint) in wallet_keys:
                    pre_amt = pre_map.get((owner, mint), 0)
                    post_amt = post_map.get((owner, mint), 0)
                    delta = post_amt - pre_amt
                    
                    if delta != 0:
                        # Found a balance change for this wallet!
                        detected_action = "buy" if delta > 0 else "sell"
                        logger.info(f"🎯 {detected_action.upper()} detected for wallet {wallet[:8]}... on token {mint[:8] if mint else 'N/A'}...: {pre_amt} → {post_amt} (Δ{delta:+,})")
                        
                        detected_trades.append({
                            'wallet': wallet,
                            'mint': mint,
                            'action': detected_action,
                            'pre_amount': pre_amt,
                            'post_amount': post_amt,
                            'delta': delta
                        })
            
            if not detected_trades:
                logger.info(f"🚫 No token balance changes detected for monitored wallets")
                logger.info(f"   Checked wallets: {[w[:8] + '...' for w in self.target_wallets]}")
                
                # === ENHANCED FALLBACK LOGIC (UPDATED BLOCK) ===
                logger.info("🔄 FALLBACK TRIGGER: No balance changes detected - initiating signer+instruction analysis")
                
                # Use trade_processor helper methods for cleaner logic
                signer_info = self.trade_processor._check_monitored_wallet_is_signer(enriched)
                instruction_info = self.trade_processor._check_trade_instructions(enriched)

                is_monitored_signer = signer_info.get("has_monitored_involvement", False)
                found_trade_instruction = instruction_info.get("has_trade_instructions", False)

                # Debug logging for fallback condition evaluation
                logger.info(f"🔍 [FALLBACK DEBUG] Condition Analysis:")
                logger.info(f"   ✍️  Is monitored signer: {is_monitored_signer}")
                if is_monitored_signer:
                    logger.info(f"      Fee payer: {signer_info.get('fee_payer', 'Unknown')}")
                    logger.info(f"      Monitored wallets: {signer_info.get('monitored_wallets', [])}")
                logger.info(f"   🔄 Found trade instruction: {found_trade_instruction}")
                if found_trade_instruction:
                    trade_programs = instruction_info.get('trade_programs', [])
                    logger.info(f"      Trade programs: {trade_programs}")
                    logger.info(f"      Total instructions: {instruction_info.get('total_instructions', 0)}")

                if is_monitored_signer or found_trade_instruction:
                    # Log which specific condition(s) triggered execution
                    triggered_conditions = []
                    if is_monitored_signer:
                        triggered_conditions.append("MONITORED_SIGNER")
                        logger.info(f"✅ [FALLBACK TRIGGER] Condition 1: Monitored wallet is signer/fee payer")
                    if found_trade_instruction:
                        triggered_conditions.append("TRADE_INSTRUCTIONS")
                        logger.info(f"✅ [FALLBACK TRIGGER] Condition 2: Trade instruction found")
                    
                    logger.info(f"🎯 [FALLBACK SUCCESS] EXECUTION APPROVED via conditions: {', '.join(triggered_conditions)}")
                    logger.info(f"   Action: {action}")
                    logger.info(f"   Token: {str(token_mint)[:8]}...")
                    logger.info(f"   Source wallet: {str(source_wallet)[:8]}...")
                    
                    # trigger copy trade
                    if action in ("buy", "swap_in"):
                        logger.info(f"🚀 [FALLBACK EXECUTION] Executing copy BUY for {str(token_mint)[:8]}...")
                        await self.execution_coordinator._execute_copy_buy(token_mint=token_mint, source_wallet=source_wallet, trade_info=enriched)
                    elif action in ("sell", "swap_out"):
                        logger.info(f"🚀 [FALLBACK EXECUTION] Executing copy SELL for {str(token_mint)[:8]}...")
                        await self.execution_coordinator._execute_copy_sell(token_mint=token_mint, source_wallet=source_wallet, trade_info=enriched)
                    return
                else:
                    logger.warning("❌ [FALLBACK FAILED] ALL CONDITIONS NOT MET - Skipping execution")
                    logger.warning(f"   Monitored signer: {is_monitored_signer}")
                    logger.warning(f"   Trade instruction: {found_trade_instruction}")
                    logger.warning(f"   Both conditions required in OR logic, neither met")
                    # log analytics
                    log_failed_trade_analysis(
                        enriched or trade_info,
                        failure_reason="fallback_conditions_not_met",
                        retry_count=0,
                        routing_data={
                            "routing": routing,
                            "signer_info": signer_info,
                            "instruction_info": instruction_info,
                            "is_monitored_signer": is_monitored_signer,
                            "found_trade_instruction": found_trade_instruction,
                            "monitored_wallets": self.target_wallets
                        }
                    )
                    return
            
            # Execute trades for each detected wallet/token combination
            logger.info(f"✅ Found {len(detected_trades)} balance change(s) across monitored wallets - executing copy trades")
            
            # Debug log the primary execution path
            if getattr(self.config, 'execution_debug', False):
                logger.debug("📊 PRIMARY EXECUTION PATH: Balance changes detected in monitored wallets")
                for trade in detected_trades:
                    logger.debug(f"  - Wallet: {trade['wallet'][:8]}... | Token: {trade['mint'][:8]}... | Action: {trade['action']}")
                    logger.debug(f"    ✅ EXECUTION CONDITION: Monitored wallet balance change detection (PRIMARY PATH)")
            
            execution_results = []
            for trade in detected_trades:
                wallet = trade['wallet']
                mint = trade['mint']
                detected_action = trade['action']
                
                logger.info(f"🚀 Executing copy trade for wallet {wallet[:8]}... token {mint[:8]}... action: {detected_action}")
                
                if getattr(self.config, 'execution_debug', False):
                    logger.debug(f"🔥 EXECUTION TRIGGER: Primary balance change detection for {wallet[:8]}.../{mint[:8]}... - {detected_action}")
                
                # Use the detected action and wallet for this specific trade
                if detected_action in ("buy", "swap_in"):
                    exec_res = await self._resilient_async_call(
                        self.execution_coordinator._execute_copy_buy,
                        token_mint=mint,
                        source_wallet=wallet,  # Use the specific wallet that had the balance change
                        trade_info=enriched,
                    )
                elif detected_action in ("sell", "swap_out"):
                    if getattr(self.config, 'execution_debug', False):
                        logger.debug(f"🔥 EXECUTION TRIGGER: Primary balance change detection for SELL {wallet[:8]}.../{mint[:8]}...")
                    
                    exec_res = await self._resilient_async_call(
                        self.execution_coordinator._execute_copy_sell,
                        token_mint=mint,
                        source_wallet=wallet,  # Use the specific wallet that had the balance change
                        trade_info=enriched,
                    )
                else:
                    logger.warning(f"⚠️ Unknown action '{detected_action}' for wallet {wallet[:8]}... - skipping execution")
                    continue
                
                execution_results.append({
                    'wallet': wallet,
                    'mint': mint,
                    'action': detected_action,
                    'result': exec_res
                })
            
            logger.info(f"🎯 Completed {len(execution_results)} copy trade executions")
            return  # Exit here since we handled all detected trades
        else:
            logger.warning(f"⚠️ No metadata available to verify token balance changes - proceeding with execution")

        if action in ("buy", "swap_in"):
            exec_res = await self._resilient_async_call(
                self.execution_coordinator._execute_copy_buy,
                token_mint=token_mint,
                source_wallet=source_wallet,
                trade_info=enriched,
            )
        elif action in ("sell", "swap_out"):
            exec_res = await self._resilient_async_call(
                self.execution_coordinator._execute_copy_sell,
                token_mint=token_mint,
                source_wallet=source_wallet,
                trade_info=enriched,
                detected_dex=dex,
            )
        else:
            logger.warning(f"⚠️ Unknown action '{action}' — skipping execution.")
            log_failed_trade_analysis(
                enriched or trade_info,
                failure_reason=f"unknown_action_{action}_skipped_execution",
                retry_count=0,
                routing_data=routing
            )
            return

        if isinstance(exec_res, dict) and exec_res.get("success"):
            logger.info(f"✅ Execution sent | Signature: {exec_res.get('signature')}")
        else:
            logger.error(f"❌ Execution failed: {exec_res}")
            log_failed_trade_analysis(
                enriched or trade_info,
                failure_reason=f"execution_failed_{action}_result_{type(exec_res).__name__}",
                retry_count=0,
                routing_data={
                    "routing": routing,
                    "execution_result": exec_res,
                    "action": action,
                    "token_mint": token_mint,
                    "dex": dex
                }
            )
    async def _resilient_async_call(self, func, *args, max_retries=5, initial_delay=0.5, backoff=2, **kwargs):
        """
        Robust async call with exponential backoff and error logging.
        """
        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[RESILIENT] Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    logger.error(f"[RESILIENT] Max retries reached for {func.__name__}")
                    raise
                await asyncio.sleep(delay)
                delay *= backoff

    async def execute_trade_with_fallback(self, trade_type, token_mint, amount=None, detected_dex=None, trade_info=None):
        if normalize_dex(detected_dex) != "direct_copy":
            return {"success": False, "error": "Universal cloner disabled for non-direct_copy"}
        try:
            if not trade_info or not trade_info.get('signature'):
                logger.error("[UNIVERSAL CLONER] No signature in trade_info, cannot clone.")
                return {"success": False, "error": "No signature in trade_info"}
            signature = trade_info['signature']
            logger.info(f"[UNIVERSAL CLONER] Executing {trade_type.upper()} for {token_mint[:8]}... (sig: {signature[:8]}...)")
            override_accounts = {"payer": str(self.wallet.public_key)}
            tx = await self._resilient_async_call(self.transaction_cloner.clone_transaction, signature, override_accounts=override_accounts)
            if tx:
                tx_sig = await self._resilient_async_call(self.transaction_cloner.send_cloned_transaction, tx)
                if tx_sig:
                    logger.info(f"[UNIVERSAL CLONER] Trade sent | Signature: {tx_sig}")
                    return {"success": True, "signature": tx_sig}
                else:
                    logger.error(f"[UNIVERSAL CLONER] Failed to send cloned transaction for {signature}")
                    return {"success": False, "error": "Failed to send cloned transaction"}
            else:
                logger.error(f"[UNIVERSAL CLONER] Failed to clone transaction for {signature}")
                return {"success": False, "error": "Failed to clone transaction"}
        except Exception as e:
            logger.error(f"[UNIVERSAL CLONER] Exception: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    # --- TEST HARNESS STUBS FOR INTEGRATION TESTS ---
    async def send_transaction_jito_first(self, *args, **kwargs):
        """Stub for Jito-first transaction sending."""
        logger.warning("send_transaction_jito_first is a stub (not implemented)")
        return False

    async def _build_optimal_transaction(self, *args, **kwargs):
        """Stub for optimal transaction building."""
        logger.warning("_build_optimal_transaction is a stub (not implemented)")
        return None


    async def _try_jito_first_execution(self, token_mint, source_wallet, *args, **kwargs):
        """Stub for Jito-first execution with correct signature."""
        logger.warning("_try_jito_first_execution is a stub (not implemented)")
        return False

    async def _try_direct_rpc_execution(self, transaction_instructions, *args, **kwargs):
        """Stub for direct RPC execution with correct signature."""
        logger.warning("_try_direct_rpc_execution is a stub (not implemented)")
        return False

    # Wallet sign method wrapper for test compatibility
    def sign(self, *args, **kwargs):
        if hasattr(self.wallet, 'sign'):
            return self.wallet.sign(*args, **kwargs)
        logger.warning("Wallet sign method not implemented.")
        return None

    # --- END TEST HARNESS STUBS ---
    """Simple copy trading bot - just the essentials"""
    
    def __init__(self, config: CopyTradeConfig):
        self.config = config
        self.is_running = False
        
        # Validate runtime environment before any initialization
        validate_runtime_env(logger)

        # Core components
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        # --- Enhanced error logging for RPC and Jito ---
        # Initialize proper Solana RPC client for transaction analysis
        try:
            import aiohttp
            self.rpc_client = AsyncClient(self.config.rpc_url)
            logger.info(f"✅ RPC client initialized with endpoint: {self.config.rpc_url}")
        except Exception as rpc_init_error:
            logger.error(f"❌ Failed to initialize RPC client: {rpc_init_error}")
            import traceback
            logger.error(traceback.format_exc())
            raise

        # 🚀 INITIALIZE JITO SERVICE for MEV protection
        self.jito_service = None
        if self.config.use_jito and JITO_AVAILABLE:
            try:
                logger.info("🚀 Initializing Jito service for MEV protection...")
                self.jito_service = JitoClient()
                logger.info("✅ Jito service initialized - transactions will use MEV protection")
            except Exception as jito_init_error:
                logger.error(f"❌ Failed to initialize Jito service: {jito_init_error}")
                import traceback
                logger.error(traceback.format_exc())
                self.jito_service = None
        elif self.config.use_jito and not JITO_AVAILABLE:
            logger.warning("⚠️ Jito requested but not available - using RPC fallback")
        else:
            logger.info("ℹ️ Jito disabled in config - using RPC only")

        # Simple state tracking
        self.target_wallets = self.config.target_wallets
        self.processed_signatures: Set[str] = set()

        # Initialize trade processor
        self.trade_processor = TradeProcessor(self.target_wallets, self.rpc_client)
        # Initialize wallet transaction parser for robust DEX/ALT decoding
        self.tx_parser = WalletTransactionParser(self.rpc_client)
        # Universal transaction cloner
        self.transaction_cloner = TransactionCloner(self.config.rpc_url, self.wallet)
        # WebSocket handler
        self.ws_handler = None
        # Simple logging
        self.csv_logger = get_copy_trade_logger("simple_copy_logs")
        logger.info(f"✅ Simple Copy Trading Bot initialized (UNIVERSAL CLONER MODE)")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🚀 Jito MEV protection: {'✅ ENABLED' if self.jito_service else '❌ DISABLED'}")
        # --- FIX: Initialize execution coordinator for real buy/sell logic ---
        self.execution_coordinator = ExecutionCoordinator(self.wallet, rpc_client=self.rpc_client, jito_service=self.jito_service, config=self.config)

    def reload_config(self, new_config: CopyTradeConfig):
        """Reload configuration at runtime and update all components."""
        logger.info("🔄 Reloading bot configuration at runtime...")
        self.config = new_config
        # Update all components that use config
        self.target_wallets = self.config.target_wallets
        self.trade_processor = TradeProcessor(self.target_wallets, self.rpc_client)
        self.transaction_cloner = TransactionCloner(self.config.rpc_url, self.wallet)
        self.execution_coordinator = ExecutionCoordinator(self.wallet, rpc_client=self.rpc_client, jito_service=self.jito_service, config=self.config)
        logger.info(f"✅ Config reloaded. New investment amount: {self.config.investment_amount_sol} SOL")

    async def _handle_websocket_trade(self, trade_info: Dict[str, Any]):
        # Step 3: Parse and decode transaction using wallet_tx_parser
        try:
            if 'transaction' in trade_info:
                # Parse and decode transaction before analysis/execution
                parsed_tx = self.tx_parser.parse_transaction(trade_info['transaction'])
                trade_info['parsed_tx'] = parsed_tx
        except Exception as e:
            logger.error(f"[TX PARSER] Error parsing transaction: {e}")
            logger.error(traceback.format_exc())
        logger.debug(f"[DEBUG] Received trade_info: {json.dumps(trade_info, default=str)}")
        """🚀 ENHANCED: Handle trades with MAXIMUM SPEED - Copy ALL transactions immediately"""
        try:
            logger.info(f"🚨 ⚡ SPEED TRADE DETECTION: {trade_info}")

            # === ENHANCED UPSTREAM DATA FIX: Ensure required fields are present with debug logging ===
            missing_fields = []
            
            # Check and fix signature
            sig = (trade_info.get("signature") or "").strip()
            if not sig or sig == "unknown":
                missing_fields.append("signature")
                logger.warning("ℹ️ [FIELD_DEBUG] No signature in trade_info; proceeding with parsed trade data.")
                # Continue processing instead of returning
            
            # Check and fix wallet_address
            if not trade_info.get('wallet_address'):
                missing_fields.append("wallet_address")
                logger.warning("[FIELD_DEBUG] Missing 'wallet_address' in trade_info, setting to first target wallet.")
                trade_info['wallet_address'] = self.target_wallets[0] if self.target_wallets else 'unknown'
            
            # Check and default DEX type
            if not trade_info.get('dex') and not trade_info.get('dex_type'):
                missing_fields.append("dex/dex_type")
                logger.debug("[FIELD_DEBUG] Missing 'dex' field - will be inferred during analysis")
                trade_info['dex'] = 'unknown'
            
            # Check and default action
            if not trade_info.get('action'):
                missing_fields.append("action")
                logger.debug("[FIELD_DEBUG] Missing 'action' field - will be inferred during analysis")
                trade_info['action'] = 'unknown'
            
            # Check and default mint
            if not trade_info.get('mint') and not trade_info.get('token_mint'):
                missing_fields.append("mint/token_mint")
                logger.debug("[FIELD_DEBUG] Missing 'mint'/'token_mint' field - will be extracted during analysis")
                trade_info['token_mint'] = 'PENDING_ANALYSIS'
            
            # Log summary of missing fields for debugging
            if missing_fields:
                logger.info(f"📋 [FIELD_DEBUG] Missing/defaulted fields: {', '.join(missing_fields)}")
                logger.debug(f"[FIELD_DEBUG] Full trade_info keys: {list(trade_info.keys())}")
            
            logger.debug(f"[DEBUG] After upstream fix: {json.dumps(trade_info, default=str)}")

            # 🚀 SPEED OPTIMIZATION: Skip lengthy analysis if basic analysis suggests immediate copy
            if trade_info.get('basic_analysis', {}).get('copy_immediately'):
                logger.debug(f"[DEBUG] basic_analysis: {json.dumps(trade_info.get('basic_analysis', {}), default=str)}")
                logger.info("⚡ IMMEDIATE COPY - Basic analysis suggests high-confidence trade")
                self.wallet = WALLET  # User's wallet is always included
                # Extract basic info and execute immediately
                likely_action = trade_info['basic_analysis'].get('likely_action', 'buy')
                detected_dex = trade_info['basic_analysis'].get('detected_dex', 'unknown')

                # Create fast trade info
                fast_trade_info = {
                    'action': likely_action,
                    'signature': trade_info['signature'],
                    'wallet_address': trade_info['wallet_address'],
                    'dex': detected_dex,
                    'token_mint': 'PENDING_ANALYSIS',  # Will be extracted during execution
                    'timestamp': datetime.now(timezone.utc),
                    'extraction_method': 'speed_copy',
                    'confidence': 10,
                    'speed_mode': True
                }

                # 🚀 PARALLEL PROCESSING: Start execution while doing analysis
                if likely_action in ['buy', 'unknown']:
                    # For buys or unknown, start execution immediately and extract token mint in parallel
                    signature = fast_trade_info['signature']
                    wallet_address = fast_trade_info['wallet_address']

                    if signature and wallet_address:
                        # Start parallel tasks: analysis + execution
                        analysis_task = asyncio.create_task(
                            self._fast_token_extraction(signature, wallet_address),
                            name="fast_analysis"
                        )

                        # Wait for token extraction (fast)
                        try:
                            token_result = await asyncio.wait_for(analysis_task, timeout=3.0)
                            logger.debug(f"[DEBUG] Fast token extraction result: {token_result}")
                            if token_result:
                                fast_trade_info['token_mint'] = token_result.get('token_mint', 'UNKNOWN')
                                await self._process_detected_trade(fast_trade_info)
                                return
                        except asyncio.TimeoutError:
                            logger.warning("⏰ Fast analysis timeout - proceeding with full analysis")
                        except Exception as e:
                            logger.error(f"[DEBUG] Exception in fast token extraction: {e}")
                
                elif likely_action in ['sell', 'swap_out']:
                    # For sells, extract token mint first, then process
                    logger.info(f"⚡ IMMEDIATE SELL PROCESSING - Extracting token mint")
                    signature = fast_trade_info['signature']
                    wallet_address = fast_trade_info['wallet_address']
                    
                    if signature and wallet_address:
                        try:
                            # Extract token mint for sell transaction
                            extracted_info = await self._fast_token_extraction(signature, wallet_address)
                            if extracted_info and extracted_info.get('token_mint'):
                                fast_trade_info['token_mint'] = extracted_info['token_mint']
                                logger.info(f"✅ SELL TOKEN EXTRACTED: {extracted_info['token_mint'][:8]}...")
                                await self._process_detected_trade(fast_trade_info)
                                return
                            else:
                                logger.error(f"❌ Failed to extract token mint from sell transaction")
                        except Exception as e:
                            logger.error(f"[DEBUG] Exception in sell token extraction: {e}")
                    
                    logger.warning(f"⚠️ Sell token extraction failed - falling back to full analysis")
                else:
                    logger.warning(f"⚠️ Unknown action '{likely_action}' - proceeding with full analysis")

            # 🚀 FALLBACK: Full analysis if immediate copy not possible
            if trade_info.get('requires_analysis'):
                logger.debug(f"[DEBUG] requires_analysis: {trade_info.get('requires_analysis')}")
                signature = trade_info['signature']
                wallet_address = trade_info['wallet_address']
                logger.debug(f"[DEBUG] Starting simple_trade_analysis for signature={signature}, wallet_address={wallet_address}")
                if signature and wallet_address:
                    # Use fast analysis with timeout
                    try:
                        result = await asyncio.wait_for(
                            self._simple_trade_analysis(signature, wallet_address, trade_info),
                            timeout=5.0  # 5 second max analysis time
                        )
                        logger.debug(f"[DEBUG] simple_trade_analysis result: {result}")
                        if result:
                            trade_info.update(result)
                        else:
                            logger.warning(f"⚠️ Fast analysis failed for {signature[:8]}... - skipping")
                            return
                    except Exception as e:
                        logger.error(f"[DEBUG] Exception in simple_trade_analysis: {e}")
                        return

            # Validate and process
            logger.debug(f"[DEBUG] Before validate_trade_info: {json.dumps(trade_info, default=str)}")
            is_valid = self.trade_processor.validate_trade_info(trade_info)
            logger.debug(f"[DEBUG] validate_trade_info result: {is_valid}")
            if is_valid:
                await self._process_detected_trade(trade_info)
            else:
                logger.warning(f"⚠️ Trade validation failed - skipping")

        except asyncio.TimeoutError:
            logger.warning("⏰ Trade handling timeout - processing anyway")
            logger.debug(f"[DEBUG] Timeout trade_info: {json.dumps(trade_info, default=str)}")
            # Process with available info
            is_valid = self.trade_processor.validate_trade_info(trade_info)
            logger.debug(f"[DEBUG] validate_trade_info (timeout) result: {is_valid}")
            if is_valid:
                await self._process_detected_trade(trade_info)
        except Exception as e:
            logger.error(f"❌ Error handling WebSocket trade: {e}")
            logger.error(f"[DEBUG] Exception details: {traceback.format_exc()}")

    async def _simple_trade_analysis(self, signature: str, wallet_address: str, trade_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Simple trade analysis - delegates to TradeProcessor with transaction data if available"""
        return await self.trade_processor.analyze_trade_simple(signature, wallet_address, trade_info)


    async def _execute_single_wallet_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict:
        """Execute trade for a specific wallet - now uses clean analysis then execution"""
        try:
            # Get routing instructions
            routing_instructions = await self.trade_processor.analyze_and_route_trade(trade_info, source_wallet)
            
            # === MINT/ACTION UNCERTAINTY DEBUGGING IN EXECUTION ===
            action = routing_instructions.get('action', 'unknown')
            token_mint = routing_instructions.get('token_mint', 'UNKNOWN')
            
            if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.error(f"Uncertain action or token mint detected in execution: action={action}, token_mint={token_mint}, trade_info={trade_info}")
                logger.error(f"   Routing instructions: {routing_instructions}")
                logger.error(f"   Requires execution: {routing_instructions.get('requires_execution', False)}")
            
            if routing_instructions.get('requires_execution'):
                # Use execution coordinator for actual execution
                action = routing_instructions['action']
                token_mint = routing_instructions['token_mint']
                
                if action in ['buy', 'swap_in']:
                    # Extract trade_info from routing instructions (contains program IDs)
                    original_trade_info = routing_instructions.get('trade_info', trade_info)
                    exec_res = await self._resilient_async_call(
                        self.execution_coordinator._execute_copy_buy,
                        token_mint=token_mint,
                        source_wallet=source_wallet,
                        trade_info=original_trade_info  # CRITICAL: Pass trade_info with program IDs
                    )
                elif action in ['sell', 'swap_out']:
                    strategy = routing_instructions.get('execution_strategy')
                    # Extract trade_info from routing instructions (contains program IDs)
                    original_trade_info = routing_instructions.get('trade_info', trade_info)
                    # Ensure detected_dex is set
                    detected_dex = routing_instructions.get('dex', 'unknown')
                    exec_res = await self._resilient_async_call(
                        self.execution_coordinator._execute_copy_sell,
                        token_mint=token_mint,
                        source_wallet=source_wallet,
                        trade_info=original_trade_info,  # CRITICAL: Pass trade_info with program IDs
                        detected_dex=detected_dex
                    )
                else:
                    exec_res = None
                
                return {
                    'success': bool(exec_res and exec_res.get('success')),
                    'exec_result': exec_res,
                    'action': action,
                    'token_mint': token_mint,
                    'routing_instructions': routing_instructions
                }
            else:
                return {
                    'success': False,
                    'error': 'Analysis failed',
                    'routing_instructions': routing_instructions
                }
                
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return {'success': False, 'error': str(e)}

    async def _fast_token_extraction(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Fast token extraction - delegates to TradeProcessor"""
        return await self.trade_processor.extract_token_info_fast(signature, wallet_address)

    async def start_monitoring(self):
        """Start simple WebSocket monitoring"""
        try:
            logger.info("🚀 Starting simple copy trading bot...")
            self.is_running = True
            
            # 🚀 INITIALIZE JITO SERVICE CONNECTIONS
            if self.jito_service:
                logger.info("🔄 Initializing Jito service connections...")
                jito_initialized = await self.jito_service.initialize()
                if jito_initialized:
                    logger.info("✅ Jito service initialized successfully - MEV protection ACTIVE")
                else:
                    logger.warning("⚠️ Jito initialization failed - falling back to RPC")
                    self.jito_service = None
                    # Update execution coordinator
                    self.execution_coordinator.jito_service = None
            
            # Initialize WebSocket handler
            logger.info("📡 Initializing WebSocket monitoring...")
            self.ws_handler = await create_websocket_handler(
                target_wallets=self.target_wallets,
                helius_ws_url=self.env_keys.HELIUS_WS_URL,
                helius_rpc_url=self.env_keys.HELIUS_RPC_URL,
                trade_callback=self._handle_websocket_trade
            )
            
            # Start monitoring
            logger.info("✅ Starting WebSocket connection...")
            websocket_task = asyncio.create_task(
                self.ws_handler.start_monitoring(),
                name="websocket_monitor"
            )
            
            # Simple status loop
            status_task = asyncio.create_task(
                self._simple_status_loop(),
                name="status_monitor"
            )
            
            logger.info("✅ Simple copy trading bot ready!")
            
            # Wait for tasks
            await asyncio.gather(websocket_task, status_task, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"❌ Error starting monitoring: {e}")
            await self.stop()

    async def _simple_status_loop(self):
        """Status monitoring with health checks"""
        try:
            while self.is_running:
                try:
                    # Show status every 5 minutes
                    await asyncio.sleep(300)
                    stats = self.execution_coordinator.get_execution_stats()
                    logger.info(f"📊 Status: {stats.get('total_executions', 0)} trades, "
                                f"{stats.get('success_rate', 0):.1f}% success rate")
                    # Health check
                    health = await self._health_check()
                    if not all(health.values()):
                        logger.warning(f"[HEALTH] Unhealthy system detected: {health}")
                except Exception as e:
                    logger.error(f"❌ Status loop error: {e}")
                    await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"❌ Status loop failed: {e}")

    async def _health_check(self) -> Dict[str, bool]:
        """
        Perform health checks on critical system components
        Returns a dictionary with health status of each component
        """
        health_status = {}
        
        try:
            # Check RPC client connectivity
            try:
                if self.rpc_client:
                    # Try a simple RPC call to check connectivity
                    response = await asyncio.wait_for(
                        self.rpc_client.get_health(),
                        timeout=5.0
                    )
                    health_status['rpc_client'] = True
                else:
                    health_status['rpc_client'] = False
            except Exception as e:
                logger.debug(f"RPC health check failed: {e}")
                health_status['rpc_client'] = False
            
            # Check Jito service if configured
            if self.jito_service:
                try:
                    # Simple check if Jito service is initialized
                    health_status['jito_service'] = hasattr(self.jito_service, 'client')
                except Exception as e:
                    logger.debug(f"Jito health check failed: {e}")
                    health_status['jito_service'] = False
            else:
                health_status['jito_service'] = True  # Not required, so mark as healthy
            
            # Check WebSocket handler
            try:
                if self.ws_handler:
                    health_status['websocket'] = hasattr(self.ws_handler, 'is_connected')
                else:
                    health_status['websocket'] = False
            except Exception as e:
                logger.debug(f"WebSocket health check failed: {e}")
                health_status['websocket'] = False
            
            # Check execution coordinator
            try:
                if self.execution_coordinator:
                    health_status['execution_coordinator'] = True
                else:
                    health_status['execution_coordinator'] = False
            except Exception as e:
                logger.debug(f"Execution coordinator health check failed: {e}")
                health_status['execution_coordinator'] = False
            
            # Check trade processor
            try:
                if self.trade_processor:
                    health_status['trade_processor'] = True
                else:
                    health_status['trade_processor'] = False
            except Exception as e:
                logger.debug(f"Trade processor health check failed: {e}")
                health_status['trade_processor'] = False
                
        except Exception as e:
            logger.error(f"❌ Health check failed with exception: {e}")
            health_status['overall'] = False
        
        return health_status

    async def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping simple copy trading bot...")
        self.is_running = False
        
        try:
            if self.ws_handler:
                await self.ws_handler.stop()
        except Exception as e:
            logger.error(f"Error stopping WebSocket: {e}")
        
        # 🚀 CLEANUP JITO SERVICE
        try:
            if self.jito_service:
                logger.info("🔄 Closing Jito service connections...")
                await self.jito_service.close()
                logger.info("✅ Jito service closed properly")
        except Exception as e:
            logger.error(f"Error closing Jito service: {e}")
        
        logger.info("✅ Bot stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum}. Shutting down...")
    if bot_instance:
        asyncio.create_task(bot_instance.stop())

async def main():
    """Main entry point"""
    global bot_instance
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configuration - TESTING PARAMETERS
    from config import MONITORED_WALLETS
    # MONITORED_WALLETS now includes the 4th wallet: 9ePNTG4j5eDGTFtUr6axt7h747HHzJPfmFh6JHAwFZsd
    config = CopyTradeConfig(
        target_wallets=MONITORED_WALLETS,
        investment_amount_sol=0.001,       # 🧪 TESTING: Meets MEV executor minimum (0.001 SOL)
        use_jito=False,                    # 🧪 TESTING: Simpler execution without Jito initially
        slippage_tolerance=0.3             # 🧪 TESTING: 30% slippage - reasonable for meme coins
    )
    
    # ...existing code...
    
    # Create and start bot
    bot_instance = SimpleCopyTradingBot(config)
    
    try:
        await bot_instance.start_monitoring()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        logger.error(traceback.format_exc())
    finally:
        await bot_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())
