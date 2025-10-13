#!/usr/bin/env python3
"""
Debug specific transaction to understand why trade detection isn't working
"""

import asyncio
from transaction_history_analyzer import TransactionHistoryAnalyzer
from env_keys import EnvKeys

async def debug_specific_transaction():
    """Debug the specific transaction that was missed"""
    print("🔍 Debugging Specific Transaction")
    print("=" * 60)
    
    # The transaction you mentioned
    signature = "2wdEcuWDtGGoWaPSHoNQ7Re2XxbiPCfS9uWJqTdNUkjqi35rizsdpTHQRwqwjDtt99mbcctG7XSQPtZrLQfwaz3D"
    wallet = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    
    print(f"🎯 Target transaction: {signature}")
    print(f"🎯 Target wallet: {wallet}")
    
    # Initialize environment and analyzer
    env_keys = EnvKeys()
    analyzer = TransactionHistoryAnalyzer(env_keys.HELIUS_RPC_URL, [wallet])
    
    try:
        print("\n🔍 Analyzing specific transaction...")
        
        # Analyze the specific transaction
        trade_info = await analyzer.analyze_transaction_for_trading(signature, wallet)
        
        if trade_info:
            print("\n✅ TRADE DETECTED!")
            print(f"   Type: {trade_info['type']}")
            print(f"   Token: {trade_info['token_mint']}")
            print(f"   Amount: {trade_info['amount']} SOL")
            print(f"   DEX: {trade_info.get('dex', 'Unknown')}")
            print(f"   Timestamp: {trade_info.get('timestamp')}")
            print(f"   SOL Balance Change: {trade_info.get('sol_balance_change')}")
            print(f"   Token Transfers: {trade_info.get('token_transfers')}")
        else:
            print("\n❌ NO TRADE DETECTED")
            print("Let me get more detailed information...")
            
            # Get raw transaction details for debugging
            from solders.signature import Signature
            from solana.rpc.async_api import AsyncClient
            from solana.rpc.commitment import Confirmed
            
            sig_obj = Signature.from_string(signature)
            client = AsyncClient(env_keys.HELIUS_RPC_URL, commitment=Confirmed)
            
            try:
                print(f"\n🔍 Getting raw transaction details...")
                tx_response = await client.get_transaction(
                    sig_obj,
                    encoding="jsonParsed",
                    commitment=Confirmed,
                    max_supported_transaction_version=0
                )
                
                if tx_response.value:
                    transaction = tx_response.value
                    print(f"✅ Transaction retrieved successfully")
                    
                    # Show basic info
                    print(f"\nℹ️ TRANSACTION INFO:")
                    if hasattr(transaction, 'block_time') and transaction.block_time:
                        from datetime import datetime
                        tx_time = datetime.fromtimestamp(transaction.block_time)
                        print(f"   Time: {tx_time}")
                    
                    # Check for metadata
                    meta = None
                    if hasattr(transaction, 'meta'):
                        meta = transaction.meta
                    
                    if meta:
                        print(f"   Error: {meta.err}")
                        print(f"   Fee: {meta.fee}")
                        
                        if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                            print(f"   Pre-balances: {len(meta.pre_balances)}")
                            print(f"   Post-balances: {len(meta.post_balances)}")
                        
                        if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                            pre_token = meta.pre_token_balances or []
                            post_token = meta.post_token_balances or []
                            print(f"   Pre-token-balances: {len(pre_token)}")
                            print(f"   Post-token-balances: {len(post_token)}")
                    
                    # Check instructions
                    instructions = []
                    if hasattr(transaction, 'transaction'):
                        tx_data = transaction.transaction
                        if hasattr(tx_data, 'message') and hasattr(tx_data.message, 'instructions'):
                            instructions = tx_data.message.instructions
                    
                    print(f"   Instructions: {len(instructions)}")
                    
                    # Show program IDs
                    programs = set()
                    for instruction in instructions:
                        if hasattr(instruction, 'program_id'):
                            programs.add(str(instruction.program_id))
                    
                    print(f"\n🏢 PROGRAMS INVOLVED:")
                    for program in programs:
                        dex_name = analyzer.dex_programs.get(program, "Unknown")
                        print(f"   {program} -> {dex_name}")
                    
                    # Check if any known DEX programs are present
                    known_dex_found = any(program in analyzer.dex_programs for program in programs)
                    print(f"\n🎯 Known DEX programs found: {known_dex_found}")
                    
                    if not known_dex_found:
                        print("⚠️ This might be why the transaction wasn't detected as a trade")
                        print("💡 The transaction may use programs not in our DEX database")
                        print("\n🔍 All program IDs found:")
                        for program in programs:
                            print(f"   {program}")
                    
                else:
                    print("❌ Could not retrieve transaction")
            
            finally:
                await client.close()
        
    except Exception as e:
        print(f"❌ Error debugging transaction: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
    
    finally:
        await analyzer.close()

if __name__ == "__main__":
    asyncio.run(debug_specific_transaction())
