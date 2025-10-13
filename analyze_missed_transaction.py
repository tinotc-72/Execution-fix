#!/usr/bin/env python3

import asyncio
import json
import requests
from datetime import datetime

async def analyze_missed_transaction():
    signature = "KD7EAroHaUxiJitKxNs7hFRAtrcJQBaMK829bY3xFVzchaTwEakLxKfw5Z7HLLP9u6HQGrXbJUventPNWYtkefx"
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"🔍 ANALYZING MISSED TRANSACTION")
    print("=" * 80)
    print(f"Signature: {signature}")
    print()
    
    # Your monitored wallets from config.py
    monitored_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj", 
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
        "7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN6X1oHXkuqvg",
        "3D49QorJyNaL9HPe4VPTLqpezZZGP5TXKYaG1gJFJXFG",
        "CuieVDEDtLo7FypA9SbLM9saXFdb1dsshEkyErMqkRQq"
    ]
    
    # DEX program mapping
    dex_programs = {
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
        "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Whirlpool",
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca Legacy"
    }
    
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
        
        response = requests.post(helius_url, json=payload)
        data = response.json()
        
        if "result" in data and data["result"]:
            tx = data["result"]
            
            print("📊 TRANSACTION DETAILS:")
            print(f"   Slot: {tx.get('slot', 'unknown')}")
            
            if tx.get("blockTime"):
                tx_time = datetime.fromtimestamp(tx["blockTime"])
                print(f"   Time: {tx_time}")
                print(f"   Age: {datetime.now() - tx_time}")
            
            success = not tx.get("meta", {}).get("err")
            print(f"   Success: {'✅' if success else '❌'}")
            
            # Get accounts involved
            account_keys = tx.get("transaction", {}).get("message", {}).get("accountKeys", [])
            print(f"   Accounts: {len(account_keys)} total")
            
            if account_keys:
                signer = account_keys[0]
                print(f"   Signer: {signer}")
                
                # Check if signer is in monitored wallets
                is_monitored = signer in monitored_wallets
                print(f"   Monitored: {'✅ YES' if is_monitored else '❌ NO'}")
                
                if not is_monitored:
                    print(f"   🚨 REASON #1: Wallet {signer} is NOT in your monitored list!")
                    print(f"      You need to add this wallet to MONITORED_WALLETS in config.py")
                    return
            
            # Check DEX programs used
            instructions = tx.get("transaction", {}).get("message", {}).get("instructions", [])
            programs_used = set()
            
            for instruction in instructions:
                program_index = instruction.get("programIdIndex")
                if program_index is not None and program_index < len(account_keys):
                    program_id = account_keys[program_index]
                    programs_used.add(program_id)
            
            print(f"   Programs Used:")
            dex_found = False
            for program in programs_used:
                dex_name = dex_programs.get(program, f"Unknown ({program})")
                print(f"     {program} → {dex_name}")
                if program in dex_programs:
                    dex_found = True
            
            if not dex_found:
                print(f"   🚨 REASON #2: No recognized DEX programs found!")
                print(f"      Your bot might not recognize this DEX")
            
            # Check logs for trading activity
            logs = tx.get("meta", {}).get("logMessages", [])
            trading_keywords = ["swap", "trade", "buy", "sell", "transfer"]
            trading_logs = [log for log in logs if any(kw in log.lower() for kw in trading_keywords)]
            
            print(f"   Logs: {len(logs)} total, {len(trading_logs)} trading-related")
            
            if trading_logs:
                print(f"   Sample Trading Logs:")
                for log in trading_logs[:2]:
                    print(f"     {log[:80]}{'...' if len(log) > 80 else ''}")
            
            # Check balance changes (token transfers)
            pre_balances = tx.get("meta", {}).get("preTokenBalances", [])
            post_balances = tx.get("meta", {}).get("postTokenBalances", [])
            
            print(f"   Token Changes: {len(pre_balances)} pre → {len(post_balances)} post")
            
            if pre_balances or post_balances:
                print(f"   ✅ Token activity detected - this looks like a trade!")
            else:
                print(f"   🚨 REASON #3: No token balance changes detected")
            
            # Summary
            print()
            print("🎯 DIAGNOSIS:")
            if is_monitored and dex_found and (pre_balances or post_balances):
                print("   ✅ Transaction should have been copied!")
                print("   🔍 Possible issues:")
                print("     • Bot wasn't running at transaction time")
                print("     • WebSocket connection dropped") 
                print("     • Transaction analysis failed")
                print("     • All DEX executors failed to execute")
            elif not is_monitored:
                print("   ❌ Transaction wallet NOT monitored - this is why it wasn't copied")
            elif not dex_found:
                print("   ❌ DEX not recognized - this is why it wasn't copied") 
            else:
                print("   ❌ Not identified as trading transaction")
                
        else:
            error = data.get("error", "Unknown error")
            print(f"❌ Failed to fetch transaction: {error}")
            
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_missed_transaction())
