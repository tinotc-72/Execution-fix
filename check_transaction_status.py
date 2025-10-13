#!/usr/bin/env python3
"""
Check Transaction Status
"""

import asyncio
import httpx
from env_keys import EnvKeys

async def check_transaction_status():
    """Check the status of our MEV transaction"""
    
    signature = "31dNHVwX4gLmbXyQ8ttCfCZHW6neoJiJcnJGqBMFbBPb5cSVJQ1SNVmLs32texnuHSAAbwmUD1F2WL2QgvbwRB37"
    
    env = EnvKeys()
    
    print(f"🔍 Checking transaction status...")
    print(f"Signature: {signature}")
    print(f"Explorer: https://solscan.io/tx/{signature}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get transaction status
        response = await client.post(
            env.HELIUS_RPC_URL,
            json={
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
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"❌ RPC Error: {data['error']}")
                return
                
            result = data.get('result')
            if result is None:
                print(f"❌ Transaction not found or still processing")
                return
                
            # Check if transaction succeeded
            meta = result.get('meta', {})
            error = meta.get('err')
            
            if error:
                print(f"❌ Transaction failed: {error}")
            else:
                print(f"✅ Transaction succeeded!")
                
            print(f"\n📊 Transaction Details:")
            print(f"Slot: {result.get('slot', 'Unknown')}")
            print(f"Block Time: {result.get('blockTime', 'Unknown')}")
            print(f"Fee: {meta.get('fee', 'Unknown')} lamports")
            
            # Check pre/post balances
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            if pre_balances and post_balances:
                print(f"SOL Balance Change: {(post_balances[0] - pre_balances[0]) / 1e9:.9f} SOL")
                
            # Check token changes
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            print(f"\n🪙 Token Balance Changes:")
            if pre_token_balances or post_token_balances:
                for balance in post_token_balances:
                    if balance not in pre_token_balances:
                        print(f"   New token: {balance['mint']}")
                        print(f"   Amount: {balance['uiTokenAmount']['amount']}")
            else:
                print(f"   No token balance changes")
                
            # Check logs for errors
            log_messages = meta.get('logMessages', [])
            print(f"\n📝 Transaction Logs:")
            for log in log_messages[-5:]:  # Last 5 logs
                print(f"   {log}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(check_transaction_status())
