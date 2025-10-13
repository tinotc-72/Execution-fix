#!/usr/bin/env python3
"""
Analyze transaction account structure to understand pump.fun requirements
"""

import asyncio
import json
import aiohttp
from env_keys import EnvKeys

async def analyze_transaction_accounts(tx_sig: str):
    """Analyze transaction account structure"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_sig,
            {
                "encoding": "json",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
    
    if "result" in result and result["result"]:
        tx_data = result["result"]
        
        print("=== Transaction Analysis ===")
        print(f"Signature: {tx_sig}")
        
        meta = tx_data.get("meta", {})
        print(f"Success: {meta.get('err') is None}")
        
        # Get message and accounts
        transaction = tx_data.get("transaction", {})
        message = transaction.get("message", {})
        
        if "accountKeys" in message:
            accounts = message["accountKeys"]
            print(f"\n=== Account Keys ({len(accounts)}) ===")
            
            for i, account in enumerate(accounts):
                account_str = account if isinstance(account, str) else str(account)
                print(f"{i:2}: {account_str}")
                
                # Identify account types
                if account_str.endswith("pump"):
                    print(f"    ^ Token Mint")
                elif account_str == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    print(f"    ^ Pump Trade Program")
                elif account_str == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    print(f"    ^ Token Program")
                elif account_str == "11111111111111111111111111111111":
                    print(f"    ^ System Program")
                elif account_str == "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL":
                    print(f"    ^ ATA Program")
                elif account_str == "ComputeBudget111111111111111111111111111111":
                    print(f"    ^ Compute Budget Program")
                elif account_str.startswith("So111"):
                    print(f"    ^ WSOL Mint")
        
        # Analyze instructions
        if "instructions" in message:
            instructions = message["instructions"]
            print(f"\n=== Instructions ({len(instructions)}) ===")
            
            for i, ix in enumerate(instructions):
                program_idx = ix.get("programIdIndex", 0)
                program_id = accounts[program_idx] if program_idx < len(accounts) else "Unknown"
                
                print(f"\nInstruction {i}:")
                print(f"  Program: {program_id}")
                print(f"  Accounts: {ix.get('accounts', [])}")
                
                # For pump.fun instructions, analyze account structure
                if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    print(f"  ^ PUMP.FUN Instruction")
                    account_indices = ix.get('accounts', [])
                    print(f"  Account details:")
                    for j, acc_idx in enumerate(account_indices):
                        if acc_idx < len(accounts):
                            acc_addr = accounts[acc_idx]
                            print(f"    {j}: [{acc_idx}] {acc_addr}")
        
        return tx_data
    else:
        print(f"Transaction not found: {result}")
        return None

async def main():
    # Analyze successful sell transaction
    print("=== SUCCESSFUL SELL TRANSACTION ===")
    await analyze_transaction_accounts("VfqeM43anBaxsR7fezsKVMY1P4DGp9LBKsxAoCbL2BQNt5LUZhec5bHqPb1DzUVYQNFqaYCHz65zirGvnfabPcX")
    
    print("\n" + "="*80 + "\n")
    
    # Analyze our failed transaction
    print("=== OUR FAILED TRANSACTION ===")
    await analyze_transaction_accounts("4q1PGHYTpavSv1jgdbr7UA3X1Da8tXAcwAgVPfa9WCryWEG7fANUYnHCeprpXDQeu5X2eqAa2dSuQPtEDfWS4oys")

if __name__ == "__main__":
    asyncio.run(main())
