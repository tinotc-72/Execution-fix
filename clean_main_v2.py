"""
🎯 CLEAN MAIN.PY - Pure orchestration, no execution logic
All trading logic is handled by separate modular components
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, Any

# Import your existing configuration and base components
try:
    from config import CopyTradeConfig, EnvKeys, WALLET
    from copy_trade_logger import get_copy_trade_logger
    CONFIG_AVAILABLE = True
    print("✅ Clean Main: Configuration available")
except ImportError:
    CONFIG_AVAILABLE = False
    print("❌ Clean Main: Configuration not available")

# Import modular trading coordinator
try:
    from trading_coordinator import create_trading_coordinator
    COORDINATOR_AVAILABLE = True
    print("✅ Clean Main: Trading coordinator available")
except ImportError:
    COORDINATOR_AVAILABLE = False
    print("❌ Clean Main: Trading coordinator not available")

# Import RPC and Jito services
try:
    from solana.rpc.async_api import AsyncClient
    from jito_enhanced_service import JitoEnhancedService
    RPC_AVAILABLE = True
    print("✅ Clean Main: RPC services available")
except ImportError:
    RPC_AVAILABLE = False
    print("❌ Clean Main: RPC services not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('clean_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class CleanCopyTradingBot:
    """
    🎯 CLEAN COPY TRADING BOT
    
    Pure orchestration layer - no execution logic
    All trading functionality delegated to modular components:
    - TradingCoordinator: Handles all trade detection and execution
    - SocketTradeDetector: Real-time WebSocket monitoring  
    - JitoTradeExecutor: Fast Jito-based execution
    - ModularExecutorManager: Fallback execution across all DEXes
    """
    
    def __init__(self, config: CopyTradeConfig):
        """Initialize bot with minimal setup - delegates to modules"""
        self.config = config
        self.is_running = False
        
        # Initialize basic components
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        
        # Initialize RPC connection
        if RPC_AVAILABLE:
            self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
            logger.info("✅ RPC client initialized")
        else:
            self.rpc_client = None
            logger.error("❌ RPC client not available")
            return
        
        # Initialize Jito service if enabled
        self.jito_service = None
        if config.use_jito:
            try:
                logger.info("🔧 Creating JitoEnhancedService...")
                self.jito_service = JitoEnhancedService(
                    preferred_region="london",
                    rpc_fallback_url=self.env_keys.HELIUS_RPC_URL,
                    wallet_keypair=self.wallet
                )
                logger.info("✅ JitoEnhancedService created successfully!")
            except Exception as jito_error:
                logger.error(f"❌ Failed to create JitoEnhancedService: {jito_error}")
                self.jito_service = None
        else:
            logger.info("🔧 Jito disabled in config")
        
        # Initialize CSV logging
        if CONFIG_AVAILABLE:
            self.csv_logger = get_copy_trade_logger("copy_trade_logs")
            logger.info("✅ CSV logger initialized")
        else:
            self.csv_logger = None
        
        # Initialize the trading coordinator (this handles everything)
        if COORDINATOR_AVAILABLE:
            self.trading_coordinator = create_trading_coordinator(
                config=config,
                wallet=self.wallet,
                rpc_client=self.rpc_client,
                jito_service=self.jito_service
            )
            logger.info("✅ Trading coordinator initialized")
        else:
            self.trading_coordinator = None
            logger.error("❌ Trading coordinator not available")
            return
        
        logger.info("✅ Clean Copy Trading Bot initialized")
        logger.info(f"   🎯 Target wallets: {len(self.config.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {self.config.investment_amount_sol} SOL")
        logger.info(f"   🚀 Jito enabled: {config.use_jito}")
    
    async def start_monitoring(self):
        """
        Start the bot - delegates everything to trading coordinator
        This is the ONLY method that does anything - pure delegation
        """
        if self.is_running:
            logger.warning("⚠️ Bot already running")
            return
        
        if not self.trading_coordinator:
            logger.error("❌ Cannot start - trading coordinator not available")
            return
        
        self.is_running = True
        logger.info("🚀 Starting Clean Copy Trading Bot...")
        
        try:
            # Delegate everything to the trading coordinator
            await self.trading_coordinator.start_monitoring()
            
        except KeyboardInterrupt:
            logger.info("👋 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Error in bot: {e}")
            logger.error(traceback.format_exc())
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self):
        """Stop the bot - delegates to trading coordinator"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping Clean Copy Trading Bot...")
        self.is_running = False
        
        if self.trading_coordinator:
            await self.trading_coordinator.stop_monitoring()
        
        if self.rpc_client:
            await self.rpc_client.close()
        
        logger.info("✅ Clean Copy Trading Bot stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status - delegates to trading coordinator"""
        if not self.trading_coordinator:
            return {'error': 'Trading coordinator not available'}
        
        base_status = {
            'bot_running': self.is_running,
            'wallet': str(self.wallet_pubkey),
            'target_wallets': len(self.config.target_wallets),
            'investment_amount': self.config.investment_amount_sol,
            'jito_enabled': self.config.use_jito and self.jito_service is not None
        }
        
        # Get detailed stats from trading coordinator
        coordinator_stats = self.trading_coordinator.get_stats()
        
        return {**base_status, **coordinator_stats}


async def main():
    """
    Main entry point - completely clean and simple
    Just configuration and delegation
    """
    if not CONFIG_AVAILABLE:
        print("❌ Configuration not available - cannot start bot")
        return
    
    if not COORDINATOR_AVAILABLE:
        print("❌ Trading coordinator not available - cannot start bot")
        return
    
    # Load configuration
    config = CopyTradeConfig(
        target_wallets=[
            # Add your target wallet addresses here
            "YourTargetWallet1Here",
            "YourTargetWallet2Here",
        ],
        investment_amount_sol=0.001,  # Adjust as needed
        use_jito=True,  # Enable Jito for speed
        enable_dexes={
            "pumpfun": True,
            "jupiter": True,
            "raydium": True,
            "cpmm": True,
            "clmm": True,
            "orca": True,
            "phoenix": False  # Disable if needed
        },
        slippage_tolerance=0.03  # 3% slippage
    )
    
    # Create and start the bot
    bot = CleanCopyTradingBot(config)
    
    try:
        # Start monitoring (this is it - everything else is modular)
        await bot.start_monitoring()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
    finally:
        await bot.stop_monitoring()


if __name__ == "__main__":
    print("🎯 Starting Clean Copy Trading Bot...")
    print("📋 All execution logic is handled by modular components:")
    print("   🔌 SocketTradeDetector: Real-time WebSocket monitoring")
    print("   🚀 JitoTradeExecutor: Fast Jito-based execution")
    print("   🔧 ModularExecutorManager: Multi-DEX fallback execution")
    print("   🎯 TradingCoordinator: Orchestrates everything")
    print()
    
    # Run the bot
    asyncio.run(main())
