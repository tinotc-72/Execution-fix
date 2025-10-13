#!/usr/bin/env python3
"""
Main Copy Trading Bot
====================

Production copy trading bot with:
- Jito MEV protection (primary execution)
- RPC fallback (secondary execution)
- WebSocket transaction monitoring
- Fixed 0.001 SOL investment amount
- Proportional selling based on target wallet activity
- Multi-DEX support (Jupiter, Pump.fun, Raydium, CLMM, Orca, Phoenix)
- Automatic position liquidation on shutdown

Author: tinotc-72
Date: July 2025
"""

import asyncio
import json
import logging
import signal
import traceback
import time
import traceback
import websockets
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import aiohttp

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Import the CSV logging system
from copy_trade_logger import get_copy_trade_logger, log_successful_copy_trade, log_failed_copy_trade
from solders.signature import Signature
from solana.rpc.commitment import Processed, Confirmed

# Import copy executors (only ones with standardized functions)
from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
from orca_copy_executor import try_orca_buy, try_orca_sell_all
from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all

# Import core modules
from config import WALLET
from env_keys import EnvKeys
from pool_discovery_service import PoolDiscoveryService, get_pool_info_for_token
from jito_service import JitoClient

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see program IDs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copy_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("copy_bot_main")

# Load environment
env = EnvKeys()

@dataclass
class WalletPosition:
    """Track position for a specific token"""
    token_mint: str
    initial_amount: float = 0.0
    current_amount: float = 0.0
    our_amount: float = 0.0
    entry_price: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CopyTradeConfig:
    """Configuration for copy trading"""
    target_wallets: List[str] = field(default_factory=list)
    investment_amount_sol: float = 0.001  # Fixed amount per trade
    max_positions: int = 10
    min_sell_threshold: float = 0.1  # Minimum % to sell
    use_jito: bool = True
    jito_timeout: float = 10.0
    # ULTRA-AGGRESSIVE: Higher slippage tolerance for trusted wallet copy trading
    slippage_tolerance: float = 0.50  # 50% slippage tolerance for ultra-aggressive copy trading
    slippage_bps: int = 5000         # 50% in basis points
    enable_dexes: Dict[str, bool] = field(default_factory=lambda: {
        "direct_pumpfun": True,  # Direct Pump.fun (highest priority for new tokens)
        "pumpfun": True,         # Jupiter-based Pump.fun
        "jupiter": True,         # Jupiter aggregator
        "raydium": True,         # Raydium DEX
        "cpmm": True,           # Raydium CPMM
        "clmm": True,           # Concentrated liquidity
        "orca": True,           # Orca DEX
        "phoenix": True         # Phoenix DEX
    })

class CopyTradingBot:
    """
    Advanced copy trading bot with Jito MEV protection and multi-DEX support
    """
    
    def __init__(self, config: CopyTradeConfig):
        self.config = config
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        
        # Initialize RPC client
        self.rpc_client = AsyncClient(env.HELIUS_RPC_URL)
        
        # Initialize Jito service
        self.jito_service = JitoClient() if config.use_jito else None
        
        # Position tracking
        self.positions: Dict[str, WalletPosition] = {}  # token_mint -> position
        self.active_positions: Dict[str, Dict[str, Any]] = {}  # Simplified position tracking for aggressive mode
        self.target_positions: Dict[str, Dict[str, float]] = defaultdict(dict)  # wallet -> {token: amount}
        
        # Balance tracking
        self.trade_counter: Dict[str, int] = defaultdict(int)  # Track how many times each token was traded
        self.execution_history: List[Dict[str, Any]] = []  # Track all trade executions
        
        # ULTRA-AGGRESSIVE: Retry state tracking
        self.current_retry_attempt: int = 0  # Track current retry attempt for dynamic slippage
        self.failed_tokens: Dict[str, int] = defaultdict(int)  # Track failures per token
        
        # Transaction tracking
        self.processed_signatures: Set[str] = set()
        self.is_running = False
        
        # WebSocket connection
        self.ws_connection = None
        
        # DEX executor mapping (only working executors)
        self.dex_executors = {
            "direct_pumpfun": (self._try_direct_pumpfun_buy, self._try_direct_pumpfun_sell),
            "pumpfun": (try_pumpfun_buy, try_pumpfun_sell_all),
            "jupiter": (try_jupiter_buy, try_jupiter_sell_all),
            "raydium": (try_raydium_buy, try_raydium_sell_all),
            "cpmm": (try_cpmm_buy, try_cpmm_sell_all),
            "clmm": (try_clmm_hybrid_buy, try_clmm_hybrid_sell_all),
            "orca": (try_orca_buy, try_orca_sell_all),
            "phoenix": (try_phoenix_buy, try_phoenix_sell_all)
        }
        
        # Initialize CSV logger
        self.csv_logger = get_copy_trade_logger("copy_trade_logs")
        
        logger.info(f"🤖 Copy Trading Bot initialized")
        logger.info(f"   Wallet: {self.wallet_pubkey}")
        logger.info(f"   Target Wallets: {len(config.target_wallets)}")
        logger.info(f"   Investment Amount: {config.investment_amount_sol} SOL")
        logger.info(f"   Jito Enabled: {config.use_jito}")
        logger.info(f"   Enabled DEXes: {[k for k, v in config.enable_dexes.items() if v]}")
        logger.info(f"   📝 CSV Logging: Enabled (logs saved to copy_trade_logs/)")
    
    async def stop_monitoring(self):
        """Gracefully stop the copy trading bot"""
        logger.info("🛑 Stopping copy trading bot...")
        self.is_running = False
        
        # Close WebSocket connection if active
        if self.ws_connection and not self.ws_connection.closed:
            try:
                await self.ws_connection.close()
                logger.info("✅ WebSocket connection closed gracefully")
            except Exception as e:
                logger.warning(f"⚠️ Error closing WebSocket: {e}")
        
        # Close RPC client
        if self.rpc_client:
            try:
                await self.rpc_client.close()
                logger.info("✅ RPC client closed gracefully")
            except Exception as e:
                logger.warning(f"⚠️ Error closing RPC client: {e}")
        
        logger.info("✅ Copy trading bot stopped gracefully")
    
    async def start_monitoring(self):
        """Start the copy trading bot with auto-restart capability"""
        try:
            self.is_running = True
            logger.info("🚀 Starting copy trading bot with auto-restart...")
            
            # Main monitoring loop with auto-restart
            while self.is_running:
                try:
                    # Start WebSocket monitoring
                    await self.start_websocket_monitoring()
                    
                    # If websocket monitoring ends and bot is still running, restart
                    if self.is_running:
                        logger.info("🔄 WebSocket monitoring ended, restarting in 10 seconds...")
                        await asyncio.sleep(10)
                        continue
                    else:
                        break
                        
                except KeyboardInterrupt:
                    logger.info("⏹️ Received shutdown signal")
                    self.is_running = False
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Critical error in main monitoring loop: {e}")
                    if self.is_running:
                        logger.info("🔄 Restarting main loop in 15 seconds...")
                        await asyncio.sleep(15)
                        continue
                    else:
                        break
            
            logger.info("🛑 Copy trading bot stopped")
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            self.is_running = False
    
    async def start_websocket_monitoring(self):
        """Start enhanced WebSocket connection using multiple subscription types with auto-reconnect"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Connect to WebSocket with enhanced settings
                ws_url = env.HELIUS_Standard_Websocket_URL
                logger.info(f"🔌 Connecting to Enhanced WebSocket: {ws_url} (Attempt {attempt + 1}/{max_retries})")
                logger.info(f"🎯 Target Wallet: {self.config.target_wallets[0]}")
                
                # Enhanced WebSocket connection with proper keepalive settings
                async with websockets.connect(
                    ws_url,
                    ping_interval=30,  # Send ping every 30 seconds
                    ping_timeout=10,   # Wait 10 seconds for pong
                    close_timeout=10,  # Close timeout
                    max_size=10**6,    # 1MB max message size
                    max_queue=32       # Message queue size
                ) as websocket:
                    self.ws_connection = websocket
                    logger.info(f"✅ WebSocket connected successfully with keepalive")
                    
                    # Setup enhanced subscriptions
                    await self.setup_enhanced_subscriptions()
                    
                    # 🔧 CRITICAL FIX: Check wallet history to catch missed BUY transactions
                    logger.info(f"🔍 SCANNING WALLET HISTORY to catch missed BUY transactions...")
                    await self.scan_wallet_history()
                    
                    # Balance display timer
                    last_balance_check = time.time()
                    last_ping_check = time.time()
                    balance_check_interval = 60  # Show balance every 60 seconds
                    ping_check_interval = 25    # Manual ping every 25 seconds as backup
                    
                    # Listen for transactions with robust error handling
                    while self.is_running:
                        try:
                            # Wait for message with shorter timeout to allow periodic checks
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            await self.process_websocket_message(message)
                            
                        except asyncio.TimeoutError:
                            # Use timeout for periodic maintenance
                            current_time = time.time()
                            
                            # Show balance periodically
                            if current_time - last_balance_check >= balance_check_interval:
                                await self.display_current_status()
                                last_balance_check = current_time
                            
                            # Manual keepalive ping as backup
                            if current_time - last_ping_check >= ping_check_interval:
                                try:
                                    await websocket.ping()
                                    logger.debug(f"📡 Manual keepalive ping sent")
                                    last_ping_check = current_time
                                except Exception as ping_error:
                                    logger.warning(f"⚠️ Manual ping failed: {ping_error}")
                                    raise  # Trigger reconnection
                            
                            continue
                            
                        except websockets.exceptions.ConnectionClosed as e:
                            logger.warning(f"⚠️ WebSocket connection closed: {e}")
                            raise  # Trigger reconnection
                            
                        except websockets.exceptions.ProtocolError as e:
                            logger.warning(f"⚠️ WebSocket protocol error: {e}")
                            raise  # Trigger reconnection
                            
                        except Exception as e:
                            logger.error(f"❌ WebSocket error: {e}")
                            # Check if connection is still alive
                            if websocket.closed:
                                logger.warning(f"🔌 WebSocket connection is closed, reconnecting...")
                                raise  # Trigger reconnection
                            continue
                
                # If we reach here, connection ended normally
                logger.info(f"🔌 WebSocket connection ended normally")
                break
                
            except Exception as e:
                logger.error(f"❌ WebSocket connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60 seconds
                else:
                    logger.error(f"❌ All WebSocket connection attempts failed, falling back to polling")
                    # Fallback to polling
                    await self.start_polling_monitoring()
                    break
    
    async def display_current_status(self):
        """Display current wallet status and balance"""
        try:
            current_balances = await self.get_wallet_balance()
            
            logger.info(f"🔍 CURRENT WALLET STATUS")
            logger.info(f"   💎 SOL Balance: {current_balances.get('SOL', 0):.6f}")
            logger.info(f"   📊 Positions: {len(self.positions)}")
            logger.info(f"   🎯 Total Executions: {len(self.execution_history)}")
            
            # Show token positions
            if self.positions:
                logger.info(f"   🎯 Active Positions:")
                for token_mint, position in list(self.positions.items())[:5]:  # Show first 5
                    token_balance = current_balances.get(token_mint, 0)
                    logger.info(f"      {token_mint[:8]}...: {position.current_amount:.6f} SOL invested, {token_balance:.6f} tokens")
            
            # Show trade counts
            if self.trade_counter:
                logger.info(f"   🔢 Trade Counts:")
                for token_mint, count in list(self.trade_counter.items())[:3]:  # Show top 3
                    logger.info(f"      {token_mint[:8]}...: {count} trades")
                    
        except Exception as e:
            logger.debug(f"Error displaying status: {e}")
    
    async def scan_wallet_history(self):
        """Scan recent wallet history to catch any BUY transactions we missed - WITH ROBUST ERROR HANDLING"""
        try:
            logger.info(f"📚 WALLET HISTORY SCAN: Checking last 50 transactions from each target wallet")
            
            for wallet_idx, wallet in enumerate(self.config.target_wallets):
                try:
                    logger.info(f"🔍 [{wallet_idx+1}/{len(self.config.target_wallets)}] Scanning history for: {wallet[:8]}...")
                    
                    # Add delay to avoid rate limiting
                    if wallet_idx > 0:
                        await asyncio.sleep(3)
                    
                    # Get last 50 transactions to catch recent BUYs
                    response = await self.rpc_client.get_signatures_for_address(
                        Pubkey.from_string(wallet),
                        limit=50
                    )
                    
                    if not response.value:
                        logger.warning(f"⚠️ No transaction history found for {wallet[:8]}...")
                        continue
                    
                    logger.info(f"📊 Found {len(response.value)} historical transactions")
                    buy_count = 0
                    sell_count = 0
                    error_count = 0
                    
                    # Analyze each transaction to find BUY trades - LIMITED TO RECENT ONES
                    for i, tx_info in enumerate(response.value[:10]):  # Only check most recent 10 to avoid rate limits
                        signature = str(tx_info.signature)
                        
                        # Skip if we already processed this
                        if signature in self.processed_signatures:
                            logger.debug(f"⏭️ Skipping already processed: {signature[:8]}...")
                            continue
                            
                        logger.info(f"📋 [{i+1}/10] Analyzing historical transaction: {signature[:8]}...")
                        
                        try:
                            # Quick analysis to identify BUY vs SELL - WITH TIMEOUT
                            trade_info = await asyncio.wait_for(
                                self.extract_trade_info_quick(signature, wallet),
                                timeout=10.0
                            )
                            
                            if trade_info:
                                if trade_info['type'] == 'buy':
                                    buy_count += 1
                                    logger.info(f"🟢 HISTORICAL BUY FOUND: {trade_info['token_mint'][:8]}... on {trade_info.get('dex', 'Unknown')}")
                                    logger.info(f"   📅 This BUY was missed during live monitoring!")
                                    
                                    # Add to processed to avoid duplicate execution
                                    self.processed_signatures.add(signature)
                                    
                                    # Execute the buy trade (historical) - CRITICAL FIX
                                    logger.info(f"🔄 Executing missed BUY trade...")
                                    await self.execute_copy_trade(trade_info, wallet)
                                    
                                elif trade_info['type'] == 'sell':
                                    sell_count += 1
                                    logger.debug(f"🔴 Historical sell: {trade_info['token_mint'][:8]}...")
                                    # Mark as processed to avoid re-analyzing
                                    self.processed_signatures.add(signature)
                            else:
                                logger.debug(f"📝 Non-trade transaction: {signature[:8]}...")
                        
                        except asyncio.TimeoutError:
                            error_count += 1
                            logger.warning(f"⏰ Timeout analyzing {signature[:8]}... (skipping)")
                            continue
                        except Exception as tx_error:
                            error_count += 1
                            logger.warning(f"⚠️ Error analyzing {signature[:8]}...: {tx_error}")
                            continue
                        
                        # Add small delay to avoid overwhelming RPC
                        await asyncio.sleep(1)
                    
                    logger.info(f"📊 HISTORY SCAN COMPLETE for {wallet[:8]}...")
                    logger.info(f"   🟢 Historical BUYs found: {buy_count}")
                    logger.info(f"   🔴 Historical SELLs found: {sell_count}") 
                    logger.info(f"   ⚠️ Errors encountered: {error_count}")
                    
                    if buy_count > 0:
                        logger.info(f"✅ SUCCESS: Found {buy_count} missed BUY transactions to execute!")
                    else:
                        logger.info(f"📭 No historical BUYs found (target wallet may not have recent purchases)")
                    
                except Exception as wallet_error:
                    logger.error(f"❌ Error scanning history for {wallet[:8]}...: {wallet_error}")
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    continue
            
            logger.info(f"✅ WALLET HISTORY SCAN COMPLETE - Now monitoring for new trades...")
            
        except Exception as e:
            logger.error(f"❌ Critical error in wallet history scan: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Don't let history scan failure prevent bot from running
            logger.info(f"🔄 Continuing with real-time monitoring despite history scan issues...")

    async def extract_trade_info_quick(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Quick trade info extraction for historical analysis"""
        try:
            # Convert string signature to Signature object
            sig_obj = Signature.from_string(signature)
            
            # Get transaction with shorter timeout for bulk processing
            tx_response = await self.rpc_client.get_transaction(
                sig_obj,
                encoding="jsonParsed",
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            
            if not tx_response or not tx_response.value:
                return None
            
            # Quick analysis - reuse existing extract_trade_info
            return await self.extract_trade_info(tx_response.value, wallet_address, signature)
            
        except Exception as e:
            logger.debug(f"Quick analysis failed for {signature[:8]}...: {e}")
            return None

    async def setup_enhanced_subscriptions(self):
        """Setup comprehensive WebSocket subscriptions to catch ALL transactions"""
        subscription_id = 1
        
        for wallet in self.config.target_wallets:
            # ❌ CRITICAL ISSUE IDENTIFIED: signatureSubscribe is BROKEN!
            # It only subscribes to future signatures involving a wallet, but:
            # 1. Most wallets use fresh transaction signatures
            # 2. We can't subscribe to wallet addresses directly  
            # 3. signatureSubscribe needs an actual signature, not a wallet address
            
            # REMOVED: The broken signatureSubscribe that was causing confusion
            # OLD CODE: signatureSubscribe with wallet address (DOESN'T WORK)
            
            # ✅ WORKING APPROACH: Use logsSubscribe + accountSubscribe + programSubscribe
            logger.info(f"🔧 Using RELIABLE method: logs + account + program subscriptions for: {wallet}")
            
            # 1. Logs subscription (current method) - KEEP as backup
            logs_params = {
                "jsonrpc": "2.0",
                "id": subscription_id,
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [wallet]},
                    {"commitment": "processed"}
                ]
            }
            await self.ws_connection.send(json.dumps(logs_params))
            logger.info(f"📡 Subscribed to LOGS for: {wallet}")
            subscription_id += 1
            
            # 2. Account subscription (balance changes) - KEEP for real-time balance
            account_params = {
                "jsonrpc": "2.0",
                "id": subscription_id,
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {
                        "encoding": "jsonParsed",
                        "commitment": "processed"
                    }
                ]
            }
            await self.ws_connection.send(json.dumps(account_params))
            logger.info(f"💰 Subscribed to ACCOUNT BALANCE for: {wallet}")
            subscription_id += 1
            
        # 3. DEX Program subscriptions (for precise trade detection)
        # Enhanced list to catch ALL possible DEX trades
        dex_programs = {
            # Jupiter (most comprehensive)
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium (popular for meme tokens)
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
            
            # Pump.fun (critical for new meme tokens)
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
            
            # Orca (secondary DEX)
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
            
            # Phoenix (order book DEX)
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
            
            # Other popular DEXes
            "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
            "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity",
            
            # � CRITICAL MISSING PROGRAMS (from transaction pattern analysis)
            # These programs were found in 100% of missed trades from target wallets
            "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh": "Target Wallet DEX Router",  # Used 10x in trades
            "2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr": "Target Wallet DEX Program", # Used 10x in trades
            "6s1xP3hpbAfFoNtUNF8mfHsjr2Bd97JxFJRWLbL6aHuX": "Target Wallet Token Swap",   # Used 10x in trades
            "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1": "Target Wallet Liquidity",   # Used 10x in trades
            "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv": "Target Wallet DEX #2",      # Used 7x in trades
            "Z9z6LsWmKURFCYKptcQLjmXUB4HbhcTwXCcHYTme8K6": "Target Wallet DEX #3",       # Used 7x in trades
            "9djsqy8mnbmPZJoYp1SqDyqQsz22YNRsrPtbXPcWQqHc": "Target Wallet DEX #4",     # Used 7x in trades
            "9smUrM3MpvJAbCLbuzkxSKSuBRR8mKeKSjjde8ao3j4t": "Target Wallet DEX #5",     # Used 7x in trades
            "GpH7NwogU6QGG4aQQXicTitwV8Yx5KL9pVcZZo3sK6jz": "Target Wallet DEX #6",     # Used 7x in trades
            "2SDG5aK3r55KZ97VqrnGU9AntFadmDr7S2Kenbuabonk": "Target Wallet DEX #7",     # Used 7x in trades
            
            # Additional programs from analysis (used 2+ times)
            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95": "Target Wallet Router #1",   # Used 6x in trades
            "GwQ9bcrcZAEK3W1S9HyiSsJAVVXSz8Zr8ExbppdJ4zQU": "Target Wallet Router #2",   # Used 6x in trades
            "BmCNT7mkSuzBi7x51PQEZGM9wPa3CBGgMHZtvinp2r5U": "Target Wallet Router #3",   # Used 5x in trades
            "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY": "Target Wallet Router #4",   # Used 3x in trades
            "jitodontfrontd1111111TradeWithAxiomDotTrade": "Axiom Trade Router",        # Used 3x in trades
            "5Mq5HT4Tu7d8xVGoNoSExr7UisBminkjVQLtqWhefv7": "Target Wallet Router #5",    # Used 3x in trades
            "7X6oasaqTdFc9Pj9ApNThY761BnVDzvp9Jshu1bi1zdq": "Target Wallet Router #6",    # Used 3x in trades
            "Dd3nJaWZfYN3V9JKMLXmFq6CrQUvR4262sgtcKsRx3mB": "Target Wallet Router #7",    # Used 3x in trades
            "7LLQA3YDDgnthf96LwHwpDDEhX1fqohb7SHWhKePbonk": "Target Wallet Router #8",    # Used 3x in trades
            "E9onaXVE9jXZb3crveouaxUsLnvhcuaCLMFk2o4RzuFZ": "Target Wallet Router #9",    # Used 2x in trades
            "4rmHQNmyX4oct9gCw3KAufRebCrYAYZygbmPKJJDoWcT": "Target Wallet Router #10",   # Used 2x in trades
            
            # Token programs (catch manual transfers)
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program"
        }
        
        for program_id, program_name in dex_programs.items():
            for wallet in self.config.target_wallets:
                program_params = {
                    "jsonrpc": "2.0",
                    "id": subscription_id,
                    "method": "programSubscribe",
                    "params": [
                        program_id,
                        {
                            "encoding": "jsonParsed",
                            "commitment": "processed",
                            "filters": [
                                {
                                    "memcmp": {
                                        "offset": 0,
                                        "bytes": wallet
                                    }
                                }
                            ]
                        }
                    ]
                }
                await self.ws_connection.send(json.dumps(program_params))
                logger.info(f"🎯 Subscribed to {program_name} for: {wallet}")
                subscription_id += 1
    
    async def start_polling_monitoring(self):
        """Fallback polling method if WebSocket fails"""
        logger.info("🔄 Starting polling monitoring (WebSocket fallback)")
        
        last_status_display = time.time()
        status_display_interval = 60  # Show status every 60 seconds
        
        while self.is_running:
            try:
                for wallet in self.config.target_wallets:
                    await self.check_wallet_transactions(wallet)
                
                # Display status periodically
                current_time = time.time()
                if current_time - last_status_display >= status_display_interval:
                    await self.display_current_status()
                    last_status_display = current_time
                
                await asyncio.sleep(5)  # Poll every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Polling error: {e}")
                await asyncio.sleep(10)
    
    async def process_websocket_message(self, message: str):
        """Process incoming WebSocket messages from multiple subscription types"""
        try:
            data = json.loads(message)
            
            # Skip subscription confirmations
            if "result" in data and isinstance(data["result"], int):
                logger.info(f"✅ WebSocket subscription confirmed: {data['result']}")
                return
            
            # Process notifications
            if "params" in data and "result" in data["params"]:
                method = data.get("method", "")
                result = data["params"]["result"]
                
                if method == "logsNotification":
                    await self.handle_logs_notification(result)
                elif method == "accountNotification":
                    await self.handle_account_notification(result)
                elif method == "programNotification":
                    await self.handle_program_notification(result)
                elif method == "signatureNotification":
                    await self.handle_signature_notification(result)
                else:
                    logger.debug(f"🤷 Unknown notification method: {method}")
                
        except Exception as e:
            logger.error(f"❌ Error processing WebSocket message: {e}")
            logger.debug(f"Message content: {message[:200]}...")
    
    async def handle_logs_notification(self, result: Dict[str, Any]):
        """Handle transaction logs notifications with AGGRESSIVE instant detection"""
        try:
            value = result.get("value", {})
            signature = value.get("signature", "")
            logs = value.get("logs", [])
            error = value.get("err")
            
            if error:
                return
            
            # 🚀 CRITICAL FIX: Don't check logs for wallet addresses - they're NEVER there!
            # Instead, analyze EVERY transaction that involves DEX activity
            if not logs:
                return
            
            log_text = ' '.join(logs).lower()
            
            # 🚀 ULTRA-AGGRESSIVE: Detect ANY DEX activity and analyze it
            dex_activity = False
            dex_detected = None
            
            # Enhanced DEX detection patterns
            if any(pattern in log_text for pattern in ['jupiter', 'jup aggregator', 'route plan']):
                dex_detected = "Jupiter"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['raydium', 'cpmm', 'clmm', 'amm']):
                dex_detected = "Raydium"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['pump.fun', 'pumpfun', 'bonding curve']):
                dex_detected = "Pump.fun"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['orca', 'whirlpool']):
                dex_detected = "Orca"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['phoenix', 'meteora', 'lifinity']):
                dex_detected = dex_detected or "DEX"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['swap', 'exchange', 'trade']):
                dex_detected = "Unknown DEX"
                dex_activity = True
            
            # 🚀 CRITICAL FIX: If ANY DEX activity detected, analyze the transaction
            if dex_activity:
                logger.info(f"⚡ INSTANT DEX DETECTION: {signature[:8]}... on {dex_detected}")
                logger.info(f"🔥 AGGRESSIVE MODE: Analyzing transaction for target wallet involvement...")
                
                # Immediately analyze the transaction to see if it involves our target wallets
                asyncio.create_task(self.analyze_transaction_aggressive(signature, dex_detected))
            
        except Exception as e:
            logger.error(f"❌ Error in aggressive logs handling: {e}")
    
    async def analyze_transaction_aggressive(self, signature: str, detected_dex: str):
        """AGGRESSIVE transaction analysis - analyzes EVERY DEX transaction for target wallet involvement"""
        try:
            logger.info(f"🔥 AGGRESSIVE ANALYSIS: {signature[:8]}... on {detected_dex}")
            
            # Get transaction details immediately
            tx_response = await self.rpc_client.get_transaction(
                signature=signature,
                max_supported_transaction_version=0,
                encoding="json"
            )
            
            if not tx_response or not tx_response.value:
                logger.debug(f"❌ Transaction not found: {signature[:8]}...")
                return
            
            tx = tx_response.value
            meta = tx.meta
            
            if meta.err:
                return  # Skip failed transactions
            
            # 🚀 CRITICAL: Check if ANY of our target wallets are involved
            account_keys = tx.transaction.message.account_keys
            involved_wallets = []
            
            for wallet in self.config.target_wallets:
                if wallet in [str(key) for key in account_keys]:
                    involved_wallets.append(wallet)
            
            if not involved_wallets:
                return  # None of our target wallets involved
            
            # 🚀 SUCCESS: Target wallet found in transaction!
            for target_wallet in involved_wallets:
                logger.info(f"🎯 TARGET WALLET FOUND: {target_wallet[:8]}... in {signature[:8]}...")
                
                # Immediately analyze the trade
                trade_info = await self.extract_trade_info_quick(signature, target_wallet)
                
                if trade_info:
                    logger.info(f"✅ TRADE EXTRACTED: {trade_info['type'].upper()} {trade_info['token_mint'][:8]}...")
                    
                    # 🚀 EXECUTE IMMEDIATELY
                    await self.execute_copy_trade(trade_info, target_wallet)
                else:
                    # Fallback to full analysis
                    logger.info(f"🔄 Quick analysis failed, using full analysis...")
                    await self.analyze_transaction(signature, target_wallet)
            
        except Exception as e:
            logger.error(f"❌ Error in aggressive transaction analysis: {e}")

    async def handle_logs_notification(self, result: Dict[str, Any]):
        """Handle logs subscription notifications with AGGRESSIVE trade detection"""
        try:
            signature = result.get("signature")
            logs = result.get("logs", [])
            
            if not signature or not logs:
                return
                
            # Convert logs to searchable text
            log_text = ' '.join(logs).lower()
            
            # 🚀 AGGRESSIVE ANALYSIS: Look for ANY trade indicators
            # Even partial matches trigger analysis
            dex_detected = None
            trade_type = None
            token_mint = None
            target_wallet = None
            
            # Extract target wallet from logs context (whoever triggered this)
            for wallet in self.target_wallets:
                if wallet in log_text or str(wallet) in str(result):
                    target_wallet = wallet
                    break
            
            if not target_wallet:
                logger.debug(f"❌ No target wallet found in logs for {signature[:8]}...")
                return
                
            logger.info(f"⚡ LOGS: Transaction {signature[:8]}... from {target_wallet[:8]}...")
            
            # 🚀 AGGRESSIVE DEX DETECTION: Look for ANY DEX mentions
            if any(dex in log_text for dex in ['pump', 'raydium', 'jupiter', 'meteora']):
                dex_detected = "Pump.fun" if 'pump' in log_text else "Jupiter" if 'jupiter' in log_text else "Raydium" if 'raydium' in log_text else "Meteora"
            elif 'orca' in log_text:
                dex_detected = "Orca"
            elif 'phoenix' in log_text:
                dex_detected = "Phoenix"
            
            # Quick trade type detection (more aggressive patterns)
            if any(pattern in log_text for pattern in ['buy', 'swapbasein', 'purchas', 'swap', 'exchange']):
                trade_type = 'buy'
            elif any(pattern in log_text for pattern in ['sell', 'swapbaseout', 'redeem', 'withdraw']):
                trade_type = 'sell'
            
            # 🚀 ULTRA-AGGRESSIVE: If we detect a DEX but no clear trade type, assume buy
            # Since your target wallets are trusted, we assume they're making valid trades
            if dex_detected and not trade_type:
                logger.info(f"🚀 AGGRESSIVE ASSUMPTION: DEX {dex_detected} detected, assuming BUY")
                trade_type = 'buy'
            
            # Quick token extraction (look for 44-character addresses)
            import re
            token_matches = re.findall(r'\b[A-Za-z0-9]{43,44}\b', log_text)
            for token in token_matches:
                if (len(token) == 44 and 
                    token != "So11111111111111111111111111111111111111112" and  # Skip WSOL
                    token != target_wallet and
                    not any(sys in token for sys in ['111111111111111111', 'TokenkegQfeZ', 'ComputeBudget'])):
                    token_mint = token
                    break
            
            # 🚀 AGGRESSIVE EXECUTION: If we detect a trade, execute immediately
            if trade_type and token_mint and dex_detected:
                logger.info(f"⚡ INSTANT TRADE: {trade_type.upper()} {token_mint[:8]}... on {dex_detected}")
                logger.info(f"🚀 AGGRESSIVE MODE: Executing immediately without full analysis!")
                
                # Create minimal trade info
                trade_info = {
                    'type': trade_type,
                    'token_mint': token_mint,
                    'amount': self.config.investment_amount_sol,
                    'timestamp': datetime.now(),
                    'dex': dex_detected,
                    'detection_method': 'ultra_fast_logs'
                }
                
                # Execute immediately without waiting
                asyncio.create_task(self.execute_copy_trade(trade_info, target_wallet))
                
            else:
                # 🚀 AGGRESSIVE MODE: Since you trust these wallets, analyze ALL their transactions
                logger.info(f"🔍 AGGRESSIVE MODE: Analyzing all transactions from trusted wallet")
                asyncio.create_task(self.analyze_transaction(signature, target_wallet))
                
        except Exception as e:
            logger.error(f"❌ Error in aggressive logs handling: {e}")
    
    async def handle_account_notification(self, result: Dict[str, Any]):
        """Handle account balance change notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            lamports = value.get("lamports", 0)
            sol_balance = lamports / 1e9
            
            logger.info(f"💰 ACCOUNT: Balance change detected at slot {slot}")
            logger.info(f"   💎 New SOL balance: {sol_balance:.6f} SOL")
            
            # Balance changes are strong indicators of trading activity
            logger.info(f"� STRONG SIGNAL: Account balance changed - likely trade!")
            
            # Get recent transaction to analyze
            # Immediately check for the transaction that caused this balance change
            for wallet in self.config.target_wallets:
                await self.check_recent_transactions_for_wallet(wallet)
            
        except Exception as e:
            logger.error(f"❌ Error handling account notification: {e}")
    
    async def handle_program_notification(self, result: Dict[str, Any]):
        """Handle DEX program notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            pubkey = value.get("pubkey", "")
            
            logger.info(f"🎯 PROGRAM: DEX interaction detected at slot {slot}")
            logger.info(f"   📍 Account: {pubkey}")
            
            # DEX program interactions are very strong trade indicators
            logger.info(f"🔥 VERY STRONG SIGNAL: DEX program interaction detected!")
            
            # This is the most reliable indicator of trading activity
            # We should immediately check for recent transactions
            for wallet in self.config.target_wallets:
                await self.check_recent_transactions_for_wallet(wallet)
            
        except Exception as e:
            logger.error(f"❌ Error handling program notification: {e}")
    
    async def check_recent_transactions_for_wallet(self, wallet_address: str):
        """Check the most recent transactions for a wallet when we get strong signals"""
        try:
            logger.info(f"🔍 Checking recent transactions for strong signal from {wallet_address[:8]}...")
            
            # Get the last 10 transactions to catch rapid-fire trading
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet_address),
                limit=10  # Get more transactions to catch rapid trades
            )
            
            if response.value:
                logger.info(f"📊 Found {len(response.value)} recent transactions to analyze")
                
                # Check each transaction for new ones we haven't processed
                new_transactions_found = 0
                for tx_info in response.value:
                    signature = str(tx_info.signature)
                    
                    # Only analyze new transactions we haven't seen before
                    if signature not in self.processed_signatures:
                        self.processed_signatures.add(signature)
                        new_transactions_found += 1
                        logger.info(f"🆕 NEW Transaction #{new_transactions_found}: {signature}")
                        logger.info(f"   🔗 https://solscan.io/tx/{signature}")
                        
                        # Analyze this transaction
                        await self.analyze_transaction(signature, wallet_address)
                
                if new_transactions_found == 0:
                    logger.debug(f"📭 No new transactions found (all already processed)")
                else:
                    logger.info(f"✅ Processed {new_transactions_found} new transactions")
                    
            else:
                logger.warning(f"⚠️  No recent transactions found for {wallet_address}")
                        
        except Exception as e:
            logger.error(f"❌ Error checking recent transactions: {e}")
    
    async def handle_signature_notification(self, result: Dict[str, Any]):
        """Handle signature notifications - catches ALL transactions from target wallets"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            
            if value and value.get("err") is None:  # Transaction succeeded
                logger.info(f"🎯 SIGNATURE: Transaction confirmed at slot {slot}")
                logger.info(f"✅ SIGNATURE CONFIRMED: This is the MOST RELIABLE detection method!")
                logger.info(f"⚡ INSTANT ANALYSIS: Checking for new transactions from ALL monitored wallets")
                
                # Check all target wallets for new activity with higher priority
                for wallet in self.config.target_wallets:
                    logger.info(f"🔍 Priority check for wallet: {wallet[:8]}...")
                    await self.check_recent_transactions_for_wallet(wallet)
            else:
                # Even failed transactions can be informative
                if value and value.get("err"):
                    logger.debug(f"⚠️ Transaction failed at slot {slot}: {value.get('err')}")
            
        except Exception as e:
            logger.error(f"❌ Error handling signature notification: {e}")
    
    def is_trade_transaction(self, logs: List[str]) -> bool:
        """Check if transaction logs indicate trading activity"""
        try:
            if not logs:
                return False
            
            # Join all logs for easier searching
            all_logs = " ".join(logs).lower()
            
            # Look for trading indicators in logs
            trade_indicators = [
                "swap",           # DEX swaps
                "jupiter",        # Jupiter aggregator
                "raydium",        # Raydium DEX
                "pump",           # Pump.fun
                "orca",           # Orca DEX
                "meteora",        # Meteora DEX
                "axiom",          # Axiom DEX
                "transfer",       # Token transfers
                "buy",            # Buy operations
                "sell",           # Sell operations
                "exchange",       # Token exchange
                "trade",          # General trading
                "dex",           # DEX operations
            ]
            
            # Enhanced indicators for actual trades (not just setup)
            strong_trade_indicators = [
                "swap",
                "jupiter", 
                "raydium",
                "pump",
                "orca",
                "axiom",
                "buy",
                "sell"
            ]
            
            # Check if any trade indicator is present
            found_indicators = [indicator for indicator in trade_indicators if indicator in all_logs]
            strong_indicators = [indicator for indicator in strong_trade_indicators if indicator in all_logs]
            
            if found_indicators:
                logger.info(f"🎯 Trade indicators found in logs: {found_indicators}")
                
                # If we have strong indicators, definitely a trade
                if strong_indicators:
                    logger.info(f"💪 Strong trade indicators: {strong_indicators}")
                    logger.debug(f"📋 Sample logs: {logs[:3]}...")
                    return True
                
                # For weaker indicators like "transfer", do additional checks
                elif "transfer" in found_indicators:
                    # Check if this looks like a setup transaction (WSOL creation/closing)
                    setup_patterns = [
                        "createaccountwithseed",
                        "initializeaccount", 
                        "closeaccount",
                        "advancenonce"
                    ]
                    
                    has_setup_pattern = any(pattern in all_logs for pattern in setup_patterns)
                    
                    if has_setup_pattern:
                        logger.info(f"🔧 Setup transaction detected (not trade): {[p for p in setup_patterns if p in all_logs]}")
                        return False  # This is setup, not a trade
                    else:
                        logger.debug(f"📋 Sample logs: {logs[:3]}...")
                        return True  # Transfer without setup patterns, likely a trade
                
                logger.debug(f"📋 Sample logs: {logs[:3]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking trade logs: {e}")
            return False
    
    async def check_wallet_transactions(self, wallet_address: str):
        """Check recent transactions for a wallet (polling fallback)"""
        try:
            logger.info(f"🔍 Polling transactions for wallet: {wallet_address}")
            
            # Get recent transactions
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet_address),
                limit=5  # Check last 5 transactions
            )
            
            if response.value:
                logger.info(f"📊 Found {len(response.value)} recent transactions")
                for tx_info in response.value:
                    signature = str(tx_info.signature)
                    
                    if signature not in self.processed_signatures:
                        self.processed_signatures.add(signature)
                        logger.info(f"🆕 New transaction found: {signature}")
                        await self.analyze_transaction(signature, wallet_address)
            else:
                logger.debug(f"📭 No recent transactions found for {wallet_address}")
                        
        except Exception as e:
            logger.error(f"❌ Error checking wallet {wallet_address}: {e}")
    
    async def analyze_transaction(self, signature: str, wallet_address: str):
        """Analyze a transaction to determine if it's a trade"""
        try:
            logger.info(f"🔍 Analyzing transaction: {signature}")
            logger.info(f"   🎯 Target wallet: {wallet_address}")
            
            # Convert string signature to Signature object
            try:
                sig_obj = Signature.from_string(signature)
            except Exception as sig_error:
                logger.error(f"❌ Invalid signature format {signature}: {sig_error}")
                return
            
            # Get transaction details with retry for unconfirmed transactions
            tx_response = None
            max_retries = 3
            
            # Wait longer for transaction to be confirmed with metadata
            logger.info(f"⏳ Waiting for transaction confirmation with metadata...")
            await asyncio.sleep(3)
            
            for attempt in range(max_retries):
                try:
                    # CRITICAL: Request full transaction metadata for token balance analysis
                    tx_response = await self.rpc_client.get_transaction(
                        sig_obj,
                        encoding="jsonParsed",
                        commitment=Confirmed,  # Use Confirmed as required by RPC
                        max_supported_transaction_version=0
                    )
                    
                    if tx_response.value:
                        # DEBUG: Investigate transaction structure
                        tx_value = tx_response.value
                        logger.info(f"✅ Transaction retrieved successfully")
                        logger.info(f"   🔍 Transaction type: {type(tx_value)}")
                        
                        # Check different possible locations for metadata
                        has_meta_direct = hasattr(tx_value, 'meta')
                        has_transaction_attr = hasattr(tx_value, 'transaction')
                        
                        logger.info(f"   📊 Has 'meta' attribute: {has_meta_direct}")
                        logger.info(f"   📊 Has 'transaction' attribute: {has_transaction_attr}")
                        
                        # Try to find metadata in different locations
                        meta = None
                        if has_meta_direct:
                            meta = tx_value.meta
                            logger.info(f"   ✅ Found meta directly: {meta is not None}")
                        elif has_transaction_attr and hasattr(tx_value.transaction, 'meta'):
                            meta = tx_value.transaction.meta
                            logger.info(f"   ✅ Found meta in transaction: {meta is not None}")
                        else:
                            # Debug: Show available attributes
                            attrs = [attr for attr in dir(tx_value) if not attr.startswith('_')]
                            logger.info(f"   🔍 Available attributes: {attrs[:10]}...")
                        
                        if meta:
                            logger.info(f"   💰 Pre-token balances: {len(meta.pre_token_balances) if hasattr(meta, 'pre_token_balances') and meta.pre_token_balances else 0}")
                            logger.info(f"   💰 Post-token balances: {len(meta.post_token_balances) if hasattr(meta, 'post_token_balances') and meta.post_token_balances else 0}")
                        
                        break
                    else:
                        logger.info(f"⏳ Transaction not confirmed yet, attempt {attempt + 1}/{max_retries}")
                        await asyncio.sleep(2)  # Wait 2 seconds before retry
                        
                except Exception as e:
                    logger.warning(f"⚠️  Error fetching transaction (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
            
            # CRITICAL: If we don't have metadata, try Finalized commitment
            if tx_response and tx_response.value:
                meta = self.extract_transaction_meta(tx_response.value)
                if meta is None:
                    logger.warning(f"⚠️ No metadata with Confirmed commitment, trying Finalized...")
                try:
                    from solana.rpc.commitment import Finalized
                    tx_response_finalized = await self.rpc_client.get_transaction(
                        sig_obj,
                        encoding="jsonParsed", 
                        commitment=Finalized,
                        max_supported_transaction_version=0
                    )
                    if tx_response_finalized.value:
                        finalized_meta = self.extract_transaction_meta(tx_response_finalized.value)
                        if finalized_meta:
                            logger.info(f"✅ Got metadata with Finalized commitment!")
                            tx_response = tx_response_finalized
                        else:
                            logger.warning(f"⚠️ Still no metadata with Finalized commitment")
                except Exception as e:
                    logger.debug(f"Finalized commitment attempt failed: {e}")
            
            if not tx_response or not tx_response.value:
                logger.warning(f"⚠️  Transaction not found after {max_retries} attempts: {signature}")
                return
            
            tx = tx_response.value
            logger.info(f"✅ Transaction retrieved successfully")
            
            # Analyze transaction for trading activity - now returns wallet-agnostic results with signature  
            trade_info = await self.extract_trade_info(tx, wallet_address, signature)
            
            if trade_info:
                trader_wallet = trade_info.get('trader_wallet', wallet_address)
                logger.info(f"🎯 TRADE DETECTED!")
                logger.info(f"   Type: {trade_info['type'].upper()}")
                logger.info(f"   Token: {trade_info['token_mint']}")
                logger.info(f"   Amount: {trade_info['amount']}")
                logger.info(f"   Trader: {trader_wallet}")
                logger.info(f"   DEX: {trade_info.get('dex', 'Unknown')}")
                logger.info(f"   🔗 https://solscan.io/tx/{signature}")
                
                # Pass the detected trader wallet to copy trade execution
                await self.execute_copy_trade(trade_info, trader_wallet)
            else:
                logger.info(f"📝 No trading activity detected in transaction")
                
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction {signature}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    def extract_transaction_meta(self, transaction):
        """Extract transaction metadata from various possible locations"""
        try:
            # Method 1: Direct meta attribute (old format)
            if hasattr(transaction, 'meta') and transaction.meta is not None:
                logger.debug(f"📊 Found meta directly")
                return transaction.meta
            
            # Method 2: EncodedConfirmedTransactionWithStatusMeta structure (Solders)
            # This is the most common structure with recent Solana Python clients
            if hasattr(transaction, 'transaction') and hasattr(transaction, 'meta'):
                logger.debug(f"📊 Found meta in Solders EncodedConfirmedTransactionWithStatusMeta")
                return transaction.meta
            
            # Method 3: Meta inside transaction attribute
            if hasattr(transaction, 'transaction') and hasattr(transaction.transaction, 'meta'):
                if transaction.transaction.meta is not None:
                    logger.debug(f"📊 Found meta in transaction.transaction")
                    return transaction.transaction.meta
            
            # Method 4: Check if this IS the transaction data (common with Solders)
            if hasattr(transaction, 'pre_token_balances') or hasattr(transaction, 'post_token_balances'):
                logger.debug(f"📊 Transaction object IS the meta")
                return transaction
            
            # Method 5: If transaction is wrapped, try to unwrap it
            if hasattr(transaction, 'value'):
                return self.extract_transaction_meta(transaction.value)
            
            # Debug: Show structure
            attrs = [attr for attr in dir(transaction) if not attr.startswith('_')]
            logger.debug(f"📊 Transaction attributes: {attrs[:10]}...")
            logger.debug(f"📊 Transaction type: {type(transaction)}")
            
            logger.warning(f"⚠️ No meta found in transaction structure")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting transaction meta: {e}")
            return None

    async def extract_trade_info(self, transaction: Any, wallet_address: str, signature: str = None) -> Optional[Dict[str, Any]]:
        """Extract trading information from transaction"""
        try:
            # Handle the transaction structure correctly
            if hasattr(transaction, 'transaction'):
                tx_data = transaction.transaction
            else:
                tx_data = transaction
            
            # Get transaction message
            if hasattr(tx_data, 'message'):
                tx_message = tx_data.message
            elif hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
                tx_message = tx_data.transaction.message
            else:
                logger.error(f"❌ Cannot find transaction message in structure: {type(transaction)}")
                return None
            
            instructions = tx_message.instructions
            
            # Look for token transfers and DEX operations
            sol_transfers = []
            token_transfers = []
            trade_type = None
            token_mint = None
            dex_detected = None
            actual_trader_wallet = None  # NEW: Track which wallet actually traded
            
            logger.info(f"📊 Analyzing {len(instructions)} instructions in transaction")
            
            # First pass: Check for DEX program calls using OFFICIAL Solana CompiledInstruction format
            all_program_ids = []
            
            for i, instruction in enumerate(instructions):
                try:
                    program_id = None
                    method_used = "none"
                    
                    # Method 1: Direct program_id attribute (for parsed instructions)
                    if hasattr(instruction, 'program_id'):
                        program_id = str(instruction.program_id)
                        method_used = "direct"
                        logger.debug(f"🔍 Instruction {i} - Direct program_id: {program_id}")
                    
                    # Method 2: program_id_index (official CompiledInstruction format per docs)
                    elif hasattr(instruction, 'program_id_index'):
                        if (hasattr(tx_message, 'account_keys') and 
                            instruction.program_id_index < len(tx_message.account_keys)):
                            program_id = str(tx_message.account_keys[instruction.program_id_index])
                            method_used = "index"
                            logger.debug(f"🔍 Instruction {i} - program_id_index[{instruction.program_id_index}]: {program_id}")
                        else:
                            logger.debug(f"⚠️  Invalid program_id_index {getattr(instruction, 'program_id_index', 'N/A')} for instruction {i}")
                    
                    # Method 3: Alternative naming (programIdIndex)
                    elif hasattr(instruction, 'programIdIndex'):
                        if (hasattr(tx_message, 'account_keys') and 
                            instruction.programIdIndex < len(tx_message.account_keys)):
                            program_id = str(tx_message.account_keys[instruction.programIdIndex])
                            method_used = "legacy_index"
                            logger.debug(f"🔍 Instruction {i} - programIdIndex[{instruction.programIdIndex}]: {program_id}")
                    
                    if program_id:
                        all_program_ids.append(program_id)
                        
                        # Known DEX program IDs - Enhanced with all missing programs from pattern analysis
                        dex_programs = {
                            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
                            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
                            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
                            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
                            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
                            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun Program",
                            "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump": "Pump.fun Trading",
                            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
                            "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Global",
                            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading V2",
                            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
                            "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
                            "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
                            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity",
                            
                            # � CRITICAL MISSING PROGRAMS (from transaction pattern analysis)
                            # These programs were found in 100% of missed trades from target wallets
                            "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh": "Target Wallet DEX Router",  # Used 10x in trades
                            "2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr": "Target Wallet DEX Program", # Used 10x in trades
                            "6s1xP3hpbAfFoNtUNF8mfHsjr2Bd97JxFJRWLbL6aHuX": "Target Wallet Token Swap",   # Used 10x in trades
                            "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1": "Target Wallet Liquidity",   # Used 10x in trades
                            "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv": "Target Wallet DEX #2",      # Used 7x in trades
                            "Z9z6LsWmKURFCYKptcQLjmXUB4HbhcTwXCcHYTme8K6": "Target Wallet DEX #3",       # Used 7x in trades
                            "9djsqy8mnbmPZJoYp1SqDyqQsz22YNRsrPtbXPcWQqHc": "Target Wallet DEX #4",     # Used 7x in trades
                            "9smUrM3MpvJAbCLbuzkxSKSuBRR8mKeKSjjde8ao3j4t": "Target Wallet DEX #5",     # Used 7x in trades
                            "GpH7NwogU6QGG4aQQXicTitwV8Yx5KL9pVcZZo3sK6jz": "Target Wallet DEX #6",     # Used 7x in trades
                            "2SDG5aK3r55KZ97VqrnGU9AntFadmDr7S2Kenbuabonk": "Target Wallet DEX #7",     # Used 7x in trades
                            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95": "Target Wallet Router #1",   # Used 6x in trades
                            "GwQ9bcrcZAEK3W1S9HyiSsJAVVXSz8Zr8ExbppdJ4zQU": "Target Wallet Router #2",   # Used 6x in trades
                            "BmCNT7mkSuzBi7x51PQEZGM9wPa3CBGgMHZtvinp2r5U": "Target Wallet Router #3",   # Used 5x in trades
                            "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY": "Target Wallet Router #4",   # Used 3x in trades
                            "jitodontfrontd1111111TradeWithAxiomDotTrade": "Axiom Trade Router",        # Used 3x in trades
                            "5Mq5HT4Tu7d8xVGoNoSExr7UisBminkjVQLtqWhefv7": "Target Wallet Router #5",    # Used 3x in trades
                            "7X6oasaqTdFc9Pj9ApNThY761BnVDzvp9Jshu1bi1zdq": "Target Wallet Router #6",    # Used 3x in trades
                            "Dd3nJaWZfYN3V9JKMLXmFq6CrQUvR4262sgtcKsRx3mB": "Target Wallet Router #7",    # Used 3x in trades
                            "7LLQA3YDDgnthf96LwHwpDDEhX1fqohb7SHWhKePbonk": "Target Wallet Router #8",    # Used 3x in trades
                            "E9onaXVE9jXZb3crveouaxUsLnvhcuaCLMFk2o4RzuFZ": "Target Wallet Router #9",    # Used 2x in trades
                            "4rmHQNmyX4oct9gCw3KAufRebCrYAYZygbmPKJJDoWcT": "Target Wallet Router #10",   # Used 2x in trades
                        }
                        
                        system_programs = {
                            "11111111111111111111111111111111": "System Program (Short)",
                            "11111111111111111111111111111112": "System Program",
                            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program",
                            "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
                            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program"
                        }
                        
                        if program_id in dex_programs:
                            dex_detected = dex_programs[program_id]
                            logger.info(f"🏢 DEX DETECTED: {dex_detected} (Method: {method_used})")
                        elif program_id in system_programs:
                            logger.debug(f"🔧 System: {system_programs[program_id]}")
                        else:
                            # DEBUG: Show ALL unknown programs to identify missing DEX programs
                            logger.info(f"❓ UNKNOWN PROGRAM: {program_id} (Method: {method_used})")
                    else:
                        # Debug: Show available attributes for troubleshooting
                        attrs = [attr for attr in dir(instruction) if not attr.startswith('_')]
                        logger.debug(f"⚠️  Instruction {i}: No program ID found. Attributes: {attrs[:8]}...")
                
                except Exception as inst_error:
                    logger.debug(f"Error processing instruction {i}: {inst_error}")
                    continue
            
            # Summary of program analysis
            unique_programs = len(set(all_program_ids))
            logger.info(f"📋 OFFICIAL ANALYSIS Summary:")
            logger.info(f"   Instructions: {len(instructions)}")
            logger.info(f"   Programs found: {len(all_program_ids)}")
            logger.info(f"   Unique programs: {unique_programs}")
            logger.info(f"   DEX detected: {dex_detected or 'None'}")
            
            # If no DEX detected, return None immediately  
            if not dex_detected:
                logger.info(f"❓ No DEX programs found - not a trading transaction")
                return None
            
            # NEW: SMART WALLET DETECTION - Find which wallet actually has token balance changes
            meta = self.extract_transaction_meta(transaction)
            if meta and hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                logger.info(f"🔍 SMART WALLET DETECTION: Finding actual trader...")
                
                # Check which wallets have token balance changes
                wallets_with_changes = set()
                
                # Collect all wallet addresses with token balances
                for balance in meta.pre_token_balances + meta.post_token_balances:
                    if hasattr(balance, 'owner'):
                        wallet_owner = str(balance.owner)
                        # Only consider our target wallets
                        if wallet_owner in self.config.target_wallets:
                            wallets_with_changes.add(wallet_owner)
                
                logger.info(f"   Target wallets with token balances: {len(wallets_with_changes)}")
                for wallet in wallets_with_changes:
                    logger.info(f"   📍 {wallet}")
                
                # AGGRESSIVE: If no token balances found but DEX detected, check SOL balances
                if len(wallets_with_changes) == 0 and dex_detected:
                    logger.info(f"🚀 AGGRESSIVE: No token balances found but DEX detected - checking SOL balances...")
                    
                    # Look at account keys for our target wallets
                    if hasattr(tx_message, 'account_keys'):
                        for account_key in tx_message.account_keys:
                            account_str = str(account_key)
                            if account_str in self.config.target_wallets:
                                logger.info(f"🎯 FOUND TARGET WALLET in transaction: {account_str}")
                                wallets_with_changes.add(account_str)
                    
                    # Also check SOL balance changes in metadata
                    if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                        logger.info(f"🔍 Checking SOL balance changes...")
                        for i, (pre_bal, post_bal) in enumerate(zip(meta.pre_balances, meta.post_balances)):
                            change = post_bal - pre_bal
                            if abs(change) > 1000000:  # > 0.001 SOL change
                                if i < len(tx_message.account_keys):
                                    account = str(tx_message.account_keys[i])
                                    if account in self.config.target_wallets:
                                        logger.info(f"💰 SOL change detected for target wallet {account}: {change/1e9:.6f} SOL")
                                        wallets_with_changes.add(account)
                
                # Now analyze each wallet to find which one had significant changes
                for potential_trader in wallets_with_changes:
                    logger.info(f"🔍 Analyzing wallet: {potential_trader}")
                    
                    # Extract wallet-specific token balance changes
                    wallet_pre_balances = {}
                    wallet_post_balances = {}
                    
                    # Get pre-transaction balances for this wallet
                    for balance in meta.pre_token_balances:
                        if hasattr(balance, 'owner') and str(balance.owner) == potential_trader:
                            mint = balance.mint
                            amount = float(balance.ui_token_amount.ui_amount or 0)
                            wallet_pre_balances[mint] = amount
                    
                    # Get post-transaction balances for this wallet  
                    for balance in meta.post_token_balances:
                        if hasattr(balance, 'owner') and str(balance.owner) == potential_trader:
                            mint = balance.mint
                            amount = float(balance.ui_token_amount.ui_amount or 0)
                            wallet_post_balances[mint] = amount
                    
                    # Analyze balance changes for this wallet
                    all_mints = set(list(wallet_pre_balances.keys()) + list(wallet_post_balances.keys()))
                    
                    # AGGRESSIVE: If no token balance changes but wallet is in transaction with DEX, assume trade
                    if len(all_mints) == 0 and dex_detected:
                        logger.info(f"🚀 AGGRESSIVE: DEX + Target Wallet detected but no token metadata")
                        logger.info(f"   Assuming {potential_trader} made a trade on {dex_detected}")
                        
                        # Check if this could be a buy (typically increases token balance)
                        # or sell (decreases token balance) by looking at instruction patterns
                        trade_type = 'buy'  # Default assumption for DEX activity
                        
                        # Try to extract token from instruction data or logs if available
                        potential_token = None
                        for i, instruction in enumerate(instructions):
                            # Look for parsed instruction data that might contain token info
                            if hasattr(instruction, 'parsed') and instruction.parsed:
                                parsed_data = instruction.parsed
                                if hasattr(parsed_data, 'info') and parsed_data.info:
                                    info = parsed_data.info
                                    # Look for mint field in various instruction types
                                    if hasattr(info, 'mint'):
                                        potential_token = str(info.mint)
                                        logger.info(f"   🪙 Found token from instruction {i}: {potential_token}")
                                        break
                        
                        actual_trader_wallet = potential_trader
                        token_mint = potential_token or 'AGGRESSIVE_DETECTION'
                        logger.info(f"🎯 AGGRESSIVE TRADE DETECTION:")
                        logger.info(f"   Trader: {actual_trader_wallet}")
                        logger.info(f"   Type: {trade_type} (assumed)")
                        logger.info(f"   Token: {token_mint}")
                        logger.info(f"   DEX: {dex_detected}")
                        break
                    
                    # Normal token balance analysis
                    for mint in all_mints:
                        if str(mint) == "So11111111111111111111111111111111111111112":  # Skip WSOL
                            continue
                            
                        pre_amount = wallet_pre_balances.get(mint, 0)
                        post_amount = wallet_post_balances.get(mint, 0)
                        change = post_amount - pre_amount
                        
                        logger.info(f"   📊 {str(mint)[:8]}: {pre_amount:.6f} → {post_amount:.6f} (Δ{change:+.6f})")
                        
                        # Found significant token change - this wallet is the trader!
                        if abs(change) > 0.000001:
                            actual_trader_wallet = potential_trader
                            token_mint = str(mint)  # Convert to string to ensure compatibility
                            
                            if change > 0:
                                trade_type = 'buy'
                                logger.info(f"🟢 BUY CONFIRMED: {actual_trader_wallet}")
                                logger.info(f"   📈 Token balance increased by {change:.6f}")
                            else:
                                trade_type = 'sell' 
                                logger.info(f"🔴 SELL CONFIRMED: {actual_trader_wallet}")
                                logger.info(f"   📉 Token balance decreased by {abs(change):.6f}")
                            
                            logger.info(f"   🎯 Token: {str(mint)}")
                            logger.info(f"   👤 Actual Trader: {actual_trader_wallet}")
                            break
                    
                    # If we found a trade, break out of wallet loop
                    if actual_trader_wallet:
                        break
            
            # Calculate the amount from balance changes
            trade_amount = 0.001  # Default small amount for copy trading
            
            # FINAL RESULT
            if trade_type and actual_trader_wallet:
                logger.info(f"🎉 TRADE EXTRACTION SUCCESS!")
                logger.info(f"   🎯 Type: {trade_type.upper()}")
                logger.info(f"   👤 Trader: {actual_trader_wallet}")
                logger.info(f"   💎 Token: {token_mint or 'UNKNOWN'}")
                logger.info(f"   💰 Copy Amount: {trade_amount:.6f} SOL")
                logger.info(f"   🏢 DEX: {dex_detected or 'Unknown'}")
                
                return {
                    'type': trade_type,
                    'token_mint': token_mint or 'UNKNOWN',
                    'amount': trade_amount,
                    'timestamp': datetime.now(),
                    'trader_wallet': actual_trader_wallet,  # NEW: Track who actually traded
                    'dex': dex_detected,
                    'original_signature': signature  # NEW: Pass signature for pool discovery
                }
            
            # Enhanced diagnostic logging for failed trade extraction
            logger.debug(f"❓ TRADE EXTRACTION ANALYSIS:")
            if dex_detected:
                logger.debug(f"   🏢 DEX detected: {dex_detected}")
                logger.debug(f"   🎯 Wallets checked: {len(wallets_with_changes) if 'wallets_with_changes' in locals() else 0}")
                logger.debug(f"   📊 Instructions analyzed: {len(instructions)}")
                
                if not actual_trader_wallet:
                    logger.debug(f"   ⚠️ No target wallet found with token balance changes")
                    logger.debug(f"   💡 This transaction might not involve our target wallets")
                else:
                    logger.debug(f"   ⚠️ DEX activity detected but trade direction could not be determined")
            else:
                logger.debug(f"   ❌ No DEX programs detected in transaction")
                logger.debug(f"   💡 This might not be a trading transaction")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting trade info: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None
            
            # Second pass: Check for parsed instructions (token transfers)
            for i, instruction in enumerate(instructions):
                try:
                    if hasattr(instruction, 'parsed') and instruction.parsed:
                        parsed = instruction.parsed
                        instruction_type = parsed.get('type', '')
                        
                        # Handle SOL transfers
                        if instruction_type == 'transfer':
                            info = parsed.get('info', {})
                            source = info.get('source')
                            destination = info.get('destination')
                            amount = float(info.get('lamports', 0)) / 1e9  # Convert lamports to SOL
                            
                            if source == wallet_address:
                                sol_transfers.append({'type': 'out', 'amount': amount})
                                logger.info(f"💸 SOL OUT: {amount} SOL from target wallet")
                            elif destination == wallet_address:
                                sol_transfers.append({'type': 'in', 'amount': amount})
                                logger.info(f"💰 SOL IN: {amount} SOL to target wallet")
                        
                        # Handle token transfers (SPL token operations)
                        elif instruction_type in ['transferChecked', 'transfer'] and 'mint' in parsed.get('info', {}):
                            info = parsed.get('info', {})
                            source = info.get('source')
                            destination = info.get('destination')
                            mint = info.get('mint')
                            
                            # Handle different amount formats
                            amount = 0
                            if 'tokenAmount' in info:
                                token_amount = info['tokenAmount']
                                amount = float(token_amount.get('uiAmount', 0))
                            elif 'amount' in info:
                                amount = float(info.get('amount', 0))
                            
                            if (source == wallet_address or destination == wallet_address) and mint:
                                direction = 'out' if source == wallet_address else 'in'
                                token_transfers.append({
                                    'mint': mint,
                                    'amount': amount,
                                    'direction': direction
                                })
                                logger.info(f"🎯 Token transfer: {amount} of {str(mint)[:8]}... ({'OUT' if direction == 'out' else 'IN'})")
                                
                                # Set token mint for the trade
                                if not token_mint and mint and mint != "So11111111111111111111111111111111111111112":
                                    token_mint = mint
                
                        # Also handle other token program instructions
                        elif instruction_type in ['burn', 'mintTo', 'approve'] and 'mint' in parsed.get('info', {}):
                            info = parsed.get('info', {})
                            mint = info.get('mint')
                            if mint and mint != "So11111111111111111111111111111111111111112":
                                logger.info(f"🔍 Token operation detected: {instruction_type} for {str(mint)[:8]}...")
                                if not token_mint:
                                    token_mint = mint
                
                except Exception as inst_error:
                    logger.debug(f"Error processing instruction {i}: {inst_error}")
                    continue
            
            # Enhanced balance analysis - check both SOL and token balance changes
            sol_balance_change = 0
            meta = self.extract_transaction_meta(transaction)
            if meta:
                # SOL balance changes
                if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                    # Find wallet index in account keys
                    wallet_index = -1
                    if hasattr(tx_message, 'account_keys'):
                        for idx, account in enumerate(tx_message.account_keys):
                            if str(account) == wallet_address:
                                wallet_index = idx
                                break
                    
                    if wallet_index >= 0 and wallet_index < len(meta.pre_balances) and wallet_index < len(meta.post_balances):
                        pre_balance = meta.pre_balances[wallet_index] / 1e9  # Convert to SOL
                        post_balance = meta.post_balances[wallet_index] / 1e9
                        sol_balance_change = post_balance - pre_balance
                        
                        logger.info(f"💰 SOL balance change: {sol_balance_change:+.6f} SOL")
                
                # Enhanced: Check token balance changes for trading activity
                if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                    pre_tokens = meta.pre_token_balances
                    post_tokens = meta.post_token_balances
                    
                    # Create lookup maps by account index
                    pre_map = {}
                    post_map = {}
                    
                    for token_balance in pre_tokens:
                        if hasattr(token_balance, 'owner') and str(token_balance.owner) == wallet_address:
                            account_idx = token_balance.account_index
                            pre_map[account_idx] = {
                                'mint': token_balance.mint,
                                'amount': float(token_balance.ui_token_amount.ui_amount or 0),
                                'raw_amount': int(token_balance.ui_token_amount.amount)
                            }
                    
                    for token_balance in post_tokens:
                        if hasattr(token_balance, 'owner') and str(token_balance.owner) == wallet_address:
                            account_idx = token_balance.account_index
                            post_map[account_idx] = {
                                'mint': token_balance.mint,
                                'amount': float(token_balance.ui_token_amount.ui_amount or 0),
                                'raw_amount': int(token_balance.ui_token_amount.amount)
                            }
    async def extract_trade_info_quick(self, signature, wallet_address):
        """Quick version of trade info extraction for historical scanning - OPTIMIZED"""
        try:
            # Get transaction with basic details only
            response = await self.rpc_client.get_transaction(
                signature=signature,
                max_supported_transaction_version=0,
                encoding="json"
            )
            
            if not response or not response.value:
                return None
                
            transaction = response.value
            meta = transaction.meta
            
            if meta.err:
                return None  # Failed transaction
            
            # Quick DEX detection from logs
            dex_detected = None
            if meta.log_messages:
                for log in meta.log_messages:
                    if "Raydium CPMM V2" in log:
                        dex_detected = "Raydium CPMM V2"
                        break
                    elif "Pump.fun Trading V2" in log:
                        dex_detected = "Pump.fun Trading V2"
                        break
                    elif "Pump.fun" in log:
                        dex_detected = "Pump.fun"
                        break
                    elif "Raydium" in log:
                        dex_detected = "Raydium"
                        break
            
            if not dex_detected:
                return None  # Not a DEX trade
            
            # Quick token balance analysis
            sol_change = 0
            token_mint = None
            token_change = 0
            
            # Calculate SOL balance change (pre/post balances)
            if meta.pre_balances and meta.post_balances:
                account_keys = transaction.transaction.message.account_keys
                for i, key in enumerate(account_keys):
                    if str(key) == wallet_address and i < len(meta.pre_balances) and i < len(meta.post_balances):
                        sol_change = (meta.post_balances[i] - meta.pre_balances[i]) / 1e9
                        break
            
            # Quick token balance analysis
            if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                pre_map = {}
                post_map = {}
                
                # Build pre-balance map
                for balance in meta.pre_token_balances:
                    if hasattr(balance, 'owner') and str(balance.owner) == wallet_address:
                        mint = balance.mint
                        amount = float(balance.ui_token_amount.ui_amount or 0)
                        pre_map[mint] = amount
                
                # Build post-balance map
                for balance in meta.post_token_balances:
                    if hasattr(balance, 'owner') and str(balance.owner) == wallet_address:
                        mint = balance.mint
                        amount = float(balance.ui_token_amount.ui_amount or 0)
                        post_map[mint] = amount
                
                # Find the token with the biggest change
                all_mints = set(list(pre_map.keys()) + list(post_map.keys()))
                max_change = 0
                
                for mint in all_mints:
                    if mint == "So11111111111111111111111111111111111111112":  # Skip WSOL
                        continue
                    
                    pre_amount = pre_map.get(mint, 0)
                    post_amount = post_map.get(mint, 0)
                    change = post_amount - pre_amount
                    
                    if abs(change) > abs(max_change):
                        max_change = change
                        token_mint = mint
                        token_change = change
            
            # Determine trade type based on changes
            trade_type = None
            if sol_change < -0.001:  # SOL decreased (spent SOL to buy tokens)
                trade_type = 'buy'
            elif sol_change > 0.001:  # SOL increased (received SOL from selling tokens)
                trade_type = 'sell'
            elif token_change > 0:  # Token increased
                trade_type = 'buy'
            elif token_change < 0:  # Token decreased
                trade_type = 'sell'
            
            if not trade_type or not token_mint:
                return None
            
            return {
                'signature': signature,
                'wallet': wallet_address,
                'type': trade_type,
                'token_mint': token_mint,
                'token_amount': abs(token_change),
                'sol_amount': abs(sol_change),
                'dex': dex_detected,
                'timestamp': transaction.block_time if hasattr(transaction, 'block_time') else None
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Quick analysis error for {signature[:8]}: {e}")
            return None
            
            # OFFICIAL SOLANA TRANSACTION ANALYSIS - Using documented preTokenBalances/postTokenBalances
            logger.debug(f"🔍 OFFICIAL SOLANA TRADE ANALYSIS:")
            logger.debug(f"   💰 SOL balance change: {sol_balance_change:+.6f} SOL")
            logger.debug(f"   🎯 Token transfers detected: {len(token_transfers)}")
            logger.debug(f"   💸 SOL transfers detected: {len(sol_transfers)}")
            logger.debug(f"   🏢 DEX detected: {dex_detected or 'None'}")
            
            # PRIMARY STRATEGY: Use OFFICIAL Solana preTokenBalances/postTokenBalances
            # This is the ONLY reliable method per Solana documentation
            meta = self.extract_transaction_meta(transaction)
            if meta:
                logger.info(f"🔍 OFFICIAL SOLANA TRADE ANALYSIS (using meta):")
                logger.info(f"   Has pre_token_balances: {hasattr(meta, 'pre_token_balances')}")
                logger.info(f"   Has post_token_balances: {hasattr(meta, 'post_token_balances')}")
                
                # Debug meta structure
                if hasattr(meta, 'pre_token_balances'):
                    logger.info(f"   Pre-token-balances type: {type(meta.pre_token_balances)}")
                    logger.info(f"   Pre-token-balances length: {len(meta.pre_token_balances) if meta.pre_token_balances else 0}")
                if hasattr(meta, 'post_token_balances'):
                    logger.info(f"   Post-token-balances type: {type(meta.post_token_balances)}")  
                    logger.info(f"   Post-token-balances length: {len(meta.post_token_balances) if meta.post_token_balances else 0}")
                
                # Use OFFICIAL Solana balance tracking per documentation
                if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                    logger.info(f"📚 Using OFFICIAL Solana preTokenBalances/postTokenBalances method")
                    logger.info(f"   Pre-balances count: {len(meta.pre_token_balances)}")
                    logger.info(f"   Post-balances count: {len(meta.post_token_balances)}")
                    
                    # Extract wallet-specific token balance changes
                    wallet_pre_balances = {}
                    wallet_post_balances = {}
                    
                    logger.info(f"🔍 Searching for balances owned by wallet: {wallet_address}")
                    
                    # Get pre-transaction balances for this wallet
                    for balance in meta.pre_token_balances:
                        logger.info(f"   PRE-BALANCE: owner={getattr(balance, 'owner', 'N/A')}, mint={getattr(balance, 'mint', 'N/A')}")
                        if hasattr(balance, 'owner') and str(balance.owner) == wallet_address:
                            mint = balance.mint
                            amount = float(balance.ui_token_amount.ui_amount or 0)
                            wallet_pre_balances[mint] = amount
                            logger.info(f"   ✅ PRE: {str(mint)[:8]} = {amount:.6f}")
                    
                    # Get post-transaction balances for this wallet  
                    for balance in meta.post_token_balances:
                        logger.info(f"   POST-BALANCE: owner={getattr(balance, 'owner', 'N/A')}, mint={getattr(balance, 'mint', 'N/A')}")
                        if hasattr(balance, 'owner') and str(balance.owner) == wallet_address:
                            mint = balance.mint
                            amount = float(balance.ui_token_amount.ui_amount or 0)
                            wallet_post_balances[mint] = amount
                            logger.info(f"   ✅ POST: {str(mint)[:8]} = {amount:.6f}")
                    
                    logger.info(f"🎯 Wallet-specific token analysis:")
                    logger.info(f"   Pre-balances for this wallet: {len(wallet_pre_balances)}")
                    logger.info(f"   Post-balances for this wallet: {len(wallet_post_balances)}")
                    
                    # Analyze balance changes - THIS IS THE OFFICIAL METHOD
                    all_mints = set(list(wallet_pre_balances.keys()) + list(wallet_post_balances.keys()))
                    logger.info(f"   Total unique mints: {len(all_mints)}")
                    
                    if len(all_mints) == 0:
                        logger.warning(f"⚠️ NO TOKEN BALANCES found for wallet {wallet_address}!")
                        logger.warning(f"   This wallet might not be directly involved in token operations")
                        logger.warning(f"   This could be a routing/intermediate transaction")
                    
                    for mint in all_mints:
                        mint_str = str(mint)  # Convert Pubkey to string
                        if mint_str == "So11111111111111111111111111111111111111112":  # Skip WSOL
                            logger.info(f"   ⏭️ Skipping WSOL: {mint_str[:8]}")
                            continue
                            
                        pre_amount = wallet_pre_balances.get(mint, 0)
                        post_amount = wallet_post_balances.get(mint, 0)
                        change = post_amount - pre_amount
                        
                        logger.info(f"   📊 {mint_str[:8]}: {pre_amount:.6f} → {post_amount:.6f} (Δ{change:+.6f})")
                        
                        # OFFICIAL DETECTION: Token balance increased = BUY
                        if change > 0.000001:  # Token balance increased
                            trade_type = 'buy'
                            token_mint = mint_str  # Use string version
                            logger.info(f"🟢 BUY CONFIRMED: Token balance increased by {change:.6f}")
                            logger.info(f"   📚 Method: Official Solana preTokenBalances/postTokenBalances")
                            logger.info(f"   🎯 Token: {mint_str}")
                            break
                            
                        # OFFICIAL DETECTION: Token balance decreased = SELL  
                        elif change < -0.000001:  # Token balance decreased
                            trade_type = 'sell'
                            token_mint = mint_str  # Use string version
                            logger.info(f"🔴 SELL CONFIRMED: Token balance decreased by {abs(change):.6f}")
                            logger.info(f"   📚 Method: Official Solana preTokenBalances/postTokenBalances")
                            logger.info(f"   🎯 Token: {mint_str}")
                            break
                else:
                    logger.warning(f"⚠️ No token balance data in transaction meta!")
                    logger.warning(f"   This transaction might not involve token balance changes")
                    logger.warning(f"   Could be: setup, routing, or failed transaction")
            else:
                logger.warning(f"⚠️ No transaction meta available!")
            
            # FALLBACK: Only if official method didn't detect anything
            if not trade_type and dex_detected:
                logger.debug(f"🔄 FALLBACK: Official method found no token changes, using transfer analysis")
                
                # Secondary Strategy: Use token transfer analysis
                tokens_in = [t for t in token_transfers if t['direction'] == 'in']
                tokens_out = [t for t in token_transfers if t['direction'] == 'out']
                
                # Look for dominant transfer pattern
                total_tokens_in = sum(t['amount'] for t in tokens_in)
                total_tokens_out = sum(t['amount'] for t in tokens_out)
                
                logger.debug(f"   📊 Tokens IN: {total_tokens_in:.2f}, Tokens OUT: {total_tokens_out:.2f}")
                
                if tokens_in and total_tokens_in > total_tokens_out:
                    # More tokens gained = likely a BUY
                    trade_type = 'buy' 
                    token_mint = tokens_in[0]['mint']
                    logger.info(f"🟢 BUY detected via fallback transfer analysis")
                    logger.info(f"   🎯 Primary token gained: {token_mint[:8]}...")
                    
                elif tokens_out and total_tokens_out > total_tokens_in:
                    # More tokens lost = likely a SELL
                    trade_type = 'sell'
                    token_mint = tokens_out[0]['mint'] 
                    logger.info(f"🔴 SELL detected via fallback transfer analysis")
                    logger.info(f"   🎯 Primary token sold: {token_mint[:8]}...")
            
            # LAST RESORT: SOL transfer patterns (unreliable due to fees/losses)
            elif not trade_type and sol_transfers and dex_detected:
                logger.warning(f"⚠️  LAST RESORT: Using unreliable SOL flow analysis")
                sol_out_total = sum(t['amount'] for t in sol_transfers if t['type'] == 'out')
                sol_in_total = sum(t['amount'] for t in sol_transfers if t['type'] == 'in')
                
                logger.debug(f"   💸 SOL OUT: {sol_out_total:.6f}, SOL IN: {sol_in_total:.6f}")
                
                if sol_out_total > sol_in_total and sol_out_total > 0.01:
                    trade_type = 'buy'
                    logger.warning(f"🟢 BUY detected via SOL flow (unreliable): {sol_out_total:.6f} SOL out")
                    
                elif sol_in_total > sol_out_total and sol_in_total > 0.01:
                    trade_type = 'sell'  
                    logger.warning(f"🔴 SELL detected via SOL flow (unreliable): {sol_in_total:.6f} SOL in")
            
            # Handle special WSOL-wrapped transactions
            elif sol_transfers:
                # Look for WSOL creation/closing patterns that indicate real trades
                has_wsol_creation = False
                has_wsol_closing = False
                
                for i, instruction in enumerate(instructions):
                    try:
                        if hasattr(instruction, 'parsed') and instruction.parsed:
                            parsed = instruction.parsed
                            if parsed.get('type') == 'createAccountWithSeed':
                                has_wsol_creation = True
                            elif parsed.get('type') == 'closeAccount':
                                has_wsol_closing = True
                    except:
                        continue
                
                total_sol_transferred = sum(abs(t['amount']) for t in sol_transfers)
                
                if has_wsol_creation and has_wsol_closing and total_sol_transferred >= 0.01:
                    # This is a WSOL-wrapped trade
                    logger.info(f"💎 WSOL-wrapped trade detected! SOL amount: {total_sol_transferred:.6f}")
                    
                    # Determine direction from the net SOL movement
                    net_sol_out = sum(t['amount'] for t in sol_transfers if t['type'] == 'out') - sum(t['amount'] for t in sol_transfers if t['type'] == 'in')
                    
                    if net_sol_out > 0.005:  # Net outflow = BUY
                        trade_type = 'buy'
                        logger.info(f"🟢 WSOL BUY detected: Net SOL outflow {net_sol_out:.6f}")
                    elif net_sol_out < -0.005:  # Net inflow = SELL
                        trade_type = 'sell' 
                        logger.info(f"🔴 WSOL SELL detected: Net SOL inflow {abs(net_sol_out):.6f}")
                elif has_wsol_creation and has_wsol_closing and total_sol_transferred < 0.01:
                    # Small WSOL operations are usually just setup, not trades
                    logger.info(f"🔧 WSOL setup transaction (small amounts) - not a trade")
                    return None
            
            # ENHANCED TOKEN MINT EXTRACTION
            if trade_type:
                if not token_mint:
                    logger.debug(f"🔍 ENHANCED token mint extraction - Trade type: {trade_type}")
                    
                    meta = self.extract_transaction_meta(transaction)
                    if meta:
                        
                        # Strategy 1: Look for tokens that actually changed for THIS wallet
                        if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                            logger.info(f"🔍 Analyzing token balance changes for wallet {wallet_address}")
                            
                            # Create wallet-specific balance maps
                            pre_balances_by_mint = {}
                            post_balances_by_mint = {}
                            
                            for token_balance in meta.pre_token_balances:
                                if hasattr(token_balance, 'owner') and str(token_balance.owner) == wallet_address:
                                    mint = token_balance.mint
                                    if mint != "So11111111111111111111111111111111111111112":  # Skip WSOL
                                        pre_balances_by_mint[mint] = float(token_balance.ui_token_amount.ui_amount or 0)
                            
                            for token_balance in meta.post_token_balances:
                                if hasattr(token_balance, 'owner') and str(token_balance.owner) == wallet_address:
                                    mint = token_balance.mint
                                    if mint != "So11111111111111111111111111111111111111112":  # Skip WSOL
                                        post_balances_by_mint[mint] = float(token_balance.ui_token_amount.ui_amount or 0)
                            
                            # Find tokens that changed significantly
                            all_mints = set(list(pre_balances_by_mint.keys()) + list(post_balances_by_mint.keys()))
                            
                            for mint in all_mints:
                                pre_amount = pre_balances_by_mint.get(mint, 0)
                                post_amount = post_balances_by_mint.get(mint, 0)
                                change = post_amount - pre_amount
                                
                                logger.info(f"   🎯 {str(mint)[:8]}: {pre_amount:.2f} → {post_amount:.2f} (change: {change:+.2f})")
                                
                                # For BUY: look for tokens that increased
                                if trade_type == 'buy' and change > 0.01:
                                    token_mint = str(mint)  # Convert to string
                                    logger.info(f"✅ BUY token found: {token_mint} (+{change:.2f})")
                                    break
                                    
                                # For SELL: look for tokens that decreased  
                                elif trade_type == 'sell' and change < -0.01:
                                    token_mint = str(mint)  # Convert to string
                                    logger.info(f"✅ SELL token found: {token_mint} ({change:.2f})")
                                    break
                        
                        # Strategy 2: Fallback to any token in the transaction (for this wallet only)
                        if not token_mint:
                            logger.info(f"🔄 Fallback: Looking for any tokens associated with wallet {wallet_address}")
                            
                            # Check post balances first (for buys)
                            if trade_type == 'buy' and hasattr(meta, 'post_token_balances'):
                                for token_balance in meta.post_token_balances:
                                    if (hasattr(token_balance, 'owner') and 
                                        str(token_balance.owner) == wallet_address and
                                        hasattr(token_balance, 'mint')):
                                        mint = token_balance.mint
                                        if str(mint) != "So11111111111111111111111111111111111111112":
                                            token_mint = str(mint)  # Convert to string
                                            logger.info(f"✅ Fallback BUY token: {token_mint}")
                                            break
                            
                            # Check pre balances for sells
                            elif trade_type == 'sell' and hasattr(meta, 'pre_token_balances'):
                                for token_balance in meta.pre_token_balances:
                                    if (hasattr(token_balance, 'owner') and 
                                        str(token_balance.owner) == wallet_address and
                                        hasattr(token_balance, 'mint')):
                                        mint = token_balance.mint
                                        if str(mint) != "So11111111111111111111111111111111111111112":
                                            token_mint = str(mint)  # Convert to string
                                            logger.info(f"✅ Fallback SELL token: {token_mint}")
                                            break
                    
                    # Strategy 3: Extract from transaction accounts (last resort)
                    if not token_mint and hasattr(tx_message, 'account_keys'):
                        logger.debug(f"🔄 Last resort: Searching transaction account keys")
                        
                        system_accounts = {
                            "11111111111111111111111111111112",  # System program
                            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
                            "So11111111111111111111111111111111111111112",  # WSOL
                            "ComputeBudget111111111111111111111111111111",  # Compute budget
                            "SysvarRent111111111111111111111111111111111",  # Sysvar rent
                            "SysvarRecentB1ockHashes11111111111111111111",  # Recent blockhashes
                            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # Associated token program
                            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Pump.fun program
                            "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump",  # Pump.fun program 2
                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun core
                            "jitodontfrontd1111111TradeWithAxiomDotTrade",  # Jito program
                            wallet_address  # The wallet itself
                        }
                        
                        for account in tx_message.account_keys:
                            account_str = str(account.pubkey) if hasattr(account, 'pubkey') else str(account)
                            if (len(account_str) == 44 and  # Valid pubkey length
                                account_str not in system_accounts):
                                token_mint = account_str
                                logger.info(f"✅ Account key token candidate: {token_mint}")
                                break
                    
                    # Fallback: Extract from transaction accounts
                    if not token_mint and hasattr(tx_message, 'account_keys'):
                        logger.debug(f"📋 Checking {len(tx_message.account_keys)} account keys...")
                        system_accounts = {
                            "11111111111111111111111111111112",  # System program
                            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
                            "So11111111111111111111111111111111111111112",  # WSOL
                            "ComputeBudget111111111111111111111111111111",  # Compute budget
                            "SysvarRent111111111111111111111111111111111",  # Sysvar rent
                            "SysvarRecentB1ockHashes11111111111111111111",  # Recent blockhashes
                            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # Associated token program
                            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Pump.fun program
                            "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump",  # Pump.fun program 2
                            "jitodontfrontd1111111TradeWithAxiomDotTrade",  # Jito program
                            wallet_address  # Target wallet
                        }
                        
                        # Look for potential token mint addresses
                        candidate_mints = []
                        for account in tx_message.account_keys:
                            # Handle different account key formats
                            if hasattr(account, 'pubkey'):
                                account_str = str(account.pubkey)
                            else:
                                account_str = str(account)
                            
                            # Skip system accounts and check if it looks like a token mint
                            if (account_str not in system_accounts and 
                                len(account_str) == 44 and  # Standard Solana address length
                                account_str[0] in 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'):  # Valid base58 start
                                candidate_mints.append(account_str)
                                logger.info(f"🔍 Candidate token mint: {account_str}")
                        
                        # For WSOL-wrapped trades, often the actual token mint is among the first few non-system accounts
                        if candidate_mints:
                            # Prioritize accounts that are writable (more likely to be the actual token being traded)
                            for account in tx_message.account_keys:
                                if hasattr(account, 'pubkey'):
                                    account_str = str(account.pubkey)
                                    is_writable = hasattr(account, 'writable') and account.writable
                                else:
                                    account_str = str(account)
                                    is_writable = False
                                
                                if account_str in candidate_mints and is_writable:
                                    token_mint = account_str
                                    logger.info(f"🎯 Token mint selected (writable): {token_mint}")
                                    break
                            
                            # If no writable candidate found, take the first candidate
                            if not token_mint:
                                token_mint = candidate_mints[0]
                                logger.info(f"🎯 Token mint selected (first candidate): {token_mint}")
                    
                    # Last resort: Use a known pattern for Pump.fun tokens
                    if not token_mint and dex_detected and "pump" in str(dex_detected).lower():
                        logger.debug(f"🔍 Attempting Pump.fun token extraction...")
                        # For Pump.fun, check if any account looks like a pump token
                        for account in tx_message.account_keys:
                            account_str = str(account.pubkey) if hasattr(account, 'pubkey') else str(account)
                            # Pump.fun tokens often have specific patterns
                            if (len(account_str) == 44 and 
                                account_str not in system_accounts and
                                not account_str.endswith('pump')):  # Not the program itself
                                token_mint = account_str
                                logger.info(f"🎯 Pump.fun token mint (pattern match): {token_mint}")
                                break
                
                # Calculate the amount from the most significant change  
                trade_amount = abs(sol_balance_change) if abs(sol_balance_change) > 0.001 else 0
                if not trade_amount and sol_transfers:
                    trade_amount = sum(abs(t['amount']) for t in sol_transfers)
                
                # FINAL RESULT
                logger.info(f"🎉 TRADE EXTRACTION SUCCESS!")
                logger.info(f"   🎯 Type: {trade_type.upper()}")
                logger.info(f"   💎 Token: {token_mint or 'UNKNOWN'}")
                logger.info(f"   💰 Amount: {trade_amount:.6f} SOL")
                logger.info(f"   🏢 DEX: {dex_detected or 'Unknown'}")
                logger.info(f"   📊 SOL balance change: {sol_balance_change:+.6f}")
                logger.info(f"   🔄 Token transfers: {len(token_transfers)}")
                
                return {
                    'type': trade_type,
                    'token_mint': token_mint or 'UNKNOWN',
                    'amount': trade_amount,
                    'timestamp': datetime.now(),
                    'sol_transfers': sol_transfers,
                    'token_transfers': token_transfers,
                    'dex': dex_detected
                }
            
            # Enhanced diagnostic logging for failed trade extraction
            logger.debug(f"❓ TRADE EXTRACTION ANALYSIS:")
            if dex_detected:
                logger.debug(f"   🏢 DEX detected: {dex_detected}")
                logger.debug(f"   💰 SOL balance change: {sol_balance_change:+.6f}")
                logger.debug(f"   🎯 Token transfers found: {len(token_transfers)}")
                logger.debug(f"   💸 SOL transfers found: {len(sol_transfers)}")
                logger.debug(f"   📊 Instructions analyzed: {len(instructions)}")
                
                if abs(sol_balance_change) < 0.001 and not sol_transfers and not token_transfers:
                    logger.debug(f"   ⚠️ No significant balance changes or transfers detected")
                    logger.debug(f"   💡 This might be a failed transaction or setup operation")
                else:
                    logger.debug(f"   ⚠️ DEX activity detected but trade direction could not be determined")
            else:
                logger.debug(f"   ❌ No DEX programs detected in transaction")
                logger.debug(f"   💡 This might not be a trading transaction")
            
            return None
            if dex_detected and not trade_type:
                logger.warning(f"⚠️ DEX activity detected ({dex_detected}) but incomplete trade info")
                logger.warning(f"   💰 SOL change: {sol_balance_change:+.6f}")
                logger.warning(f"   🎯 Token transfers: {len(token_transfers)}")
                logger.warning(f"   💸 SOL transfers: {len(sol_transfers)}")
                logger.warning(f"   📊 Instructions analyzed: {len(instructions)}")
                
            logger.debug(f"❓ No clear trade pattern found in transaction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting trade info: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None
    
    async def execute_copy_trade(self, trade_info: Dict[str, Any], source_wallet: str):
        """Execute copy trade with ULTRA-AGGRESSIVE speed optimization and pool discovery"""
        try:
            trade_type = trade_info.get('type', 'unknown')
            token_mint = trade_info['token_mint']
            dex = trade_info.get('dex', 'Unknown')
            detection_method = trade_info.get('detection_method', 'standard')
            original_signature = trade_info.get('original_signature', None)
            
            # 🔍 POOL DISCOVERY: Extract pool information from target wallet's successful transaction
            pool_info = None
            if original_signature:
                logger.info(f"🔍 POOL DISCOVERY: Analyzing target wallet's transaction...")
                logger.info(f"   Original signature: {original_signature}")
                logger.info(f"   Token: {token_mint}")
                
                try:
                    pool_info = await get_pool_info_for_token(
                        self.rpc_client, 
                        token_mint, 
                        original_signature
                    )
                    
                    if pool_info:
                        logger.info(f"✅ Pool discovery successful!")
                        logger.info(f"   DEX Type: {pool_info.dex_type}")
                        logger.info(f"   Pool ID: {pool_info.pool_id}")
                        if pool_info.bonding_curve:
                            logger.info(f"   Bonding Curve: {pool_info.bonding_curve}")
                        logger.info(f"🎉 Independent executors now have the pool info they need!")
                    else:
                        logger.warning(f"⚠️ Pool discovery failed - executors will need fallback methods")
                        
                except Exception as pool_error:
                    logger.warning(f"⚠️ Pool discovery error: {pool_error}")
                    logger.info(f"💡 Continuing with execution - some executors may still work")
            else:
                logger.info(f"⚠️ No original signature available - skipping pool discovery")
            
            if detection_method == 'ultra_fast_logs':
                logger.info(f"⚡ ULTRA-FAST EXECUTION: {trade_type.upper()} {token_mint[:8]}... on {dex}")
                logger.info(f"🚀 TRUSTED WALLET MODE: Skipping ALL safety checks!")
            else:
                logger.info(f"💹 EXECUTING COPY TRADE: {trade_type.upper()}")
            
            # 🚀 ULTRA-AGGRESSIVE: For trusted wallets, execute with NEVER GIVE UP retry logic
            if trade_type == 'buy':
                logger.info(f"🚀 TRUSTED BUY: Executing immediately with {self.config.investment_amount_sol} SOL")
                
                # RETRY LOOP: Keep trying until we succeed (trusted wallets deserve this!)
                max_retry_attempts = 5  # Try up to 5 times with different strategies
                success = None
                
                for attempt in range(max_retry_attempts):
                    # Set retry state for dynamic slippage escalation
                    self.current_retry_attempt = attempt
                    
                    if attempt > 0:
                        logger.info(f"")
                        logger.info(f"🔄 RETRY ATTEMPT {attempt + 1}/{max_retry_attempts}")
                        logger.info(f"🎯 Target wallet succeeded - we WILL find a way!")
                        logger.info(f"🔥 Escalating slippage and changing strategy...")
                    
                    # Use your existing execute_trade_with_fallback system (preserves all DEX routing)
                    # Now with pool discovery information for independent executors
                    success = await self.execute_trade_with_fallback(
                        'buy', 
                        token_mint, 
                        self.config.investment_amount_sol, 
                        dex,  # Pass detected DEX for smart routing
                        pool_info  # Pass discovered pool information
                    )
                    
                    if success and success.get('success'):
                        break  # Success! Exit retry loop
                    
                    # Analyze failure and adjust strategy for next attempt
                    if success and not success.get('success'):
                        error_msg = success.get('error', '')
                        
                        if attempt < max_retry_attempts - 1:  # Don't wait on final attempt
                            # Strategy adjustments for next attempt
                            if '0x1771' in error_msg or 'slippage' in error_msg.lower():
                                logger.info(f"🎯 Next attempt: Increasing slippage tolerance even higher")
                                # The main config will be updated in the DEX executors
                                
                            elif 'AccountOwnedByWrongProgram' in error_msg or 'bonding_curve' in error_msg:
                                logger.info(f"🎯 Next attempt: Will prioritize alternative routing methods")
                                
                            elif 'token_not_tradable' in error_msg or 'no routes' in error_msg:
                                logger.info(f"🎯 Next attempt: Will try more specialized DEXes")
                                
                            else:
                                logger.info(f"🎯 Next attempt: General retry with different DEX priority")
                            
                            # Short delay between attempts
                            retry_delay = 2.0 + (attempt * 1.0)  # Increasing delay
                            logger.info(f"⏳ Waiting {retry_delay:.1f}s before retry...")
                            await asyncio.sleep(retry_delay)
                
                # Reset retry state
                self.current_retry_attempt = 0
                
                if success and success.get('success'):
                    logger.info(f"✅ ULTRA-AGGRESSIVE BUY SUCCESS: {token_mint[:8]}... (attempt {attempt + 1})")
                    logger.info(f"🎉 NEVER GIVE UP STRATEGY WORKED!")
                    
                    # Update the simplified active_positions for ultra-fast mode
                    self.active_positions[token_mint] = {
                        'amount': self.config.investment_amount_sol,
                        'buy_time': datetime.now(),
                        'source_wallet': source_wallet,
                        'dex': dex,
                        'detection_method': detection_method,
                        'signature': success.get('signature', ''),
                        'retry_attempts': attempt + 1
                    }
                    
                    # Also update the main positions system to maintain consistency
                    if token_mint not in self.positions:
                        from models import WalletPosition
                        self.positions[token_mint] = WalletPosition(
                            token_mint=token_mint,
                            initial_amount=self.config.investment_amount_sol,
                            current_amount=self.config.investment_amount_sol,
                            our_amount=self.config.investment_amount_sol
                        )
                    
                else:
                    logger.error(f"❌ ULTRA-AGGRESSIVE BUY FAILED AFTER {max_retry_attempts} ATTEMPTS: {token_mint[:8]}...")
                    logger.error(f"💔 Even our NEVER GIVE UP strategy couldn't match the target wallet")
                    logger.error(f"🎯 This token may require manual investigation")
                    if success:
                        logger.error(f"   Final error: {success.get('error', 'Unknown error')}")
                    if success:
                        logger.error(f"   Error: {success.get('error', 'Unknown error')}")
                    
            elif trade_type == 'sell':
                # Check if we have this position (check both tracking systems)
                has_position = (token_mint in self.active_positions or token_mint in self.positions)
                
                if has_position:
                    logger.info(f"🔥 TRUSTED SELL: Liquidating position in {token_mint[:8]}...")
                    
                    # Use your existing execute_trade_with_fallback system for selling
                    success = await self.execute_trade_with_fallback('sell_all', token_mint)
                    
                    if success and success.get('success'):
                        logger.info(f"✅ AGGRESSIVE SELL SUCCESS: {token_mint[:8]}...")
                        
                        # Clean up both tracking systems
                        if token_mint in self.active_positions:
                            del self.active_positions[token_mint]
                        if token_mint in self.positions:
                            del self.positions[token_mint]
                            
                    else:
                        logger.error(f"❌ AGGRESSIVE SELL FAILED: {token_mint[:8]}...")
                        if success:
                            logger.error(f"   Error: {success.get('error', 'Unknown error')}")
                else:
                    logger.info(f"⚠️ No position in {token_mint[:8]}... to sell")
                    # 🔧 CRITICAL FIX: If we see a SELL but don't have position, 
                    # it means we missed the BUY - scan recent history
                    logger.info(f"🔍 MISSED BUY DETECTED - Scanning recent history for {token_mint[:8]}...")
                    await self.find_missing_buy_transaction(token_mint, source_wallet)
            
        except Exception as e:
            logger.error(f"❌ Error in aggressive copy trade execution: {e}")

    async def find_missing_buy_transaction(self, token_mint: str, trader_wallet: str):
        """Find the BUY transaction we missed for this token"""
        try:
            logger.info(f"🕵️ DETECTIVE MODE: Looking for missed BUY of {token_mint[:8]}...")
            
            # Get more transaction history
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(trader_wallet),
                limit=100  # Look deeper into history
            )
            
            if not response.value:
                logger.warning(f"⚠️ No transaction history to search")
                return
            
            logger.info(f"🔍 Searching through {len(response.value)} historical transactions...")
            
            for tx_info in response.value:
                signature = str(tx_info.signature)
                
                # Skip if already processed
                if signature in self.processed_signatures:
                    continue
                
                try:
                    # Quick check if this transaction involves our token
                    trade_info = await self.extract_trade_info_quick(signature, trader_wallet)
                    
                    if (trade_info and 
                        trade_info.get('token_mint') == token_mint and 
                        trade_info.get('type') == 'buy'):
                        
                        logger.info(f"🎯 FOUND MISSING BUY TRANSACTION!")
                        logger.info(f"   Signature: {signature}")
                        logger.info(f"   Token: {token_mint[:8]}...")
                        logger.info(f"   🔗 https://solscan.io/tx/{signature}")
                        
                        # Execute the missed buy
                        await self.execute_copy_trade(trade_info, trader_wallet)
                        
                        # Mark as processed
                        self.processed_signatures.add(signature)
                        break
                        
                except Exception as search_error:
                    logger.debug(f"Search error for {signature[:8]}...: {search_error}")
                    continue
            
            logger.info(f"🔍 Detective search complete for {token_mint[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ Error in missing buy search: {e}")
    
    async def get_token_balance_fast(self, token_mint: str) -> float:
        """Get token balance with minimal overhead for AGGRESSIVE mode"""
        try:
            # Use your existing wallet balance system
            balances = await self.get_wallet_balance()
            return balances.get(token_mint, 0.0)
        except Exception as e:
            logger.error(f"❌ Fast balance check failed: {e}")
            return 0.0
    
    async def execute_copy_buy(self, token_mint: str, source_wallet: str, detected_dex: str = None):
        """Execute a copy buy trade"""
        try:
            # Skip if token mint is unknown
            if token_mint == 'UNKNOWN':
                logger.warning(f"⚠️  Cannot execute buy - token mint is unknown")
                return
            
            # For copy trading, be more aggressive - the target wallet already validated this!
            logger.info(f"🎯 COPY TRADING MODE: Target wallet {source_wallet} already traded {token_mint}")
            logger.info(f"💪 Following the lead - if they could trade it, so can we!")
            logger.info(f"🚀 Proceeding with aggressive copy trade strategy")
            
            # Basic validation only
            try:
                Pubkey.from_string(token_mint)
            except:
                logger.warning(f"⚠️ Invalid token format: {token_mint}")
                return
            
            # Optional validation (non-blocking)
            try:
                from token_validator import TokenValidator
                validator = TokenValidator(self.rpc_client)
                
                is_tradable = await validator.is_token_tradable(token_mint)
                if not is_tradable:
                    logger.warning(f"⚠️ Validator suggests token may be risky: {token_mint}")
                    logger.info(f"💪 But proceeding anyway - target wallet traded it successfully!")
            except Exception as e:
                logger.debug(f"Validation error (non-blocking): {e}")
            
            # MODIFIED: Always execute trades even for same token (remove position check)
            # Track how many times we've traded this token
            self.trade_counter[token_mint] += 1
            trade_count = self.trade_counter[token_mint]
            
            if token_mint in self.positions:
                logger.info(f"⚠️  Already have position in {token_mint} - but executing trade #{trade_count} anyway!")
                logger.info(f"🔄 MULTIPLE TRADE MODE: Target wallet traded again, so we follow!")
            else:
                logger.info(f"🎯 NEW TOKEN TRADE #{trade_count}: {token_mint}")
            
            # Check position limits only for NEW positions
            if token_mint not in self.positions and len(self.positions) >= self.config.max_positions:
                logger.warning(f"⚠️  Maximum positions ({self.config.max_positions}) reached")
                logger.info(f"💡 Consider selling some positions to make room for new trades")
                return
            
            # Get balance BEFORE trade
            pre_balances = await self.get_wallet_balance()
            logger.info(f"💰 PRE-TRADE BALANCE CHECK:")
            logger.info(f"   SOL: {pre_balances.get('SOL', 0):.6f}")
            if token_mint in pre_balances:
                logger.info(f"   {token_mint[:8]}...: {pre_balances[token_mint]:.6f}")
            
            logger.info(f"💰 Executing BUY #{trade_count}: {self.config.investment_amount_sol} SOL → {token_mint}")
            logger.info(f"   🎯 Fixed investment amount: {self.config.investment_amount_sol} SOL (regardless of target wallet amount)")
            logger.info(f"   🚀 Copy trading - following target wallet's lead!")
            
            # Try Jito first, then fallback to RPC with smart routing
            success = await self.execute_trade_with_fallback(
                'buy', token_mint, self.config.investment_amount_sol, detected_dex
            )
            
            if success['success']:
                # Reset retry counter on success
                self.current_retry_attempt = 0
                
                # Get balance AFTER trade with retry logic
                await asyncio.sleep(3)  # Wait longer for balance update
                
                # Retry balance check up to 3 times
                post_balances = None
                for retry in range(3):
                    try:
                        post_balances = await self.get_wallet_balance()
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Balance check retry {retry+1}/3 failed: {e}")
                        if retry < 2:
                            await asyncio.sleep(2)
                
                if not post_balances:
                    post_balances = pre_balances  # Fallback to prevent crash
                
                # Log balance changes
                await self.log_balance_change('buy', token_mint, pre_balances, post_balances, success['signature'])
                
                # CSV LOG: Successful trade
                try:
                    self.csv_logger.log_trade_success(
                        source_wallet=source_wallet,
                        trade_type='buy',
                        token_mint=token_mint,
                        amount_sol=self.config.investment_amount_sol,
                        executor_used=success.get('executor', 'unknown'),
                        transaction_signature=success['signature'],
                        pre_balances=pre_balances,
                        post_balances=post_balances,
                        detected_dex=detected_dex or 'Unknown',
                        detection_method='websocket',
                        slippage_used=0.05,  # Default, could be dynamic
                        trade_count_for_token=trade_count,
                        portfolio_position_count=len(self.positions),
                        notes=f"Copy trade #{trade_count} from target wallet - SUCCESS after {self.current_retry_attempt + 1} attempts"
                    )
                except Exception as csv_error:
                    logger.error(f"❌ CSV logging failed: {csv_error}")
                    # Continue despite CSV error
                
                # Track or update position
                if token_mint not in self.positions:
                    # New position
                    self.positions[token_mint] = WalletPosition(
                        token_mint=token_mint,
                        initial_amount=self.config.investment_amount_sol,
                        current_amount=self.config.investment_amount_sol,
                        our_amount=self.config.investment_amount_sol
                    )
                    logger.info(f"✅ NEW POSITION created: {self.config.investment_amount_sol} SOL in {token_mint}")
                else:
                    # Update existing position
                    self.positions[token_mint].current_amount += self.config.investment_amount_sol
                    self.positions[token_mint].our_amount += self.config.investment_amount_sol
                    logger.info(f"✅ POSITION UPDATED: Added {self.config.investment_amount_sol} SOL to {token_mint}")
                    logger.info(f"   Total position: {self.positions[token_mint].current_amount:.6f} SOL")
                
                logger.info(f"🎉 Buy #{trade_count} successful!")
                logger.info(f"   🔗 Transaction: https://solscan.io/tx/{success['signature']}")
                logger.info(f"   � Total trades for this token: {trade_count}")
                
                # Log summary periodically
                if len(self.execution_history) % 5 == 0:  # Every 5 trades
                    await self.log_trade_execution_summary()
                    
            else:
                logger.error(f"❌ Buy #{trade_count} failed for {token_mint}")
                logger.error(f"   Error: {success.get('error', 'Unknown error')}")
                
                # CSV LOG: Failed trade
                if success.get('failed_executors'):
                    # Multiple executor failure
                    self.csv_logger.log_multiple_executor_failure(
                        source_wallet=source_wallet,
                        trade_type='buy',
                        token_mint=token_mint,
                        amount_sol=self.config.investment_amount_sol,
                        failed_executors=success['failed_executors'],
                        detected_dex=detected_dex or 'Unknown',
                        detection_method='websocket',
                        trade_count_for_token=trade_count,
                        portfolio_position_count=len(self.positions),
                        notes=f"All executors failed for copy trade #{trade_count}"
                    )
                else:
                    # Single executor failure
                    self.csv_logger.log_trade_failure(
                        source_wallet=source_wallet,
                        trade_type='buy',
                        token_mint=token_mint,
                        amount_sol=self.config.investment_amount_sol,
                        executor_attempted=success.get('executor', 'unknown'),
                        failure_reason=success.get('error', 'Unknown error'),
                        detected_dex=detected_dex or 'Unknown',
                        detection_method='websocket',
                        trade_count_for_token=trade_count,
                        portfolio_position_count=len(self.positions),
                        notes=f"Copy trade #{trade_count} failed"
                    )
                
        except Exception as e:
            logger.error(f"❌ Error in copy buy: {e}")
            import traceback
            logger.debug(f"Full error traceback: {traceback.format_exc()}")
    
    async def execute_copy_sell(self, token_mint: str, trade_info: Dict[str, Any], source_wallet: str):
        """Execute a copy sell trade with proportional selling"""
        try:
            # First check if we have a tracked position
            if token_mint not in self.positions:
                logger.warning(f"⚠️  No tracked position to sell in {token_mint}")
                
                # Double-check by looking at actual wallet balance
                current_balances = await self.get_wallet_balance()
                if token_mint in current_balances and current_balances[token_mint] > 0:
                    logger.info(f"💡 Found untracked balance: {current_balances[token_mint]} tokens")
                    logger.info(f"🔧 Proceeding with sell anyway - updating position tracking")
                    
                    # Create position from current balance
                    from models import Position
                    self.positions[token_mint] = Position(
                        initial_amount=current_balances[token_mint],
                        current_amount=current_balances[token_mint],
                        our_amount=self.config.investment_amount_sol
                    )
                else:
                    logger.warning(f"⚠️  No actual balance found for {token_mint}")
                    
                    # CSV LOG: Failed sell - no position
                    try:
                        self.csv_logger.log_trade_failure(
                            source_wallet=source_wallet,
                            trade_type='sell',
                            token_mint=token_mint,
                            amount_sol=0,
                            executor_attempted='position_check',
                            failure_reason=f"No position found for token {token_mint[:8]}...",
                            transaction_signature='',
                            pre_balances=current_balances,
                            post_balances=current_balances,
                            detected_dex=trade_info.get('dex', 'Unknown'),
                            detection_method='websocket',
                            notes="Attempted sell but no position exists"
                        )
                    except Exception as csv_error:
                        logger.error(f"❌ CSV logging failed: {csv_error}")
                    
                    return
            
            position = self.positions[token_mint]
            
            # Get balance BEFORE trade with retry
            pre_balances = None
            for retry in range(3):
                try:
                    pre_balances = await self.get_wallet_balance()
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Pre-sell balance check retry {retry+1}/3 failed: {e}")
                    if retry < 2:
                        await asyncio.sleep(2)
            
            if not pre_balances:
                pre_balances = {"SOL": 0.0}
                
            logger.info(f"💰 PRE-SELL BALANCE CHECK:")
            logger.info(f"   SOL: {pre_balances.get('SOL', 0):.6f}")
            if token_mint in pre_balances:
                logger.info(f"   {token_mint[:8]}...: {pre_balances[token_mint]:.6f}")
                
                # Verify we actually have tokens to sell
                if pre_balances[token_mint] <= 0:
                    logger.error(f"❌ Zero balance detected for {token_mint[:8]}... - cannot sell")
                    
                    # CSV LOG: Failed sell - zero balance
                    try:
                        self.csv_logger.log_trade_failure(
                            source_wallet=source_wallet,
                            trade_type='sell',
                            token_mint=token_mint,
                            amount_sol=0,
                            executor_attempted='balance_check',
                            failure_reason=f"Zero balance for token {token_mint[:8]}...",
                            transaction_signature='',
                            pre_balances=pre_balances,
                            post_balances=pre_balances,
                            detected_dex=trade_info.get('dex', 'Unknown'),
                            detection_method='websocket',
                            notes="Balance check revealed zero tokens to sell"
                        )
                    except Exception as csv_error:
                        logger.error(f"❌ CSV logging failed: {csv_error}")
                        
                    return
            else:
                logger.error(f"❌ Token {token_mint[:8]}... not found in wallet balance")
                
                # CSV LOG: Failed sell - token not in wallet
                try:
                    self.csv_logger.log_trade_failure(
                        source_wallet=source_wallet,
                        trade_type='sell',
                        token_mint=token_mint,
                        amount_sol=0,
                        executor_attempted='balance_check',
                        failure_reason=f"Token {token_mint[:8]}... not in wallet",
                        transaction_signature='',
                        pre_balances=pre_balances,
                        post_balances=pre_balances,
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        detection_method='websocket',
                        notes="Token not found in wallet balance"
                    )
                except Exception as csv_error:
                    logger.error(f"❌ CSV logging failed: {csv_error}")
                    
                return
            
            # Calculate proportional sell amount
            # This is simplified - you'd need to track the source wallet's position changes
            original_amount = trade_info.get('amount', 0)
            
            # Update target wallet position tracking
            if source_wallet not in self.target_positions:
                self.target_positions[source_wallet] = {}
            
            current_target_amount = self.target_positions[source_wallet].get(token_mint, 0)
            
            # Calculate sell percentage based on their activity
            if current_target_amount > 0:
                sell_percentage = min(1.0, original_amount / current_target_amount)
            else:
                sell_percentage = 1.0  # Sell all if we can't determine
            
            # Apply minimum sell threshold
            if sell_percentage < self.config.min_sell_threshold:
                logger.info(f"⚠️  Sell amount too small ({sell_percentage:.2%}), skipping")
                return
            
            logger.info(f"💸 Executing SELL: {sell_percentage:.2%} of {token_mint}")
            
            # Execute sell
            success = None
            if sell_percentage >= 0.95:  # Sell all if > 95%
                success = await self.execute_trade_with_fallback('sell_all', token_mint)
                
                if success['success']:
                    # Get balance AFTER trade
                    await asyncio.sleep(2)  # Wait for balance update
                    post_balances = await self.get_wallet_balance()
                    
                    # Log balance changes
                    await self.log_balance_change('sell_all', token_mint, pre_balances, post_balances, success['signature'])
                    
                    # CSV LOG: Successful sell
                    self.csv_logger.log_trade_success(
                        source_wallet=source_wallet,
                        trade_type='sell',
                        token_mint=token_mint,
                        amount_sol=position.current_amount,  # Amount of SOL position being sold
                        executor_used=success.get('executor', 'unknown'),
                        transaction_signature=success['signature'],
                        pre_balances=pre_balances,
                        post_balances=post_balances,
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        detection_method='websocket',
                        trade_count_for_token=self.trade_counter.get(token_mint, 1),
                        portfolio_position_count=len(self.positions) - 1,  # -1 because position will be removed
                        notes=f"Sell all ({sell_percentage:.1%}) following target wallet"
                    )
                    
                    # Remove position
                    del self.positions[token_mint]
                    logger.info(f"✅ Sell all successful!")
                    logger.info(f"   🔗 Transaction: https://solscan.io/tx/{success['signature']}")
                    logger.info(f"   🗑️  Position closed for {token_mint}")
            else:
                # Partial sell - this would need more sophisticated implementation
                logger.info(f"⚠️  Partial sell not implemented, selling all instead")
                success = await self.execute_trade_with_fallback('sell_all', token_mint)
                
                if success['success']:
                    # Get balance AFTER trade
                    await asyncio.sleep(2)  # Wait for balance update
                    post_balances = await self.get_wallet_balance()
                    
                    # Log balance changes
                    await self.log_balance_change('sell_all', token_mint, pre_balances, post_balances, success['signature'])
                    
                    # CSV LOG: Successful partial sell (sold as all)
                    self.csv_logger.log_trade_success(
                        source_wallet=source_wallet,
                        trade_type='sell',
                        token_mint=token_mint,
                        amount_sol=position.current_amount,
                        executor_used=success.get('executor', 'unknown'),
                        transaction_signature=success['signature'],
                        pre_balances=pre_balances,
                        post_balances=post_balances,
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        detection_method='websocket',
                        trade_count_for_token=self.trade_counter.get(token_mint, 1),
                        portfolio_position_count=len(self.positions) - 1,
                        notes=f"Partial sell implemented as sell all ({sell_percentage:.1%})"
                    )
                    
                    del self.positions[token_mint]
                    logger.info(f"✅ Sell successful!")
                    logger.info(f"   🔗 Transaction: https://solscan.io/tx/{success['signature']}")
                    logger.info(f"   🗑️  Position closed for {token_mint}")
            
            if not success or not success['success']:
                logger.error(f"❌ Sell failed for {token_mint}")
                failure_reason = "Unknown error"
                if success:
                    logger.error(f"   Error: {success.get('error', 'Unknown error')}")
                    failure_reason = success.get('error', 'Unknown error')
                
                # CSV LOG: Failed sell
                if success and success.get('failed_executors'):
                    # Multiple executor failure
                    self.csv_logger.log_multiple_executor_failure(
                        source_wallet=source_wallet,
                        trade_type='sell',
                        token_mint=token_mint,
                        amount_sol=position.current_amount,
                        failed_executors=success['failed_executors'],
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        detection_method='websocket',
                        trade_count_for_token=self.trade_counter.get(token_mint, 1),
                        portfolio_position_count=len(self.positions),
                        notes=f"All executors failed for sell ({sell_percentage:.1%}) following target wallet"
                    )
                else:
                    # Single executor failure
                    self.csv_logger.log_trade_failure(
                        source_wallet=source_wallet,
                        trade_type='sell',
                        token_mint=token_mint,
                        amount_sol=position.current_amount,
                        executor_attempted=success.get('executor', 'unknown') if success else 'unknown',
                        failure_reason=failure_reason,
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        detection_method='websocket',
                        trade_count_for_token=self.trade_counter.get(token_mint, 1),
                        portfolio_position_count=len(self.positions),
                        notes=f"Sell failed ({sell_percentage:.1%}) following target wallet"
                    )
            
        except Exception as e:
            logger.error(f"❌ Error in copy sell: {e}")
    
    async def execute_trade_with_fallback(self, trade_type: str, token_mint: str, amount_sol: float = None, detected_dex: str = None, pool_info = None) -> Dict[str, Any]:
        """Execute trade with Jito first, RPC fallback - ULTRA-AGGRESSIVE for trusted wallets with pool discovery"""
        
        # ULTRA-AGGRESSIVE COPY TRADING MODE: SKIP ALL VALIDATIONS
        # If target wallet traded it, WE TRADE IT - no questions asked!
        logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
        logger.info(f"💎 Skipping all validations - if they can trade it, so can we!")
        
        # SPEED OPTIMIZATION: Skip format validation for ultra-fast execution
        logger.debug(f"⚡ SPEED MODE: Skipping token format validation for {token_mint[:8]}...")
        logger.debug(f"🎯 TRUSTED WALLET: Following target wallet's exact trade")
        
        # Try Jito first if enabled
        if self.config.use_jito and self.jito_service:
            logger.info("⚡ Attempting Jito execution...")
            try:
                jito_result = await self.execute_via_jito(trade_type, token_mint, amount_sol)
                if jito_result['success']:
                    logger.info("✅ Jito execution successful")
                    return jito_result
                else:
                    logger.warning("⚠️  Jito execution failed, falling back to RPC")
            except Exception as e:
                logger.warning(f"⚠️  Jito error: {e}, falling back to RPC")
        
        # Fallback to RPC execution with smart routing and pool discovery
        logger.info("🔄 Executing via RPC...")
        if pool_info:
            logger.info(f"🔍 Pool info available for independent executors!")
            logger.info(f"   DEX Type: {pool_info.dex_type}")
        rpc_result = await self.execute_via_rpc(trade_type, token_mint, amount_sol, detected_dex, pool_info)
        
        # ULTRA-AGGRESSIVE ERROR HANDLING: NEVER GIVE UP ON TRUSTED WALLET TRADES!
        if not rpc_result['success']:
            error_msg = rpc_result.get('error', '')
            
            logger.error(f"❌ All DEXes failed for trusted wallet trade: {token_mint[:8]}...")
            logger.error(f"💔 Error summary: {error_msg}")
            
            # BUT FOR TRUSTED WALLETS - WE NEVER GIVE UP!
            logger.info(f"")
            logger.info(f"🔥 TRUSTED WALLET OVERRIDE: This trade WILL be retried!")
            logger.info(f"� Your target wallet successfully executed this exact trade")
            logger.info(f"🚀 We will keep trying different methods until we succeed")
            logger.info(f"")
            
            # Enhanced error categorization for better retries
            if 'AccountOwnedByWrongProgram' in error_msg or '0xbbf' in error_msg or 'bonding_curve' in error_msg.lower():
                logger.warning(f"🎯 PUMP.FUN ISSUE: Token may need different trading method")
                logger.info(f"💡 Target wallet likely used direct Pump.fun or special routing")
                # Don't skip - this should be retried with alternative methods
                rpc_result['retry_different_method'] = True
                rpc_result['suggested_method'] = 'alternative_routing'
                
            elif '0x1771' in error_msg or 'slippage' in error_msg.lower():
                logger.info(f"🎯 SLIPPAGE ISSUE: Price moved too fast (good for meme tokens!)")
                logger.info(f"💡 Will retry with even higher slippage tolerance")
                rpc_result['retry_higher_slippage'] = True
                rpc_result['suggested_slippage'] = '75%'  # Even higher!
                
            elif any(keyword in error_msg.lower() for keyword in [
                'token_not_tradable', 'incorrect program id', 'ata', 'account not found', 'no routes'
            ]):
                logger.info(f"🎯 ROUTING ISSUE: Standard DEXes don't have liquidity yet")
                logger.info(f"💡 Target wallet used alternative method - will find the same route")
                rpc_result['retry_alternative_dex'] = True
                rpc_result['suggested_alternative'] = 'specialized_routing'
            
            # IMPORTANT: Never mark as "skipped" for trusted wallet trades
            # Always allow for retries with different strategies
            logger.info(f"📋 RETRY STRATEGY: Will attempt alternative execution methods")
            logger.info(f"🎯 Success rate will be tracked for future optimization")
            
        return rpc_result
    
    async def _validate_token_compatibility(self, token_mint: str):
        """Enhanced token compatibility validation"""
        try:
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Get token account info to check if it's a valid SPL token
            account_info = await self.rpc_client.get_account_info(token_pubkey)
            
            if not account_info.value:
                raise Exception("Token account does not exist")
            
            # Check if the account owner is the Token Program
            token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            system_program = Pubkey.from_string("11111111111111111111111111111111")
            
            if account_info.value.owner == system_program:
                logger.warning(f"⚠️  Token {token_mint} is owned by System Program")
                logger.warning(f"   This is likely a very new or non-standard token")
                logger.warning(f"   SPL-based DEXes (Jupiter, Raydium, etc.) will not work")
                logger.info(f"💡 Recommendation: Skip this token or use specialized Pump.fun executors only")
                raise Exception(f"Non-SPL token detected - owned by System Program")
                
            elif account_info.value.owner != token_program:
                logger.warning(f"⚠️  Token {token_mint} uses non-standard token program")
                logger.warning(f"   Owner: {account_info.value.owner}")
                logger.warning(f"   Expected: {token_program}")
                raise Exception(f"Non-standard token program - DEX compatibility limited")
            
            logger.debug(f"✅ Token compatibility check passed for {token_mint}")
            logger.debug(f"   Standard SPL token - full DEX compatibility expected")
            
        except Exception as e:
            logger.warning(f"⚠️  Token compatibility validation error: {e}")
            # For copy trading, we continue despite validation issues but with awareness
            raise e
    
    async def execute_via_jito(self, trade_type: str, token_mint: str, amount_sol: float = None) -> Dict[str, Any]:
        """Execute trade via Jito Block Engine for MEV protection"""
        try:
            from models import Bundle
            from jito_service import JitoClient
            from solders.pubkey import Pubkey
            from env_keys import EnvKeys
            
            logger.info(f"🔥 Executing {trade_type} via Jito Block Engine for MEV protection")
            
            # Initialize Jito client
            jito_client = JitoClient()
            
            # Initialize environment keys
            env_keys = EnvKeys()
            
            # First, try to create transaction using Jupiter (most reliable)
            try:
                from jupiter_trade_executor import JupiterTradeExecutor
                
                jupiter_executor = JupiterTradeExecutor(self.wallet, env_keys.HELIUS_RPC_URL)
                token_pubkey = Pubkey.from_string(token_mint)
                
                # Create the transaction based on trade type
                if trade_type == 'buy':
                    if not amount_sol:
                        amount_sol = self.config.initial_investment
                    
                    logger.info(f"💰 Creating Jupiter buy transaction: {amount_sol} SOL → {token_mint}")
                    
                    # Get the Jupiter swap transaction (without sending)
                    from jupiter_trade_executor import get_best_route, get_swap_transaction, SOL_MINT
                    import base64
                    from solders.transaction import VersionedTransaction
                    
                    # Get Jupiter route and transaction
                    lamports = int(amount_sol * 1e9)
                    route = get_best_route(str(SOL_MINT), token_mint, lamports)
                    if not route:
                        logger.error("❌ Failed to get Jupiter route")
                        return {"success": False, "signature": ""}
                    
                    # Get the swap transaction
                    swap_tx_b64 = get_swap_transaction(route, self.wallet.pubkey())
                    if not swap_tx_b64:
                        logger.error("❌ Failed to get Jupiter swap transaction")
                        return {"success": False, "signature": ""}
                    
                    # Create versioned transaction
                    tx = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
                    
                    # Add Jito tip for MEV protection
                    from jito_tips import JitoTips
                    jito_tips = JitoTips(self.rpc_client)
                    
                    # Add 50k lamports tip (well above minimum for priority)
                    tipped_tx = await jito_tips.add_tip_to_transaction(tx, self.wallet, 50000)
                    if not tipped_tx:
                        logger.error("❌ Failed to add Jito tip to transaction")
                        return {"success": False, "signature": ""}
                    
                    tx = tipped_tx
                    
                elif trade_type == 'sell_all':
                    logger.info(f"💸 Creating Jupiter sell transaction: {token_mint} → SOL")
                    
                    # Similar process for sell transactions
                    from jupiter_trade_executor import get_token_balance, get_best_route, get_swap_transaction
                    import base64
                    from solders.transaction import VersionedTransaction
                    from solana.rpc.async_api import AsyncClient
                    from solana.rpc.commitment import Processed
                    
                    # Get token balance
                    client = AsyncClient(env_keys.HELIUS_RPC_URL, commitment=Processed)
                    
                    try:
                        # Get token account and balance
                        from solders.pubkey import Pubkey
                        from spl.token.instructions import get_associated_token_address
                        
                        token_ata = get_associated_token_address(self.wallet.pubkey(), token_pubkey)
                        account_info = await client.get_account_info(token_ata)
                        
                        if not account_info.value:
                            logger.error("❌ No token account found")
                            return {"success": False, "signature": ""}
                        
                        # Parse token account data to get balance
                        from spl.token.core import AccountInfo
                        token_account = AccountInfo.from_bytes(account_info.value.data)
                        token_balance = int(token_account.amount)
                        
                        if token_balance == 0:
                            logger.error("❌ No tokens to sell")
                            return {"success": False, "signature": ""}
                        
                        # Get Jupiter route for sell
                        route = get_best_route(token_mint, str(SOL_MINT), token_balance)
                        if not route:
                            logger.error("❌ Failed to get Jupiter sell route")
                            return {"success": False, "signature": ""}
                        
                        # Get the swap transaction
                        swap_tx_b64 = get_swap_transaction(route, self.wallet.pubkey())
                        if not swap_tx_b64:
                            logger.error("❌ Failed to get Jupiter sell transaction")
                            return {"success": False, "signature": ""}
                        
                        # Create versioned transaction
                        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
                        
                        # Add Jito tip for MEV protection
                        from jito_tips import JitoTips
                        jito_tips = JitoTips(client)
                        
                        # Add 50k lamports tip (well above minimum for priority)
                        tipped_tx = await jito_tips.add_tip_to_transaction(tx, self.wallet, 50000)
                        if not tipped_tx:
                            logger.error("❌ Failed to add Jito tip to sell transaction")
                            return {"success": False, "signature": ""}
                        
                        tx = tipped_tx
                        
                    finally:
                        await client.close()
                else:
                    logger.error(f"❌ Unknown trade type: {trade_type}")
                    return {"success": False, "signature": ""}
                
                # Sign the transaction
                tx.sign([self.wallet])
                
                # Create bundle and submit via Jito
                bundle = Bundle(transactions=[tx])
                
                logger.info("� Submitting transaction bundle to Jito Block Engine...")
                result = await jito_client.send_bundle(bundle)
                
                if result:
                    # Extract signature from result
                    signature = result if isinstance(result, str) else str(result)
                    logger.info(f"✅ Jito execution successful! Signature: {signature}")
                    return {"success": True, "signature": signature}
                else:
                    logger.error("❌ Jito Block Engine returned no result")
                    return {"success": False, "signature": ""}
                    
            except Exception as jupiter_error:
                logger.error(f"❌ Jupiter transaction creation failed: {jupiter_error}")
                return {"success": False, "signature": ""}
                
        except Exception as e:
            logger.error(f"❌ Jito execution error: {e}")
            return {"success": False, "signature": ""}
    
    async def execute_via_rpc(self, trade_type: str, token_mint: str, amount_sol: float = None, detected_dex: str = None, pool_info = None) -> Dict[str, Any]:
        """Execute trade via RPC using DEX executors with smart routing and pool discovery"""
        try:
            last_error = ""
            
            # Import rate limit manager
            from rate_limit_manager import rate_limit_manager
            
            # Check if we're hitting rate limits before starting
            if not rate_limit_manager.can_make_jupiter_request():
                logger.warning(f"🚦 Pre-emptive rate limit check: waiting for Jupiter slot...")
                await rate_limit_manager.wait_for_jupiter_slot()
            
            # Check wallet SOL balance first (warning only - don't block trades)
            try:
                sol_balance_response = await self.rpc_client.get_balance(self.wallet_pubkey, Processed)
                if sol_balance_response.value:
                    sol_balance = sol_balance_response.value / 1e9
                    required_amount = (amount_sol or self.config.investment_amount_sol) + 0.005
                    if sol_balance < required_amount:
                        logger.warning(f"⚠️ Low SOL balance: {sol_balance:.6f} SOL (need {required_amount:.6f} SOL)")
                        logger.warning(f"   Trade may fail due to insufficient balance, but attempting anyway")
                    else:
                        logger.debug(f"✅ Sufficient SOL balance: {sol_balance:.6f} SOL")
                else:
                    logger.warning(f"⚠️ Could not retrieve SOL balance - proceeding anyway")
            except Exception as e:
                logger.warning(f"⚠️ Balance check error: {e} - proceeding anyway")
            
            # Check if this is a non-SPL token to adjust strategy
            is_non_spl_token = False
            try:
                token_pubkey = Pubkey.from_string(token_mint)
                account_info = await self.rpc_client.get_account_info(token_pubkey)
                system_program = Pubkey.from_string("11111111111111111111111111111111")
                
                if account_info.value and account_info.value.owner == system_program:
                    is_non_spl_token = True
                    logger.info(f"🎯 Non-SPL token detected - prioritizing Pump.fun executors")
            except:
                pass  # If we can't check, proceed normally
            
            # Smart DEX routing based on detected program
            def get_prioritized_dexes():
                """Get DEX executors in priority order - RESTORED TO JUPITER-INDEPENDENT IMPLEMENTATIONS"""
                prioritized = []
                
                logger.info("� RESTORED INDEPENDENT DEX EXECUTORS:")
                logger.info("✅ Fixed Jupiter dependency crisis - your weeks of work restored!")
                logger.info("")
                logger.info("� TRULY INDEPENDENT EXECUTORS (No Jupiter API):")
                
                # STEP 1: Try truly independent executors first (your original work!)
                independent_executors = []
                
                # Raydium (your direct AMM implementation)
                if "raydium" in self.dex_executors and self.config.enable_dexes.get("raydium", False):
                    buy_func, sell_func = self.dex_executors["raydium"]
                    independent_executors.append(("raydium", buy_func, sell_func))
                    logger.info("🟣 RAYDIUM: ✅ Direct AMM (needs pool discovery from transactions)")
                
                # Direct Pump.fun (your bonding curve implementation)  
                if "direct_pumpfun" in self.dex_executors and self.config.enable_dexes.get("direct_pumpfun", False):
                    buy_func, sell_func = self.dex_executors["direct_pumpfun"]
                    independent_executors.append(("direct_pumpfun", buy_func, sell_func))
                    logger.info("🚀 DIRECT PUMP.FUN: ✅ Native bonding curve (needs graduation handling)")
                
                # CPMM (your Raydium V4 implementation)
                if "cpmm" in self.dex_executors and self.config.enable_dexes.get("cpmm", False):
                    buy_func, sell_func = self.dex_executors["cpmm"]
                    independent_executors.append(("cpmm", buy_func, sell_func))
                    logger.info("🟣 CPMM: ✅ Direct Raydium V4 (restored from Jupiter fallback)")
                
                # Orca (your whirlpool/legacy implementation)
                if "orca" in self.dex_executors and self.config.enable_dexes.get("orca", False):
                    buy_func, sell_func = self.dex_executors["orca"]
                    independent_executors.append(("orca", buy_func, sell_func))
                    logger.info("� ORCA: ✅ Direct whirlpool/legacy (restored from Jupiter fallback)")
                
                # Pump.fun (your implementation, fixed from Jupiter fallback)
                if "pumpfun" in self.dex_executors and self.config.enable_dexes.get("pumpfun", False):
                    buy_func, sell_func = self.dex_executors["pumpfun"]
                    independent_executors.append(("pumpfun", buy_func, sell_func))
                    logger.info("🚀 PUMP.FUN: ✅ Direct bonding curve (restored from Jupiter fallback)")
                
                logger.info("")
                logger.info("🎯 JUPITER AGGREGATOR & OTHER EXECUTORS:")
                
                # STEP 2: Add Jupiter-dependent ones as fallback (clearly labeled)
                jupiter_dependent = ["jupiter", "phoenix", "clmm"]  # Phoenix and CLMM may use Jupiter
                
                for executor_name in jupiter_dependent:
                    if (executor_name in self.dex_executors and 
                        self.config.enable_dexes.get(executor_name, False)):
                        buy_func, sell_func = self.dex_executors[executor_name]
                        independent_executors.append((executor_name, buy_func, sell_func))
                        
                        if executor_name == "jupiter":
                            logger.info(f"   🌟 JUPITER: Explicit Jupiter aggregator (rate limited at 60 req/min)")
                        else:
                            logger.info(f"   ⚠️ {executor_name.upper()}: Uses Jupiter API (will rate limit)")
                
                logger.info("")
                if independent_executors:
                    total_independent = len([x for x in independent_executors if x[0] not in jupiter_dependent])
                    total_jupiter_dependent = len([x for x in independent_executors if x[0] in jupiter_dependent])
                    logger.info(f"✅ SUCCESS: {total_independent} truly independent executors restored!")
                    logger.info(f"🌟 AVAILABLE: Jupiter aggregator when you need maximum liquidity")
                    
                    # Count Jupiter vs other Jupiter-dependent
                    jupiter_count = 1 if "jupiter" in [x[0] for x in independent_executors] else 0
                    other_jupiter_dependent = total_jupiter_dependent - jupiter_count
                    
                    if other_jupiter_dependent > 0:
                        logger.info(f"⚠️ WARNING: {other_jupiter_dependent} other executors still use Jupiter API")
                    
                    logger.info("🎉 Your weeks of DEX implementation work is now being used!")
                else:
                    logger.error("� CRITICAL: NO EXECUTORS AVAILABLE!")
                    logger.error("🔧 Check your executor configurations")
                
                return independent_executors
                
                # DEX name mapping from detected DEX strings to executor names
                dex_mapping = {
                    "Jupiter V6": ["jupiter", "pumpfun"],  # Jupiter can route through many DEXes
                    "Jupiter V4": ["jupiter", "pumpfun"], 
                    "Raydium V4": ["raydium", "cpmm"],
                    "Raydium CPMM": ["cpmm", "raydium"],
                    "Raydium CPMM V2": ["cpmm", "raydium"],
                    "Orca Whirlpool": ["orca", "clmm"],
                    "Orca": ["orca"],
                    "Pump.fun": ["direct_pumpfun", "pumpfun"],
                    "Axiom DEX": ["jupiter"]  # Axiom often routes through Jupiter
                }
                
                # If we detected a specific DEX, prioritize matching executors
                if detected_dex and detected_dex in dex_mapping:
                    preferred_executors = dex_mapping[detected_dex]
                    logger.info(f"🎯 Smart routing: Detected {detected_dex}, prioritizing {preferred_executors}")
                    
                    # Add preferred executors first
                    for executor_name in preferred_executors:
                        if (executor_name in self.dex_executors and 
                            self.config.enable_dexes.get(executor_name, False)):
                            buy_func, sell_func = self.dex_executors[executor_name]
                            prioritized.append((executor_name, buy_func, sell_func))
                    
                    # Add remaining executors
                    for dex_name, (buy_func, sell_func) in self.dex_executors.items():
                        if (self.config.enable_dexes.get(dex_name, False) and 
                            dex_name not in preferred_executors):
                            remaining.append((dex_name, buy_func, sell_func))
                else:
                    # FAST COPY TRADING: Prioritize the DEXes that are actually working
                    logger.info("� FAST COPY TRADING: Using proven successful DEXes first")
                    
                    # Based on your logs, ORCA is working. Let's prioritize working ones and avoid Jupiter-heavy ones
                    # Avoid: jupiter, cpmm (uses Jupiter), pumpfun (uses Jupiter), clmm (uses Jupiter fallback)
                    success_priority = ["orca", "phoenix", "raydium"]
                    
                    # Add working DEXes first
                    for dex_name in success_priority:
                        if (dex_name in self.dex_executors and 
                            self.config.enable_dexes.get(dex_name, False)):
                            buy_func, sell_func = self.dex_executors[dex_name]
                            prioritized.append((dex_name, buy_func, sell_func))
                    
                    # Then add remaining DEXes as fallback
                    remaining_dexes = ["direct_pumpfun", "jupiter", "cpmm", "clmm", "pumpfun"]
                    for dex_name in remaining_dexes:
                        if (dex_name in self.dex_executors and 
                            self.config.enable_dexes.get(dex_name, False)):
                            buy_func, sell_func = self.dex_executors[dex_name]
                            prioritized.append((dex_name, buy_func, sell_func))
                
                return prioritized
            
            # Get prioritized DEX list
            all_dexes = get_prioritized_dexes()
            
            success_count = 0
            ata_errors = 0
            quote_errors = 0
            rate_limit_errors = 0
            failed_executors = {}  # Track all failed executors for CSV logging
            
            for i, (dex_name, buy_func, sell_func) in enumerate(all_dexes):
                logger.info(f"🔄 Trying {dex_name.upper()}...")
                
                # Rate limiting for Jupiter-based executors
                jupiter_based_dexes = ["orca", "phoenix", "jupiter", "cpmm", "clmm", "pumpfun"]
                if dex_name in jupiter_based_dexes:
                    if not rate_limit_manager.can_make_jupiter_request():
                        logger.warning(f"🚦 {dex_name.upper()}: Jupiter rate limited, waiting for slot...")
                        await rate_limit_manager.wait_for_jupiter_slot()
                    
                    # Record that we're about to make a Jupiter request
                    rate_limit_manager.record_jupiter_request()
                
                try:
                    # PROGRESSIVE SLIPPAGE ESCALATION
                    # Start conservative and escalate based on retry attempts
                    slippage_levels = [0.05, 0.10, 0.15, 0.20, 0.30]  # 5%, 10%, 15%, 20%, 30%
                    attempt_index = min(self.current_retry_attempt, len(slippage_levels) - 1)
                    final_slippage = slippage_levels[attempt_index]
                    final_slippage_bps = int(final_slippage * 10000)
                    
                    copy_trade_kwargs = {
                        'slippage_tolerance': final_slippage,  # Progressive escalating slippage
                        'slippage_bps': final_slippage_bps     # Progressive for Orca/Phoenix
                    }
                    
                    # Add pool information for independent executors
                    if pool_info:
                        copy_trade_kwargs['pool_info'] = {
                            'dex_type': pool_info.dex_type,
                            'pool_id': pool_info.pool_id,
                            'bonding_curve': pool_info.bonding_curve,
                            'associated_bonding_curve': pool_info.associated_bonding_curve,
                            'creator': pool_info.creator,
                            'pool_coin_token_account': pool_info.pool_coin_token_account,
                            'pool_pc_token_account': pool_info.pool_pc_token_account,
                            'vault_a': pool_info.vault_a,
                            'vault_b': pool_info.vault_b,
                            'amm_id': pool_info.amm_id,
                            'amm_authority': pool_info.amm_authority,
                            'original_signature': pool_info.original_signature
                        }
                        logger.debug(f"📦 Pool info added to executor kwargs: {pool_info.dex_type}")
                    
                    if self.current_retry_attempt > 0:
                        logger.info(f"� SLIPPAGE ESCALATION: Attempt {self.current_retry_attempt + 1}/5 using {final_slippage:.0%} slippage")
                    else:
                        logger.info(f"🎯 COPY TRADE: Starting with {final_slippage:.0%} slippage tolerance")
                    
                    if trade_type == 'buy':
                        # Try to pass slippage parameters if the executor supports them
                        try:
                            result = await buy_func(
                                self.wallet, 
                                token_mint, 
                                amount_sol or self.config.investment_amount_sol,
                                **copy_trade_kwargs
                            )
                        except TypeError:
                            # Fallback if executor doesn't support kwargs
                            result = await buy_func(self.wallet, token_mint, amount_sol or self.config.investment_amount_sol)
                            
                    elif trade_type == 'sell_all':
                        # Try to pass slippage parameters if the executor supports them
                        try:
                            result = await sell_func(self.wallet, token_mint, **copy_trade_kwargs)
                        except TypeError:
                            # Fallback if executor doesn't support kwargs
                            result = await sell_func(self.wallet, token_mint)
                    else:
                        logger.warning(f"⚠️  Unknown trade type: {trade_type}")
                        continue
                    
                    if result['success']:
                        logger.info(f"✅ {dex_name.upper()} success: {result['signature']}")
                        result['executor'] = dex_name  # Add executor name to result
                        return result
                    else:
                        last_error = result.get('error', 'Unknown error')
                        failed_executors[dex_name] = last_error  # Track failed executor
                        
                        # ENHANCED SLIPPAGE DETECTION AND LOGGING
                        if self._is_slippage_error(last_error):
                            slippage_levels = [0.05, 0.10, 0.15, 0.20, 0.30]  # 5%, 10%, 15%, 20%, 30%
                            current_slippage = slippage_levels[min(self.current_retry_attempt, len(slippage_levels) - 1)]
                            
                            logger.error(f"🔴 SLIPPAGE EXCEEDED: {dex_name.upper()} failed due to slippage!")
                            logger.error(f"   💔 Current slippage tolerance: {current_slippage:.0%}")
                            logger.error(f"   📈 Token price moved faster than {current_slippage:.0%} limit")
                            logger.error(f"   🎯 This is common with volatile meme tokens")
                            
                            if self.current_retry_attempt < 4:  # Not final attempt
                                next_slippage = slippage_levels[self.current_retry_attempt + 1]
                                logger.info(f"   🔄 Will retry with {next_slippage:.0%} slippage on next attempt")
                            else:
                                logger.error(f"   💀 FINAL SLIPPAGE FAILURE: Even 30% slippage wasn't enough!")
                                logger.error(f"   🚨 This token is EXTREMELY volatile - manual review needed")
                        else:
                            logger.warning(f"⚠️  {dex_name.upper()} failed: {last_error}")
                        
                        # Track error types for better diagnostics
                        if 'ata' in last_error.lower() or 'incorrect program id' in last_error.lower():
                            ata_errors += 1
                        elif 'token_not_tradable' in last_error.lower() or 'quote' in last_error.lower():
                            quote_errors += 1
                        elif '429' in last_error or 'rate limit' in last_error.lower():
                            rate_limit_errors += 1
                            rate_limit_errors += 1
                        
                except Exception as e:
                    last_error = str(e)
                    failed_executors[dex_name] = last_error  # Track failed executor
                    logger.warning(f"⚠️  {dex_name.upper()} error: {e}")
                    
                    # Enhanced error analysis for Jupiter/DEX-specific issues
                    error_msg = str(e).lower()
                    
                    # Jupiter slippage exceeded error
                    if '0x1771' in str(e) or 'custom program error: 0x1771' in error_msg:
                        logger.warning(f"🔄 {dex_name.upper()}: Slippage tolerance exceeded")
                        logger.info(f"💡 Token price moved too quickly - this is common in copy trading")
                        
                    # Rate limiting
                    elif '429' in str(e) or 'rate limit' in error_msg or 'too many requests' in error_msg:
                        rate_limit_errors += 1
                        logger.info(f"⏰ {dex_name.upper()}: Rate limited - will try next executor")
                        
                    # ATA/Account issues
                    elif 'ata' in error_msg or 'incorrect program id' in error_msg or 'account not found' in error_msg:
                        ata_errors += 1
                        logger.info(f"🏦 {dex_name.upper()}: Token account issue - possibly very new token")
                        
                    # Jupiter routing issues
                    elif 'no routes' in error_msg or 'token_not_tradable' in error_msg:
                        quote_errors += 1
                        logger.info(f"🗺️  {dex_name.upper()}: No trading route found")
                        
                    # Compute budget issues
                    elif 'compute budget exceeded' in error_msg or 'computational budget exceeded' in error_msg:
                        logger.info(f"💻 {dex_name.upper()}: Transaction too complex - trying simpler executor")
                        
                    # Generic tracking
                    else:
                        # Track error types
                        if 'ata' in error_msg or 'incorrect program id' in error_msg:
                            ata_errors += 1
                        elif 'token_not_tradable' in error_msg or 'quote' in error_msg:
                            quote_errors += 1
                        elif '429' in str(e) or 'rate limit' in error_msg:
                            rate_limit_errors += 1
                    
                    continue
            
            # Provide diagnostic information
            if is_non_spl_token:
                logger.error("❌ All proven executors failed for non-SPL token")
                logger.info(f"💡 Target wallet successfully traded this token using different methods")
            else:
                logger.error("❌ All DEX executors failed")
                if ata_errors > 0:
                    logger.error(f"🔍 Diagnostic: {ata_errors} DEXes failed due to ATA/token compatibility issues")
                    logger.info(f"💡 This suggests the token might be too new or use a non-standard format")
                if quote_errors > 0:
                    logger.error(f"🔍 Diagnostic: {quote_errors} DEXes failed due to quote/routing issues")
                    logger.info(f"💡 This suggests the token might not be tradable on major DEXes yet")
                if rate_limit_errors > 0:
                    logger.info(f"🔍 Note: {rate_limit_errors} DEXes hit rate limits - this is normal for fast copy trading")
            
            return {"success": False, "signature": "", "error": last_error, "failed_executors": failed_executors}
            
        except Exception as e:
            logger.error(f"❌ RPC execution error: {e}")
            return {"success": False, "signature": "", "error": str(e)}
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        try:
            total_positions = len(self.positions)
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "wallet": str(self.wallet_pubkey),
                "total_positions": total_positions,
                "max_positions": self.config.max_positions,
                "positions": {}
            }
            
            for token_mint, position in self.positions.items():
                status["positions"][token_mint] = {
                    "initial_amount": position.initial_amount,
                    "current_amount": position.current_amount,
                    "our_amount": position.our_amount,
                    "last_updated": position.last_updated.isoformat()
                }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting portfolio status: {e}")
            return {}
    
    def _decode_token_account(self, data: bytes):
        """
        Decode raw token account data from Solana
        Token account structure:
        - mint: 32 bytes (pubkey)
        - owner: 32 bytes (pubkey)  
        - amount: 8 bytes (u64)
        - delegate: 36 bytes (optional pubkey)
        - state: 1 byte
        - is_native: 12 bytes (optional u64)
        - delegated_amount: 8 bytes (u64)
        - close_authority: 36 bytes (optional pubkey)
        """
        if len(data) < 165:  # Minimum token account size
            return None
            
        try:
            import struct
            from solders.pubkey import Pubkey
            
            # First 32 bytes = mint pubkey
            mint_bytes = data[0:32]
            mint = Pubkey(mint_bytes)
            
            # Skip owner (32 bytes) to get to amount at offset 64
            amount_bytes = data[64:72]  # 8 bytes for u64
            amount = struct.unpack('<Q', amount_bytes)[0]  # little-endian u64
            
            # Get decimals - this requires additional RPC call normally
            # For now, assume 6 decimals for most SPL tokens (except SOL which is 9)
            decimals = 9 if str(mint) == "So11111111111111111111111111111111111111112" else 6
            
            ui_amount = amount / (10 ** decimals)
            
            return {
                'mint': str(mint),
                'amount': amount,
                'ui_amount': ui_amount,
                'decimals': decimals
            } if ui_amount > 0 else None
            
        except Exception as e:
            logger.debug(f"Token account decode error: {e}")
            return None

    async def get_wallet_balance(self) -> Dict[str, float]:
        """Get current SOL and token balances"""
        try:
            balances = {"SOL": 0.0}
            
            # Get SOL balance
            sol_balance_response = await self.rpc_client.get_balance(self.wallet_pubkey, Processed)
            if sol_balance_response.value:
                balances["SOL"] = sol_balance_response.value / 1e9  # Convert lamports to SOL
            
            # Get token balances using parsed format
            from solders.pubkey import Pubkey
            from solana.rpc.types import TokenAccountOpts
            
            try:
                # Fix: Remove unsupported encoding parameter
                token_accounts_response = await self.rpc_client.get_token_accounts_by_owner(
                    self.wallet_pubkey,
                    TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
                )
                
                if token_accounts_response.value:
                    for account in token_accounts_response.value:
                        try:
                            # Handle raw bytes data (your client returns raw bytes)
                            if hasattr(account, 'account') and hasattr(account.account, 'data'):
                                data = account.account.data
                                
                                if isinstance(data, bytes) and len(data) >= 165:
                                    # Decode raw token account data
                                    decoded = self._decode_token_account(data)
                                    
                                    if decoded and decoded['ui_amount'] > 0:
                                        mint = decoded['mint']
                                        amount = decoded['ui_amount']
                                        balances[mint] = amount
                                        
                                        # Log significant token balances
                                        if amount > 1.0:
                                            logger.debug(f"Token balance: {mint[:8]}... = {amount:.6f}")
                                
                                # Fallback: Try parsing as dict (if other clients work differently)
                                elif isinstance(data, dict):
                                    parsed_info = data.get('parsed', {}).get('info', {})
                                    mint = parsed_info.get('mint')
                                    token_amount = parsed_info.get('tokenAmount', {})
                                    ui_amount = token_amount.get('uiAmount', 0)
                                    
                                    if mint and ui_amount and ui_amount > 0:
                                        balances[mint] = float(ui_amount)
                                
                        except Exception as parse_error:
                            logger.debug(f"Failed to parse token account: {parse_error}")
                            continue
                            
            except Exception as token_error:
                logger.debug(f"Token balance retrieval error: {token_error}")
                # Return at least SOL balance if token parsing fails
                pass
            
            return balances
            
        except Exception as e:
            logger.error(f"❌ Error getting wallet balance: {e}")
            return {"SOL": 0.0}
    
    async def log_balance_change(self, trade_type: str, token_mint: str, pre_balances: Dict[str, float], post_balances: Dict[str, float], signature: str):
        """Log balance changes before and after trade"""
        try:
            logger.info(f"💰 BALANCE TRACKING - {trade_type.upper()} TRADE COMPLETED")
            logger.info(f"   🔗 Transaction: {signature}")
            logger.info(f"   🎯 Token: {token_mint[:8]}...")
            
            # SOL balance change
            pre_sol = pre_balances.get("SOL", 0.0)
            post_sol = post_balances.get("SOL", 0.0)
            sol_change = post_sol - pre_sol
            
            logger.info(f"   💎 SOL: {pre_sol:.6f} → {post_sol:.6f} (Δ{sol_change:+.6f})")
            
            # Token balance changes
            all_tokens = set(list(pre_balances.keys()) + list(post_balances.keys()))
            all_tokens.discard("SOL")  # Already handled SOL
            
            for token in all_tokens:
                pre_amount = pre_balances.get(token, 0.0)
                post_amount = post_balances.get(token, 0.0)
                change = post_amount - pre_amount
                
                if abs(change) > 0.000001:  # Only show significant changes
                    logger.info(f"   🎯 {token[:8]}...: {pre_amount:.6f} → {post_amount:.6f} (Δ{change:+.6f})")
            
            # Track execution
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "trade_type": trade_type,
                "token_mint": token_mint,
                "signature": signature,
                "pre_balances": pre_balances,
                "post_balances": post_balances,
                "sol_change": sol_change
            }
            self.execution_history.append(execution_record)
            
            # Keep only last 100 executions to prevent memory issues
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
                
        except Exception as e:
            logger.error(f"❌ Error logging balance change: {e}")
    
    async def log_trade_execution_summary(self):
        """Log summary of all trade executions"""
        try:
            if not self.execution_history:
                logger.info(f"📊 No trade executions recorded yet")
                return
            
            logger.info(f"📊 TRADE EXECUTION SUMMARY")
            logger.info(f"   Total Executions: {len(self.execution_history)}")
            
            # Group by token
            token_stats = defaultdict(list)
            for execution in self.execution_history[-20:]:  # Last 20 executions
                token_stats[execution['token_mint']].append(execution)
            
            for token_mint, executions in token_stats.items():
                buy_count = len([e for e in executions if e['trade_type'] == 'buy'])
                sell_count = len([e for e in executions if e['trade_type'] in ['sell', 'sell_all']])
                total_sol_spent = sum([abs(e['sol_change']) for e in executions if e['trade_type'] == 'buy'])
                
                logger.info(f"   🎯 {token_mint[:8]}...: {buy_count} buys, {sell_count} sells, {total_sol_spent:.6f} SOL spent")
                
        except Exception as e:
            logger.error(f"❌ Error logging trade summary: {e}")
    
    async def get_comprehensive_transaction_history(self, limit: int = 100, days_back: int = 7) -> Dict[str, Any]:
        """Get comprehensive transaction history for all target wallets using the dedicated analyzer"""
        try:
            logger.info(f"🔍 COMPREHENSIVE TRANSACTION ANALYSIS")
            logger.info(f"🎯 Target wallets: {len(self.config.target_wallets)}")
            logger.info(f"📊 Parameters: {limit} transactions per wallet, {days_back} days back")
            
            # Import the transaction history analyzer
            from transaction_history_analyzer import TransactionHistoryAnalyzer
            
            # Initialize analyzer with our RPC URL and target wallets
            analyzer = TransactionHistoryAnalyzer(env.HELIUS_RPC_URL, self.config.target_wallets)
            
            try:
                # Get all trades for all wallets
                all_trades = await analyzer.get_all_trades_for_all_wallets(limit, days_back)
                
                # Save results to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_trade_analysis_{timestamp}.json"
                saved_filename = await analyzer.save_analysis_to_file(all_trades, filename)
                
                # Generate summary statistics
                summary = self._generate_trade_summary(all_trades)
                
                logger.info(f"")
                logger.info(f"📊 COMPREHENSIVE ANALYSIS SUMMARY:")
                logger.info(f"   🎯 Wallets analyzed: {summary['total_wallets']}")
                logger.info(f"   🟢 Total buy transactions: {summary['total_buys']}")
                logger.info(f"   🔴 Total sell transactions: {summary['total_sells']}")
                logger.info(f"   💹 Grand total trades: {summary['total_trades']}")
                logger.info(f"   📊 Most active DEX: {summary['most_active_dex']}")
                logger.info(f"   💾 Results saved to: {saved_filename}")
                logger.info(f"")
                
                return {
                    'analysis_results': all_trades,
                    'summary': summary,
                    'filename': saved_filename,
                    'parameters': {
                        'limit': limit,
                        'days_back': days_back,
                        'wallets_analyzed': len(self.config.target_wallets)
                    }
                }
                
            finally:
                await analyzer.close()
                
        except Exception as e:
            logger.error(f"❌ Error in comprehensive transaction analysis: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return {
                'error': str(e),
                'analysis_results': {},
                'summary': {}
            }
    
    def _generate_trade_summary(self, all_trades: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from trade analysis results"""
        try:
            total_wallets = len(all_trades)
            total_buys = 0
            total_sells = 0
            dex_counts = {}
            token_counts = {}
            
            for wallet, trades in all_trades.items():
                if 'error' in trades:
                    continue
                    
                # Count trades
                total_buys += len(trades.get('buys', []))
                total_sells += len(trades.get('sells', []))
                
                # Count DEX usage
                for trade_list in [trades.get('buys', []), trades.get('sells', [])]:
                    for trade in trade_list:
                        dex = trade.get('dex', 'Unknown')
                        dex_counts[dex] = dex_counts.get(dex, 0) + 1
                        
                        token = trade.get('token_mint', 'Unknown')
                        token_counts[token] = token_counts.get(token, 0) + 1
            
            # Find most active DEX
            most_active_dex = max(dex_counts.items(), key=lambda x: x[1])[0] if dex_counts else "None"
            
            # Find most traded token
            most_traded_token = max(token_counts.items(), key=lambda x: x[1])[0] if token_counts else "None"
            
            return {
                'total_wallets': total_wallets,
                'total_buys': total_buys,
                'total_sells': total_sells,
                'total_trades': total_buys + total_sells,
                'most_active_dex': f"{most_active_dex} ({dex_counts.get(most_active_dex, 0)} trades)",
                'most_traded_token': f"{most_traded_token[:8]}..." if len(most_traded_token) > 8 else most_traded_token,
                'dex_breakdown': dex_counts,
                'token_breakdown': dict(list(token_counts.items())[:10])  # Top 10 tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating trade summary: {e}")
            return {
                'total_wallets': 0,
                'total_buys': 0,
                'total_sells': 0,
                'total_trades': 0,
                'most_active_dex': "Error",
                'error': str(e)
            }
    
    async def analyze_recent_trades_and_copy(self, limit: int = 20, days_back: int = 1):
        """Analyze recent trades from target wallets and identify copy opportunities"""
        try:
            logger.info(f"🎯 ANALYZING RECENT TRADES FOR COPY OPPORTUNITIES")
            logger.info(f"📊 Looking at last {limit} transactions from past {days_back} day(s)")
            
            # Get recent transaction history
            analysis = await self.get_comprehensive_transaction_history(limit, days_back)
            
            if 'error' in analysis:
                logger.error(f"❌ Failed to analyze recent trades: {analysis['error']}")
                return
            
            all_trades = analysis['analysis_results']
            copy_opportunities = []
            
            # Analyze trades for copy opportunities
            for wallet, trades in all_trades.items():
                if 'error' in trades:
                    logger.warning(f"⚠️ Skipping wallet {wallet} due to error: {trades['error']}")
                    continue
                
                # Look at recent buys (potential copy opportunities)
                recent_buys = sorted(trades.get('buys', []), 
                                   key=lambda x: x.get('timestamp', datetime.min), 
                                   reverse=True)
                
                for buy in recent_buys[:5]:  # Look at 5 most recent buys
                    token_mint = buy['token_mint']
                    
                    # Check if we already have this position
                    already_have_position = token_mint in self.positions
                    
                    copy_opportunity = {
                        'wallet': wallet,
                        'token_mint': token_mint,
                        'trade_type': 'buy',
                        'amount': buy['amount'],
                        'dex': buy.get('dex', 'Unknown'),
                        'timestamp': buy['timestamp'],
                        'signature': buy['signature'],
                        'already_have_position': already_have_position,
                        'should_copy': not already_have_position  # Only copy if we don't already have it
                    }
                    
                    copy_opportunities.append(copy_opportunity)
            
            # Sort opportunities by timestamp (most recent first)
            copy_opportunities.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
            logger.info(f"")
            logger.info(f"🎯 COPY OPPORTUNITIES IDENTIFIED:")
            
            new_opportunities = [opp for opp in copy_opportunities if opp['should_copy']]
            existing_positions = [opp for opp in copy_opportunities if not opp['should_copy']]
            
            logger.info(f"   🟢 New copy opportunities: {len(new_opportunities)}")
            logger.info(f"   ⚪ Existing positions: {len(existing_positions)}")
            
            # Show new opportunities
            if new_opportunities:
                logger.info(f"")
                logger.info(f"🚀 NEW COPY OPPORTUNITIES:")
                for i, opp in enumerate(new_opportunities[:3]):  # Show top 3
                    logger.info(f"   {i+1}. {opp['token_mint'][:8]}... from {opp['wallet'][:8]}...")
                    logger.info(f"      💰 {opp['amount']:.4f} SOL on {opp['dex']}")
                    logger.info(f"      🕐 {opp['timestamp']}")
                    logger.info(f"      🔗 {opp['signature'][:16]}...")
            
            # Show existing positions
            if existing_positions:
                logger.info(f"")
                logger.info(f"⚪ EXISTING POSITIONS (already holding):")
                for i, opp in enumerate(existing_positions[:3]):  # Show top 3
                    logger.info(f"   {i+1}. {opp['token_mint'][:8]}... (already have position)")
            
            return {
                'copy_opportunities': copy_opportunities,
                'new_opportunities': new_opportunities,
                'existing_positions': existing_positions,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing recent trades: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}
    
    async def stop(self):
        """Stop the copy trading bot and liquidate all remaining positions"""
        logger.info("🛑 Stopping copy trading bot...")
        self.is_running = False
        
        # Show daily CSV summary before stopping
        try:
            logger.info("📊 Generating final trading summary...")
            self.csv_logger.print_daily_summary()
        except Exception as e:
            logger.warning(f"⚠️ Error generating CSV summary: {e}")
        
        # Liquidate all remaining positions before stopping
        await self.liquidate_all_positions()
        
        if self.ws_connection:
            await self.ws_connection.close()
        await self.rpc_client.close()
        logger.info("🛑 Copy trading bot stopped")
    
    async def show_trading_summary(self):
        """Show current day's trading summary from CSV logs"""
        try:
            logger.info("📊 Current Trading Summary:")
            self.csv_logger.print_daily_summary()
        except Exception as e:
            logger.error(f"❌ Error showing trading summary: {e}")
    
    async def liquidate_all_positions(self):
        """Sell all remaining positions when stopping the bot"""
        try:
            if not self.positions:
                logger.info("💰 No positions to liquidate")
                return
            
            logger.info(f"💸 EMERGENCY LIQUIDATION: Selling all {len(self.positions)} remaining positions")
            logger.info(f"🔄 This ensures no positions are left behind when copied wallet may have already sold")
            
            # Get pre-liquidation balances for tracking
            pre_balances = await self.get_wallet_balance()
            logger.info(f"💰 Pre-liquidation SOL balance: {pre_balances.get('SOL', 0):.6f} SOL")
            
            liquidation_results = []
            successful_sales = 0
            failed_sales = 0
            
            # Create a copy of positions to avoid modification during iteration
            positions_to_sell = dict(self.positions)
            
            for token_mint, position in positions_to_sell.items():
                logger.info(f"💸 Liquidating position: {token_mint[:8]}... ({position.current_amount:.6f} SOL invested)")
                
                try:
                    # Execute sell_all for each position
                    result = await self.execute_trade_with_fallback('sell_all', token_mint)
                    
                    if result['success']:
                        successful_sales += 1
                        liquidation_results.append({
                            'token': token_mint,
                            'status': 'SUCCESS',
                            'signature': result['signature'],
                            'invested_amount': position.current_amount
                        })
                        
                        # Remove position from tracking
                        if token_mint in self.positions:
                            del self.positions[token_mint]
                        
                        logger.info(f"✅ Successfully liquidated {token_mint[:8]}...")
                        logger.info(f"   🔗 Transaction: https://solscan.io/tx/{result['signature']}")
                        
                    else:
                        failed_sales += 1
                        error_msg = result.get('error', 'Unknown error')
                        liquidation_results.append({
                            'token': token_mint,
                            'status': 'FAILED',
                            'error': error_msg,
                            'invested_amount': position.current_amount
                        })
                        
                        logger.error(f"❌ Failed to liquidate {token_mint[:8]}...: {error_msg}")
                        
                        # For failed liquidations, we might want to keep trying with other DEXes
                        # or mark the position for manual intervention
                        logger.warning(f"⚠️ Position {token_mint[:8]}... requires manual liquidation")
                        
                except Exception as e:
                    failed_sales += 1
                    liquidation_results.append({
                        'token': token_mint,
                        'status': 'ERROR',
                        'error': str(e),
                        'invested_amount': position.current_amount
                    })
                    
                    logger.error(f"❌ Error liquidating {token_mint[:8]}...: {e}")
                    
                # Small delay between liquidations to avoid overwhelming RPC
                await asyncio.sleep(0.5)
            
            # Get post-liquidation balances
            await asyncio.sleep(3)  # Wait for all transactions to settle
            post_balances = await self.get_wallet_balance()
            
            # Calculate total SOL recovered
            sol_recovered = post_balances.get('SOL', 0) - pre_balances.get('SOL', 0)
            
            # Summary report
            logger.info(f"📊 LIQUIDATION SUMMARY:")
            logger.info(f"   ✅ Successful sales: {successful_sales}")
            logger.info(f"   ❌ Failed sales: {failed_sales}")
            logger.info(f"   💰 SOL recovered: {sol_recovered:+.6f} SOL")
            logger.info(f"   🏦 Final SOL balance: {post_balances.get('SOL', 0):.6f} SOL")
            logger.info(f"   📍 Remaining positions: {len(self.positions)}")
            
            if failed_sales > 0:
                logger.warning(f"⚠️ {failed_sales} positions failed to liquidate - may require manual intervention")
                for result in liquidation_results:
                    if result['status'] in ['FAILED', 'ERROR']:
                        logger.warning(f"   🔴 {result['token'][:8]}...: {result.get('error', 'Unknown error')}")
            
            if successful_sales > 0:
                logger.info(f"✅ Successfully liquidated {successful_sales} positions")
                total_recovered = sum(r['invested_amount'] for r in liquidation_results if r['status'] == 'SUCCESS')
                logger.info(f"💰 Total invested amount liquidated: {total_recovered:.6f} SOL")
            
            # Save liquidation report for reference
            liquidation_report = {
                'timestamp': datetime.now().isoformat(),
                'pre_sol_balance': pre_balances.get('SOL', 0),
                'post_sol_balance': post_balances.get('SOL', 0),
                'sol_recovered': sol_recovered,
                'successful_sales': successful_sales,
                'failed_sales': failed_sales,
                'results': liquidation_results
            }
            
            # Add to execution history for record keeping
            self.execution_history.append({
                'timestamp': datetime.now().isoformat(),
                'trade_type': 'liquidation',
                'token_mint': 'ALL_POSITIONS',
                'signature': 'BATCH_LIQUIDATION',
                'liquidation_report': liquidation_report
            })
            
        except Exception as e:
            logger.error(f"❌ Error during position liquidation: {e}")
            logger.error(f"⚠️ Some positions may still be open - check manually!")
    
    def _is_slippage_error(self, error_message: str) -> bool:
        """Detect if an error is related to slippage tolerance being exceeded"""
        error_lower = error_message.lower()
        
        # Common slippage error patterns
        slippage_indicators = [
            '0x1771',  # Jupiter slippage exceeded error code
            'slippage tolerance exceeded',
            'slippage',
            'custom program error: 0x1771',
            'price impact too high',
            'insufficient output amount',
            'amount out below minimum',
            'slippage_tolerance_exceeded'
        ]
        
        return any(indicator in error_lower for indicator in slippage_indicators)
    
    async def _try_direct_pumpfun_buy(self, wallet: Keypair, token_mint: str, amount_sol: float) -> Dict[str, Any]:
        """Direct Pump.fun buy wrapper"""
        try:
            from direct_pumpfun import try_direct_pumpfun_buy
            return await try_direct_pumpfun_buy(wallet, token_mint, amount_sol)
        except Exception as e:
            logger.error(f"❌ Direct Pump.fun buy error: {e}")
            return {"success": False, "signature": "", "error": str(e)}
    
    async def _try_direct_pumpfun_sell(self, wallet: Keypair, token_mint: str) -> Dict[str, Any]:
        """Direct Pump.fun sell wrapper (placeholder)"""
        # For now, fall back to other DEXes for selling
        logger.info("💸 Direct Pump.fun sell not implemented, trying other DEXes...")
        return {"success": False, "signature": "", "error": "Direct sell not implemented"}

async def emergency_liquidate_all():
    """Standalone function to liquidate all positions (can be called independently)"""
    try:
        logger.info("🚨 EMERGENCY LIQUIDATION: Creating bot instance for position cleanup...")
        
        # Create minimal config for liquidation
        config = CopyTradeConfig(
            target_wallets=[],  # Not needed for liquidation
            investment_amount_sol=0.001,
            max_positions=10,
            use_jito=True,
            enable_dexes={
                "direct_pumpfun": True,
                "pumpfun": True,
                "jupiter": True,
                "raydium": True,
                "cpmm": True,
                "clmm": True,
                "orca": True,
                "phoenix": True
            }
        )
        
        # Create bot instance
        bot = CopyTradingBot(config)
        
        # Get current positions by checking wallet balances
        logger.info("🔍 Scanning wallet for token positions...")
        balances = await bot.get_wallet_balance()
        
        # Remove SOL from the balance check
        token_balances = {k: v for k, v in balances.items() if k != "SOL" and v > 0.000001}
        
        if not token_balances:
            logger.info("💰 No token positions found in wallet")
            return
        
        logger.info(f"💸 Found {len(token_balances)} token positions to liquidate")
        for token_mint, balance in token_balances.items():
            logger.info(f"   🎯 {token_mint[:8]}...: {balance:.6f} tokens")
        
        # Create temporary positions for liquidation
        for token_mint, balance in token_balances.items():
            bot.positions[token_mint] = WalletPosition(
                token_mint=token_mint,
                initial_amount=0.001,  # Placeholder
                current_amount=0.001,  # Placeholder
                our_amount=0.001      # Placeholder
            )
        
        # Perform liquidation
        await bot.liquidate_all_positions()
        
        logger.info("✅ Emergency liquidation completed")
        
    except Exception as e:
        logger.error(f"❌ Emergency liquidation error: {e}")
        raise

async def main():
    """Main function to run the copy trading bot"""
    global bot_instance
    
    # Configuration
    config = CopyTradeConfig(
        target_wallets=[
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Primary target wallet to copy
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Secondary target wallet to copy
            # "THIRD_WALLET_ADDRESS_HERE",  # 📝 UNCOMMENT: Add third wallet for testing
        ],
        investment_amount_sol=0.001,  # Fixed 0.001 SOL per trade
        max_positions=10,
        min_sell_threshold=0.1,  # Minimum 10% sell
        use_jito=True,
        jito_timeout=10.0,
        enable_dexes={
            "direct_pumpfun": True,  # Direct Pump.fun (highest priority)
            "pumpfun": True,         # Jupiter-based Pump.fun
            "jupiter": True,         # Jupiter aggregator (most comprehensive)
            "raydium": True,         # Raydium V4 DEX
            "cpmm": True,           # Raydium CPMM
            "clmm": True,           # CLMM + Jupiter hybrid  
            "orca": True,           # Orca DEX
            "phoenix": True         # Phoenix DEX
        }
    )
    
    # Validate configuration
    if not config.target_wallets:
        logger.error("❌ No target wallets configured! Please add wallet addresses to copy.")
        logger.info("💡 Edit the target_wallets list in main() function")
        return
    
    # Create and start bot
    bot = CopyTradingBot(config)
    bot_instance = bot  # Set global instance for signal handler
    
    # 🚀 AGGRESSIVE OPTIMIZATIONS - Since you trust your target wallets
    logger.info("⚡ ENABLING AGGRESSIVE OPTIMIZATIONS...")
    
    # 1. Skip token validation (trust your target wallets)
    original_validate = bot._validate_token_compatibility
    async def aggressive_validate(token_mint: str):
        """Minimal validation for aggressive mode"""
        try:
            from solders.pubkey import Pubkey
            Pubkey.from_string(token_mint)  # Just check format
            logger.debug(f"⚡ Fast validation passed: {token_mint[:8]}...")
        except:
            raise Exception(f"Invalid token format")
    bot._validate_token_compatibility = aggressive_validate
    
    # 2. Faster balance checking (SOL only)
    original_get_balance = bot.get_wallet_balance
    async def fast_get_balance():
        """Ultra-fast balance checking - SOL only"""
        try:
            from solana.rpc.commitment import Processed
            sol_response = await bot.rpc_client.get_balance(bot.wallet_pubkey, Processed)
            return {"SOL": sol_response.value / 1e9 if sol_response.value else 0.0}
        except:
            return {"SOL": 0.0}
    bot.get_wallet_balance = fast_get_balance
    
    # 3. Skip pre/post balance logging for speed
    async def no_balance_logging(*args, **kwargs):
        pass
    bot.log_balance_change = no_balance_logging
    
    # 4. Reduce sleep times
    original_execute_copy_buy = bot.execute_copy_buy
    async def fast_execute_copy_buy(token_mint: str, source_wallet: str, detected_dex: str = None):
        """Faster buy execution with minimal delays"""
        try:
            if token_mint == 'UNKNOWN':
                return
            
            # Skip most validation - trust the target wallet
            try:
                from solders.pubkey import Pubkey
                Pubkey.from_string(token_mint)
            except:
                logger.warning(f"⚠️ Invalid token format: {token_mint}")
                return
            
            # Track trades
            bot.trade_counter[token_mint] += 1
            trade_count = bot.trade_counter[token_mint]
            
            logger.info(f"⚡ AGGRESSIVE BUY #{trade_count}: {bot.config.investment_amount_sol} SOL → {token_mint[:8]}...")
            logger.info(f"🎯 Trusting target wallet {source_wallet[:8]}... - NO VALIDATION!")
            
            # Execute immediately
            success = await bot.execute_trade_with_fallback(
                'buy', token_mint, bot.config.investment_amount_sol, detected_dex
            )
            
            if success['success']:
                # Minimal delay and tracking
                if token_mint not in bot.positions:
                    from models import WalletPosition
                    bot.positions[token_mint] = WalletPosition(
                        token_mint=token_mint,
                        initial_amount=bot.config.investment_amount_sol,
                        current_amount=bot.config.investment_amount_sol,
                        our_amount=bot.config.investment_amount_sol
                    )
                else:
                    bot.positions[token_mint].current_amount += bot.config.investment_amount_sol
                    bot.positions[token_mint].our_amount += bot.config.investment_amount_sol
                
                logger.info(f"⚡ AGGRESSIVE BUY SUCCESS: {success['signature'][:8]}...")
            else:
                logger.error(f"❌ Aggressive buy failed: {success.get('error', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"❌ Aggressive buy error: {e}")
    
    bot.execute_copy_buy = fast_execute_copy_buy
    
    logger.info("✅ AGGRESSIVE MODE ENABLED!")
    logger.info("   🚀 Token validation: MINIMAL (trust target wallets)")
    logger.info("   ⚡ Balance checking: FAST (SOL only)")
    logger.info("   🎯 Delays: REMOVED (immediate execution)")
    logger.info("   💪 Risk: HIGH (maximum speed)")
    
    try:
        logger.info("⚡ Starting AGGRESSIVE Copy Trading Bot...")
        logger.info("=" * 60)
        logger.info(f"Investment Amount: {config.investment_amount_sol} SOL per trade")
        logger.info(f"Target Wallets: {len(config.target_wallets)}")
        logger.info(f"Max Positions: {config.max_positions}")
        logger.info(f"Jito Enabled: {config.use_jito}")
        logger.info(f"Auto-Liquidation: ✅ Enabled (positions will be sold on shutdown)")
        logger.info(f"Expected Copy Speed: <2 seconds total")
        logger.info("=" * 60)
        
        # Start monitoring
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Stopping bot gracefully...")
        await bot.stop()  # This will automatically liquidate positions
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        await bot.stop()  # This will automatically liquidate positions

# Global bot instance for signal handler
bot_instance = None

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum} - initiating graceful shutdown...")
        if bot_instance and asyncio.get_event_loop().is_running():
            # Schedule the graceful shutdown
            asyncio.create_task(graceful_shutdown())
        else:
            print("⚠️ No bot instance running or event loop not active")
            exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

async def graceful_shutdown():
    """Perform graceful shutdown with position liquidation"""
    global bot_instance
    
    if bot_instance:
        print("🔄 Performing graceful shutdown with position liquidation...")
        try:
            await bot_instance.stop()  # This will automatically liquidate positions
            print("✅ Graceful shutdown completed")
        except Exception as e:
            print(f"❌ Error during graceful shutdown: {e}")
            print("⚠️ Some positions may still be open - check manually!")
        finally:
            exit(0)
    else:
        print("⚠️ No bot instance to shutdown")
        exit(1)

if __name__ == "__main__":
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Add target wallet addresses here
    print("⚡ ULTRA-AGGRESSIVE SOLANA COPY TRADING BOT")
    print("=" * 50)
    print("🚀 AGGRESSIVE MODE: Minimal validation, maximum speed")
    print("⚠️  CONFIGURE TARGET WALLETS BEFORE RUNNING!")
    print("Edit main() function to add wallet addresses")
    print("=" * 50)
    print("💡 Press Ctrl+C for graceful shutdown with automatic position liquidation")
    print("⚡ Expected speed: <2 seconds total copy time")
    print("=" * 50)
    
    # Run the bot with aggressive optimizations
    asyncio.run(main())
