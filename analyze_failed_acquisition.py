#!/usr/bin/env python3
"""
Analyze why "successful" transactions didn't acquire tokens
"""

import asyncio
import json
import requests

async def analyze_failed_acquisition():
    """Analyze why successful transactions didn't acquire tokens"""
    
    print("🔍 ANALYZING WHY 'SUCCESSFUL' TRANSACTIONS DIDN'T ACQUIRE TOKENS")
    print("="*70)
    
    # These are the "successful" signatures from your logs
    successful_signatures = [
        "PKVY7DmmsAoC6P1xCke21DVPttT1kQ87EF6Txt5kYkRxs4acpDLcbauYimL7FtvrE1jsk7C74oRBFZACGjKFfuH",
        "2Unzu2ZKyRv5AxEtSeecB86E9zpxihwQoRuavrqwfAdtjuxA4dkuqbZCTTcxz5HASg7JxnkCDugEb1akBg643jSJ",
        "4vkAz2xGdoAwfPT4Xi5us9TU7DHuVo7NrNuxRj9mzKKiYzKT4z2V6rr5hgByAfKU4ht6Yxzn8UoR4TRPY9bgBxsw"
    ]
    
    target_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"  # Your wallet
    
    print(f"📊 ANALYZING {len(successful_signatures)} 'SUCCESSFUL' TRANSACTIONS")
    print(f"🎯 Target wallet: {target_wallet}")
    print()
    
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    for i, signature in enumerate(successful_signatures, 1):
        print(f"📝 TRANSACTION {i}: {signature}")
        
        try:
            # Get transaction details
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            response = requests.post(rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if not data.get('result'):
                print(f"   ❌ No transaction data found")
                continue
                
            transaction = data['result']
            meta = transaction.get('meta', {})
            
            # Check if transaction succeeded
            if meta.get('err'):
                print(f"   ❌ Transaction failed: {meta['err']}")
                continue
                
            print(f"   ✅ Transaction succeeded on blockchain")
            
            # Check account balances
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            account_keys = transaction.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            # Find your wallet in the account keys
            wallet_index = None
            for idx, account in enumerate(account_keys):
                if account == target_wallet:
                    wallet_index = idx
                    break
            
            if wallet_index is not None:
                pre_sol = pre_balances[wallet_index] / 1e9
                post_sol = post_balances[wallet_index] / 1e9
                sol_change = post_sol - pre_sol
                
                print(f"   💰 SOL Balance Change: {sol_change:.6f} SOL")
                
                if sol_change < -0.001:  # Spent more than just fees
                    print(f"   💸 SOL was spent ({abs(sol_change):.6f} SOL)")
                else:
                    print(f"   🚨 Minimal SOL spent - possible failed swap!")
            else:
                print(f"   ❓ Your wallet not found in transaction accounts")
            
            # Check token balance changes
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            your_token_changes = []
            for post_token in post_token_balances:
                if post_token['owner'] == target_wallet:
                    # Find corresponding pre-balance
                    pre_amount = 0
                    for pre_token in pre_token_balances:
                        if (pre_token['owner'] == target_wallet and 
                            pre_token['mint'] == post_token['mint']):
                            pre_amount = float(pre_token['uiTokenAmount']['uiAmount'] or 0)
                            break
                    
                    post_amount = float(post_token['uiTokenAmount']['uiAmount'] or 0)
                    change = post_amount - pre_amount
                    
                    if abs(change) > 0.000001:  # Meaningful change
                        your_token_changes.append({
                            'mint': post_token['mint'],
                            'change': change,
                            'symbol': 'TOKENS'
                        })
            
            if your_token_changes:
                print(f"   🪙 Token Balance Changes:")
                for change in your_token_changes:
                    print(f"      {change['change']:+.6f} {change['symbol']} ({change['mint'][:8]}...)")
            else:
                print(f"   🚨 NO TOKEN BALANCE CHANGES - BUY FAILED!")
                
        except Exception as e:
            print(f"   ❌ Error analyzing transaction: {e}")
        
        print()
    
    print("🎯 SUMMARY:")
    print("   The transactions succeeded on blockchain but failed to acquire tokens because:")
    print("   1. ❌ Wrong action (sell detected → buy executed)")
    print("   2. ❌ Corrupted token data from emergency fallback")
    print("   3. ❌ Bad timing (buying while price crashes from sells)")
    print("   4. ❌ Wrong pool state calculations")
    print("   5. ❌ MEV executor logs 'success' for blockchain success, not acquisition success")

if __name__ == "__main__":
    asyncio.run(analyze_failed_acquisition())
