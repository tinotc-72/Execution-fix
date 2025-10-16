#!/usr/bin/env python3
"""
Test script to validate new submit_via_jito and submit_via_rpc methods.
Tests the following:
1. submit_via_jito() method exists and uses JitoClient.send_transaction
2. submit_via_rpc() method exists (wrapper for _submit_to_rpc)
3. send_and_confirm() logs which route succeeded with [SUBMIT_JITO] region= format
"""

import sys


def test_submit_via_jito_exists():
    """Test that submit_via_jito method exists"""
    print("=" * 80)
    print("TEST 1: submit_via_jito() Method Exists")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for method definition
        patterns = [
            "async def submit_via_jito(self, vtx: VersionedTransaction)",
            "Submit transaction via Jito using JitoClient.send_transaction",
            "await self.jito_client.send_transaction(signed_tx_bytes)",
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern[:60]}...")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ submit_via_jito() method is implemented")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_submit_via_rpc_exists():
    """Test that submit_via_rpc method exists"""
    print("\n" + "=" * 80)
    print("TEST 2: submit_via_rpc() Method Exists")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for method definition
        patterns = [
            "async def submit_via_rpc(self, vtx: VersionedTransaction)",
            "Submit transaction via RPC (existing path)",
            "return await self._submit_to_rpc(vtx)",
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern[:60]}...")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ submit_via_rpc() method is implemented")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_send_and_confirm_uses_new_methods():
    """Test that send_and_confirm uses new submit methods"""
    print("\n" + "=" * 80)
    print("TEST 3: send_and_confirm() Uses New Submit Methods")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for method calls
        patterns = [
            "signature = await self.submit_via_jito(vtx)",
            "signature = await self.submit_via_rpc(vtx)",
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ send_and_confirm() uses new submit methods")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_jito_logging_format():
    """Test that send_and_confirm logs Jito route with correct format"""
    print("\n" + "=" * 80)
    print("TEST 4: Jito Logging Format [SUBMIT_JITO] region=")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for logging pattern
        patterns = [
            'print(f"[SUBMIT_JITO] region={region} signature={signature}")',
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ Jito logging format is correct")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_rpc_logging_format():
    """Test that send_and_confirm logs RPC route"""
    print("\n" + "=" * 80)
    print("TEST 5: RPC Logging Format [SUBMIT_RPC]")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for logging pattern
        patterns = [
            'print(f"[SUBMIT_RPC] signature={signature}")',
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ RPC logging format is correct")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_region_extraction():
    """Test that region is extracted from jito_endpoint"""
    print("\n" + "=" * 80)
    print("TEST 6: Region Extraction from Endpoint")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for region extraction logic
        patterns = [
            'region = "unknown"',
            'if self.jito_endpoint:',
            'parts = self.jito_endpoint.split("//")',
            'domain_parts = parts[1].split(".")',
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ Region extraction logic is implemented")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_jito_client_send_transaction_usage():
    """Test that submit_via_jito uses JitoClient.send_transaction"""
    print("\n" + "=" * 80)
    print("TEST 7: JitoClient.send_transaction Usage")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check for JitoClient.send_transaction call
        patterns = [
            "result = await self.jito_client.send_transaction(signed_tx_bytes)",
            '# JSON-RPC shape: {"jsonrpc":"2.0","id":1,"result":"<signature>"}',
            'signature = result.get("result")',
        ]
        
        for pattern in patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
            else:
                print(f"❌ Missing: {pattern}")
                return False
        
        print("✅ JitoClient.send_transaction is used correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SUBMIT METHODS VALIDATION TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        ("submit_via_jito() exists", test_submit_via_jito_exists),
        ("submit_via_rpc() exists", test_submit_via_rpc_exists),
        ("send_and_confirm() uses new methods", test_send_and_confirm_uses_new_methods),
        ("Jito logging format", test_jito_logging_format),
        ("RPC logging format", test_rpc_logging_format),
        ("Region extraction", test_region_extraction),
        ("JitoClient.send_transaction usage", test_jito_client_send_transaction_usage),
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
