#!/usr/bin/env python3
"""
Pump.fun Copy Executor - MEV Enhanced
This file replaces the old pumpfun_CC_copy_executor.py with MEV-optimized trading
All functions maintain the same interface for seamless integration
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from solders.keypair import Keypair

# Import all MEV functionality
try:
    from mev_pumpfun_executor import (
        MEVPumpFunExecutor,
        MEVExecutorConfig,
        try_pumpfun_buy as mev_try_pumpfun_buy,
        try_pumpfun_sell_all as mev_try_pumpfun_sell_all,
        get_mev_executor
    )
    
    # Create wrapper functions that match the old interface exactly
    async def try_pumpfun_buy(mint_str: str, sol_amount: float, wallet: Keypair, **kwargs) -> Optional[str]:
        """MEV-optimized pump.fun buy - maintains old interface"""
        return await mev_try_pumpfun_buy(mint_str, sol_amount, wallet, **kwargs)
        
    async def try_pumpfun_sell_all(mint_str: str, wallet: Keypair, **kwargs) -> Optional[str]:
        """MEV-optimized pump.fun sell all - maintains old interface"""
        return await mev_try_pumpfun_sell_all(mint_str, wallet, **kwargs)
        
    # Legacy class for compatibility
    class PumpFunCopyExecutor(MEVPumpFunExecutor):
        """Legacy class name for backward compatibility"""
        
        def __init__(self, wallet: Keypair, **kwargs):
            # Get the original private key string from environment since that's what MEV bot expects
            from env_keys import EnvKeys
            env = EnvKeys()
            private_key = env.PHANTOM_PRIVATE_KEY
            super().__init__(private_key, **kwargs)
            
    print("🚀 MEV-Enhanced Pump.fun Executor loaded - Professional trading capabilities active!")
    
except ImportError as e:
    logging.error(f"❌ Failed to import MEV executor: {e}")
    
    # Fallback to prevent system breakage
    async def try_pumpfun_buy(mint_str: str, sol_amount: float, wallet: Keypair, **kwargs) -> Optional[str]:
        logging.error("❌ MEV executor not available - buy failed")
        return None
        
    async def try_pumpfun_sell_all(mint_str: str, wallet: Keypair, **kwargs) -> Optional[str]:
        logging.error("❌ MEV executor not available - sell failed")
        return None
        
    class PumpFunCopyExecutor:
        def __init__(self, *args, **kwargs):
            logging.error("❌ MEV executor not available")

# Export everything for compatibility
__all__ = [
    'try_pumpfun_buy',
    'try_pumpfun_sell_all', 
    'PumpFunCopyExecutor'
]
