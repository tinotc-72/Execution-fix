#!/usr/bin/env python3
"""
Analyze a specific transaction to understand what happened
"""

import asyncio
import sys
from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
from solana.rpc.async_api import AsyncClient
from env_keys import EnvKeys

async def analyze_transaction(signature: str):
    """Analyze a specific transaction"""
    try:
        print(f"🔍 ANALYZING TRANSACTION: {signature}")
        print("=" * 80)
        
        # Initialize RPC client
        env_keys = EnvKeys()
        rpc_client = AsyncClient(env_keys.HELIUS_RPC_URL)
        
        # Initialize analyzer
        analyzer = OfficialWalletPerspectiveAnalyzer(rpc_client)
        
        # Your target wallets from config
        target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        
        print(f"🎯 CHECKING TRANSACTION FOR TARGET WALLETS:")
        for i, wallet in enumerate(target_wallets):
            print(f"   [{i+1}] {wallet}")
        print()
        
        # Analyze for each target wallet
        for i, wallet in enumerate(target_wallets):
            print(f"🔍 [{i+1}/2] ANALYZING FOR WALLET: {wallet[:8]}...")
            
            result = await analyzer.analyze_wallet_action(signature, wallet)
            
            if result:
                print(f"✅ RESULT FOR {wallet[:8]}:")
                print(f"   🎯 Action: {result.get('action', 'Unknown')}")
                print(f"   💎 Token: {result.get('token_mint', 'Unknown')}")
                print(f"   📊 Amount Change: {result.get('amount_change', 0)}")
                print(f"   🎖️ Confidence: {result.get('confidence', 0)}/10")
                print(f"   📝 Reason: {result.get('reason', 'No reason')}")
                print()
            else:
                print(f"❌ NO RESULT FOR {wallet[:8]}...")
                print()
        
        # Also get raw transaction data
        print(f"🔍 RAW TRANSACTION ANALYSIS:")
        print("-" * 40)
        
        try:
            from solders.signature import Signature as SoldersSignature
            sig_obj = SoldersSignature.from_string(signature)
            
            tx_response = await rpc_client.get_transaction(
                sig_obj,
                encoding="json",
                commitment="confirmed",
                max_supported_transaction_version=0
            )
            
            if tx_response and tx_response.value:
                tx = tx_response.value
                meta = tx.transaction.meta if hasattr(tx.transaction, 'meta') else None
                
                print(f"✅ Transaction found:")
                print(f"   🔍 Slot: {tx.slot}")
                print(f"   💰 Fee: {meta.fee if meta else 'Unknown'} lamports")
                print(f"   ✅ Success: {meta.err is None if meta else 'Unknown'}")
                
                if meta:
                    print(f"   📊 Pre-balances: {len(meta.pre_balances) if meta.pre_balances else 0}")
                    print(f"   📊 Post-balances: {len(meta.post_balances) if meta.post_balances else 0}")
                    print(f"   🪙 Pre-token-balances: {len(meta.pre_token_balances) if meta.pre_token_balances else 0}")
                    print(f"   🪙 Post-token-balances: {len(meta.post_token_balances) if meta.post_token_balances else 0}")
                    print(f"   📝 Log messages: {len(meta.log_messages) if meta.log_messages else 0}")
                    
                    if meta.log_messages:
                        print(f"\n📝 LOG MESSAGES (first 10):")
                        for i, log in enumerate(meta.log_messages[:10]):
                            print(f"      [{i}] {log}")
                
            else:
                print(f"❌ Transaction not found or no data")
                
        except Exception as e:
            print(f"❌ Error getting raw transaction: {e}")
        
        await rpc_client.close()
        
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_transaction.py <signature>")
        sys.exit(1)
    
    signature = sys.argv[1]
    asyncio.run(analyze_transaction(signature))
