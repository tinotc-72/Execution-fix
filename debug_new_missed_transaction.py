#!/usr/bin/env python3
"""
Debug script to analyze another missed transaction
"""
import asyncio
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
import env_keys

async def debug_new_missed_transaction():
    """Analyze the new missed transaction"""
    
    # The new transaction you're asking about
    signature = "2i2Y5X4gwcFkLRoYxjbQEe3hdqQsGW3Q1tm76gTxm8jeK3pxKdzNDpiZy6UQc8SBGAyAgVLACrYq9LvL32Xea27M"
    
    print("🔍 DEBUG: NEW MISSED TRANSACTION ANALYSIS")
    print("=" * 60)
    print(f"📝 Signature: {signature}")
    print(f"📏 Signature length: {len(signature)} chars (standard is 88)")
    print("")
    
    # Initialize RPC client
    env = env_keys.EnvKeys()
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        print("🔍 Step 1: Fetching transaction details...")
        
        # Get the transaction
        sig_obj = Signature.from_string(signature)
        tx_response = await client.get_transaction(
            sig_obj, 
            encoding="json", 
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print("❌ TRANSACTION NOT FOUND!")
            print("   Possible reasons:")
            print("   1. Signature is incorrect")
            print("   2. Transaction is too old (beyond RPC retention)")
            print("   3. Transaction failed and was not confirmed")
            return
        
        tx = tx_response.value
        print("✅ Transaction found!")
        
        # Basic transaction info
        print(f"   🕐 Block time: {datetime.fromtimestamp(tx.block_time) if tx.block_time else 'Unknown'}")
        print(f"   📦 Slot: {tx.slot}")
        print(f"   ✅ Success: {tx.transaction.meta.err is None}")
        
        if tx.transaction.meta.err:
            print(f"   ❌ Error: {tx.transaction.meta.err}")
            print("   → Failed transactions are typically ignored by copy trading bots")
            return
        
        print("")
        print("🔍 Step 2: Checking wallet involvement...")
        
        # Get account keys
        accounts = tx.transaction.transaction.message.account_keys
        
        # Check both target wallets
        target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        
        target_found = None
        target_account_index = None
        is_target_signer = False
        
        for wallet in target_wallets:
            target_pubkey = Pubkey.from_string(wallet)
            for i, account in enumerate(accounts):
                if account == target_pubkey:
                    target_found = wallet
                    target_account_index = i
                    # Check if this account is a signer
                    is_target_signer = i < tx.transaction.transaction.message.header.num_required_signatures
                    break
            if target_found:
                break
        
        if target_found:
            print(f"✅ Target wallet found: {target_found[:8]}... (index {target_account_index})")
            print(f"   🖊️  Is signer: {is_target_signer}")
            if not is_target_signer:
                print("   ⚠️  Target wallet is NOT a signer - this might be a passive involvement")
        else:
            print("❌ Neither target wallet found in transaction!")
            print("   This transaction does not involve either of your target wallets")
            return
        
        print("")
        print("🔍 Step 3: Analyzing DEX programs...")
        
        # Updated DEX programs dictionary (including our fix)
        dex_programs = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",  # FIXED
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Legacy",
            "PhoeNiX7VmQJCM2U2DLCLfJcGKFnZAJQ3rYJhFQJ8qoH": "Phoenix",
            "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
            "11111111111111111111111111111111": "System Program",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program"
        }
        
        instructions = tx.transaction.transaction.message.instructions
        dexes_detected = []
        unknown_programs = []
        
        print(f"   📋 Total instructions: {len(instructions)}")
        
        for i, instruction in enumerate(instructions):
            program_id = str(accounts[instruction.program_id_index])
            
            if program_id in dex_programs:
                dex_name = dex_programs[program_id]
                if "DEX" in dex_name or any(keyword in dex_name for keyword in ["Jupiter", "Raydium", "Pump.fun", "Orca", "Phoenix"]):
                    dexes_detected.append(dex_name)
                    print(f"   {i+1}. 🎯 DEX DETECTED: {dex_name}")
                else:
                    print(f"   {i+1}. ✅ {dex_name}")
                print(f"      Program ID: {program_id}")
            else:
                unknown_programs.append(program_id)
                print(f"   {i+1}. ❓ UNKNOWN: {program_id}")
        
        if not dexes_detected:
            print("   ⚠️  No known DEX programs detected!")
            print("   This might be a direct transfer, unknown DEX, or new program")
        
        print("")
        print("🔍 Step 4: Token analysis...")
        
        # Check for token mints in pre/post balances
        pre_balances = tx.transaction.meta.pre_token_balances or []
        post_balances = tx.transaction.meta.post_token_balances or []
        
        tokens_involved = set()
        for balance in pre_balances + post_balances:
            if hasattr(balance, 'mint'):
                tokens_involved.add(balance.mint)
        
        print(f"   🪙 Tokens involved: {len(tokens_involved)}")
        for token in tokens_involved:
            print(f"      {token}")
        
        # Check SOL balance changes for target wallet
        if target_account_index is not None and target_account_index < len(tx.transaction.meta.pre_balances):
            pre_sol_balances = tx.transaction.meta.pre_balances
            post_sol_balances = tx.transaction.meta.post_balances
            
            pre_sol = pre_sol_balances[target_account_index] / 1e9
            post_sol = post_sol_balances[target_account_index] / 1e9
            sol_change = post_sol - pre_sol
            
            print("")
            print(f"   💰 Target wallet SOL change: {sol_change:+.6f} SOL")
            if sol_change < -0.001:  # Significant decrease
                print(f"      → SOL decreased significantly (likely a BUY)")
            elif sol_change > 0.001:  # Significant increase
                print(f"      → SOL increased significantly (likely a SELL)")
            else:
                print(f"      → Minimal SOL change")
        
        print("")
        print("🔍 Step 5: Why was this transaction missed?")
        print("")
        
        # Analysis of potential issues
        reasons = []
        
        if not is_target_signer:
            reasons.append("❓ Target wallet was not a signer (passive involvement)")
        
        if not dexes_detected:
            reasons.append("❓ No known DEX programs detected")
        
        if unknown_programs:
            reasons.append(f"❓ Unknown programs present: {len(unknown_programs)} programs")
            for prog in unknown_programs[:3]:  # Show first 3
                reasons.append(f"   → {prog}")
        
        if not tokens_involved:
            reasons.append("❓ No token mints detected in pre/post balances")
        
        if reasons:
            print("🤔 POTENTIAL REASONS FOR MISSING THIS TRANSACTION:")
            for reason in reasons:
                print(f"   {reason}")
        else:
            print("❗ THIS TRANSACTION SHOULD HAVE BEEN DETECTED!")
            print("   The transaction has all the characteristics needed for detection")
        
        print("")
        print("💡 NEXT STEPS:")
        if unknown_programs:
            print("   → Research the unknown programs to see if they're new DEXes")
            print("   → Check if any unknown programs are trading-related")
        if not is_target_signer:
            print("   → Verify if your system requires target wallet to be a signer")
        print("   → Check WebSocket logs for timing of this transaction")
        print("   → Verify your target wallet addresses are correct")
        
        return {
            "transaction_found": True,
            "target_wallet": target_found,
            "target_involved": target_found is not None,
            "target_is_signer": is_target_signer,
            "dexes_detected": dexes_detected,
            "unknown_programs": unknown_programs,
            "tokens_involved": list(tokens_involved),
            "should_have_been_detected": bool(dexes_detected and is_target_signer)
        }
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {"error": str(e)}
    
    finally:
        await client.close()

if __name__ == "__main__":
    result = asyncio.run(debug_new_missed_transaction())
    print("")
    print("🔍 ANALYSIS COMPLETE")
