#!/usr/bin/env python3
"""
QUICK FIX: Analyze the sell transaction and update our detection logic
"""

import asyncio
import aiohttp
import json
from env_keys import EnvKeys

async def quick_fix_analysis():
    # The SELL transaction our system got wrong
    sell_sig = "2oAemxGqPk3pY3A1hGrV3q91EeBtAVLJ1ez8LM2KrMeGwTT2Xa3pa9ZgzU5U7aMcyoDMPegpKhr1eZhGpAgsxEwW"
    
    print("🚨 CRITICAL: Fixing our sell detection failure")
    print(f"Analyzing: {sell_sig[:12]}...")
    
    kz = EnvKeys()
    rpc_url = kz.HELIUS_RPC_URL
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [sell_sig, {"encoding": "json", "commitment": "confirmed", "maxSupportedTransactionVersion": 0}]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            data = await response.json()
            
            if 'error' in data:
                print(f"Error: {data['error']}")
                return
            
            result = data.get('result')
            if not result:
                print("No result found")
                return
            
            meta = result.get('meta', {})
            logs = meta.get('logMessages', [])
            
            print(f"Total logs: {len(logs)}")
            
            # Current flawed detection
            has_buy_exact_in = any('BuyExactIn' in log for log in logs)
            has_close_account = any('CloseAccount' in log for log in logs)
            
            print(f"❌ Our wrong result: BuyExactIn={has_buy_exact_in}, CloseAccount={has_close_account} → BUY")
            
            # Look for what actually indicates SELL
            print("\n🔍 SEARCHING FOR SELL PATTERNS:")
            
            # Check all logs for patterns
            sell_indicators = []
            for i, log in enumerate(logs):
                if any(keyword in log for keyword in ['sell', 'Sell', 'SELL', 'withdraw', 'Withdraw', 'exit']):
                    sell_indicators.append(f"[{i+1}] {log}")
            
            if sell_indicators:
                print("✅ SELL INDICATORS FOUND:")
                for indicator in sell_indicators:
                    print(f"   {indicator}")
            
            # Check transfer patterns
            token_transfers = sum(1 for log in logs if 'Transfer' in log and 'So11111111111111111111111111111111111111112' not in log)
            sol_transfers = sum(1 for log in logs if 'Transfer' in log and 'So11111111111111111111111111111111111111112' in log)
            
            print(f"\n💰 TRANSFER PATTERN:")
            print(f"   Token transfers: {token_transfers}")
            print(f"   SOL transfers: {sol_transfers}")
            
            if token_transfers > sol_transfers:
                print("   🔥 PATTERN: More token→SOL transfers (typical SELL)")
            
            # Show first 10 logs to identify pattern
            print(f"\n📝 FIRST 10 LOGS:")
            for i, log in enumerate(logs[:10], 1):
                print(f"   {i:2d}: {log}")
            
            print(f"\n🚨 CONCLUSION:")
            print(f"   This is clearly a SELL transaction")
            print(f"   We need to update our detection logic!")
            
            # Proposed new logic
            print(f"\n💡 PROPOSED FIX:")
            print(f"   Current logic is wrong - defaulting to BUY when neither instruction is found")
            print(f"   Better approach: Use transfer ratios or look for different instructions")
            
            if token_transfers > sol_transfers and token_transfers > 0:
                print(f"   ✅ Transfer ratio method would correctly identify this as SELL")
            else:
                print(f"   ❌ Need to find different discriminating pattern")

if __name__ == "__main__":
    asyncio.run(quick_fix_analysis())
