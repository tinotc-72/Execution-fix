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

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Import utilities
from utils import get_transaction_with_logs, load_keypair

# Import specialized modules
from copy_trade_logger import get_copy_trade_logger

# Import execution coordinator for trading
from execution_coordinator import ExecutionCoordinator

# Import core services
try:
    from config import WALLET
    WALLET_AVAILABLE = True
except ImportError:
    from solders.keypair import Keypair
    WALLET = Keypair()
    WALLET_AVAILABLE = False

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

# Setup simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Global bot instance for signal handlers
bot_instance = None

@dataclass
class CopyTradeConfig:
    """Simple configuration for copy trading"""
    target_wallets: List[str]
    investment_amount_sol: float = 0.001  # Fixed: MEV executor minimum requirement
    max_positions: int = 10
    use_jito: bool = True
    slippage_tolerance: float = 0.15
    enable_dexes: Dict[str, bool] = field(default_factory=lambda: {
        "pumpfun": True,
        "jupiter": True,
        "raydium": True
    })

class SimpleCopyTradingBot:
    """Simple copy trading bot - just the essentials"""
    
    def __init__(self, config: CopyTradeConfig):
        self.config = config
        self.is_running = False
        
        # Core components
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
        
        # Execution coordinator for all trading
        self.execution_coordinator = ExecutionCoordinator(
            config=config,
            wallet=self.wallet,
            jito_service=None  # Can add Jito later if needed
        )
        
        # Simple state tracking
        self.target_wallets = config.target_wallets
        self.processed_signatures: Set[str] = set()
        
        # WebSocket handler
        self.ws_handler = None
        
        # Simple logging
        self.csv_logger = get_copy_trade_logger("simple_copy_logs")
        
        logger.info(f"✅ Simple Copy Trading Bot initialized")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {config.investment_amount_sol} SOL")

    def _validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        """Simple validation for trade info"""
        required_fields = ['action', 'wallet_address', 'signature', 'token_mint']
        
        for field in required_fields:
            if not trade_info.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check if wallet is in target list
        wallet_address = trade_info.get('wallet_address', '')
        if wallet_address not in self.target_wallets:
            logger.debug(f"Not a target wallet: {wallet_address[:8]}...")
            return False
        
        # Basic token mint validation
        token_mint = trade_info.get('token_mint', '')
        if len(token_mint) < 43:
            logger.warning(f"Invalid token mint: {token_mint}")
            return False
        
        logger.info(f"✅ Trade validation passed: {trade_info['action']} {token_mint[:8]}...")
        return True

    async def _handle_websocket_trade(self, trade_info: Dict[str, Any]):
        """Handle trades detected via WebSocket"""
        try:
            logger.info(f"🚨 TRADE DETECTED: {trade_info}")
            
            # Simple analysis if needed
            if trade_info.get('requires_analysis'):
                signature = trade_info.get('signature')
                wallet_address = trade_info.get('wallet_address')
                
                if signature and wallet_address:
                    # Use simple official analysis
                    result = await self._simple_trade_analysis(signature, wallet_address)
                    if result:
                        trade_info.update(result)
                    else:
                        logger.warning(f"Analysis failed for {signature[:8]}...")
                        return
            
            # Validate and process
            if self._validate_trade_info(trade_info):
                await self._process_detected_trade(trade_info)
            else:
                logger.warning(f"Trade validation failed - skipping")
                    
        except Exception as e:
            logger.error(f"❌ Error handling WebSocket trade: {e}")

    async def _simple_trade_analysis(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Simple trade analysis using official analyzer"""
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

    async def _process_detected_trade(self, trade_info: Dict[str, Any]):
        """Process validated trade - just copy it"""
        try:
            action = trade_info['action'].lower()
            token_mint = trade_info['token_mint']
            source_wallet = trade_info['wallet_address']
            
            logger.info(f"🎯 COPYING {action.upper()} for {token_mint[:8]}... from {source_wallet[:8]}...")
            
            if action == 'buy':
                logger.info(f"💎 Executing copy BUY")
                await self.execution_coordinator._execute_copy_buy(
                    token_mint=token_mint,
                    source_wallet=source_wallet,
                    detected_dex=trade_info.get('dex', 'Unknown'),
                    trade_info=trade_info
                )
            elif action == 'sell':
                logger.info(f"💸 Executing copy SELL")
                await self.execution_coordinator._execute_copy_sell(
                    token_mint=token_mint,
                    trade_info=trade_info,
                    source_wallet=source_wallet
                )
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                    
        except Exception as e:
            logger.error(f"❌ Error processing trade: {e}")

    async def start_monitoring(self):
        """Start simple WebSocket monitoring"""
        try:
            logger.info("🚀 Starting simple copy trading bot...")
            self.is_running = True
            
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
        """Simple status monitoring"""
        try:
            while self.is_running:
                try:
                    # Show status every 5 minutes
                    await asyncio.sleep(300)
                    
                    stats = self.execution_coordinator.get_execution_stats()
                    logger.info(f"📊 Status: {stats.get('total_executions', 0)} trades, "
                              f"{stats.get('success_rate', 0):.1f}% success rate")
                    
                except Exception as e:
                    logger.error(f"❌ Status loop error: {e}")
                    await asyncio.sleep(60)
                    
        except Exception as e:
            logger.error(f"❌ Status loop failed: {e}")

    async def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping simple copy trading bot...")
        self.is_running = False
        
        try:
            if self.ws_handler:
                await self.ws_handler.stop()
        except Exception as e:
            logger.error(f"Error stopping WebSocket: {e}")
        
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
    
    # Configuration
    config = CopyTradeConfig(
        target_wallets=[
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Target wallet 1
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Target wallet 2  
        ],
        investment_amount_sol=0.001,  # Fixed: MEV executor minimum requirement
        use_jito=False,
        slippage_tolerance=0.3
    )
    
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
