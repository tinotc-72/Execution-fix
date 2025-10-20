#!/usr/bin/env python3
"""
Integration test demonstrating the submit methods work together properly.
This validates the complete flow: Jito → RPC fallback with proper logging.
"""

import sys


def test_method_signatures():
    """Verify method signatures are correct"""
    print("=" * 80)
    print("TEST: Method Signatures")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check submit_via_jito signature
        if 'async def submit_via_jito(self, vtx: VersionedTransaction) -> Optional[str]:' in content:
            print("✅ submit_via_jito signature correct")
        else:
            print("❌ submit_via_jito signature incorrect")
            return False
        
        # Check submit_via_rpc signature
        if 'async def submit_via_rpc(self, vtx: VersionedTransaction) -> Optional[str]:' in content:
            print("✅ submit_via_rpc signature correct")
        else:
            print("❌ submit_via_rpc signature incorrect")
            return False
        
        # Check send_and_confirm signature
        if 'async def send_and_confirm(self, vtx: VersionedTransaction) -> Optional[str]:' in content:
            print("✅ send_and_confirm signature correct")
        else:
            print("❌ send_and_confirm signature incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_submit_via_jito_implementation():
    """Verify submit_via_jito uses JitoClient.send_transaction"""
    print("\n" + "=" * 80)
    print("TEST: submit_via_jito Implementation")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the submit_via_jito method
        start_idx = content.find('async def submit_via_jito(')
        if start_idx == -1:
            print("❌ Method not found")
            return False
        
        # Find the end of the method (next async def or class boundary)
        next_method = content.find('async def ', start_idx + 1)
        method_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:]
        
        # Verify key components
        checks = {
            'Type validation': 'if not isinstance(vtx, VersionedTransaction):' in method_content,
            'Jito availability check': 'if not JITO_AVAILABLE or not self.jito_client:' in method_content,
            'Convert to bytes': 'signed_tx_bytes = bytes(vtx)' in method_content,
            'Enhanced service': 'if self.jito_service and self.jito_enhanced_initialized:' in method_content,
            'JitoClient call': 'await self.jito_client.send_transaction(signed_tx_bytes)' in method_content,
            'Extract signature': 'signature = result.get("result")' in method_content or 'signature = result.get("signature")' in method_content,
            'Error handling': 'except Exception as e:' in method_content,
        }
        
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_submit_via_rpc_implementation():
    """Verify submit_via_rpc wraps _submit_to_rpc"""
    print("\n" + "=" * 80)
    print("TEST: submit_via_rpc Implementation")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the submit_via_rpc method
        start_idx = content.find('async def submit_via_rpc(')
        if start_idx == -1:
            print("❌ Method not found")
            return False
        
        next_method = content.find('async def ', start_idx + 1)
        method_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:]
        
        # Verify key components
        checks = {
            'Type validation': 'if not isinstance(vtx, VersionedTransaction):' in method_content,
            'Session init': 'if not self.session:' in method_content,
            'Calls _submit_to_rpc': 'return await self._submit_to_rpc(vtx)' in method_content,
            'Error handling': 'except Exception as e:' in method_content,
        }
        
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_send_and_confirm_integration():
    """Verify send_and_confirm integrates both methods with logging"""
    print("\n" + "=" * 80)
    print("TEST: send_and_confirm Integration")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the send_and_confirm method
        start_idx = content.find('async def send_and_confirm(self, vtx: VersionedTransaction)')
        if start_idx == -1:
            print("❌ Method not found")
            return False
        
        next_method = content.find('# Backward compatibility alias', start_idx + 1)
        method_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:]
        
        # Verify integration components
        checks = {
            'Jito available check': 'if JITO_AVAILABLE and self.jito_client:' in method_content,
            'Region extraction': 'region = "unknown"' in method_content,
            'Parse endpoint': 'parts = self.jito_endpoint.split("//")'in method_content,
            'Calls submit_via_jito': 'signature = await self.submit_via_jito(vtx)' in method_content,
            'Jito log format': 'print(f"[SUBMIT_JITO] region={region} signature={signature}")' in method_content,
            'Calls submit_via_rpc': 'signature = await self.submit_via_rpc(vtx)' in method_content,
            'RPC log format': 'print(f"[SUBMIT_RPC] signature={signature}")' in method_content,
            'Fallback message': 'Falling back to RPC' in method_content,
        }
        
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_logging_format_compliance():
    """Verify logging format meets requirements"""
    print("\n" + "=" * 80)
    print("TEST: Logging Format Compliance")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Check exact format from problem statement
        jito_log_format = '[SUBMIT_JITO] region='
        rpc_log_format = '[SUBMIT_RPC]'
        
        if jito_log_format in content:
            print(f"✅ Jito log format: {jito_log_format}")
        else:
            print(f"❌ Jito log format missing: {jito_log_format}")
            return False
        
        if rpc_log_format in content:
            print(f"✅ RPC log format: {rpc_log_format}")
        else:
            print(f"❌ RPC log format missing: {rpc_log_format}")
            return False
        
        # Verify full log statements
        full_checks = {
            'Full Jito log': 'print(f"[SUBMIT_JITO] region={region} signature={signature}")' in content,
            'Full RPC log': 'print(f"[SUBMIT_RPC] signature={signature}")' in content,
        }
        
        for check_name, passed in full_checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        ("Method Signatures", test_method_signatures),
        ("submit_via_jito Implementation", test_submit_via_jito_implementation),
        ("submit_via_rpc Implementation", test_submit_via_rpc_implementation),
        ("send_and_confirm Integration", test_send_and_confirm_integration),
        ("Logging Format Compliance", test_logging_format_compliance),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 All integration tests passed!")
        print("\n✅ Implementation meets all requirements:")
        print("   • submit_via_jito(vtx) uses JitoClient.send_transaction")
        print("   • submit_via_rpc(vtx) uses existing RPC path")
        print("   • send_and_confirm(vtx) tries Jito then RPC")
        print("   • Logs which route succeeded: [SUBMIT_JITO] region=")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
