#!/usr/bin/env python3

"""
Test strict action extraction in trade_processor.py
Verifies that actions are only returned when there are actual token balance changes
"""

import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Mock trade info with no balance changes (account creation)
MOCK_NO_BALANCE_CHANGE = {
    'signature': 'account_creation_test_sig',
    'action': 'buy',  # This should be ignored due to no balance change
    'basic_analysis': {
        'likely_action': 'buy',  # This should also be ignored
    },
    'meta': {
        'preTokenBalances': [],
        'postTokenBalances': [{
            'owner': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'mint': 'GnM6XZ7DN9KSPW2ZVMNqCggsxjnxHMGb2t4kiWrUpump',
            'uiTokenAmount': {
                'amount': '0',  # Zero balance - no actual change
                'decimals': 6
            }
        }]
    }
}

# Mock trade info with actual balance changes
MOCK_WITH_BALANCE_CHANGE = {
    'signature': 'real_trade_test_sig',
    'action': 'buy',
    'basic_analysis': {
        'likely_action': 'buy',
    },
    'meta': {
        'preTokenBalances': [{
            'owner': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'mint': 'GnM6XZ7DN9KSPW2ZVMNqCggsxjnxHMGb2t4kiWrUpump',
            'uiTokenAmount': {
                'amount': '0',  # Starting with 0
                'decimals': 6
            }
        }],
        'postTokenBalances': [{
            'owner': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'mint': 'GnM6XZ7DN9KSPW2ZVMNqCggsxjnxHMGb2t4kiWrUpump',
            'uiTokenAmount': {
                'amount': '1000000',  # Now has tokens - real change
                'decimals': 6
            }
        }]
    }
}

# Mock trade info with ultra-aggressive assumption (should be ignored)
MOCK_ULTRA_AGGRESSIVE = {
    'signature': 'ultra_aggressive_test_sig',
    'action': 'buy',
    'method': 'ultra_aggressive_assumption',  # Should be rejected
    'meta': {
        'preTokenBalances': [{
            'owner': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'mint': 'GnM6XZ7DN9KSPW2ZVMNqCggsxjnxHMGb2t4kiWrUpump',
            'uiTokenAmount': {
                'amount': '0',
                'decimals': 6
            }
        }],
        'postTokenBalances': [{
            'owner': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'mint': 'GnM6XZ7DN9KSPW2ZVMNqCggsxjnxHMGb2t4kiWrUpump',
            'uiTokenAmount': {
                'amount': '500000',  # Has change but method is unreliable
                'decimals': 6
            }
        }]
    }
}

async def test_strict_action_extraction():
    """Test strict action extraction requirements"""
    
    print("🧪 Testing Strict Action Extraction in TradeProcessor")
    print("=" * 65)
    
    try:
        # Import the TradeProcessor
        from trade_processor import TradeProcessor
        
        # Initialize processor
        processor = TradeProcessor(
            target_wallets=["A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"],
            rpc_client=None
        )
        
        # Test 1: No balance change should return 'unknown'
        print("\\n🔍 Test 1: No Token Balance Change")
        print("-" * 40)
        
        result1 = processor._extract_action(MOCK_NO_BALANCE_CHANGE)
        print(f"Input: Account creation with action='buy' in both direct and basic_analysis")
        print(f"Expected: 'unknown' (no balance change)")
        print(f"Actual: '{result1}'")
        
        if result1 == 'unknown':
            print("✅ SUCCESS: No balance change correctly returns 'unknown'")
        else:
            print(f"❌ FAILED: Expected 'unknown', got '{result1}'")
        
        # Test 2: With balance change should allow specific action
        print("\\n🔍 Test 2: With Token Balance Change")
        print("-" * 40)
        
        result2 = processor._extract_action(MOCK_WITH_BALANCE_CHANGE)
        print(f"Input: Real trade with token balance increase")
        print(f"Expected: 'buy' (balance change + valid action)")
        print(f"Actual: '{result2}'")
        
        if result2 == 'buy':
            print("✅ SUCCESS: Balance change allows specific action")
        else:
            print(f"❌ FAILED: Expected 'buy', got '{result2}'")
        
        # Test 3: Ultra-aggressive assumption should be rejected even with balance change
        print("\\n🔍 Test 3: Ultra-Aggressive Assumption Rejection")
        print("-" * 40)
        
        result3 = processor._extract_action(MOCK_ULTRA_AGGRESSIVE)
        print(f"Input: Has balance change but method='ultra_aggressive_assumption'")
        print(f"Expected: 'unknown' (unreliable method rejected)")
        print(f"Actual: '{result3}'")
        
        if result3 == 'unknown':
            print("✅ SUCCESS: Ultra-aggressive assumptions correctly rejected")
        else:
            print(f"❌ FAILED: Expected 'unknown', got '{result3}'")
        
        # Test 4: Balance change detection helper
        print("\\n🔍 Test 4: Balance Change Detection Helper")
        print("-" * 40)
        
        has_change_1 = processor._has_actual_token_balance_change(MOCK_NO_BALANCE_CHANGE)
        has_change_2 = processor._has_actual_token_balance_change(MOCK_WITH_BALANCE_CHANGE)
        
        print(f"No balance change case: {has_change_1} (should be False)")
        print(f"With balance change case: {has_change_2} (should be True)")
        
        if not has_change_1 and has_change_2:
            print("✅ SUCCESS: Balance change detection works correctly")
        else:
            print(f"❌ FAILED: Balance detection incorrect - no_change:{has_change_1}, with_change:{has_change_2}")
        
        # Summary
        print("\\n" + "=" * 65)
        print("🏆 STRICT ACTION EXTRACTION TEST SUMMARY")
        print("=" * 65)
        
        all_passed = (result1 == 'unknown' and 
                     result2 == 'buy' and 
                     result3 == 'unknown' and
                     not has_change_1 and has_change_2)
        
        if all_passed:
            print("✅ ALL TESTS PASSED!")
            print("✅ Changes implemented:")
            print("  • _extract_action now requires actual token balance changes")
            print("  • Returns 'unknown' for account creation (no balance change)")
            print("  • Rejects ultra-aggressive assumptions even with balance changes")
            print("  • Only allows buy/sell/swap when real token movement is detected")
            
            print("\\n🎯 Expected behavior:")
            print("  • Account creation → Action: 'unknown'")
            print("  • Real token trades → Action: 'buy'/'sell'/'swap'")
            print("  • Ultra-aggressive methods → Action: 'unknown' (rejected)")
            
            return True
        else:
            print("❌ SOME TESTS FAILED - see results above")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_strict_action_extraction())
    
    if success:
        print("\\n🎉 STRICT ACTION EXTRACTION SUCCESSFULLY IMPLEMENTED!")
        print("Your trade processor now requires real token balance changes before determining actions.")
    else:
        print("\\n⚠️ Some issues remain - check the test output above.")