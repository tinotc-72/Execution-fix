#!/usr/bin/env python3
"""
Investigate why our transactions aren't invoking the pump.fun program
Compare our accounts with successful transaction accounts
"""

import asyncio
import aiohttp
from solders.pubkey import Pubkey
from env_keys import EnvKeys

async def check_account_validity():
    """Check if the accounts we're using actually exist and are valid"""
    
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    # Accounts from successful transaction that we're copying
    accounts_to_check = {
        "Token mint": "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump",
        "Bonding curve": "EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV", 
        "Associated bonding curve": "AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ",
        "Associated user": "9DGQqtdBJHU4fN66cRE1JLVVVJq3KK4mYZxLoSZHqWKf",
        "Bonding curve token account": "DkYPayDaykVxT4RbpNoCct6ztG6kbcgZftjnS6cUb6U",
        "Pump program": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    }
    
    print("🔍 CHECKING ACCOUNT VALIDITY")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        for name, address in accounts_to_check.items():
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    address,
                    {"encoding": "base64"}
                ]
            }
            
            try:
                async with session.post(helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data:
                        result = data['result']
                        if result and result.get('value'):
                            account_info = result['value']
                            owner = account_info.get('owner')
                            lamports = account_info.get('lamports', 0)
                            print(f"✅ {name}: EXISTS")
                            print(f"   Address: {address}")
                            print(f"   Owner: {owner}")
                            print(f"   Lamports: {lamports:,}")
                            print()
                        else:
                            print(f"❌ {name}: DOES NOT EXIST")
                            print(f"   Address: {address}")
                            print()
                    else:
                        print(f"❓ {name}: ERROR CHECKING")
                        print(f"   Response: {data}")
                        print()
                        
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
                print()
                
            await asyncio.sleep(0.1)  # Rate limiting

async def check_our_account_setup():
    """Check our specific account setup"""
    
    print("🔍 CHECKING OUR ACCOUNT SETUP")
    print("="*80)
    
    our_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    our_token_account = "21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG"
    
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    accounts_to_check = {
        "Our wallet": our_wallet,
        "Our token account": our_token_account,
    }
    
    async with aiohttp.ClientSession() as session:
        for name, address in accounts_to_check.items():
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    address,
                    {"encoding": "base64"}
                ]
            }
            
            try:
                async with session.post(helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data:
                        result = data['result']
                        if result and result.get('value'):
                            account_info = result['value']
                            owner = account_info.get('owner')
                            lamports = account_info.get('lamports', 0)
                            print(f"✅ {name}: EXISTS")
                            print(f"   Address: {address}")
                            print(f"   Owner: {owner}")
                            print(f"   Lamports: {lamports:,}")
                            
                            # Check token account balance specifically
                            if "token account" in name.lower():
                                # Get token account balance
                                token_payload = {
                                    "jsonrpc": "2.0",
                                    "id": 1,
                                    "method": "getTokenAccountBalance",
                                    "params": [address]
                                }
                                
                                async with session.post(helius_url, json=token_payload) as token_response:
                                    token_data = await token_response.json()
                                    if 'result' in token_data:
                                        balance_info = token_data['result']['value']
                                        amount = balance_info.get('amount', '0')
                                        print(f"   Token balance: {amount}")
                            
                            print()
                        else:
                            print(f"❌ {name}: DOES NOT EXIST")
                            print(f"   Address: {address}")
                            print()
                            
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
                print()

async def compare_instruction_structure():
    """Compare our instruction structure with successful transaction"""
    
    print("🔍 INSTRUCTION STRUCTURE COMPARISON")
    print("="*80)
    
    # Our latest instruction data
    our_instruction = "33e685a4017f83ad002d3101000000000000000000000000"
    
    # Successful transaction instruction data
    successful_instruction = "33e685a4017f83adea9478896d120000b0ef430800000000"
    
    print(f"Our instruction:        {our_instruction}")
    print(f"Successful instruction: {successful_instruction}")
    print()
    
    # Parse both
    print("PARSED DATA:")
    print("=" * 40)
    
    for name, instruction_hex in [("Our", our_instruction), ("Successful", successful_instruction)]:
        discriminator = instruction_hex[:16]
        token_amount_hex = instruction_hex[16:32]
        min_sol_out_hex = instruction_hex[32:48]
        
        token_amount = int.from_bytes(bytes.fromhex(token_amount_hex), 'little')
        min_sol_out = int.from_bytes(bytes.fromhex(min_sol_out_hex), 'little')
        
        print(f"{name}:")
        print(f"  Discriminator: {discriminator}")
        print(f"  Token amount: {token_amount:,}")
        print(f"  Min SOL out: {min_sol_out:,}")
        print()

async def main():
    """Main analysis function"""
    await check_account_validity()
    await check_our_account_setup() 
    await compare_instruction_structure()
    
    print("🤔 HYPOTHESIS:")
    print("Our transactions succeed but don't invoke the pump program.")
    print("This suggests one of:")
    print("1. Account validation failure (account doesn't exist or wrong owner)")
    print("2. Instruction data format issue")
    print("3. Program execution prerequisites not met")
    print("4. Account order/permissions issue")

if __name__ == "__main__":
    asyncio.run(main())
