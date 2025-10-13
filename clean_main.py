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

class CleanCopyTradingBot:\n    \"\"\"\n    🎯 CLEAN COPY TRADING BOT\n    \n    Pure orchestration layer - no execution logic\n    All trading functionality delegated to modular components:\n    - TradingCoordinator: Handles all trade detection and execution\n    - SocketTradeDetector: Real-time WebSocket monitoring  \n    - JitoTradeExecutor: Fast Jito-based execution\n    - ModularExecutorManager: Fallback execution across all DEXes\n    \"\"\"\n    \n    def __init__(self, config: CopyTradeConfig):\n        \"\"\"Initialize bot with minimal setup - delegates to modules\"\"\"\n        self.config = config\n        self.is_running = False\n        \n        # Initialize basic components\n        self.env_keys = EnvKeys()\n        self.wallet = WALLET\n        self.wallet_pubkey = self.wallet.pubkey()\n        \n        # Initialize RPC connection\n        if RPC_AVAILABLE:\n            self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)\n            logger.info(\"✅ RPC client initialized\")\n        else:\n            self.rpc_client = None\n            logger.error(\"❌ RPC client not available\")\n            return\n        \n        # Initialize Jito service if enabled\n        self.jito_service = None\n        if config.use_jito:\n            try:\n                logger.info(\"🔧 Creating JitoEnhancedService...\")\n                self.jito_service = JitoEnhancedService(\n                    preferred_region=\"london\",\n                    rpc_fallback_url=self.env_keys.HELIUS_RPC_URL,\n                    wallet_keypair=self.wallet\n                )\n                logger.info(\"✅ JitoEnhancedService created successfully!\")\n            except Exception as jito_error:\n                logger.error(f\"❌ Failed to create JitoEnhancedService: {jito_error}\")\n                self.jito_service = None\n        else:\n            logger.info(\"🔧 Jito disabled in config\")\n        \n        # Initialize CSV logging\n        if CONFIG_AVAILABLE:\n            self.csv_logger = get_copy_trade_logger(\"copy_trade_logs\")\n            logger.info(\"✅ CSV logger initialized\")\n        else:\n            self.csv_logger = None\n        \n        # Initialize the trading coordinator (this handles everything)\n        if COORDINATOR_AVAILABLE:\n            self.trading_coordinator = create_trading_coordinator(\n                config=config,\n                wallet=self.wallet,\n                rpc_client=self.rpc_client,\n                jito_service=self.jito_service\n            )\n            logger.info(\"✅ Trading coordinator initialized\")\n        else:\n            self.trading_coordinator = None\n            logger.error(\"❌ Trading coordinator not available\")\n            return\n        \n        logger.info(\"✅ Clean Copy Trading Bot initialized\")\n        logger.info(f\"   🎯 Target wallets: {len(self.config.target_wallets)}\")\n        logger.info(f\"   💰 Investment per trade: {self.config.investment_amount_sol} SOL\")\n        logger.info(f\"   🚀 Jito enabled: {config.use_jito}\")\n    \n    async def start_monitoring(self):\n        \"\"\"\n        Start the bot - delegates everything to trading coordinator\n        This is the ONLY method that does anything - pure delegation\n        \"\"\"\n        if self.is_running:\n            logger.warning(\"⚠️ Bot already running\")\n            return\n        \n        if not self.trading_coordinator:\n            logger.error(\"❌ Cannot start - trading coordinator not available\")\n            return\n        \n        self.is_running = True\n        logger.info(\"🚀 Starting Clean Copy Trading Bot...\")\n        \n        try:\n            # Delegate everything to the trading coordinator\n            await self.trading_coordinator.start_monitoring()\n            \n        except KeyboardInterrupt:\n            logger.info(\"👋 Keyboard interrupt received\")\n        except Exception as e:\n            logger.error(f\"❌ Error in bot: {e}\")\n            logger.error(traceback.format_exc())\n        finally:\n            await self.stop_monitoring()\n    \n    async def stop_monitoring(self):\n        \"\"\"Stop the bot - delegates to trading coordinator\"\"\"\n        if not self.is_running:\n            return\n        \n        logger.info(\"🛑 Stopping Clean Copy Trading Bot...\")\n        self.is_running = False\n        \n        if self.trading_coordinator:\n            await self.trading_coordinator.stop_monitoring()\n        \n        if self.rpc_client:\n            await self.rpc_client.close()\n        \n        logger.info(\"✅ Clean Copy Trading Bot stopped\")\n    \n    def get_status(self) -> Dict[str, Any]:\n        \"\"\"Get current bot status - delegates to trading coordinator\"\"\"\n        if not self.trading_coordinator:\n            return {'error': 'Trading coordinator not available'}\n        \n        base_status = {\n            'bot_running': self.is_running,\n            'wallet': str(self.wallet_pubkey),\n            'target_wallets': len(self.config.target_wallets),\n            'investment_amount': self.config.investment_amount_sol,\n            'jito_enabled': self.config.use_jito and self.jito_service is not None\n        }\n        \n        # Get detailed stats from trading coordinator\n        coordinator_stats = self.trading_coordinator.get_stats()\n        \n        return {**base_status, **coordinator_stats}\n\n\nasync def main():\n    \"\"\"\n    Main entry point - completely clean and simple\n    Just configuration and delegation\n    \"\"\"\n    if not CONFIG_AVAILABLE:\n        print(\"❌ Configuration not available - cannot start bot\")\n        return\n    \n    if not COORDINATOR_AVAILABLE:\n        print(\"❌ Trading coordinator not available - cannot start bot\")\n        return\n    \n    # Load configuration\n    config = CopyTradeConfig(\n        target_wallets=[\n            # Add your target wallet addresses here\n            \"YourTargetWallet1Here\",\n            \"YourTargetWallet2Here\",\n        ],\n        investment_amount_sol=0.001,  # Adjust as needed\n        use_jito=True,  # Enable Jito for speed\n        enable_dexes={\n            \"pumpfun\": True,\n            \"jupiter\": True,\n            \"raydium\": True,\n            \"cpmm\": True,\n            \"clmm\": True,\n            \"orca\": True,\n            \"phoenix\": False  # Disable if needed\n        },\n        slippage_tolerance=0.03  # 3% slippage\n    )\n    \n    # Create and start the bot\n    bot = CleanCopyTradingBot(config)\n    \n    try:\n        # Start monitoring (this is it - everything else is modular)\n        await bot.start_monitoring()\n    except KeyboardInterrupt:\n        logger.info(\"👋 Shutting down...\")\n    except Exception as e:\n        logger.error(f\"❌ Fatal error: {e}\")\n        logger.error(traceback.format_exc())\n    finally:\n        await bot.stop_monitoring()\n\n\nif __name__ == \"__main__\":\n    print(\"🎯 Starting Clean Copy Trading Bot...\")\n    print(\"📋 All execution logic is handled by modular components:\")\n    print(\"   🔌 SocketTradeDetector: Real-time WebSocket monitoring\")\n    print(\"   🚀 JitoTradeExecutor: Fast Jito-based execution\")\n    print(\"   🔧 ModularExecutorManager: Multi-DEX fallback execution\")\n    print(\"   🎯 TradingCoordinator: Orchestrates everything\")\n    print()\n    \n    # Run the bot\n    asyncio.run(main())\n
