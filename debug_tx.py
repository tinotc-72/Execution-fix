#!/usr/bin/env python3

import asyncio
import json
import requests

async def debug_transaction():
    """Debug the transaction to see what programs are actually used"""
    
    signature = "3fmwcJWcVoE7qtdFJSz9UQhpXjJohbGa3H79aqLzXhPHJhArxU2rBHZewmEKhdVD7ekSTcheABJzpov1iVgivAzi"
    
    url = 'https://mainnet.helius-rpc.com/v0'
    params = {'api-key': '7277139c-ff2c-4257-ad06-2db6aa16c315'}

    payload = {
        'id': 1,
        'jsonrpc': '2.0',
        'method': 'getTransaction',
        'params': [
            signature,
            {
                'encoding': 'json',
                'commitment': 'confirmed',
                'maxSupportedTransactionVersion': 0
            }
        ]
    }

    response = requests.post(url, params=params, json=payload)
    data = response.json()

    if 'result' in data and data['result']:
        tx = data['result']
        account_keys = tx['transaction']['message']['accountKeys']
        
        print("🔍 Transaction Account Keys:")
        for i, key in enumerate(account_keys):
            print(f"  [{i}] {key}")
            
        print(f"\\n🎯 Looking for Raydium CPMM program: dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN")
        if "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN" in account_keys:
            print("✅ Found Raydium CPMM program in account keys!")
        else:
            print("❌ Raydium CPMM program NOT found in account keys")
            
        print(f"\\n🎯 Looking for target wallet: suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK")
        if "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK" in account_keys:
            print("✅ Found target wallet in account keys!")
        else:
            print("❌ Target wallet NOT found in account keys")

if __name__ == "__main__":
    asyncio.run(debug_transaction())
