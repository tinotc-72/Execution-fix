#!/usr/bin/env python3

import httpx

# Working transaction signature
working_sig = "ynYE8YGdZsXNW2EzgE4XwbEF2neiEUkYvP7ejyUPZBRSt1TRn8Qxyx8gnTWCp2ddixYgpjNFkSKTTUxr4Rgr69h"
helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"

print(f"🔍 Analyzing working transaction: {working_sig}")

resp = httpx.post(helius_url, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [working_sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
})

if resp.status_code == 200:
    result = resp.json()
    if "result" in result and result["result"]:
        tx = result["result"]
        message = tx.get("transaction", {}).get("message", {})
        
        print(f"\n📋 Transaction Analysis:")
        print(f"⏰ Block Time: {tx.get('blockTime')}")
        print(f"🏦 Slot: {tx.get('slot')}")
        
        account_keys = message.get("accountKeys", [])
        if account_keys and isinstance(account_keys[0], dict):
            account_keys = [k["pubkey"] for k in account_keys]
        
        instructions = message.get("instructions", [])
        
        print(f"\n🔑 Account Keys ({len(account_keys)}):")
        for i, key in enumerate(account_keys):
            print(f"  {i:2d}: {key}")
        
        print(f"\n📋 Instructions ({len(instructions)}):")
        for i, ix in enumerate(instructions):
            prog_id = ix.get("programId")
            accounts = ix.get("accounts", [])
            print(f"\n  Instruction {i+1}: {prog_id}")
            if prog_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                print(f"    🎯 PUMP.FUN BUY INSTRUCTION")
                print(f"    📋 Accounts ({len(accounts)}):")
                for j, acc in enumerate(accounts):
                    marker = " <-- TARGET CREATOR_VAULT" if acc == "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ" else ""
                    marker += " <-- MINT" if acc == "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump" else ""
                    print(f"      {j:2d}: {acc}{marker}")
            else:
                print(f"    📋 Accounts: {len(accounts)} accounts")
        
        # Check for errors
        meta = tx.get("meta", {})
        if meta.get("err"):
            print(f"\n❌ Transaction Error: {meta['err']}")
        else:
            print(f"\n✅ Transaction Success")
            
        print(f"\n🏷️ Key Observations:")
        print(f"   - This is a DIRECT Pump.fun transaction, not router-based")
        print(f"   - Creator vault J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ is at index 9")
        print(f"   - The account structure is different from router transactions")