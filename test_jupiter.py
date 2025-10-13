#!/usr/bin/env python3
"""
Jupiter Test Script - Debug Jupiter API issues
"""

import asyncio
import traceback
from jupiter_utils import get_jupiter_quote, get_jupiter_transaction
from config import get_wallet_keypair

async def test_jupiter():
    """Test Jupiter API calls directly"""
    try:
        print("🔍 Testing Jupiter API...")
        
        # Test parameters (same as main.py)
        input_mint = "So11111111111111111111111111111111111111112"  # WSOL
        output_mint = "B62hAe9hUrTY1LGSRPgThygHMDfaQyZP9hzrWvdVbonk"  # Recent token from logs
        amount = int(0.01 * 1e9)  # 0.01 SOL in lamports
        slippage_bps = 300
        
        print(f"📊 Test params:")
        print(f"   Input: {input_mint}")
        print(f"   Output: {output_mint}")
        print(f"   Amount: {amount:,} lamports")
        print(f"   Slippage: {slippage_bps} bps")
        
        print("\n🔍 Step 1: Testing get_jupiter_quote...")
        quote_result = await get_jupiter_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps
        )
        
        print(f"📊 Quote result: {quote_result}")
        
        if not quote_result.success:
            print(f"❌ Quote failed: {quote_result.error}")
            return
            
        print("✅ Quote successful!")
        
        print("\n🔍 Step 2: Testing get_jupiter_transaction...")
        
        # Get wallet for transaction building
        wallet = get_wallet_keypair()
        wallet_pubkey = str(wallet.pubkey())
        
        print(f"📱 Wallet: {wallet_pubkey}")
        
        tx_result = await get_jupiter_transaction(
            quote=quote_result.quote,
            wallet_pubkey=wallet_pubkey,
            priority_fee_lamports=50000
        )
        
        print(f"📊 Transaction result: {tx_result}")
        
        if not tx_result.success:
            print(f"❌ Transaction failed: {tx_result.error}")
            return
            
        print("✅ Transaction successful!")
        print(f"📄 Transaction type: {type(tx_result.transaction)}")
        
        return True
        
    except Exception as e:
        print(f"❌ FATAL EXCEPTION in Jupiter test: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_jupiter())
    if success:
        print("\n✅ Jupiter test PASSED")
    else:
        print("\n❌ Jupiter test FAILED")
