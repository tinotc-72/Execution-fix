#!/usr/bin/env python3
"""
EMERGENCY ANALYSIS: Fix the sell detection failure
Transaction 2oAemxGqPk3pY3A1hGrV3q91EeBtAVLJ1ez8LM2KrMeGwTT2Xa3pa9ZgzU5U7aMcyoDMPegpKhr1eZhGpAgsxEwW
is actually a SELL but our system classified it as BUY
"""

import asyncio
import aiohttp
import json
from env_keys import EnvKeys

async def emergency_analysis():
    print("🚨 EMERGENCY SELL DETECTION FAILURE ANALYSIS")
    print("=" * 60)
    
    # The confirmed SELL transaction that our system got wrong
    sell_signature = "2oAemxGqPk3pY3A1hGrV3q91EeBtAVLJ1ez8LM2KrMeGwTT2Xa3pa9ZgzU5U7aMcyoDMPegpKhr1eZhGpAgsxEwW"
    
    print(f"📊 Analyzing CONFIRMED SELL: {sell_signature[:12]}...")
    print("🔍 Our system incorrectly classified this as BUY")
    print("🎯 Goal: Find what we missed to fix our detection")
    print("=" * 60)
    
    kz = EnvKeys()
    rpc_url = kz.HELIUS_RPC_URL
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            sell_signature,
            {
                "encoding": "json",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(rpc_url, json=payload) as response:
                data = await response.json()
                
                if 'error' in data:
                    print(f"❌ RPC Error: {data['error']}")
                    return
                
                result = data.get('result')
                if not result:
                    print("❌ No transaction data found")
                    return
                
                meta = result.get('meta', {})
                logs = meta.get('logMessages', [])
                
                if not logs:
                    print("❌ No logs found")
                    return
                
                print(f"✅ Transaction loaded: {len(logs)} logs")
                print(f"✅ Status: {'SUCCESS' if meta.get('err') is None else 'FAILED'}")
                print()
                
                # Our FAILED detection logic
                has_buy_exact_in = any('BuyExactIn' in log for log in logs)
                has_close_account = any('CloseAccount' in log for log in logs)
                
                print("🤖 OUR CURRENT (FAILED) DETECTION:")
                print(f"   BuyExactIn found: {has_buy_exact_in}")
                print(f"   CloseAccount found: {has_close_account}")
                print(f"   Our wrong classification: BUY")
                print()
                
                # Let's find what indicates this is actually a SELL
                print("🔍 SEARCHING FOR SELL PATTERNS:")
                
                # Look for any sell-related keywords
                sell_patterns = []
                for i, log in enumerate(logs):
                    log_lower = log.lower()
                    if any(keyword in log_lower for keyword in [
                        'sell', 'close', 'withdraw', 'exit', 'liquidate',
                        'sellexactin', 'sellexactout', 'closeposition'
                    ]):
                        sell_patterns.append(f"[{i+1}] {log}")
                
                if sell_patterns:
                    print("   🔥 POTENTIAL SELL INDICATORS FOUND:")
                    for pattern in sell_patterns:
                        print(f"      {pattern}")
                else:
                    print("   ❌ No obvious sell keywords found")
                
                print()
                
                # Analyze transfer patterns
                print("💰 TRANSFER ANALYSIS:")
                token_transfers = 0
                sol_transfers = 0
                
                for log in logs:
                    if 'Transfer' in log:
                        if 'So11111111111111111111111111111111111111112' in log:
                            sol_transfers += 1
                        else:
                            token_transfers += 1
                
                print(f"   Token transfers: {token_transfers}")
                print(f"   SOL transfers: {sol_transfers}")
                
                # Show transfer pattern (sells typically have more token→SOL)
                if token_transfers > sol_transfers:
                    print("   🔥 PATTERN: More token transfers than SOL (typical of SELL)")
                elif sol_transfers > token_transfers:
                    print("   📈 PATTERN: More SOL transfers than token (typical of BUY)")
                else:
                    print("   ⚖️ PATTERN: Equal transfers")
                
                print()
                
                # Show ALL logs to find the discriminating pattern
                print("📝 ALL TRANSACTION LOGS:")
                print("   (Looking for the pattern that indicates SELL)")
                for i, log in enumerate(logs, 1):
                    # Highlight logs with potential importance
                    if any(keyword in log for keyword in [
                        'Instruction:', 'Transfer', 'Close', 'Program log'
                    ]):
                        print(f"   🔥 {i:2d}: {log}")
                    else:
                        print(f"      {i:2d}: {log}")
                
                print()
                print("🚨 CRITICAL QUESTIONS:")
                print("1. What specific pattern in these logs indicates SELL?")
                print("2. How should we modify our detection rules?")
                print("3. Is there a different instruction we should look for?")
                print("4. Should we use transfer ratios instead of instructions?")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(emergency_analysis())
