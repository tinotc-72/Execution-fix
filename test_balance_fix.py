#!/usr/bin/env python3
"""
Quick test to check if balance checking is working properly
"""

import asyncio
import sys
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts

async def test_balance_check():
    """Test token balance checking"""
    
    # Use your wallet and RPC
    from env_keys import EnvKeys
    env = EnvKeys()
    
    client = AsyncClient(env.HELIUS_RPC_URL, commitment=Processed)
    
    # Your wallet pubkey
    wallet_pubkey = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    
    try:
        print(f"🔍 Testing balance check for wallet: {wallet_pubkey}")
        
        # Test SOL balance
        sol_balance_response = await client.get_balance(wallet_pubkey, Processed)
        if sol_balance_response.value:
            sol_balance = sol_balance_response.value / 1e9
            print(f"💎 SOL Balance: {sol_balance:.6f} SOL")
        else:
            print(f"❌ Failed to get SOL balance")
        
        # Test token accounts
        print(f"\n🪙 Testing token accounts...")
        token_accounts_response = await client.get_token_accounts_by_owner(
            wallet_pubkey,
            TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
        )
        
        if token_accounts_response.value:
            print(f"✅ Found {len(token_accounts_response.value)} token accounts")
            
            balances = {}
            for i, account in enumerate(token_accounts_response.value):
                try:
                    print(f"\n🔍 Account {i+1}:")
                    print(f"   Type: {type(account)}")
                    print(f"   Has account attr: {hasattr(account, 'account')}")
                    
                    if hasattr(account, 'account'):
                        account_info = account.account
                        print(f"   Account type: {type(account_info)}")
                        print(f"   Has data attr: {hasattr(account_info, 'data')}")
                        
                        if hasattr(account_info, 'data'):
                            data = account_info.data
                            print(f"   Data type: {type(data)}")
                            print(f"   Data: {data}")
                            
                            # Try different parsing methods
                            if isinstance(data, dict):
                                print("   📊 Dict format detected")
                                parsed = data.get('parsed', {})
                                if 'info' in parsed:
                                    info = parsed['info']
                                    mint = info.get('mint')
                                    token_amount = info.get('tokenAmount', {})
                                    ui_amount = token_amount.get('uiAmount', 0)
                                    
                                    if mint and ui_amount and ui_amount > 0:
                                        balances[mint] = float(ui_amount)
                                        print(f"   ✅ Token: {mint}")
                                        print(f"   💰 Balance: {ui_amount}")
                            
                            elif hasattr(data, 'parsed'):
                                print("   📊 Parsed attr detected")
                                parsed = data.parsed
                                if 'info' in parsed:
                                    info = parsed['info']
                                    mint = info.get('mint')
                                    token_amount = info.get('tokenAmount', {})
                                    ui_amount = token_amount.get('uiAmount', 0)
                                    
                                    if mint and ui_amount and ui_amount > 0:
                                        balances[mint] = float(ui_amount)
                                        print(f"   ✅ Token: {mint}")
                                        print(f"   💰 Balance: {ui_amount}")
                            
                except Exception as e:
                    print(f"   ❌ Error parsing account {i+1}: {e}")
                    
            print(f"\n📊 FINAL BALANCES:")
            for token, amount in balances.items():
                print(f"   🪙 {token}: {amount}")
                
        else:
            print(f"❌ No token accounts found")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    print("🧪 BALANCE CHECK TEST")
    print("=" * 50)
    asyncio.run(test_balance_check())
