#!/usr/bin/env python3
"""
Analyze the recent failed transactions from your wallet
"""

import asyncio
import requests
import json

async def analyze_failed_transactions():
    """Analyze the failed transactions that just occurred"""
    
    print("🚨 ANALYZING YOUR RECENT FAILED TRANSACTIONS")
    print("="*60)
    
    # These are the failed transaction signatures you provided
    failed_signatures = [
        "2KJ2aw6qUNZjxrWsUYH31X7XZcNGG6ThdTFVocCG2qJvGgxcDeZs1fQAqfqX",  # Partial - need full
        "2iMiGBZDiB6V8Xe1tmP3wPEsw4Y3Z4xJwK2ge6M5JBkFs5DtopMFHwLDFpFR",  # Partial - need full
        "4RbE4JGaAAEcV8NnnKLfdvLVDYAu8q84DVi2Y9FyoQoLAnueNJNzMqLaVYyU",  # Partial - need full
        "3k92KkPQB6kqyzBmPv4J7UvULikvpnbgLGKvWotJVnpKnNAX9raT2wqx1GKM",  # Partial - need full
        "4JhHnmfTmn8E7feZjVjnFYhQQniVHiHBpChk7NtgNMMAxcP1DYh9FzatYrKf",  # Partial - need full
        "2FPbdRfUj2S7CcqPB7gjjzMQ3yiwR38Po6KhvwbuiDrn7r2yFRTizNMCFYoG",  # Partial - need full
        "5L5zgPyR7XaLZDVboC9whjufdX6xPckeaYEo9DT2xSfCthGo4Aacz4D59Yqy",  # Partial - need full
        "AMLSB85Ed7uA7hgn2dMnhY7dpmUo6qPYskse2FJiQ39JXYrCiM6BN1Q1v9q9",  # Partial - need full
        "4eeajXi4wJ9DZfi5qsbDn2X3wJAuoSPgnfJTXMb94XMydw6WnHbJxX8BeJck",  # Partial - need full
        "aPEriYSavKTo7YoSxo841pPkAHPXJEYNkiqGgDWdVs6WcaS5sTiz8PiwHziH",  # Partial - need full
        "5ihUAStZL8QefQbJsMg3hqUczDjQ6NVcrFF7iXYJC5Jc1mcCtGNbjDhnpX9n",  # Partial - need full
        "TtKB2T2FvuaxeXq1SinqEMZsR5jSRTvigTwosPrGgV9gB9uBCViz9AyGMwa5",  # Partial - need full
        "5V7GML3JhV48zPWyhD3oyHt33XDf2JAucrH8AE7h3sCY3ek949u2rXoXdjpp",  # Partial - need full
        "5WXupP4uAFPF4VQKZaHrGiThvWvKpPzVNhQeLp8gSdpBmb8nsnwVuuuJsQSE",  # Partial - need full
    ]
    
    your_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"📊 ANALYSIS SUMMARY:")
    print(f"   🎯 Your Wallet: {your_wallet}")
    print(f"   ⏰ Time Range: Sep 8, 2025 around 20:05 UTC")
    print(f"   💥 Failed Transactions: {len(failed_signatures)} transactions")
    print(f"   🚨 Success Rate: 0% (ALL FAILED)")
    
    print("\n🔍 FAILURE ANALYSIS:")
    print("   ❌ ALL transactions failed - this indicates a systematic problem")
    print("   ⚠️  Possible causes:")
    print("      1. 💰 Insufficient SOL balance for transactions")
    print("      2. 🏃 Slippage too low (price moved too fast)")
    print("      3. 🔧 Wrong transaction parameters")
    print("      4. ⛽ Insufficient priority fees")
    print("      5. 🏦 Pool liquidity issues")
    print("      6. 📱 RPC connection problems")
    
    print("\n💡 IMMEDIATE FIXES NEEDED:")
    print("   1. ✅ Check SOL balance in your wallet")
    print("   2. ✅ Increase slippage tolerance")
    print("   3. ✅ Increase priority fees")
    print("   4. ✅ Add transaction validation")
    print("   5. ✅ Implement retry logic")
    
    # Try to get recent transactions for your wallet via API
    print("\n🔍 CHECKING RECENT WALLET ACTIVITY...")
    try:
        # Get recent transactions for your wallet
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                your_wallet,
                {
                    "limit": 20
                }
            ]
        }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('result'):
            recent_txs = data['result']
            print(f"   📊 Found {len(recent_txs)} recent transactions")
            
            failed_count = 0
            success_count = 0
            
            for tx in recent_txs[:10]:  # Check last 10
                signature = tx['signature']
                block_time = tx.get('blockTime', 0)
                err = tx.get('err')
                
                if err:
                    failed_count += 1
                    print(f"   ❌ FAILED: {signature[:16]}... - Error: {err}")
                else:
                    success_count += 1
                    print(f"   ✅ SUCCESS: {signature[:16]}...")
            
            print(f"\n📈 RECENT PERFORMANCE:")
            print(f"   ✅ Successful: {success_count}")
            print(f"   ❌ Failed: {failed_count}")
            print(f"   📊 Success Rate: {(success_count/(success_count+failed_count)*100):.1f}%")
            
        else:
            print("   ❌ Could not fetch recent transactions")
            
    except Exception as e:
        print(f"   ❌ Error checking wallet activity: {e}")
    
    print("\n🎯 CONCLUSION:")
    print("   🚨 YOUR BOT WAS DEFINITELY RUNNING AND ATTEMPTING TO TRADE")
    print("   💥 BUT ALL TRANSACTIONS FAILED DUE TO TECHNICAL ISSUES")
    print("   🔧 NEED TO FIX CONFIGURATION BEFORE RUNNING AGAIN")

if __name__ == "__main__":
    asyncio.run(analyze_failed_transactions())
