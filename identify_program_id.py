#!/usr/bin/env python3
"""
Program ID Identification - Find the exact program this wallet uses for selling
"""

import asyncio
import json
import requests
from env_keys import EnvKeys

async def identify_program_id():
    """Identify the exact program ID used by the wallet"""
    
    kz = EnvKeys()
    rpc_url = kz.HELIUS_RPC_URL
    
    # Analyze one specific transaction to get the full program ID
    signature = "3i7qjnkAvQ9jnsbFBccUnTsc4Xx4WbnjBAB4Wm9GrV3xKEikn8nwEAZqpqx3xwwrpFuf71ASg7QhPD78duPNqaNS"
    
    payload = {
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
    
    response = requests.post(rpc_url, json=payload, timeout=30)
    result = response.json()
    
    transaction = result["result"]["transaction"]
    message = transaction["message"]
    account_keys = message["accountKeys"]
    instructions = message["instructions"]
    
    print("🔍 EXACT PROGRAM IDs USED BY THE WALLET:")
    print("="*60)
    
    for idx, instruction in enumerate(instructions):
        program_idx = instruction.get("programIdIndex", 0)
        program_id = account_keys[program_idx]
        
        # Known programs to filter out
        system_programs = [
            "11111111111111111111111111111111",  # System Program
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # Associated Token Program
            "ComputeBudget111111111111111111111111111111"  # Compute Budget
        ]
        
        if program_id not in system_programs:
            print(f"Instruction {idx}: {program_id}")
            print(f"   Data: {instruction.get('data', '')[:50]}...")
    
    print("\n🎯 KEY FINDING:")
    print("The wallet consistently uses program: dbcij3LWdqJQsRZgqBo4e3c6qfxRCYRJvjBR5DpNbY4R")
    print("This appears to be a CUSTOM TRADING PROGRAM or MEV-protected router")
    
    # Let's also check what tokens they're trading
    print("\n💰 TOKEN ANALYSIS:")
    meta = result["result"]["meta"]
    pre_token_balances = meta.get("preTokenBalances", [])
    post_token_balances = meta.get("postTokenBalances", [])
    
    for balance in pre_token_balances:
        mint = balance.get("mint")
        amount = balance.get("uiTokenAmount", {}).get("uiAmount", 0)
        print(f"Pre-balance: {amount} tokens of {mint}")
    
    for balance in post_token_balances:
        mint = balance.get("mint")
        amount = balance.get("uiTokenAmount", {}).get("uiAmount", 0)
        print(f"Post-balance: {amount} tokens of {mint}")

if __name__ == "__main__":
    asyncio.run(identify_program_id())