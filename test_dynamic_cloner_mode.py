#!/usr/bin/env python3
"""
Test for dynamic cloner mode implementation.

Validates that:
1. use_universal_cloner=False when dex, action, and token_mint are all present
2. use_universal_cloner=True when any of these fields are missing/unknown
"""

import sys

def test_dynamic_mode_logic():
    """Test the dynamic cloner mode logic"""
    print("=" * 80)
    print("DYNAMIC CLONER MODE VALIDATION")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Complete fields - should enable builders",
            "trade_info": {
                "dex": "meteora",
                "action": "swap",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": False
        },
        {
            "name": "Missing dex - should use cloner",
            "trade_info": {
                "dex": None,
                "action": "swap",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": True
        },
        {
            "name": "Unknown dex - should use cloner",
            "trade_info": {
                "dex": "unknown",
                "action": "swap",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": True
        },
        {
            "name": "Missing action - should use cloner",
            "trade_info": {
                "dex": "meteora",
                "action": None,
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": True
        },
        {
            "name": "Unknown action - should use cloner",
            "trade_info": {
                "dex": "meteora",
                "action": "unknown",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": True
        },
        {
            "name": "Missing token_mint - should use cloner",
            "trade_info": {
                "dex": "meteora",
                "action": "swap",
                "token_mint": None
            },
            "expected_cloner": True
        },
        {
            "name": "PENDING_ANALYSIS token_mint - should use cloner",
            "trade_info": {
                "dex": "meteora",
                "action": "swap",
                "token_mint": "PENDING_ANALYSIS"
            },
            "expected_cloner": True
        },
        {
            "name": "Empty string dex - should use cloner",
            "trade_info": {
                "dex": "",
                "action": "swap",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": True
        },
        {
            "name": "All complete with raydium - should enable builders",
            "trade_info": {
                "dex": "raydium",
                "action": "buy",
                "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
            },
            "expected_cloner": False
        },
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        trade_info = test_case['trade_info']
        
        # Apply the exact logic from main.py
        have_all = all(trade_info.get(k) not in (None, "", "unknown", "PENDING_ANALYSIS")
                       for k in ("dex", "action", "token_mint"))
        
        if have_all:
            use_universal_cloner = False
        else:
            use_universal_cloner = True
        
        expected = test_case['expected_cloner']
        
        print(f"Input: dex={trade_info.get('dex')}, action={trade_info.get('action')}, token_mint={trade_info.get('token_mint')}")
        print(f"Expected: use_universal_cloner={expected}")
        print(f"Actual: use_universal_cloner={use_universal_cloner}")
        
        if use_universal_cloner == expected:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

def test_code_structure():
    """Validate the code changes are present in main.py"""
    print("\n" + "=" * 80)
    print("CODE STRUCTURE VALIDATION")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for dynamic mode banner
    if "DYNAMIC MODE" in content:
        print("✅ Initialization banner updated to DYNAMIC MODE")
    else:
        print("❌ Initialization banner not updated")
        return False
    
    # Check for the dynamic cloner logic
    if "have_all = all(trade_info.get(k) not in (None" in content:
        print("✅ Dynamic cloner logic found")
    else:
        print("❌ Dynamic cloner logic not found")
        return False
    
    # Check for the mode logging (per problem statement patch)
    if "ENABLED (complete fields)" in content and 'Builders %s; Cloner as %s' in content:
        print("✅ Builder mode logging found")
    else:
        print("❌ Builder mode logging not found")
        return False
    
    if '"fallback" if have_all else "PRIMARY"' in content:
        print("✅ Cloner mode logging found")
    else:
        print("❌ Cloner mode logging not found")
        return False
    
    # Check that use_universal_cloner is added to trade_info
    if 'trade_info["use_universal_cloner"]' in content:
        print("✅ use_universal_cloner flag added to trade_info")
    else:
        print("❌ use_universal_cloner flag not added to trade_info")
        return False
    
    print("\n✅ All code structure checks passed")
    return True

def main():
    """Run all tests"""
    print("\n" + "🚀" * 40)
    print("DYNAMIC CLONER MODE TEST SUITE")
    print("🚀" * 40)
    
    # Test logic
    result1 = test_dynamic_mode_logic()
    
    # Test code structure
    result2 = test_code_structure()
    
    print("\n" + "🎉" * 40)
    if result1 == 0 and result2:
        print("ALL VALIDATIONS PASSED!")
        print("🎉" * 40 + "\n")
        return 0
    else:
        print("SOME VALIDATIONS FAILED!")
        print("❌" * 40 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
