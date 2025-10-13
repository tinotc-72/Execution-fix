#!/usr/bin/env python3
"""
Analyze Detected Transactions
============================

Analyze the specific transactions that our enhanced WebSocket monitor detected
to understand why they triggered trade signals and what we can improve.
"""

import asyncio
import json
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from solana.rpc.commitment import Confirmed
from env_keys import EnvKeys

env = EnvKeys()

async def analyze_single_transaction(signature: str):
    """Analyze a single transaction"""
    
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        print(f"🔍 Analyzing: {signature}")
        
        # Get transaction details
        sig_obj = Signature.from_string(signature)
        
        tx_response = await client.get_transaction(
            sig_obj,
            encoding="jsonParsed",
            commitment=Confirmed,
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print(f"❌ Transaction not found")
            return
        
        tx = tx_response.value
        
        # Get basic info
        if hasattr(tx, 'transaction'):
            tx_data = tx.transaction
        else:
            tx_data = tx
        
        if hasattr(tx_data, 'message'):
            tx_message = tx_data.message
        elif hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
            tx_message = tx_data.transaction.message
        else:
            print(f"❌ Cannot find transaction message")
            return
        
        instructions = tx_message.instructions
        print(f"📊 Instructions: {len(instructions)}")
        
        # Check account balance changes
        sol_balance_change = 0
        if hasattr(tx, 'meta') and tx.meta:
            meta = tx.meta
            if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                # Find wallet index
                wallet_index = -1
                if hasattr(tx_message, 'account_keys'):
                    for idx, account in enumerate(tx_message.account_keys):
                        if str(account) == wallet_address:
                            wallet_index = idx
                            break
                
                if wallet_index >= 0 and wallet_index < len(meta.pre_balances) and wallet_index < len(meta.post_balances):
                    pre_balance = meta.pre_balances[wallet_index] / 1e9
                    post_balance = meta.post_balances[wallet_index] / 1e9
                    sol_balance_change = post_balance - pre_balance
                    
                    print(f"💰 SOL balance change: {sol_balance_change:+.6f} SOL")
                    print(f"   📊 Pre: {pre_balance:.6f} SOL")
                    print(f"   📊 Post: {post_balance:.6f} SOL")
        
        # Check for DEX programs
        dex_programs = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            "11111111111111111111111111111112": "System Program"
        }
        
        # Check program IDs
        detected_dexes = []
        for instruction in instructions:
            program_id = None
            if hasattr(instruction, 'program_id'):
                program_id = str(instruction.program_id)
            elif hasattr(instruction, 'program_id_index'):
                if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
                    program_id = str(tx_message.account_keys[instruction.program_id_index])
            
            if program_id and program_id in dex_programs:
                detected_dexes.append(dex_programs[program_id])
        
        print(f"🎯 Detected programs: {list(set(detected_dexes))}")
        
        # Check parsed instructions
        sol_transfers = []
        token_transfers = []
        
        for i, instruction in enumerate(instructions):
            try:
                if hasattr(instruction, 'parsed') and instruction.parsed:
                    parsed = instruction.parsed
                    instruction_type = parsed.get('type', 'unknown')
                    
                    if instruction_type == 'transfer':
                        info = parsed.get('info', {})
                        source = info.get('source')
                        destination = info.get('destination')
                        amount = float(info.get('lamports', 0)) / 1e9
                        
                        if source == wallet_address or destination == wallet_address:
                            direction = 'OUT' if source == wallet_address else 'IN'
                            sol_transfers.append({'type': direction.lower(), 'amount': amount})
                            print(f"💸 SOL {direction}: {amount:.6f} SOL")
                    
                    elif instruction_type in ['transferChecked', 'transfer']:
                        info = parsed.get('info', {})
                        source = info.get('source')
                        destination = info.get('destination')
                        mint = info.get('mint')
                        
                        # Handle different amount formats
                        amount = 0
                        if 'tokenAmount' in info:
                            amount = float(info['tokenAmount'].get('uiAmount', 0))
                        elif 'amount' in info:
                            amount = float(info.get('amount', 0))
                        
                        if (source == wallet_address or destination == wallet_address) and mint:
                            direction = 'OUT' if source == wallet_address else 'IN'
                            token_transfers.append({
                                'mint': mint,
                                'amount': amount,
                                'direction': direction.lower()
                            })
                            print(f"🎯 Token {direction}: {amount} of {mint[:8]}...")
                    
                    print(f"   Instruction {i}: {instruction_type}")
            except Exception as e:
                print(f"   Error parsing instruction {i}: {e}")
        
        # Summary
        print(f"\n📋 SUMMARY:")
        print(f"   💰 SOL balance change: {sol_balance_change:+.6f} SOL")
        print(f"   💸 SOL transfers: {len(sol_transfers)}")
        print(f"   🎯 Token transfers: {len(token_transfers)}")
        print(f"   🔗 Solscan: https://solscan.io/tx/{signature}")
        
        # Determine if this should be a trade
        if abs(sol_balance_change) > 0.001:  # Significant balance change
            print(f"✅ SHOULD BE DETECTED AS TRADE (significant balance change)")
        elif sol_transfers and token_transfers:
            print(f"✅ SHOULD BE DETECTED AS TRADE (SOL + token transfers)")
        elif any("jupiter" in dex.lower() or "raydium" in dex.lower() or "pump" in dex.lower() for dex in detected_dexes):
            print(f"✅ SHOULD BE DETECTED AS TRADE (DEX program)")
        else:
            print(f"❌ NOT A TRADE (setup/management transaction)")
        
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
    finally:
        await client.close()

async def main():
    """Analyze the transactions detected by enhanced monitor"""
    
    # Transactions detected by enhanced WebSocket monitor
    transactions = [
        "3UdVffRWBNacREJUVNoAWpiY4zUQoALoi5L3RWAn6iJSSv3BAHpde4NodYoJjWd1TZkerZ8KcfqcUj785GzQcZUh",
        "Pb3ztg2quHKXnZ2tiv9Epy1PxwERXee1Jxu5dSHFAa69WgDxVFtRcrexEA8AAcXwh12k5V2EYs4mm3QT1jYcV7Q"
    ]
    
    print("🔍 ANALYZING ENHANCED WEBSOCKET DETECTED TRANSACTIONS")
    print("=" * 60)
    print("These transactions were detected by our enhanced WebSocket monitor")
    print("with balance changes from 1853.36 SOL → 1876.62 SOL (+23.26 SOL)")
    print("=" * 60)
    
    for i, signature in enumerate(transactions, 1):
        print(f"\n🎯 TRANSACTION {i}/{len(transactions)}")
        print("-" * 50)
        
        await analyze_single_transaction(signature)
        
        if i < len(transactions):
            print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
