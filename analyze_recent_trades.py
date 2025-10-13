#!/usr/bin/env python3
"""
Analyze Recent Transactions
===========================
Get recent transactions for the target wallet to find actual trading activity
"""

import asyncio
import json
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.commitment import Confirmed
from env_keys import EnvKeys

env = EnvKeys()

async def analyze_recent_transactions():
    """Analyze recent transactions to find actual trades"""
    
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        print(f"🔍 Analyzing recent transactions for: {wallet_address}")
        
        # Get recent signatures
        response = await client.get_signatures_for_address(
            Pubkey.from_string(wallet_address),
            limit=20  # Check last 20 transactions
        )
        
        if not response.value:
            print("❌ No transactions found")
            return
        
        print(f"📊 Found {len(response.value)} recent transactions")
        
        # Analyze each transaction
        for i, tx_info in enumerate(response.value):
            signature = str(tx_info.signature)
            print(f"\n--- Transaction {i+1} ---")
            print(f"Signature: {signature}")
            print(f"Slot: {tx_info.slot}")
            print(f"Block Time: {tx_info.block_time}")
            print(f"🔗 https://solscan.io/tx/{signature}")
            
            # Get detailed transaction
            try:
                sig_obj = Signature.from_string(signature)
                tx_response = await client.get_transaction(
                    sig_obj,
                    encoding="jsonParsed",
                    commitment=Confirmed,
                    max_supported_transaction_version=0
                )
                
                if not tx_response.value:
                    print("❌ Transaction details not found")
                    continue
                
                tx = tx_response.value
                
                # Check if successful
                if hasattr(tx, 'meta') and tx.meta and hasattr(tx.meta, 'err'):
                    if tx.meta.err:
                        print(f"❌ Transaction failed: {tx.meta.err}")
                        continue
                    else:
                        print("✅ Transaction successful")
                
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
                    continue
                
                instructions = tx_message.instructions
                print(f"📊 Instructions: {len(instructions)}")
                
                # Check for DEX programs
                dex_programs = {
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
                    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                    "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX"
                }
                
                found_dex = []
                sol_transfers = []
                token_transfers = []
                
                # Analyze instructions
                for j, instruction in enumerate(instructions):
                    # Check program IDs
                    program_id = None
                    if hasattr(instruction, 'program_id'):
                        program_id = str(instruction.program_id)
                    elif hasattr(instruction, 'program_id_index'):
                        if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
                            program_id = str(tx_message.account_keys[instruction.program_id_index])
                    
                    if program_id and program_id in dex_programs:
                        found_dex.append(dex_programs[program_id])
                        print(f"🎯 DEX found: {dex_programs[program_id]}")
                    
                    # Check parsed instructions
                    if hasattr(instruction, 'parsed') and instruction.parsed:
                        parsed = instruction.parsed
                        
                        if parsed.get('type') == 'transfer':
                            info = parsed.get('info', {})
                            source = info.get('source')
                            destination = info.get('destination')
                            amount = float(info.get('lamports', 0)) / 1e9
                            
                            if source == wallet_address:
                                sol_transfers.append(f"OUT: {amount} SOL")
                            elif destination == wallet_address:
                                sol_transfers.append(f"IN: {amount} SOL")
                        
                        elif parsed.get('type') in ['transferChecked', 'transfer'] and 'mint' in parsed.get('info', {}):
                            info = parsed.get('info', {})
                            source = info.get('source')
                            destination = info.get('destination')
                            mint = info.get('mint')
                            
                            amount = 0
                            if 'tokenAmount' in info:
                                amount = info['tokenAmount'].get('uiAmount', 0)
                            elif 'amount' in info:
                                amount = float(info.get('amount', 0))
                            
                            if source == wallet_address or destination == wallet_address:
                                direction = "OUT" if source == wallet_address else "IN"
                                token_transfers.append(f"{direction}: {amount} of {mint[:8]}...")
                
                # Check balance changes
                sol_balance_change = 0
                if hasattr(tx, 'meta') and tx.meta:
                    meta = tx.meta
                    if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
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
                
                # Summary
                if found_dex:
                    print(f"🏛️  DEX Programs: {', '.join(found_dex)}")
                if sol_transfers:
                    print(f"💸 SOL Transfers: {', '.join(sol_transfers)}")
                if token_transfers:
                    print(f"🪙 Token Transfers: {', '.join(token_transfers)}")
                
                # Determine if this is a real trade
                is_trade = False
                if found_dex and (abs(sol_balance_change) > 0.001 or token_transfers):
                    is_trade = True
                    trade_type = "UNKNOWN"
                    if sol_balance_change < -0.001 and any("IN:" in tt for tt in token_transfers):
                        trade_type = "BUY"
                    elif sol_balance_change > 0.001 and any("OUT:" in tt for tt in token_transfers):
                        trade_type = "SELL"
                    
                    print(f"🎯 TRADE DETECTED: {trade_type}")
                else:
                    print("📝 Setup/Management transaction")
                
                print("-" * 60)
                
                # Only analyze first few detailed
                if i >= 5:
                    print("... (showing first 5 detailed, continuing with summary)")
                    break
                    
            except Exception as e:
                print(f"❌ Error analyzing transaction: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_recent_transactions())
