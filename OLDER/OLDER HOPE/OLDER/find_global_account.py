#!/usr/bin/env python3
"""
Find the correct global account for pump.fun
"""

import asyncio
import aiohttp
from env_keys import EnvKeys

async def find_global_account():
    """Find the correct global account that should be owned by pump.fun program"""
    
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    # Let's check recent pump.fun transactions to see what the first account is
    print("🔍 SEARCHING FOR CORRECT GLOBAL ACCOUNT")
    print("="*80)
    
    # Search for recent pump.fun transactions
    search_params = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "searchTransactions",
        "params": {
            "query": {
                "and": [
                    {"programAccounts": ["6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"]},
                    {"blockTime": {"gt": 1734000000}}  # Recent transactions
                ]
            },
            "limit": 10,
            "searchTransactionHistory": True,
            "encoding": "jsonParsed"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(helius_url, json=search_params) as response:
                data = await response.json()
                
                if 'result' in data and data['result']:
                    for i, tx in enumerate(data['result'][:3]):  # Check first 3
                        print(f"\n--- Transaction {i+1}: {tx['signature']} ---")
                        
                        instructions = tx['transaction']['message']['instructions']
                        for j, instruction in enumerate(instructions):
                            if instruction['programId'] == '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P':
                                accounts = instruction['accounts']
                                print(f"Instruction {j} accounts:")
                                for k, account in enumerate(accounts[:3]):  # First 3 accounts
                                    print(f"  {k}: {account}")
                                    
                                    # Check what this account is owned by
                                    account_check = {
                                        "jsonrpc": "2.0",
                                        "id": 1,
                                        "method": "getAccountInfo",
                                        "params": [account, {"encoding": "base64"}]
                                    }
                                    
                                    async with session.post(helius_url, json=account_check) as account_response:
                                        account_data = await account_response.json()
                                        if 'result' in account_data and account_data['result']['value']:
                                            owner = account_data['result']['value']['owner']
                                            lamports = account_data['result']['value']['lamports']
                                            print(f"     Owner: {owner}")
                                            print(f"     Lamports: {lamports:,}")
                                        else:
                                            print(f"     NOT FOUND")
                                    
                                    await asyncio.sleep(0.1)
                                break
                        
                else:
                    print("No recent transactions found")
                    
        except Exception as e:
            print(f"Error searching: {e}")

async def check_known_global_accounts():
    """Check some potential global accounts"""
    
    print("\n🔍 CHECKING POTENTIAL GLOBAL ACCOUNTS")
    print("="*80)
    
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    # Some potential global accounts from pump.fun
    potential_globals = [
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # Common in many transactions
        "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM",  # Fee recipient we were using
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1",  # Event authority
        "8WHNZ5pwqy6ZgS8jJUjtT3MKoSNWoAp4LCpm8hNHaWfN",  # Program data
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, account in enumerate(potential_globals):
            print(f"\nChecking account {i+1}: {account}")
            
            account_check = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [account, {"encoding": "base64"}]
            }
            
            try:
                async with session.post(helius_url, json=account_check) as response:
                    data = await response.json()
                    
                    if 'result' in data and data['result']['value']:
                        owner = data['result']['value']['owner']
                        lamports = data['result']['value']['lamports']
                        print(f"  ✅ EXISTS")
                        print(f"  Owner: {owner}")
                        print(f"  Lamports: {lamports:,}")
                        
                        if owner == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                            print(f"  🎉 OWNED BY PUMP.FUN PROGRAM!")
                    else:
                        print(f"  ❌ NOT FOUND")
                        
            except Exception as e:
                print(f"  Error: {e}")
                
            await asyncio.sleep(0.1)

async def main():
    """Main function"""
    await find_global_account()
    await check_known_global_accounts()

if __name__ == "__main__":
    asyncio.run(main())
