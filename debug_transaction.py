#!/usr/bin/env python3
"""
Debug Transaction Analysis
=========================
Analyze the specific transaction to understand why trade detection is failing
"""

import asyncio
import json
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from solana.rpc.commitment import Confirmed
from env_keys import EnvKeys

env = EnvKeys()

async def analyze_transaction():
    """Analyze the specific transaction that failed"""
    
    signature = "P8UHqmfrgdVs1scoh7pk2GszPmtLbi96NwtzA9CQfPEdfoPquDP4o8TL3tFd2A1omEuJMeawCnozViRgbNVyFeE"
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        print(f"🔍 Analyzing transaction: {signature}")
        print(f"🎯 Target wallet: {wallet_address}")
        
        # Get transaction details
        sig_obj = Signature.from_string(signature)
        tx_response = await client.get_transaction(
            sig_obj,
            encoding="jsonParsed",
            commitment=Confirmed,
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print("❌ Transaction not found")
            return
        
        tx = tx_response.value
        print("✅ Transaction retrieved successfully")
        
        # Analyze structure
        if hasattr(tx, 'transaction'):
            tx_data = tx.transaction
        else:
            tx_data = tx
        
        if hasattr(tx_data, 'message'):
            tx_message = tx_data.message
        elif hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
            tx_message = tx_data.transaction.message
        else:
            print("❌ Cannot find transaction message")
            return
        
        instructions = tx_message.instructions
        print(f"📊 Found {len(instructions)} instructions")
        
        # Analyze each instruction
        for i, instruction in enumerate(instructions):
            print(f"\n--- Instruction {i+1} ---")
            
            # Check if it has parsed data
            if hasattr(instruction, 'parsed') and instruction.parsed:
                parsed = instruction.parsed
                print(f"Type: {parsed.get('type', 'unknown')}")
                print(f"Info: {json.dumps(parsed.get('info', {}), indent=2)}")
            else:
                print("No parsed data available")
            
            # Check program ID
            program_id = None
            if hasattr(instruction, 'program_id'):
                program_id = str(instruction.program_id)
            elif hasattr(instruction, 'program_id_index'):
                if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
                    program_id = str(tx_message.account_keys[instruction.program_id_index])
            
            if program_id:
                print(f"Program ID: {program_id}")
        
        # Check account keys
        if hasattr(tx_message, 'account_keys'):
            print(f"\n📋 Account Keys ({len(tx_message.account_keys)}):")
            for i, account in enumerate(tx_message.account_keys):
                account_str = str(account)
                is_target = "🎯 TARGET WALLET" if account_str == wallet_address else ""
                print(f"  {i}: {account_str} {is_target}")
        
        # Check meta information
        if hasattr(tx, 'meta') and tx.meta:
            meta = tx.meta
            print(f"\n💰 Balance Changes:")
            
            if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                for i, (pre, post) in enumerate(zip(meta.pre_balances, meta.post_balances)):
                    if i < len(tx_message.account_keys):
                        account = str(tx_message.account_keys[i])
                        change = (post - pre) / 1e9  # Convert to SOL
                        if abs(change) > 0.0001:  # Only show significant changes
                            marker = "🎯" if account == wallet_address else ""
                            print(f"  Account {i}: {change:+.6f} SOL {marker}")
            
            # Check token balance changes
            if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                print(f"\n🪙 Token Balance Changes:")
                print(f"Pre-token balances: {len(meta.pre_token_balances)}")
                print(f"Post-token balances: {len(meta.post_token_balances)}")
                
                for token_balance in meta.post_token_balances:
                    if hasattr(token_balance, 'owner') and str(token_balance.owner) == wallet_address:
                        print(f"  Target wallet token: {token_balance}")
        
        print(f"\n🔗 Solscan: https://solscan.io/tx/{signature}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_transaction())
