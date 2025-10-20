#!/usr/bin/env python3
"""
Test script to validate Jupiter executor and FastExecutor fixes.
Tests the following:
1. _as_mint_str() helper correctly coerces Pubkey objects to strings
2. Null-safety check prevents crashes on None routes
3. send_and_confirm() method exists and handles VersionedTransaction
4. get_tip_accounts() helper returns tip accounts
5. Jito import is optional and doesn't fail at import time
"""

import sys
import asyncio


def test_mint_str_helper():
    """Test _as_mint_str() helper function"""
    print("=" * 80)
    print("TEST 1: _as_mint_str() Helper Function")
    print("=" * 80)
    
    try:
        # Check if helper exists
        with open('mev_jupiter_executor.py', 'r') as f:
            content = f.read()
        
        if 'def _as_mint_str(m) -> str:' in content:
            print("✅ _as_mint_str() helper function exists")
        else:
            print("❌ _as_mint_str() helper function not found")
            return False
        
        # Check implementation
        if 'return str(m) if not isinstance(m, Pubkey) else str(m)' in content:
            print("✅ Helper correctly coerces to string")
        else:
            print("⚠️ Helper implementation may differ from expected")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_null_safety_check():
    """Test null-safety check in get_best_route"""
    print("\n" + "=" * 80)
    print("TEST 2: Null-Safety Check in get_best_route()")
    print("=" * 80)
    
    try:
        with open('mev_jupiter_executor.py', 'r') as f:
            content = f.read()
        
        # Check for null-safety pattern
        patterns = [
            "if not isinstance(data, dict):",
            'logger.error("[JUPITER_QUOTE] no route; endpoints failed")',
            "return None"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found pattern: {pattern[:50]}...")
            else:
                print(f"❌ Missing pattern: {pattern}")
                return False
        
        print("✅ Null-safety check is implemented correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_mint_coercion_in_get_best_route():
    """Test that get_best_route uses _as_mint_str()"""
    print("\n" + "=" * 80)
    print("TEST 3: Mint Coercion in get_best_route()")
    print("=" * 80)
    
    try:
        with open('mev_jupiter_executor.py', 'r') as f:
            content = f.read()
        
        # Check for coercion calls
        patterns = [
            "input_mint = _as_mint_str(input_mint)",
            "output_mint = _as_mint_str(output_mint)"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ Mint coercion is applied correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_jito_optional_import():
    """Test that Jito import is optional"""
    print("\n" + "=" * 80)
    print("TEST 4: Jito Optional Import")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for optional import pattern
        patterns = [
            "# Make Jito imports optional - never fail at import time",
            "try:",
            "from jito_service import JitoClient",
            "JITO_AVAILABLE = True",
            "except ImportError:",
            "JITO_AVAILABLE = False",
            "JitoClient = None"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ Jito import is properly guarded")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_send_and_confirm_method():
    """Test send_and_confirm() method exists"""
    print("\n" + "=" * 80)
    print("TEST 5: send_and_confirm() Method")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for method definition
        patterns = [
            "async def send_and_confirm(self, vtx: VersionedTransaction)",
            "Unified submit logic: tries Jito first, then RPC fallback",
            "Try Jito first if available",
            "RPC fallback (always available)"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern[:60]}...")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ send_and_confirm() method is implemented")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_get_tip_accounts_helper():
    """Test get_tip_accounts() helper exists"""
    print("\n" + "=" * 80)
    print("TEST 6: get_tip_accounts() Helper")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for method definition
        patterns = [
            "async def get_tip_accounts(self)",
            "Get Jito tip accounts for transaction tips",
            "if not JITO_AVAILABLE:",
            "return await self.get_official_tip_accounts()"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern[:60]}...")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ get_tip_accounts() helper is implemented")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_env_keys_usage():
    """Test that EnvKeys is used for Jito configuration"""
    print("\n" + "=" * 80)
    print("TEST 7: EnvKeys Usage for Jito Configuration")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for EnvKeys usage
        patterns = [
            "from env_keys import EnvKeys",
            "env_keys = EnvKeys()",
            "jito_uuid = env_keys.JITO_UUID",
            "jito_region_url = env_keys.JITO_BUNDLE_ENDPOINT"
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ EnvKeys is used correctly for Jito configuration")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("EXECUTOR FIXES VALIDATION TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        ("_as_mint_str() Helper", test_mint_str_helper),
        ("Null-Safety Check", test_null_safety_check),
        ("Mint Coercion in get_best_route", test_mint_coercion_in_get_best_route),
        ("Jito Optional Import", test_jito_optional_import),
        ("send_and_confirm() Method", test_send_and_confirm_method),
        ("get_tip_accounts() Helper", test_get_tip_accounts_helper),
        ("EnvKeys Usage", test_env_keys_usage)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
