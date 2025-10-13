#!/usr/bin/env python3
"""
Quick test to verify all imports are working
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    import asyncio
    import json
    import logging
    print("✅ Basic imports OK")
    
    # Test Solana imports
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    print("✅ Solana imports OK")
    
    # Test custom modules
    from config import WALLET
    print("✅ Config import OK")
    
    from env_keys import EnvKeys
    print("✅ EnvKeys import OK")
    
    from copy_trade_logger import get_copy_trade_logger
    print("✅ Copy trade logger import OK")
    
    # Test DEX executors
    from jupiter_copy_executor import try_jupiter_buy
    print("✅ Jupiter executor import OK")
    
    from pumpfun_CC_copy_executor import try_pumpfun_buy
    print("✅ Pumpfun executor import OK")
    
    from raydium_copy_executor import try_raydium_buy
    print("✅ Raydium executor import OK")
    
    from cpmm_copy_executor import try_cpmm_buy
    print("✅ CPMM executor import OK")
    
    from clmm_hybrid_copy_executor import try_clmm_hybrid_buy
    print("✅ CLMM hybrid executor import OK")
    
    from orca_copy_executor import try_orca_buy
    print("✅ Orca executor import OK")
    
    from phoenix_copy_executor import try_phoenix_buy
    print("✅ Phoenix executor import OK")
    
    # Test additional services
    from pool_discovery_service import PoolDiscoveryService
    print("✅ Pool discovery service import OK")
    
    from jito_service import JitoClient
    print("✅ Jito service import OK")
    
    from rate_limit_manager import rate_limit_manager
    print("✅ Rate limit manager import OK")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    print("✅ Ready to run the copy trading bot!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
