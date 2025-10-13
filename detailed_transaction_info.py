#!/usr/bin/env python3
"""
Get detailed info about a successful transaction
"""

import requests
import json
from datetime import datetime

def analyze_failed_transaction():
    """Get detailed information about what the transaction did"""
    
    signature = "oZMfyPibSGA6nhwAmj6J91DixsVZYgLUbdRW8nSomJsCbJUjNf41TCZX6KjiStjaWY5QxtckbCW6oxGpyuBSo1F"
    
    print(f"❌ ANALYZING FAILED TRANSACTION")
    print(f"📋 Signature: {signature}")
    print("=" * 80)
    
    try:
        # Use Helius RPC URL directly
        rpc_url = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
        
        # Fetch with parsed format for better details
        response = requests.post(rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "jsonParsed",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed"
                }
            ]
        })
        
        data = response.json()
        
        if 'result' not in data or not data['result']:
            print("❌ Transaction not found")
            return
        
        tx = data['result']
        meta = tx.get('meta', {})
        
        print("📊 TRANSACTION DETAILS:")
        print(f"   Status: {'✅ SUCCESS' if not meta.get('err') else '❌ FAILED'}")
        print(f"   Slot: {tx.get('slot')}")
        print(f"   Block Time: {datetime.fromtimestamp(tx.get('blockTime', 0))}")
        print(f"   Fee: {meta.get('fee', 0)} lamports")
        print(f"   Compute Units: {meta.get('computeUnitsConsumed', 0)}")
        print()
        
        # Show balance changes
        print("💰 BALANCE CHANGES:")
        if 'preBalances' in meta and 'postBalances' in meta:
            accounts = tx['transaction']['message']['accountKeys']
            for i, (pre, post) in enumerate(zip(meta['preBalances'], meta['postBalances'])):
                if pre != post:
                    change = post - pre
                    pubkey = accounts[i]['pubkey'] if isinstance(accounts[i], dict) else accounts[i]
                    print(f"   {pubkey[:20]}...: {change:+,} lamports")
        print()
        
        # Show instructions
        print("📝 INSTRUCTIONS:")
        instructions = tx['transaction']['message']['instructions']
        for i, inst in enumerate(instructions):
            program_id = inst.get('programId', 'Unknown')
            parsed = inst.get('parsed', {})
            
            print(f"   {i+1}. Program: {program_id}")
            
            if parsed:
                inst_type = parsed.get('type', 'Unknown')
                info = parsed.get('info', {})
                print(f"      Type: {inst_type}")
                
                # Show key details based on instruction type
                if 'amount' in info:
                    print(f"      Amount: {info['amount']}")
                if 'source' in info:
                    print(f"      Source: {info['source'][:20]}...")
                if 'destination' in info:
                    print(f"      Destination: {info['destination'][:20]}...")
                if 'mint' in info:
                    print(f"      Mint: {info['mint'][:20]}...")
            
            print()
        
        # Show log messages if any
        if 'logMessages' in meta:
            print("📋 LOG MESSAGES:")
            for log in meta['logMessages'][:10]:  # Show first 10
                print(f"   {log}")
            if len(meta['logMessages']) > 10:
                print(f"   ... and {len(meta['logMessages']) - 10} more")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_failed_transaction()
