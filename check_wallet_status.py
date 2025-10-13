#!/usr/bin/env python3
"""
Check wallet balance and fix transaction issues
"""

import requests
import json

def check_wallet_status():
    """Check your wallet's current status"""
    
    print("🔍 CHECKING YOUR WALLET STATUS")
    print("="*50)
    
    your_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    try:
        # Check SOL balance
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [your_wallet]
        }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('result'):
            balance_lamports = data['result']['value']
            balance_sol = balance_lamports / 1_000_000_000
            
            print(f"💰 SOL BALANCE: {balance_sol:.6f} SOL")
            
            if balance_sol < 0.01:
                print("🚨 CRITICAL: Very low SOL balance!")
                print("   Need at least 0.1 SOL for trading + fees")
            elif balance_sol < 0.1:
                print("⚠️  WARNING: Low SOL balance")
                print("   Recommend at least 0.5 SOL for active trading")
            else:
                print("✅ SOL balance looks adequate")
                
        else:
            print("❌ Could not fetch balance")
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
    
    # Check recent failed transactions
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                your_wallet,
                {"limit": 5}
            ]
        }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('result'):
            recent_txs = data['result']
            print(f"\n📊 LAST 5 TRANSACTIONS:")
            
            for i, tx in enumerate(recent_txs, 1):
                signature = tx['signature']
                err = tx.get('err')
                block_time = tx.get('blockTime', 0)
                
                if err:
                    print(f"   {i}. ❌ {signature[:16]}... - FAILED: {err}")
                else:
                    print(f"   {i}. ✅ {signature[:16]}... - SUCCESS")
                    
    except Exception as e:
        print(f"❌ Error checking transactions: {e}")
    
    print("\n🔧 RECOMMENDED FIXES:")
    print("1. 💰 Ensure wallet has at least 0.5 SOL")
    print("2. 🎯 Increase slippage tolerance to 15-20%")
    print("3. ⛽ Increase priority fees to 500,000 micro-lamports")
    print("4. ⏱️ Add delays between transactions")
    print("5. 🔄 Implement proper retry logic")

if __name__ == "__main__":
    check_wallet_status()
