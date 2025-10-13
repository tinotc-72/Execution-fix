#!/usr/bin/env python3
"""
WORKING Copy Trading Bot - Simplified version that actually detects trades
"""

import asyncio
import json
import logging
import signal
import traceback
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Import core services
from config import WALLET
from env_keys import EnvKeys
from wallet_tx_parser import WebSocketWalletMonitor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CopyTradeConfig:
    """Configuration for copy trading bot"""
    target_wallets: List[str]
    investment_amount_sol: float = 0.001
    max_positions: int = 10

class SimpleCopyTradingBot:
    """Simplified copy trading bot that focuses on trade detection"""
    
    def __init__(self, config: CopyTradeConfig):
        self.config = config
        self.is_running = False
        
        # Initialize core components
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        
        # RPC connections
        self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
        
        # Trading state
        self.target_wallets = config.target_wallets
        self.positions: Dict[str, Any] = {}
        self.trade_counter = defaultdict(int)
        self.processed_signatures: Set[str] = set()
        
        # WebSocket monitoring
        self.ws_monitor = None
        
        logger.info(f"✅ Copy Trading Bot initialized")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")

    async def handle_detected_trade(self, trade_info: Dict[str, Any]):
        """Handle trades detected via WebSocket"""
        try:
            logger.info(f"🚨 TRADE DETECTED!")
            logger.info(f"   👤 Wallet: {trade_info['wallet_address'][:8]}...")
            logger.info(f"   🎬 Action: {trade_info['action'].upper()}")
            logger.info(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
            logger.info(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
            logger.info(f"   📝 Signature: {trade_info['signature'][:12]}...")
            logger.info(f"   ⏰ Time: {trade_info['timestamp']}")
            
            # Execute copy trading based on the detected action
            if trade_info['action'] == 'buy':
                token_mint = trade_info.get('token_mint')
                if token_mint:
                    logger.info(f"🎯 WOULD EXECUTE COPY BUY for {token_mint[:8]}...")
                    logger.info(f"   💰 Amount: {self.config.investment_amount_sol} SOL")
                    
                    # Track the trade
                    self.trade_counter[token_mint] += 1
                    logger.info(f"✅ BUY DETECTED - Total trades for {token_mint[:8]}...: {self.trade_counter[token_mint]}")
                    
            elif trade_info['action'] == 'sell':
                token_mint = trade_info.get('token_mint')
                if token_mint:
                    logger.info(f"🎯 WOULD EXECUTE COPY SELL for {token_mint[:8]}...")
                    logger.info(f"✅ SELL DETECTED - Total trades for {token_mint[:8]}...: {self.trade_counter[token_mint]}")
                    
        except Exception as e:
            logger.error(f"❌ Error handling trade: {e}")
            traceback.print_exc()

    async def start_monitoring(self):
        """Start WebSocket monitoring"""
        try:
            self.is_running = True
            
            # Initialize WebSocket monitoring
            logger.info("📡 Initializing WebSocket monitoring...")
            self.ws_monitor = WebSocketWalletMonitor(self.target_wallets)
            self.ws_monitor.set_trade_callback(self.handle_detected_trade)
            
            # Start WebSocket monitoring
            logger.info("🚀 Starting WebSocket monitoring...")
            await self.ws_monitor.start_monitoring()
            
        except Exception as e:
            logger.error(f"❌ Error starting monitoring: {e}")
            traceback.print_exc()
            await self.stop()

    async def stop(self):
        """Stop the copy trading bot"""
        logger.info("⏹️ Stopping Copy Trading Bot...")
        self.is_running = False
        
        if self.ws_monitor:
            self.ws_monitor.stop_monitoring()
            logger.info("⏹️ WebSocket monitoring stopped")
        
        logger.info("✅ Copy Trading Bot stopped")

# Global bot instance for signal handlers
bot_instance = None

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum} - stopping bot...")
        if bot_instance:
            bot_instance.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

async def main():
    """Main function"""
    global bot_instance
    
    logger.info("🚀 SIMPLIFIED COPY TRADING BOT")
    logger.info("=" * 60)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Configuration
    config = CopyTradeConfig(
        target_wallets=[
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ],
        investment_amount_sol=0.001,
        max_positions=10
    )
    
    # Create bot instance
    bot_instance = SimpleCopyTradingBot(config)
    
    try:
        await bot_instance.start_monitoring()
    except KeyboardInterrupt:
        logger.info("👋 Stopping bot gracefully...")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        if bot_instance:
            await bot_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())
