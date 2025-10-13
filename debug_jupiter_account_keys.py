#!/usr/bin/env python3

"""
Detailed test to debug why Jupiter method doesn't reach account keys fallback.
This will show us the exact execution path.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

# Mock transaction specifically designed to fail all normal extraction methods
MOCK_TRANSACTION_EMPTY_ALL = {
    "transaction": {
        "message": {
            "accountKeys": [
                "11111111111111111111111111111111",  # System Program (should be excluded)
                "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # VALID TOKEN MINT
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program (should be excluded) 
                "So11111111111111111111111111111111111111112",  # Wrapped SOL (should be excluded)
                "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"   # ANOTHER VALID TOKEN MINT
            ]
        },
        "signatures": ["test_signature_debug_jupiter"]
    },
    "meta": {
        "logMessages": [],  # Empty logs to force account keys fallback
        "preTokenBalances": [],  # Empty token balances to force account keys fallback
        "postTokenBalances": []  # Empty token balances to force account keys fallback
    }
}

async def debug_jupiter_method():
    """Debug the Jupiter method step by step"""
    
    try:
        # Import and setup
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from trade_processor import TradeProcessor
        from solana.rpc.async_api import AsyncClient
        
        # Setup debug logging to see all messages
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        logger = logging.getLogger(__name__)
        
        print("🔬 DEBUGGING JUPITER METHOD - ULTRA-AGGRESSIVE ACCOUNT KEYS FALLBACK")
        print("=" * 80)
        
        # Initialize processor
        rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
        processor = TradeProcessor(rpc_client)
        
        print("\\n📋 Test Transaction Structure:")
        print(f"   Account Keys: {len(MOCK_TRANSACTION_EMPTY_ALL['transaction']['message']['accountKeys'])}")
        print(f"   Token Balances: {len(MOCK_TRANSACTION_EMPTY_ALL['meta']['postTokenBalances'])}")
        print(f"   Log Messages: {len(MOCK_TRANSACTION_EMPTY_ALL['meta']['logMessages'])}")
        print(f"   Expected to find: 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")
        
        print("\\n🧪 Executing _extract_jupiter_token_from_balance_changes...")
        print("-" * 60)
        
        # Call the method with debug logging enabled
        result = await processor._extract_jupiter_token_from_balance_changes(MOCK_TRANSACTION_EMPTY_ALL)
        
        print("-" * 60)
        print(f"🎯 FINAL RESULT: {result}")
        
        if result:
            if isinstance(result, dict):
                print(f"   Type: Dictionary")
                print(f"   Token Mint: {result.get('token_mint', 'N/A')}")
                print(f"   Action: {result.get('action', 'N/A')}")
                print(f"   Method: {result.get('method', 'N/A')}")
            else:
                print(f"   Type: String")
                print(f"   Value: {result}")
                print(f"   Expected: 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")
                
            if str(result) == "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R" or (isinstance(result, dict) and result.get('token_mint') == "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"):
                print("   ✅ SUCCESS: Ultra-aggressive fallback working!")
            else:
                print("   ⚠️  UNEXPECTED: Different result than expected")
        else:
            print("   ❌ NULL RESULT: Ultra-aggressive fallback not working")
            
        return result
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(debug_jupiter_method())