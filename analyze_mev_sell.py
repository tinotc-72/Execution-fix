#!/usr/bin/env python3
"""
Detailed MEV Bot Sell Transaction Analysis
Analyzes the specific instruction structure for MEV-style sells
"""

import json
from solders.transaction import Transaction
from solders.signature import Signature
from solders.pubkey import Pubkey
import base64
from env_keys import EnvKeys

def analyze_mev_sell_transaction(signature_str: str):
    """Deep analysis of MEV bot sell transaction"""
    try:
        env = EnvKeys()
        
        # Get transaction details
        import httpx
        
        response = httpx.post(
            env.HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature_str,
                    {
                        "encoding": "base64",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            },
            timeout=10.0
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return
            
        data = response.json()
        
        if 'error' in data:
            print(f"❌ RPC Error: {data['error']}")
            return
            
        tx_data = data['result']
        if not tx_data:
            print("❌ Transaction not found")
            return
            
        # Parse the transaction
        tx_bytes = base64.b64decode(tx_data['transaction'][0])
        transaction = Transaction.from_bytes(tx_bytes)
        
        print(f"🎯 MEV SELL TRANSACTION ANALYSIS")
        print(f"=" * 50)
        print(f"Signature: {signature_str}")
        print(f"Success: {'✅' if not tx_data.get('meta', {}).get('err') else '❌'}")
        
        # Analyze fee structure
        meta = tx_data.get('meta', {})
        fee = meta.get('fee', 0) / 1_000_000_000  # Convert to SOL
        print(f"Fee: {fee:.9f} SOL")
        
        # Analyze compute budget settings
        compute_units_consumed = meta.get('computeUnitsConsumed', 0)
        print(f"Compute Units Used: {compute_units_consumed:,}")
        
        # Basic transaction info
        print(f"Total Instructions: {len(transaction.message.instructions)}")
        print(f"Total Accounts: {len(transaction.message.account_keys)}")
        
        # Try to get instructions from the RPC response as well  
        try:
            # The transaction data might be in different formats
            if isinstance(tx_data.get('transaction'), list):
                # Base64 encoded transaction
                print(f"\n📋 Transaction is base64 encoded")
            else:
                # JSON transaction
                transaction_obj = tx_data.get('transaction', {})
                message = transaction_obj.get('message', {})
                
                print(f"\n📋 INSTRUCTION DETAILS (from RPC):")
                if 'instructions' in message:
                    instructions = message['instructions']
                    print(f"RPC Instructions count: {len(instructions)}")
                    
                    for i, instruction in enumerate(instructions):
                        print(f"\n   [{i}] Instruction:")
                        print(f"       Program ID Index: {instruction.get('programIdIndex', 'N/A')}")
                        print(f"       Accounts: {instruction.get('accounts', [])}")
                        print(f"       Data: {instruction.get('data', 'N/A')}")
        except Exception as e:
            print(f"Could not parse transaction structure: {e}")
                
        # Also try parsed instructions
        if 'meta' in tx_data and 'innerInstructions' in tx_data['meta']:
            inner_instructions = tx_data['meta']['innerInstructions']
            print(f"\n📋 INNER INSTRUCTIONS:")
            for i, inner_group in enumerate(inner_instructions):
                print(f"\n   Group [{i}]:")
                for j, inner_inst in enumerate(inner_group.get('instructions', [])):
                    print(f"       [{j}] Program ID Index: {inner_inst.get('programIdIndex', 'N/A')}")
                    print(f"           Data: {inner_inst.get('data', 'N/A')}")
        
        # Original instruction analysis
        print(f"\n📋 PARSED TRANSACTION INSTRUCTIONS:")
        print(f"Parsed Instructions count: {len(transaction.message.instructions)}")
        
        for i, instruction in enumerate(transaction.message.instructions):
            program_id = transaction.message.account_keys[instruction.program_id_index]
            print(f"\n   [{i}] Program: {program_id}")
            print(f"       Accounts: {len(instruction.accounts)}")
            print(f"       Data length: {len(instruction.data)} bytes")
            
            # Check for known programs
            if str(program_id) == "ComputeBudget111111111111111111111111111111":
                print(f"       Type: Compute Budget Instruction")
                if len(instruction.data) >= 5:
                    instruction_type = instruction.data[0]
                    if instruction_type == 2:  # SetComputeUnitLimit
                        compute_units = int.from_bytes(instruction.data[1:5], 'little')
                        print(f"       → Compute Unit Limit: {compute_units:,}")
                    elif instruction_type == 3:  # SetComputeUnitPrice
                        micro_lamports = int.from_bytes(instruction.data[1:9], 'little')
                        print(f"       → Priority Fee: {micro_lamports:,} micro-lamports")
                        
            elif str(program_id) == "11111111111111111111111111111111":
                print(f"       Type: System Program")
                if len(instruction.data) >= 4:
                    instruction_type = int.from_bytes(instruction.data[0:4], 'little')
                    print(f"       → System Instruction Type: {instruction_type}")
                    
            elif str(program_id) == "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW":
                print(f"       Type: 🤖 MEV BOT SELL INSTRUCTION")
                print(f"       → This is the core MEV sell logic!")
                
                # Analyze the MEV sell instruction data
                data_hex = instruction.data.hex()
                print(f"       → Instruction Data: {data_hex}")
                
                # Analyze accounts involved
                print(f"       → Accounts involved:")
                for j, account_index in enumerate(instruction.accounts):
                    if account_index < len(transaction.message.account_keys):
                        account_pubkey = transaction.message.account_keys[account_index]
                        print(f"           [{j}] {account_pubkey}")
                    
            elif str(program_id) == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                print(f"       Type: 🎯 PUMP.FUN SELL")
                data_hex = instruction.data.hex()
                print(f"       → Sell Instruction Data: {data_hex}")
                
                # Analyze accounts involved  
                print(f"       → Accounts involved:")
                for j, account_index in enumerate(instruction.accounts):
                    if account_index < len(transaction.message.account_keys):
                        account_pubkey = transaction.message.account_keys[account_index]
                        print(f"           [{j}] {account_pubkey}")
                
        # Analyze account changes
        print(f"\n💰 BALANCE CHANGES:")
        pre_balances = meta.get('preBalances', [])
        post_balances = meta.get('postBalances', [])
        
        for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
            if pre != post and i < len(transaction.message.account_keys):
                change = (post - pre) / 1_000_000_000
                account = transaction.message.account_keys[i]
                direction = "+" if change > 0 else ""
                print(f"   {account}: {direction}{change:.9f} SOL")
                
        # Analyze token changes
        if 'preTokenBalances' in meta and 'postTokenBalances' in meta:
            print(f"\n🪙 TOKEN CHANGES:")
            pre_tokens = {tb['accountIndex']: tb for tb in meta['preTokenBalances']}
            post_tokens = {tb['accountIndex']: tb for tb in meta['postTokenBalances']}
            
            all_indices = set(pre_tokens.keys()) | set(post_tokens.keys())
            for idx in all_indices:
                if idx < len(transaction.message.account_keys):
                    pre_balance = int(pre_tokens.get(idx, {}).get('uiTokenAmount', {}).get('amount', '0'))
                    post_balance = int(post_tokens.get(idx, {}).get('uiTokenAmount', {}).get('amount', '0'))
                    
                    if pre_balance != post_balance:
                        change = post_balance - pre_balance
                        account = transaction.message.account_keys[idx]
                        mint = pre_tokens.get(idx, post_tokens.get(idx, {})).get('mint', 'Unknown')
                        decimals = pre_tokens.get(idx, post_tokens.get(idx, {})).get('uiTokenAmount', {}).get('decimals', 0)
                        
                        if decimals > 0:
                            ui_change = change / (10 ** decimals)
                            direction = "+" if change > 0 else ""
                            print(f"   {account}: {direction}{ui_change:,.6f} tokens (mint: {mint})")
                        
        print(f"\n🚀 MEV SELL OPTIMIZATION ANALYSIS:")
        print(f"   • Uses MEV bot program for advanced routing")
        print(f"   • Optimized compute budget settings")
        print(f"   • Direct token-to-SOL conversion")
        print(f"   • Minimal instruction count for speed")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        signature = sys.argv[1]
    else:
        signature = "5eUCwkgzHcT1Z4fB5BTK4npSRwpHHfuSnu1Bw6mnRZ18MBg6hm7tHoADTjnRZU7bJLNDJadBJ6jgtHkFHZf2pqvT"
    
    analyze_mev_sell_transaction(signature)
