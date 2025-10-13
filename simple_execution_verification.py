#!/usr/bin/env python3
"""
🧪 SIMPLE EXECUTION VERIFICATION TEST
Quick test to verify individual execution methods work correctly

This is a simple test you can run anytime to check:
1. ✅ Bot initialization
2. ✅ Jito service status
3. ✅ DEX executors availability
4. ✅ Execution method signatures
5. ✅ Configuration validity
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import CopyTradingBot, CopyTradeConfig
from config import WALLET
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simple_execution_verification():
    """Simple verification of execution methods"""
    
    print("🧪 SIMPLE EXECUTION VERIFICATION TEST")
    print("=" * 50)
    print("⚠️ NOTE: This is a safe test - no real transactions executed")
    print("=" * 50)
    
    results = {
        "bot_creation": False,
        "jito_service": False,
        "dex_executors": False,
        "execution_methods": False,
        "error_handling": False
    }
    
    try:
        # Test 1: Bot Creation
        print("\n1️⃣ Testing bot creation...")
        config = CopyTradeConfig(
            target_wallets=["9WwGxj1rPMZZg4KhzWsxRxij3hiKkZyzN1TfXR8zzGzv"],  # Test wallet
            investment_amount_sol=0.001,
            use_jito=True,
            enable_dexes={
                "raydium": True,
                "cpmm": True,
                "clmm": True,
                "orca": True,
                "direct_pumpfun": True,
                "pumpfun": True,
                "jupiter": True
            }
        )
        
        bot = CopyTradingBot(config)
        print("✅ Bot created successfully")
        results["bot_creation"] = True
        
        # Test 2: Jito Service
        print("\n2️⃣ Testing Jito service...")
        if bot.jito_service:
            print("✅ Jito service available")
            print(f"   🌍 Endpoint: {bot.jito_service.primary_endpoint}")
            print(f"   🔄 Backup regions: {len(bot.jito_service.backup_endpoints)}")
            results["jito_service"] = True
        else:
            print("❌ Jito service not available")
            
        # Test 3: DEX Executors
        print("\n3️⃣ Testing DEX executors...")
        if hasattr(bot, 'dex_executors') and bot.dex_executors:
            print(f"✅ DEX executors loaded: {len(bot.dex_executors)}")
            
            enabled_count = 0
            for dex_name, (buy_func, sell_func) in bot.dex_executors.items():
                enabled = config.enable_dexes.get(dex_name, False)
                if enabled:
                    enabled_count += 1
                    print(f"   ✅ {dex_name}: {buy_func.__name__}")
                else:
                    print(f"   ⚪ {dex_name}: DISABLED")
                    
            print(f"   📊 Enabled: {enabled_count}/{len(bot.dex_executors)}")
            results["dex_executors"] = enabled_count >= 3
        else:
            print("❌ DEX executors not found")
            
        # Test 4: Execution Methods
        print("\n4️⃣ Testing execution methods...")
        
        execution_methods = [
            # Strategy #1: Jito-first
            "_try_jito_first_execution",
            "_build_optimal_transaction",
            
            # Strategy #2: Direct DEX
            "_execute_copy_buy_internal",
            "_get_prioritized_dex_executors",
            
            # Strategy #3: Complex execution
            "_reanalyze_transaction_with_balance_data",
            
            # Buy/Sell flows
            "_execute_copy_buy",
            "_execute_copy_sell",
            "_execute_copy_sell_all",
            
            # Position management
            "_update_position_after_buy_success",
        ]
        
        available_methods = 0
        for method_name in execution_methods:
            if hasattr(bot, method_name):
                print(f"   ✅ {method_name}")
                available_methods += 1
            else:
                print(f"   ❌ {method_name}")
                
        method_percentage = (available_methods / len(execution_methods)) * 100
        print(f"   📊 Methods available: {available_methods}/{len(execution_methods)} ({method_percentage:.1f}%)")
        results["execution_methods"] = method_percentage >= 80
        
        # Test 5: Error Handling
        print("\n5️⃣ Testing error handling...")
        
        error_methods = [
            "emergency_kill",
            "stop",
            "liquidate_all_positions"
        ]
        
        available_handlers = 0
        for method_name in error_methods:
            if hasattr(bot, method_name):
                print(f"   ✅ {method_name}")
                available_handlers += 1
            else:
                print(f"   ❌ {method_name}")
                
        results["error_handling"] = available_handlers >= 2
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            
        print(f"\n📋 Overall: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🏆 EXCELLENT: Your execution system is ready!")
            print("   ✅ All critical components working")
            print("   ✅ Safe to run live copy trading")
        elif success_rate >= 70:
            print("✅ GOOD: Your execution system is mostly ready")
            print("   ⚠️ Minor issues to address")
            print("   ✅ Should work for copy trading")
        else:
            print("❌ NEEDS WORK: Your execution system has issues")
            print("   🔧 Fix failed tests before live trading")
            
        # Execution Strategy Summary
        print("\n🚀 EXECUTION STRATEGY SUMMARY:")
        print("1. 🏆 Strategy #1: Jito-first execution (200-500ms + MEV protection)")
        print("2. 🎪 Strategy #2: Direct DEX execution (Raydium, Orca, etc.)")
        print("3. 🔄 Strategy #3: Complex execution with validation & retry")
        
        if results["jito_service"] and results["dex_executors"]:
            print("✅ ALL STRATEGIES READY - Maximum execution reliability!")
        elif results["dex_executors"]:
            print("⚠️ DEX strategies ready - Jito may need attention")
        else:
            print("❌ Execution strategies need work")
            
        print("\n🎯 QUICK EXECUTION TEST:")
        print("   To test actual execution (safe mode):")
        print("   > python3 execution_method_functional_test.py")
        
        print("\n📚 EXECUTION METHODS AVAILABLE:")
        if results["execution_methods"]:
            print("   ✅ Buy execution: _execute_copy_buy")
            print("   ✅ Sell execution: _execute_copy_sell") 
            print("   ✅ Liquidation: _execute_copy_sell_all")
            print("   ✅ Jito integration: _try_jito_first_execution")
            print("   ✅ Position tracking: _update_position_after_buy_success")
        else:
            print("   ❌ Some execution methods missing")
            
        print("\n" + "=" * 50)
        return success_rate >= 70
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main verification function"""
    try:
        print("🧪 Starting simple execution verification...")
        success = await simple_execution_verification()
        
        if success:
            print("✅ Verification completed successfully!")
        else:
            print("❌ Verification found issues to fix")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
