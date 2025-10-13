#!/usr/bin/env python3

import httpx
import json

def get_pump_instruction_accounts():
    """Get the exact accounts used in Pump.fun instruction"""
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    # Successful transaction 
    signature = "2LuKV1tecqH6RG4tbGVZpDM4n3tHUpFxpuz7gVBsbPTzDee3RRqoicZSNuJfYtLna94GknCSuHWbBe73pGifhoYF"
    
    # Try different encoding
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
                
            instructions = message.get("instructions", [])
            
            print(f"📋 All accounts in message ({len(account_keys)} total):")
            for i, acc in enumerate(account_keys):
                print(f"  Message[{i:2d}]: {acc}")
            
            # Look for Pump.fun instructions by program ID index
            pump_program_index = None
            for i, account in enumerate(account_keys):
                if account == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    pump_program_index = i
                    break
            
            if pump_program_index is not None:
                print(f"\n🔍 Pump.fun program found at index {pump_program_index}")
                
                for ix_idx, ix in enumerate(instructions):
                    prog_idx = ix.get("programIdIndex")
                    if prog_idx == pump_program_index:
                        accounts_used = ix.get("accounts", [])
                        print(f"\n🎯 Pump.fun instruction {ix_idx} uses {len(accounts_used)} accounts:")
                        for j, acc_idx in enumerate(accounts_used):
                            if acc_idx < len(account_keys):
                                account = account_keys[acc_idx]
                                marker = ""
                                if account == "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump":
                                    marker = " <-- MINT"
                                elif account == "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ":
                                    marker = " <-- CREATOR_VAULT"
                                elif account == "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP":
                                    marker = " <-- FEE_RECIPIENT"
                                elif account == "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf":
                                    marker = " <-- GLOBAL"
                                elif account == "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ":
                                    marker = " <-- FEE_CONFIG"
                                elif account == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                                    marker = " <-- TOKEN_PROGRAM"
                                elif account == "11111111111111111111111111111111":
                                    marker = " <-- SYSTEM_PROGRAM"
                                elif account == "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1":
                                    marker = " <-- EVENT_AUTHORITY"
                                elif account == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                                    marker = " <-- PUMP_PROGRAM"
                                print(f"  Ix[{j:2d}] -> Msg[{acc_idx:2d}]: {account}{marker}")
                            else:
                                print(f"  Ix[{j:2d}] -> Msg[{acc_idx}]: [INVALID INDEX]")

if __name__ == "__main__":
    get_pump_instruction_accounts()