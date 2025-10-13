#!/usr/bin/env python3
"""
Debug Action Flow - Track exactly what happens to action determination
"""

import asyncio
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_action_flow():
    """Analyze the exact action flow that's causing the issue"""
    
    print("🔍 DEBUGGING ACTION FLOW")
    print("="*50)
    
    # This is what your logs show for the detected transaction
    trade_info = {
        'signature': 'KoAtRDrfEMjUuxr5BRRdL5HCMrmYTLY35W1kuh5nrzLmb8ZhcYD21FHwyMTZf5qd7VRe94qBcYaa5RpmUNtFHGT',
        'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
        'logs': ['Program log: Instruction: Sell'],  # Clearly shows SELL
        'basic_analysis': {
            'likely_action': 'sell',  # Correctly detected as SELL
            'confidence': 'high',
            'reasoning': 'Found sell indicator: instruction: sell',
            'detected_dex': 'unknown',
            'copy_immediately': True
        }
    }
    
    print("📊 ORIGINAL TRADE INFO:")
    print(f"   Signature: {trade_info['signature'][:8]}...")
    print(f"   Wallet: {trade_info['wallet_address'][:8]}...")
    print(f"   Logs: {trade_info['logs']}")
    print(f"   Basic Analysis: {trade_info['basic_analysis']}")
    print()
    
    # Step 1: Check what main.py does
    print("1️⃣ MAIN.PY LOGIC:")
    likely_action = trade_info['basic_analysis'].get('likely_action', 'buy')
    print(f"   likely_action = {likely_action}")
    
    if likely_action in ['buy', 'unknown']:
        print(f"   ✅ Would proceed with execution (action in ['buy', 'unknown'])")
    else:
        print(f"   ❌ Would SKIP execution (action '{likely_action}' not in ['buy', 'unknown'])")
    print()
    
    # Step 2: Check trade processor logic
    print("2️⃣ TRADE PROCESSOR LOGIC:")
    from trade_processor import TradeProcessor
    
    processor = TradeProcessor(['suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK'])
    
    # Simulate what _extract_action does
    action = trade_info.get('action')
    print(f"   Direct action field: {action}")
    
    if not action and 'basic_analysis' in trade_info:
        action = trade_info['basic_analysis'].get('likely_action', 'unknown')
        print(f"   From basic_analysis: {action}")
    
    if not action:
        action = 'unknown'
        print(f"   Default fallback: {action}")
    
    final_action = action.lower()
    print(f"   Final action: {final_action}")
    print()
    
    # Step 3: What would happen in routing
    print("3️⃣ EXPECTED ROUTING:")
    if final_action in ['buy', 'swap_in']:
        print(f"   Would call: _get_buy_strategy()")
    elif final_action in ['sell', 'swap_out']:
        print(f"   Would call: _get_sell_strategy()")
    else:
        print(f"   Would call: _get_fallback_strategy()")
    print()
    
    # Step 4: Identify the discrepancy
    print("4️⃣ DISCREPANCY ANALYSIS:")
    print(f"   Detected action: '{likely_action}'")
    print(f"   Expected behavior: SKIP (because it's a sell)")
    print(f"   Actual log shows: 'ANALYZING BUY from suqh5sHt...'")
    print(f"   🚨 CONCLUSION: Something is converting 'sell' → 'buy'!")
    print()
    
    # Step 5: Check for copy trading strategy conversion
    print("5️⃣ COPY TRADING STRATEGY CHECK:")
    print("   Possible explanations:")
    print("   A) Emergency fallback forcing action='buy'")
    print("   B) Contrarian strategy: sell → buy conversion")
    print("   C) Action override somewhere in the pipeline")
    print("   D) Different transaction being analyzed")

if __name__ == "__main__":
    asyncio.run(analyze_action_flow())
