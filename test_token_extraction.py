#!/usr/bin/env python3
"""
Test token mint extraction from the recent transaction
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from env_keys import EnvKeys

async def test_improved_extraction():
    env = EnvKeys()
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    sig = '2HGUhYFo7PwmYQk5bKgZMGVTDgWxFzJ1ztYeyxgfKGvxsYW5oaQDeBWqQ5s284WHAaKkgKZGXin2mXCV2W46MpwX'
    sig_obj = Signature.from_string(sig)
    
    response = await client.get_transaction(
        sig_obj,
        encoding='jsonParsed',
        max_supported_transaction_version=0
    )
    
    if response.value:
        transaction = response.value
        wallet_address = 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK'
        
        # Extract transaction structure
        if hasattr(transaction, 'transaction'):
            tx_data = transaction.transaction
        else:
            tx_data = transaction
        
        if hasattr(tx_data, 'message'):
            tx_message = tx_data.message
        else:
            tx_message = tx_data.transaction.message
        
        print('=== IMPROVED TOKEN EXTRACTION ===')
        print(f'Transaction: {sig}')
        print()
        
        token_mint = None
        
        # Check account keys with improved logic
        if hasattr(tx_message, 'account_keys'):
            system_accounts = {
                '11111111111111111111111111111112',
                'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                'So11111111111111111111111111111111111111112',
                'ComputeBudget111111111111111111111111111111',
                'SysvarRent111111111111111111111111111111111',
                'SysvarRecentB1ockHashes11111111111111111111',
                'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',
                'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA',
                '5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump',
                'jitodontfrontd1111111TradeWithAxiomDotTrade',
                wallet_address
            }
            
            print(f'📋 Analyzing {len(tx_message.account_keys)} accounts...')
            candidate_mints = []
            
            for i, account in enumerate(tx_message.account_keys):
                # Handle different account formats
                if hasattr(account, 'pubkey'):
                    account_str = str(account.pubkey)
                    is_writable = hasattr(account, 'writable') and account.writable
                else:
                    account_str = str(account)
                    is_writable = False
                
                is_system = account_str in system_accounts
                
                status = "(system)" if is_system else "(candidate)"
                writable_status = "W" if is_writable else " "
                
                print(f'  {i+1:2d}. {account_str[:8]}...{account_str[-8:]} [{writable_status}] {status}')
                
                if not is_system and len(account_str) == 44:
                    candidate_mints.append((account_str, is_writable))
            
            print()
            print(f'📊 Found {len(candidate_mints)} candidate token mints:')
            
            # Priority 1: Writable candidates (most likely to be the traded token)
            writable_candidates = [mint for mint, writable in candidate_mints if writable]
            if writable_candidates:
                token_mint = writable_candidates[0]
                print(f'🎯 SELECTED (writable): {token_mint}')
            else:
                # Priority 2: First non-system candidate
                if candidate_mints:
                    token_mint = candidate_mints[0][0]
                    print(f'🎯 SELECTED (first candidate): {token_mint}')
        
        print()
        print('=== RESULT ===')
        if token_mint:
            print(f'✅ Token mint extracted: {token_mint}')
            print(f'🚀 Trade WOULD EXECUTE: BUY 0.001 SOL → {token_mint}')
            print(f'🔗 Check token: https://solscan.io/token/{token_mint}')
        else:
            print('❌ Still no token mint found')
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_improved_extraction())
