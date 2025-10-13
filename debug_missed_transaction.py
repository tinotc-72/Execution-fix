#!/usr/bin/env python3
"""
Debug script to analyze why a specific transaction was missed
"""
import asyncio
import sys
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import env_keys

async def debug_missed_transaction():
    """Analyze the specific missed transaction"""
    
    # The transaction you're asking about
    signature = "2wdEcuWDtGGoWaPSHoNQ7Re2XxbiPCfS9uWJqTdNUkjqi35rizsdpTHQRwqwjDtt99mbcctG7XSQPtZrLQfwaz3D"
    target_wallet = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    
    print("🔍 DEBUG: MISSED TRANSACTION ANALYSIS")
    print("=" * 60)
    print(f"📝 Signature: {signature}")
    print(f"👤 Target wallet: {target_wallet}")
    print(f"📏 Signature length: {len(signature)} chars (standard is 88)")
    print("")
    
    # Initialize RPC client
    env = env_keys.EnvKeys()
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        print("🔍 Step 1: Fetching transaction details...")
        
        # Get the transaction
        from solders.signature import Signature
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
        target_pubkey = Pubkey.from_string(target_wallet)
        
        is_target_signer = False
        target_account_index = None
        
        for i, account in enumerate(accounts):
            if account == target_pubkey:
                target_account_index = i
                # Check if this account is a signer
                is_target_signer = i < tx.transaction.transaction.message.header.num_required_signatures
                break
        
        if target_account_index is not None:
            print(f"✅ Target wallet found in transaction (index {target_account_index})")
            print(f"   🖊️  Is signer: {is_target_signer}")
            if not is_target_signer:
                print("   ⚠️  Target wallet is NOT a signer - this might be a passive involvement")
        else:
            print("❌ Target wallet NOT found in transaction!")
            print("   This transaction does not involve the target wallet directly")
            return
        
        print("")
        print("🔍 Step 3: Analyzing DEX programs...")
        
        # Known DEX programs
        dex_programs = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium V4",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca",
            "PhoeNiX7VmQJCM2U2DLCLfJcGKFnZAJQ3rYJhFQJ8qoH": "Phoenix"
        }
        
        instructions = tx.transaction.transaction.message.instructions
        dexes_detected = []
        
        print(f"   📋 Total instructions: {len(instructions)}")
        
        for i, instruction in enumerate(instructions):
            program_id = str(accounts[instruction.program_id_index])
            
            if program_id in dex_programs:
                dex_name = dex_programs[program_id]
                dexes_detected.append(dex_name)
                print(f"   {i+1}. 🎯 DEX DETECTED: {dex_name}")
                print(f"      Program ID: {program_id}")
            else:
                print(f"   {i+1}. Program: {program_id[:8]}...")
        
        if not dexes_detected:
            print("   ⚠️  No known DEX programs detected!")
            print("   This might be a direct transfer or unknown DEX")
        
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
        
        # Check SOL balance changes
        pre_sol_balances = tx.transaction.meta.pre_balances
        post_sol_balances = tx.transaction.meta.post_balances
        
        if target_account_index is not None and target_account_index < len(pre_sol_balances):
            pre_sol = pre_sol_balances[target_account_index] / 1e9
            post_sol = post_sol_balances[target_account_index] / 1e9
            sol_change = post_sol - pre_sol
            
            print("")
            print(f"   💰 Target wallet SOL change: {sol_change:+.6f} SOL")
            if sol_change < 0:
                print(f"      → SOL decreased (likely a BUY)")
            elif sol_change > 0:
                print(f"      → SOL increased (likely a SELL)")
            else:
                print(f"      → No SOL change (might be token-to-token swap)")
        
        print("")
        print("🔍 Step 5: Why might this have been missed?")
        print("")
        
        # Analysis of potential issues
        reasons = []
        
        if not is_target_signer:
            reasons.append("❓ Target wallet was not a signer (passive involvement)")
        
        if not dexes_detected:
            reasons.append("❓ No known DEX programs detected")
        
        if len(signature) != 88:
            reasons.append("❓ Unusual signature length")
        
        if not tokens_involved:
            reasons.append("❓ No token mints detected in pre/post balances")
        
        if reasons:
            print("🤔 POTENTIAL REASONS FOR MISSING THIS TRANSACTION:")
            for reason in reasons:
                print(f"   {reason}")
        else:
            print("❗ THIS TRANSACTION SHOULD HAVE BEEN DETECTED!")
            print("   The transaction has all the characteristics of a tradable DEX transaction")
            print("   This suggests there might be an issue with:")
            print("   1. WebSocket subscription not receiving this transaction")
            print("   2. Transaction processing logic filtering it out")
            print("   3. Timing issue (transaction processed before system was monitoring)")
        
        print("")
        print("💡 RECOMMENDATIONS:")
        if not is_target_signer:
            print("   → Check if your system only monitors transactions where target wallet is a signer")
        if dexes_detected:
            print(f"   → Ensure your system recognizes these DEXes: {', '.join(dexes_detected)}")
        print("   → Check WebSocket logs around the transaction time")
        print("   → Verify target wallet addresses in your configuration")
        print("   → Test with a known working transaction from the same wallet")
        
        return {
            "transaction_found": True,
            "target_involved": target_account_index is not None,
            "target_is_signer": is_target_signer,
            "dexes_detected": dexes_detected,
            "tokens_involved": list(tokens_involved),
            "should_have_been_detected": bool(dexes_detected and is_target_signer)
        }
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {"error": str(e)}
    
    finally:
        await client.close()

if __name__ == "__main__":
    result = asyncio.run(debug_missed_transaction())
    print("")
    print("🔍 DEBUG COMPLETE")
