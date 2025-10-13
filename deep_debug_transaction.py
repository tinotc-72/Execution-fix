#!/usr/bin/env python3
"""
Advanced transaction debugging to examine transaction structure in detail
"""

import asyncio
import json
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from env_keys import EnvKeys

async def deep_debug_transaction():
    """Deep debug of the specific transaction structure"""
    print("🔬 DEEP TRANSACTION ANALYSIS")
    print("=" * 70)
    
    # The transaction you mentioned
    signature = "2wdEcuWDtGGoWaPSHoNQ7Re2XxbiPCfS9uWJqTdNUkjqi35rizsdpTHQRwqwjDtt99mbcctG7XSQPtZrLQfwaz3D"
    wallet = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    
    print(f"🎯 Target transaction: {signature}")
    print(f"🎯 Target wallet: {wallet}")
    
    # Initialize environment
    env_keys = EnvKeys()
    sig_obj = Signature.from_string(signature)
    client = AsyncClient(env_keys.HELIUS_RPC_URL, commitment=Confirmed)
    
    try:
        print(f"\n📡 Fetching transaction with different encodings...")
        
        # Try different encodings
        encodings = ["jsonParsed", "json", "base64", "base58"]
        
        for encoding in encodings:
            try:
                print(f"\n🔍 Trying encoding: {encoding}")
                tx_response = await client.get_transaction(
                    sig_obj,
                    encoding=encoding,
                    commitment=Confirmed,
                    max_supported_transaction_version=0
                )
                
                if tx_response.value:
                    transaction = tx_response.value
                    print(f"✅ Success with {encoding}")
                    
                    # Basic transaction info
                    print(f"\n📊 TRANSACTION STRUCTURE:")
                    print(f"   Type: {type(transaction)}")
                    
                    if hasattr(transaction, 'block_time') and transaction.block_time:
                        from datetime import datetime
                        tx_time = datetime.fromtimestamp(transaction.block_time)
                        print(f"   Block time: {tx_time}")
                    
                    if hasattr(transaction, 'slot'):
                        print(f"   Slot: {transaction.slot}")
                    
                    # Metadata analysis
                    meta = None
                    if hasattr(transaction, 'meta'):
                        meta = transaction.meta
                        print(f"\n💰 METADATA:")
                        print(f"   Error: {meta.err}")
                        print(f"   Fee: {meta.fee}")
                        
                        # Balance changes
                        if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                            pre_balances = meta.pre_balances
                            post_balances = meta.post_balances
                            print(f"   Account balances: {len(pre_balances)} accounts")
                            
                            for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                                if pre != post:
                                    change = (post - pre) / 1e9  # Convert to SOL
                                    print(f"      Account {i}: {change:+.9f} SOL")
                        
                        # Token balance changes
                        if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                            pre_token = meta.pre_token_balances or []
                            post_token = meta.post_token_balances or []
                            print(f"   Pre-token balances: {len(pre_token)}")
                            print(f"   Post-token balances: {len(post_token)}")
                            
                            if pre_token or post_token:
                                print(f"   🪙 TOKEN CHANGES:")
                                
                                # Create dictionaries for easier comparison
                                pre_dict = {(tb.account_index, tb.mint): tb.ui_token_amount.ui_amount for tb in pre_token}
                                post_dict = {(tb.account_index, tb.mint): tb.ui_token_amount.ui_amount for tb in post_token}
                                
                                all_keys = set(pre_dict.keys()) | set(post_dict.keys())
                                
                                for (account_idx, mint) in all_keys:
                                    pre_amt = pre_dict.get((account_idx, mint), 0) or 0
                                    post_amt = post_dict.get((account_idx, mint), 0) or 0
                                    
                                    if abs(pre_amt - post_amt) > 0.000001:  # Significant change
                                        change = post_amt - pre_amt
                                        print(f"      Account {account_idx}, Token {mint[:8]}...: {change:+.6f}")
                        
                        # Log messages
                        if hasattr(meta, 'log_messages') and meta.log_messages:
                            print(f"\n📝 LOG MESSAGES ({len(meta.log_messages)}):")
                            for i, log in enumerate(meta.log_messages[:10]):  # Show first 10
                                print(f"      {i}: {log}")
                            if len(meta.log_messages) > 10:
                                print(f"      ... and {len(meta.log_messages) - 10} more")
                    
                    # Transaction message analysis
                    if hasattr(transaction, 'transaction'):
                        tx_data = transaction.transaction
                        print(f"\n📋 TRANSACTION MESSAGE:")
                        
                        if hasattr(tx_data, 'message'):
                            message = tx_data.message
                            
                            # Account keys
                            if hasattr(message, 'account_keys'):
                                account_keys = message.account_keys
                                print(f"   Account keys: {len(account_keys)}")
                                
                                # Check if our wallet is in the account keys
                                wallet_index = -1
                                for i, key in enumerate(account_keys):
                                    if str(key) == wallet:
                                        wallet_index = i
                                        print(f"      Target wallet at index: {i}")
                                        break
                            
                            # Instructions
                            if hasattr(message, 'instructions'):
                                instructions = message.instructions
                                print(f"   Instructions: {len(instructions)}")
                                
                                for i, instruction in enumerate(instructions):
                                    print(f"      Instruction {i}:")
                                    
                                    if hasattr(instruction, 'program_id'):
                                        program_id = str(instruction.program_id)
                                        print(f"         Program ID: {program_id}")
                                        
                                        # Check known DEXes
                                        dex_programs = {
                                            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                                            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
                                            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                                            "27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv": "Raydium CPMM",
                                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                                            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Whirlpool",
                                            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
                                        }
                                        
                                        if program_id in dex_programs:
                                            print(f"         🎯 DEX: {dex_programs[program_id]}")
                                        else:
                                            print(f"         ❓ Unknown program")
                                    
                                    if hasattr(instruction, 'accounts'):
                                        print(f"         Accounts: {len(instruction.accounts)}")
                                    
                                    if hasattr(instruction, 'data'):
                                        print(f"         Data length: {len(instruction.data) if instruction.data else 0}")
                    
                    break  # Use first successful encoding
                
                else:
                    print(f"❌ Failed with {encoding}")
                    
            except Exception as e:
                print(f"❌ Error with {encoding}: {e}")
        
        # Also check if this transaction appears in recent signatures
        print(f"\n🔍 Checking if transaction appears in recent signatures...")
        from solders.pubkey import Pubkey
        
        wallet_pubkey = Pubkey.from_string(wallet)
        recent_sigs = await client.get_signatures_for_address(wallet_pubkey, limit=20)
        
        if recent_sigs.value:
            found_in_recent = False
            for i, sig_info in enumerate(recent_sigs.value):
                if str(sig_info.signature) == signature:
                    found_in_recent = True
                    print(f"✅ Transaction found at position {i} in recent signatures")
                    print(f"   Block time: {sig_info.block_time}")
                    print(f"   Confirmation status: {getattr(sig_info, 'confirmation_status', 'Unknown')}")
                    print(f"   Error: {sig_info.err}")
                    break
            
            if not found_in_recent:
                print(f"⚠️ Transaction NOT found in recent 20 signatures")
                print(f"💡 This might be why your bot missed it - timing issue")
        
    except Exception as e:
        print(f"❌ Error in deep analysis: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(deep_debug_transaction())
