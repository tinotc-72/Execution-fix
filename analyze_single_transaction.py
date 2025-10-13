#!/usr/bin/env python3
"""
Single Transaction Analysis Tool
Uses proper balance-based detection to analyze a specific transaction
"""

import asyncio
import aiohttp
import json
from env_keys import EnvKeys

class SingleTransactionAnalyzer:
    """Analyze a single transaction using proper balance-based detection"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            self.rpc_url = kz.HELIUS_RPC_URL
            print(f"📡 RPC URL loaded: {self.rpc_url[:50]}...")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            raise
    
    async def analyze_transaction(self, signature: str, expected_wallet: str = None):
        """
        Analyze a transaction using proper balance-based detection
        """
        print(f"🔍 ANALYZING TRANSACTION: {signature}")
        print("=" * 80)
        
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
        
        try:
            async with aiohttp.ClientSession() as session:
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
                    message = transaction.get('message', {})
                    
                    print(f"📊 TRANSACTION OVERVIEW:")
                    print(f"   Status: {'✅ SUCCESS' if meta.get('err') is None else '❌ FAILED'}")
                    print(f"   Fee: {meta.get('fee', 0) / 1e9:.6f} SOL")
                    print(f"   Compute Units: {meta.get('computeUnitsConsumed', 'Unknown')}")
                    
                    # Get account keys and find wallets
                    account_keys = message.get('accountKeys', [])
                    print(f"\n👥 ACCOUNTS INVOLVED ({len(account_keys)} total):")
                    
                    wallet_accounts = []
                    for i, account in enumerate(account_keys[:10]):  # Show first 10
                        # Skip system accounts
                        if account not in [
                            '11111111111111111111111111111111',
                            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                            'So11111111111111111111111111111111111111112',
                            'ComputeBudget111111111111111111111111111111',
                            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',
                        ]:
                            wallet_accounts.append((i, account))
                            print(f"   [{i}] {account}")
                    
                    if len(account_keys) > 10:
                        print(f"   ... and {len(account_keys) - 10} more accounts")
                    
                    # Analyze SOL balance changes
                    print(f"\n💰 SOL BALANCE ANALYSIS:")
                    pre_balances = meta.get('preBalances', [])
                    post_balances = meta.get('postBalances', [])
                    
                    sol_changes = []
                    for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                        if i < len(account_keys):
                            delta = post - pre
                            if delta != 0:  # Only show accounts with balance changes
                                sol_changes.append({
                                    'account_index': i,
                                    'account': account_keys[i],
                                    'pre_balance': pre / 1e9,
                                    'post_balance': post / 1e9,
                                    'delta': delta / 1e9
                                })
                    
                    for change in sol_changes:
                        status = "📈" if change['delta'] > 0 else "📉"
                        print(f"   {status} [{change['account_index']}] {change['account'][:8]}...")
                        print(f"      Pre:  {change['pre_balance']:.6f} SOL")
                        print(f"      Post: {change['post_balance']:.6f} SOL")
                        print(f"      Δ:    {change['delta']:+.6f} SOL")
                    
                    # Analyze token balance changes
                    print(f"\n🪙 TOKEN BALANCE ANALYSIS:")
                    pre_token_balances = meta.get('preTokenBalances', [])
                    post_token_balances = meta.get('postTokenBalances', [])
                    
                    # Create token change mapping
                    token_changes = {}
                    
                    # Process pre-balances
                    for balance in pre_token_balances:
                        owner = balance.get('owner')
                        mint = balance.get('mint')
                        amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                        decimals = balance.get('uiTokenAmount', {}).get('decimals', 0)
                        
                        key = f"{owner}:{mint}"
                        token_changes[key] = {
                            'owner': owner,
                            'mint': mint,
                            'decimals': decimals,
                            'pre_amount': amount,
                            'post_amount': 0,
                            'pre_ui': amount / (10 ** decimals) if decimals > 0 else amount,
                            'post_ui': 0
                        }
                    
                    # Process post-balances
                    for balance in post_token_balances:
                        owner = balance.get('owner')
                        mint = balance.get('mint')
                        amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                        decimals = balance.get('uiTokenAmount', {}).get('decimals', 0)
                        
                        key = f"{owner}:{mint}"
                        if key in token_changes:
                            token_changes[key]['post_amount'] = amount
                            token_changes[key]['post_ui'] = amount / (10 ** decimals) if decimals > 0 else amount
                        else:
                            token_changes[key] = {
                                'owner': owner,
                                'mint': mint,
                                'decimals': decimals,
                                'pre_amount': 0,
                                'post_amount': amount,
                                'pre_ui': 0,
                                'post_ui': amount / (10 ** decimals) if decimals > 0 else amount
                            }
                    
                    # Show significant token changes
                    significant_changes = []
                    for key, change in token_changes.items():
                        delta = change['post_amount'] - change['pre_amount']
                        if delta != 0:
                            change['delta'] = delta
                            change['delta_ui'] = change['post_ui'] - change['pre_ui']
                            significant_changes.append(change)
                    
                    for change in significant_changes:
                        status = "📈" if change['delta'] > 0 else "📉"
                        print(f"   {status} {change['owner'][:8]}... | {change['mint'][:8]}...")
                        print(f"      Pre:  {change['pre_ui']:,.6f}")
                        print(f"      Post: {change['post_ui']:,.6f}")
                        print(f"      Δ:    {change['delta_ui']:+,.6f}")
                    
                    # PERFORM BUY/SELL ANALYSIS for each wallet
                    print(f"\n🎯 BUY/SELL DETECTION ANALYSIS:")
                    print("=" * 50)
                    
                    detected_trades = []
                    
                    # Analyze each wallet that had balance changes
                    analyzed_wallets = set()
                    
                    # From SOL changes
                    for change in sol_changes:
                        wallet = change['account']
                        if wallet not in analyzed_wallets:
                            analyzed_wallets.add(wallet)
                            trade_result = self._analyze_wallet_trade(wallet, sol_changes, significant_changes, change['account_index'])
                            if trade_result:
                                detected_trades.append(trade_result)
                    
                    # From token changes
                    for change in significant_changes:
                        wallet = change['owner']
                        if wallet not in analyzed_wallets:
                            analyzed_wallets.add(wallet)
                            # Find wallet index
                            wallet_index = None
                            for i, account in enumerate(account_keys):
                                if account == wallet:
                                    wallet_index = i
                                    break
                            
                            if wallet_index is not None:
                                trade_result = self._analyze_wallet_trade(wallet, sol_changes, significant_changes, wallet_index)
                                if trade_result:
                                    detected_trades.append(trade_result)
                    
                    # Summary
                    print(f"\n📋 ANALYSIS SUMMARY:")
                    print(f"   Total wallets analyzed: {len(analyzed_wallets)}")
                    print(f"   Trades detected: {len(detected_trades)}")
                    
                    for i, trade in enumerate(detected_trades):
                        print(f"\n   🎯 TRADE {i+1}:")
                        print(f"      Wallet: {trade['wallet'][:8]}...")
                        print(f"      Action: {trade['action'].upper()}")
                        print(f"      Confidence: {trade['confidence']}")
                        print(f"      SOL change: {trade['sol_delta']:+.6f} SOL")
                        print(f"      Tokens gained: {trade['tokens_gained']}")
                        print(f"      Tokens lost: {trade['tokens_lost']}")
                        print(f"      Reasoning: {trade['reasoning']}")
                    
                    return {
                        'signature': signature,
                        'success': meta.get('err') is None,
                        'sol_changes': sol_changes,
                        'token_changes': significant_changes,
                        'detected_trades': detected_trades,
                        'accounts': account_keys
                    }
                    
        except Exception as e:
            print(f"❌ Error analyzing transaction: {e}")
            return None
    
    def _analyze_wallet_trade(self, wallet: str, sol_changes: list, token_changes: list, wallet_index: int):
        """Analyze if a specific wallet performed a buy/sell trade"""
        
        print(f"\n🔍 Analyzing wallet: {wallet[:8]}... (index {wallet_index})")
        
        # Find SOL change for this wallet
        sol_delta = 0
        for change in sol_changes:
            if change['account'] == wallet:
                sol_delta = change['delta']
                break
        
        # Find token changes for this wallet
        wallet_token_changes = [change for change in token_changes if change['owner'] == wallet]
        
        tokens_gained = 0
        tokens_lost = 0
        gained_details = []
        lost_details = []
        
        for change in wallet_token_changes:
            if change['delta'] > 0:
                tokens_gained += 1
                gained_details.append({
                    'mint': change['mint'],
                    'amount': change['delta_ui']
                })
            elif change['delta'] < 0:
                tokens_lost += 1
                lost_details.append({
                    'mint': change['mint'],
                    'amount': abs(change['delta_ui'])
                })
        
        print(f"   💰 SOL delta: {sol_delta:+.6f} SOL")
        print(f"   🪙 Tokens gained: {tokens_gained}, Tokens lost: {tokens_lost}")
        
        if gained_details:
            print(f"   📈 Gained tokens:")
            for detail in gained_details:
                print(f"      + {detail['amount']:,.6f} of {detail['mint'][:8]}...")
        
        if lost_details:
            print(f"   📉 Lost tokens:")
            for detail in lost_details:
                print(f"      - {detail['amount']:,.6f} of {detail['mint'][:8]}...")
        
        # Apply detection logic
        action = None
        confidence = "LOW"
        reasoning = "No clear trading pattern"
        
        if sol_delta < 0 and tokens_gained > 0:
            action = "BUY"
            confidence = "HIGH"
            reasoning = "SOL decreased, tokens gained - classic BUY pattern"
        elif sol_delta > 0 and tokens_lost > 0:
            action = "SELL"
            confidence = "HIGH"
            reasoning = "SOL increased, tokens lost - classic SELL pattern"
        elif tokens_gained > 0 and tokens_lost == 0 and abs(sol_delta) < 0.001:
            action = "BUY"
            confidence = "MEDIUM"
            reasoning = "Only gained tokens, minimal SOL change - likely airdrop or BUY"
        elif tokens_lost > 0 and tokens_gained == 0 and abs(sol_delta) < 0.001:
            action = "SELL"
            confidence = "MEDIUM"
            reasoning = "Only lost tokens, minimal SOL change - likely SELL or transfer"
        elif tokens_gained > 0 and tokens_lost > 0:
            if sol_delta < 0:
                action = "BUY"
                confidence = "MEDIUM"
                reasoning = "Complex swap with net SOL decrease - likely BUY"
            elif sol_delta > 0:
                action = "SELL"
                confidence = "MEDIUM"
                reasoning = "Complex swap with net SOL increase - likely SELL"
            else:
                action = "SWAP"
                confidence = "MEDIUM"
                reasoning = "Token-to-token swap with no net SOL change"
        
        if action:
            print(f"   🎯 DETECTED: {action} ({confidence} confidence)")
            print(f"   💭 Reasoning: {reasoning}")
            
            return {
                'wallet': wallet,
                'wallet_index': wallet_index,
                'action': action,
                'confidence': confidence,
                'reasoning': reasoning,
                'sol_delta': sol_delta,
                'tokens_gained': tokens_gained,
                'tokens_lost': tokens_lost,
                'gained_details': gained_details,
                'lost_details': lost_details
            }
        else:
            print(f"   ❓ No clear trade detected")
            return None

async def main():
    """Main analysis function"""
    
    # Transaction to analyze - USER PROVIDED
    signature = "3pH89QetQ2BhiWMjX2a5a9kEcngU3UGDMLMBVX7muWrBrnAGD51eHPiPJ6dCEYAUJpWp1YsPDHEqGcqUonRqt1NJ"
    
    analyzer = SingleTransactionAnalyzer()
    result = await analyzer.analyze_transaction(signature)
    
    if result:
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"🔗 View on Solscan: https://solscan.io/tx/{signature}")
    else:
        print(f"\n❌ Analysis failed")

if __name__ == "__main__":
    asyncio.run(main())
