#!/usr/bin/env python3
"""
Test script to validate the single reliable RPC submitter implementation.

This test verifies:
1. executors/submit.py module exists and exports send_and_confirm_v0_tx
2. send_and_confirm_v0_tx has proper signature and docstring
3. FastExecutor now returns structured results with signature and status
4. All executors import the shared submitter
5. Jito-first with RPC fallback pattern is preserved
"""

import sys
import os


def test_submit_module_exists():
    """Test that executors/submit.py module exists"""
    print("=" * 80)
    print("TEST 1: executors/submit.py Module Exists")
    print("=" * 80)
    
    try:
        # Check if directory exists
        if not os.path.exists("executors"):
            print("❌ executors directory does not exist")
            return False
        
        # Check if submit.py exists
        if not os.path.exists("executors/submit.py"):
            print("❌ executors/submit.py does not exist")
            return False
        
        # Try to import
        try:
            from executors.submit import send_and_confirm_v0_tx
            print("✅ executors/submit.py exists and imports successfully")
            return True
        except ImportError as e:
            print(f"❌ Failed to import: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_send_and_confirm_signature():
    """Test that send_and_confirm_v0_tx has correct signature"""
    print("\n" + "=" * 80)
    print("TEST 2: send_and_confirm_v0_tx Function Signature")
    print("=" * 80)
    
    try:
        with open('executors/submit.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Function definition': 'async def send_and_confirm_v0_tx(' in content,
            'vtx parameter': 'vtx: VersionedTransaction' in content,
            'rpc_url parameter': 'rpc_url: str' in content,
            'max_retries parameter': 'max_retries: int = 5' in content,
            'retry_delay parameter': 'retry_delay: float = 0.8' in content,
            'Returns Dict': '-> Dict[str, Any]:' in content,
            'Docstring': 'Send a VersionedTransaction to the RPC and confirm it.' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_structured_results():
    """Test that send_and_confirm_v0_tx returns structured results"""
    print("\n" + "=" * 80)
    print("TEST 3: Structured Result Format")
    print("=" * 80)
    
    try:
        with open('executors/submit.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Returns success field': '"success": True' in content,
            'Returns signature field': '"signature": sig' in content,
            'Returns status field': '"status": status' in content,
            'Returns error on failure': '"error":' in content,
            'No None returns on success': 'return None' not in content or '"success": False' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_rpc_submission():
    """Test that send_and_confirm_v0_tx properly submits to RPC"""
    print("\n" + "=" * 80)
    print("TEST 4: RPC Submission Implementation")
    print("=" * 80)
    
    try:
        with open('executors/submit.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Uses sendTransaction RPC method': '"method": "sendTransaction"' in content,
            'Uses base64 encoding': 'base64.b64encode(raw).decode()' in content,
            'Uses httpx.AsyncClient': 'async with httpx.AsyncClient' in content,
            'Posts to RPC URL': 'await client.post(rpc_url' in content,
            'Extracts signature from result': 'sig = data.get("result")' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_confirmation_polling():
    """Test that send_and_confirm_v0_tx polls for confirmation"""
    print("\n" + "=" * 80)
    print("TEST 5: Confirmation Polling Implementation")
    print("=" * 80)
    
    try:
        with open('executors/submit.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Uses getSignatureStatuses': '"method": "getSignatureStatuses"' in content,
            'Searches transaction history': '"searchTransactionHistory": True' in content,
            'Has retry loop': 'for attempt in range(1, max_retries + 1):' in content,
            'Logs confirmation attempts': '[CONFIRM] attempt=' in content,
            'Logs final status': '[CONFIRM][FINAL]' in content,
            'Sleeps between retries': 'await asyncio.sleep(retry_delay)' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_fast_executor_integration():
    """Test that FastExecutor uses send_and_confirm_v0_tx"""
    print("\n" + "=" * 80)
    print("TEST 6: FastExecutor Integration")
    print("=" * 80)
    
    try:
        with open('fast_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Imports send_and_confirm_v0_tx': 'from executors.submit import send_and_confirm_v0_tx' in content,
            'send_and_confirm returns Dict': '-> Optional[Dict[str, Any]]:' in content,
            'Calls send_and_confirm_v0_tx': 'await send_and_confirm_v0_tx(vtx, self._rpc_url)' in content,
            'Jito-first pattern preserved': 'if self.use_jito:' in content and 'await self._submit_via_jito(vtx)' in content,
            'Returns structured result': 'return result' in content or '"success": True' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_jupiter_executor_integration():
    """Test that Jupiter executor uses shared submitter"""
    print("\n" + "=" * 80)
    print("TEST 7: Jupiter Executor Integration")
    print("=" * 80)
    
    try:
        with open('mev_jupiter_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Imports send_and_confirm_v0_tx': 'from executors.submit import send_and_confirm_v0_tx' in content,
            'Uses send_and_confirm_v0_tx in retry': 'await send_and_confirm_v0_tx(transaction, RPC_URL' in content,
            'Jito-first pattern in retry': 'if jito_is_configured(self.jito_service):' in content,
            'Returns signature on success': 'return signature' in content or 'return sig' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_meteora_executor_integration():
    """Test that Meteora executor handles structured results"""
    print("\n" + "=" * 80)
    print("TEST 8: Meteora Executor Integration")
    print("=" * 80)
    
    try:
        with open('mev_meteora_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            'Calls send_and_confirm': 'await self.fast_executor.send_and_confirm(vtx)' in content or 'await fast_executor.send_and_confirm(vtx)' in content,
            'Handles structured result': 'result.get("success")' in content or 'result["signature"]' in content,
            'Extracts signature from result': 'sig = result["signature"]' in content,
            'Handles error from result': 'result.get("error")' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_direct_copy_executor_integration():
    """Test that Direct Copy executor handles structured results"""
    print("\n" + "=" * 80)
    print("TEST 9: Direct Copy Executor Integration")
    print("=" * 80)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        checks = {
            'submit_cloned_tx calls send_and_confirm': 'await fast_executor.send_and_confirm(final_vtx)' in content,
            'Handles structured result': 'result.get("success")' in content,
            'Extracts signature from result': 'signature = result["signature"]' in content,
            'Handles error from result': 'result.get("error")' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SINGLE RELIABLE RPC SUBMITTER VALIDATION TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        ("Submit Module Exists", test_submit_module_exists),
        ("send_and_confirm_v0_tx Signature", test_send_and_confirm_signature),
        ("Structured Result Format", test_structured_results),
        ("RPC Submission Implementation", test_rpc_submission),
        ("Confirmation Polling", test_confirmation_polling),
        ("FastExecutor Integration", test_fast_executor_integration),
        ("Jupiter Executor Integration", test_jupiter_executor_integration),
        ("Meteora Executor Integration", test_meteora_executor_integration),
        ("Direct Copy Executor Integration", test_direct_copy_executor_integration),
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
        print("   • executors/submit.py with send_and_confirm_v0_tx() created")
        print("   • All executors refactored to use shared submitter")
        print("   • Structured results with signature and status")
        print("   • Jito-first with RPC fallback preserved")
        print("   • Robust confirmation polling implemented")
        print("   • No None returns on success")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
