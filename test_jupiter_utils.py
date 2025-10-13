#!/usr/bin/env python3
"""
Test Jupiter Utils - Verify that the Jupiter utilities are working correctly
"""

import asyncio
from jupiter_utils import get_jupiter_quote, get_jupiter_transaction, JUPITER_AVAILABLE

async def test_jupiter_integration():
    """Test the Jupiter utilities"""
    print("🧪 Testing Jupiter Integration...")
    
    # Test parameters
    test_token = "5SHqbKukwFLCnTarVS1SEUGBj8LtYQPTrZYvxoVSbonk"  # Example token from terminal
    sol_amount = 0.001  # 0.001 SOL
    lamports = int(sol_amount * 1e9)
    wallet_pubkey = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    
    print(f"📊 Test parameters:")
    print(f"   Token: {test_token}")
    print(f"   Amount: {sol_amount} SOL ({lamports:,} lamports)")
    print(f"   Wallet: {wallet_pubkey}")
    
    try:
        # Test 1: Get Jupiter quote
        print(f"\n🔍 Test 1: Getting Jupiter quote...")
        quote_result = await get_jupiter_quote(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint=test_token,
            amount=lamports,
            slippage_bps=5000,
            wallet_pubkey=wallet_pubkey
        )
        
        if quote_result.success:
            print(f"✅ Quote successful!")
            print(f"   Input: {quote_result.quote['inAmount']} lamports")
            print(f"   Output: {quote_result.quote['outAmount']} tokens")
        else:
            print(f"❌ Quote failed: {quote_result.error}")
            return False
        
        # Test 2: Get Jupiter transaction
        print(f"\n🔍 Test 2: Getting Jupiter transaction...")
        tx_result = await get_jupiter_transaction(
            quote=quote_result.quote,
            wallet_pubkey=wallet_pubkey,
            priority_fee_lamports=50000
        )
        
        if tx_result.success:
            print(f"✅ Transaction built successfully!")
            print(f"   Transaction type: {type(tx_result.transaction)}")
            print(f"   Transaction ready for signing and submission")
        else:
            print(f"❌ Transaction building failed: {tx_result.error}")
            return False
        
        print(f"\n✅ ALL TESTS PASSED! Jupiter integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_jupiter_integration())
    if result:
        print(f"\n🎉 Jupiter utilities are ready for Jito execution!")
    else:
        print(f"\n🚨 Jupiter utilities need fixing before Jito can work!")
