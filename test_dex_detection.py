#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transaction_analyzer import TransactionAnalyzer
from solana.rpc.async_api import AsyncClient

async def test_dex_detection():
    """Test DEX detection for the failing transaction"""
    
    # The problematic transaction that was being detected as Pump.fun
    signature = "3fmwcJWcVoE7qtdFJSz9UQhpXjJohbGa3H79aqLzXhPHJhArxU2rBHZewmEKhdVD7ekSTcheABJzpov1iVgivAzi"
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    rpc_client = AsyncClient("https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
    
    try:
        analyzer = TransactionAnalyzer(rpc_client)
        result = await analyzer.analyze_transaction_with_balance_detection(signature, wallet_address)
        
        print("🔍 Transaction Analysis Result:")
        print(f"  - Token: {result.get('token_mint', 'N/A')}")
        print(f"  - Action: {result.get('action', 'N/A')}")
        print(f"  - DEX: {result.get('dex', 'N/A')}")
        print(f"  - Confidence: {result.get('confidence', 'N/A')}")
        
        if result.get('dex') == 'raydium_cpmm':
            print("✅ SUCCESS: Correctly detected as Raydium CPMM!")
        else:
            print(f"❌ ISSUE: Expected 'raydium_cpmm', got '{result.get('dex')}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await rpc_client.close()

if __name__ == "__main__":
    asyncio.run(test_dex_detection())
