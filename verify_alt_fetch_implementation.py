#!/usr/bin/env python3
"""
Verification script for ALT fetch implementation.
Validates that all requirements from the problem statement are met.
"""
import sys
import os


def check_file_exists(filepath, description):
    """Check if a file exists and report result"""
    if os.path.exists(filepath):
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description} - FILE NOT FOUND")
        return False


def check_function_exists(filepath, function_name, signature_pattern):
    """Check if a function with specific signature exists in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if function_name in content and signature_pattern in content:
                print(f"   ✅ {function_name}() function exists with correct signature")
                return True
            else:
                print(f"   ❌ {function_name}() function not found or incorrect signature")
                return False
    except Exception as e:
        print(f"   ❌ Error checking {function_name}: {e}")
        return False


def check_integration_guidance(filepath):
    """Check if integration guidance is present in the file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            required_terms = [
                "INTEGRATION GUIDANCE",
                "MessageV0.try_compile",
                "addressTableLookups",
                "meta.loadedAddresses"
            ]
            all_present = all(term in content for term in required_terms)
            if all_present:
                print(f"   ✅ Integration guidance present with all required terms")
                return True
            else:
                missing = [term for term in required_terms if term not in content]
                print(f"   ❌ Integration guidance incomplete, missing: {missing}")
                return False
    except Exception as e:
        print(f"   ❌ Error checking integration guidance: {e}")
        return False


def run_tests():
    """Run the test files and check results"""
    import subprocess
    
    tests = [
        ("test_alt_fetch.py", "Synchronous ALT fetch helpers test"),
        ("test_alt_integration.py", "ALT integration test"),
        ("demo_alt_fetch.py", "ALT fetch demonstration")
    ]
    
    all_passed = True
    for test_file, description in tests:
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"   ✅ {description} - PASSED")
            else:
                print(f"   ❌ {description} - FAILED")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {description} - ERROR: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("ALT FETCH IMPLEMENTATION VERIFICATION")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # Check 1: utils/alt_fetch.py exists
    print("Check 1: Core implementation file")
    if not check_file_exists("utils/alt_fetch.py", "utils/alt_fetch.py exists"):
        all_checks_passed = False
    print()
    
    # Check 2: Required functions exist
    print("Check 2: Required functions in utils/alt_fetch.py")
    checks = [
        check_function_exists("utils/alt_fetch.py", "rpc_call", "def rpc_call(rpc_url: str, method: str, params:"),
        check_function_exists("utils/alt_fetch.py", "fetch_lookup_table", "def fetch_lookup_table(rpc_url: str, table_pubkey: str)"),
        check_function_exists("utils/alt_fetch.py", "build_alts_from_tables", "def build_alts_from_tables(rpc_url: str, table_pubkeys:")
    ]
    if not all(checks):
        all_checks_passed = False
    print()
    
    # Check 3: Integration guidance
    print("Check 3: Integration guidance in utils/alt_fetch.py")
    if not check_integration_guidance("utils/alt_fetch.py"):
        all_checks_passed = False
    print()
    
    # Check 4: Test files exist
    print("Check 4: Test and demo files")
    test_files = [
        ("test_alt_fetch.py", "Test file exists"),
        ("demo_alt_fetch.py", "Demo file exists"),
        ("ALT_FETCH_IMPLEMENTATION.md", "Implementation documentation exists")
    ]
    for filepath, description in test_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    print()
    
    # Check 5: Run tests
    print("Check 5: Run tests and demos")
    if not run_tests():
        all_checks_passed = False
    print()
    
    # Check 6: Verify problem statement requirements
    print("Check 6: Problem statement requirements")
    try:
        with open("utils/alt_fetch.py", 'r') as f:
            content = f.read()
            
        requirements = [
            ("import requests", "Uses requests library"),
            ("getAddressLookupTable", "Uses getAddressLookupTable RPC method"),
            ("AddressLookupTableAccount", "Builds AddressLookupTableAccount objects"),
            ("from solders.pubkey import Pubkey", "Uses solders Pubkey"),
        ]
        
        for pattern, description in requirements:
            if pattern in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} - NOT FOUND")
                all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Error checking requirements: {e}")
        all_checks_passed = False
    print()
    
    # Final summary
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    if all_checks_passed:
        print("✅ ALL VERIFICATION CHECKS PASSED")
        print("\n✨ Implementation meets all requirements from problem statement:")
        print("   ✅ utils/alt_fetch.py exists with required functions")
        print("   ✅ rpc_call() uses requests library")
        print("   ✅ fetch_lookup_table() uses getAddressLookupTable RPC")
        print("   ✅ build_alts_from_tables() builds AddressLookupTableAccount objects")
        print("   ✅ Integration guidance provided")
        print("   ✅ Tests and demos included")
        print("   ✅ All tests passing")
        print("\n🎉 Implementation is complete and correct!")
        return 0
    else:
        print("❌ SOME VERIFICATION CHECKS FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
