#!/usr/bin/env python3
"""
Direct executor test - test individual executors to find which ones return real signatures
"""

import asyncio
import sys
from config import CopyTradeConfig
from official_executor_wrappers import try_pumpfun_buy, try_jupiter_buy

async def test_direct_executor(executor_func, executor_name, token_mint, amount_sol):
    """Test a specific executor and validate its signature"""
    try:
        print(f"\n🧪 Testing {executor_name}...")
        print(f"   💎 Token: {token_mint[:8]}...")
        print(f"   💰 Amount: {amount_sol} SOL")
        
        result = await executor_func(
            wallet_keypair=config.wallet,
            token_mint=token_mint,
            amount_sol=amount_sol,
            max_retries=1,
            confirmation_timeout=20.0,
            priority_fee_multiplier=2.0,
            slippage_tolerance=0.30,
            original_wallet="direct_test"
        )
        
        print(f"   📊 Result: {result}")
        
        if result and result.get('success'):
            signature = result.get('signature', '')
            
            # Check if signature is real
            if signature and signature != '1111111111111111111111111111111111111111111111111111111111111111' and len(signature) >= 64:
                print(f"   ✅ {executor_name}: REAL signature {signature[:12]}...")
                print(f"   🌐 Solscan: https://solscan.io/tx/{signature}")
                return True, signature
            else:
                print(f"   ❌ {executor_name}: FAKE signature {signature}")
                return False, signature
        else:
            error = result.get('error', 'No error info') if result else 'No result returned'
            print(f"   ❌ {executor_name}: Failed - {error}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ {executor_name}: Exception - {e}")
        return False, None

async def main():
    """Test all executors to find which ones work"""
    global config
    config = CopyTradeConfig()
    
    print("🔬 DIRECT EXECUTOR SIGNATURE TEST")
    print("Testing each executor individually to find real vs fake signatures")
    print("=" * 60)
    
    # Use the same token from your logs that was working
    test_token = "J3FBk7xAEDgcFem1G3Z2DwSZNiAQHg62ujzkn2bbBAGS"
    test_amount = 0.0001  # Small test amount
    
    # Test executors one by one
    executors_to_test = [
        (try_pumpfun_buy, "PUMP.FUN"),
        (try_jupiter_buy, "JUPITER"),
    ]
    
    real_signatures = []
    fake_signatures = []
    
    for executor_func, executor_name in executors_to_test:
        is_real, signature = await test_direct_executor(
            executor_func, executor_name, test_token, test_amount
        )
        
        if is_real:
            real_signatures.append((executor_name, signature))
        elif signature:
            fake_signatures.append((executor_name, signature))
        
        # Wait between tests
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if real_signatures:
        print("✅ EXECUTORS WITH REAL SIGNATURES:")
        for name, sig in real_signatures:
            print(f"   🎯 {name}: {sig[:12]}...")
            print(f"      🌐 https://solscan.io/tx/{sig}")
    else:
        print("❌ NO EXECUTORS RETURNED REAL SIGNATURES")
    
    if fake_signatures:
        print("\n❌ EXECUTORS WITH FAKE SIGNATURES:")
        for name, sig in fake_signatures:
            print(f"   🚫 {name}: {sig}")
    
    print("\n" + "=" * 60)
    if real_signatures:
        print("✅ CONCLUSION: Some executors ARE working correctly")
        print("🎯 Use the working executors for your bot")
    else:
        print("❌ CONCLUSION: All executors returning fake signatures")
        print("🔧 Need to fix the executor implementation")

if __name__ == "__main__":
    asyncio.run(main())
