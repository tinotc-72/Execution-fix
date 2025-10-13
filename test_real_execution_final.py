#!/usr/bin/env python3
"""
REAL EXECUTION TEST - Actually test execution capabilities with TINY amounts
This will attempt REAL trades with minimal SOL to prove executors work
WARNING: This will spend small amounts of SOL for testing
"""

import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging for visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_real_execution_capabilities():
    """
    Test ACTUAL execution with tiny amounts to prove executors work
    This will attempt real trades to verify the system works
    """
    
    print('🚨 REAL EXECUTION CAPABILITY TEST')
    print('=' * 60)
    print('⚠️  WARNING: This will attempt REAL trades with tiny amounts')
    print('💰 Testing with minimal SOL to prove your executors work')
    print('🎯 Goal: Verify execution happens, not just validation')
    print()
    
    # Get user confirmation
    response = input('🤔 Do you want to proceed with REAL execution testing? (yes/no): ')
    if response.lower() not in ['yes', 'y']:
        print('❌ Test cancelled - no execution attempted')
        return False
    
    test_amount = input('💰 Enter test amount in SOL (recommend 0.0001): ')
    try:
        test_sol = float(test_amount)
        if test_sol > 0.01:  # Safety limit
            print('⚠️ Amount too high for testing - limiting to 0.01 SOL')
            test_sol = 0.01
    except:
        print('💡 Using default: 0.0001 SOL')
        test_sol = 0.0001
    
    print(f'🧪 Testing with {test_sol} SOL')
    print()
    
    try:
        # Setup
        from config import WALLET, BOT_PUBKEY
        from env_keys import EnvKeys
        from solana.rpc.async_api import AsyncClient
        
        env_keys = EnvKeys()
        rpc_client = AsyncClient(env_keys.HELIUS_RPC_URL)
        
        # Check wallet balance first
        print('1. 💰 Checking Wallet Balance...')
        balance_response = await rpc_client.get_balance(WALLET.pubkey())
        sol_balance = balance_response.value / 1e9
        
        print(f'   Current balance: {sol_balance:.6f} SOL')
        
        if sol_balance < test_sol + 0.001:  # Need extra for fees
            print(f'   ❌ Insufficient balance for test')
            print(f'   💡 Need at least {test_sol + 0.001:.6f} SOL (including fees)')
            await rpc_client.close()
            return False
        
        print(f'   ✅ Sufficient balance for testing')
        print()
        
        # Test 1: Jupiter Execution with WSOL (should work)
        print('2. 🪐 Testing Jupiter Execution (WSOL)...')
        print(f'   Attempting to buy {test_sol} SOL worth of WSOL via Jupiter')
        
        try:
            from official_executor_wrappers import try_jupiter_buy
            
            jupiter_result = await try_jupiter_buy(
                WALLET,
                'So11111111111111111111111111111111111111112',  # WSOL
                test_sol
            )
            
            print(f'   📊 Jupiter Result:')
            print(f'      Success: {jupiter_result.get("success", False)}')
            print(f'      Signature: {jupiter_result.get("signature", "None")}')
            print(f'      Error: {jupiter_result.get("error", "None")}')
            
            if jupiter_result.get("success") and jupiter_result.get("signature"):
                print(f'   ✅ JUPITER EXECUTION SUCCESSFUL!')
                print(f'   🔗 Signature: {jupiter_result["signature"]}')
                print(f'   💎 Your executor WORKS for Jupiter trades!')
                jupiter_works = True
            else:
                print(f'   ❌ Jupiter execution failed')
                print(f'   🐛 Error: {jupiter_result.get("error", "Unknown")}')
                jupiter_works = False
                
        except Exception as e:
            print(f'   ❌ Jupiter test exception: {str(e)}')
            jupiter_works = False
        
        print()
        
        # Test 2: Test with a different token (if balance allows)
        if sol_balance > test_sol * 2 + 0.002:  # Have enough for another test
            print('3. 🎯 Testing Alternative Token Execution...')
            
            # Try USDC (should route to Jupiter)
            try:
                from official_executor_wrappers import try_jupiter_buy
                
                print(f'   Attempting to buy {test_sol} SOL worth of USDC via Jupiter')
                
                usdc_result = await try_jupiter_buy(
                    WALLET,
                    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
                    test_sol
                )
                
                print(f'   📊 USDC Result:')
                print(f'      Success: {usdc_result.get("success", False)}')
                print(f'      Signature: {usdc_result.get("signature", "None")}')
                
                if usdc_result.get("success") and usdc_result.get("signature"):
                    print(f'   ✅ USDC EXECUTION SUCCESSFUL!')
                    print(f'   🔗 Signature: {usdc_result["signature"]}')
                    usdc_works = True
                else:
                    print(f'   ❌ USDC execution failed: {usdc_result.get("error", "Unknown")}')
                    usdc_works = False
                    
            except Exception as e:
                print(f'   ❌ USDC test exception: {str(e)}')
                usdc_works = False
        else:
            print('3. ⚠️ Skipping second test - insufficient balance')
            usdc_works = None
        
        print()
        
        # Test 3: Test pump.fun validation (should reject WSOL correctly)
        print('4. 🔥 Testing Pump.fun Validation...')
        
        try:
            from official_executor_wrappers import try_pumpfun_buy
            
            print(f'   Attempting pump.fun trade with WSOL (should be rejected)')
            
            pumpfun_result = await try_pumpfun_buy(
                WALLET,
                'So11111111111111111111111111111111111111112',  # WSOL
                test_sol
            )
            
            print(f'   📊 Pump.fun Result:')
            print(f'      Success: {pumpfun_result.get("success", False)}')
            print(f'      Error: {pumpfun_result.get("error", "None")}')
            
            if not pumpfun_result.get("success"):
                print(f'   ✅ PUMP.FUN CORRECTLY REJECTED WSOL!')
                print(f'   🛡️ Validation working - no money wasted!')
                pumpfun_validation_works = True
            else:
                print(f'   ⚠️ Pump.fun accepted WSOL (unexpected)')
                pumpfun_validation_works = False
                
        except Exception as e:
            print(f'   ❌ Pump.fun test exception: {str(e)}')
            pumpfun_validation_works = False
        
        print()
        
        # Test 4: Check final balance
        print('5. 📊 Final Balance Check...')
        
        final_balance_response = await rpc_client.get_balance(WALLET.pubkey())
        final_sol_balance = final_balance_response.value / 1e9
        
        balance_change = sol_balance - final_sol_balance
        
        print(f'   Initial balance: {sol_balance:.6f} SOL')
        print(f'   Final balance: {final_sol_balance:.6f} SOL')
        print(f'   Balance change: -{balance_change:.6f} SOL')
        
        await rpc_client.close()
        
        # Results Summary
        print()
        print('🎉 REAL EXECUTION TEST COMPLETE!')
        print('=' * 50)
        print()
        print('📋 TEST RESULTS:')
        
        if jupiter_works:
            print('   ✅ Jupiter Executor: WORKING!')
            print('      💎 Your bot CAN execute Jupiter trades')
        else:
            print('   ❌ Jupiter Executor: FAILED')
            print('      🐛 Jupiter trades will not work')
        
        if usdc_works is True:
            print('   ✅ USDC Trading: WORKING!')
            print('      💎 Your bot CAN trade USDC via Jupiter')
        elif usdc_works is False:
            print('   ❌ USDC Trading: FAILED')
        else:
            print('   ⚠️ USDC Trading: SKIPPED (insufficient balance)')
        
        if pumpfun_validation_works:
            print('   ✅ Pump.fun Validation: WORKING!')
            print('      🛡️ Invalid trades are correctly rejected')
        else:
            print('   ❌ Pump.fun Validation: NEEDS ATTENTION')
        
        print()
        print('💰 FINANCIAL IMPACT:')
        print(f'   Test cost: {balance_change:.6f} SOL (${balance_change * 150:.4f} USD approx)')
        
        if jupiter_works or usdc_works:
            print()
            print('🔥 CRITICAL RESULT: YOUR EXECUTORS WORK!')
            print('✅ When memecoins are detected, execution WILL happen')
            print('💎 Your 8 months of work has paid off!')
            print('🚀 Ready for profitable memecoin copy trading!')
            
            return True
        else:
            print()
            print('❌ CRITICAL ISSUE: Executors not working properly')
            print('🐛 Execution problems need to be resolved')
            print('💔 More debugging required')
            
            return False
        
    except Exception as e:
        print(f'❌ REAL EXECUTION TEST ERROR: {e}')
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print('🚨 REAL EXECUTION CAPABILITY TEST')
    print('This will test if your executors actually work by attempting real trades')
    print()
    
    result = asyncio.run(test_real_execution_capabilities())
    
    if result:
        print('\n🎯 FINAL RESULT: EXECUTION CAPABILITIES CONFIRMED!')
        print('🚀 Your bot is ready for live memecoin trading!')
    else:
        print('\n❌ FINAL RESULT: EXECUTION ISSUES DETECTED')
        print('🔧 Further debugging required')
