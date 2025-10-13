#!/usr/bin/env python3

import httpx
import json

def get_fee_config_address():
    """Get the exact fee config address"""
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    # Successful transaction 
    signature = "2LuKV1tecqH6RG4tbGVZpDM4n3tHUpFxpuz7gVBsbPTzDee3RRqoicZSNuJfYtLna94GknCSuHWbBe73pGifhoYF"
    
    resp = httpx.post(helius_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    })
    
    if resp.status_code == 200:
        result = resp.json()
        if "result" in result and result["result"]:
            tx = result["result"]
            message = tx.get("transaction", {}).get("message", {})
            account_keys = message.get("accountKeys", [])
            
            # Check Message[14] specifically
            if len(account_keys) > 14:
                addr = account_keys[14]
                print(f"Message[14] address: '{addr}'")
                print(f"Address length: {len(addr)}")
                print(f"Address characters: {[c for c in addr]}")
                
                # Test each character
                for i, c in enumerate(addr):
                    print(f"  {i:2d}: '{c}' (ord: {ord(c)})")

if __name__ == "__main__":
    get_fee_config_address()