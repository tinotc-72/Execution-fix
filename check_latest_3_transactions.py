#!/usr/bin/env python3
"""
Check the last 3 transactions to see if IllegalOwner errors persist
"""

import requests
import json
from datetime import datetime

def check_latest_3_transactions():
    print("🔍 CHECKING LATEST 3 TRANSACTIONS")
    print("=" * 60)
    
    wallet_address = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    rpc_url = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"👤 Wallet: {wallet_address}")
    print(f"📡 Fetching latest 3 transactions...")
    print()
    
    # Get recent transaction signatures
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {"limit": 3, "commitment": "confirmed"}
        ]
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=15)
        data = response.json()
        
        if "result" not in data or not data["result"]:
            print("❌ No recent transactions found")
            return
        
        transactions = data["result"]
        print(f"✅ Found {len(transactions)} recent transactions")
        print()
        
        for i, tx in enumerate(transactions, 1):
            signature = tx["signature"]
            timestamp = datetime.fromtimestamp(tx["blockTime"]).strftime("%Y-%m-%d %H:%M:%S")
            error = tx.get("err")
            
            print(f"📋 TRANSACTION {i}/3:")
            print(f"   Signature: {signature}")
            print(f"   Time: {timestamp}")
            print(f"   Status: {'❌ FAILED' if error else '✅ SUCCESS'}")
            
            if error:
                print(f"   Error: {error}")
                
                # Check if it's the same IllegalOwner error
                if isinstance(error, dict) and "InstructionError" in error:
                    instruction_error = error["InstructionError"]
                    if len(instruction_error) > 1 and instruction_error[1] == "IllegalOwner":
                        print(f"   🔍 ANALYSIS: Same IllegalOwner error detected!")
                        print(f"   🚨 This means the ATA existence checking is NOT working")
            print()
        
        # Analysis
        failed_count = sum(1 for tx in transactions if tx.get("err"))
        success_count = len(transactions) - failed_count
        
        print("📊 RECENT ACTIVITY SUMMARY:")
        print(f"   Total: {len(transactions)}")
        print(f"   Success: {success_count}")
        print(f"   Failed: {failed_count}")
        
        if failed_count > 0:
            print()
            print("🚨 PROBLEM PERSISTS!")
            print("   IllegalOwner errors are still happening")
            print("   This suggests:")
            print("   • Bot restart didn't load the fixed code")
            print("   • There's another ATA creation path we missed")
            print("   • The fixes aren't being used properly")
            print()
            print("🔧 NEXT STEPS:")
            print("   1. Check if bot is actually using the fixed files")
            print("   2. Look for other ATA creation logic")
            print("   3. Add more debugging to trace the issue")
        else:
            print()
            print("✅ GOOD NEWS!")
            print("   Recent transactions are successful")
            print("   The fixes appear to be working")
            
    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")

if __name__ == "__main__":
    check_latest_3_transactions()
