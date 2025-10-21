#!/usr/bin/env python3
"""
Analyze the reference Pump.fun transactions to extract exact instruction data and account structure.

Reference transactions:
- Buy: 2XM4sLbvnKMr5p7PxVwir89ZamznQ4RgxWE1z36xRzRjANeKpSaYjGqhEHHoAV5NZpqHXvhyKp4HWtG4gBQL7VtH
- Sell: 4UacebZRJDyTRN41f2hngRxtxqrF1MgLVeMnLVAmLe7jgxZQ4wi1RRuXuxmAiiyuBuyBq3EPDJgyGqR26KVsY514
"""

import asyncio
import json
import httpx
import os

# Use public RPC for analysis
RPC_URL = os.getenv("HELIUS_RPC_URL", "https://api.mainnet-beta.solana.com")

async def analyze_transaction(signature: str, tx_type: str):
    """Analyze a Pump.fun transaction to extract exact structure"""
    
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
    
    print(f"\n{'='*80}")
    print(f"🎯 Analyzing Pump.fun {tx_type.upper()} transaction")
    print(f"Signature: {signature}")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(RPC_URL, json=payload)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ RPC Error: {data['error']}")
            return None
        
        result = data.get('result')
        if not result:
            print(f"❌ No transaction data found")
            return None
        
        # Extract transaction data
        transaction = result.get('transaction', {})
        message = transaction.get('message', {})
        account_keys = message.get('accountKeys', [])
        instructions = message.get('instructions', [])
        
        print(f"📝 Total account keys: {len(account_keys)}")
        print(f"📝 Total instructions: {len(instructions)}")
        
        # Show all account keys
        print(f"\n🔑 Account Keys:")
        for i, account in enumerate(account_keys):
            print(f"  [{i:2d}] {account}")
        
        # Analyze each instruction
        pumpfun_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        
        for ix_idx, instruction in enumerate(instructions):
            program_id_index = instruction.get('programIdIndex', 0)
            program_id = account_keys[program_id_index] if program_id_index < len(account_keys) else 'Unknown'
            accounts = instruction.get('accounts', [])
            data = instruction.get('data', '')
            
            print(f"\n📋 Instruction {ix_idx}:")
            print(f"  Program ID: {program_id}")
            print(f"  Program Index: {program_id_index}")
            print(f"  Data: {data}")
            print(f"  Accounts ({len(accounts)}):")
            
            for acc_idx, account_index in enumerate(accounts):
                if account_index < len(account_keys):
                    account_address = account_keys[account_index]
                    print(f"    [{acc_idx:2d}] Index {account_index:2d}: {account_address}")
            
            # Focus on Pump.fun swap instruction
            if program_id == pumpfun_program or "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P" in program_id:
                print(f"\n  🚀 PUMP.FUN SWAP INSTRUCTION FOUND:")
                print(f"    Instruction data (base58): {data}")
                
                # Decode instruction data to hex
                import base58
                try:
                    data_bytes = base58.b58decode(data)
                    data_hex = data_bytes.hex()
                    print(f"    Instruction data (hex): {data_hex}")
                    print(f"    Data length: {len(data_bytes)} bytes")
                    
                    # Extract discriminator (first 8 bytes)
                    if len(data_bytes) >= 8:
                        discriminator = data_bytes[:8]
                        print(f"    Discriminator (hex): {discriminator.hex()}")
                        
                        # Extract parameters (remaining bytes)
                        if len(data_bytes) > 8:
                            params = data_bytes[8:]
                            print(f"    Parameters (hex): {params.hex()}")
                            print(f"    Parameters length: {len(params)} bytes")
                            
                            # Try to parse as u64 values
                            import struct
                            if len(params) >= 16:
                                val1 = struct.unpack("<Q", params[:8])[0]
                                val2 = struct.unpack("<Q", params[8:16])[0]
                                print(f"    Parsed as two u64 values:")
                                print(f"      Value 1: {val1} ({val1/1_000_000_000:.9f} SOL if lamports)")
                                print(f"      Value 2: {val2} ({val2/1_000_000_000:.9f} SOL if lamports)")
                except Exception as e:
                    print(f"    Error decoding data: {e}")
        
        # Analyze transaction metadata
        meta = result.get('meta', {})
        if meta:
            print(f"\n📊 Transaction Metadata:")
            print(f"  Status: {'✅ Success' if not meta.get('err') else '❌ Failed'}")
            if meta.get('err'):
                print(f"  Error: {meta.get('err')}")
            
            fee = meta.get('fee', 0)
            print(f"  Fee: {fee} lamports ({fee/1_000_000_000:.9f} SOL)")
            
            # Show token balance changes
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            if pre_token_balances or post_token_balances:
                print(f"\n  💰 Token Balance Changes:")
                
                # Create a map of account index to token changes
                token_changes = {}
                
                for pre_bal in pre_token_balances:
                    acc_idx = pre_bal.get('accountIndex')
                    mint = pre_bal.get('mint')
                    amount = int(pre_bal.get('uiTokenAmount', {}).get('amount', 0))
                    token_changes[acc_idx] = {
                        'mint': mint,
                        'pre': amount,
                        'post': amount
                    }
                
                for post_bal in post_token_balances:
                    acc_idx = post_bal.get('accountIndex')
                    mint = post_bal.get('mint')
                    amount = int(post_bal.get('uiTokenAmount', {}).get('amount', 0))
                    
                    if acc_idx in token_changes:
                        token_changes[acc_idx]['post'] = amount
                    else:
                        token_changes[acc_idx] = {
                            'mint': mint,
                            'pre': 0,
                            'post': amount
                        }
                
                for acc_idx, change in token_changes.items():
                    delta = change['post'] - change['pre']
                    if delta != 0:
                        account = account_keys[acc_idx] if acc_idx < len(account_keys) else 'Unknown'
                        mint = change['mint']
                        print(f"    Account [{acc_idx}] {account}")
                        print(f"      Mint: {mint}")
                        print(f"      Change: {delta:+,} tokens")
        
        return {
            'signature': signature,
            'type': tx_type,
            'account_keys': account_keys,
            'instructions': instructions,
            'meta': meta
        }

async def main():
    """Analyze both reference transactions"""
    
    # Reference transactions
    buy_sig = "2XM4sLbvnKMr5p7PxVwir89ZamznQ4RgxWE1z36xRzRjANeKpSaYjGqhEHHoAV5NZpqHXvhyKp4HWtG4gBQL7VtH"
    sell_sig = "4UacebZRJDyTRN41f2hngRxtxqrF1MgLVeMnLVAmLe7jgxZQ4wi1RRuXuxmAiiyuBuyBq3EPDJgyGqR26KVsY514"
    
    buy_data = await analyze_transaction(buy_sig, "buy")
    sell_data = await analyze_transaction(sell_sig, "sell")
    
    print(f"\n{'='*80}")
    print("✅ Analysis complete!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(main())
