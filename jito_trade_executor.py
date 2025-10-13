"""
🚀 JITO TRADE EXECUTOR - Separate modular trade execution using Jito for maximum speed
This module handles all trade execution logic using your existing fast_executor with Jito
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict

# Import your existing Jito-enabled executor
try:
    from fast_executor import FastExecutor
    FAST_EXECUTOR_AVAILABLE = True
    print("✅ Jito Trade Executor: FastExecutor available")
except ImportError:
    print("❌ Jito Trade Executor: FastExecutor not available")
    FAST_EXECUTOR_AVAILABLE = False

# Import your existing executors
try:
    from official_executor_wrappers import (
        execute_pumpfun_buy, execute_pumpfun_sell,
        execute_jupiter_buy, execute_jupiter_sell,
        execute_raydium_buy, execute_raydium_sell,
        execute_cpmm_buy, execute_cpmm_sell,
        execute_clmm_buy, execute_clmm_sell
    )
    OFFICIAL_EXECUTORS_AVAILABLE = True
    print("✅ Jito Trade Executor: Official executors available")
except ImportError:
    print("❌ Jito Trade Executor: Official executors not available")
    OFFICIAL_EXECUTORS_AVAILABLE = False

# Import legacy executors as fallback
try:
    from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
    try_jupiter_buy = None
    try_jupiter_sell_all = None
    try_cpmm_buy = None
    try_cpmm_sell_all = None
    try_clmm_hybrid_buy = None
    try_clmm_hybrid_sell_all = None
    
    # Try to import other executors if available
    try:
        from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
    except ImportError:
        pass
        
    try:
        from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
    except ImportError:
        pass
        
    try:
        from clmm_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
    except ImportError:
        pass
        
    LEGACY_EXECUTORS_AVAILABLE = True
    print("✅ Jito Trade Executor: Legacy executors available")
except ImportError:
    print("❌ Jito Trade Executor: Legacy executors not available")
    LEGACY_EXECUTORS_AVAILABLE = False

logger = logging.getLogger(__name__)

class JitoTradeExecutor:
    """
    🚀 MODULAR JITO TRADE EXECUTOR
    - Handles all trade execution using Jito for maximum speed
    - Uses your existing fast_executor for Jito integration
    - Coordinates with specialized DEX executors
    - Pure execution logic - no detection
    """
    
    def __init__(self, wallet_keypair, rpc_client, jito_service=None, config=None):
        """
        Initialize Jito trade executor
        
        Args:
            wallet_keypair: Your wallet keypair for signing transactions
            rpc_client: RPC client for blockchain interactions  
            jito_service: Enhanced Jito service for MEV protection
            config: Trading configuration
        """
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_client = rpc_client
        self.jito_service = jito_service
        self.config = config or self._default_config()
        
        # Initialize FastExecutor with Jito if available
        self.fast_executor = None
        if FAST_EXECUTOR_AVAILABLE:
            try:
                self.fast_executor = FastExecutor(wallet_keypair)
                logger.info("✅ FastExecutor initialized with Jito integration")
            except Exception as e:
                logger.error(f"❌ Failed to initialize FastExecutor: {e}")
                
        # Execution statistics
        self.execution_stats = defaultdict(int)
        self.execution_history = []
        
        # DEX execution priorities (fastest to slowest)
        self.dex_priorities = [
            "direct_pumpfun",  # Highest priority for new meme coins
            "pumpfun", 
            "jupiter",
            "raydium_cpmm",
            "clmm",
            "orca"
        ]
        
        logger.info(f"🚀 Jito Trade Executor initialized")
        logger.info(f"   💎 Wallet: {str(self.wallet_pubkey)[:8]}...")
        logger.info(f"   ⚡ Jito Service: {'✅ Available' if jito_service else '❌ Not available'}")
        logger.info(f"   🚀 Fast Executor: {'✅ Available' if self.fast_executor else '❌ Not available'}")
        
    def _default_config(self):
        """Default trading configuration"""
        return {
            'investment_amount_sol': 0.001,
            'slippage_tolerance': 0.15,
            'slippage_bps': 1500,
            'max_retries': 2,
            'execution_timeout': 15.0,
            'enable_dexes': {
                "direct_pumpfun": True,
                "pumpfun": True,
                "jupiter": True,
                "raydium_cpmm": True,
                "clmm": True,
                "orca": True
            }
        }
        
    async def execute_buy_trade(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a buy trade using Jito for maximum speed
        
        Args:
            trade_info: Trade information including token_mint, amount, etc.
            
        Returns:
            Execution result with signature, success status, etc.
        """
        start_time = time.time()
        token_mint = trade_info.get('token_mint')
        amount_sol = trade_info.get('amount_sol', self.config['investment_amount_sol'])
        detected_dex = trade_info.get('dex', 'unknown')
        
        logger.info(f"🚀 EXECUTING BUY TRADE via Jito")
        logger.info(f"   💎 Token: {token_mint[:8] if token_mint else 'Unknown'}...")
        logger.info(f"   💰 Amount: {amount_sol} SOL")
        logger.info(f"   🏪 Detected DEX: {detected_dex}")
        
        # Determine execution strategy based on detected DEX
        execution_strategy = self._determine_execution_strategy(detected_dex, 'buy')
        
        for attempt, (dex_name, executor_func) in enumerate(execution_strategy, 1):
            if not self.config['enable_dexes'].get(dex_name, False):
                logger.debug(f"⏭️ Skipping disabled DEX: {dex_name}")
                continue
                
            try:
                logger.info(f"🎯 Attempt {attempt}: {dex_name.upper()} BUY")
                
                # Execute using appropriate method
                if self.fast_executor and dex_name in ["direct_pumpfun", "fast_execution"]:
                    # Use FastExecutor with Jito for maximum speed
                    result = await self._execute_with_fast_executor(
                        'buy', token_mint, amount_sol, dex_name
                    )
                else:
                    # Use specialized DEX executor
                    result = await self._execute_with_dex_executor(
                        executor_func, token_mint, amount_sol, 'buy'
                    )
                
                execution_time = time.time() - start_time
                
                if result and result.get('success'):
                    logger.info(f"✅ BUY SUCCESS via {dex_name.upper()}")
                    logger.info(f"   📝 Signature: {result.get('signature', 'Unknown')[:12]}...")
                    logger.info(f"   ⚡ Execution time: {execution_time:.2f}s")
                    
                    # Update statistics
                    self.execution_stats[f"{dex_name}_buy_success"] += 1
                    self.execution_stats["total_buy_success"] += 1
                    
                    # Record execution
                    self._record_execution(trade_info, result, dex_name, 'buy', execution_time)
                    
                    return {
                        'success': True,
                        'signature': result.get('signature'),
                        'dex': dex_name,
                        'execution_time': execution_time,
                        'amount_sol': amount_sol,
                        'token_mint': token_mint,
                        'method': 'jito_execution'
                    }
                else:
                    logger.warning(f"⚠️ {dex_name.upper()} BUY failed: {result.get('error', 'Unknown error')}")
                    self.execution_stats[f"{dex_name}_buy_failed"] += 1
                    
            except Exception as e:
                logger.error(f"❌ {dex_name.upper()} BUY exception: {e}")
                self.execution_stats[f"{dex_name}_buy_error"] += 1
                
                # Continue to next DEX on error
                continue
                
        # All attempts failed
        execution_time = time.time() - start_time
        logger.error(f"❌ ALL BUY ATTEMPTS FAILED for {token_mint[:8]}... after {execution_time:.2f}s")
        self.execution_stats["total_buy_failed"] += 1
        
        return {
            'success': False,
            'error': 'All execution attempts failed',
            'execution_time': execution_time,
            'attempts': len(execution_strategy),
            'token_mint': token_mint
        }
        
    async def execute_sell_trade(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a sell trade using Jito for maximum speed
        
        Args:
            trade_info: Trade information including token_mint, percentage, etc.
            
        Returns:
            Execution result with signature, success status, etc.
        """
        start_time = time.time()
        token_mint = trade_info.get('token_mint')
        sell_percentage = trade_info.get('sell_percentage', 100.0)  # Default to 100%
        detected_dex = trade_info.get('dex', 'unknown')
        
        logger.info(f"🚀 EXECUTING SELL TRADE via Jito")
        logger.info(f"   💎 Token: {token_mint[:8] if token_mint else 'Unknown'}...")
        logger.info(f"   📊 Percentage: {sell_percentage}%")
        logger.info(f"   🏪 Detected DEX: {detected_dex}")
        
        # Determine execution strategy based on detected DEX
        execution_strategy = self._determine_execution_strategy(detected_dex, 'sell')
        
        for attempt, (dex_name, executor_func) in enumerate(execution_strategy, 1):
            if not self.config['enable_dexes'].get(dex_name, False):
                logger.debug(f"⏭️ Skipping disabled DEX: {dex_name}")
                continue
                
            try:
                logger.info(f"🎯 Attempt {attempt}: {dex_name.upper()} SELL")
                
                # Execute using appropriate method
                if self.fast_executor and dex_name in ["direct_pumpfun", "fast_execution"]:
                    # Use FastExecutor with Jito for maximum speed
                    result = await self._execute_with_fast_executor(
                        'sell', token_mint, sell_percentage, dex_name
                    )
                else:
                    # Use specialized DEX executor
                    result = await self._execute_with_dex_executor(
                        executor_func, token_mint, sell_percentage, 'sell'
                    )
                
                execution_time = time.time() - start_time
                
                if result and result.get('success'):
                    logger.info(f"✅ SELL SUCCESS via {dex_name.upper()}")
                    logger.info(f"   📝 Signature: {result.get('signature', 'Unknown')[:12]}...")
                    logger.info(f"   ⚡ Execution time: {execution_time:.2f}s")
                    
                    # Update statistics
                    self.execution_stats[f"{dex_name}_sell_success"] += 1
                    self.execution_stats["total_sell_success"] += 1
                    
                    # Record execution
                    self._record_execution(trade_info, result, dex_name, 'sell', execution_time)
                    
                    return {
                        'success': True,
                        'signature': result.get('signature'),
                        'dex': dex_name,
                        'execution_time': execution_time,
                        'sell_percentage': sell_percentage,
                        'token_mint': token_mint,
                        'method': 'jito_execution'
                    }
                else:
                    logger.warning(f"⚠️ {dex_name.upper()} SELL failed: {result.get('error', 'Unknown error')}")
                    self.execution_stats[f"{dex_name}_sell_failed"] += 1
                    
            except Exception as e:
                logger.error(f"❌ {dex_name.upper()} SELL exception: {e}")
                self.execution_stats[f"{dex_name}_sell_error"] += 1
                
                # Continue to next DEX on error
                continue
                
        # All attempts failed
        execution_time = time.time() - start_time
        logger.error(f"❌ ALL SELL ATTEMPTS FAILED for {token_mint[:8]}... after {execution_time:.2f}s")
        self.execution_stats["total_sell_failed"] += 1
        
        return {
            'success': False,
            'error': 'All execution attempts failed',
            'execution_time': execution_time,
            'attempts': len(execution_strategy),
            'token_mint': token_mint
        }
        
    async def _execute_with_fast_executor(self, action: str, token_mint: str, amount: float, dex_name: str) -> Dict[str, Any]:
        """Execute trade using FastExecutor with Jito integration"""
        try:
            logger.info(f"⚡ Using FastExecutor with Jito for {action.upper()}")
            
            if action == 'buy':
                # Build buy transaction and submit via FastExecutor
                signature = await self.fast_executor.execute_buy_trade(
                    token_mint=token_mint,
                    amount_sol=amount,
                    slippage_bps=self.config['slippage_bps']
                )
            else:  # sell
                # Build sell transaction and submit via FastExecutor
                signature = await self.fast_executor.execute_sell_trade(
                    token_mint=token_mint,
                    sell_percentage=amount,
                    slippage_bps=self.config['slippage_bps']
                )
            
            if signature:
                return {
                    'success': True,
                    'signature': signature,
                    'method': 'fast_executor_jito'
                }
            else:
                return {
                    'success': False,
                    'error': 'FastExecutor returned no signature'
                }
                
        except Exception as e:
            logger.error(f"❌ FastExecutor error: {e}")
            return {
                'success': False,
                'error': f'FastExecutor error: {str(e)}'
            }
            
    async def _execute_with_dex_executor(self, executor_func, token_mint: str, amount: float, action: str) -> Dict[str, Any]:
        """Execute trade using specialized DEX executor"""
        try:
            logger.info(f"🏪 Using DEX executor for {action.upper()}")
            
            if action == 'buy':
                result = await executor_func(
                    self.wallet_keypair,
                    token_mint,
                    amount,
                    slippage_bps=self.config['slippage_bps']
                )
            else:  # sell
                result = await executor_func(
                    self.wallet_keypair,
                    token_mint,
                    percentage=amount
                )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ DEX executor error: {e}")
            return {
                'success': False,
                'error': f'DEX executor error: {str(e)}'
            }
            
    def _determine_execution_strategy(self, detected_dex: str, action: str) -> List[Tuple[str, callable]]:
        """
        Determine execution strategy based on detected DEX and action
        Returns list of (dex_name, executor_function) tuples in priority order
        """
        strategy = []
        
        # Map detected DEX to appropriate executors
        dex_mapping = {
            'pumpfun': ['direct_pumpfun', 'pumpfun'],
            'jupiter': ['jupiter'],
            'raydium_cpmm': ['raydium_cpmm'],
            'clmm': ['clmm'],
            'orca': ['orca'],
            'unknown': self.dex_priorities  # Try all if unknown
        }
        
        # Get DEX list for detected platform
        dex_list = dex_mapping.get(detected_dex, self.dex_priorities)
        
        # Build strategy with executor functions
        if OFFICIAL_EXECUTORS_AVAILABLE:
            executor_map = {
                'direct_pumpfun': (execute_pumpfun_buy if action == 'buy' else execute_pumpfun_sell),
                'pumpfun': (execute_pumpfun_buy if action == 'buy' else execute_pumpfun_sell),
                'jupiter': (execute_jupiter_buy if action == 'buy' else execute_jupiter_sell),
                'raydium_cpmm': (execute_cpmm_buy if action == 'buy' else execute_cpmm_sell),
                'clmm': (execute_clmm_buy if action == 'buy' else execute_clmm_sell)
            }
        elif LEGACY_EXECUTORS_AVAILABLE:
            executor_map = {
                'direct_pumpfun': (try_pumpfun_buy if action == 'buy' else try_pumpfun_sell_all),
                'pumpfun': (try_pumpfun_buy if action == 'buy' else try_pumpfun_sell_all),
                'jupiter': (try_jupiter_buy if action == 'buy' else try_jupiter_sell_all),
                'raydium_cpmm': (try_cpmm_buy if action == 'buy' else try_cpmm_sell_all),
                'clmm': (try_clmm_hybrid_buy if action == 'buy' else try_clmm_hybrid_sell_all)
            }
        else:
            logger.error("❌ No executors available")
            return []
            
        # Build strategy list
        for dex_name in dex_list:
            if dex_name in executor_map:
                strategy.append((dex_name, executor_map[dex_name]))
                
        return strategy
        
    def _record_execution(self, trade_info: Dict[str, Any], result: Dict[str, Any], 
                         dex: str, action: str, execution_time: float):
        """Record execution for analysis and reporting"""
        execution_record = {
            'timestamp': datetime.now(timezone.utc),
            'action': action,
            'dex': dex,
            'token_mint': trade_info.get('token_mint'),
            'signature': result.get('signature'),
            'success': result.get('success', False),
            'execution_time': execution_time,
            'source_wallet': trade_info.get('wallet_address'),
            'detection_source': trade_info.get('detection_source', 'unknown')
        }
        
        self.execution_history.append(execution_record)
        
        # Keep only last 1000 executions
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
            
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'stats': dict(self.execution_stats),
            'recent_executions': self.execution_history[-10:],  # Last 10
            'total_executions': len(self.execution_history),
            'wallet': str(self.wallet_pubkey)[:8] + "...",
            'jito_enabled': self.fast_executor is not None
        }


class JitoTradeExecutorManager:
    """
    🎯 MANAGER CLASS - Simple interface for main.py integration
    This is what main.py will import and use
    """
    
    def __init__(self):
        self.executor = None
        self.is_initialized = False
        
    def initialize(self, wallet_keypair, rpc_client, jito_service=None, config=None):
        """Initialize the executor with configuration"""
        try:
            self.executor = JitoTradeExecutor(wallet_keypair, rpc_client, jito_service, config)
            self.is_initialized = True
            logger.info("✅ Jito Trade Executor Manager initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing executor manager: {e}")
            return False
            
    async def execute_trade(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade (buy or sell)"""
        if not self.is_initialized or not self.executor:
            return {
                'success': False,
                'error': 'Executor not initialized'
            }
            
        try:
            action = trade_info.get('action', '').lower()
            
            if action == 'buy':
                return await self.executor.execute_buy_trade(trade_info)
            elif action == 'sell':
                return await self.executor.execute_sell_trade(trade_info)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
                
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return {
                'success': False,
                'error': f'Execution error: {str(e)}'
            }
            
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if self.executor:
            return self.executor.get_execution_stats()
        else:
            return {'error': 'Executor not initialized'}


# Factory function for easy import
def create_jito_trade_executor(wallet_keypair, rpc_client, jito_service=None, config=None):
    """
    Factory function to create and initialize a Jito trade executor
    
    Usage in main.py:
        executor = create_jito_trade_executor(wallet, rpc_client, jito_service, config)
        result = await executor.execute_trade(trade_info)
    """
    manager = JitoTradeExecutorManager()
    
    if manager.initialize(wallet_keypair, rpc_client, jito_service, config):
        return manager
    else:
        return None
