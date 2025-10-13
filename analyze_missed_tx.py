#!/usr/bin/env python3
"""
Analyze why the copy trading bot missed a specific transaction
"""
import asyncio
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Finalized
from datetime import datetime
import sys

async def analyze_missed_transaction():
    """Analyze the specific missed transaction"""
    
    # The transaction we're investigating
    missed_signature = '31VWBmdGocG89E4bx1BtGZhi7TETNj6obpPPGfs19N3Zbyc2qPRxAhKpvRnqiX6gy1hv88SnVC5gXwR4kjYxzeKB'
    target_wallet = 'DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj'
    
    print(f"🔍 INVESTIGATING MISSED TRANSACTION")
    print(f"=" * 60)
    print(f"Transaction: {missed_signature}")
    print(f"Target Wallet: {target_wallet}")
    print(f"Bot was monitoring this wallet: ✅ YES")
    print(f"")
    
    client = AsyncClient('https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315')
    
    try:
        # Get the transaction details
        print("📡 Fetching transaction details...")
        tx_response = await client.get_transaction(
            Signature.from_string(missed_signature),
            commitment=Finalized,
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print("❌ Transaction not found or not accessible")
            return
        
        tx = tx_response.value
        print("✅ Transaction found!")
        print(f"")
        
        # Transaction timing
        if tx.block_time:
            tx_time = datetime.fromtimestamp(tx.block_time)
            print(f"🕐 Transaction Time: {tx_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   Block Time: {tx.block_time}")
            print(f"   Slot: {tx.slot}")
        
        # Success status
        success = not bool(tx.transaction.meta.err) if tx.transaction.meta else "Unknown"
        print(f"✅ Transaction Success: {success}")
        
        if tx.transaction.meta and tx.transaction.meta.err:
            print(f"❌ Transaction Error: {tx.transaction.meta.err}")
        
        print(f"")
        
        # Analyze accounts involved
        if hasattr(tx.transaction, 'transaction') and hasattr(tx.transaction.transaction, 'message'):
            message = tx.transaction.transaction.message
            
            if hasattr(message, 'account_keys'):
                account_keys = [str(key) for key in message.account_keys]
                
                # Check if target wallet is involved
                wallet_involved = target_wallet in account_keys
                print(f"🎯 Target Wallet Involved: {wallet_involved}")
                
                if wallet_involved:
                    wallet_index = account_keys.index(target_wallet)
                    print(f"   Position in accounts: {wallet_index}")
                    print(f"   Role: {'Signer' if wallet_index == 0 else 'Participant'}")
                else:
                    print(f"⚠️  Target wallet NOT found in transaction accounts!")
                    print(f"   This explains why the bot missed it - wallet not involved")
                
                print(f"")
                print(f"📋 All Accounts ({len(account_keys)} total):")
                for i, account in enumerate(account_keys):
                    marker = ' 🎯 TARGET' if account == target_wallet else ''
                    signer_marker = ' 🔑 SIGNER' if i == 0 else ''
                    print(f"   {i:2d}: {account}{marker}{signer_marker}")
                
                print(f"")
            
            # Analyze programs/DEXes used
            if hasattr(message, 'instructions'):
                print(f"🏗️  Instructions Analysis ({len(message.instructions)} instructions):")
                
                dex_programs = {
                    'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter V6',
                    'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB': 'Jupiter V4', 
                    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium V4',
                    'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C': 'Raydium CPMM V2',
                    '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
                    'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpool',
                    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': 'SPL Token',
                    'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': 'Associated Token',
                    '11111111111111111111111111111111': 'System Program',
                    'ComputeBudget111111111111111111111111111111': 'Compute Budget'
                }
                
                detected_dex = None
                for i, instruction in enumerate(message.instructions):
                    program_id = str(message.account_keys[instruction.program_id_index])
                    program_name = dex_programs.get(program_id, f'Unknown ({program_id[:8]}...)')
                    
                    if program_id in ['JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 
                                    'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB',
                                    '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',
                                    'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C',
                                    '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',
                                    'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc']:
                        detected_dex = program_name
                    
                    print(f"   {i}: {program_name}")
                
                if detected_dex:
                    print(f"")
                    print(f"🏢 PRIMARY DEX DETECTED: {detected_dex}")
                    print(f"   Bot should have detected this as a tradeable transaction")
                
        print(f"")
        print(f"🔍 DIAGNOSIS:")
        print(f"=" * 40)
        
        if not wallet_involved:
            print(f"❌ REASON: Target wallet was NOT involved in this transaction")
            print(f"   - The transaction exists but doesn't involve your monitored wallet")
            print(f"   - This is why your bot correctly ignored it")
            print(f"   - Check if you're looking at the wrong wallet or transaction")
        else:
            print(f"⚠️  POTENTIAL ISSUE: Target wallet WAS involved but bot missed it")
            print(f"   Possible reasons:")
            print(f"   1. 🕐 Timing: Bot wasn't running at {tx_time}")
            print(f"   2. 🔌 WebSocket: Connection issue during this time") 
            print(f"   3. 🏗️  Transaction type: Filtered out by bot logic")
            print(f"   4. ⚡ Speed: Transaction processed too quickly")
            print(f"   5. 🔄 Retry: Bot was in retry loop and missed new transactions")
        
        # Check if this was a successful trade
        if success and detected_dex:
            print(f"")
            print(f"💹 TRADE ANALYSIS:")
            print(f"   ✅ This was a successful {detected_dex} transaction")
            print(f"   🎯 Bot should have attempted to copy this")
            print(f"   📊 Check bot logs around {tx_time} for any activity")
            
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    print("🤖 Copy Trading Bot - Transaction Analysis Tool")
    print("=" * 60)
    asyncio.run(analyze_missed_transaction())
