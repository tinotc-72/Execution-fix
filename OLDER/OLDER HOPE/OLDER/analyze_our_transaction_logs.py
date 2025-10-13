#!/usr/bin/env python3
"""
Analyze the program logs from our sell transactions to understand why they don't execute
"""

import asyncio
import aiohttp
import json
from env_keys import EnvKeys

async def analyze_transaction_logs(signature: str):
    """Get detailed transaction logs to understand execution"""
    
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0,
                "commitment": "confirmed"
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(helius_url, json=payload) as response:
            data = await response.json()
            
            if 'result' in data and data['result']:
                tx_data = data['result']
                
                print(f"🔍 TRANSACTION ANALYSIS: {signature}")
                print("="*80)
                
                # Check transaction success/failure
                meta = tx_data.get('meta', {})
                error = meta.get('err')
                
                if error:
                    print(f"❌ Transaction failed with error: {error}")
                else:
                    print(f"✅ Transaction succeeded")
                
                print(f"💰 Fee: {meta.get('fee', 0)} lamports")
                print(f"🖥️  Compute units consumed: {meta.get('computeUnitsConsumed', 0)}")
                
                # Analyze program logs
                logs = meta.get('logMessages', [])
                print(f"\n📋 PROGRAM LOGS ({len(logs)} entries):")
                
                pump_program_invoked = False
                sell_instruction_found = False
                transfer_found = False
                
                for i, log in enumerate(logs):
                    print(f"  {i:2}: {log}")
                    
                    if "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke" in log:
                        pump_program_invoked = True
                    elif "Instruction: Sell" in log:
                        sell_instruction_found = True
                    elif "Instruction: Transfer" in log:
                        transfer_found = True
                
                print(f"\n🔎 ANALYSIS:")
                print(f"   Pump program invoked: {'✅' if pump_program_invoked else '❌'}")
                print(f"   Sell instruction recognized: {'✅' if sell_instruction_found else '❌'}")
                print(f"   Token transfer executed: {'✅' if transfer_found else '❌'}")
                
                # Check balance changes
                pre_balances = meta.get('preBalances', [])
                post_balances = meta.get('postBalances', [])
                
                if len(pre_balances) == len(post_balances):
                    print(f"\n💰 SOL BALANCE CHANGES:")
                    for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                        change = post - pre
                        if change != 0:
                            print(f"   Account {i}: {change:+,} lamports")
                        
                # Check token balance changes
                pre_token_balances = meta.get('preTokenBalances', [])
                post_token_balances = meta.get('postTokenBalances', [])
                
                print(f"\n🪙 TOKEN BALANCE CHANGES:")
                if not pre_token_balances and not post_token_balances:
                    print("   No token balance changes recorded")
                else:
                    print(f"   Pre-balances: {len(pre_token_balances)}")
                    print(f"   Post-balances: {len(post_token_balances)}")
                    
                    for balance in pre_token_balances:
                        print(f"   PRE: Account {balance.get('accountIndex')}: {balance.get('uiTokenAmount', {}).get('amount', 0)} tokens")
                    
                    for balance in post_token_balances:
                        print(f"   POST: Account {balance.get('accountIndex')}: {balance.get('uiTokenAmount', {}).get('amount', 0)} tokens")
                
                # Check inner instructions
                inner_instructions = meta.get('innerInstructions', [])
                print(f"\n⚙️  INNER INSTRUCTIONS: {len(inner_instructions)}")
                for inner in inner_instructions:
                    print(f"   Index {inner.get('index')}: {len(inner.get('instructions', []))} instructions")
                
                return True
            else:
                print(f"❌ Could not fetch transaction data for {signature}")
                return False

async def main():
    """Analyze recent failed sell transactions"""
    
    # Our recent sell transaction signatures
    signatures = [
        "2Tp8K4PrDaPofm6GButvuFKLEVCuq6cQPSYXbus8aT9maisTSA84AJL6iCUJJeQjZvqtDPYk1sfjcow1ef2WL8tT",  # Latest attempt
        "3pS9svE42TdwUAV2UWHgNc7qZGYJs63TGS52j99mhKd47rZrwcXcjrUFXXZBsoeamDwaL8BXCJoyWuxmYH67TsNm",  # Second attempt
        "5sxzaTpBxBwVxG2Hymj5LCnyDnQSh95XqaWxoLHcyJAtZVSAnihm7QZjgm49N5b3q4mfaPt3utqLeJmYPTyo6QCX",  # Earlier attempt
    ]
    
    for signature in signatures:
        await analyze_transaction_logs(signature)
        print("\n" + "="*80 + "\n")
        await asyncio.sleep(1)  # Rate limiting

if __name__ == "__main__":
    asyncio.run(main())
