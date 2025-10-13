#!/usr/bin/env python3

import asyncio
import logging
from env_keys import EnvKeys

# Configure logging
logging.basicConfig(level=logging.INFO)

async def find_active_pumpfun_token():
    """Find a currently active Pump.fun token for testing"""
    
    env_keys = EnvKeys()
    
    # Get recent Pump.fun transactions to find active tokens
    import httpx
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Use Helius API to get recent transactions for Pump.fun program
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun program
                {
                    "limit": 10,
                    "commitment": "confirmed"
                }
            ]
        }
        
        response = await client.post(env_keys.HELIUS_RPC_URL, json=rpc_payload)
        
        if response.status_code == 200:
            result = response.json()
            signatures = result.get('result', [])
            
            print(f"🔍 Found {len(signatures)} recent Pump.fun transactions")
            
            # Analyze the first few transactions to extract token mints
            for i, sig_info in enumerate(signatures[:5]):
                signature = sig_info['signature']
                print(f"\n📝 Transaction {i+1}: {signature}")
                
                # Get transaction details
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": "json",
                            "commitment": "confirmed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                tx_response = await client.post(env_keys.HELIUS_RPC_URL, json=tx_payload)
                
                if tx_response.status_code == 200:
                    tx_result = tx_response.json()
                    
                    if 'result' in tx_result and tx_result['result']:
                        tx_data = tx_result['result']
                        
                        # Look for token mints in the account keys
                        if 'transaction' in tx_data and 'message' in tx_data['transaction']:
                            account_keys = tx_data['transaction']['message'].get('accountKeys', [])
                            
                            # Find potential token mints (usually 44 characters)
                            for account in account_keys:
                                if len(account) == 44 and not account.startswith('11111'):  # Filter out system program
                                    print(f"   🪙 Potential token: {account}")
                                    
                                    # Return the first valid token we find
                                    if i == 0:  # Use from the most recent transaction
                                        return account
                                        
                await asyncio.sleep(0.1)  # Small delay between requests
        
        return None

async def test_sell_with_direct_executor():
    """Test sell functionality using the direct sell executor"""
    
    print(f"\n🎯 Testing DIRECT SELL executor...")
    
    try:
        from mev_direct_sell_executor import MEVDirectSellExecutor
        from env_keys import EnvKeys
        
        env_keys = EnvKeys()
        private_key = env_keys.PHANTOM_PRIVATE_KEY
        
        # Find a test wallet that recently sold tokens
        test_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"  # From our original transaction
        test_token = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"
        
        sell_executor = MEVDirectSellExecutor(private_key)
        
        print(f"🔍 Analyzing sell patterns for wallet: {test_wallet[:8]}...")
        
        # Analyze the wallet's sell pattern
        sell_pattern = await sell_executor.analyze_wallet_sell_pattern(
            test_wallet, 
            test_token
        )
        
        if sell_pattern:
            print(f"✅ SELL EXECUTOR WORKS: Found sell pattern")
            print(f"   📝 Pattern signature: {sell_pattern.get('signature', 'Unknown')}")
            return True
        else:
            print(f"❌ No sell pattern found for test wallet")
            return False
            
    except Exception as e:
        print(f"❌ Direct sell executor test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🔍 Searching for active Pump.fun token...")
    
    # Find active token
    active_token = asyncio.run(find_active_pumpfun_token())
    
    if active_token:
        print(f"\n✅ Found active token: {active_token}")
    else:
        print(f"\n⚠️ Could not find active token")
        
    # Test sell executor
    sell_works = asyncio.run(test_sell_with_direct_executor())
    
    if sell_works:
        print(f"\n✅ SELL CAPABILITY CONFIRMED!")
    else:
        print(f"\n⚠️ SELL CAPABILITY NEEDS INVESTIGATION")