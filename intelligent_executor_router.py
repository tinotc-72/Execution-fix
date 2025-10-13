#!/usr/bin/env python3
"""
🎯 INTELLIGENT EXECUTOR ROUTING
Enhanced execution system that uses DEX detection confidence to route to specific executors
instead of the "shotgun approach" of trying all executors in parallel.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from execution_coordinator import ExecutionCoordinator

logger = logging.getLogger(__name__)

class IntelligentExecutorRouter:
    """
    🧠 Smart executor routing based on DEX detection confidence
    Routes transactions to specific executors based on program ID detection
    """
    
    def __init__(self, execution_coordinator: ExecutionCoordinator):
        self.coordinator = execution_coordinator
        
        # Define exact executor mapping based on detected DEX
        self.dex_executor_mapping = {
            # High confidence program ID matches -> specific executor
            'pumpfun': ['direct_pumpfun', 'pumpfun'],
            'raydium_cpmm': ['cpmm'],
            'raydium_clmm': ['clmm'],
            'raydium_amm': ['raydium'],
            'jupiter': ['jupiter'],
            'orca': ['orca'],
            'phoenix': ['phoenix'],
            
            # Fallback mappings for text pattern matches
            'raydium': ['raydium', 'cpmm', 'clmm'],  # Generic Raydium -> try all variants
            'unknown': ['jupiter', 'raydium', 'cpmm'],  # Unknown -> safe defaults
        }
        
        # Executor priority based on detection confidence
        self.confidence_strategy = {
            'high': 'single_executor',      # Use only the detected executor
            'medium': 'focused_parallel',   # Use detected + 1-2 backup executors
            'low': 'conservative_parallel', # Use multiple safe executors
            'fallback': 'full_parallel'     # Use all available executors
        }
    
    async def execute_intelligent_buy(
        self, 
        token_mint: str, 
        source_wallet: str, 
        trade_info: Dict[str, Any]
    ) -> bool:
        """
        🎯 INTELLIGENT ROUTING: Route to specific executor based on detection confidence
        
        Args:
            token_mint: Token to buy
            source_wallet: Source wallet that made the original trade
            trade_info: Trade information including detection results
            
        Returns:
            bool: Success status
        """
        try:
            # Extract detection information from trade_info
            basic_analysis = trade_info.get('basic_analysis', {})
            detected_dex = basic_analysis.get('detected_dex', 'unknown')
            detection_confidence = basic_analysis.get('detection_confidence', 'low')
            detection_method = basic_analysis.get('detection_method', 'text_pattern')
            
            logger.info(f"🎯 INTELLIGENT ROUTING:")
            logger.info(f"   🏪 Detected DEX: {detected_dex}")
            logger.info(f"   📊 Confidence: {detection_confidence}")
            logger.info(f"   🔍 Method: {detection_method}")
            
            # Get execution strategy based on confidence
            strategy = self.confidence_strategy.get(detection_confidence, 'conservative_parallel')
            logger.info(f"   🧠 Strategy: {strategy}")
            
            # Route to appropriate execution method
            if strategy == 'single_executor':
                return await self._execute_single_executor(token_mint, source_wallet, detected_dex, trade_info)
            elif strategy == 'focused_parallel':
                return await self._execute_focused_parallel(token_mint, source_wallet, detected_dex, trade_info)
            elif strategy == 'conservative_parallel':
                return await self._execute_conservative_parallel(token_mint, source_wallet, detected_dex, trade_info)
            else:  # full_parallel
                return await self._execute_full_parallel(token_mint, source_wallet, trade_info)
                
        except Exception as e:
            logger.error(f"❌ Intelligent routing error: {e}")
            # Fallback to original execution method
            return await self.coordinator._execute_copy_buy(token_mint, source_wallet, detected_dex, trade_info)
    
    async def _execute_single_executor(
        self, 
        token_mint: str, 
        source_wallet: str, 
        detected_dex: str, 
        trade_info: Dict[str, Any]
    ) -> bool:
        """
        🎯 HIGH CONFIDENCE: Execute with single, specific executor
        """
        executors = self.dex_executor_mapping.get(detected_dex, ['jupiter'])
        primary_executor = executors[0]
        
        logger.info(f"🎯 HIGH CONFIDENCE EXECUTION: Using {primary_executor} executor only")
        
        try:
            # Get the specific executor function
            executor_func = self._get_executor_function(primary_executor)
            if not executor_func:
                logger.warning(f"⚠️ Executor {primary_executor} not available, falling back")
                return await self._execute_focused_parallel(token_mint, source_wallet, detected_dex, trade_info)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                executor_func(
                    self.coordinator.wallet,
                    token_mint,
                    self.coordinator.config.investment_amount_sol
                ),
                timeout=15.0  # Single executor gets more time
            )
            
            if result and result.get('success'):
                logger.info(f"✅ Single executor success: {primary_executor}")
                return True
            else:
                logger.warning(f"⚠️ Single executor failed: {primary_executor}")
                return False
                
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Single executor timeout: {primary_executor}")
            return False
        except Exception as e:
            logger.error(f"❌ Single executor error: {e}")
            return False
    
    async def _execute_focused_parallel(
        self, 
        token_mint: str, 
        source_wallet: str, 
        detected_dex: str, 
        trade_info: Dict[str, Any]
    ) -> bool:
        """
        🎯 MEDIUM CONFIDENCE: Execute with detected executor + 1-2 backups
        """
        executors = self.dex_executor_mapping.get(detected_dex, ['jupiter', 'raydium'])
        # Limit to max 3 executors for focused approach
        focused_executors = executors[:3]
        
        logger.info(f"🎯 FOCUSED PARALLEL EXECUTION: Using {len(focused_executors)} executors: {focused_executors}")
        
        return await self._parallel_execute_with_executors(token_mint, focused_executors)
    
    async def _execute_conservative_parallel(
        self, 
        token_mint: str, 
        source_wallet: str, 
        detected_dex: str, 
        trade_info: Dict[str, Any]
    ) -> bool:
        """
        🎯 LOW CONFIDENCE: Execute with conservative executor set
        """
        # Use safe, proven executors for low confidence
        conservative_executors = ['jupiter', 'raydium', 'cpmm']
        
        logger.info(f"🎯 CONSERVATIVE PARALLEL EXECUTION: Using {len(conservative_executors)} safe executors")
        
        return await self._parallel_execute_with_executors(token_mint, conservative_executors)
    
    async def _execute_full_parallel(
        self, 
        token_mint: str, 
        source_wallet: str, 
        trade_info: Dict[str, Any]
    ) -> bool:
        """
        🎯 FALLBACK: Execute with all available executors (original shotgun approach)
        If all fail, use universal cloner fallback.
        """
        logger.info(f"🎯 FULL PARALLEL EXECUTION: Using all available executors (fallback)")
        # Try all original executors
        result = await self.coordinator._execute_copy_buy(token_mint, source_wallet, None, trade_info)
        if result:
            return result
        # Universal fallback
        try:
            from official_executor_wrappers import try_universal_fallback
            logger.info("🛡️ Universal cloner fallback engaged!")
            fallback_result = await try_universal_fallback(self.coordinator.wallet, trade_info)
            if fallback_result.get('success'):
                logger.info("✅ Universal cloner fallback succeeded!")
                return True
            else:
                logger.error(f"❌ Universal cloner fallback failed: {fallback_result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"❌ Universal cloner fallback import error: {e}")
            return False
    
    async def _parallel_execute_with_executors(
        self, 
        token_mint: str, 
        executor_names: List[str],
        trade_info: Dict[str, Any] = None
    ) -> bool:
        """
        Execute with specific list of executors in parallel. If all fail, use universal cloner fallback.
        """
        try:
            # Create tasks for each executor
            tasks = []
            for executor_name in executor_names:
                executor_func = self._get_executor_function(executor_name)
                if executor_func:
                    task = asyncio.create_task(
                        self._try_executor_with_timeout(
                            executor_name, executor_func, token_mint
                        ),
                        name=f"exec_{executor_name}"
                    )
                    tasks.append(task)
            
            if not tasks:
                logger.error("❌ No valid executors found")
                return False
            
            # Wait for first success or all failures
            done, pending = await asyncio.wait(
                tasks, 
                return_when=asyncio.FIRST_COMPLETED,
                timeout=12.0
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Check results
            for task in done:
                try:
                    result = await task
                    if result:
                        logger.info(f"✅ Focused execution success")
                        return True
                except Exception as e:
                    logger.debug(f"Task error: {e}")
            
            logger.warning(f"⚠️ All focused executors failed. Trying universal cloner fallback...")
            # Universal fallback
            if trade_info:
                try:
                    from official_executor_wrappers import try_universal_fallback
                    fallback_result = await try_universal_fallback(self.coordinator.wallet, trade_info)
                    if fallback_result.get('success'):
                        logger.info("✅ Universal cloner fallback succeeded!")
                        return True
                    else:
                        logger.error(f"❌ Universal cloner fallback failed: {fallback_result.get('error')}")
                        return False
                except Exception as e:
                    logger.error(f"❌ Universal cloner fallback import error: {e}")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"❌ Parallel execution error: {e}")
            return False
    
    async def _try_executor_with_timeout(
        self, 
        executor_name: str, 
        executor_func, 
        token_mint: str
    ) -> bool:
        """
        Try single executor with timeout and error handling
        """
        try:
            result = await asyncio.wait_for(
                executor_func(
                    self.coordinator.wallet,
                    token_mint,
                    self.coordinator.config.investment_amount_sol
                ),
                timeout=10.0
            )
            
            if result and result.get('success'):
                logger.info(f"✅ {executor_name} executor success")
                return True
            else:
                logger.debug(f"⚠️ {executor_name} executor failed")
                return False
                
        except asyncio.TimeoutError:
            logger.debug(f"⏰ {executor_name} executor timeout")
            return False
        except Exception as e:
            logger.debug(f"❌ {executor_name} executor error: {e}")
            return False
    
    def _get_executor_function(self, executor_name: str):
        """
        Get the actual executor function for a given executor name
        """
        # Map executor names to actual functions
        executor_map = {
            'direct_pumpfun': self.coordinator._try_direct_pumpfun_buy,
            'pumpfun': self._get_pumpfun_executor,
            'jupiter': self._get_jupiter_executor,
            'raydium': self._get_raydium_executor,
            'cpmm': self._get_cpmm_executor,
            'clmm': self._get_clmm_executor,
            'orca': self._get_orca_executor,
            'phoenix': self._get_phoenix_executor,
        }
        
        return executor_map.get(executor_name)
    
    def _get_pumpfun_executor(self):
        """Get pump.fun executor function"""
        try:
            from official_executor_wrappers import try_pumpfun_buy
            return try_pumpfun_buy
        except ImportError:
            return None
    
    def _get_jupiter_executor(self):
        """Get Jupiter executor function"""
        try:
            from official_executor_wrappers import try_jupiter_buy
            return try_jupiter_buy
        except ImportError:
            return None
    
    def _get_raydium_executor(self):
        """Get Raydium executor function"""
        try:
            from official_executor_wrappers import try_raydium_buy
            return try_raydium_buy
        except ImportError:
            return None
    
    def _get_cpmm_executor(self):
        """Get CPMM executor function"""
        try:
            from official_executor_wrappers import try_cpmm_buy
            return try_cpmm_buy
        except ImportError:
            return None
    
    def _get_clmm_executor(self):
        """Get CLMM executor function"""
        try:
            from official_executor_wrappers import try_clmm_hybrid_buy
            return try_clmm_hybrid_buy
        except ImportError:
            return None
    
    def _get_orca_executor(self):
        """Get Orca executor function"""
        try:
            from official_executor_wrappers import try_orca_buy
            return try_orca_buy
        except ImportError:
            return None
    
    def _get_phoenix_executor(self):
        """Get Phoenix executor function"""
        try:
            from official_executor_wrappers import try_phoenix_buy
            return try_phoenix_buy
        except ImportError:
            return None


# Example integration with existing system
async def create_intelligent_router(execution_coordinator: ExecutionCoordinator) -> IntelligentExecutorRouter:
    """
    Factory function to create intelligent router
    """
    return IntelligentExecutorRouter(execution_coordinator)


# Example usage
if __name__ == "__main__":
    async def test_intelligent_routing():
        """Test the intelligent routing system"""
        
        # Mock trade info with high confidence detection
        high_confidence_trade = {
            'basic_analysis': {
                'detected_dex': 'raydium_cpmm',
                'detection_confidence': 'high',
                'detection_method': 'program_id'
            },
            'token_mint': 'test_token',
            'signature': 'test_sig'
        }
        
        # Mock trade info with low confidence detection
        low_confidence_trade = {
            'basic_analysis': {
                'detected_dex': 'unknown',
                'detection_confidence': 'low',
                'detection_method': 'text_pattern'
            },
            'token_mint': 'test_token',
            'signature': 'test_sig'
        }
        
        print("🧪 Testing Intelligent Executor Routing")
        print("=" * 50)
        
        print("📊 High Confidence Trade (Raydium CPMM):")
        print("   🎯 Expected: Single executor (CPMM)")
        print("   📊 Confidence: high")
        print("   🔍 Method: program_id")
        
        print("\n📊 Low Confidence Trade (Unknown):")
        print("   🎯 Expected: Conservative parallel (Jupiter, Raydium, CPMM)")
        print("   📊 Confidence: low")
        print("   🔍 Method: text_pattern")
        
        print("\n✅ Intelligent routing system ready!")
    
    asyncio.run(test_intelligent_routing())
