#!/usr/bin/env python3
"""
PROPER BUY/SELL DETECTION using Balance Analysis
This implements the correct approach using preBalances, postBalances, and token balance changes
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from env_keys import EnvKeys

class ProperBuySellDetector:
    """
    Proper buy/sell detection using balance change analysis
    Based on the correct approach of tracking SOL and token balance changes
    """
    
    def __init__(self):
        self.kz = EnvKeys()
        self.rpc_url = self.kz.HELIUS_RPC_URL
    
    async def analyze_transaction(self, signature: str, wallet_address: str) -> Optional[str]:
        """
        Analyze a transaction to determine if it's a BUY or SELL
        Returns: 'buy', 'sell', or None if unable to determine
        """
        
        print(f"🎯 PROPER BALANCE-BASED DETECTION")
        print(f"📊 Analyzing: {signature[:12]}...")
        print(f"👤 Target wallet: {wallet_address[:8]}...")
        
        # Fetch full transaction data
        payload = {
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
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.rpc_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'error' in data:
                        print(f"❌ RPC Error: {data['error']}")
                        return None
                    
                    result = data.get('result')
                    if not result:
                        print(f"❌ No transaction data found")
                        return None
                    
                    # Extract transaction components
                    meta = result.get('meta', {})
                    transaction = result.get('transaction', {})
                    
                    if meta.get('err') is not None:
                        print(f"❌ Transaction failed: {meta.get('err')}")
                        return None
                    
                    print(f"✅ Transaction loaded successfully")
                    
                    # Perform balance-based analysis
                    trade_direction = self._analyze_balance_changes(meta, transaction, wallet_address)
                    
                    return trade_direction
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def _analyze_balance_changes(self, meta: Dict[str, Any], transaction: Dict[str, Any], wallet_address: str) -> Optional[str]:
        """
        The CORRECT way to detect buy/sell: analyze balance changes
        """
        
        print(f"\n🔍 BALANCE CHANGE ANALYSIS")
        print("=" * 50)
        
        # Get account keys and find wallet index
        message = transaction.get('message', {})
        account_keys = message.get('accountKeys', [])
        
        # Find wallet's index in account keys
        wallet_index = None
        for i, account in enumerate(account_keys):
            if account == wallet_address:
                wallet_index = i
                break
        
        if wallet_index is None:
            print(f"❌ Wallet {wallet_address[:8]}... not found in transaction accounts")
            return None
        
        print(f"✅ Found wallet at index {wallet_index}")
        
        # Analyze SOL balance changes
        pre_balances = meta.get('preBalances', [])
        post_balances = meta.get('postBalances', [])
        
        if wallet_index >= len(pre_balances) or wallet_index >= len(post_balances):
            print(f"❌ Balance data incomplete")
            return None
        
        pre_sol = pre_balances[wallet_index]
        post_sol = post_balances[wallet_index]
        sol_delta = post_sol - pre_sol
        
        print(f"💰 SOL BALANCE CHANGE:")
        print(f"   Pre:  {pre_sol / 1e9:.6f} SOL")
        print(f"   Post: {post_sol / 1e9:.6f} SOL")
        print(f"   Delta: {sol_delta / 1e9:.6f} SOL ({'📉 DECREASE' if sol_delta < 0 else '📈 INCREASE' if sol_delta > 0 else '➡️ NO CHANGE'})")
        
        # Analyze token balance changes
        pre_token_balances = meta.get('preTokenBalances', [])
        post_token_balances = meta.get('postTokenBalances', [])
        
        # Track token changes for our wallet
        token_changes = {}
        
        # Process pre-balances
        for balance in pre_token_balances:
            if balance.get('owner') == wallet_address:
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                token_changes[mint] = {'pre': amount, 'post': 0}
        
        # Process post-balances
        for balance in post_token_balances:
            if balance.get('owner') == wallet_address:
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if mint in token_changes:
                    token_changes[mint]['post'] = amount
                else:
                    token_changes[mint] = {'pre': 0, 'post': amount}
        
        print(f"\n🪙 TOKEN BALANCE CHANGES:")
        gained_tokens = []
        lost_tokens = []
        
        for mint, change in token_changes.items():
            pre = change['pre']
            post = change['post']
            delta = post - pre
            
            print(f"   {mint[:8]}...")
            print(f"     Pre:  {pre}")
            print(f"     Post: {post}")
            print(f"     Delta: {delta} ({'📈 GAINED' if delta > 0 else '📉 LOST' if delta < 0 else '➡️ NO CHANGE'})")
            
            if delta > 0:
                gained_tokens.append(mint)
            elif delta < 0:
                lost_tokens.append(mint)
        
        # Apply the CORRECT logic
        print(f"\n🧠 DECISION LOGIC:")
        print("=" * 30)
        
        # Core rule: Did wallet send SOL and receive tokens (BUY) or vice versa (SELL)?
        if sol_delta < 0 and gained_tokens:
            decision = 'buy'
            print(f"✅ BUY DETECTED:")
            print(f"   📉 SOL decreased by {abs(sol_delta) / 1e9:.6f} SOL")
            print(f"   📈 Gained {len(gained_tokens)} token type(s)")
            print(f"   💡 Wallet spent SOL to acquire tokens")
            
        elif sol_delta > 0 and lost_tokens:
            decision = 'sell'
            print(f"✅ SELL DETECTED:")
            print(f"   📈 SOL increased by {sol_delta / 1e9:.6f} SOL")
            print(f"   📉 Lost {len(lost_tokens)} token type(s)")
            print(f"   💡 Wallet sold tokens to receive SOL")
            
        else:
            # Edge cases and complex scenarios
            if gained_tokens and not lost_tokens:
                decision = 'buy'
                print(f"✅ BUY DETECTED (edge case):")
                print(f"   📈 Gained tokens without losing any")
                print(f"   💡 Likely a buy transaction")
                
            elif lost_tokens and not gained_tokens:
                decision = 'sell'
                print(f"✅ SELL DETECTED (edge case):")
                print(f"   📉 Lost tokens without gaining any")
                print(f"   💡 Likely a sell transaction")
                
            else:
                decision = None
                print(f"❓ UNABLE TO DETERMINE:")
                print(f"   📊 SOL delta: {sol_delta / 1e9:.6f}")
                print(f"   📊 Gained tokens: {len(gained_tokens)}")
                print(f"   📊 Lost tokens: {len(lost_tokens)}")
                print(f"   💡 Complex transaction pattern")
        
        return decision

async def test_proper_detection():
    """Test the proper detection on the problematic sell transaction"""
    
    # The SELL transaction that our old system got wrong
    sell_signature = "2oAemxGqPk3pY3A1hGrV3q91EeBtAVLJ1ez8LM2KrMeGwTT2Xa3pa9ZgzU5U7aMcyoDMPegpKhr1eZhGpAgsxEwW"
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # Example wallet
    
    detector = ProperBuySellDetector()
    
    print("🚨 TESTING PROPER DETECTION ON CONFIRMED SELL")
    print("=" * 60)
    print("This transaction was incorrectly classified as BUY by our old system")
    print("Let's see if balance-based detection gets it right...")
    print("=" * 60)
    
    result = await detector.analyze_transaction(sell_signature, wallet_address)
    
    print(f"\n🎯 FINAL RESULT:")
    print("=" * 30)
    if result == 'sell':
        print(f"✅ CORRECT! Detected as SELL")
        print(f"🔧 Balance-based detection works!")
    elif result == 'buy':
        print(f"❌ STILL WRONG! Detected as BUY")
        print(f"🔧 Need to investigate further...")
    else:
        print(f"❓ INCONCLUSIVE: Unable to determine")
        print(f"🔧 May need additional logic...")

if __name__ == "__main__":
    asyncio.run(test_proper_detection())
