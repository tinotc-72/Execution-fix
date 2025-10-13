#!/usr/bin/env python3
"""
Quick diagnostic script to analyze the specific missing transactions
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed, Finalized
import json
from env_keys import EnvKeys

# Initialize environment
env = EnvKeys()

async def analyze_specific_transactions():
    """Analyze the specific transactions that were missed"""
    
    print("🔍 ANALYZING MISSED TRANSACTIONS")
    print("=" * 60)
    
    # The transactions you mentioned
    missed_transactions = [
        "3QvKTUM1F7TJsU3hUdfMRxu5y3L1e1mkUAHgepaVhMg4KWyiVcrf8wGNtaSEwgmJoyNzDyqxLuKqk48ZBuy9QfMJ",
        "5WA2yg9CUtw5Vtwno9XAwYwJjm5S2CVU8rtR43ah1n4x4VX1uNaZQGbL6ePTa3CKjbcBCTx6rCKD8eC"
    ]
    
    target_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    # Initialize RPC client
    rpc_client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        for i, signature_str in enumerate(missed_transactions, 1):
            print(f"\n🔍 TRANSACTION #{i}: {signature_str}")
            print(f"🔗 https://solscan.io/tx/{signature_str}")
            print("-" * 50)
            
            try:
                sig_obj = Signature.from_string(signature_str)
                
                # Try to get transaction with full metadata
                tx_response = await rpc_client.get_transaction(
                    sig_obj,
                    encoding="jsonParsed",
                    commitment=Finalized,
                    max_supported_transaction_version=0
                )
                
                if not tx_response.value:
                    print(f"❌ Transaction not found: {signature_str}")
                    continue
                
                tx = tx_response.value
                
                # Check if target wallet is involved
                account_keys = []
                if hasattr(tx.transaction.message, 'account_keys'):
                    account_keys = [str(key) for key in tx.transaction.message.account_keys]
                
                wallet_involved = target_wallet in account_keys
                print(f"🎯 Target wallet involved: {wallet_involved}")
                
                if wallet_involved:
                    print(f"✅ {target_wallet} IS in this transaction!")
                else:
                    print(f"❌ {target_wallet} NOT in this transaction")
                    print(f"   Account keys found: {len(account_keys)}")
                    for j, key in enumerate(account_keys[:5]):
                        print(f"   [{j}] {key}")
                
                # Check instruction programs
                instructions = tx.transaction.message.instructions
                programs_found = []
                
                for inst in instructions:
                    program_id = None
                    if hasattr(inst, 'program_id'):
                        program_id = str(inst.program_id)
                    elif hasattr(inst, 'program_id_index') and inst.program_id_index < len(account_keys):
                        program_id = account_keys[inst.program_id_index]
                    
                    if program_id and program_id not in programs_found:
                        programs_found.append(program_id)
                
                print(f"💾 Programs used ({len(programs_found)}):")
                for program in programs_found:
                    print(f"   📄 {program}")
                
                # Check metadata for balance changes
                meta = tx.meta
                if meta:
                    pre_token = len(meta.pre_token_balances) if meta.pre_token_balances else 0
                    post_token = len(meta.post_token_balances) if meta.post_token_balances else 0
                    print(f"💰 Token balances: {pre_token} pre → {post_token} post")
                    
                    # Show token balance changes for our wallet
                    if meta.pre_token_balances or meta.post_token_balances:
                        print(f"🔍 Token balance analysis:")
                        
                        wallet_tokens_pre = {}
                        wallet_tokens_post = {}
                        
                        for balance in meta.pre_token_balances:
                            if hasattr(balance, 'owner') and str(balance.owner) == target_wallet:
                                mint = str(balance.mint)
                                amount = float(balance.ui_token_amount.ui_amount or 0)
                                wallet_tokens_pre[mint] = amount
                                print(f"   PRE  {mint[:8]}...: {amount:.6f}")
                        
                        for balance in meta.post_token_balances:
                            if hasattr(balance, 'owner') and str(balance.owner) == target_wallet:
                                mint = str(balance.mint)
                                amount = float(balance.ui_token_amount.ui_amount or 0)
                                wallet_tokens_post[mint] = amount
                                print(f"   POST {mint[:8]}...: {amount:.6f}")
                        
                        # Calculate changes
                        all_mints = set(list(wallet_tokens_pre.keys()) + list(wallet_tokens_post.keys()))
                        for mint in all_mints:
                            pre = wallet_tokens_pre.get(mint, 0)
                            post = wallet_tokens_post.get(mint, 0)
                            change = post - pre
                            if abs(change) > 0.000001:
                                action = "BUY" if change > 0 else "SELL"
                                print(f"   🎯 {action}: {mint[:8]}... Δ{change:+.6f}")
                
                print(f"✅ Transaction analysis complete")
                
            except Exception as e:
                print(f"❌ Error analyzing transaction {signature_str}: {e}")
    
    finally:
        await rpc_client.close()

if __name__ == "__main__":
    asyncio.run(analyze_specific_transactions())
