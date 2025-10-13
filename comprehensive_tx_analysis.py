#!/usr/bin/env python3

"""
Comprehensive Transaction Analysis Tool
Analyzes the specific transaction signature to understand what happened
"""

import asyncio
import json
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def comprehensive_transaction_analysis():
    """Perform comprehensive analysis of the transaction"""
    
    signature = "5Dz5vtE5wmtQi738itycjf7cRmFFWXWMUKQUXXFyuBpbQkTfmtbosSCmX84LtPc5DhTfCoEkb8NUUr9vN68HmTc"
    
    try:
        # Import necessary modules
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.commitment import Finalized
        
        print(f"🔍 COMPREHENSIVE TRANSACTION ANALYSIS")
        print(f"Signature: {signature}")
        print("=" * 100)
        
        # Initialize RPC client with Helius
        rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
        rpc_client = AsyncClient(rpc_url)
        
        # Fetch transaction with finalized commitment
        print("\\n📡 FETCHING TRANSACTION DATA...")
        print("-" * 50)
        
        try:
            from solders.signature import Signature
            sig_obj = Signature.from_string(signature)
            
            response = await rpc_client.get_transaction(
                sig_obj, 
                commitment=Finalized,
                max_supported_transaction_version=0
            )
            
            if not response.value:
                print("❌ Transaction not found or failed to fetch")
                print("   This could mean:")
                print("   - Invalid signature")
                print("   - Transaction too old (pruned from RPC)")
                print("   - RPC node doesn't have this data")
                return
                
            tx_data = response.value.to_json()
            transaction = json.loads(tx_data)
            
            print("✅ Transaction fetched successfully")
            
        except Exception as fetch_error:
            print(f"❌ Failed to fetch transaction: {fetch_error}")
            return
        
        # Parse basic info
        meta = transaction.get('meta', {})
        tx_msg = transaction.get('transaction', {})
        message = tx_msg.get('message', {})
        
        print("\\n📋 BASIC TRANSACTION INFORMATION")
        print("-" * 50)
        
        # Transaction status
        success = meta.get('err') is None
        print(f"✅ Status: {'SUCCESS' if success else 'FAILED'}")
        
        if not success:
            print(f"❌ Error Details: {meta.get('err')}")
        
        # Timing and location
        block_time = transaction.get('blockTime')
        if block_time:
            dt = datetime.fromtimestamp(block_time)
            print(f"🕐 Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        print(f"🎯 Slot: {transaction.get('slot', 'N/A'):,}")
        print(f"💰 Fee Paid: {meta.get('fee', 0):,} lamports ({meta.get('fee', 0) / 1_000_000_000:.9f} SOL)")
        
        # Account information
        account_keys = message.get('accountKeys', [])
        print(f"🔑 Accounts Involved: {len(account_keys)}")
        
        # Instructions
        instructions = message.get('instructions', [])
        print(f"📋 Instructions: {len(instructions)}")
        
        # Token activity
        pre_balances = meta.get('preTokenBalances', [])
        post_balances = meta.get('postTokenBalances', [])
        print(f"🪙 Token Balance Changes: {len(pre_balances)} → {len(post_balances)}")
        
        # Logs
        log_messages = meta.get('logMessages', [])
        print(f"📝 Log Messages: {len(log_messages)}")
        
        # Show account keys
        print("\\n🔑 ACCOUNT KEYS ANALYSIS")
        print("-" * 50)
        
        known_programs = {
            '11111111111111111111111111111111': '🏛️  System Program',
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': '🪙  Token Program',
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': '🔗 Associated Token Program',
            'ComputeBudget111111111111111111111111111111': '⚙️  Compute Budget Program',
            'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': '🪐 Jupiter Aggregator',
            '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': '🌊 Raydium AMM',
            'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK': '🌊 Raydium CLMM',
            '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': '🚀 Pump.fun',
            'DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1': '🐋 Orca',
            'So11111111111111111111111111111111111111112': '💎 Wrapped SOL (WSOL)',
        }
        
        for i, account in enumerate(account_keys[:15]):  # Show first 15 accounts
            label = known_programs.get(account, f"🔍 Unknown: {account[:8]}...")
            signer = "✍️ " if i < message.get('header', {}).get('numRequiredSignatures', 0) else "   "
            print(f"  {i:2d}: {signer}{label}")
            if account in known_programs and '🪐🌊🚀🐋' in label:
                print(f"      ↳ This is a DEX/Trading program!")
        
        if len(account_keys) > 15:
            print(f"  ... and {len(account_keys) - 15} more accounts")
        
        # Analyze instructions
        print("\\n📋 INSTRUCTION ANALYSIS")
        print("-" * 50)
        
        for i, instruction in enumerate(instructions):
            program_id_index = instruction.get('programIdIndex')
            if program_id_index is not None and program_id_index < len(account_keys):
                program_id = account_keys[program_id_index]
                program_name = known_programs.get(program_id, f"Unknown ({program_id[:8]}...)")
            else:
                program_id = instruction.get('programId', 'N/A')
                program_name = known_programs.get(program_id, f"Unknown ({str(program_id)[:8]}...)")
            
            accounts = instruction.get('accounts', [])
            data = instruction.get('data', '')
            
            print(f"  Instruction {i+1}:")
            print(f"    Program: {program_name}")
            print(f"    Accounts: {len(accounts)} referenced")
            print(f"    Data: {len(data)} bytes")
        
        # Token balance analysis
        if pre_balances or post_balances:
            print("\\n💰 TOKEN BALANCE CHANGES")
            print("-" * 50)
            
            # Create comprehensive balance change map
            balance_changes = {}
            
            # Process pre-balances
            for balance in pre_balances:
                owner = balance.get('owner', 'N/A')
                mint = balance.get('mint', 'N/A')
                amount_info = balance.get('uiTokenAmount', {})
                amount = float(amount_info.get('uiAmountString', '0'))
                decimals = amount_info.get('decimals', 0)
                
                key = (owner, mint)
                balance_changes[key] = {
                    'pre_amount': amount,
                    'post_amount': 0,
                    'decimals': decimals,
                    'owner': owner,
                    'mint': mint
                }
            
            # Process post-balances
            for balance in post_balances:
                owner = balance.get('owner', 'N/A')
                mint = balance.get('mint', 'N/A')
                amount_info = balance.get('uiTokenAmount', {})
                amount = float(amount_info.get('uiAmountString', '0'))
                decimals = amount_info.get('decimals', 0)
                
                key = (owner, mint)
                if key in balance_changes:
                    balance_changes[key]['post_amount'] = amount
                else:
                    balance_changes[key] = {
                        'pre_amount': 0,
                        'post_amount': amount,
                        'decimals': decimals,
                        'owner': owner,
                        'mint': mint
                    }
            
            # Show significant changes
            significant_changes = []
            for key, change in balance_changes.items():
                delta = change['post_amount'] - change['pre_amount']
                if abs(delta) > 0.000001:  # Only meaningful changes
                    significant_changes.append((key, change, delta))
            
            if significant_changes:
                print("\\n  📊 Significant Balance Changes:")
                for (owner, mint), change, delta in significant_changes:
                    direction = "📈" if delta > 0 else "📉"
                    action = "RECEIVED" if delta > 0 else "SENT"
                    
                    print(f"    {direction} {owner[:8]}... {action} {abs(delta):,.6f}")
                    print(f"        Token: {mint[:8]}...")
                    print(f"        Before: {change['pre_amount']:,.6f}")
                    print(f"        After: {change['post_amount']:,.6f}")
                    print()
            else:
                print("  ℹ️  No significant token balance changes detected")
        
        # Log analysis
        if log_messages:
            print("\\n📝 TRANSACTION LOGS ANALYSIS")
            print("-" * 50)
            
            # Look for important patterns in logs
            swap_logs = []
            error_logs = []
            program_logs = []
            
            for log in log_messages:
                if any(keyword in log.lower() for keyword in ['swap', 'trade', 'exchange']):
                    swap_logs.append(log)
                elif any(keyword in log.lower() for keyword in ['error', 'failed', 'insufficient']):
                    error_logs.append(log)
                elif 'Program' in log and 'invoke' in log:
                    program_logs.append(log)
            
            if error_logs:
                print("  ❌ Error-related logs:")
                for log in error_logs:
                    print(f"    {log}")
                print()
            
            if swap_logs:
                print("  🔄 Swap-related logs:")
                for log in swap_logs:
                    print(f"    {log}")
                print()
            
            print("  📋 First 10 log messages:")
            for i, log in enumerate(log_messages[:10]):
                print(f"    {i+1:2d}: {log}")
            
            if len(log_messages) > 10:
                print(f"    ... and {len(log_messages) - 10} more log messages")
        
        # Try to determine transaction purpose
        print("\\n🎯 TRANSACTION PURPOSE ANALYSIS")
        print("-" * 50)
        
        purposes = []
        
        # Check for DEX activity
        dex_programs_found = []
        for account in account_keys:
            if account in known_programs and any(emoji in known_programs[account] for emoji in ['🪐', '🌊', '🚀', '🐋']):
                dex_programs_found.append(known_programs[account])
        
        if dex_programs_found:
            purposes.append(f"🔄 DEX Trading via: {', '.join(dex_programs_found)}")
        
        # Check for token transfers
        if significant_changes:
            purposes.append(f"💸 Token Transfer ({len(significant_changes)} balance changes)")
        
        # Check for program deployment/interaction
        unique_programs = set()
        for instruction in instructions:
            program_id = instruction.get('programId')
            if program_id and program_id not in ['11111111111111111111111111111111', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA']:
                unique_programs.add(program_id)
        
        if unique_programs:
            purposes.append(f"⚙️  Program Interaction ({len(unique_programs)} programs)")
        
        if purposes:
            print("  Detected purposes:")
            for purpose in purposes:
                print(f"    {purpose}")
        else:
            print("  🤔 Purpose unclear - might be a simple transfer or failed transaction")
        
        print("\\n" + "=" * 100)
        print("🏁 ANALYSIS COMPLETE")
        print("\\nKey Findings:")
        print(f"• Transaction {'succeeded' if success else 'failed'}")
        print(f"• Involved {len(account_keys)} accounts and {len(instructions)} instructions")
        print(f"• Paid {meta.get('fee', 0):,} lamports in fees")
        if dex_programs_found:
            print(f"• Used DEX platforms: {', '.join(dex_programs_found)}")
        if significant_changes:
            print(f"• Made {len(significant_changes)} significant token balance changes")
        
        await rpc_client.close()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(comprehensive_transaction_analysis())