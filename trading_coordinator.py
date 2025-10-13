"""
🎯 TRADING COORDINATOR - Main execution orchestrator
Coordinates between trade detection and execution modules
Handles all trading logic without polluting main.py
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from collections import defaultdict

# Import modular components
try:
    from socket_trade_detector import SocketTradeDetector
    SOCKET_DETECTOR_AVAILABLE = True
    print("✅ Trading Coordinator: Socket detector available")
except ImportError:
    SOCKET_DETECTOR_AVAILABLE = False
    print("❌ Trading Coordinator: Socket detector not available")

try:
    from jito_trade_executor import JitoTradeExecutorManager
    JITO_EXECUTOR_AVAILABLE = True
    print("✅ Trading Coordinator: Jito executor available")
except ImportError:
    JITO_EXECUTOR_AVAILABLE = False
    print("❌ Trading Coordinator: Jito executor not available")

try:
    from modular_executor_manager import ModularExecutorManager, create_executor_manager
    MODULAR_EXECUTOR_AVAILABLE = True
    print("✅ Trading Coordinator: Modular executor manager available")
except ImportError:
    MODULAR_EXECUTOR_AVAILABLE = False
    print("❌ Trading Coordinator: Modular executor manager not available")

# Import your existing analysis tools
try:
    from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
    ANALYZER_AVAILABLE = True
    print("✅ Trading Coordinator: Official analyzer available")
except ImportError:
    ANALYZER_AVAILABLE = False
    print("❌ Trading Coordinator: Official analyzer not available")

logger = logging.getLogger(__name__)

class TradingCoordinator:
    """
    🎯 MAIN TRADING COORDINATOR
    
    Coordinates all trading activities:
    - Uses SocketTradeDetector for real-time detection
    - Uses JitoTradeExecutor for fast execution
    - Uses ModularExecutorManager for fallback execution
    - Handles all position tracking and trade logic
    - Keeps main.py completely clean
    """
    
    def __init__(self, config, wallet, rpc_client, jito_service=None):
        """Initialize trading coordinator with your existing components"""
        self.config = config
        self.wallet = wallet
        self.rpc_client = rpc_client
        self.jito_service = jito_service
        
        # State tracking
        self.is_running = False
        self.processed_signatures: Set[str] = set()
        self.positions: Dict[str, Any] = {}
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.trade_counter = defaultdict(int)
        self.failed_tokens: Dict[str, int] = defaultdict(int)
        self.execution_history: List[Dict[str, Any]] = []
        
        # Initialize modular components
        self._initialize_components()
        
        logger.info("✅ Trading Coordinator initialized")
        logger.info(f"   🎯 Target wallets: {len(config.target_wallets)}")
        logger.info(f"   💰 Investment per trade: {config.investment_amount_sol} SOL")
    
    def _initialize_components(self):
        """Initialize all modular trading components"""
        
        # 1. Initialize Socket Trade Detector
        if SOCKET_DETECTOR_AVAILABLE:
            self.socket_detector = SocketTradeDetector(
                target_wallets=self.config.target_wallets,
                trade_callback=self._handle_detected_trade,
                rpc_client=self.rpc_client
            )
            logger.info("✅ Socket Trade Detector initialized")
        else:
            self.socket_detector = None
            logger.warning("❌ Socket Trade Detector not available")
        
        # 2. Initialize Jito Trade Executor
        if JITO_EXECUTOR_AVAILABLE and self.jito_service:
            self.jito_executor = JitoTradeExecutorManager(
                wallet=self.wallet,
                rpc_client=self.rpc_client,
                jito_service=self.jito_service,
                config=self.config
            )
            logger.info("✅ Jito Trade Executor initialized")
        else:
            self.jito_executor = None
            if not JITO_EXECUTOR_AVAILABLE:
                logger.warning("❌ Jito Trade Executor not available")
            else:
                logger.warning("❌ Jito service not provided")
        
        # 3. Initialize Modular Executor Manager (fallback)
        if MODULAR_EXECUTOR_AVAILABLE:
            self.modular_executor = create_executor_manager(
                wallet=self.wallet,
                jito_service=self.jito_service,
                config=self.config
            )
            logger.info("✅ Modular Executor Manager initialized")
        else:
            self.modular_executor = None
            logger.warning("❌ Modular Executor Manager not available")
        
        # 4. Initialize Official Analyzer
        if ANALYZER_AVAILABLE:
            self.analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
            logger.info("✅ Official Wallet Analyzer initialized")
        else:
            self.analyzer = None
            logger.warning("❌ Official Wallet Analyzer not available")
    
    async def start_monitoring(self):
        """Start the trading system - main entry point"""
        if self.is_running:
            logger.warning("⚠️ Trading system already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting Trading Coordinator...")
        
        try:
            # Start socket-based trade detection
            if self.socket_detector:
                logger.info("🔌 Starting socket trade detection...")
                await self.socket_detector.start_monitoring()
            else:
                logger.warning("⚠️ No socket detector available - using fallback polling")
                # Start fallback polling mechanism
                asyncio.create_task(self._fallback_polling())
            
            # Keep the system running
            while self.is_running:
                await self._periodic_maintenance()
                await asyncio.sleep(30)  # Maintenance every 30 seconds
                
        except Exception as e:
            logger.error(f"❌ Error in trading coordinator: {e}")
            logger.error(traceback.format_exc())
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self):
        """Stop the trading system"""
        logger.info("🛑 Stopping Trading Coordinator...")
        self.is_running = False
        
        if self.socket_detector:
            await self.socket_detector.stop_monitoring()
        
        logger.info("✅ Trading Coordinator stopped")
    
    async def _handle_detected_trade(self, trade_info: Dict[str, Any]):
        """
        Handle trades detected by socket detector
        This is the main callback that processes all detected trades
        """
        try:
            start_time = time.time()
            logger.info(f"🎯 TRADE DETECTED: {trade_info['action'].upper()}")
            logger.info(f"   👤 Wallet: {trade_info['wallet_address'][:8]}...")
            logger.info(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
            logger.info(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
            
            # Skip if already processed
            signature = trade_info.get('signature')
            if signature and signature in self.processed_signatures:
                logger.debug(f"⏭️ Already processed: {signature[:8]}...")
                return
            
            # Mark as processed
            if signature:
                self.processed_signatures.add(signature)
            
            # Validate trade info
            if not self._validate_trade_info(trade_info):
                logger.warning("⚠️ Trade validation failed - skipping")
                return
            
            # Route to appropriate handler
            action = trade_info['action'].lower()
            if action == 'buy':
                await self._execute_copy_buy(trade_info)
            elif action == 'sell':
                await self._execute_copy_sell(trade_info)
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
            
            # Record execution time
            execution_time = time.time() - start_time
            logger.info(f"⚡ Trade processed in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error handling detected trade: {e}")
            logger.error(traceback.format_exc())
    
    async def _execute_copy_buy(self, trade_info: Dict[str, Any]):
        """Execute copy buy trade"""
        try:
            token_mint = trade_info['token_mint']
            amount_sol = self.config.investment_amount_sol
            source_wallet = trade_info['wallet_address']
            detected_dex = trade_info.get('dex', 'unknown')
            
            logger.info(f"💎 EXECUTING COPY BUY")
            logger.info(f"   🎯 Token: {token_mint[:8]}...")
            logger.info(f"   💰 Amount: {amount_sol} SOL")
            logger.info(f"   👤 Source: {source_wallet[:8]}...")
            logger.info(f"   🏪 DEX: {detected_dex}")
            
            # Try Jito execution first (fastest)
            if self.jito_executor and self.config.use_jito:
                logger.info("🚀 Attempting Jito execution...")
                jito_result = await self.jito_executor.execute_trade({
                    'action': 'buy',
                    'token_mint': token_mint,
                    'amount_sol': amount_sol,
                    'source_wallet': source_wallet,
                    'detected_dex': detected_dex,
                    'trade_info': trade_info
                })\n                \n                if jito_result.get('success'):\n                    logger.info(f\"✅ Jito buy executed: {jito_result.get('signature', 'No signature')[:12]}...\")\n                    await self._record_successful_trade('buy', token_mint, amount_sol, \n                                                       jito_result.get('signature'), 'jito')\n                    return\n                else:\n                    logger.warning(f\"⚠️ Jito buy failed: {jito_result.get('error', 'Unknown error')}\")\n            \n            # Fallback to modular executor\n            if self.modular_executor:\n                logger.info(\"🔄 Attempting modular executor fallback...\")\n                \n                # Try the detected DEX first, then others\n                dex_priority = [detected_dex] if detected_dex != 'unknown' else []\n                dex_priority.extend(['pumpfun', 'jupiter', 'raydium', 'cpmm', 'clmm', 'orca'])\n                \n                for dex in dex_priority:\n                    if not self.config.enable_dexes.get(dex, False):\n                        continue\n                        \n                    try:\n                        logger.info(f\"🎯 Trying {dex.upper()} executor...\")\n                        result = await self.modular_executor.execute_buy(\n                            token_mint=token_mint,\n                            amount_sol=amount_sol,\n                            preferred_dex=dex,\n                            trade_info=trade_info\n                        )\n                        \n                        if result.success:\n                            logger.info(f\"✅ {dex.upper()} buy executed: {result.signature[:12]}...\")\n                            await self._record_successful_trade('buy', token_mint, amount_sol, \n                                                               result.signature, dex)\n                            return\n                        else:\n                            logger.warning(f\"⚠️ {dex.upper()} buy failed: {result.error}\")\n                            \n                    except Exception as e:\n                        logger.error(f\"❌ Error with {dex} executor: {e}\")\n                        continue\n            \n            # All execution methods failed\n            logger.error(f\"❌ All buy execution methods failed for {token_mint[:8]}...\")\n            await self._record_failed_trade('buy', token_mint, amount_sol, 'all_methods_failed')\n            \n        except Exception as e:\n            logger.error(f\"❌ Error in copy buy execution: {e}\")\n            logger.error(traceback.format_exc())\n    \n    async def _execute_copy_sell(self, trade_info: Dict[str, Any]):\n        \"\"\"Execute copy sell trade\"\"\"\n        try:\n            token_mint = trade_info['token_mint']\n            source_wallet = trade_info['wallet_address']\n            detected_dex = trade_info.get('dex', 'unknown')\n            \n            # Check if we have this position\n            if token_mint not in self.positions:\n                logger.warning(f\"⚠️ No position found for {token_mint[:8]}... - skipping sell\")\n                return\n            \n            position = self.positions[token_mint]\n            logger.info(f\"💸 EXECUTING COPY SELL\")\n            logger.info(f\"   🎯 Token: {token_mint[:8]}...\")\n            logger.info(f\"   💰 Position: {position.get('amount', 0)} SOL invested\")\n            logger.info(f\"   👤 Source: {source_wallet[:8]}...\")\n            logger.info(f\"   🏪 DEX: {detected_dex}\")\n            \n            # Determine sell percentage (you can customize this logic)\n            sell_percentage = 100.0  # Default: sell all\n            \n            # Try Jito execution first (fastest)\n            if self.jito_executor and self.config.use_jito:\n                logger.info(\"🚀 Attempting Jito sell execution...\")\n                jito_result = await self.jito_executor.execute_trade({\n                    'action': 'sell',\n                    'token_mint': token_mint,\n                    'percentage': sell_percentage,\n                    'source_wallet': source_wallet,\n                    'detected_dex': detected_dex,\n                    'trade_info': trade_info\n                })\n                \n                if jito_result.get('success'):\n                    logger.info(f\"✅ Jito sell executed: {jito_result.get('signature', 'No signature')[:12]}...\")\n                    await self._record_successful_trade('sell', token_mint, 0, \n                                                       jito_result.get('signature'), 'jito')\n                    # Remove position\n                    del self.positions[token_mint]\n                    return\n                else:\n                    logger.warning(f\"⚠️ Jito sell failed: {jito_result.get('error', 'Unknown error')}\")\n            \n            # Fallback to modular executor\n            if self.modular_executor:\n                logger.info(\"🔄 Attempting modular executor sell fallback...\")\n                \n                # Try the detected DEX first, then others\n                dex_priority = [detected_dex] if detected_dex != 'unknown' else []\n                dex_priority.extend(['pumpfun', 'jupiter', 'raydium', 'cpmm', 'clmm', 'orca'])\n                \n                for dex in dex_priority:\n                    if not self.config.enable_dexes.get(dex, False):\n                        continue\n                        \n                    try:\n                        logger.info(f\"🎯 Trying {dex.upper()} sell executor...\")\n                        result = await self.modular_executor.execute_sell(\n                            token_mint=token_mint,\n                            percentage=sell_percentage,\n                            preferred_dex=dex,\n                            trade_info=trade_info\n                        )\n                        \n                        if result.success:\n                            logger.info(f\"✅ {dex.upper()} sell executed: {result.signature[:12]}...\")\n                            await self._record_successful_trade('sell', token_mint, 0, \n                                                               result.signature, dex)\n                            # Remove position\n                            del self.positions[token_mint]\n                            return\n                        else:\n                            logger.warning(f\"⚠️ {dex.upper()} sell failed: {result.error}\")\n                            \n                    except Exception as e:\n                        logger.error(f\"❌ Error with {dex} sell executor: {e}\")\n                        continue\n            \n            # All execution methods failed\n            logger.error(f\"❌ All sell execution methods failed for {token_mint[:8]}...\")\n            await self._record_failed_trade('sell', token_mint, 0, 'all_methods_failed')\n            \n        except Exception as e:\n            logger.error(f\"❌ Error in copy sell execution: {e}\")\n            logger.error(traceback.format_exc())\n    \n    def _validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:\n        \"\"\"Validate trade information before processing\"\"\"\n        required_fields = ['action', 'wallet_address', 'token_mint']\n        \n        for field in required_fields:\n            if not trade_info.get(field):\n                logger.warning(f\"⚠️ Missing required field: {field}\")\n                return False\n        \n        # Validate wallet is in target list\n        wallet_address = trade_info.get('wallet_address', '')\n        if wallet_address not in self.config.target_wallets:\n            logger.warning(f\"⚠️ Not a target wallet: {wallet_address[:8]}...\")\n            return False\n        \n        # Validate token mint\n        token_mint = trade_info.get('token_mint', '')\n        if len(token_mint) < 43 or len(token_mint) > 44:\n            logger.warning(f\"⚠️ Invalid token mint: {token_mint}\")\n            return False\n        \n        # Filter out system programs\n        system_programs = {\n            \"11111111111111111111111111111111\",\n            \"ComputeBudget111111111111111111111111111111\",\n            \"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA\",\n            \"ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL\",\n        }\n        \n        if token_mint in system_programs:\n            logger.warning(f\"⚠️ System program detected: {token_mint[:8]}...\")\n            return False\n        \n        return True\n    \n    async def _record_successful_trade(self, action: str, token_mint: str, amount: float, \n                                     signature: str, method: str):\n        \"\"\"Record successful trade execution\"\"\"\n        trade_record = {\n            'timestamp': datetime.now(timezone.utc),\n            'action': action,\n            'token_mint': token_mint,\n            'amount': amount,\n            'signature': signature,\n            'method': method,\n            'success': True\n        }\n        \n        self.execution_history.append(trade_record)\n        self.trade_counter[token_mint] += 1\n        \n        # Update positions\n        if action == 'buy':\n            self.positions[token_mint] = {\n                'amount': amount,\n                'timestamp': datetime.now(timezone.utc),\n                'signature': signature,\n                'method': method\n            }\n        \n        logger.info(f\"📊 Trade recorded: {action.upper()} {amount} SOL via {method.upper()}\")\n    \n    async def _record_failed_trade(self, action: str, token_mint: str, amount: float, reason: str):\n        \"\"\"Record failed trade execution\"\"\"\n        trade_record = {\n            'timestamp': datetime.now(timezone.utc),\n            'action': action,\n            'token_mint': token_mint,\n            'amount': amount,\n            'reason': reason,\n            'success': False\n        }\n        \n        self.execution_history.append(trade_record)\n        self.failed_tokens[token_mint] += 1\n        \n        logger.warning(f\"📊 Failed trade recorded: {action.upper()} {amount} SOL - {reason}\")\n    \n    async def _fallback_polling(self):\n        \"\"\"Fallback polling mechanism if socket detection is not available\"\"\"\n        logger.info(\"🔄 Starting fallback polling mechanism...\")\n        \n        while self.is_running:\n            try:\n                # Poll each target wallet for recent transactions\n                for wallet in self.config.target_wallets:\n                    await self._poll_wallet_transactions(wallet)\n                    \n                await asyncio.sleep(5)  # Poll every 5 seconds\n                \n            except Exception as e:\n                logger.error(f\"❌ Error in fallback polling: {e}\")\n                await asyncio.sleep(10)\n    \n    async def _poll_wallet_transactions(self, wallet: str):\n        \"\"\"Poll a specific wallet for recent transactions\"\"\"\n        try:\n            # Implementation would use your existing transaction polling logic\n            # This is a placeholder for the polling mechanism\n            pass\n            \n        except Exception as e:\n            logger.error(f\"❌ Error polling wallet {wallet[:8]}...: {e}\")\n    \n    async def _periodic_maintenance(self):\n        \"\"\"Perform periodic maintenance tasks\"\"\"\n        try:\n            # Display current status\n            logger.info(f\"📊 STATUS UPDATE:\")\n            logger.info(f\"   🎯 Positions: {len(self.positions)}\")\n            logger.info(f\"   📈 Total trades: {len(self.execution_history)}\")\n            logger.info(f\"   ⚡ Processed signatures: {len(self.processed_signatures)}\")\n            \n            # Cleanup old processed signatures (keep last 1000)\n            if len(self.processed_signatures) > 1000:\n                # Keep the most recent ones (this is a simple approach)\n                sorted_sigs = sorted(list(self.processed_signatures))\n                self.processed_signatures = set(sorted_sigs[-1000:])\n                logger.info(\"🧹 Cleaned up old processed signatures\")\n            \n        except Exception as e:\n            logger.error(f\"❌ Error in periodic maintenance: {e}\")\n    \n    def get_stats(self) -> Dict[str, Any]:\n        \"\"\"Get current trading statistics\"\"\"\n        successful_trades = [t for t in self.execution_history if t['success']]\n        failed_trades = [t for t in self.execution_history if not t['success']]\n        \n        return {\n            'total_trades': len(self.execution_history),\n            'successful_trades': len(successful_trades),\n            'failed_trades': len(failed_trades),\n            'success_rate': len(successful_trades) / len(self.execution_history) * 100 if self.execution_history else 0,\n            'active_positions': len(self.positions),\n            'processed_signatures': len(self.processed_signatures),\n            'is_running': self.is_running\n        }\n\n\n# Factory function for easy initialization from main.py\ndef create_trading_coordinator(config, wallet, rpc_client, jito_service=None) -> TradingCoordinator:\n    \"\"\"\n    Factory function to create trading coordinator\n    Use this in main.py to initialize the trading system\n    \"\"\"\n    return TradingCoordinator(\n        config=config,\n        wallet=wallet,\n        rpc_client=rpc_client,\n        jito_service=jito_service\n    )\n
