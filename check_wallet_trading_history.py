#!/usr/bin/env python3
"""
Official wallet trading history checker
Based on Helius Transaction API documentation
"""

import requests
import json
from env_keys import RPC_URL

def check_wallet_history(wallet_address):
    """Check recent transactions for a wallet using official Helius API"""
    
    print(f"\n🔍 Checking trading history for: {wallet_address[:8]}...")
    
    # Official Helius API endpoint for transaction history
    url = RPC_URL
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {
                "limit": 20,  # Get last 20 transactions
                "commitment": "confirmed"
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if "result" in data:
            signatures = data["result"]
            print(f"   📊 Found {len(signatures)} recent transactions")
            
            # Check each transaction for trading activity
            trading_count = 0
            for i, sig_info in enumerate(signatures[:10]):  # Check first 10
                signature = sig_info["signature"]
                
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
                
                tx_response = requests.post(url, json=tx_payload, timeout=10)
                tx_data = tx_response.json()
                
                if "result" in tx_data and tx_data["result"]:
                    meta = tx_data["result"].get("meta", {})
                    logs = meta.get("logMessages", [])
                    
                    # Check for DEX programs in logs
                    dex_programs = []
                    for log in logs:
                        if "Program" in log and "invoke" in log:
                            # Extract program ID from log
                            parts = log.split()
                            if len(parts) >= 2:
                                program_id = parts[1]
                                
                                # Check official DEX program IDs
                                if program_id in [
                                    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",  # Jupiter V4
                                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter V6
                                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium AMM
                                    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # Raydium Router
                                    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",  # Raydium CLMM
                                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # Pump.fun
                                    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Orca V1
                                    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",   # Orca Whirlpool
                                ]:
                                    dex_programs.append(program_id)
                    
                    if dex_programs:
                        trading_count += 1
                        print(f"   🎯 [{i+1}] TRADING TRANSACTION: {signature[:16]}...")
                        print(f"       DEX: {dex_programs[0][:16]}...")
                        
                        # Look for token transfers in logs
                        transfers = []
                        for log in logs:
                            if "Transfer" in log:
                                transfers.append(log)
                        
                        if transfers:
                            print(f"       📊 Token transfers: {len(transfers)}")
                    else:
                        print(f"   📝 [{i+1}] Non-trading: {signature[:16]}...")
            
            print(f"   🎯 Trading transactions found: {trading_count}/10")
            return trading_count > 0
            
        else:
            print(f"   ❌ Error: {data}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking history: {e}")
        return False

def main():
    """Check trading history for target wallets"""
    
    print("🧪 OFFICIAL Wallet Trading History Check")
    print("=" * 50)
    print("📋 Using official Helius Transaction API")
    print("🎯 Checking for recent DEX trading activity")
    print("=" * 50)
    
    # Target wallets from your config
    wallets = [
        "suqh5sHtLjGXaQJg7RBgPBZYWaQcDgp6wbKgzA1TgQ5r",
        "DfMxre4cQ4q89q8v6fTfGGP1hFd6i2YS1sP8p6zB9U4n"
    ]
    
    active_traders = []
    
    for wallet in wallets:
        has_trading = check_wallet_history(wallet)
        if has_trading:
            active_traders.append(wallet)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total wallets checked: {len(wallets)}")
    print(f"   Active traders found: {len(active_traders)}")
    
    if active_traders:
        print(f"   🎯 Active trading wallets:")
        for wallet in active_traders:
            print(f"      - {wallet}")
        print(f"\n✅ Your WebSocket bot should detect trades from these wallets!")
    else:
        print(f"   ℹ️ No recent trading activity detected")
        print(f"   💡 Wallets may be doing setup/initialization only")
        print(f"   🕐 Consider checking during active trading hours")

if __name__ == "__main__":
    main()
