#!/usr/bin/env python3

"""
Test ultra-aggressive account keys fallback across all extraction methods.
This test verifies that when all other extraction methods fail, the methods
fall back to checking account keys for any valid Solana addresses.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json

# Mock transaction with account keys but no token balances, logs, etc.
MOCK_TRANSACTION_WITH_ACCOUNT_KEYS = {
    "transaction": {
        "message": {
            "accountKeys": [
                "11111111111111111111111111111111",  # System Program (should be excluded)
                "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # VALID TOKEN MINT
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program (should be excluded) 
                "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB",  # Known wallet (should be excluded)
                "So11111111111111111111111111111111111111112",  # Wrapped SOL (should be excluded)
                "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # ANOTHER VALID TOKEN MINT
                "ComputeBudget111111111111111111111111111111"   # Compute Budget (should be excluded)
            ]
        },
        "signatures": ["test_signature_12345"]
    },
    "meta": {
        "logMessages": [],  # Empty logs to force account keys fallback
        "preTokenBalances": [],  # Empty token balances to force account keys fallback
        "postTokenBalances": []  # Empty token balances to force account keys fallback
    }
}

async def test_ultra_aggressive_account_keys():
    """Test ultra-aggressive account keys fallback across all extraction methods"""
    
    try:
        # Import and setup
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from trade_processor import TradeProcessor
        from solana.rpc.async_api import AsyncClient
        
        # Setup logging to capture debug messages
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        logger = logging.getLogger(__name__)
        
        print("🧪 Testing Ultra-Aggressive Account Keys Fallback")
        print("=" * 60)
        
        # Initialize processor
        rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
        processor = TradeProcessor(rpc_client)
        
        results = {}
        expected_mint = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"  # First valid mint in account keys
        
        # Test 1: _extract_sophisticated_token_mint
        print("\\n🔍 Testing _extract_sophisticated_token_mint with account keys fallback...")
        try:
            # This method needs a wallet_pubkey parameter
            wallet_pubkey = "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB"
            result1 = await processor._extract_sophisticated_token_mint(MOCK_TRANSACTION_WITH_ACCOUNT_KEYS, wallet_pubkey)
            results["sophisticated"] = result1
            if result1 == expected_mint:
                print(f"✅ SUCCESS: Found expected mint {result1[:8]}... via account keys fallback")
            else:
                print(f"⚠️  UNEXPECTED: Got {result1[:8] if result1 else None}... expected {expected_mint[:8]}...")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["sophisticated"] = None
        
        # Test 2: _extract_real_token_mint  
        print("\\n🔍 Testing _extract_real_token_mint with account keys fallback...")
        try:
            result2 = await processor._extract_real_token_mint(MOCK_TRANSACTION_WITH_ACCOUNT_KEYS)
            results["real_token"] = result2
            if result2 == expected_mint:
                print(f"✅ SUCCESS: Found expected mint {result2[:8]}... via account keys fallback")
            else:
                print(f"⚠️  UNEXPECTED: Got {result2[:8] if result2 else None}... expected {expected_mint[:8]}...")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["real_token"] = None
        
        # Test 3: _extract_jupiter_token_from_balance_changes
        print("\\n🔍 Testing _extract_jupiter_token_from_balance_changes with account keys fallback...")
        try:
            result3 = await processor._extract_jupiter_token_from_balance_changes(MOCK_TRANSACTION_WITH_ACCOUNT_KEYS)
            results["jupiter_balance"] = result3
            if result3 == expected_mint:
                print(f"✅ SUCCESS: Found expected mint {result3[:8]}... via account keys fallback")
            else:
                print(f"⚠️  UNEXPECTED: Got {result3[:8] if result3 else None}... expected {expected_mint[:8]}...")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["jupiter_balance"] = None
            
        # Summary
        print("\\n" + "=" * 60)
        print("🏆 ULTRA-AGGRESSIVE ACCOUNT KEYS FALLBACK TEST SUMMARY")
        print("=" * 60)
        
        success_count = sum(1 for result in results.values() if result == expected_mint)
        total_methods = len(results)
        
        print(f"SUCCESS RATE: {success_count}/{total_methods} methods")
        print(f"Expected mint: {expected_mint}")
        print("")
        
        for method, result in results.items():
            status = "✅ SUCCESS" if result == expected_mint else "❌ FAILED"
            result_display = result[:8] + "..." if result else "None"
            print(f"{status} - {method}: {result_display}")
        
        if success_count == total_methods:
            print("\\n🎉 ALL METHODS SUCCESSFULLY IMPLEMENTED ULTRA-AGGRESSIVE ACCOUNT KEYS FALLBACK!")
        else:
            print(f"\\n⚠️  {total_methods - success_count} methods need ultra-aggressive account keys fallback implementation")
            
        return results
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return {}

if __name__ == "__main__":
    results = asyncio.run(test_ultra_aggressive_account_keys())
    
    # Additional validation
    if results:
        print("\\n📊 DETAILED RESULTS:")
        print(json.dumps(results, indent=2))