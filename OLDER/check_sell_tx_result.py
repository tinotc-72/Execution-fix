#!/usr/bin/env python3
"""
Check the result of our sell transaction
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from env_keys import EnvKeys

async def check_transaction_result():
    """Check the result of our sell transaction"""
    
    from solders.signature import Signature
    tx_signature = Signature.from_string("3ZVzhSkF6whCKQuwvBFZmnnXwhL6S8NjYQtg1QRXLdJVBTSWrVdGTY6S79BMDnhoBrLWmEa5L8fG4fk3goMZ7e76")
    
    print(f"🔍 CHECKING TRANSACTION: {tx_signature}")
    print("="*80)
    
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
    
    try:
        # Wait a bit longer
        await asyncio.sleep(5)
        
        # Get transaction status with full detail
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
                    print("🎉 TRANSACTION SUCCEEDED!")
                    
                    # Check compute units used
                    compute_units = getattr(meta, 'compute_units_consumed', 0)
                    print(f"Compute units consumed: {compute_units:,}")
                    
                    if compute_units > 0:
                        print("🎉 PUMP.FUN PROGRAM WAS INVOKED!")
                    
                    # Check logs
                    if hasattr(meta, 'log_messages') and meta.log_messages:
                        print("\nTransaction logs:")
                        for log in meta.log_messages:
                            print(f"  {log}")
                    
                    # Check balance changes
                    if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                        print("\nSOL balance changes:")
                        for i, (pre, post) in enumerate(zip(meta.pre_balances, meta.post_balances)):
                            if pre != post:
                                change = post - pre
                                print(f"  Account {i}: {pre:,} -> {post:,} ({change:+,} lamports)")
                                if change > 0 and i == 6:  # Our wallet should be account 6
                                    print(f"    💰 WE RECEIVED {change/1_000_000_000:.6f} SOL!")
                    
                    # Check token balance changes
                    if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                        print("\nToken balance changes:")
                        
                        print("Pre-token balances:")
                        for balance in meta.pre_token_balances:
                            print(f"  Account: {balance.account_index}, Owner: {balance.owner}, Amount: {balance.ui_token_amount.ui_amount}")
                        
                        print("Post-token balances:")
                        for balance in meta.post_token_balances:
                            print(f"  Account: {balance.account_index}, Owner: {balance.owner}, Amount: {balance.ui_token_amount.ui_amount}")
            else:
                print("No transaction metadata available")
        else:
            print("❌ Transaction not found or not confirmed yet")
            
        # Also check with signature status
        sig_status = await client.get_signature_statuses([tx_signature])
        if sig_status.value and sig_status.value[0]:
            status = sig_status.value[0]
            print(f"\nSignature status:")
            print(f"  Confirmation status: {status.confirmation_status}")
            print(f"  Slot: {status.slot}")
            if status.err:
                print(f"  Error: {status.err}")
            else:
                print(f"  Success: ✅")
                
    except Exception as e:
        print(f"❌ Error checking transaction: {e}")
        
    finally:
        await client.close()

async def main():
    """Main function"""
    await check_transaction_result()

if __name__ == "__main__":
    asyncio.run(main())
