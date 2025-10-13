#!/usr/bin/env python3
"""
Quick Executor Status Check
==========================
Fast check to verify all executors are properly configured and functional.
"""

import asyncio
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_executor_check():
    """Quick check of all executor functionality"""
    
    logger.info("🔍 QUICK EXECUTOR STATUS CHECK")
    logger.info("="*50)
    
    # All configured executors from main.py
    configured_executors = {
        "direct_pumpfun": ("Direct Pump.fun", "High priority for new tokens"),
        "pumpfun": ("Jupiter-based Pump.fun", "Standard Pump.fun routing"),
        "jupiter": ("Jupiter Aggregator", "Most comprehensive routing"),
        "raydium": ("Raydium DEX", "Raydium V4 AMM"),
        "cpmm": ("Raydium CPMM", "Raydium Concentrated Pool"),
        "clmm": ("CLMM Hybrid", "Concentrated liquidity"),
        "orca": ("Orca DEX", "Orca Whirlpool"),
        "phoenix": ("Phoenix DEX", "Phoenix CLOB")
    }
    
    # Test each executor
    test_results = {}
    
    for executor_name, (display_name, description) in configured_executors.items():
        logger.info(f"\n🧪 Testing {display_name}...")
        
        try:
            if executor_name == "direct_pumpfun":
                # Test direct_pumpfun
                from direct_pumpfun import try_direct_pumpfun_buy, try_direct_pumpfun_sell
                buy_func = try_direct_pumpfun_buy
                sell_func = try_direct_pumpfun_sell
                
            elif executor_name == "pumpfun":
                from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
                buy_func = try_pumpfun_buy
                sell_func = try_pumpfun_sell_all
                
            elif executor_name == "jupiter":
                from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
                buy_func = try_jupiter_buy
                sell_func = try_jupiter_sell_all
                
            elif executor_name == "raydium":
                from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
                buy_func = try_raydium_buy
                sell_func = try_raydium_sell_all
                
            elif executor_name == "cpmm":
                from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
                buy_func = try_cpmm_buy
                sell_func = try_cpmm_sell_all
                
            elif executor_name == "clmm":
                # Map to clmm_hybrid
                from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
                buy_func = try_clmm_hybrid_buy
                sell_func = try_clmm_hybrid_sell_all
                
            elif executor_name == "orca":
                from orca_copy_executor import try_orca_buy, try_orca_sell_all
                buy_func = try_orca_buy
                sell_func = try_orca_sell_all
                
            elif executor_name == "phoenix":
                from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all
                buy_func = try_phoenix_buy
                sell_func = try_phoenix_sell_all
                
            else:
                raise ImportError(f"Unknown executor: {executor_name}")
            
            # Verify functions are callable
            if callable(buy_func) and callable(sell_func):
                test_results[executor_name] = {
                    "status": "✅ FUNCTIONAL",
                    "display_name": display_name,
                    "description": description,
                    "buy_function": buy_func.__name__,
                    "sell_function": sell_func.__name__
                }
                logger.info(f"  ✅ {display_name}: FUNCTIONAL")
                logger.info(f"     Buy: {buy_func.__name__}")
                logger.info(f"     Sell: {sell_func.__name__}")
            else:
                test_results[executor_name] = {
                    "status": "❌ NOT_CALLABLE",
                    "display_name": display_name,
                    "error": "Functions not callable"
                }
                logger.error(f"  ❌ {display_name}: Functions not callable")
                
        except ImportError as e:
            test_results[executor_name] = {
                "status": "❌ IMPORT_FAILED",
                "display_name": display_name,
                "error": str(e)
            }
            logger.error(f"  ❌ {display_name}: Import failed - {e}")
            
        except Exception as e:
            test_results[executor_name] = {
                "status": "❌ ERROR",
                "display_name": display_name,
                "error": str(e)
            }
            logger.error(f"  ❌ {display_name}: Error - {e}")
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 EXECUTOR STATUS SUMMARY")
    logger.info("="*50)
    
    working = [name for name, result in test_results.items() if "FUNCTIONAL" in result["status"]]
    broken = [name for name, result in test_results.items() if "FUNCTIONAL" not in result["status"]]
    
    logger.info(f"✅ WORKING EXECUTORS ({len(working)}/8):")
    for executor_name in working:
        result = test_results[executor_name]
        logger.info(f"   • {result['display_name']} - {result['description']}")
    
    if broken:
        logger.info(f"\n❌ BROKEN EXECUTORS ({len(broken)}/8):")
        for executor_name in broken:
            result = test_results[executor_name]
            logger.error(f"   • {result['display_name']} - {result.get('error', 'Unknown error')}")
    
    # Final assessment
    logger.info(f"\n🎯 SYSTEM STATUS:")
    if len(working) >= 6:
        logger.info(f"   🟢 EXCELLENT - {len(working)} working executors")
        logger.info(f"   💪 Multiple redundancy layers available")
    elif len(working) >= 4:
        logger.info(f"   🟡 GOOD - {len(working)} working executors") 
        logger.info(f"   ✅ Sufficient redundancy for copy trading")
    elif len(working) >= 2:
        logger.info(f"   🟠 MINIMAL - {len(working)} working executors")
        logger.info(f"   ⚠️  Limited redundancy")
    else:
        logger.info(f"   🔴 CRITICAL - Only {len(working)} working executor(s)")
        logger.info(f"   ❌ Insufficient for reliable copy trading")
    
    # Test wallet integration
    logger.info(f"\n💼 WALLET INTEGRATION TEST:")
    try:
        from config import WALLET
        logger.info(f"   ✅ Wallet loaded: {WALLET.pubkey()}")
        logger.info(f"   🔐 Ready for trading operations")
    except Exception as e:
        logger.error(f"   ❌ Wallet integration failed: {e}")
    
    logger.info("="*50)
    
    return test_results

if __name__ == "__main__":
    asyncio.run(quick_executor_check())
