#!/usr/bin/env python3
"""
Test for getSignatureStatuses confirmation functionality in FastExecutor.
Validates the implementation according to the problem statement.
"""

import sys


def test_imports():
    """Verify httpx and asyncio imports are present"""
    print("=" * 80)
    print("TEST: Imports")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            'httpx import': 'import httpx' in content,
            'asyncio import': 'import asyncio' in content,
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


def test_rpc_url_initialization():
    """Verify _rpc_url is initialized in __init__"""
    print("\n" + "=" * 80)
    print("TEST: RPC URL Initialization")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the __init__ method
        start_idx = content.find('def __init__(self')
        if start_idx == -1:
            print("❌ __init__ method not found")
            return False
        
        # Find the end of __init__ (next method definition)
        next_method = content.find('def _get_default_logger', start_idx)
        init_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:start_idx+2000]
        
        checks = {
            'EnvKeys import in method': 'env_keys = EnvKeys()' in init_content or 'from env_keys import EnvKeys' in content,
            '_rpc_url initialization': 'self._rpc_url = getattr(env_keys, "HELIUS_RPC_URL", None)' in init_content,
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


def test_confirm_once_method():
    """Verify _confirm_once method implementation"""
    print("\n" + "=" * 80)
    print("TEST: _confirm_once Method")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the _confirm_once method
        start_idx = content.find('async def _confirm_once(self, sig: str) -> dict | None:')
        if start_idx == -1:
            print("❌ _confirm_once method not found")
            return False
        
        # Find the end of the method
        next_method = content.find('async def _confirm_with_retries', start_idx)
        method_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:]
        
        checks = {
            'RPC URL check': 'if not self._rpc_url:' in method_content,
            'Warning log': 'self.logger.warning("[CONFIRM] no RPC url configured")' in method_content,
            'Payload structure': '"method":"getSignatureStatuses"' in method_content,
            'searchTransactionHistory': '"searchTransactionHistory": True' in method_content,
            'httpx.AsyncClient': 'async with httpx.AsyncClient(timeout=10.0) as client:' in method_content,
            'POST request': 'await client.post(self._rpc_url, json=payload)' in method_content,
            'raise_for_status': 'r.raise_for_status()' in method_content,
            'return JSON': 'return r.json()' in method_content,
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


def test_confirm_with_retries_method():
    """Verify _confirm_with_retries method implementation"""
    print("\n" + "=" * 80)
    print("TEST: _confirm_with_retries Method")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the _confirm_with_retries method
        start_idx = content.find('async def _confirm_with_retries(self, sig: str, attempts: int = 5, delay_s: float = 0.8)')
        if start_idx == -1:
            print("❌ _confirm_with_retries method not found")
            return False
        
        # Find the end of the method
        next_method = content.find('async def close', start_idx)
        method_content = content[start_idx:next_method] if next_method != -1 else content[start_idx:]
        
        checks = {
            'For loop': 'for i in range(attempts):' in method_content,
            'Call _confirm_once': 'data = await self._confirm_once(sig)' in method_content,
            'Extract value': 'value = ((data or {}).get("result") or {}).get("value") or []' in method_content,
            'Extract status': 'status = value[0] if value else None' in method_content,
            'Log attempt': 'self.logger.info(f"[CONFIRM] attempt={i+1}/{attempts} status={status}")' in method_content,
            'Check status': 'if status:' in method_content,
            'Return status': 'return status' in method_content,
            'Sleep between attempts': 'await asyncio.sleep(delay_s)' in method_content,
            'Return None on failure': 'return None' in method_content,
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
    """Verify send_and_confirm calls _confirm_with_retries"""
    print("\n" + "=" * 80)
    print("TEST: send_and_confirm Integration")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        # Find the send_and_confirm method
        start_idx = content.find('async def send_and_confirm(self, vtx')
        if start_idx == -1:
            print("❌ send_and_confirm method not found")
            return False
        
        # Get method content (find end of method)
        method_end = start_idx + 1000  # reasonable length for the method
        method_content = content[start_idx:method_end]
        
        checks = {
            'Call _submit_via_jito': 'sig = await self._submit_via_jito(vtx)' in method_content,
            'Check sig from Jito': 'if not sig:' in method_content,
            'Call _submit_to_rpc': 'sig = await self._submit_to_rpc(vtx)' in method_content or 'sig = await self._submit_via_rpc(vtx)' in method_content,
            'Return None on no sig': 'if not sig:' in method_content and 'return None' in method_content,
            'Call _confirm_with_retries': 'status = await self._confirm_with_retries(sig)' in method_content,
            'Final log': 'self.logger.info(f"[CONFIRM][FINAL] sig={sig} status={status}")' in method_content,
            'Return signature': 'return sig' in method_content,
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


def test_log_format_compliance():
    """Verify logging format meets requirements"""
    print("\n" + "=" * 80)
    print("TEST: Logging Format Compliance")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            '[CONFIRM] log format': '[CONFIRM] attempt=' in content and '[CONFIRM] no RPC url configured' in content,
            '[CONFIRM][FINAL] log format': '[CONFIRM][FINAL] sig=' in content and 'status=' in content,
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


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CONFIRMATION FUNCTIONALITY TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("RPC URL Initialization", test_rpc_url_initialization),
        ("_confirm_once Method", test_confirm_once_method),
        ("_confirm_with_retries Method", test_confirm_with_retries_method),
        ("send_and_confirm Integration", test_send_and_confirm_integration),
        ("Logging Format Compliance", test_log_format_compliance),
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
        print("\n🎉 All tests passed!")
        print("\n✅ Implementation meets all requirements:")
        print("   • httpx and asyncio imports added")
        print("   • self._rpc_url initialized from EnvKeys")
        print("   • _confirm_once() calls getSignatureStatuses")
        print("   • _confirm_with_retries() implements retry logic")
        print("   • send_and_confirm() calls confirmation after submit")
        print("   • Logs [CONFIRM][FINAL] with signature and status")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
