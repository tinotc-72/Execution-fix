#!/usr/bin/env python3
"""
Check the buy transaction result
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from env_keys import EnvKeys

async def check_buy_transaction():
    """Check the result of our buy transaction"""
    
    tx_signature = Signature.from_string("397uuWymp3AMRPUau6myZizsaaKjAyBujZhYsdYRFDKRR1E27GXecDkGc6C5vvFprmnd2deN68uuxAcSJK7UfJrf")
    
    print(f"🔍 CHECKING BUY TRANSACTION: {tx_signature}")
    print("="*80)
    
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
    
    try:
        await asyncio.sleep(3)  # Wait for confirmation
        
        # Get transaction status
        tx_result = await client.get_transaction(
            tx_signature, 
            encoding="jsonParsed",
            max_supported_transaction_version=0
        )
        
        if tx_result.value:
            print("✅ Transaction found!")
            
            meta = tx_result.value.transaction.meta
            if meta:
                if meta.err:
                    print(f"❌ Transaction failed: {meta.err}")
                    
                    # Show logs for debugging
                    if hasattr(meta, 'log_messages') and meta.log_messages:
                        print("\nError logs:")
                        for log in meta.log_messages:
                            print(f"  {log}")
                else:
                    print("✅ TRANSACTION SUCCEEDED!")
                    
                    # Check compute units used
                    compute_units = getattr(meta, 'compute_units_consumed', 0)
                    print(f"Compute units consumed: {compute_units:,}")
                    
                    # Check logs
                    if hasattr(meta, 'log_messages') and meta.log_messages:
                        print("\nTransaction logs:")
                        for log in meta.log_messages:
                            print(f"  {log}")
                    
                    # Check token balance changes
                    if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                        print("\nToken balance changes:")
                        
                        print("Pre-token balances:")
                        for balance in meta.pre_token_balances or []:
                            print(f"  Account: {balance.account_index}, Owner: {balance.owner}, Amount: {balance.ui_token_amount.ui_amount}")
                        
                        print("Post-token balances:")
                        for balance in meta.post_token_balances or []:
                            print(f"  Account: {balance.account_index}, Owner: {balance.owner}, Amount: {balance.ui_token_amount.ui_amount}")
                            
                        # Calculate changes
                        pre_balances = {b.account_index: b.ui_token_amount.ui_amount for b in (meta.pre_token_balances or [])}
                        post_balances = {b.account_index: b.ui_token_amount.ui_amount for b in (meta.post_token_balances or [])}
                        
                        for account_idx in post_balances:
                            pre = pre_balances.get(account_idx, 0) or 0
                            post = post_balances[account_idx] or 0
                            change = post - pre
                            if change != 0:
                                print(f"  Account {account_idx}: {pre} → {post} ({change:+})")
                                
                    else:
                        print("No token balance information available")
                        
        else:
            print("❌ Transaction not found")
            
    except Exception as e:
        print(f"❌ Error checking transaction: {e}")
        
    finally:
        await client.close()

async def main():
    """Main function"""
    await check_buy_transaction()

if __name__ == "__main__":
    asyncio.run(main())
