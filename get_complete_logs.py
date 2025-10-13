#!/usr/bin/env python3

"""
Get complete log messages for the transaction
"""

import asyncio
import json

async def get_complete_logs():
    """Get all log messages from the transaction"""
    
    signature = "5Dz5vtE5wmtQi738itycjf7cRmFFWXWMUKQUXXFyuBpbQkTfmtbosSCmX84LtPc5DhTfCoEkb8NUUr9vN68HmTc"
    
    try:
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.commitment import Finalized
        from solders.signature import Signature
        
        rpc_client = AsyncClient("https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
        sig_obj = Signature.from_string(signature)
        
        response = await rpc_client.get_transaction(
            sig_obj, 
            commitment=Finalized,
            max_supported_transaction_version=0
        )
        
        if response.value:
            tx_data = response.value.to_json()
            transaction = json.loads(tx_data)
            
            meta = transaction.get('meta', {})
            log_messages = meta.get('logMessages', [])
            
            print(f"📝 ALL LOG MESSAGES ({len(log_messages)} total):")
            print("=" * 80)
            
            for i, log in enumerate(log_messages):
                print(f"{i+1:2d}: {log}")
            
            # Also show post token balances
            post_balances = meta.get('postTokenBalances', [])
            if post_balances:
                print(f"\\n🪙 POST TOKEN BALANCES:")
                print("=" * 80)
                for i, balance in enumerate(post_balances):
                    owner = balance.get('owner', 'N/A')
                    mint = balance.get('mint', 'N/A') 
                    amount_info = balance.get('uiTokenAmount', {})
                    amount = amount_info.get('uiAmountString', '0')
                    decimals = amount_info.get('decimals', 0)
                    
                    print(f"Balance {i+1}:")
                    print(f"  Owner: {owner}")
                    print(f"  Mint: {mint}")
                    print(f"  Amount: {amount} (decimals: {decimals})")
                    print()
                    
        await rpc_client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_complete_logs())