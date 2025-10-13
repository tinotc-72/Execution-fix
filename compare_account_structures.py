#!/usr/bin/env python3

import httpx
import json

def compare_account_structures():
    """Compare our account structure with the successful transaction"""
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    # Recent successful transaction
    signature = "4ocpfga6nVxwf9YpfzG3GzK6qHg2yBF7wUxzQ8SJTSMrhu2V7J7PViX5NYAPF9CVMR2WA4ERfRLujJVC7MbCXo51"
    
    print(f"🔍 Analyzing successful transaction: {signature}")
    
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
            
            print(f"\n📋 All accounts in successful transaction ({len(account_keys)} total):")
            for i, acc in enumerate(account_keys):
                print(f"  Message[{i:2d}]: {acc}")
            
            # Find Pump.fun instruction
            pump_program_index = None
            for idx, account in enumerate(account_keys):
                if account == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    pump_program_index = idx
                    break
            
            if pump_program_index is not None:
                for ix_idx, ix in enumerate(instructions):
                    prog_idx = ix.get("programIdIndex")
                    if prog_idx == pump_program_index:
                        accounts_used = ix.get("accounts", [])
                        
                        print(f"\n🎯 Pump.fun instruction uses {len(accounts_used)} accounts:")
                        successful_accounts = []
                        for j, acc_idx in enumerate(accounts_used):
                            if acc_idx < len(account_keys):
                                account = account_keys[acc_idx]
                                successful_accounts.append(account)
                                marker = ""
                                if j == 0:
                                    marker = " <-- [0] GLOBAL"
                                elif j == 1:
                                    marker = " <-- [1] FEE_RECIPIENT"
                                elif j == 2:
                                    marker = " <-- [2] MINT"
                                elif j == 8:
                                    marker = " <-- [8] TOKEN_PROGRAM"
                                elif j == 9:
                                    marker = " <-- [9] CREATOR_VAULT"
                                elif j == 13:
                                    marker = " <-- [13] FEE_CONFIG"
                                print(f"  Successful[{j:2d}]: {account}{marker}")
                        
                        print(f"\n🔍 OUR CURRENT ACCOUNT STRUCTURE:")
                        our_accounts = [
                            "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # global
                            "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP",  # fee_recipient_writable
                            "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump",  # mint
                            "2hFs2bu8vhEPWtynp49hFU199gUWkJW1dZaJRWXbtPHa", # bonding_curve
                            "BxE1Fvd8qftJdzC4ZxaDfDyo2BrEWAPkSfZQztZMAnz1", # associated_bonding_curve
                            "USER_TOKEN_ACCOUNT",                               # user_token_account
                            "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB",  # user (our wallet)
                            "11111111111111111111111111111111",                 # system_program
                            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",     # token_program
                            "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ",  # creator_vault
                            "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1", # event_authority
                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # pump_program
                            "8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt", # second_fee_recipient
                            "Dq9gcfQLqpnu7M7kWBzmR2vYdWBCZm6nxgmbxXPCsqzc", # fee_config
                        ]
                        
                        for i, acc in enumerate(our_accounts):
                            print(f"  Our[{i:2d}]: {acc}")
                        
                        print(f"\n🔄 COMPARISON:")
                        mismatches = 0
                        for i in range(min(len(successful_accounts), len(our_accounts))):
                            if successful_accounts[i] != our_accounts[i] and our_accounts[i] != "USER_TOKEN_ACCOUNT":
                                print(f"  ❌ Position {i}: Successful='{successful_accounts[i]}' vs Our='{our_accounts[i]}'")
                                mismatches += 1
                            elif our_accounts[i] == "USER_TOKEN_ACCOUNT":
                                print(f"  🟡 Position {i}: Dynamic account (user token account)")
                            else:
                                print(f"  ✅ Position {i}: Match")
                        
                        print(f"\n📊 Total mismatches: {mismatches}")
                        
                        return successful_accounts

if __name__ == "__main__":
    compare_account_structures()