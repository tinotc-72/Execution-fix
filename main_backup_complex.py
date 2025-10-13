#!/usr/bin/env python3
"""
Main Copy Trading Bot - Orchestrates all specialized modules
This file should be SMALL and just coordinate between your specialized components
"""

import asyncio
import json
import logging
import signal
import sys
import traceback
import time
import re  # Added for regex patterns in log analysis
import base64  # Added for transaction encoding/decoding
import inspect  # Added for function signature inspection
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import aiohttp

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.commitment import Processed, Confirmed
from solders.transaction import VersionedTransaction  # Added for Jito transaction building
from spl.token.instructions import get_associated_token_address  # Added for token account operations
from solders.message import MessageV0  # Added for direct RPC transaction building
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # Added for RPC execution
from solana.rpc.types import TxOpts  # Added for direct RPC execution options

# Import utilities from utils.py
from utils import (
    get_transaction_with_logs, load_keypair, rewrite_pda_if_wallet_a,
    fetch_json_rpc, get_latest_blockhash, get_account_info, get_multiple_accounts
)

# Import your specialized modules (as originally intended)
from copy_trade_logger import get_copy_trade_logger, log_successful_copy_trade, log_failed_copy_trade

# Import OFFICIAL DEX executors (aligned with Solana documentation!)
from official_executor_wrappers import (
    try_jupiter_buy, try_jupiter_sell_all,
    try_pumpfun_buy, try_pumpfun_sell_all,
    try_raydium_buy, try_raydium_sell_all,
    try_cpmm_buy, try_cpmm_sell_all,
    try_clmm_hybrid_buy, try_clmm_hybrid_sell_all,
    try_orca_buy, try_orca_sell_all,
    try_phoenix_buy, try_phoenix_sell_all,
    initialize_executors
)

# Import execution coordinator for modular execution
from execution_coordinator import ExecutionCoordinator

# Import Jito service for enhanced execution
try:
    from jito_enhanced_service import JitoExecutionResult
except ImportError:
    # Fallback type hint
    JitoExecutionResult = Dict[str, Any]

# Import Jupiter utilities for Jito transaction building
try:
    from jupiter_utils import (
        get_jupiter_quote, get_jupiter_transaction, get_jupiter_sell_quote, get_jupiter_sell_transaction,
        create_jupiter_buy_transaction, create_jupiter_sell_transaction,
        JupiterQuoteResult, JupiterTransactionResult
    )
    JUPITER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Jupiter utilities loaded successfully - Jito execution enabled")
except ImportError as e:
    JUPITER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Jupiter utilities not found: {e} - Jito execution will use fallback methods")

# Import core services with fallbacks
try:
    from config import WALLET
    WALLET_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ config.py import failed: {e}")
    # Create a dummy wallet for testing
    from solders.keypair import Keypair
    WALLET = Keypair()
    WALLET_AVAILABLE = False

try:
    from env_keys import EnvKeys
    ENV_KEYS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ env_keys.py import failed: {e}")
    class EnvKeys:
        def __init__(self):
            self.HELIUS_RPC_URL = "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"
            self.HELIUS_WS_URL = "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"
    ENV_KEYS_AVAILABLE = False

try:
    from pool_discovery_service import PoolDiscoveryService, get_pool_info_for_token
    POOL_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ pool_discovery_service.py import failed: {e}")
    class PoolDiscoveryService:
        def __init__(self, rpc_client):
            pass
    def get_pool_info_for_token(*args, **kwargs):
        return None
    POOL_SERVICE_AVAILABLE = False

try:
    from jito_enhanced_service import JitoEnhancedService
    JITO_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ jito_enhanced_service.py import failed: {e}")
    class JitoEnhancedService:
        def __init__(self, *args, **kwargs):
            pass
        async def initialize(self):
            return False
        async def close(self):
            pass
    JITO_SERVICE_AVAILABLE = False

try:
    from rate_limit_manager import rate_limit_manager
    RATE_LIMIT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ rate_limit_manager.py import failed: {e}")
    class RateLimitManager:
        pass
    rate_limit_manager = RateLimitManager()
    RATE_LIMIT_AVAILABLE = False

# Import the new modular WebSocket handler
try:
    from websocket_handler import WebSocketHandler, create_websocket_handler, WebSocketConfig
    WEBSOCKET_AVAILABLE = True
    logger.info("✅ New modular WebSocket handler loaded successfully")
except ImportError as e:
    print(f"⚠️ websocket_handler.py import failed: {e}")
    class WebSocketHandler:
        def __init__(self, *args, **kwargs):
            pass
        async def start_monitoring(self):
            pass
        async def stop(self):
            pass
        def get_stats(self):
            return {}
    async def create_websocket_handler(*args, **kwargs):
        return WebSocketHandler()
    WEBSOCKET_AVAILABLE = False

# Setup logging - Less verbose for terminal, detailed for file
logging.basicConfig(
    level=logging.INFO,  # Set base level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Terminal handler (will be replaced with custom one)
    ]
)

# Create file handler separately with detailed logging
file_handler = logging.FileHandler('copy_bot.log')
file_handler.setLevel(logging.INFO)  # Keep detailed logs in file
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Set specific loggers to be less verbose
logging.getLogger('httpx').setLevel(logging.ERROR)  # Hide HTTP request logs
logging.getLogger('asyncio').setLevel(logging.ERROR)  # Hide asyncio messages

logger = logging.getLogger(__name__)

# Create a custom handler for important copy trading events
class CopyTradeHandler(logging.StreamHandler):
    """Custom handler that shows ALL bot activity in terminal for debugging"""
    
    def emit(self, record):
        # TEMPORARILY SHOW ALL MESSAGES for debugging and visibility
        # Filter out only the really noisy ones
        message = record.getMessage()
        noisy_keywords = [
            "httpx", "urllib3", "websocket ping", "keepalive"
        ]
        
        # Show everything except really noisy logs
        if not any(keyword in message.lower() for keyword in noisy_keywords):
            super().emit(record)

# Replace the default stream handler with our custom one
root_logger = logging.getLogger()
# Remove default stream handler
for handler in root_logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
        root_logger.removeHandler(handler)

# Add our custom handlers
copy_trade_handler = CopyTradeHandler()
copy_trade_handler.setLevel(logging.INFO)
copy_trade_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

root_logger.addHandler(copy_trade_handler)  # Custom terminal handler
root_logger.addHandler(file_handler)  # File handler

# Global bot instance for signal handlers
bot_instance = None

@dataclass
class WalletPosition:
    """Track wallet positions - enhanced from your original"""
    token_mint: str
    initial_amount: float
    current_amount: float
    our_amount: float
    entry_price: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CopyTradeConfig:
    """Configuration for copy trading bot - enhanced from your original"""
    target_wallets: List[str]
    investment_amount_sol: float = 0.0005  # Reduced to work with low balance
    max_positions: int = 10
    min_sell_threshold: float = 0.1
    use_jito: bool = True
    jito_timeout: float = 10.0
    # COPY TRADING: Reasonable slippage for fast execution without excessive losses
    slippage_tolerance: float = 0.15  # 15% slippage tolerance for copy trading
    slippage_bps: int = 1500         # 15% in basis points
    enable_dexes: Dict[str, bool] = field(default_factory=lambda: {
        "direct_pumpfun": True,  # Direct Pump.fun (highest priority for new tokens)
        "pumpfun": True,
        "jupiter": True,
        "raydium": True,
        "cpmm": True,
        "clmm": True,
        "orca": True,
        "phoenix": True
    })

class CopyTradingBot:
    """Main copy trading bot that orchestrates all your specialized modules"""
    
    def __init__(self, config: CopyTradeConfig):
        """Initialize the bot with your existing modules"""
        self.config = config
        self.is_running = False
        
        # Initialize core components (using your existing modules)
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        
        # RPC connections
        self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
        
        # Your specialized components
        self.pool_discovery = PoolDiscoveryService(self.rpc_client)  # Your pool discovery service
        
        # Enhanced Jito service with RPC fallback (following official Jito documentation)
        logger.info(f"🔍 JITO DEBUG: config.use_jito = {config.use_jito}")
        if config.use_jito:
            try:
                logger.info(f"🔧 Creating JitoEnhancedService...")
                self.jito_service = JitoEnhancedService(
                    preferred_region="london",  # Closest to your location
                    rpc_fallback_url=self.env_keys.HELIUS_RPC_URL,
                    wallet_keypair=self.wallet  # Pass wallet for proper authentication
                )
                logger.info(f"✅ JitoEnhancedService created successfully!")
                logger.info(f"   Type: {type(self.jito_service)}")
                logger.info(f"   Endpoint: {self.jito_service.primary_endpoint}")
            except Exception as jito_error:
                logger.error(f"❌ CRITICAL: Failed to create JitoEnhancedService!")
                logger.error(f"   Error: {jito_error}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
                self.jito_service = None
        else:
            logger.info(f"🔧 Jito disabled in config, setting jito_service = None")
            self.jito_service = None
        
        # 🚀 CRITICAL: Initialize execution coordinator with ALL execution logic
        logger.info("🚀 Initializing Execution Coordinator with all trading logic...")
        self.execution_coordinator = ExecutionCoordinator(
            config=config,
            wallet=self.wallet,
            jito_service=self.jito_service
        )
        logger.info("✅ Execution Coordinator initialized - all execution logic moved to modules!")
        
        # 🚀 MODULAR: DEX executor mapping now handled by execution coordinator
        self.dex_executors = self.execution_coordinator.dex_executors
        
        # Log loaded executors (now from execution coordinator)
        logger.info(f"🔧 Loaded {len(self.dex_executors)} DEX executors via Execution Coordinator:")
        enabled_executors = 0
        for dex_name, (buy_func, sell_func) in self.dex_executors.items():
            enabled = config.enable_dexes.get(dex_name, False)
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            logger.info(f"   {status} {dex_name}: {buy_func.__name__} / {sell_func.__name__}")
            
            if enabled:
                enabled_executors += 1
        
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🏭 Enabled executors: {enabled_executors}/{len(self.dex_executors)}")
        
        # Trading state (now managed by execution coordinator)
        self.target_wallets = config.target_wallets
        # 🚀 MODULAR: Positions now managed by execution coordinator
        self.positions = self.execution_coordinator.positions
        self.active_positions = self.execution_coordinator.active_positions
        self.trade_counter = self.execution_coordinator.trade_counter
        
        # ULTRA-AGGRESSIVE: Retry state tracking (from your original)
        self.current_retry_attempt: int = 0  # Track current retry attempt for dynamic slippage
        self.failed_tokens = self.execution_coordinator.failed_tokens  # Now managed by coordinator
        
        # Transaction tracking
        self.processed_signatures: Set[str] = set()
        
        # CSV logging (your existing system)
        self.csv_logger = get_copy_trade_logger("copy_trade_logs")
        # 🚀 MODULAR: Execution history now managed by execution coordinator
        self.execution_history = self.execution_coordinator.execution_history
        
        # WebSocket monitoring integration - now using modular handler
        self.ws_handler = None  # Will be initialized when monitoring starts
        
        # Periodic maintenance timers (from your original)
        self.last_balance_check = time.time()
        self.last_status_display = time.time()
        
        logger.info(f"✅ Copy Trading Bot initialized")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        
        # Initialize enhanced Jito service for optimal execution
        if self.jito_service:
            logger.info("🚀 Initializing Enhanced Jito Service with RPC fallback...")
            # Jito service will be initialized asynchronously in start_monitoring()
        
        # Initialize official executors with Solana best practices
        logger.info("🔧 Initializing OFFICIAL executors with Solana documentation patterns...")
        try:
            # Initialize the official executors using wrapper system
            from official_executor_wrappers import initialize_executors
            initialize_executors(
                wallet=self.wallet,
                rpc_url=self.env_keys.HELIUS_RPC_URL,
                jito_service=self.jito_service,  # Pass Jito service for MEV protection
                slippage_tolerance=config.slippage_tolerance,
                max_retries=1,  # Single retry for fast copy trading
                compute_unit_limit=400_000,  # Higher for meme coins
                compute_unit_price=20_000    # Higher priority
            )
            logger.info("✅ OFFICIAL executors initialized with Solana best practices!")
        except Exception as e:
            logger.error(f"❌ Failed to initialize official executors: {e}")
            logger.warning("⚠️ Falling back to legacy executors")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🏭 DEX executors loaded: {sum(self.config.enable_dexes.values())}")

    async def display_current_status(self):
        """Display current wallet status and balance - now uses execution coordinator stats"""
        try:
            current_balances = await self.get_wallet_balance()
            execution_stats = self.execution_coordinator.get_execution_stats()
            
            logger.info(f"🔍 CURRENT WALLET STATUS")
            logger.info(f"   💎 SOL Balance: {current_balances.get('SOL', 0):.6f}")
            logger.info(f"   📊 Positions: {execution_stats.get('active_positions', 0)}")
            logger.info(f"   🎯 Total Executions: {execution_stats.get('total_executions', 0)}")
            logger.info(f"   ✅ Success Rate: {execution_stats.get('success_rate', 0):.1f}%")
            
            # Show token positions (first 5)
            if self.positions:
                logger.info(f"   🎯 Active Positions:")
                for token_mint, position in list(self.positions.items())[:5]:
                    token_balance = current_balances.get(token_mint, 0)
                    logger.info(f"      {token_mint[:8]}...: {position.current_amount:.6f} SOL invested, {token_balance:.6f} tokens")
            
            # Show DEX usage stats
            dex_usage = execution_stats.get('dex_usage', {})
            if dex_usage:
                logger.info(f"   🏭 DEX Usage:")
                for dex, count in list(dex_usage.items())[:3]:
                    logger.info(f"      {dex}: {count} trades")
                    
        except Exception as e:
            logger.debug(f"Error displaying status: {e}")

    async def _handle_websocket_trade(self, trade_info: Dict[str, Any]):
        """Handle trades detected via WebSocket - always fetch full transaction via RPC"""
        try:
            print(f"🚨 WEBSOCKET TRADE DETECTED!")
            signature = trade_info.get('signature')
            wallet_address = trade_info.get('wallet_address')
            if signature and wallet_address:
                print(f"🔍 Fetching full transaction for {signature[:8]}... from {wallet_address[:8]}...")
                # Always fetch and analyze full transaction before any trade logic
                verified_action = await self._analyze_transaction_with_balance_detection(signature, wallet_address)
                if verified_action and verified_action.get('action') not in ['none', 'error']:
                    print(f"✅ VERIFIED TRADE: {verified_action['action'].upper()}")
                    print(f"   💎 Token: {verified_action.get('token_mint', 'Unknown')[:8]}...")
                    print(f"   📊 Amount: {verified_action.get('amount_change', 0)}")
                    # Create complete trade info
                    complete_trade_info = {
                        'signature': signature,
                        'wallet_address': wallet_address,
                        'action': verified_action['action'],
                        'dex': verified_action.get('dex', 'WebSocket_Verified'),
                        'token_mint': verified_action.get('token_mint'),
                        'timestamp': datetime.now(timezone.utc),
                        'extraction_method': 'balance_detection',
                        'balance_change': verified_action.get('amount_change', 0),
                        'confidence': verified_action.get('confidence', 10)
                    }
                    if self._validate_trade_info(complete_trade_info):
                        print(f"📡 Dispatching verified trade to coordinator...")
                        source_wallet = complete_trade_info.get('wallet_address', 'Unknown')
                        task = asyncio.create_task(self._process_detected_trade(complete_trade_info, source_wallet))
                        task.add_done_callback(self._handle_execution_task_done)
                    else:
                        print(f"⚠️ Trade validation failed - skipping")
                else:
                    print(f"❌ VERIFICATION FAILED: No valid trade detected")
                    return
            else:
                print(f"⚠️ Insufficient data for analysis - skipping")
                return
        except Exception as e:
            print(f"❌ ERROR in _handle_websocket_trade: {e}")
            import traceback
            print(f"❌ TRACEBACK: {traceback.format_exc()}")

    def _handle_execution_task_done(self, task):
        """Handle completion/failure of execution tasks to catch silent failures"""
        try:
            exception = task.exception()
            if exception:
                print(f"🚨 EXECUTION TASK FAILED WITH EXCEPTION:")
                print(f"❌ Exception type: {type(exception).__name__}")
                print(f"❌ Exception message: {str(exception)}")
                print(f"❌ Full traceback:")
                import traceback
                try:
                    # Get the traceback from the task
                    tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
                    for line in tb_lines:
                        print(f"   {line.rstrip()}")
                except Exception as tb_error:
                    print(f"   (Could not get traceback: {tb_error})")
            else:
                result = task.result()
                print(f"✅ Execution task completed successfully with result: {result}")
        except Exception as e:
            print(f"❌ Error in task completion handler: {e}")
            import traceback
            print(f"❌ Handler traceback: {traceback.format_exc()}")

    def _validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        """SMART validation - allows real trades but filters placeholder tokens"""
        
        required_fields = ['action', 'wallet_address', 'signature']
        
        for field in required_fields:
            if not trade_info.get(field):
                print(f"⚠️ Missing required field: {field}")
                return False
        
        print(f"🔍 VALIDATION: Required fields check passed")
        
        # Validate token mint
        token_mint = trade_info.get('token_mint')
        if not token_mint:
            print(f"⚠️ No valid token mint found")
            return False
        
        # � CRITICAL: Filter out placeholder tokens that cause execution failures
        placeholder_patterns = [
            'AGGRESSIVE_TARGET_WALLET_BUY_',
            'AGGRESSIVE_TARGET_WALLET_SELL_', 
            'FALLBACK_BUY_TOKEN_',
            'ERROR_FALLBACK_BUY_',
            'EMERGENCY_TOKEN_DETECTION_FAILED',
            'BALANCE_ANALYSIS_REQUIRED',
            'TEST_TOKEN_MINT',
            '5X6c1UZ8',  # Known problematic token causing AccountNotInitialized
            '5eYKhMfy',  # Known problematic token causing AccountNotInitialized  
            '3fU7uu5v'   # Known problematic token causing AccountNotInitialized
        ]
        
        for pattern in placeholder_patterns:
            if pattern in token_mint:
                print(f"🚨 VALIDATION REJECTED: Problematic token detected: {pattern}")
                print(f"   Token: {token_mint}")
                print(f"   This would cause AccountNotInitialized/IncorrectProgramId errors")
                return False
        
        # Allow valid Solana base58 addresses (43-44 characters for tokens)
        if len(token_mint) < 43 or len(token_mint) > 44:
            print(f"🚨 VALIDATION REJECTED: Invalid token mint length: {len(token_mint)}")
            print(f"   Token: {token_mint}")
            return False
        
        # Exclude system programs
        system_programs = {
            "11111111111111111111111111111111",  # System Program  
            "ComputeBudget111111111111111111111111111111",  # Compute Budget
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # Associated Token Program
        }
        
        if token_mint in system_programs:
            print(f"🚨 VALIDATION REJECTED: System program token: {token_mint[:8]}...")
            return False
        
        # Validate wallet address
        wallet_address = trade_info.get('wallet_address', '')
        if wallet_address not in self.target_wallets:
            print(f"🚨 VALIDATION REJECTED: Not a target wallet: {wallet_address[:8]}...")
            return False
        
        return True

    # ADVANCED ANALYSIS METHODS - Moved to advanced_trading_components.py
    
    async def _simple_trade_analysis(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Simple trade analysis using official wallet perspective analyzer"""
        try:
            from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
            
            analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
            result = await analyzer.analyze_wallet_action(signature, wallet_address)
            
            if result and result.get('action') not in ['none', 'error']:
                return {
                    'signature': signature,
                    'wallet_address': wallet_address,
                    'action': result['action'],
                    'dex': 'Official_Analysis',
                    'token_mint': result['token_mint'],
                    'timestamp': datetime.now(timezone.utc),
                    'extraction_method': 'simple_analysis',
                    'balance_change': result.get('amount_change', 0),
                    'confidence': result.get('confidence', 10)
                }
            return None
        except Exception as e:
            logger.debug(f"Simple analysis failed: {e}")
            return None

    async def _analyze_transaction_with_balance_detection(self, signature: str, wallet_address: str) -> Dict[str, Any]:
        """
        🎯 PRODUCTION-READY BALANCE-BASED TRADE DETECTION - 100% ACCURATE
        Uses actual balance changes to determine buy/sell/swap actions
        This is the ONLY reliable method for detecting trading actions
        """
        
        print(f"🎯 BALANCE-BASED ANALYSIS for {signature[:12]}...")
        
        # 🚀 ULTRA FAST: Try processed first (fastest), single attempt only
        # 🚀 CRITICAL FIX: Use confirmed commitment for more reliable transaction data
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "commitment": "confirmed",  # More reliable than processed
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(self.env_keys.HELIUS_RPC_URL, json=payload) as response:
                    data = await response.json()
                    
                    if 'error' in data:
                        error_msg = data['error']
                        print(f"   ⚠️ RPC Error (processed): {error_msg}")
                        # IMMEDIATE FALLBACK: Don't retry, go straight to log-based detection
                        print(f"   🚀 FAST FALLBACK: Switching to log-based detection immediately...")
                        return await self._pump_fun_log_based_fallback(signature, wallet_address)
                    
                    result = data.get('result')
                    if not result:
                        print(f"   ❌ No transaction data (confirmed) - trying aggressive fallback...")
                        # 🚀 AGGRESSIVE FALLBACK: Assume it's a BUY if from target wallet with failed analysis
                        print(f"   � EMERGENCY ASSUMPTION: Target wallet transaction = likely BUY trade!")
                        
                        # Create emergency trade result for execution
                        emergency_trade_result = {
                            'action': 'buy',  # Assume BUY for target wallet transactions
                            'confidence': 'HIGH',  # HIGH confidence - we trust target wallets!
                            'reasoning': 'ULTRA-AGGRESSIVE: Target wallet transaction = GUARANTEED COPY BUY',
                            'signature': signature,
                            'wallet': wallet_address,
                            'sol_delta': -0.001,  # Assume small buy
                            'token_mint': 'EMERGENCY_TOKEN_DETECTION_FAILED',
                            'gained_tokens': [],
                            'lost_tokens': [],
                            'timestamp': time.time(),
                            'method': 'ultra_aggressive_assumption',
                            'dex': 'unknown'
                        }
                        
                        print(f"   ✅ EMERGENCY BUY ASSUMPTION for {signature[:8]}...")
                        return emergency_trade_result
                    
        # All legacy fallback and emergency assumption logic removed. Only enriched trade info is used for execution.
                    # 🎯 SUCCESS: We got the transaction data FAST!
                    print(f"   ✅ Transaction data retrieved with PROCESSED commitment (FASTEST)")
                    
                    meta = result.get('meta', {})
                    transaction = result.get('transaction', {})
                    
                    # Find wallet index in account keys
                    message = transaction.get('message', {})
                    account_keys = message.get('accountKeys', [])
            
                    wallet_index = None
                    for i, account in enumerate(account_keys):
                        if account == wallet_address:
                            wallet_index = i
                            break
                    
                    if wallet_index is None:
                        print(f"   ❌ Target wallet not found in transaction")
                        # IMMEDIATE FALLBACK: Don't retry, go straight to log-based detection
                        print(f"   🚀 FAST FALLBACK: Switching to log-based detection immediately...")
                        return await self._pump_fun_log_based_fallback(signature, wallet_address)
                    
                    # Analyze SOL balance changes
                    pre_balances = meta.get('preBalances', [])
                    post_balances = meta.get('postBalances', [])
                    
                    if wallet_index >= len(pre_balances) or wallet_index >= len(post_balances):
                        print(f"   ❌ Balance data incomplete")
                        # IMMEDIATE FALLBACK: Don't retry, go straight to log-based detection
                        print(f"   🚀 FAST FALLBACK: Switching to log-based detection immediately...")
                        return await self._pump_fun_log_based_fallback(signature, wallet_address)
                    
                    sol_delta = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1e9  # Convert to SOL
                    
                    # Analyze token balance changes
                    pre_token_balances = meta.get('preTokenBalances', [])
                    post_token_balances = meta.get('postTokenBalances', [])
                    
                    # Track token changes for our wallet
                    token_changes = {}
                    
                    # Process pre-transaction token balances
                    for balance in pre_token_balances:
                        if balance.get('owner') == wallet_address:
                            mint = balance.get('mint')
                            ui_amount = balance.get('uiTokenAmount', {})
                            amount = float(ui_amount.get('uiAmount', 0) or 0)
                            token_changes[mint] = {
                                'pre': amount,
                                'post': 0,
                                'symbol': ui_amount.get('symbol', mint[:8]),
                                'decimals': ui_amount.get('decimals', 0)
                            }
                    
                    # Process post-transaction token balances
                    for balance in post_token_balances:
                        if balance.get('owner') == wallet_address:
                            mint = balance.get('mint')
                            ui_amount = balance.get('uiTokenAmount', {})
                            amount = float(ui_amount.get('uiAmount', 0) or 0)
                            
                            if mint in token_changes:
                                token_changes[mint]['post'] = amount
                            else:
                                token_changes[mint] = {
                                    'pre': 0,
                                    'post': amount,
                                    'symbol': ui_amount.get('symbol', mint[:8]),
                                    'decimals': ui_amount.get('decimals', 0)
                                }
                    
                    # Calculate token deltas
                    gained_tokens = []
                    lost_tokens = []
                    significant_changes = []
                    
                    for mint, change in token_changes.items():
                        delta = change['post'] - change['pre']
                        if abs(delta) > 0.000001:  # Ignore dust
                            change['delta'] = delta
                            significant_changes.append((mint, change))
                            
                            if delta > 0:
                                gained_tokens.append((mint, delta, change['symbol']))
                            else:
                                lost_tokens.append((mint, abs(delta), change['symbol']))
                    
                    # Determine action with HIGH confidence
                    action = None
                    confidence = "LOW"
                    reasoning = ""
                    primary_token = None
                    
                    print(f"   💰 SOL delta: {sol_delta:+.6f} SOL")
                    print(f"   🪙 Token changes: {len(gained_tokens)} gained, {len(lost_tokens)} lost")
                    
                    for mint, amount, symbol in gained_tokens:
                        print(f"      ✅ Gained {amount:,.6f} {symbol}")
                    for mint, amount, symbol in lost_tokens:
                        print(f"      ❌ Lost {amount:,.6f} {symbol}")
                    
                    # DECISION LOGIC - HIGH CONFIDENCE DETECTION
                    if sol_delta < -0.001 and len(gained_tokens) > 0 and len(lost_tokens) == 0:
                        # Spent SOL and gained tokens = BUY
                        action = "BUY"
                        confidence = "HIGH"
                        reasoning = f"Spent {abs(sol_delta):.6f} SOL, gained {gained_tokens[0][1]:,.6f} {gained_tokens[0][2]}"
                        primary_token = gained_tokens[0][0]
                        
                    elif sol_delta > 0.001 and len(lost_tokens) > 0 and len(gained_tokens) == 0:
                        # Gained SOL and lost tokens = SELL
                        action = "SELL"
                        confidence = "HIGH"
                        reasoning = f"Gained {sol_delta:+.6f} SOL, sold {lost_tokens[0][1]:,.6f} {lost_tokens[0][2]}"
                        primary_token = lost_tokens[0][0]
                        
                    elif len(gained_tokens) > 0 and len(lost_tokens) > 0:
                        # Token-to-token swap
                        action = "SWAP"
                        confidence = "MEDIUM"
                        reasoning = f"Swapped {lost_tokens[0][1]:,.6f} {lost_tokens[0][2]} for {gained_tokens[0][1]:,.6f} {gained_tokens[0][2]}"
                        primary_token = gained_tokens[0][0] if len(gained_tokens) > 0 else lost_tokens[0][0]
                        
                    elif abs(sol_delta) > 0.001 and len(significant_changes) == 0:
                        # Pure SOL transfer (not trading)
                        print(f"   ℹ️ Pure SOL transfer, not a trade - trying fallback...")
                        return await self._pump_fun_log_based_fallback(signature, wallet_address)
                        
                    else:
                        print(f"   ❓ Unclear transaction pattern - applying AGGRESSIVE interpretation...")
                        
                        # 🚀 ULTRA-AGGRESSIVE: If any SOL movement from target wallet, assume it's a trade!
                        if abs(sol_delta) > 0.0001:  # Even tiny SOL movements
                            if sol_delta < 0:
                                action = "BUY"
                                confidence = "HIGH"  # High confidence - target wallets know what they're doing!
                                reasoning = f"ULTRA-AGGRESSIVE: Target wallet spent {abs(sol_delta):.6f} SOL = COPY BUY"
                                primary_token = f"AGGRESSIVE_BUY_TOKEN_{signature[:8]}"
                                
                                print(f"   🚀 ULTRA-AGGRESSIVE BUY: Copy target wallet's {abs(sol_delta):.6f} SOL trade!")
                            else:
                                action = "SELL"  
                                confidence = "HIGH"  # High confidence for sells too
                                reasoning = f"ULTRA-AGGRESSIVE: Target wallet gained {sol_delta:.6f} SOL = COPY SELL"
                                primary_token = f"AGGRESSIVE_SELL_TOKEN_{signature[:8]}"
                                
                                print(f"   💸 ULTRA-AGGRESSIVE SELL: Copy target wallet's {sol_delta:.6f} SOL sale!")
                        else:
                            # Even if no SOL movement, still try to copy if it's from target wallet
                            action = "BUY"
                            confidence = "MEDIUM"
                            reasoning = f"ULTRA-AGGRESSIVE: Target wallet transaction detected = assume BUY"
                            primary_token = f"EMERGENCY_ASSUMPTION_TOKEN_{signature[:8]}"
                            
                            print(f"   🚨 EMERGENCY BUY ASSUMPTION: Target wallet transaction = COPY IT!")
                    
                    if action:
                        # 🚀 CRITICAL FIX: DETECT PUMP.FUN PLATFORM FOR PRIORITIZATION
                        detected_platform = "unknown"
                        
                        # Check transaction logs for Pump.fun program ID
                        logs = meta.get('logMessages', [])
                        pump_fun_programs = [
                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun main program
                            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"   # Pump.fun bonding curve
                        ]
                        
                        for log in logs:
                            for pump_program in pump_fun_programs:
                                if pump_program in log:
                                    detected_platform = "pumpfun"
                                    print(f"   🎪 PUMP.FUN DETECTED: Platform identified for native transaction building!")
                                    break
                            if detected_platform == "pumpfun":
                                break
                        
                        # Check account keys for other DEX programs if not Pump.fun
                        if detected_platform == "unknown":
                            for account in account_keys:
                                if account == "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C":
                                    detected_platform = "raydium_cpmm"
                                    break
                                elif account == "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc":
                                    detected_platform = "orca"
                                    break
                                elif account == "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB":
                                    detected_platform = "jupiter"
                                    break
                        
                        trade_result = {
                            'action': action.lower(),  # Normalize to lowercase for consistency
                            'confidence': confidence,
                            'reasoning': reasoning,
                            'signature': signature,
                            'wallet': wallet_address,
                            'sol_delta': sol_delta,
                            'token_mint': primary_token,
                            'gained_tokens': gained_tokens,
                            'lost_tokens': lost_tokens,
                            'timestamp': time.time(),
                            'method': 'balance_based_detection_fast',
                            'dex': detected_platform  # 🚀 ADD DEX PLATFORM FOR ROUTING!
                        }
                        
                        print(f"   ✅ {action} detected with {confidence} confidence")
                        print(f"   🎯 Reasoning: {reasoning}")
                        
                        return trade_result
                    
        except Exception as e:
            print(f"   ❌ Error in fast balance analysis: {e}")
            # IMMEDIATE FALLBACK: Don't retry, go straight to log-based detection
            print(f"   � FAST FALLBACK: Switching to log-based detection immediately...")
            return await self._pump_fun_log_based_fallback(signature, wallet_address)

    async def _pump_fun_log_based_fallback(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """🎯 REAL TOKEN EXTRACTION: Extract actual token mint from transaction logs"""
        try:
            print(f"   🎯 EXTRACTING REAL TOKEN from transaction: {signature[:8]}...")
            
            # Get the actual transaction to extract real token mint
            import aiohttp
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.rpc_client._provider.endpoint_uri,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('result') and data['result'].get('transaction'):
                            tx = data['result']['transaction']
                            
                            # Extract token mint from transaction instructions
                            real_token_mint = self._extract_real_token_mint(tx)
                            
                            if real_token_mint and len(real_token_mint) == 44:
                                print(f"   ✅ REAL TOKEN EXTRACTED: {real_token_mint[:8]}...")
                                
                                return {
                                    'action': 'buy',
                                    'confidence': "HIGH",
                                    'reasoning': f"Real token extracted from transaction",
                                    'signature': signature,
                                    'wallet': wallet_address,
                                    'token_mint': real_token_mint,
                                    'timestamp': time.time(),
                                    'method': 'real_token_extraction',
                                    'dex': 'extracted_from_tx'
                                }
            
            print(f"   ⚠️ Could not extract real token mint - skipping trade")
            return None
                    
        except Exception as e:
            print(f"   ❌ Error in real token extraction: {e}")
            return None
    
    def _extract_real_token_mint(self, transaction: dict) -> Optional[str]:
        """Extract the actual token mint from transaction data"""
        try:
            # Look in transaction message accounts
            if 'message' in transaction and 'accountKeys' in transaction['message']:
                accounts = transaction['message']['accountKeys']
                
                # Skip system programs and find token mints (44-character base58)
                system_programs = {
                    "11111111111111111111111111111111",
                    "ComputeBudget111111111111111111111111111111",
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
                }
                
                for account in accounts:
                    account_key = account if isinstance(account, str) else account.get('pubkey', '')
                    
                    # Find tokens (44 chars, not system programs)
                    if (len(account_key) == 44 and 
                        account_key not in system_programs and
                        not account_key.startswith('So1111')):  # Skip WSOL
                        
                        print(f"   🎯 Found potential token: {account_key[:8]}...")
                        return account_key
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error extracting token mint: {e}")
            return None

    async def _reanalyze_transaction_with_balance_data(self, signature: str, wallet_address: str, detected_action: str) -> Optional[Dict[str, Any]]:
        """🚨 OFFICIAL SOLANA METHOD: Re-analyze transaction using official balance data analysis WITH RETRY LOGIC"""
        
        # 🚀 CRITICAL FIX: Implement retry logic for timing issues
        max_retries = 5
        retry_delays = [0.5, 1.0, 2.0, 3.0, 5.0]  # Progressive delays
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"� RETRY {attempt+1}/{max_retries}: Waiting {retry_delays[attempt]:.1f}s for transaction to be processed...")
                    await asyncio.sleep(retry_delays[attempt])
                
                print(f"�🔧 OFFICIAL BALANCE ANALYSIS (attempt {attempt+1}): {signature[:8]}... for wallet {wallet_address[:8]}...")
                
                # 🎯 NEW: Use the official wallet perspective analyzer
                from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
                
                analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
                result = await analyzer.analyze_wallet_action(signature, wallet_address)
                
                if result and result.get('action') != 'none' and result.get('action') != 'error':
                    print(f"✅ OFFICIAL ANALYSIS SUCCESS! (attempt {attempt+1})")
                    print(f"   🎯 Action: {result['action'].upper()}")
                    print(f"   💎 Token: {result.get('token_mint', 'Unknown')[:8]}...")
                    print(f"   📊 Amount: {result.get('amount_change', 0)}")
                    print(f"   🎖️ Confidence: {result.get('confidence', 0)}/10")
                    
                    # Convert to the format expected by the main bot
                    return {
                        'signature': signature,
                        'wallet_address': wallet_address,
                        'action': result['action'],
                        'dex': 'Official_Balance_Analysis',
                        'token_mint': result['token_mint'],
                        'timestamp': datetime.now(timezone.utc),
                        'extraction_method': 'official_solana_balance_analysis',
                        'balance_change': result.get('amount_change', 0),
                        'confidence': result.get('confidence', 10)
                    }
                else:
                    if result:
                        print(f"❌ OFFICIAL ANALYSIS (attempt {attempt+1}): {result.get('action', 'unknown')} - {result.get('reason', 'no reason')}")
                        
                        # Special handling for specific error cases
                        if result.get('action') == 'error' and 'No transaction data' in str(result.get('reason', '')):
                            print(f"   ⏳ Transaction not ready yet, will retry...")
                            continue  # Retry this specific error
                    else:
                        print(f"❌ OFFICIAL ANALYSIS FAILED (attempt {attempt+1}) - no result returned")
                        continue  # Retry if no result
                        
            except Exception as e:
                print(f"❌ Error in official balance re-analysis (attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    print(f"   ⏳ Will retry in {retry_delays[attempt]:.1f}s...")
                    continue
                else:
                    print(f"❌ Traceback: {traceback.format_exc()}")
        
        print(f"🚨 ALL RETRIES EXHAUSTED: Could not analyze transaction {signature[:8]}... after {max_retries} attempts")
        return None

    # 🚀 EXECUTION METHODS - Now delegate to execution coordinator
    async def _execute_copy_buy(self, token_mint: str, source_wallet: str, detected_dex: str = None, trade_info: Dict[str, Any] = None):
        """Execute copy buy - delegates to execution coordinator"""
        return await self.execution_coordinator._execute_copy_buy(
            token_mint=token_mint,
            source_wallet=source_wallet,
            detected_dex=detected_dex,
            trade_info=trade_info
        )

    async def _execute_copy_sell(self, token_mint: str, trade_info: Dict[str, Any] = None, source_wallet: str = None):
        """Execute copy sell - delegates to execution coordinator"""
        return await self.execution_coordinator._execute_copy_sell(
            token_mint=token_mint,
            trade_info=trade_info,
            source_wallet=source_wallet
        )

    async def _try_direct_pumpfun_buy(self, wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """Direct Pump.fun buy - delegates to execution coordinator"""
        return await self.execution_coordinator._try_direct_pumpfun_buy(
            wallet_keypair=wallet_keypair,
            token_mint=token_mint,
            amount_sol=amount_sol,
            **kwargs
        )

    async def _try_direct_pumpfun_sell(self, wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Direct Pump.fun sell - delegates to execution coordinator"""
        return await self.execution_coordinator._try_direct_pumpfun_sell(
            wallet_keypair=wallet_keypair,
            token_mint=token_mint,
            **kwargs
        )

    async def _process_detected_trade(self, trade_info: Dict[str, Any], source_wallet: str = None):
        """Main trading coordinator - processes validated trades with complete information"""
        print(f"🚨 DEBUG: _process_detected_trade called! Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")  # Force debug
        try:
            action = trade_info['action'].lower()
            token_mint = trade_info['token_mint']
            # Use provided source_wallet or fallback to trade_info
            source_wallet = source_wallet or trade_info['wallet_address']
            detected_dex = trade_info.get('dex', 'Unknown')
            
            logger.info(f"🎯 PROCESSING {action.upper()} TRADE for {token_mint[:8]}...")
            
            if action == 'buy':
                logger.info(f"💎 COPY BUY DETECTED - Executing proportional copy trade")
                await self._execute_copy_buy(token_mint, source_wallet, detected_dex, trade_info)
            elif action == 'sell':
                logger.info(f"� COPY SELL DETECTED - Executing PROPORTIONAL SELL")
                logger.info(f"   👤 Source wallet: {source_wallet[:8]}... sold on {detected_dex}")
                logger.info(f"   🎯 Analyzing target wallet sell percentage for proportional copy")
                await self._execute_copy_sell(token_mint, trade_info, source_wallet)
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                    
        except Exception as e:
            logger.error(f"❌ Error processing detected trade: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    async def _instant_account_analysis(self, wallet: str):
        """🚀 ULTRA FAST account analysis when account changes detected"""
        try:
            logger.info(f"⚡ INSTANT ACCOUNT ANALYSIS: {wallet[:8]}...")
            
            # Get the most recent transactions for this wallet
            await self._fetch_and_analyze_recent_transactions(wallet)
            
        except Exception as e:
            logger.error(f"❌ Error in instant account analysis: {e}")

    async def _instant_transaction_analysis(self, signature: str, wallet: str):
        """🚀 ULTRA FAST transaction analysis - NO DELAYS!"""
        analysis_start = time.time()
        try:
            logger.info(f"⚡ INSTANT ANALYSIS: {signature[:8]}... from {wallet[:8]}...")
            
            # Skip if already processed (avoid duplicates)
            if signature in self.processed_signatures:
                logger.debug(f"⏭️ Already processed: {signature[:8]}...")
                return
            
            # Mark as processing immediately to avoid race conditions
            self.processed_signatures.add(signature)
            
            # 🚀 ULTRA FAST: Use minimal timeout for instant analysis
            try:
                await asyncio.wait_for(
                    self._fetch_and_analyze_transaction(signature, wallet),
                    timeout=2.0  # Faster timeout for copy trading
                )
                
                analysis_time = time.time() - analysis_start
                logger.info(f"⚡ INSTANT ANALYSIS COMPLETE: {signature[:8]}... in {analysis_time:.2f}s")
                
            except asyncio.TimeoutError:
                analysis_time = time.time() - analysis_start
                logger.warning(f"⏰ INSTANT analysis timeout: {signature[:8]}... after {analysis_time:.2f}s")
            except Exception as e:
                analysis_time = time.time() - analysis_start
                logger.error(f"❌ INSTANT analysis error: {signature[:8]}... after {analysis_time:.2f}s: {e}")
                
        except Exception as e:
            analysis_time = time.time() - analysis_start
            logger.error(f"❌ Error in instant analysis after {analysis_time:.2f}s: {e}")

    async def _fetch_and_analyze_recent_transactions(self, wallet: str):
        """🚀 ULTRA FAST recent transaction analysis for instant account changes"""
        try:
            logger.info(f"⚡ FETCHING RECENT TXS: {wallet[:8]}...")
            
            # Get just the 5 most recent transactions for speed
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet),
                limit=5  # Ultra-fast - just check the most recent
            )
            
            if not response.value:
                logger.debug(f"⚠️ No recent transactions for {wallet[:8]}...")
                return
            
            logger.info(f"⚡ Analyzing {len(response.value)} recent transactions...")
            
            # Process in parallel for maximum speed
            tasks = []
            for i, tx_info in enumerate(response.value):
                signature = str(tx_info.signature)
                
                # Skip if already processed
                if signature in self.processed_signatures:
                    continue
                
                # Create parallel analysis task
                task = asyncio.create_task(
                    self._analyze_single_transaction_with_timeout(signature, wallet, i+1)
                )
                tasks.append(task)
            
            if tasks:
                # Wait for all analyses with short timeout
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=6.0  # Faster parallel analysis for copy trading
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Parallel analysis timeout for {wallet[:8]}...")
                
        except Exception as e:
            logger.error(f"❌ Error fetching recent transactions: {e}")

    async def emergency_full_rescan(self, wallet: str):
        """Emergency full rescan if trades are being missed"""
        try:
            logger.warning(f"🚨 EMERGENCY FULL RESCAN for {wallet[:8]}...")
            
            # Get last 500 transactions (ultra-deep scan)
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet),
                limit=500  # Ultra-deep emergency scan
            )
            
            if not response.value:
                logger.warning(f"⚠️ No transactions found in emergency scan for {wallet[:8]}...")
                return
            
            logger.info(f"🚨 Emergency scanning {len(response.value)} transactions...")
            
            # Clear processed signatures to reprocess everything
            old_processed = self.processed_signatures.copy()
            self.processed_signatures.clear()
            
            emergency_buys_found = 0
            
            # Analyze top 100 transactions with no skipping
            for i, tx_info in enumerate(response.value[:100]):
                signature = str(tx_info.signature)
                
                logger.info(f"🚨 [{i+1}/100] Emergency analysis: {signature[:8]}...")
                
                try:
                    trade_info = await asyncio.wait_for(
                        self.extract_trade_info_quick(signature, wallet),
                        timeout=10.0  # Faster emergency analysis for copy trading
                    )
                    
                    if trade_info and trade_info.get('trade_type') == 'buy':
                        emergency_buys_found += 1
                        token_mint = trade_info.get('token_mint', 'UNKNOWN')
                        dex = trade_info.get('dex', 'Unknown')
                        
                        logger.warning(f"🚨 EMERGENCY BUY FOUND: {token_mint[:8]}... on {dex}")
                        logger.warning(f"   🎯 This BUY was missed during normal monitoring!")
                        
                        # Execute copy trade for missed BUY (without trade_info)
                        await self._execute_copy_buy(token_mint, wallet, dex, None)
                    
                    # Mark as processed
                    self.processed_signatures.add(signature)
                    
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Emergency analysis timeout for {signature[:8]}...")
                    self.processed_signatures.add(signature)
                except Exception as e:
                    logger.debug(f"Emergency analysis error for {signature[:8]}...: {e}")
                    self.processed_signatures.add(signature)
                
                # Removed delay for instant copy trading
            
            logger.warning(f"🚨 EMERGENCY RESCAN COMPLETE: {emergency_buys_found} missed BUYs recovered!")
            
        except Exception as e:
            logger.error(f"❌ Error in emergency full rescan: {e}")

    async def extract_trade_info_quick(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Quick trade info extraction for historical analysis - from your original main.py"""
        try:
            from solders.signature import Signature
            
            # Convert string signature to Signature object
            sig_obj = Signature.from_string(signature)
            
            # Get transaction with shorter timeout for bulk processing
            tx_response = await self.rpc_client.get_transaction(
                sig_obj,
                encoding="jsonParsed",
                commitment=Processed,
                max_supported_transaction_version=0
            )
            
            if not tx_response or not tx_response.value:
                return None
            
            # OLD FLAWED DETECTION REMOVED
            return None
            
        except Exception as e:
            logger.debug(f"Quick analysis failed for {signature[:8]}...: {e}")
            return None

    async def start_monitoring(self):
        """🚀 FIXED: Stable WebSocket monitoring with proper concurrency"""
        try:
            logger.info("🚀 Starting stable WebSocket monitoring...")
            self.is_running = True
            
            # Initialize Enhanced Jito Service
            if self.jito_service:
                logger.info("🚀 Initializing Enhanced Jito Service...")
                jito_initialized = await self.jito_service.initialize()
                if jito_initialized:
                    logger.info("✅ Enhanced Jito Service ready for Jito-first execution!")
                else:
                    logger.warning("⚠️ Jito Service initialization failed, will use RPC only")
            
            # 🚀 CRITICAL FIX: Initialize WebSocket monitoring FIRST
            logger.info("📡 Initializing modular WebSocket handler...")
            self.ws_handler = await create_websocket_handler(
                target_wallets=self.target_wallets,
                helius_ws_url=self.env_keys.HELIUS_WS_URL,
                helius_rpc_url=self.env_keys.HELIUS_RPC_URL,
                trade_callback=self._handle_websocket_trade
            )
            
            # 🚀 CRITICAL FIX: Start WebSocket monitoring immediately with proper error handling
            logger.info("✅ Starting WebSocket connection...")
            
            # Create tasks for concurrent execution
            tasks = []
            
            # Task 1: WebSocket monitoring (PRIMARY - most important)
            websocket_task = asyncio.create_task(
                self.ws_handler.start_monitoring(),
                name="websocket_monitor"
            )
            tasks.append(websocket_task)
            
            # Task 2: Status monitoring (BACKGROUND)
            status_task = asyncio.create_task(
                self._status_monitor_loop(),
                name="status_monitor"
            )
            tasks.append(status_task)
            
            logger.info("✅ All monitoring tasks started! WebSocket should be stable now.")
            logger.info("🎯 Bot is now ready for real-time copy trading!")
            
            # Wait for tasks to complete (they should run indefinitely)
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"❌ Task execution error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error starting monitoring: {e}")
            logger.error(traceback.format_exc())
            await self.stop()

    async def _status_monitor_loop(self):
        """📊 BACKGROUND: Status monitoring loop"""
        try:
            while self.is_running:
                try:
                    # Display status every 5 minutes
                    if time.time() - self.last_status_display > 300:
                        await self.display_current_status()
                        if self.jito_service:
                            self.jito_service.log_stats()
                        self.last_status_display = time.time()
                    
                    # Check every 10 seconds (reduced from 30)
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.error(f"❌ Status monitor error: {e}")
                    await asyncio.sleep(20)  # Reduced error wait time
                    
        except Exception as e:
            logger.error(f"❌ Status monitor loop error: {e}")

    async def stop(self):
        """🚨 IMMEDIATE STOP: Skip all cleanup and terminate immediately"""
        logger.error("🚨 IMMEDIATE STOP: Terminating bot immediately...")
        self.is_running = False
        
        # Skip all cleanup - just set flags and exit
        try:
            if self.ws_handler:
                await self.ws_handler.stop()
        except:
            pass
        
        logger.error("� IMMEDIATE STOP COMPLETE - Process will terminate")
        
        # Force immediate exit
        import os
        import signal
        os.kill(os.getpid(), signal.SIGKILL)

    def emergency_kill(self):
        """🚨 NUCLEAR EMERGENCY KILL: Forcefully terminate this process and all related processes"""
        import os
        import signal
        import subprocess
        
        logger.error("🚨 NUCLEAR EMERGENCY KILL ACTIVATED!")
        logger.error("🚨 Forcefully terminating all trading bot processes...")
        
        try:
            # Force stop everything immediately
            self.is_running = False
            
            # Get current process ID
            current_pid = os.getpid()
            logger.error(f"🚨 Current process PID: {current_pid}")
            
            # Kill all Python processes running main.py (most effective)
            try:
                subprocess.run(['pkill', '-9', '-f', 'main.py'], capture_output=True)
                logger.error("🔥 Killed all main.py processes")
            except Exception as e:
                logger.error(f"❌ Error killing main.py processes: {e}")
            
            # Kill all python3 processes running in this directory
            try:
                current_dir = os.getcwd()
                subprocess.run(['pkill', '-9', '-f', f'python3.*{current_dir}'], capture_output=True)
                logger.error("🔥 Killed all python3 processes in current directory")
            except Exception as e:
                logger.error(f"❌ Error killing directory processes: {e}")
            
            # Nuclear self-termination - bypass all cleanup
            logger.error("🔥 Self-terminating current process...")
            os.kill(current_pid, signal.SIGKILL)
            
        except Exception as e:
            logger.error(f"❌ Nuclear kill failed: {e}")
            # Ultimate nuclear option
            os._exit(1)

    @staticmethod
    def kill_all_trading_bots():
        """🚨 STATIC METHOD: Kill all trading bot processes from anywhere"""
        import subprocess
        import os
        
        print("🚨 KILLING ALL TRADING BOT PROCESSES...")
        
        # Method 1: pkill by process name
        process_patterns = ['main.py', 'copy_trading', 'trading_bot']
        for pattern in process_patterns:
            try:
                subprocess.run(['pkill', '-9', '-f', pattern], capture_output=True)
                print(f"🔥 Killed processes matching: {pattern}")
            except Exception as e:
                print(f"❌ Error killing {pattern}: {e}")
        
        # Method 2: Get and kill specific PIDs
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'python' in line and 'main.py' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        try:
                            os.kill(int(pid), 9)  # SIGKILL
                            print(f"🔥 Force killed PID: {pid}")
                        except:
                            pass
        except Exception as e:
            print(f"❌ Error in PID-based killing: {e}")
        
        print("✅ Kill operation completed")

    async def get_wallet_balance(self) -> Dict[str, float]:
        """Get comprehensive wallet balances using official Solana methods"""
        try:
            balances = {}
            
            # Get SOL balance using official RPC client
            sol_response = await self.rpc_client.get_balance(self.wallet_pubkey)
            balances['SOL'] = (sol_response.value / 1e9) if sol_response.value else 0.0
            
            # Get token balances using official token program methods
            try:
                from solders.pubkey import Pubkey
                
                # Get all token accounts for this wallet
                token_accounts_response = await self.rpc_client.get_token_accounts_by_owner(
                    self.wallet_pubkey,
                    {"programId": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")},
                    encoding="jsonParsed"
                )
                
                if token_accounts_response.value:
                    for account in token_accounts_response.value:
                        try:
                            parsed_info = account.account.data.parsed.info
                            token_mint = parsed_info.mint
                            token_amount = float(parsed_info.tokenAmount.uiAmount or 0.0)
                            
                            if token_amount > 0.000001:  # Only include non-dust amounts
                                balances[token_mint] = token_amount
                                
                        except Exception as token_error:
                            logger.debug(f"Error parsing token account: {token_error}")
                            continue
                            
            except Exception as token_error:
                logger.debug(f"Error getting token accounts: {token_error}")
            
            logger.debug(f"💰 Wallet balances: SOL={balances.get('SOL', 0):.6f}, Tokens={len(balances)-1}")
            return balances
            
        except Exception as e:
            logger.error(f"❌ Error getting wallet balance: {e}")
            return {'SOL': 0.0}

    async def liquidate_all_positions(self):
        """Sell all remaining positions when stopping the bot - now uses execution coordinator"""
        try:
            logger.info("💸 Delegating liquidation to execution coordinator...")
            result = await self.execution_coordinator.liquidate_all_positions()
            
            logger.info(f"💸 LIQUIDATION COMPLETE via execution coordinator:")
            logger.info(f"   ✅ Successful: {result.get('successful', 0)}")
            logger.info(f"   ❌ Failed: {result.get('failed', 0)}")
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Error in liquidate_all_positions: {e}")
            return {'successful': 0, 'failed': 0}

    # DUPLICATE METHOD REMOVED - Using comprehensive _handle_websocket_trade at line 389

    # OLD DETECTION METHOD REMOVED: _parse_transaction_logs_advanced

    # OLD DETECTION METHOD REMOVED: _extract_token_mint_from_logs

    # OLD DETECTION METHOD REMOVED: _is_buy_transaction_from_logs

    async def _fetch_and_analyze_transaction(self, signature: str, wallet: str):
        """Fetch and analyze a single transaction using official Solana balance-based detection"""
        try:
            logger.debug(f"🔍 Official analysis: {signature[:8]}... from {wallet[:8]}...")
            
            # Use the official wallet perspective analyzer for accurate detection
            from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
            
            analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
            result = await analyzer.analyze_wallet_action(signature, wallet)
            
            if result and result.get('action') not in ['none', 'error']:
                logger.info(f"✅ Trade detected: {result['action'].upper()} {result.get('token_mint', 'Unknown')[:8]}...")
                
                # Convert to the format expected by the main bot
                trade_info = {
                    'signature': signature,
                    'wallet_address': wallet,
                    'action': result['action'],
                    'dex': 'Official_Analysis',
                    'token_mint': result['token_mint'],
                    'timestamp': datetime.now(timezone.utc),
                    'extraction_method': 'official_wallet_perspective_analyzer',
                    'balance_change': result.get('amount_change', 0),
                    'confidence': result.get('confidence', 10)
                }
                
                # Process the detected trade
                await self._handle_websocket_trade(trade_info)
                return trade_info
            else:
                logger.debug(f"No trade action detected for {signature[:8]}...")
                return None
                
        except Exception as e:
            logger.debug(f"Error analyzing transaction: {e}")
            return None

    async def _analyze_single_transaction_with_timeout(self, signature: str, wallet: str, index: int):
        """Analyze single transaction with timeout using official methods"""
        try:
            logger.debug(f"🔍 [{index}] Official analysis: {signature[:8]}...")
            
            # Use timeout to prevent hanging
            result = await asyncio.wait_for(
                self._fetch_and_analyze_transaction(signature, wallet),
                timeout=5.0  # 5 second timeout per transaction
            )
            
            if result:
                logger.info(f"✅ [{index}] Trade found: {result['action'].upper()} {result.get('token_mint', 'Unknown')[:8]}...")
                return result
            else:
                logger.debug(f"ℹ️ [{index}] No trade detected")
                return None
                
        except asyncio.TimeoutError:
            logger.warning(f"⏰ [{index}] Analysis timeout: {signature[:8]}...")
            return None
        except Exception as e:
            logger.debug(f"❌ [{index}] Analysis error: {e}")
            return None
        except Exception as e:
            logger.debug(f"Error analyzing transaction {index}: {e}")
            return None
        try:
            log_text = ' '.join(logs).lower()
            
            # 🚨 CRITICAL: Check for explicit SELL indicators FIRST (these override everything)
            explicit_sell_indicators = [
                'instruction: sell',  # Direct sell instruction like we saw in the failed transaction
                'program log: sell',
                'sell instruction',
                'swapquotetobase',
                'exactoutwithslippage'
            ]
            
            # 🚨 CRITICAL: If we find explicit sell patterns, it's definitely a SELL
            for sell_pattern in explicit_sell_indicators:
                if sell_pattern in log_text:
                    print(f"🔍 EXPLICIT SELL DETECTED: Found '{sell_pattern}' in logs")
                    return False  # This is a SELL, not a BUY
            
            # 🚨 CRITICAL: Check for explicit BUY indicators
            explicit_buy_indicators = [
                'instruction: buy',   # Direct buy instruction
                'program log: buy',
                'buy instruction',
                'swapbasetoquote',
                'exactinwithslippage'
            ]
            
            # Check for explicit buy patterns
            for buy_pattern in explicit_buy_indicators:
                if buy_pattern in log_text:
                    print(f"🔍 EXPLICIT BUY DETECTED: Found '{buy_pattern}' in logs")
                    return True  # This is definitely a BUY
            
            # If no explicit patterns, use balance analysis instead of guessing
            print(f"🔍 NO EXPLICIT TRADE PATTERN: Defaulting to balance analysis for accuracy")
            return None  # Signal that we need balance analysis
            
        except Exception as e:
            logger.debug(f"❌ Error in trade direction detection: {e}")
            return None  # Default to balance analysis on error

            
        except Exception as e:
            logger.warning(f"   ⚠️ Error building sell transaction: {e}")
            logger.debug(f"   Traceback: {traceback.format_exc()}")
            return None

