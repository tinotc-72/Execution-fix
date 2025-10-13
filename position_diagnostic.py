#!/usr/bin/env python3
"""
Position Diagnostic Tool
========================

This tool checks:
1. Current token positions in your wallet
2. Recent transactions from target wallets
3. Whether sells were missed due to WebSocket timeout

"""

import asyncio
import json
from datetime import datetime, timedelta
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.commitment import Processed, Finalized
from config import WALLET
from env_keys import EnvKeys

env = EnvKeys()

async def check_current_positions():
    """Check current token positions in wallet"""
    print("🔍 DIAGNOSTIC: Checking current wallet positions...")
    
    try:
        client = AsyncClient(env.HELIUS_RPC_URL)
        wallet_pubkey = WALLET.pubkey()
        
        print(f"   Wallet: {wallet_pubkey}")
        
        # Get SOL balance
        sol_response = await client.get_balance(wallet_pubkey, Processed)
        sol_balance = sol_response.value / 1e9 if sol_response.value else 0
        print(f"   💎 SOL Balance: {sol_balance:.6f}")
        
        # Get all token accounts
        from solana.rpc.types import TokenAccountOpts
        response = await client.get_token_accounts_by_owner(
            wallet_pubkey,
            TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")),
        )
        
        positions_found = []
        
        if response.value:
            print(f"   📊 Found {len(response.value)} token accounts")
            
            for account in response.value:
                try:
                    # Get detailed account info with parsed data
                    account_pubkey = account.pubkey
                    detailed_response = await client.get_account_info(account_pubkey, encoding="jsonParsed")
                    
                    if detailed_response.value and detailed_response.value.data:
                        parsed_info = detailed_response.value.data.parsed['info']
                        mint = parsed_info['mint']
                        token_amount = parsed_info['tokenAmount']
                        ui_amount = float(token_amount['uiAmount'] or 0)
                        
                        if ui_amount > 0.000001:  # Only show positions with meaningful amounts
                            positions_found.append({
                                'mint': mint,
                                'amount': ui_amount,
                                'account': str(account_pubkey)
                            })
                            print(f"   🎯 {mint}: {ui_amount:.6f} tokens")
                            
                except Exception as e:
                    print(f"   ⚠️ Error parsing account {account.pubkey}: {e}")
                    continue
        else:
            print("   ❌ No token accounts found")
        
        await client.close()
        return positions_found
        
    except Exception as e:
        print(f"❌ Error checking positions: {e}")
        return []

async def check_target_wallet_recent_activity(target_wallet: str, hours_back: int = 24):
    """Check recent activity from target wallet"""
    print(f"\n🎯 DIAGNOSTIC: Checking recent activity from {target_wallet[:8]}...")
    
    try:
        client = AsyncClient(env.HELIUS_RPC_URL)
        wallet_pubkey = Pubkey.from_string(target_wallet)
        
        # Get recent transactions (last 24 hours)
        response = await client.get_signatures_for_address(
            wallet_pubkey,
            limit=50  # Check last 50 transactions
        )
        
        recent_trades = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        if response.value:
            print(f"   📊 Found {len(response.value)} recent transactions")
            
            for i, tx_info in enumerate(response.value):
                # Convert blockTime to datetime if available
                if hasattr(tx_info, 'block_time') and tx_info.block_time:
                    tx_time = datetime.fromtimestamp(tx_info.block_time)
                    if tx_time < cutoff_time:
                        continue  # Skip older transactions
                        
                    print(f"   📝 Transaction {i+1}: {tx_info.signature}")
                    print(f"      Time: {tx_time}")
                    print(f"      Slot: {getattr(tx_info, 'slot', 'Unknown')}")
                    
                    # Analyze this transaction
                    try:
                        sig_obj = Signature.from_string(str(tx_info.signature))
                        tx_response = await client.get_transaction(
                            sig_obj,
                            encoding="jsonParsed",
                            commitment=Finalized,
                            max_supported_transaction_version=0
                        )
                        
                        if tx_response.value:
                            # Quick analysis for DEX activity
                            tx_data = tx_response.value
                            
                            # Check for DEX programs in instructions
                            dex_detected = None
                            trade_type = None
                            
                            if hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
                                message = tx_data.transaction.message
                                instructions = message.instructions
                                
                                for instruction in instructions:
                                    try:
                                        program_id = None
                                        if hasattr(instruction, 'program_id'):
                                            program_id = str(instruction.program_id)
                                        elif hasattr(instruction, 'program_id_index'):
                                            if hasattr(message, 'account_keys'):
                                                program_id = str(message.account_keys[instruction.program_id_index])
                                        
                                        if program_id:
                                            dex_programs = {
                                                "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                                                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                                                "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
                                                "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                                                "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
                                                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
                                            }
                                            
                                            if program_id in dex_programs:
                                                dex_detected = dex_programs[program_id]
                                                break
                                                
                                    except Exception as inst_error:
                                        continue
                            
                            # Check token balance changes to determine buy/sell
                            if hasattr(tx_data, 'meta'):
                                meta = tx_data.meta
                                if (hasattr(meta, 'pre_token_balances') and 
                                    hasattr(meta, 'post_token_balances')):
                                    
                                    # Analyze balance changes
                                    for balance in meta.post_token_balances:
                                        if hasattr(balance, 'owner') and str(balance.owner) == target_wallet:
                                            # Check if this is an increase (buy) or decrease (sell)
                                            post_amount = float(balance.ui_token_amount.ui_amount or 0)
                                            
                                            # Find corresponding pre balance
                                            pre_amount = 0
                                            for pre_balance in meta.pre_token_balances:
                                                if (hasattr(pre_balance, 'owner') and 
                                                    str(pre_balance.owner) == target_wallet and
                                                    pre_balance.mint == balance.mint):
                                                    pre_amount = float(pre_balance.ui_token_amount.ui_amount or 0)
                                                    break
                                            
                                            change = post_amount - pre_amount
                                            if abs(change) > 0.000001:
                                                trade_type = 'BUY' if change > 0 else 'SELL'
                                                token_mint = str(balance.mint)
                                                
                                                recent_trades.append({
                                                    'signature': str(tx_info.signature),
                                                    'time': tx_time,
                                                    'type': trade_type,
                                                    'token': token_mint,
                                                    'dex': dex_detected,
                                                    'change': change
                                                })
                                                
                                                print(f"      🎯 TRADE: {trade_type} {token_mint[:8]}... on {dex_detected or 'Unknown'}")
                                                print(f"         Change: {change:+.6f} tokens")
                                                break
                            
                            if not dex_detected:
                                print(f"      📝 Non-trading transaction")
                                
                    except Exception as analyze_error:
                        print(f"      ⚠️ Analysis error: {analyze_error}")
                        
                else:
                    print(f"   📝 Transaction {i+1}: {tx_info.signature} (no timestamp)")
        else:
            print("   ❌ No recent transactions found")
        
        await client.close()
        return recent_trades
        
    except Exception as e:
        print(f"❌ Error checking target wallet activity: {e}")
        return []

async def main():
    """Main diagnostic function"""
    print("🔍 COPY TRADING DIAGNOSTIC TOOL")
    print("=" * 50)
    print("Checking why positions haven't been sold...")
    print()
    
    # Target wallets from your config
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", 
        "HKwCgqkgBjkpuv3b8ZcEJ3oNxsR7Sf4WtbDLoyjkT26J"
    ]
    
    # Step 1: Check current positions
    current_positions = await check_current_positions()
    
    # Step 2: Check recent target wallet activity
    all_recent_trades = []
    for wallet in target_wallets:
        recent_trades = await check_target_wallet_recent_activity(wallet, hours_back=48)
        all_recent_trades.extend(recent_trades)
    
    # Step 3: Analysis
    print(f"\n📊 ANALYSIS:")
    print(f"   Current positions in wallet: {len(current_positions)}")
    print(f"   Recent trades from targets: {len(all_recent_trades)}")
    
    if current_positions:
        print(f"\n🎯 CURRENT POSITIONS:")
        for pos in current_positions:
            print(f"   {pos['mint']}: {pos['amount']:.6f} tokens")
    
    if all_recent_trades:
        print(f"\n📈 RECENT TARGET WALLET ACTIVITY:")
        buy_count = len([t for t in all_recent_trades if t['type'] == 'BUY'])
        sell_count = len([t for t in all_recent_trades if t['type'] == 'SELL'])
        
        print(f"   Buys: {buy_count}")
        print(f"   Sells: {sell_count}")
        
        print(f"\n📝 TRADE DETAILS:")
        for trade in all_recent_trades[-10:]:  # Show last 10 trades
            print(f"   {trade['time']}: {trade['type']} {trade['token'][:8]}... on {trade['dex'] or 'Unknown'}")
    
    # Step 4: Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if current_positions and not any(t['type'] == 'SELL' for t in all_recent_trades[-5:]):
        print(f"   ⚠️ You have positions but recent target activity shows no sells")
        print(f"   🔧 This suggests WebSocket timeout prevented sell detection")
        print(f"   ✅ The timeout fixes should resolve this going forward")
        
    if current_positions:
        print(f"   🔄 Consider manually liquidating current positions if target wallets already sold")
        print(f"   🚀 Restart bot with timeout fixes to prevent future missed sells")
    
    print(f"\n✅ Diagnostic complete!")

if __name__ == "__main__":
    asyncio.run(main())
