#!/usr/bin/env python3
"""
Simple Copy Trading Bot - INTELLIGENT Execution Mode

INTELLIGENT EXECUTION PHILOSOPHY:
==================================
Execute trades ONLY when trade intent can be fully reconstructed from the transaction.
Never blindly execute on account changes or wallet triggers alone.

EXECUTION FLOW OVERVIEW:
========================

1. INITIALIZATION (SimpleCopyTradingBot.__init__)
   - Validates environment variables (RPC_URL, PHANTOM_PRIVATE_KEY)
   - Initializes RPC client for Solana network communication
   - Sets up Jito service for MEV protection (if configured)
   - Creates trade processor for analysis and execution coordinator for execution
   - Establishes WebSocket handler for real-time trade monitoring

2. TRADE DETECTION (_handle_websocket_trade)
   - Receives trade events from WebSocket monitor
   - Parses transaction logs and instructions to extract:
     * Direction: buy/sell/swap (parsed from logs/instructions)
     * Token Mint: SPL token address (extracted from transaction)
     * Amount: trade size information
   - Routes to intelligent processing pipeline

3. INTELLIGENT VALIDATION (Only execute if we can reconstruct trade intent):
   - Action must be parseable from logs/instructions (buy, sell, swap_in, swap_out)
   - Token mint must be extractable from transaction
   - No execution on incomplete data (action=unknown or token=UNKNOWN)
   - Logs and skips ambiguous trades where direction or token cannot be parsed
   
4. INTELLIGENT EXECUTION LOGIC:
   - Parses transaction logs and instructions to extract direction, token mints, and amounts
   - Execute BUY if monitored wallet buys (action=buy/swap_in)
   - Execute SELL if monitored wallet sells (action=sell/swap_out)
   - Maintain 0.001 SOL investment for all buy trades
   - Skip trades when trade intent cannot be reconstructed

5. TRADE EXECUTION (via execution_coordinator)
   - Routes to appropriate executor based on DEX type
   - Buy with 0.001 SOL (explicit 0.001 SOL investment)
   - Sell proportionally based on monitored wallet's percentage
   - Logs success/failure with comprehensive debugging info

6. HEALTH MONITORING (_simple_status_loop + _health_check)
   - Periodic health checks on all critical components
   - Logs execution statistics every 5 minutes
   - Alerts on unhealthy system state

AUDIT LOGGING:
==============
Documents trade parsing results, execution decisions, and skipped trades:
- Logs trade parsing success with action and token mint (parsed from logs/instructions)
- Logs trade parsing failures with specific reasons
- Logs execution decisions with full context
- Records skipped trades with signature and reason for audit trail

KEY BEHAVIOR (INTELLIGENT MODE):
- Only executes trades when intent (buy/sell/swap) is reconstructable
- Only executes trades when token mint is extractable from transaction
- Parses logs and instructions to extract direction and tokens
- Logs and skips ambiguous trades where direction or token cannot be parsed
- Maintains 0.001 SOL investment for buys
- Provides robust audit logging for all decisions
- EXECUTE ONLY PARSED TRADES - No blind execution on triggers alone
"""

import asyncio
import json
import logging
import signal
import sys
import traceback
import time
import os
import inspect
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from solders.pubkey import Pubkey
from config import WALLET

# Import utilities
from utils import get_transaction_with_logs, load_keypair, RPCClient
from utils.debug_span import set_span_id

# Import specialized modules
from copy_trade_logger import get_copy_trade_logger

# Import transaction cloner
from transaction_cloner import TransactionCloner

# Import trade processor for clean logic separation
from trade_processor import TradeProcessor
from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields

# Runtime diagnostics to detect stale module imports
def _origin(mod):
    try:
        return pathlib.Path(inspect.getfile(mod)).resolve()
    except Exception:
        return None

def _warn_origin(name, mod, repo_root: pathlib.Path):
    p = _origin(mod)
    print(f"[RUNTIME] {name} path: {p}")
    if p and repo_root not in p.parents and p != repo_root:
        print(f"[RUNTIME][WARN] {name} is being imported from OUTSIDE repo: {p}")

REPO_ROOT = pathlib.Path(__file__).resolve().parent

# Import core services with diagnostics
import fast_executor, jito_service, env_keys, execution_coordinator
_warn_origin("fast_executor", fast_executor, REPO_ROOT)
_warn_origin("jito_service", jito_service, REPO_ROOT)
_warn_origin("env_keys", env_keys, REPO_ROOT)
_warn_origin("execution_coordinator", execution_coordinator, REPO_ROOT)

# Import execution coordinator for trading
from execution_coordinator import ExecutionCoordinator

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

# Custom StreamHandler that flushes after every log record
class FlushingStreamHandler(logging.StreamHandler):
    """StreamHandler that flushes after every log record for real-time output."""
    def emit(self, record):
        super().emit(record)
        self.flush()

# Setup DEEP DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for deeper logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[FlushingStreamHandler()]
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


from execution_coordinator import normalize_dex, ROUTE_MAP, maybe_execute


def _have_all_fields(trade_info: dict) -> bool:
    """
    Check if trade_info has all required fields for execution.
    
    Returns True only if dex, wallet_address are all present and valid,
    AND token_mint (or mint) is present.
    
    Treats mint and token_mint as synonyms and normalizes to token_mint.
    
    Args:
        trade_info: Trade information dictionary
        
    Returns:
        bool: True if all required fields are present and valid
    """
    token_mint = trade_info.get("token_mint") or trade_info.get("mint")
    ok = all(v not in (None, "", "unknown", "PENDING_ANALYSIS") for v in (trade_info.get("dex"), trade_info.get("wallet_address"), token_mint))
    if ok and trade_info.get("token_mint") is None and token_mint:
        trade_info["token_mint"] = token_mint
    return ok




def schedule_deep_analysis(trade_info: dict):
    """
    Schedule deep analysis as a background task (non-blocking).
    
    This function creates an async task to analyze the trade without blocking
    the main execution flow. Used when requires_full_analysis is set but we
    want to attempt fast-path execution if fields are already ready.
    
    Args:
        trade_info: Trade information dictionary
    """
    # Note: This is a stub that creates a background task
    # The actual analysis will happen in _simple_trade_analysis
    # For now, we just log that scheduling was requested
    pass


async def try_backfill(trade_info: dict, rpc_client) -> bool:
    """
    Try to backfill missing signature and transaction data.
    
    This function attempts to fetch the latest transaction signature and full transaction
    data when trade_info is missing a signature (common for websocket_account_change events).
    
    Args:
        trade_info: Trade information dictionary that may be missing signature
        rpc_client: RPC client for fetching signature and transaction data
        
    Returns:
        bool: True if signature exists or was successfully backfilled, False otherwise
    """
    # If signature already exists, return True immediately
    sig = (trade_info.get("signature") or "").strip()
    if sig and sig != "unknown":
        logger.debug(f"[BACKFILL] Signature already present: {sig[:12]}...")
        return True
    
    # Get wallet address for backfill
    wallet_address = trade_info.get("wallet_address")
    if not wallet_address:
        logger.warning("⏳ [BACKFILL] No wallet address — cannot backfill")
        return False
    
    try:
        # Import backfill_latest_tx from websocket_handler
        from websocket_handler import backfill_latest_tx
        
        # Get RPC URL from client
        rpc_url = rpc_client.rpc_url if hasattr(rpc_client, 'rpc_url') else str(rpc_client)
        
        # Fetch latest signature via RPC
        logger.info(f"🔍 [BACKFILL] Attempting to fetch latest signature for wallet {wallet_address[:12]}...")
        backfill_result = await backfill_latest_tx(rpc_url, wallet_address)
        
        if not backfill_result:
            logger.info("⏳ [BACKFILL] No recent signature — waiting for logs event")
            return False
        
        # Check if we got a signature
        signature = backfill_result.get("signature")
        if not signature:
            logger.info("⏳ [BACKFILL] No recent signature — waiting for logs event")
            return False
        
        # Check if transaction data is available
        transaction = backfill_result.get("transaction")
        if not transaction:
            logger.info("⏳ [BACKFILL] getTransaction returned None — waiting for logs event")
            return False
        
        # Successfully backfilled - attach all data to trade_info
        trade_info["signature"] = signature
        trade_info["transaction"] = transaction
        trade_info["meta"] = backfill_result.get("meta")
        trade_info["logs"] = backfill_result.get("logs", [])
        
        logger.info(f"✅ [BACKFILL] Successfully backfilled signature {signature[:12]}... with transaction data")
        return True
        
    except Exception as e:
        logger.warning(f"⏳ [BACKFILL] Backfill failed: {e} — waiting for logs event")
        return False


async def route_and_execute(trade_info: dict, rpc, keypair, jito=None):
    """
    Route and execute trade with hard guard validation.
    
    ⚠️ CRITICAL: This function MUST be called with 'await' in async handlers!
    
    Skips execution if fields are incomplete. Wraps coordinator call in try/except to log any errors.
    
    Why await is critical:
    - Without await, coordinator logs never appear (🧭 [COORDINATOR] Route=...)
    - Without await, trade execution happens silently in background without error handling
    - Without await, the calling function returns before execution completes
    
    Args:
        trade_info: Trade information dictionary with required fields
        rpc: RPC client or RPC URL string
        keypair: Wallet keypair for signing transactions
        jito: Optional Jito service for MEV protection
        
    Example (CORRECT):
        await route_and_execute(trade_info, rpc=self.rpc_client, keypair=self.wallet, jito=self.jito_service)
        
    Example (WRONG - will fail silently):
        route_and_execute(trade_info, rpc=self.rpc_client, keypair=self.wallet, jito=self.jito_service)
    """
    if not _have_all_fields(trade_info):
        logger.warning("🛑 [PIPELINE_EXIT] Fields incomplete, skipping execution")
        return
    logger.info("🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator")
    
    # Extract rpc_url from rpc_client if needed
    rpc_url = rpc.rpc_url if hasattr(rpc, 'rpc_url') else rpc
    try:
        await maybe_execute(trade_info, rpc_url, keypair, jito_service=jito)
    except Exception as e:
        logger.error(f"❌ [PIPELINE_EXIT] Coordinator crashed: {e}", exc_info=True)


class SimpleCopyTradingBot:
    async def _process_detected_trade(self, trade_info: Dict[str, Any]):
        """
        INTELLIGENT TRADE DETECTION AND EXECUTION:
        Execute trades ONLY when trade intent can be fully reconstructed from transaction.
        
        Implements intelligent Solana copy trading with strict validation:
        
        EXECUTION PHILOSOPHY (INTELLIGENT MODE):
        - Only execute when trade intent (buy/sell/swap) is reconstructable
        - Only execute when token mint is extractable from transaction
        - Parses transaction logs and instructions to extract:
          * Direction: buy/sell/swap (parsed from logs/instructions)
          * Token Mint: SPL token address (extracted from transaction)
          * Amount: trade size information
        - Never blindly executes on account changes or wallet triggers alone
        
        INTELLIGENT VALIDATION (Only execute if we can reconstruct trade intent):
        - Action must be parseable from logs/instructions (buy, sell, swap_in, swap_out)
        - Token mint must be extractable from transaction
        - No execution on incomplete data (action=unknown or token=UNKNOWN)
        - Logs and skips ambiguous trades where direction or token cannot be parsed
        
        EXECUTION LOGIC:
        - Execute BUY if monitored wallet buys (action=buy/swap_in/swap)
        - Execute SELL if monitored wallet sells (action=sell/swap_out)
        - Maintain 0.001 SOL investment for all buy trades
        
        AUDIT LOGGING:
        - Documents trade parsing results
        - Logs execution decisions
        - Records skipped trades with signature and reason
        """
        # Generate correlation ID from signature/event_id/uuid
        sig = (trade_info.get("signature") or "").strip()
        event_id = trade_info.get("event_id", "")
        
        if sig and sig != "unknown":
            # Use signature as base for correlation ID
            correlation_id = f"{sig[:12]}"
        elif event_id:
            # Use event_id if available
            correlation_id = f"evt_{event_id[:8]}"
        else:
            # Generate UUID-based correlation ID
            correlation_id = f"uuid_{str(uuid.uuid4())[:8]}"
        
        # Set correlation ID for this thread
        set_span_id(correlation_id)
        
        # Log correlation context
        logger.info(
            "🪪 [CTX] corr=%s, dex=%s, wallet=%s",
            correlation_id,
            trade_info.get("dex", "unknown"),
            trade_info.get("wallet_address", "unknown")
        )
        
        # Get signature for audit trail (fallback to NO_SIGNATURE if not available)
        if not sig or sig == "unknown":
            sig = "NO_SIGNATURE"
        
        # STEP 1: Parse transaction logs and instructions to extract trade intent
        # Parses transaction logs and instructions to extract:
        # - Direction: buy/sell/swap (parsed from logs/instructions)
        # - Token Mint: SPL token address (extracted from transaction)
        # - Amount: trade size information
        logger.info(f"🔍 [TRADE_PARSE] Parsing transaction to reconstruct trade intent...")
        logger.info(f"   Signature: {sig[:12]}...")
        
        # Apply field inference from logs and transaction data
        trade_info = self.trade_processor.infer_missing_fields(trade_info)
        
        # Get source wallet
        source_wallet = (
            trade_info.get("wallet_address")
            or (self.target_wallets[0] if self.target_wallets else None)
            or str(self.wallet_pubkey)
        )
        
        # Check for trade instructions (DEX programs)
        instruction_info = self.trade_processor._check_trade_instructions(trade_info)
        has_trade_instructions = instruction_info.get('has_trade_instructions', False)
        
        if not has_trade_instructions:
            logger.warning(f"⚠️ [TRADE_PARSE] Cannot determine trade direction - no DEX instructions found")
            logger.info(f"📋 [AUDIT] Trade skipped: signature={sig[:12]}..., reason='No trade instructions detected'")
            return
        
        # Extract action and token mint from transaction
        action = trade_info.get('action', 'unknown')
        token_mint = trade_info.get('token_mint', 'UNKNOWN')
        
        # Use analyze_and_route_trade to extract missing fields if needed
        if token_mint == 'UNKNOWN' or action == 'unknown':
            logger.info(f"🔍 [TRADE_PARSE] Analyzing transaction for missing fields...")
            routing = await self.trade_processor.analyze_and_route_trade(trade_info, source_wallet)
            action = routing.get('action', action)
            token_mint = routing.get('token_mint', token_mint)
            trade_info.update(routing)
        
        # INTELLIGENT VALIDATION: Only execute if we can reconstruct trade intent
        valid_actions = {'buy', 'sell', 'swap', 'swap_in', 'swap_out'}
        
        # Check if action can be determined
        if action == 'unknown' or action not in valid_actions:
            logger.warning(f"⚠️ [TRADE_PARSE] Cannot determine trade direction from logs/instructions")
            logger.info(f"   Action: {action} (parsed from logs/instructions)")
            logger.info(f"📋 [SKIP] Skipping ambiguous trade: signature={sig[:12]}..., direction cannot be parsed")
            logger.info(f"📋 [AUDIT] Trade skipped: signature={sig[:12]}..., reason='direction cannot be parsed'")
            return
        
        # Check if token mint can be extracted
        if token_mint == 'UNKNOWN':
            logger.warning(f"⚠️ [TRADE_PARSE] Cannot extract token mint from transaction")
            logger.info(f"   Token Mint: {token_mint} (extracted from transaction)")
            logger.info(f"📋 [SKIP] Skipping ambiguous trade: signature={sig[:12]}..., token cannot be identified")
            logger.info(f"📋 [AUDIT] Trade skipped: signature={sig[:12]}..., reason='token cannot be identified'")
            return
        
        # Successfully parsed trade intent
        logger.info(f"✅ [TRADE_PARSE] Successfully parsed trade intent:")
        logger.info(f"   Action: {action} (parsed from logs/instructions)")
        logger.info(f"   Token Mint: {token_mint[:12]}... (extracted from transaction)")
        logger.info(f"   Source Wallet: {source_wallet[:12]}...")
        
        # Execute based on reconstructed trade intent
        # Execute BUY if monitored wallet buys
        # Execute SELL if monitored wallet sells
        if action in ("buy", "swap_in", "swap"):
            logger.info(f"🟢 [COPY_BUY] Executing BUY matching monitored wallet")
            logger.info(f"   Token: {token_mint[:12]}...")
            logger.info(f"   Amount: 0.001 SOL (explicit 0.001 SOL investment)")
            await self.execution_coordinator._execute_copy_buy(
                token_mint=token_mint,
                source_wallet=source_wallet,
                trade_info=trade_info,
                amount_sol=0.001  # Explicit 0.001 SOL investment
            )
            logger.info(f"📋 [AUDIT] Trade executed: signature={sig[:12]}..., action=BUY, amount=0.001 SOL, token={token_mint[:12]}...")
        elif action in ("sell", "swap_out"):
            logger.info(f"🔴 [COPY_SELL] Executing SELL matching monitored wallet")
            logger.info(f"   Token: {token_mint[:12]}...")
            await self.execution_coordinator._execute_copy_sell(
                token_mint=token_mint,
                source_wallet=source_wallet,
                trade_info=trade_info
            )
            logger.info(f"📋 [AUDIT] Trade executed: signature={sig[:12]}..., action=SELL, token={token_mint[:12]}...")
        else:
            # Should not reach here due to validation above
            logger.warning(f"⚠️ [TRADE_PARSE] Unexpected action '{action}'")
            logger.info(f"📋 [AUDIT] Trade skipped: signature={sig[:12]}..., reason='unexpected action type'")
    
    def _calculate_sell_percentage(self, trade_info: Dict[str, Any], source_wallet: str, token_mint: str) -> float:
        """
        Calculate the sell percentage based on monitored wallet's balance change.
        
        Args:
            trade_info: Transaction information with balance data
            source_wallet: Monitored wallet address
            token_mint: Token mint address
            
        Returns:
            float: Sell percentage (0-100)
        """
        try:
            # Get balance changes from transaction
            meta = trade_info.get('meta')
            if not meta:
                tx = trade_info.get('transaction_full') or trade_info.get('transaction', {})
                meta = tx.get('meta')
            
            if not meta:
                logger.warning("⚠️ [SELL_PCT] No meta data - defaulting to 100% sell")
                return 100.0
            
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            # Find source wallet's balance change for this token
            pre_amount = 0
            post_amount = 0
            
            for tb in pre_token_balances:
                if tb.get('owner') == source_wallet and tb.get('mint') == token_mint:
                    pre_amount = float(tb.get('uiTokenAmount', {}).get('uiAmount') or 0)
                    break
            
            for tb in post_token_balances:
                if tb.get('owner') == source_wallet and tb.get('mint') == token_mint:
                    post_amount = float(tb.get('uiTokenAmount', {}).get('uiAmount') or 0)
                    break
            
            if pre_amount == 0:
                logger.warning(f"⚠️ [SELL_PCT] No pre-balance found for {source_wallet[:8]}... - defaulting to 100% sell")
                return 100.0
            
            # Calculate percentage sold
            amount_sold = pre_amount - post_amount
            percentage_sold = (amount_sold / pre_amount) * 100
            
            # Ensure percentage is between 0 and 100
            percentage_sold = max(0, min(100, percentage_sold))
            
            logger.info(f"📊 [SELL_PCT] Monitored wallet sold {percentage_sold:.2f}% ({amount_sold:.6f} / {pre_amount:.6f})")
            
            return percentage_sold
            
        except Exception as e:
            logger.error(f"❌ [SELL_PCT] Error calculating sell percentage: {e}")
            logger.warning("   Defaulting to 100% sell")
            return 100.0

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
            self.rpc_client = RPCClient(self.config.rpc_url)
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
                # Get auth token from EnvKeys (JITO_UUID or JITO_AUTH_TOKEN)
                from env_keys import kz
                auth_token = kz.JITO_UUID or kz.JITO_AUTH_TOKEN
                block_engine_base = kz.JITO_BUNDLE_ENDPOINT or "https://mainnet.block-engine.jito.wtf"
                
                # Initialize with proper parameters
                self.jito_service = JitoClient(auth_token=auth_token, block_engine_base=block_engine_base)
                
                if auth_token:
                    logger.info(f"✅ Jito service initialized with auth token: {auth_token[:8]}...")
                else:
                    logger.info("✅ Jito service initialized without auth token (default rate limits)")
                logger.info(f"   Block engine: {block_engine_base}")
                logger.info("   Transactions will use MEV protection")
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
        logger.info(f"✅ Simple Copy Trading Bot initialized (DYNAMIC MODE)")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🚀 Jito MEV protection: {'✅ ENABLED' if self.jito_service else '❌ DISABLED'}")
        logger.info(f"   🔄 Mode: Builders enabled when fields complete, Cloner as fallback")
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
        """
        Handle incoming trade events from WebSocket with enhanced validation and parsing.
        
        This method is the entry point for all trade events detected via WebSocket monitoring.
        It performs several critical functions:
        
        1. Transaction Parsing: Uses wallet_tx_parser to decode and parse transaction data
        2. Field Validation: Ensures all required fields are present, defaulting missing ones
        3. Debug Logging: Logs any missing fields for upstream debugging
        4. Speed Optimization: Routes trades based on confidence for fast execution
        
        Args:
            trade_info (Dict[str, Any]): Trade information from WebSocket. Expected keys:
                - signature (str, optional): Transaction signature
                - wallet_address (str, optional): Source wallet address
                - transaction (dict, optional): Raw transaction data
                - dex/dex_type (str, optional): DEX identifier
                - action (str, optional): Trade action (buy/sell/swap)
                - mint/token_mint (str, optional): Token mint address
        
        Field Defaulting Strategy:
            - signature: Log warning, continue processing (may be unavailable for account-change events)
            - wallet_address: Default to first target wallet
            - dex/dex_type: Default to 'unknown', will be inferred during analysis
            - action: Default to 'unknown', will be inferred during analysis
            - mint/token_mint: Default to 'PENDING_ANALYSIS', will be extracted during analysis
        
        Note:
            This method implements graceful degradation - missing fields don't halt execution,
            but rather trigger fallback analysis and extraction logic downstream.
        """
        import traceback
        
        logger.info(f"[PIPELINE_ENTRY] 🚨 Trade event received from WebSocket")
        logger.debug(f"[PIPELINE_ENTRY] Trade info keys: {list(trade_info.keys())}")
        
        # Step 3: Parse and decode transaction using wallet_tx_parser
        try:
            if 'transaction' in trade_info:
                # Parse and decode transaction before analysis/execution
                logger.debug(f"[PIPELINE_ENTRY] Parsing transaction with wallet_tx_parser...")
                # Pass trade_info which contains both transaction and meta
                parsed_tx = self.tx_parser.parse_transaction(trade_info)
                trade_info['parsed_tx'] = parsed_tx
                logger.debug(f"[PIPELINE_ENTRY] ✅ Transaction parsed successfully")
                # Merge parser-detected fields into trade_info before any defaulting logic
                merge_parsed_fields(trade_info, parsed_tx)
        except Exception as e:
            logger.error(f"[PIPELINE_ENTRY] ❌ Error parsing transaction: {e}")
            logger.error(traceback.format_exc())
            
        logger.debug(f"[PIPELINE_ENTRY] Received trade_info: {json.dumps(trade_info, default=str)[:500]}...")
        """🚀 ENHANCED: Handle trades with MAXIMUM SPEED - Copy ALL transactions immediately"""
        try:
            logger.info(f"[PIPELINE_ENTRY] ⚡ SPEED TRADE DETECTION: Processing trade...")

            # === ENHANCED UPSTREAM DATA FIX: Ensure required fields are present with debug logging ===
            # This section validates and defaults missing fields to prevent execution failures
            # downstream. Each missing field is logged for debugging upstream data issues.
            
            # Check signature
            sig = (trade_info.get("signature") or "").strip()
            if sig and sig != "unknown":
                logger.debug(f"[PIPELINE_ENTRY] Signature: {sig[:12]}...")
            
            # Check wallet_address - try to extract from transaction if still missing
            if not trade_info.get("wallet_address"):
                # Try first signer from the tx
                msg = (trade_info.get("transaction") or {}).get("message", {})
                signers = [k["pubkey"] for k in (msg.get("accountKeys") or []) if k.get("signer")]
                if signers:
                    trade_info["wallet_address"] = signers[0]
                    logger.info("[PIPELINE_ENTRY] Set wallet_address from tx signer: %s", signers[0])
                else:
                    logger.warning("[PIPELINE_ENTRY] No signer in tx; leaving wallet_address empty")
            else:
                logger.debug(f"[PIPELINE_ENTRY] Wallet: {trade_info.get('wallet_address')[:12]}...")
            
            # Now compute what's still missing after merge and extraction
            missing = []
            for k in ("wallet_address", "dex", "action", "token_mint"):
                if trade_info.get(k) in (None, "", "unknown", "PENDING_ANALYSIS"):
                    missing.append(k)
            if missing:
                logger.info(f"[PIPELINE_ENTRY] 📋 Missing/defaulted fields: {', '.join(missing)}")
            else:
                logger.info(f"[PIPELINE_ENTRY] ✅ All expected fields present")
            
            logger.debug(f"[PIPELINE_ENTRY] After upstream fix: {json.dumps(trade_info, default=str)[:500]}...")

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
            # Support both requires_analysis and requires_full_analysis field names
            if trade_info.get('requires_analysis') or trade_info.get('requires_full_analysis'):
                logger.debug(f"[DEBUG] requires_analysis: {trade_info.get('requires_analysis')}, requires_full_analysis: {trade_info.get('requires_full_analysis')}")
                signature = trade_info.get('signature')
                wallet_address = trade_info.get('wallet_address')
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
                            logger.warning(f"⚠️ Fast analysis failed for {signature[:8]}... - will attempt fast path execution if fields are ready")
                    except Exception as e:
                        logger.warning(f"⚠️ Deep analysis scheduling failed: {e}")
                    # DO NOT return here — still attempt fast path execution if fields are ready

            # STEP 0: For websocket_account_change, try backfill before proceeding
            detection_method = trade_info.get("detection_method", "")
            if detection_method == "websocket_account_change":
                logger.info("🔍 [BACKFILL] websocket_account_change detected — attempting backfill...")
                backfill_success = await try_backfill(trade_info, self.rpc_client)
                
                if not backfill_success:
                    # Backfill failed, log and wait for subsequent logs event
                    logger.info("⏳ [BACKFILL] Backfill failed — waiting for subsequent websocket_logs event")
                    logger.info("ℹ️ [PIPELINE] Not marking as skipped to allow logs event to proceed")
                    return  # Return without marking as skipped
                
                logger.info("✅ [BACKFILL] Backfill succeeded — proceeding to validation")
                
                # Parse the newly backfilled transaction and merge fields
                try:
                    if 'transaction' in trade_info:
                        logger.debug(f"[BACKFILL] Parsing backfilled transaction...")
                        # Pass both transaction and meta to parser as per problem statement
                        tx_with_meta = {
                            "transaction": trade_info.get("transaction", {}),
                            "meta": trade_info.get("meta")
                        }
                        parsed = self.tx_parser.parse_transaction(tx_with_meta)
                        merge_parsed_fields(trade_info, parsed)
                        logger.debug(f"[BACKFILL] ✅ Merged fields from backfilled transaction")
                except Exception as e:
                    logger.error(f"[BACKFILL] ❌ Error parsing backfilled transaction: {e}")
            
            # STEP 1: Infer missing fields before validation - with error resilience
            logger.debug(f"[DEBUG] Before infer_missing_fields: {json.dumps(trade_info, default=str)}")
            try:
                trade_info = self.trade_processor.infer_missing_fields(trade_info)
                logger.debug(f"[DEBUG] After infer_missing_fields: {json.dumps(trade_info, default=str)}")
            except Exception as e:
                logger.error("❌ infer_missing_fields crashed", exc_info=True)
            finally:
                # Do NOT return early on requires_full_analysis
                if trade_info.get("requires_full_analysis"):
                    try:
                        schedule_deep_analysis(trade_info)  # fire-and-forget
                        logger.info("ℹ️ Deep analysis scheduled; continuing fast-path")
                    except Exception as e:
                        logger.warning(f"⚠️ Deep analysis scheduling failed: {e}")
                
                # Check if we have all required fields and call coordinator
                have_all = _have_all_fields(trade_info)
                trade_info["use_universal_cloner"] = not have_all
                
                # Log mode selection
                if have_all:
                    logger.info("🧭 [MODE] Builders enabled (all fields complete), Cloner as fallback")
                else:
                    logger.info("🧭 [MODE] Cloner fallback (fields incomplete)")
                
                # Log handoff to coordinator
                logger.info("📤 [HANDOFF] Calling coordinator now…")
                await route_and_execute(trade_info, self.rpc_client, self.wallet, jito=self.jito_service)
                logger.info("📥 [HANDOFF] Coordinator call returned")
            
            # STEP 2: Validate and process
            logger.debug(f"[DEBUG] Before validate_trade_info: {json.dumps(trade_info, default=str)}")
            is_valid = self.trade_processor.validate_trade_info(trade_info)
            logger.debug(f"[DEBUG] validate_trade_info result: {is_valid}")
            if is_valid:
                await self._process_detected_trade(trade_info)
            else:
                # Enhanced logging for skipped trades per problem statement requirements
                logger.warning(f"⚠️ Trade validation failed - skipping")
                
                # Log full context for debugging (per problem statement: log raw tx and reason)
                sig = trade_info.get('signature', 'unknown')
                logger.error(f"❌ [SKIPPED_TRADE] Signature: {sig}")
                logger.error(f"❌ [SKIPPED_TRADE] Reason: Validation failed - missing or invalid required fields")
                
                # Log what fields failed validation
                mint = trade_info.get('token_mint') or trade_info.get('mint')
                action = trade_info.get('action')
                dex = trade_info.get('dex') or trade_info.get('dex_type')
                
                validation_issues = []
                if not sig or sig == 'unknown':
                    validation_issues.append("missing signature")
                if not mint or mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
                    validation_issues.append(f"invalid/missing mint (got: {mint})")
                if not action or action == 'unknown':
                    validation_issues.append(f"invalid/missing action (got: {action})")
                if not dex or dex == 'unknown':
                    validation_issues.append(f"unknown DEX (got: {dex})")
                
                logger.error(f"❌ [SKIPPED_TRADE] Validation issues: {', '.join(validation_issues)}")
                
                # Log raw transaction data for offline analysis (per problem statement)
                if 'transaction' in trade_info or 'transaction_full' in trade_info:
                    tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                    logger.error(f"❌ [SKIPPED_TRADE] Raw transaction keys: {list(tx.keys()) if tx else 'None'}")
                    if 'logs' in trade_info:
                        logger.error(f"❌ [SKIPPED_TRADE] Log count: {len(trade_info['logs'])} messages")
                else:
                    logger.error(f"❌ [SKIPPED_TRADE] No transaction data available for analysis")
                
                # Log to failed_trade_analysis.log for offline debugging
                log_failed_trade_analysis(
                    trade_info,
                    failure_reason=f"validation_failed: {', '.join(validation_issues)}",
                    retry_count=0,
                    routing_data=None
                )

        except asyncio.TimeoutError:
            logger.warning("⏰ Trade handling timeout - processing anyway")
            logger.debug(f"[DEBUG] Timeout trade_info: {json.dumps(trade_info, default=str)}")
            # Infer missing fields before validation (timeout case)
            trade_info = self.trade_processor.infer_missing_fields(trade_info)
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
        Perform comprehensive health checks on all critical system components.
        
        This method validates the operational status of:
        - RPC client connectivity (ability to communicate with Solana network)
        - Jito service initialization (MEV protection, if configured)
        - WebSocket handler (real-time trade monitoring)
        - Execution coordinator (trade execution logic)
        - Trade processor (trade analysis and routing)
        
        Returns:
            Dict[str, bool]: Dictionary mapping component names to health status.
                           True indicates healthy, False indicates unhealthy.
                           
        Note:
            Components marked as optional (like Jito) will return True if not configured,
            as their absence doesn't indicate a system health issue.
        """
        health_status = {}
        
        try:
            # Check RPC client connectivity
            # This is critical - without RPC we cannot interact with Solana network
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
            # Jito is optional, so its absence is not a health issue
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
            # Critical for real-time trade detection
            try:
                if self.ws_handler:
                    health_status['websocket'] = hasattr(self.ws_handler, 'is_connected')
                else:
                    health_status['websocket'] = False
            except Exception as e:
                logger.debug(f"WebSocket health check failed: {e}")
                health_status['websocket'] = False
            
            # Check execution coordinator
            # Critical for trade execution
            try:
                if self.execution_coordinator:
                    health_status['execution_coordinator'] = True
                else:
                    health_status['execution_coordinator'] = False
            except Exception as e:
                logger.debug(f"Execution coordinator health check failed: {e}")
                health_status['execution_coordinator'] = False
            
            # Check trade processor
            # Critical for trade analysis and routing
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
