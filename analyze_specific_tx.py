#!/usr/bin/env python3
"""
Analyze specific transaction to understand buy vs sell patterns
"""

import requests
import json
from env_keys import EnvKeys

def analyze_transaction(signature):
    """Analyze a specific transaction to understand its structure"""
    
    print(f"🔍 Analyzing transaction: {signature[:16]}...")
    
    # Load RPC URL
    kz = EnvKeys()
    url = kz.HELIUS_RPC_URL
    
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
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if "result" in data and data["result"]:
            result = data["result"]
            meta = result.get("meta", {})
            logs = meta.get("logMessages", [])
            
            print(f"\n📊 TRANSACTION ANALYSIS:")
            print(f"   Signature: {signature}")
            print(f"   Log messages: {len(logs)}")
            
            # Analyze logs line by line
            print(f"\n📝 ALL LOG MESSAGES:")
            for i, log in enumerate(logs):
                print(f"   [{i+1:2d}] {log}")
            
            # Look for specific patterns
            print(f"\n🔍 PATTERN ANALYSIS:")
            
            # Check for buy/sell indicators
            buy_patterns = []
            sell_patterns = []
            
            for i, log in enumerate(logs):
                log_lower = log.lower()
                
                # Buy indicators
                if any(word in log_lower for word in ['buy', 'purchase', 'in']):
                    buy_patterns.append(f"Line {i+1}: {log}")
                
                # Sell indicators  
                if any(word in log_lower for word in ['sell', 'sold', 'out']):
                    sell_patterns.append(f"Line {i+1}: {log}")
            
            print(f"   🟢 BUY patterns found: {len(buy_patterns)}")
            for pattern in buy_patterns:
                print(f"      {pattern}")
                
            print(f"   🔴 SELL patterns found: {len(sell_patterns)}")
            for pattern in sell_patterns:
                print(f"      {pattern}")
            
            # Analyze token transfers
            print(f"\n💰 TOKEN TRANSFER ANALYSIS:")
            transfer_logs = [log for log in logs if 'Transfer' in log]
            print(f"   Transfer logs found: {len(transfer_logs)}")
            
            for i, transfer in enumerate(transfer_logs):
                print(f"   [{i+1}] {transfer}")
            
            # Check pre/post token balances
            pre_balances = meta.get("preTokenBalances", [])
            post_balances = meta.get("postTokenBalances", [])
            
            print(f"\n📈 TOKEN BALANCE CHANGES:")
            print(f"   Pre-balances: {len(pre_balances)}")
            print(f"   Post-balances: {len(post_balances)}")
            
            # Compare balances to determine buy/sell
            for pre in pre_balances:
                account = pre.get("accountIndex")
                mint = pre.get("mint")
                pre_amount = float(pre.get("uiTokenAmount", {}).get("uiAmount", 0))
                
                # Find corresponding post balance
                post = next((p for p in post_balances if p.get("accountIndex") == account), None)
                if post:
                    post_amount = float(post.get("uiTokenAmount", {}).get("uiAmount", 0))
                    change = post_amount - pre_amount
                    
                    if change > 0:
                        print(f"   🟢 +{change:.6f} {mint[:8]}... (RECEIVED = potential BUY)")
                    elif change < 0:
                        print(f"   🔴 {change:.6f} {mint[:8]}... (SENT = potential SELL)")
                    else:
                        print(f"   ⚪ No change {mint[:8]}...")
            
            return logs, pre_balances, post_balances
            
        else:
            print(f"❌ Transaction not found or error: {data}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        return None, None, None

if __name__ == "__main__":
    # Analyze the specific transaction you mentioned as a sell
    sell_signature = "WARi9zjewz6eQxPajSpr8kGEDLw52foAweghWZ8yx5KgJmuUAUY3Mc7NLnFyGiVTHXc22qKimxUWXZ4BAuB27Rs"
    
    print("🧪 TRANSACTION BUY/SELL ANALYSIS")
    print("=" * 60)
    print("🎯 Analyzing a transaction you identified as a SELL")
    print("   to understand the correct detection patterns")
    print("=" * 60)
    
    analyze_transaction(sell_signature)
