#!/usr/bin/env python3

import os
import sys
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import json
import base64

def reverse_engineer_sell_transaction():
    """Reverse engineer the sell transaction to verify bot logic"""
    
    print("🔍 REVERSE ENGINEERING SELL TRANSACTION")
    print("="*60)
    
    # Use the RPC URL directly
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    rpc_client = Client(rpc_url)
    
    # The sell transaction signature
    signature = "34GLAGU9raQ1GHXdmvj4AoNVxSjxV6QQFyG7fUbNrXQTdNFkWkNidJahFNaSwb5jNk7BB6M1PWY9hNKiSDeVhHhP"
    
    print(f"🔍 Transaction: {signature}")
    print()
    
    try:
        # Convert signature to proper format
        from solders.signature import Signature
        sig_obj = Signature.from_string(signature)
        
        # Get transaction with detailed encoding
        print("1️⃣ Fetching transaction with jsonParsed encoding...")
        tx_response = rpc_client.get_transaction(
            sig_obj, 
            encoding="jsonParsed",
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print("❌ Transaction not found with jsonParsed encoding")
            
            # Try with base64 encoding
            print("🔄 Trying with base64 encoding...")
            tx_response = rpc_client.get_transaction(
                sig_obj,
                encoding="base64",
                max_supported_transaction_version=0
            )
            
        if not tx_response.value:
            print("❌ Transaction not found")
            return
            
        transaction = tx_response.value
        print("✅ Transaction found")
        
        # 2. Analyze transaction metadata
        print("\n2️⃣ Analyzing transaction metadata...")
        meta = getattr(transaction, 'meta', None)
        if meta:
            print(f"   Status: {'✅ Success' if not meta.err else '❌ Failed'}")
            print(f"   Fee: {meta.fee / 1e9:.6f} SOL")
            print(f"   Compute units: {getattr(meta, 'units_consumed', 'N/A')}")
            
            # Look for token balance changes (key indicator of sell)
            post_token_balances = getattr(meta, 'post_token_balances', [])
            pre_token_balances = getattr(meta, 'pre_token_balances', [])
            
            if post_token_balances and pre_token_balances:
                print(f"\n   📊 Token Balance Changes:")
                
                # Create balance change map
                pre_balances = {tb.account_index: tb for tb in pre_token_balances}
                post_balances = {tb.account_index: tb for tb in post_token_balances}
                
                all_indices = set(pre_balances.keys()) | set(post_balances.keys())
                
                for index in all_indices:
                    pre_tb = pre_balances.get(index)
                    post_tb = post_balances.get(index)
                    
                    if pre_tb and post_tb and pre_tb.mint == post_tb.mint:
                        pre_amount = float(pre_tb.ui_token_amount.amount) if pre_tb.ui_token_amount.amount else 0
                        post_amount = float(post_tb.ui_token_amount.amount) if post_tb.ui_token_amount.amount else 0
                        change = post_amount - pre_amount
                        
                        if abs(change) > 0:
                            direction = "📈 RECEIVED" if change > 0 else "📉 SOLD"
                            print(f"     Account {index} ({pre_tb.mint[:8]}...): {direction}")
                            print(f"       Before: {pre_amount:,.0f}")
                            print(f"       After: {post_amount:,.0f}")
                            print(f"       Change: {change:+,.0f}")
                            
                            # Identify the wallet owner
                            if hasattr(pre_tb, 'owner'):
                                print(f"       Owner: {pre_tb.owner}")
        else:
            print("   ⚠️ No metadata available")
                                
        # 3. Analyze transaction structure
        print("\n3️⃣ Analyzing transaction structure...")
        tx_data = getattr(transaction, 'transaction', None)
        
        if tx_data:
            if hasattr(tx_data, 'transaction'):
                # For VersionedTransaction
                message = tx_data.transaction.message
            else:
                # For regular Transaction
                message = getattr(tx_data, 'message', None)
                
            if message:
                # Get account keys
                account_keys = getattr(message, 'account_keys', [])
                    
                print(f"   Accounts involved: {len(account_keys)}")
                
                # Look for DEX programs
                dex_programs = {
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM", 
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
                    "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V2"
                }
                
                detected_dexs = []
                for account in account_keys:
                    account_str = str(account.pubkey) if hasattr(account, 'pubkey') else str(account)
                    if account_str in dex_programs:
                        detected_dexs.append(dex_programs[account_str])
                        
                if detected_dexs:
                    print(f"   🏪 DEXs detected: {', '.join(set(detected_dexs))}")
                else:
                    print("   ⚠️ No known DEX programs detected")
                    
                # Analyze instructions
                instructions = getattr(message, 'instructions', [])
                print(f"   Instructions: {len(instructions)}")
                
                for i, instruction in enumerate(instructions):
                    program_id_index = getattr(instruction, 'program_id_index', None)
                    if program_id_index is not None and program_id_index < len(account_keys):
                        program_account = account_keys[program_id_index]
                        program_id = str(program_account.pubkey) if hasattr(program_account, 'pubkey') else str(program_account)
                        
                        if program_id in dex_programs:
                            print(f"     Instruction {i+1}: {dex_programs[program_id]}")
                            
                            # Try to decode instruction data for more details
                            data = getattr(instruction, 'data', None)
                            if data:
                                try:
                                    if isinstance(data, str):
                                        decoded_data = base64.b64decode(data)
                                        print(f"       Data length: {len(decoded_data)} bytes")
                                        print(f"       First 8 bytes (hex): {decoded_data[:8].hex()}")
                                except:
                                    pass
            else:
                print("   ⚠️ Could not access message data")
        else:
            print("   ⚠️ Could not access transaction data")
                    
        # 4. Look at logs for sell patterns
        print("\n4️⃣ Analyzing transaction logs...")
        log_messages = getattr(meta, 'log_messages', []) if meta else []
        if log_messages:
            print(f"   Total log messages: {len(log_messages)}")
            
            # Look for sell-related patterns
            sell_patterns = [
                "TransferChecked",
                "Transfer", 
                "Swap",
                "CloseAccount",
                "SyncNative"
            ]
            
            for pattern in sell_patterns:
                matching_logs = [log for log in log_messages if pattern in log]
                if matching_logs:
                    print(f"   📝 {pattern} operations: {len(matching_logs)}")
                    
            # Show key log messages
            print(f"\n   🔍 Key log messages:")
            for i, log in enumerate(log_messages[:10]):  # First 10 logs
                if any(pattern in log for pattern in sell_patterns):
                    print(f"     {i+1}: {log}")
        else:
            print("   ⚠️ No log messages available")
                    
        # 5. Determine sell characteristics
        print("\n5️⃣ SELL TRANSACTION ANALYSIS:")
        print("-" * 40)
        
        # Check for common sell patterns
        sell_indicators = {
            "has_token_transfers": False,
            "has_sol_increase": False,
            "has_close_account": False,
            "estimated_sell_amount": 0,
            "estimated_sol_received": 0,
            "dex_used": detected_dexs[0] if detected_dexs else "Unknown"
        }
        
        # Analyze SOL balance changes
        if meta:
            pre_balances = getattr(meta, 'pre_balances', [])
            post_balances = getattr(meta, 'post_balances', [])
            
            if len(pre_balances) > 0 and len(post_balances) > 0:
                # First account is usually the signer (seller)
                sol_change = (post_balances[0] - pre_balances[0]) / 1e9
                if sol_change > 0:
                    sell_indicators["has_sol_increase"] = True
                    sell_indicators["estimated_sol_received"] = sol_change
                    
        # Check logs for close account (complete sell)
        if log_messages:
            for log in log_messages:
                if "CloseAccount" in log:
                    sell_indicators["has_close_account"] = True
                if "Transfer" in log:
                    sell_indicators["has_token_transfers"] = True
                    
        # Print analysis
        print(f"   🏪 DEX Used: {sell_indicators['dex_used']}")
        print(f"   💰 SOL Received: {sell_indicators['estimated_sol_received']:.6f} SOL")
        print(f"   📤 Token Transfers: {'✅' if sell_indicators['has_token_transfers'] else '❌'}")
        print(f"   🔒 Account Closed: {'✅' if sell_indicators['has_close_account'] else '❌'}")
        print(f"   📊 Complete Sell: {'✅' if sell_indicators['has_close_account'] else '🔄 Partial'}")
        
        print("\n" + "="*60)
        print("🎯 SELL PATTERN IDENTIFICATION:")
        print("="*60)
        
        if sell_indicators["has_close_account"]:
            print("✅ COMPLETE SELL DETECTED")
            print("   • Entire token balance was sold")
            print("   • Token account was closed")
            print("   • Rent was reclaimed")
        else:
            print("🔄 PARTIAL SELL DETECTED")
            print("   • Only portion of tokens sold")
            print("   • Token account remains open")
            print("   • Proportional selling strategy")
            
        print(f"\n💡 FOR YOUR BOT:")
        print(f"   • Use {sell_indicators['dex_used']} for this type of sell")
        print(f"   • Expect ~{sell_indicators['estimated_sol_received']:.6f} SOL for similar amounts")
        print(f"   • {'Complete' if sell_indicators['has_close_account'] else 'Partial'} sell strategy detected")
        
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reverse_engineer_sell_transaction()
