#!/usr/bin/env python3
"""
Analyze real Pump.fun transaction to understand exact account order and ATA structure
"""

import asyncio
import json
import httpx
from env_keys import EnvKeys

async def analyze_pumpfun_transaction(signature: str):
    """Analyze a real Pump.fun transaction to understand the exact structure"""
    
    env = EnvKeys()
    
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
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(env.HELIUS_RPC_URL, json=payload)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ RPC Error: {data['error']}")
            return
        
        result = data.get('result')
        if not result:
            print(f"❌ No transaction data found")
            return
        
        print(f"🎯 Analyzing Pump.fun transaction: {signature}")
        print("=" * 80)
        
        # Extract transaction data
        transaction = result.get('transaction', {})
        message = transaction.get('message', {})
        account_keys = message.get('accountKeys', [])
        instructions = message.get('instructions', [])
        
        print(f"📝 Total account keys: {len(account_keys)}")
        print(f"📝 Total instructions: {len(instructions)}")
        print()
        
        # Show all account keys first
        print("🔑 Account Keys:")
        for i, account in enumerate(account_keys):
            print(f"  [{i:2d}] {account}")
        print()
        
        # Analyze each instruction
        for ix_idx, instruction in enumerate(instructions):
            program_id_index = instruction.get('programIdIndex', 0)
            program_id = account_keys[program_id_index] if program_id_index < len(account_keys) else 'Unknown'
            accounts = instruction.get('accounts', [])
            data = instruction.get('data', '')
            
            print(f"📋 Instruction {ix_idx}:")
            print(f"  Program ID: {program_id}")
            print(f"  Program Index: {program_id_index}")
            print(f"  Accounts ({len(accounts)}):")
            
            for acc_idx, account_index in enumerate(accounts):
                if account_index < len(account_keys):
                    account_address = account_keys[account_index]
                    print(f"    [{acc_idx:2d}] Index {account_index:2d}: {account_address}")
                else:
                    print(f"    [{acc_idx:2d}] Index {account_index:2d}: INVALID INDEX")
            
            if data:
                print(f"  Data: {data}")
            else:
                print(f"  Data: (empty)")
            print()
            
            # Special analysis for ATA and Pump.fun programs
            if program_id == "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL":
                print(f"  🔍 ATA PROGRAM ANALYSIS:")
                if len(accounts) >= 4:
                    ata_account = account_keys[accounts[0]]
                    mint_account = account_keys[accounts[1]]
                    owner_account = account_keys[accounts[2]]
                    payer_account = account_keys[accounts[3]]
                    
                    print(f"    ATA Address: {ata_account}")
                    print(f"    Mint:        {mint_account}")
                    print(f"    Owner:       {owner_account}")
                    print(f"    Payer:       {payer_account}")
                    
                    # Verify ATA derivation
                    from solders.pubkey import Pubkey
                    try:
                        owner_pubkey = Pubkey.from_string(owner_account)
                        mint_pubkey = Pubkey.from_string(mint_account)
                        token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
                        ata_program = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
                        
                        derived_ata, bump = Pubkey.find_program_address(
                            [bytes(owner_pubkey), bytes(token_program), bytes(mint_pubkey)],
                            ata_program
                        )
                        
                        matches = str(derived_ata) == ata_account
                        print(f"    Derived ATA: {derived_ata}")
                        print(f"    Matches:     {'✅ YES' if matches else '❌ NO'}")
                        print(f"    Bump:        {bump}")
                        
                    except Exception as e:
                        print(f"    Derivation Error: {e}")
                print()
            
            elif program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                print(f"  🚀 PUMP.FUN PROGRAM ANALYSIS:")
                print(f"    This is the main Pump.fun buy/sell instruction")
                if len(accounts) >= 7:
                    print(f"    Account structure appears to follow Pump.fun pattern")
                    # Look for the payer/user wallet
                    for acc_idx, account_index in enumerate(accounts):
                        if account_index < len(account_keys):
                            account_address = account_keys[account_index]
                            # Check if this might be the user wallet (typically appears multiple times)
                            appearances = sum(1 for idx in accounts if idx == account_index and idx < len(account_keys))
                            if appearances > 1:
                                print(f"      Account {acc_idx} ({account_address}) appears {appearances} times - likely user wallet")
                print()
        
        # Analyze transaction metadata
        meta = result.get('meta', {})
        if meta:
            print("📊 Transaction Metadata:")
            print(f"  Status: {'✅ Success' if not meta.get('err') else '❌ Failed'}")
            if meta.get('err'):
                print(f"  Error: {meta.get('err')}")
            
            fee = meta.get('fee', 0)
            print(f"  Fee: {fee} lamports")
            
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            if len(pre_balances) == len(post_balances) == len(account_keys):
                print(f"  Balance Changes:")
                for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                    if pre != post:
                        change = post - pre
                        account = account_keys[i] if i < len(account_keys) else 'Unknown'
                        print(f"    [{i:2d}] {account[:8]}...{account[-8:]}: {change:+,} lamports")

if __name__ == "__main__":
    signature = "5cUKAb9cTwKxktLfP8FqM9bBjEwT7F6bbqESshhJ46jBtiDwwHBA9bhZau6Ci1G8uvsGZvQzut5Ux4rQ2BRR6Jdu"
    asyncio.run(analyze_pumpfun_transaction(signature))