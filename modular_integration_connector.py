"""
🔗 MODULAR INTEGRATION CONNECTOR
This file connects socket detection and Jito execution to main.py without adding logic to main.py
Links the separate socket_trade_detector.py and jito_trade_executor.py modules
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, List
from datetime import datetime, timezone

# Import your modular components
try:
    from socket_trade_detector import create_socket_trade_detector
    SOCKET_DETECTOR_AVAILABLE = True
    print("✅ Integration Connector: Socket Trade Detector available")
except ImportError:
    print("❌ Integration Connector: Socket Trade Detector not available")
    SOCKET_DETECTOR_AVAILABLE = False

try:
    from jito_trade_executor import create_jito_trade_executor
    JITO_EXECUTOR_AVAILABLE = True
    print("✅ Integration Connector: Jito Trade Executor available")
except ImportError:
    print("❌ Integration Connector: Jito Trade Executor not available")
    JITO_EXECUTOR_AVAILABLE = False

logger = logging.getLogger(__name__)

class ModularTradingSystem:
    """
    🔗 MODULAR TRADING SYSTEM CONNECTOR
    
    This class provides a single interface that main.py can use to:
    1. Start socket-based trade detection 
    2. Execute trades using Jito-enabled executors
    3. Coordinate between detection and execution modules
    
    NO LOGIC ADDED TO MAIN.PY - Everything is handled here!
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the modular trading system
        
        Args:
            config: Configuration dict containing:
                - target_wallets: List of wallets to monitor
                - wallet_keypair: Your trading wallet
                - rpc_client: RPC client
                - jito_service: Jito service for MEV protection
                - trading_config: Trading parameters
        """
        self.config = config
        
        # Core components
        self.target_wallets = config['target_wallets']
        self.wallet_keypair = config['wallet_keypair']
        self.rpc_client = config['rpc_client']
        self.jito_service = config.get('jito_service')
        self.trading_config = config.get('trading_config', {})
        
        # Modular components (will be initialized)
        self.socket_detector = None
        self.jito_executor = None
        
        # System state
        self.is_running = False
        self.trade_count = 0
        self.last_trade_time = None
        
        logger.info("🔗 Modular Trading System initialized")
        logger.info(f"   🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"   💎 Trading wallet: {str(self.wallet_keypair.pubkey())[:8]}...")
        logger.info(f"   ⚡ Jito service: {'✅ Available' if self.jito_service else '❌ Not available'}")
        
    async def initialize_components(self) -> bool:
        """Initialize all modular components"""
        try:
            logger.info("🔧 Initializing modular components...")
            
            # Initialize socket trade detector
            if SOCKET_DETECTOR_AVAILABLE:
                self.socket_detector = await create_socket_trade_detector(
                    target_wallets=self.target_wallets,
                    trade_callback=self._handle_detected_trade,  # This is the bridge!
                    rpc_client=self.rpc_client
                )
                
                if self.socket_detector:
                    logger.info("✅ Socket trade detector initialized")
                else:
                    logger.error("❌ Failed to initialize socket trade detector")
                    return False
            else:
                logger.error("❌ Socket detector not available")
                return False
                
            # Initialize Jito trade executor
            if JITO_EXECUTOR_AVAILABLE:
                self.jito_executor = create_jito_trade_executor(
                    wallet_keypair=self.wallet_keypair,
                    rpc_client=self.rpc_client,
                    jito_service=self.jito_service,
                    config=self.trading_config
                )
                
                if self.jito_executor:
                    logger.info("✅ Jito trade executor initialized")
                else:
                    logger.error("❌ Failed to initialize Jito trade executor")
                    return False
            else:
                logger.error("❌ Jito executor not available")
                return False
                
            logger.info("✅ All modular components initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing components: {e}")
            logger.error(traceback.format_exc())
            return False
            
    async def start_trading_system(self) -> bool:
        """Start the complete modular trading system"""
        try:
            if not self.socket_detector or not self.jito_executor:
                logger.error("❌ Components not initialized")
                return False
                
            logger.info("🚀 Starting modular trading system...")
            self.is_running = True
            
            # Start socket trade detection (this will run indefinitely)
            logger.info("🔌 Starting socket trade detection...")
            await self.socket_detector.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting trading system: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
            return False
            
    async def stop_trading_system(self):
        """Stop the complete modular trading system"""
        try:
            logger.info("⏹️ Stopping modular trading system...")
            self.is_running = False
            
            if self.socket_detector:
                await self.socket_detector.stop()
                
            logger.info("✅ Modular trading system stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping trading system: {e}")
            
    async def _handle_detected_trade(self, trade_info: Dict[str, Any]):
        """
        🌉 THE BRIDGE FUNCTION
        This is called by socket_trade_detector when a trade is detected
        It then calls jito_trade_executor to execute the trade
        
        This is where detection meets execution!
        """
        try:
            self.trade_count += 1
            self.last_trade_time = datetime.now(timezone.utc)
            
            signature = trade_info.get('signature', 'unknown')
            action = trade_info.get('action', 'unknown')
            token_mint = trade_info.get('token_mint', 'unknown')
            wallet = trade_info.get('wallet_address', 'unknown')
            
            logger.info(f"🌉 BRIDGE: Trade #{self.trade_count} detected!")
            logger.info(f"   📝 Signature: {signature[:12]}...")
            logger.info(f"   🎬 Action: {action.upper()}")
            logger.info(f"   💎 Token: {token_mint[:8]}...")
            logger.info(f"   👤 Source wallet: {wallet[:8]}...")
            
            # Validate we have an executor
            if not self.jito_executor:
                logger.error("❌ No Jito executor available for trade execution")
                return
                
            # Prepare trade for execution
            execution_trade_info = self._prepare_trade_for_execution(trade_info)
            
            # Execute the trade using Jito
            logger.info(f"⚡ Executing {action.upper()} trade via Jito...")
            execution_start = asyncio.get_event_loop().time()
            
            try:
                # This is where the magic happens - Jito execution!
                execution_result = await self.jito_executor.execute_trade(execution_trade_info)
                
                execution_time = asyncio.get_event_loop().time() - execution_start
                
                if execution_result.get('success'):
                    exec_signature = execution_result.get('signature', 'unknown')
                    exec_dex = execution_result.get('dex', 'unknown')
                    
                    logger.info(f"✅ EXECUTION SUCCESS!")
                    logger.info(f"   📝 Execution signature: {exec_signature[:12]}...")
                    logger.info(f"   🏪 DEX used: {exec_dex.upper()}")
                    logger.info(f"   ⚡ Execution time: {execution_time:.2f}s")
                    logger.info(f"   🎯 Copy trade #{self.trade_count} completed!")
                    
                else:
                    error = execution_result.get('error', 'Unknown error')
                    logger.error(f"❌ EXECUTION FAILED!")
                    logger.error(f"   Error: {error}")
                    logger.error(f"   ⚡ Failed after: {execution_time:.2f}s")
                    
            except asyncio.TimeoutError:
                execution_time = asyncio.get_event_loop().time() - execution_start
                logger.error(f"⏰ EXECUTION TIMEOUT after {execution_time:.2f}s")
                
            except Exception as exec_error:
                execution_time = asyncio.get_event_loop().time() - execution_start
                logger.error(f"❌ EXECUTION ERROR after {execution_time:.2f}s: {exec_error}")
                logger.error(traceback.format_exc())
                
        except Exception as e:
            logger.error(f"❌ Error in bridge function: {e}")
            logger.error(traceback.format_exc())
            
    def _prepare_trade_for_execution(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare detected trade info for execution"""
        execution_info = trade_info.copy()
        
        # Add execution-specific parameters
        execution_info.update({
            'amount_sol': self.trading_config.get('investment_amount_sol', 0.001),
            'sell_percentage': 100.0,  # Default to 100% for sells
            'slippage_bps': self.trading_config.get('slippage_bps', 1500),
            'max_retries': self.trading_config.get('max_retries', 2),
            'execution_timeout': self.trading_config.get('execution_timeout', 15.0)
        })
        
        return execution_info
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'is_running': self.is_running,
            'trade_count': self.trade_count,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'target_wallets': len(self.target_wallets),
            'components': {
                'socket_detector': self.socket_detector is not None,
                'jito_executor': self.jito_executor is not None
            }
        }
        
        # Add executor stats if available
        if self.jito_executor:
            try:
                executor_stats = self.jito_executor.get_stats()
                status['executor_stats'] = executor_stats
            except Exception as e:
                status['executor_stats_error'] = str(e)
                
        return status
        
    async def emergency_rescan(self, wallet: str = None, max_transactions: int = 100):
        """Trigger emergency rescan for missed trades"""
        if self.socket_detector:
            wallets_to_scan = [wallet] if wallet else self.target_wallets
            
            for w in wallets_to_scan:
                logger.warning(f"🚨 Emergency rescan for {w[:8]}...")
                await self.socket_detector.emergency_rescan(w, max_transactions)


# Simple interface functions for main.py integration

async def create_modular_trading_system(config: Dict[str, Any]):
    """
    🎯 MAIN.PY INTEGRATION FUNCTION
    
    This is the ONLY function main.py needs to call!
    
    Usage in main.py:
        config = {
            'target_wallets': self.target_wallets,
            'wallet_keypair': self.wallet,
            'rpc_client': self.rpc_client,
            'jito_service': self.jito_service,
            'trading_config': self.config.__dict__
        }
        
        trading_system = await create_modular_trading_system(config)
        await trading_system.start_trading_system()
    """
    try:
        # Create system
        system = ModularTradingSystem(config)
        
        # Initialize components
        if await system.initialize_components():
            logger.info("✅ Modular trading system created and initialized")
            return system
        else:
            logger.error("❌ Failed to initialize modular trading system")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creating modular trading system: {e}")
        logger.error(traceback.format_exc())
        return None


def get_integration_status():
    """Check if all required modules are available"""
    return {
        'socket_detector_available': SOCKET_DETECTOR_AVAILABLE,
        'jito_executor_available': JITO_EXECUTOR_AVAILABLE,
        'fully_operational': SOCKET_DETECTOR_AVAILABLE and JITO_EXECUTOR_AVAILABLE
    }
