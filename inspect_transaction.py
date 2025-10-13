#!/usr/bin/env python3
"""
Simple transaction inspector
"""

import asyncio
import json
from env_keys import EnvKeys
import aiohttp

async def inspect_transaction():
    """Inspect the specific transaction"""
    signature = "58wAhXT6ehHtMgeeneVzH5aDy57Zuy4viCXGnRHGsk2fNjnAHsHGNBqvwiReTWFEgktrhYT92PsqTGwFwi27UUyN"
    
    env_keys = EnvKeys()
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "json",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(env_keys.HELIUS_RPC_URL, json=payload) as response:
            data = await response.json()
            
            print("🔍 TRANSACTION ANALYSIS:")
            print("=" * 60)
            
            if 'error' in data:
                print(f"❌ RPC Error: {data['error']}")
                return
            
            result = data.get('result')
            if not result:
                print("❌ No transaction data")
                return
            
            print(f"✅ Transaction found!")
            print(f"📝 Signature: {signature}")
            print()
            
            # Check if transaction was successful
            meta = result.get('meta', {})
            if meta.get('err'):
                print(f"❌ TRANSACTION FAILED: {meta['err']}")
            else:
                print(f"✅ Transaction succeeded")
            
            print(f"💰 Fee: {meta.get('fee', 0)} lamports")
            print()
            
            # Check account keys
            transaction = result.get('transaction', {})
            message = transaction.get('message', {})
            account_keys = message.get('accountKeys', [])
            
            print(f"👥 ACCOUNT KEYS ({len(account_keys)}):")
            for i, key in enumerate(account_keys):
                print(f"   [{i}] {key}")
            print()
            
            # Check for target wallets
            target_wallets = [
                "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
                "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
            ]
            
            print(f"🎯 TARGET WALLET INVOLVEMENT:")
            for wallet in target_wallets:
                if wallet in account_keys:
                    index = account_keys.index(wallet)
                    print(f"   ✅ {wallet[:8]}... found at index {index}")
                else:
                    print(f"   ❌ {wallet[:8]}... NOT INVOLVED")
            print()
            
            # Check instructions
            instructions = message.get('instructions', [])
            print(f"📋 INSTRUCTIONS ({len(instructions)}):")
            for i, instruction in enumerate(instructions):
                program_id_index = instruction.get('programIdIndex', 0)
                program_id = account_keys[program_id_index] if program_id_index < len(account_keys) else "Unknown"
                
                # Identify program type
                program_name = "Unknown"
                if program_id == "ComputeBudget111111111111111111111111111111":
                    program_name = "Compute Budget"
                elif program_id == "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL":
                    program_name = "Associated Token Account"
                elif program_id == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    program_name = "Token Program"
                elif program_id == "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW":
                    program_name = "Pump.fun"
                elif program_id == "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB":
                    program_name = "Jupiter"
                
                accounts = instruction.get('accounts', [])
                print(f"   [{i}] {program_name} ({program_id[:8]}...)")
                print(f"       Accounts: {accounts}")
            print()
            
            # Check logs
            logs = meta.get('logMessages', [])
            print(f"📝 LOG MESSAGES ({len(logs)}):")
            for i, log in enumerate(logs):
                print(f"   [{i}] {log}")
            print()
            
            # Check balance changes
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            print(f"💰 SOL BALANCE CHANGES:")
            for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                change = (post - pre) / 1e9  # Convert to SOL
                if abs(change) > 0.000001:  # Only show meaningful changes
                    account = account_keys[i] if i < len(account_keys) else f"Account[{i}]"
                    print(f"   [{i}] {account[:8]}...: {change:+.9f} SOL")
            print()
            
            # Check token balance changes
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            print(f"🪙 TOKEN BALANCE CHANGES:")
            print(f"   Pre-token balances: {len(pre_token_balances)}")
            print(f"   Post-token balances: {len(post_token_balances)}")
            
            if pre_token_balances or post_token_balances:
                all_token_balances = {}
                
                # Process pre-balances
                for balance in pre_token_balances:
                    account_index = balance.get('accountIndex', -1)
                    mint = balance.get('mint', 'Unknown')
                    owner = balance.get('owner', 'Unknown')
                    amount = balance.get('uiTokenAmount', {}).get('uiAmount', 0)
                    
                    key = (account_index, mint, owner)
                    all_token_balances[key] = {'pre': amount, 'post': 0}
                
                # Process post-balances
                for balance in post_token_balances:
                    account_index = balance.get('accountIndex', -1)
                    mint = balance.get('mint', 'Unknown')
                    owner = balance.get('owner', 'Unknown')
                    amount = balance.get('uiTokenAmount', {}).get('uiAmount', 0)
                    
                    key = (account_index, mint, owner)
                    if key in all_token_balances:
                        all_token_balances[key]['post'] = amount
                    else:
                        all_token_balances[key] = {'pre': 0, 'post': amount}
                
                for (account_index, mint, owner), balances in all_token_balances.items():
                    change = balances['post'] - balances['pre']
                    if abs(change) > 0.000001:  # Only show meaningful changes
                        print(f"   Account[{account_index}] {owner[:8]}...: {change:+.6f} {mint[:8]}...")

if __name__ == "__main__":
    asyncio.run(inspect_transaction())
