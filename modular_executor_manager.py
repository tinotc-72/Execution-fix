"""
🔗 MODULAR EXECUTOR MANAGER
Links your different executors as modules that main.py can call
Uses your existing proven executors with Jito integration
"""

import asyncio
import logging
import traceback
import time
from typing import Dict, Any, List, Callable, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass

# Import your existing executors
try:
    from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
    PUMPFUN_AVAILABLE = True
    print("✅ Modular Executor: Pump.fun available")
except ImportError:
    PUMPFUN_AVAILABLE = False
    print("❌ Modular Executor: Pump.fun not available")

try:
    from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
    JUPITER_AVAILABLE = True
    print("✅ Modular Executor: Jupiter available")
except ImportError:
    JUPITER_AVAILABLE = False
    print("❌ Modular Executor: Jupiter not available")

try:
    from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
    RAYDIUM_AVAILABLE = True
    print("✅ Modular Executor: Raydium available")
except ImportError:
    RAYDIUM_AVAILABLE = False
    print("❌ Modular Executor: Raydium not available")

try:
    from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
    CPMM_AVAILABLE = True
    print("✅ Modular Executor: CPMM available")
except ImportError:
    CPMM_AVAILABLE = False
    print("❌ Modular Executor: CPMM not available")

try:
    from clmm_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
    CLMM_AVAILABLE = True
    print("✅ Modular Executor: CLMM available")
except ImportError:
    CLMM_AVAILABLE = False
    print("❌ Modular Executor: CLMM not available")

try:
    from orca_copy_executor import try_orca_buy, try_orca_sell_all
    ORCA_AVAILABLE = True
    print("✅ Modular Executor: Orca available")
except ImportError:
    ORCA_AVAILABLE = False
    print("❌ Modular Executor: Orca not available")

try:
    from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all
    PHOENIX_AVAILABLE = True
    print("✅ Modular Executor: Phoenix available")
except ImportError:
    PHOENIX_AVAILABLE = False
    print("❌ Modular Executor: Phoenix not available")

# Import Jito integration
try:
    from fast_executor import FastExecutor
    FAST_EXECUTOR_AVAILABLE = True
    print("✅ Modular Executor: FastExecutor with Jito available")
except ImportError:
    FAST_EXECUTOR_AVAILABLE = False
    print("❌ Modular Executor: FastExecutor not available")

logger = logging.getLogger(__name__)

@dataclass
class ExecutorResult:
    """Standardized result from any executor"""
    success: bool
    signature: Optional[str] = None
    error: Optional[str] = None
    dex: Optional[str] = None
    execution_time: float = 0.0
    method: str = "unknown"
    token_mint: Optional[str] = None
    amount: float = 0.0

class ModularExecutorManager:
    """
    🔗 MODULAR EXECUTOR MANAGER
    
    Manages all your different executors as separate modules
    Provides unified interface for main.py to call
    Handles Jito integration for maximum speed
    """
    
    def __init__(self, wallet_keypair, rpc_client, jito_service=None, config=None):
        """
        Initialize modular executor manager
        
        Args:
            wallet_keypair: Your wallet keypair
            rpc_client: RPC client
            jito_service: Jito service for MEV protection
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
                logger.info("✅ FastExecutor initialized for Jito execution")
            except Exception as e:
                logger.error(f"❌ Failed to initialize FastExecutor: {e}")
        
        # Define executor modules with priorities
        self.executor_modules = self._initialize_executor_modules()
        
        # Execution statistics
        self.stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'executor_stats': {},
            'execution_history': []
        }
        
        logger.info(f"🔗 Modular Executor Manager initialized")
        logger.info(f"   💎 Wallet: {str(self.wallet_pubkey)[:8]}...")
        logger.info(f"   ⚡ Jito Service: {'✅ Available' if jito_service else '❌ Not available'}")
        logger.info(f"   🚀 FastExecutor: {'✅ Available' if self.fast_executor else '❌ Not available'}")
        logger.info(f"   🏭 Available executors: {len(self.executor_modules)}")
        
        for name, module in self.executor_modules.items():
            enabled = self.config['enable_dexes'].get(name, False)
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            logger.info(f"      {status} {name}: {module['priority']}")
    
    def _default_config(self):
        """Default configuration"""
        return {
            'investment_amount_sol': 0.001,
            'slippage_tolerance': 0.15,
            'slippage_bps': 1500,
            'max_retries': 2,
            'execution_timeout': 15.0,
            'enable_dexes': {
                'direct_pumpfun': True,
                'pumpfun': True,
                'jupiter': True,
                'raydium': True,
                'cpmm': True,
                'clmm': True,
                'orca': True,
                'phoenix': True
            }
        }
    
    def _initialize_executor_modules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available executor modules"""
        modules = {}
        
        # Direct Pump.fun (highest priority for new meme coins)
        modules['direct_pumpfun'] = {
            'buy_func': self._direct_pumpfun_buy,
            'sell_func': self._direct_pumpfun_sell,
            'priority': 1,
            'description': 'Direct Pump.fun execution',
            'available': True,  # Always available as it uses FastExecutor
            'use_jito': True
        }
        
        # Pump.fun
        if PUMPFUN_AVAILABLE:
            modules['pumpfun'] = {
                'buy_func': try_pumpfun_buy,
                'sell_func': try_pumpfun_sell_all,
                'priority': 2,
                'description': 'Pump.fun copy executor',
                'available': True,
                'use_jito': False
            }
        
        # Jupiter
        if JUPITER_AVAILABLE:
            modules['jupiter'] = {
                'buy_func': try_jupiter_buy,
                'sell_func': try_jupiter_sell_all,
                'priority': 3,
                'description': 'Jupiter aggregator',
                'available': True,
                'use_jito': False
            }
        
        # Raydium
        if RAYDIUM_AVAILABLE:
            modules['raydium'] = {
                'buy_func': try_raydium_buy,
                'sell_func': try_raydium_sell_all,
                'priority': 4,
                'description': 'Raydium AMM',
                'available': True,
                'use_jito': False
            }
        
        # CPMM
        if CPMM_AVAILABLE:
            modules['cpmm'] = {
                'buy_func': try_cpmm_buy,
                'sell_func': try_cpmm_sell_all,
                'priority': 5,
                'description': 'Raydium CPMM',
                'available': True,
                'use_jito': False
            }
        
        # CLMM
        if CLMM_AVAILABLE:
            modules['clmm'] = {
                'buy_func': try_clmm_hybrid_buy,
                'sell_func': try_clmm_hybrid_sell_all,
                'priority': 6,
                'description': 'Concentrated Liquidity',
                'available': True,
                'use_jito': False
            }
        
        # Orca
        if ORCA_AVAILABLE:
            modules['orca'] = {
                'buy_func': try_orca_buy,
                'sell_func': try_orca_sell_all,
                'priority': 7,
                'description': 'Orca AMM',
                'available': True,
                'use_jito': False
            }
        
        # Phoenix
        if PHOENIX_AVAILABLE:
            modules['phoenix'] = {
                'buy_func': try_phoenix_buy,
                'sell_func': try_phoenix_sell_all,
                'priority': 8,
                'description': 'Phoenix orderbook',
                'available': True,
                'use_jito': False
            }
        
        return modules
    
    async def execute_buy(self, token_mint: str, amount_sol: float = None, 
                         preferred_dex: str = None, **kwargs) -> ExecutorResult:
        """
        Execute a buy trade using modular executors
        
        Args:
            token_mint: Token to buy
            amount_sol: Amount in SOL to spend
            preferred_dex: Preferred DEX to try first
            **kwargs: Additional parameters
            
        Returns:
            ExecutorResult with execution details
        """
        start_time = time.time()
        amount_sol = amount_sol or self.config['investment_amount_sol']
        
        logger.info(f"🚀 MODULAR BUY EXECUTION")
        logger.info(f"   💎 Token: {token_mint[:8]}...")
        logger.info(f"   💰 Amount: {amount_sol} SOL")
        logger.info(f"   🎯 Preferred DEX: {preferred_dex or 'Auto-select'}")
        
        # Get execution strategy
        execution_order = self._get_execution_order('buy', preferred_dex)
        
        for attempt, (dex_name, module) in enumerate(execution_order, 1):
            if not self.config['enable_dexes'].get(dex_name, False):
                logger.debug(f"⏭️ Skipping disabled DEX: {dex_name}")
                continue
            
            try:
                logger.info(f"🎯 Attempt {attempt}: {dex_name.upper()} BUY")
                
                # Execute using the module
                if module['use_jito'] and self.fast_executor:
                    # Use Jito execution for maximum speed
                    result = await self._execute_with_jito(
                        'buy', token_mint, amount_sol, dex_name
                    )
                else:
                    # Use standard executor
                    result = await self._execute_with_standard_executor(
                        module['buy_func'], token_mint, amount_sol, 'buy', dex_name
                    )
                
                execution_time = time.time() - start_time
                
                if result.success:
                    logger.info(f"✅ BUY SUCCESS via {dex_name.upper()}")
                    logger.info(f"   📝 Signature: {result.signature[:12] if result.signature else 'None'}...")
                    logger.info(f"   ⚡ Execution time: {execution_time:.2f}s")
                    
                    # Update statistics
                    self._update_stats('buy', dex_name, True, execution_time)
                    
                    result.execution_time = execution_time
                    result.dex = dex_name
                    return result
                else:
                    logger.warning(f"⚠️ {dex_name.upper()} BUY failed: {result.error}")
                    self._update_stats('buy', dex_name, False, execution_time)
                    
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {dex_name.upper()} BUY exception: {e}")
                self._update_stats('buy', dex_name, False, execution_time)
                continue
        
        # All attempts failed
        total_time = time.time() - start_time
        logger.error(f"❌ ALL BUY ATTEMPTS FAILED for {token_mint[:8]}... after {total_time:.2f}s")
        
        return ExecutorResult(
            success=False,
            error="All buy attempts failed",
            execution_time=total_time,
            token_mint=token_mint
        )
    
    async def execute_sell(self, token_mint: str, percentage: float = 100.0,
                          preferred_dex: str = None, **kwargs) -> ExecutorResult:
        """
        Execute a sell trade using modular executors
        
        Args:
            token_mint: Token to sell
            percentage: Percentage to sell (default 100%)
            preferred_dex: Preferred DEX to try first
            **kwargs: Additional parameters
            
        Returns:
            ExecutorResult with execution details
        """
        start_time = time.time()
        
        logger.info(f"🚀 MODULAR SELL EXECUTION")
        logger.info(f"   💎 Token: {token_mint[:8]}...")
        logger.info(f"   📊 Percentage: {percentage}%")
        logger.info(f"   🎯 Preferred DEX: {preferred_dex or 'Auto-select'}")
        
        # Get execution strategy
        execution_order = self._get_execution_order('sell', preferred_dex)
        
        for attempt, (dex_name, module) in enumerate(execution_order, 1):
            if not self.config['enable_dexes'].get(dex_name, False):
                logger.debug(f"⏭️ Skipping disabled DEX: {dex_name}")
                continue
            
            try:
                logger.info(f"🎯 Attempt {attempt}: {dex_name.upper()} SELL")
                
                # Execute using the module
                if module['use_jito'] and self.fast_executor:
                    # Use Jito execution for maximum speed
                    result = await self._execute_with_jito(
                        'sell', token_mint, percentage, dex_name
                    )
                else:
                    # Use standard executor
                    result = await self._execute_with_standard_executor(
                        module['sell_func'], token_mint, percentage, 'sell', dex_name
                    )
                
                execution_time = time.time() - start_time
                
                if result.success:
                    logger.info(f"✅ SELL SUCCESS via {dex_name.upper()}")
                    logger.info(f"   📝 Signature: {result.signature[:12] if result.signature else 'None'}...")
                    logger.info(f"   ⚡ Execution time: {execution_time:.2f}s")
                    
                    # Update statistics
                    self._update_stats('sell', dex_name, True, execution_time)
                    
                    result.execution_time = execution_time
                    result.dex = dex_name
                    return result
                else:
                    logger.warning(f"⚠️ {dex_name.upper()} SELL failed: {result.error}")
                    self._update_stats('sell', dex_name, False, execution_time)
                    
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ {dex_name.upper()} SELL exception: {e}")
                self._update_stats('sell', dex_name, False, execution_time)
                continue
        
        # All attempts failed
        total_time = time.time() - start_time
        logger.error(f"❌ ALL SELL ATTEMPTS FAILED for {token_mint[:8]}... after {total_time:.2f}s")
        
        return ExecutorResult(
            success=False,
            error="All sell attempts failed",
            execution_time=total_time,
            token_mint=token_mint
        )
    
    def _get_execution_order(self, action: str, preferred_dex: str = None) -> List[Tuple[str, Dict[str, Any]]]:
        """Get execution order based on priorities and preferences"""
        # Filter enabled executors
        available_executors = [
            (name, module) for name, module in self.executor_modules.items()
            if self.config['enable_dexes'].get(name, False) and module['available']
        ]
        
        # If preferred DEX specified, try it first
        if preferred_dex and preferred_dex in self.executor_modules:
            if self.config['enable_dexes'].get(preferred_dex, False):
                # Move preferred DEX to front
                preferred_module = self.executor_modules[preferred_dex]
                others = [(name, module) for name, module in available_executors if name != preferred_dex]
                return [(preferred_dex, preferred_module)] + others
        
        # Sort by priority (lower number = higher priority)
        available_executors.sort(key=lambda x: x[1]['priority'])
        
        return available_executors
    
    async def _execute_with_jito(self, action: str, token_mint: str, amount: float, dex_name: str) -> ExecutorResult:
        """Execute using FastExecutor with Jito integration"""
        try:
            logger.info(f"⚡ Using Jito execution for {action.upper()}")
            
            if action == 'buy':
                signature = await self.fast_executor.execute_buy_trade(
                    token_mint=token_mint,
                    amount_sol=amount,
                    slippage_bps=self.config['slippage_bps']
                )
            else:  # sell
                signature = await self.fast_executor.execute_sell_trade(
                    token_mint=token_mint,
                    sell_percentage=amount,
                    slippage_bps=self.config['slippage_bps']
                )
            
            if signature:
                return ExecutorResult(
                    success=True,
                    signature=signature,
                    method='jito_execution',
                    token_mint=token_mint,
                    amount=amount
                )
            else:
                return ExecutorResult(
                    success=False,
                    error='Jito execution returned no signature',
                    method='jito_execution'
                )
                
        except Exception as e:
            logger.error(f"❌ Jito execution error: {e}")
            return ExecutorResult(
                success=False,
                error=f'Jito execution error: {str(e)}',
                method='jito_execution'
            )
    
    async def _execute_with_standard_executor(self, executor_func: Callable, token_mint: str, 
                                            amount: float, action: str, dex_name: str) -> ExecutorResult:
        """Execute using standard executor function"""
        try:
            logger.debug(f"🏪 Using standard {dex_name} executor for {action.upper()}")
            
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
            
            # Standardize result format
            if isinstance(result, dict):
                return ExecutorResult(
                    success=result.get('success', False),
                    signature=result.get('signature'),
                    error=result.get('error'),
                    method=f'{dex_name}_executor',
                    token_mint=token_mint,
                    amount=amount
                )
            else:
                # Handle different result formats
                return ExecutorResult(
                    success=bool(result),
                    signature=str(result) if result else None,
                    method=f'{dex_name}_executor',
                    token_mint=token_mint,
                    amount=amount
                )
                
        except Exception as e:
            logger.error(f"❌ Standard executor error: {e}")
            return ExecutorResult(
                success=False,
                error=f'Standard executor error: {str(e)}',
                method=f'{dex_name}_executor'
            )
    
    async def _direct_pumpfun_buy(self, wallet_keypair, token_mint: str, amount_sol: float, **kwargs) -> ExecutorResult:
        """Direct Pump.fun buy using Jito"""
        if self.fast_executor:
            return await self._execute_with_jito('buy', token_mint, amount_sol, 'direct_pumpfun')
        else:
            return ExecutorResult(
                success=False,
                error='FastExecutor not available for direct Pump.fun',
                method='direct_pumpfun'
            )
    
    async def _direct_pumpfun_sell(self, wallet_keypair, token_mint: str, percentage: float = 100.0, **kwargs) -> ExecutorResult:
        """Direct Pump.fun sell using Jito"""
        if self.fast_executor:
            return await self._execute_with_jito('sell', token_mint, percentage, 'direct_pumpfun')
        else:
            return ExecutorResult(
                success=False,
                error='FastExecutor not available for direct Pump.fun',
                method='direct_pumpfun'
            )
    
    def _update_stats(self, action: str, dex: str, success: bool, execution_time: float):
        """Update execution statistics"""
        self.stats['total_executions'] += 1
        
        if success:
            self.stats['successful_executions'] += 1
        else:
            self.stats['failed_executions'] += 1
        
        # DEX-specific stats
        if dex not in self.stats['executor_stats']:
            self.stats['executor_stats'][dex] = {
                'total': 0, 'success': 0, 'failed': 0,
                'avg_execution_time': 0.0, 'total_time': 0.0
            }
        
        dex_stats = self.stats['executor_stats'][dex]
        dex_stats['total'] += 1
        dex_stats['total_time'] += execution_time
        dex_stats['avg_execution_time'] = dex_stats['total_time'] / dex_stats['total']
        
        if success:
            dex_stats['success'] += 1
        else:
            dex_stats['failed'] += 1
        
        # Add to history (keep last 100)
        self.stats['execution_history'].append({
            'timestamp': datetime.now(timezone.utc),
            'action': action,
            'dex': dex,
            'success': success,
            'execution_time': execution_time
        })
        
        if len(self.stats['execution_history']) > 100:
            self.stats['execution_history'] = self.stats['execution_history'][-100:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'manager_stats': self.stats,
            'available_executors': {
                name: {
                    'description': module['description'],
                    'priority': module['priority'],
                    'enabled': self.config['enable_dexes'].get(name, False),
                    'available': module['available'],
                    'use_jito': module['use_jito']
                }
                for name, module in self.executor_modules.items()
            },
            'wallet': str(self.wallet_pubkey)[:8] + "...",
            'jito_enabled': self.fast_executor is not None
        }
    
    def get_available_executors(self) -> List[str]:
        """Get list of available executor names"""
        return [name for name, module in self.executor_modules.items() if module['available']]
    
    def enable_executor(self, executor_name: str, enabled: bool = True):
        """Enable or disable a specific executor"""
        if executor_name in self.executor_modules:
            self.config['enable_dexes'][executor_name] = enabled
            logger.info(f"{'✅ Enabled' if enabled else '❌ Disabled'} executor: {executor_name}")
        else:
            logger.warning(f"⚠️ Unknown executor: {executor_name}")


# Factory function for easy integration with main.py
def create_modular_executor_manager(wallet_keypair, rpc_client, jito_service=None, config=None):
    """
    Factory function to create modular executor manager
    
    This is what main.py will import and use:
    
    Usage in main.py:
        from modular_executor_manager import create_modular_executor_manager
        
        self.executor_manager = create_modular_executor_manager(
            wallet_keypair=self.wallet,
            rpc_client=self.rpc_client,
            jito_service=self.jito_service,
            config=self.config.__dict__
        )
        
        # Execute buy
        result = await self.executor_manager.execute_buy(token_mint, amount_sol)
        
        # Execute sell
        result = await self.executor_manager.execute_sell(token_mint, percentage)
    """
    try:
        manager = ModularExecutorManager(wallet_keypair, rpc_client, jito_service, config)
        logger.info("✅ Modular Executor Manager created successfully")
        return manager
    except Exception as e:
        logger.error(f"❌ Error creating modular executor manager: {e}")
        logger.error(traceback.format_exc())
        return None


def get_executor_status():
    """Check status of all executor modules"""
    return {
        'pumpfun_available': PUMPFUN_AVAILABLE,
        'jupiter_available': JUPITER_AVAILABLE,
        'raydium_available': RAYDIUM_AVAILABLE,
        'cpmm_available': CPMM_AVAILABLE,
        'clmm_available': CLMM_AVAILABLE,
        'orca_available': ORCA_AVAILABLE,
        'phoenix_available': PHOENIX_AVAILABLE,
        'fast_executor_available': FAST_EXECUTOR_AVAILABLE,
        'total_available': sum([
            PUMPFUN_AVAILABLE, JUPITER_AVAILABLE, RAYDIUM_AVAILABLE,
            CPMM_AVAILABLE, CLMM_AVAILABLE, ORCA_AVAILABLE, PHOENIX_AVAILABLE
        ])
    }
