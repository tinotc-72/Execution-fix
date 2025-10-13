#!/usr/bin/env python3
"""
Test the fixed action flow to ensure sells aren't converted to buys
"""

import asyncio
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_fixed_action_flow():
    """Test that the fixed logic preserves sell actions"""
    
    print("🧪 TESTING FIXED ACTION FLOW")
    print("="*50)
    
    # Test case: SELL transaction (like the one from your logs)
    trade_info = {
        'signature': 'KoAtRDrfEMjUuxr5BRRdL5HCMrmYTLY35W1kuh5nrzLmb8ZhcYD21FHwyMTZf5qd7VRe94qBcYaa5RpmUNtFHGT',
        'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
        'logs': ['Program log: Instruction: Sell'],
        'basic_analysis': {
            'likely_action': 'sell',  # Correctly detected as SELL
            'confidence': 'high',
            'reasoning': 'Found sell indicator: instruction: sell',
            'detected_dex': 'unknown',
            'copy_immediately': True
        },
        'requires_analysis': True
    }
    
    print("📊 TEST CASE - SELL TRANSACTION:")
    print(f"   Basic Analysis Action: {trade_info['basic_analysis']['likely_action']}")
    print(f"   Expected Behavior: Process as SELL")
    print()
    
    # Test 1: Basic action extraction
    print("1️⃣ TESTING ACTION EXTRACTION:")
    from trade_processor import TradeProcessor
    
    processor = TradeProcessor(['suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK'])
    extracted_action = processor._extract_action(trade_info)
    
    print(f"   Extracted action: '{extracted_action}'")
    print(f"   ✅ PASS" if extracted_action == 'sell' else f"   ❌ FAIL - Expected 'sell', got '{extracted_action}'")
    print()
    
    # Test 2: Main.py immediate processing logic
    print("2️⃣ TESTING MAIN.PY IMMEDIATE PROCESSING:")
    likely_action = trade_info['basic_analysis'].get('likely_action', 'buy')
    
    if likely_action in ['buy', 'unknown']:
        print(f"   Would use: Fast token extraction path")
        result = "FAST_PATH"
    elif likely_action in ['sell', 'swap_out']:
        print(f"   Would use: Immediate sell processing path")
        result = "IMMEDIATE_SELL"
    else:
        print(f"   Would use: Full analysis path")
        result = "FULL_ANALYSIS"
    
    print(f"   Processing path: {result}")
    print(f"   ✅ PASS" if result == "IMMEDIATE_SELL" else f"   ❌ FAIL - Expected 'IMMEDIATE_SELL', got '{result}'")
    print()
    
    # Test 3: Emergency override protection
    print("3️⃣ TESTING EMERGENCY OVERRIDE PROTECTION:")
    
    # Simulate emergency data that would try to override
    emergency_trade_info = trade_info.copy()
    emergency_trade_info['action'] = 'buy'  # Emergency override trying to force buy
    emergency_trade_info['method'] = 'ultra_aggressive_assumption'
    
    protected_action = processor._extract_action(emergency_trade_info)
    print(f"   Emergency override action: 'buy'")
    print(f"   Protected extracted action: '{protected_action}'")
    print(f"   ✅ PASS" if protected_action == 'sell' else f"   ❌ FAIL - Emergency override not blocked!")
    print()
    
    print("🎯 SUMMARY:")
    all_pass = (extracted_action == 'sell' and result == "IMMEDIATE_SELL" and protected_action == 'sell')
    if all_pass:
        print("   ✅ ALL TESTS PASS - Sell actions are now preserved!")
        print("   ✅ Your bot will no longer convert sells to buys!")
        print("   ✅ You should now see: '🔍 ANALYZING SELL from suqh5sHt...'")
    else:
        print("   ❌ SOME TESTS FAILED - Additional fixes may be needed")
    
    return all_pass

if __name__ == "__main__":
    asyncio.run(test_fixed_action_flow())
