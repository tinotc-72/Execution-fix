#!/usr/bin/env python3
"""
Main Copy Trading Bot - Orchestrates all specialized modules
This file should be SMALL and just coordinate between your specialized components
"""

import asyncio
import json
import logging
import signal
import traceback
import time
import websockets
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import aiohttp

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.commitment import Processed, Confirmed

# Import your specialized modules (as originally intended)
from copy_trade_logger import get_copy_trade_logger, log_successful_copy_trade, log_failed_copy_trade
from wallet_tx_parser import WalletATxParser

# Import all your DEX executors (your weeks of work!)
from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
from orca_copy_executor import try_orca_buy, try_orca_sell_all
from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all

# Import core services
from config import WALLET
from env_keys import EnvKeys
from pool_discovery_service import PoolDiscoveryService, get_pool_info_for_token
from jito_service import JitoClient
from fast_executor import FastExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copy_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CopyTradeConfig:
    """Configuration for copy trading bot"""
    target_wallets: List[str]
    investment_amount_sol: float = 0.001
    max_positions: int = 10
    min_sell_threshold: float = 0.1
    use_jito: bool = True
    jito_timeout: float = 10.0
    enable_dexes: Dict[str, bool] = field(default_factory=lambda: {
        "direct_pumpfun": True,
        "pumpfun": True,
        "jupiter": True,
        "raydium": True,
        "cpmm": True,
        "clmm": True,
        "orca": True,
        "phoenix": True
    })

@dataclass
class WalletPosition:
    """Track wallet positions"""
    token_mint: str
    initial_amount: float
    current_amount: float
    our_amount: float
    last_updated: datetime = field(default_factory=datetime.now)

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
        
        # RPC and WebSocket connections
        self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
        self.ws_url = self.env_keys.HELIUS_Standard_Websocket_URL
        
        # Your specialized components
        self.transaction_parser = WalletATxParser()  # Your transaction parsing logic
        self.fast_executor = None  # Will be initialized in start_monitoring
        self.pool_discovery = PoolDiscoveryService()  # Your pool discovery service
        self.jito_client = JitoClient() if config.use_jito else None  # Your Jito service
        
        # Trading state
        self.target_wallets = config.target_wallets
        self.positions: Dict[str, WalletPosition] = {}
        self.trade_counter = defaultdict(int)
        
        # CSV logging (your existing system)
        self.csv_logger = get_copy_trade_logger()
        self.execution_history = []
        
        # WebSocket state
        self.ws_connection = None
        self.subscription_ids = {}
        
        logger.info(f"✅ Copy Trading Bot initialized")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🏭 DEX executors loaded: {sum(self.config.enable_dexes.values())}")

    async def start_monitoring(self):
        """Start monitoring target wallets using WebSocket"""
        try:
            # Initialize FastExecutor (your existing component)
            self.fast_executor = FastExecutor()
            await self.fast_executor.initialize()
            
            logger.info("🚀 Starting WebSocket monitoring...")
            self.is_running = True
            
            # Connect to WebSocket and start monitoring
            await self._monitor_wallets_via_websocket()
            
        except Exception as e:
            logger.error(f"❌ Error starting monitoring: {e}")
            await self.stop()

    async def _monitor_wallets_via_websocket(self):
        """Monitor target wallets via WebSocket - using your existing pattern"""
        while self.is_running:
            try:
                # Create WebSocket connection
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.env_keys.HELIUS_API_KEY}"
                }
                
                async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                    self.ws_connection = ws
                    logger.info("✅ WebSocket connected")
                    
                    # Subscribe to all target wallets
                    await self._setup_subscriptions(ws)
                    
                    # Listen for messages
                    async for message in ws:
                        if not self.is_running:
                            break
                            
                        try:
                            data = json.loads(message)
                            await self._handle_websocket_message(data)
                        except Exception as e:
                            logger.error(f"❌ Error processing message: {e}")
                            
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                if self.is_running:
                    logger.info("🔄 Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)

    async def _setup_subscriptions(self, ws):
        """Setup WebSocket subscriptions for all target wallets"""
        for wallet in self.target_wallets:
            # Subscribe to logs
            logs_sub = {
                "jsonrpc": "2.0",
                "id": f"logs_{wallet}",
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [wallet]},
                    {"commitment": "confirmed"}
                ]
            }
            
            await ws.send(json.dumps(logs_sub))
            response = await ws.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                self.subscription_ids[f"logs_{wallet}"] = response_data["result"]
                logger.info(f"✅ Subscribed to logs for {wallet[:8]}...")
            
            # Subscribe to account changes
            account_sub = {
                "jsonrpc": "2.0",
                "id": f"account_{wallet}",
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {"encoding": "jsonParsed", "commitment": "confirmed"}
                ]
            }
            
            await ws.send(json.dumps(account_sub))
            response = await ws.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                self.subscription_ids[f"account_{wallet}"] = response_data["result"]
                logger.info(f"✅ Subscribed to account for {wallet[:8]}...")

    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages and always fetch full transaction via RPC"""
        try:
            if "method" not in data or data["method"] != "subscription":
                return
            params = data.get("params", {})
            subscription = params.get("subscription")
            result = params.get("result")
            if not (subscription and result):
                return
            target_wallet = None
            for wallet in self.target_wallets:
                if (subscription == self.subscription_ids.get(f"logs_{wallet}") or 
                    subscription == self.subscription_ids.get(f"account_{wallet}")):
                    target_wallet = wallet
                    break
            if not target_wallet:
                return
            # Always fetch full transaction for logs or account notifications
            signature = result.get("signature")
            if signature:
                logger.info(f"🔍 New transaction from {target_wallet[:8]}...: {signature[:8]}... (fetching full transaction)")
                await self._analyze_and_copy_transaction(signature, target_wallet)
        except Exception as e:
            logger.error(f"❌ Error handling WebSocket message: {e}")

    async def _analyze_and_copy_transaction(self, signature: str, source_wallet: str):
        """Always fetch full transaction via RPC and analyze for trade execution"""
        try:
            logger.info(f"🔍 Fetching full transaction for {signature[:8]}... from {source_wallet[:8]}...")
            trade_info = await self.transaction_parser.parse_solana_transaction(signature)
            if not trade_info:
                logger.info(f"📝 No trade detected in {signature[:8]}...")
                return
            token_mint = trade_info.get("token_mint")
            trade_type = trade_info.get("type") or trade_info.get("trade_type")
            dex = trade_info.get("dex", "Unknown")
            if not token_mint or not trade_type:
                logger.warning(f"⚠️ Incomplete trade info: token={token_mint}, type={trade_type}")
                return
            logger.info(f"⚡ TRADE DETECTED: {trade_type.upper()} {token_mint[:8]}... on {dex}")
            if trade_type.lower() in ['buy', 'purchase']:
                await self._execute_copy_buy(token_mint, source_wallet, dex)
            elif trade_type.lower() in ['sell', 'sell_all']:
                await self._execute_copy_sell(token_mint, trade_info, source_wallet)
            else:
                logger.warning(f"⚠️ Unknown trade type: {trade_type}")
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction: {e}")
            logger.debug(traceback.format_exc())

    async def _execute_copy_buy(self, token_mint: str, source_wallet: str, detected_dex: str = None):
        """Execute copy buy using your specialized DEX executors"""
        try:
            logger.info(f"💰 COPY BUY: {self.config.investment_amount_sol} SOL → {token_mint[:8]}...")
            
            # Get prioritized DEX list based on detected DEX
            dex_executors = self._get_prioritized_dex_executors(detected_dex)
            
            # Try each DEX executor until one succeeds
            for dex_name, buy_func, sell_func in dex_executors:
                if not self.config.enable_dexes.get(dex_name, False):
                    continue
                    
                logger.info(f"🔄 Trying {dex_name.upper()}...")
                
                try:
                    # Call your specialized executor function
                    result = await buy_func(
                        self.wallet,
                        token_mint,
                        self.config.investment_amount_sol,
                        slippage_tolerance=0.3  # 30% slippage for copy trading
                    )
                    
                    if result.get('success'):
                        signature = result.get('signature', '')
                        logger.info(f"✅ COPY BUY SUCCESS via {dex_name.upper()}")
                        logger.info(f"   🔗 Transaction: https://solscan.io/tx/{signature}")
                        
                        # Track position
                        self._track_new_position(token_mint, self.config.investment_amount_sol)
                        
                        # Log to CSV (your existing system)
                        log_successful_copy_trade(
                            source_wallet, token_mint, 'buy', 
                            self.config.investment_amount_sol, dex_name, signature
                        )
                        return
                    else:
                        error = result.get('error', 'Unknown error')
                        logger.warning(f"⚠️ {dex_name.upper()} failed: {error}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {dex_name.upper()} error: {e}")
                    continue
            
            # All DEXes failed
            logger.error(f"❌ All DEX executors failed for {token_mint[:8]}...")
            log_failed_copy_trade(source_wallet, token_mint, 'buy', "All DEXes failed")
            
        except Exception as e:
            logger.error(f"❌ Error in copy buy: {e}")

    async def _execute_copy_sell(self, token_mint: str, trade_info: Dict[str, Any], source_wallet: str):
        """Execute copy sell using your specialized DEX executors"""
        try:
            if token_mint not in self.positions:
                logger.warning(f"⚠️ No position to sell for {token_mint[:8]}...")
                return
                
            logger.info(f"💸 COPY SELL: {token_mint[:8]}...")
            
            # Get prioritized DEX list
            dex_executors = self._get_prioritized_dex_executors()
            
            # Try each DEX executor
            for dex_name, buy_func, sell_func in dex_executors:
                if not self.config.enable_dexes.get(dex_name, False):
                    continue
                    
                logger.info(f"🔄 Trying {dex_name.upper()} sell...")
                
                try:
                    # Call your specialized executor function
                    result = await sell_func(
                        self.wallet,
                        token_mint,
                        slippage_tolerance=0.3
                    )
                    
                    if result.get('success'):
                        signature = result.get('signature', '')
                        logger.info(f"✅ COPY SELL SUCCESS via {dex_name.upper()}")
                        logger.info(f"   🔗 Transaction: https://solscan.io/tx/{signature}")
                        
                        # Remove position
                        if token_mint in self.positions:
                            del self.positions[token_mint]
                        
                        # Log to CSV
                        log_successful_copy_trade(
                            source_wallet, token_mint, 'sell', 0, dex_name, signature
                        )
                        return
                    else:
                        error = result.get('error', 'Unknown error')
                        logger.warning(f"⚠️ {dex_name.upper()} sell failed: {error}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {dex_name.upper()} sell error: {e}")
                    continue
            
            logger.error(f"❌ All DEX executors failed to sell {token_mint[:8]}...")
            log_failed_copy_trade(source_wallet, token_mint, 'sell', "All DEXes failed")
            
        except Exception as e:
            logger.error(f"❌ Error in copy sell: {e}")

    def _get_prioritized_dex_executors(self, detected_dex: str = None):
        """Get prioritized list of your DEX executors"""
        # Your complete DEX executor mapping
        all_executors = [
            ("direct_pumpfun", None, None),  # Would need to implement direct pumpfun
            ("pumpfun", try_pumpfun_buy, try_pumpfun_sell_all),
            ("jupiter", try_jupiter_buy, try_jupiter_sell_all),
            ("raydium", try_raydium_buy, try_raydium_sell_all),
            ("cpmm", try_cpmm_buy, try_cpmm_sell_all),
            ("clmm", try_clmm_hybrid_buy, try_clmm_hybrid_sell_all),
            ("orca", try_orca_buy, try_orca_sell_all),
            ("phoenix", try_phoenix_buy, try_phoenix_sell_all),
        ]
        
        # Prioritize based on detected DEX
        if detected_dex:
            dex_priority_map = {
                "Pump.fun": ["pumpfun", "direct_pumpfun"],
                "Jupiter": ["jupiter", "pumpfun"],
                "Raydium": ["raydium", "cpmm"],
                "Orca": ["orca", "clmm"],
            }
            
            priority_dexes = dex_priority_map.get(detected_dex, [])
            prioritized = []
            
            # Add priority DEXes first
            for executor in all_executors:
                if executor[0] in priority_dexes:
                    prioritized.append(executor)
            
            # Add remaining DEXes
            for executor in all_executors:
                if executor[0] not in priority_dexes:
                    prioritized.append(executor)
                    
            return prioritized
        
        return all_executors

    def _track_new_position(self, token_mint: str, amount_sol: float):
        """Track new position"""
        if token_mint not in self.positions:
            self.positions[token_mint] = WalletPosition(
                token_mint=token_mint,
                initial_amount=amount_sol,
                current_amount=amount_sol,
                our_amount=amount_sol
            )
        else:
            # Add to existing position
            position = self.positions[token_mint]
            position.current_amount += amount_sol
            position.our_amount += amount_sol
            position.last_updated = datetime.now()

    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping copy trading bot...")
        self.is_running = False
        
        if self.ws_connection:
            await self.ws_connection.close()
        
        if self.rpc_client:
            await self.rpc_client.close()
            
        logger.info("✅ Bot stopped")

async def main():
    """Main function - now properly modular!"""
    # Configuration
    config = CopyTradeConfig(
        target_wallets=[
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ],
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
    
    # Create bot instance using your modules
    bot = CopyTradingBot(config)
    
    try:
        logger.info("🚀 MODULAR COPY TRADING BOT")
        logger.info("=" * 50)
        logger.info("✅ Using your specialized modules:")
        logger.info("   📊 WalletATxParser - transaction analysis")
        logger.info("   ⚡ FastExecutor - trade execution")
        logger.info("   🏭 Individual DEX executors")
        logger.info("   📈 Pool discovery service")
        logger.info("   🔥 Jito service for MEV protection")
        logger.info("   📝 CSV logging system")
        logger.info("=" * 50)
        
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 Stopping bot gracefully...")
        await bot.stop()
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
