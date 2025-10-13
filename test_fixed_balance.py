#!/usr/bin/env python3
"""
Fixed balance checker that can decode raw token account data
"""

import asyncio
import struct
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts

def decode_token_account(data: bytes):
    """
    Decode raw token account data from Solana
    Token account structure:
    - mint: 32 bytes (pubkey)
    - owner: 32 bytes (pubkey)  
    - amount: 8 bytes (u64)
    - delegate: 36 bytes (optional pubkey)
    - state: 1 byte
    - is_native: 12 bytes (optional u64)
    - delegated_amount: 8 bytes (u64)
    - close_authority: 36 bytes (optional pubkey)
    """
    if len(data) < 165:  # Minimum token account size
        return None
        
    try:
        # First 32 bytes = mint pubkey
        mint_bytes = data[0:32]
        mint = Pubkey(mint_bytes)
        
        # Skip owner (32 bytes) to get to amount at offset 64
        amount_bytes = data[64:72]  # 8 bytes for u64
        amount = struct.unpack('<Q', amount_bytes)[0]  # little-endian u64
        
        # Get decimals - this requires additional RPC call normally
        # For now, assume 6 decimals for most SPL tokens (except SOL which is 9)
        decimals = 9 if str(mint) == "So11111111111111111111111111111111111111112" else 6
        
        ui_amount = amount / (10 ** decimals)
        
        return {
            'mint': str(mint),
            'amount': amount,
            'ui_amount': ui_amount,
            'decimals': decimals
        }
        
    except Exception as e:
        print(f"   ❌ Error decoding: {e}")
        return None

async def test_fixed_balance_check():
    """Test the fixed balance checking"""
    
    # Use your wallet and RPC
    from env_keys import EnvKeys
    env = EnvKeys()
    
    client = AsyncClient(env.HELIUS_RPC_URL, commitment=Processed)
    
    # Your wallet pubkey
    wallet_pubkey = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    
    try:
        print(f"🔍 Testing FIXED balance check for wallet: {wallet_pubkey}")
        
        # Test SOL balance
        sol_balance_response = await client.get_balance(wallet_pubkey, Processed)
        if sol_balance_response.value:
            sol_balance = sol_balance_response.value / 1e9
            print(f"💎 SOL Balance: {sol_balance:.6f} SOL")
        else:
            print(f"❌ Failed to get SOL balance")
        
        # Test token accounts with DECODING
        print(f"\n🪙 Testing token accounts with DECODING...")
        token_accounts_response = await client.get_token_accounts_by_owner(
            wallet_pubkey,
            TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
        )
        
        if token_accounts_response.value:
            print(f"✅ Found {len(token_accounts_response.value)} token accounts")
            print(f"🔧 Decoding token account data...")
            
            balances = {"SOL": sol_balance}
            valid_tokens = 0
            
            for i, account in enumerate(token_accounts_response.value):
                try:
                    if hasattr(account, 'account') and hasattr(account.account, 'data'):
                        data = account.account.data
                        
                        if isinstance(data, bytes) and len(data) >= 165:
                            decoded = decode_token_account(data)
                            
                            if decoded and decoded['ui_amount'] > 0:
                                mint = decoded['mint']
                                amount = decoded['ui_amount']
                                
                                balances[mint] = amount
                                valid_tokens += 1
                                
                                print(f"   ✅ Token {valid_tokens}: {mint[:8]}... = {amount:.6f}")
                                
                                # Special check for the token from your logs
                                if mint == "fvPSourDFevMVUGYpUwwvgXoKRMXPDGaST9VT2Ybonk":
                                    print(f"   🎯 FOUND TARGET TOKEN! Balance: {amount:.6f}")
                                
                except Exception as e:
                    print(f"   ❌ Error decoding account {i+1}: {e}")
                    
            print(f"\n📊 FINAL DECODED BALANCES:")
            print(f"   💎 SOL: {balances.get('SOL', 0):.6f}")
            print(f"   🪙 Valid tokens found: {valid_tokens}")
            
            # Show first few tokens
            token_count = 0
            for token, amount in balances.items():
                if token != 'SOL' and token_count < 5:
                    print(f"   🪙 {token[:8]}...: {amount:.6f}")
                    token_count += 1
                    
            if valid_tokens > 5:
                print(f"   ... and {valid_tokens - 5} more tokens")
                
            # Check specifically for the target token
            target_token = "fvPSourDFevMVUGYpUwwvgXoKRMXPDGaST9VT2Ybonk"
            if target_token in balances:
                print(f"\n🎯 TARGET TOKEN STATUS:")
                print(f"   Token: {target_token}")
                print(f"   Balance: {balances[target_token]:.6f}")
                print(f"   ✅ CAN SELL THIS TOKEN!")
            else:
                print(f"\n❌ TARGET TOKEN NOT FOUND:")
                print(f"   Token: {target_token}")
                print(f"   🚨 This is why sell operations are failing!")
                
        else:
            print(f"❌ No token accounts found")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    print("🔧 FIXED BALANCE CHECK TEST")
    print("=" * 50)
    asyncio.run(test_fixed_balance_check())
