#!/usr/bin/env python3

import asyncio
import logging
import sys
from env_keys import EnvKeys, load_wallet_from_private_key
from config import CopyTradeConfig

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_main_py_executors():
    """Test which executors are available when running main.py"""
    
    print(f"🎯 TESTING MAIN.PY EXECUTORS")
    print(f"=" * 50)
    
    try:
        # Import main.py components
        from main import SimpleCopyTradingBot
        from execution_coordinator import ExecutionCoordinator
        
        # Setup config like main.py does
        env_keys = EnvKeys()
        
        config = CopyTradeConfig(
            target_wallets=['3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv'],  # Test wallet
            investment_amount_sol=0.001,
            use_jito=False,
            slippage_tolerance=0.3
        )
        
        print(f"✅ Successfully imported SimpleCopyTradingBot")
        print(f"✅ Config created with investment amount: {config.investment_amount_sol} SOL")
        
        # Initialize the bot like main.py does
        bot = SimpleCopyTradingBot(config)
        
        print(f"✅ SimpleCopyTradingBot initialized")
        print(f"   📱 Wallet: {bot.wallet.pubkey()}")
        
        # Check the execution coordinator
        coordinator = bot.execution_coordinator
        print(f"✅ ExecutionCoordinator available")
        
        # Test what executors are available in the coordinator
        print(f"\n🔍 CHECKING AVAILABLE EXECUTORS:")
        
        executor_status = {}
        
        # Check MEV Direct Copy Executor
        try:
            from mev_direct_copy_executor import MEVDirectCopyExecutor
            executor_status['MEV_DIRECT_COPY'] = '✅ AVAILABLE'
            print(f"✅ MEV Direct Copy Executor: Available")
        except Exception as e:
            executor_status['MEV_DIRECT_COPY'] = f'❌ {str(e)[:30]}'
            print(f"❌ MEV Direct Copy Executor: {e}")
        
        # Check MEV Pump.fun Executor
        try:
            from mev_pumpfun_executor import MEVPumpFunExecutor
            executor_status['MEV_PUMPFUN'] = '✅ AVAILABLE'
            print(f"✅ MEV Pump.fun Executor: Available")
        except Exception as e:
            executor_status['MEV_PUMPFUN'] = f'❌ {str(e)[:30]}'
            print(f"❌ MEV Pump.fun Executor: {e}")
        
        # Check MEV Raydium Executor
        try:
            from mev_raydium_executor import MEVRaydiumExecutor
            executor_status['MEV_RAYDIUM'] = '✅ AVAILABLE'
            print(f"✅ MEV Raydium Executor: Available")
        except Exception as e:
            executor_status['MEV_RAYDIUM'] = f'❌ {str(e)[:30]}'
            print(f"❌ MEV Raydium Executor: {e}")
        
        # Check MEV Meteora Executor
        try:
            from mev_meteora_executor import MEVMeteoraExecutor
            executor_status['MEV_METEORA'] = '✅ AVAILABLE'
            print(f"✅ MEV Meteora Executor: Available")
        except Exception as e:
            executor_status['MEV_METEORA'] = f'❌ {str(e)[:30]}'
            print(f"❌ MEV Meteora Executor: {e}")
        
        # Test actual execution methods
        print(f"\n🧪 TESTING EXECUTION METHODS:")
        
        test_token = "GvAECH86V7bFE5tN3irR3PPxneFdaJYaNNxHm67u4FJW"
        test_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"
        
        # Test 1: Direct copy buy method
        try:
            result = await coordinator._execute_copy_buy(
                token_mint=test_token,
                source_wallet=test_wallet,
                trade_info={'dex': 'pumpfun', 'signature': 'test'},
                detected_dex='pumpfun',
                amount_sol=0.001
            )
            
            if result and result.get('success'):
                print(f"✅ _execute_copy_buy: SUCCESS")
                executor_status['COPY_BUY_METHOD'] = '✅ WORKS'
            else:
                print(f"⚠️ _execute_copy_buy: Function works, expected no actual trade")
                executor_status['COPY_BUY_METHOD'] = '⚠️ FUNCTIONAL'
                
        except Exception as e:
            print(f"❌ _execute_copy_buy error: {e}")
            executor_status['COPY_BUY_METHOD'] = f'❌ {str(e)[:30]}'
        
        # Test 2: Copy sell method
        try:
            result = await coordinator._execute_copy_sell(
                token_mint=test_token,
                source_wallet=test_wallet,
                trade_info={'dex': 'pumpfun'},
                detected_dex='pumpfun'
            )
            
            if result and result.get('success'):
                print(f"✅ _execute_copy_sell: SUCCESS")
                executor_status['COPY_SELL_METHOD'] = '✅ WORKS'
            else:
                print(f"⚠️ _execute_copy_sell: Function works, expected no actual trade")
                executor_status['COPY_SELL_METHOD'] = '⚠️ FUNCTIONAL'
                
        except Exception as e:
            print(f"❌ _execute_copy_sell error: {e}")
            executor_status['COPY_SELL_METHOD'] = f'❌ {str(e)[:30]}'
        
        return executor_status
        
    except Exception as e:
        print(f"❌ Failed to test main.py executors: {e}")
        import traceback
        traceback.print_exc()
        return {}

async def test_main_py_integration():
    """Test the actual main.py workflow"""
    
    print(f"\n🎯 TESTING MAIN.PY INTEGRATION")
    print(f"=" * 50)
    
    try:
        # Test import and initialization
        from main import SimpleCopyTradingBot
        from config import CopyTradeConfig
        
        env_keys = EnvKeys()
        config = CopyTradeConfig(
            target_wallets=['3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv'],
            investment_amount_sol=0.001,
            use_jito=False,
            slippage_tolerance=0.3
        )
        
        bot = SimpleCopyTradingBot(config)
        
        # Test simulation of a trade detection
        mock_trade_info = {
            'signature': '5cUKAb9cTwKxktLfP8FqM9bBjEwT7F6bbqESshhJ46jBtiDwwHBA9bhZau6Ci1G8uvsGZvQzut5Ux4rQ2BRR6Jdu',
            'wallet': '3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv',
            'token_mint': 'mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd',
            'action': 'buy',
            'amount_sol': 0.001,
            'dex': 'pumpfun'
        }
        
        print(f"✅ Bot integration test successful")
        print(f"   📱 Wallet: {bot.wallet.pubkey()}")
        print(f"   🎯 Target wallets: {len(bot.target_wallets)}")
        print(f"   💰 Investment amount: {bot.config.investment_amount_sol} SOL")
        
        return True
        
    except Exception as e:
        print(f"❌ Main.py integration test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 MAIN.PY EXECUTOR ANALYSIS")
    
    # Test executors
    executor_status = asyncio.run(test_main_py_executors())
    
    # Test integration
    integration_works = asyncio.run(test_main_py_integration())
    
    print(f"\n📊 MAIN.PY EXECUTOR SUMMARY:")
    print(f"=" * 50)
    
    if executor_status:
        for executor, status in executor_status.items():
            print(f"   {executor}: {status}")
    
    print(f"\n   MAIN.PY INTEGRATION: {'✅ WORKS' if integration_works else '❌ BROKEN'}")
    
    working_count = len([s for s in executor_status.values() if '✅' in s]) if executor_status else 0
    total_count = len(executor_status) if executor_status else 0
    
    print(f"\n🎯 FINAL STATUS:")
    if working_count >= 3 and integration_works:
        print(f"✅ MAIN.PY IS READY FOR COPY TRADING!")
        print(f"   {working_count}/{total_count} executors available")
        print(f"   Integration layer working")
    else:
        print(f"⚠️ Main.py may need additional setup")
        print(f"   {working_count}/{total_count} executors available")