#!/usr/bin/env python3

import httpx
import json

def get_transaction_accounts(signature):
    """Get exact account structure from a transaction"""
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"🔍 Getting transaction details for: {signature}")
    
    # Get detailed transaction info
    resp = httpx.post(helius_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
    })
    
    if resp.status_code == 200:
        result = resp.json()
        if "result" in result and result["result"]:
            tx = result["result"]
            message = tx.get("transaction", {}).get("message", {})
            account_keys = message.get("accountKeys", [])
            
            # Handle different response formats
            if account_keys and isinstance(account_keys[0], dict):
                account_keys = [k["pubkey"] for k in account_keys]
                
            instructions = message.get("instructions", [])
            
            print(f"\n📋 All accounts in transaction ({len(account_keys)} total):")
            for i, acc in enumerate(account_keys):
                print(f"  {i:2d}: {acc}")
            
            # Look for Pump.fun instructions
            for ix_idx, ix in enumerate(instructions):
                prog_id = ix.get("programId")
                if prog_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    accounts = ix.get("accounts", [])
                    print(f"\n🎯 Pump.fun instruction {ix_idx}:")
                    print(f"📋 Uses {len(accounts)} accounts:")
                    for j, acc_idx in enumerate(accounts):
                        if acc_idx < len(account_keys):
                            print(f"  {j:2d}: {account_keys[acc_idx]}")
                        else:
                            print(f"  {j:2d}: [INDEX {acc_idx} OUT OF RANGE]")
            
            return account_keys
    
    return None

if __name__ == "__main__":
    # Successful transaction 
    success_sig = "2LuKV1tecqH6RG4tbGVZpDM4n3tHUpFxpuz7gVBsbPTzDee3RRqoicZSNuJfYtLna94GknCSuHWbBe73pGifhoYF"
    accounts = get_transaction_accounts(success_sig)