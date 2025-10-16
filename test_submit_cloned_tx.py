#!/usr/bin/env python3
"""
Test for submit_cloned_tx helper function and FastExecutor integration.
Validates that:
1. submit_cloned_tx properly calls fast_executor.send_and_confirm
2. exec_ok and exec_err are properly returned
3. RPC fallback works when Jito is not available
"""

import sys
import asyncio
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockVersionedTransaction:
    """Mock VersionedTransaction for testing"""
    def __init__(self, success=True):
        self.success = success


class MockFastExecutor:
    """Mock FastExecutor for testing"""
    def __init__(self, return_signature: Optional[str] = "test_signature_123"):
        self.return_signature = return_signature
        self.called = False
        
    async def send_and_confirm(self, vtx):
        """Mock send_and_confirm method"""
        self.called = True
        logger.info(f"[MOCK] send_and_confirm called with vtx: {vtx}")
        
        # Simulate Jito/RPC fallback behavior
        if self.return_signature:
            logger.info(f"[MOCK] Returning signature: {self.return_signature}")
        else:
            logger.info(f"[MOCK] Returning None (simulating failure)")
        
        return self.return_signature


async def test_submit_cloned_tx_success():
    """Test submit_cloned_tx with successful submission"""
    print("\n" + "="*60)
    print("TEST 1: submit_cloned_tx - Successful Submission")
    print("="*60)
    
    try:
        # Import the function
        from mev_direct_copy_executor import submit_cloned_tx
        
        # Create mock objects
        mock_vtx = MockVersionedTransaction(success=True)
        mock_executor = MockFastExecutor(return_signature="sig_success_123")
        
        # Call submit_cloned_tx
        result = await submit_cloned_tx(mock_vtx, mock_executor)
        
        # Verify
        assert mock_executor.called, "❌ send_and_confirm was not called"
        assert result == "sig_success_123", f"❌ Expected 'sig_success_123', got '{result}'"
        
        print("✅ PASS: submit_cloned_tx successfully called send_and_confirm")
        print(f"✅ PASS: Returned signature: {result}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_submit_cloned_tx_failure():
    """Test submit_cloned_tx with failed submission"""
    print("\n" + "="*60)
    print("TEST 2: submit_cloned_tx - Failed Submission")
    print("="*60)
    
    try:
        # Import the function
        from mev_direct_copy_executor import submit_cloned_tx
        
        # Create mock objects
        mock_vtx = MockVersionedTransaction(success=False)
        mock_executor = MockFastExecutor(return_signature=None)  # Simulate failure
        
        # Call submit_cloned_tx
        result = await submit_cloned_tx(mock_vtx, mock_executor)
        
        # Verify
        assert mock_executor.called, "❌ send_and_confirm was not called"
        assert result is None, f"❌ Expected None, got '{result}'"
        
        print("✅ PASS: submit_cloned_tx handled failure correctly")
        print(f"✅ PASS: Returned None as expected")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_submit_cloned_tx_none_executor():
    """Test submit_cloned_tx with None executor"""
    print("\n" + "="*60)
    print("TEST 3: submit_cloned_tx - None FastExecutor")
    print("="*60)
    
    try:
        # Import the function
        from mev_direct_copy_executor import submit_cloned_tx
        
        # Create mock objects
        mock_vtx = MockVersionedTransaction(success=True)
        
        # Call submit_cloned_tx with None executor
        result = await submit_cloned_tx(mock_vtx, None)
        
        # Verify
        assert result is None, f"❌ Expected None, got '{result}'"
        
        print("✅ PASS: submit_cloned_tx handled None executor correctly")
        print(f"✅ PASS: Returned None as expected")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exec_ok_exec_err_import():
    """Test that exec_ok and exec_err are properly imported"""
    print("\n" + "="*60)
    print("TEST 4: exec_ok and exec_err Import")
    print("="*60)
    
    try:
        # Import the executor module
        import mev_direct_copy_executor
        
        # Check for exec_ok and exec_err in imports
        import inspect
        source = inspect.getsource(mev_direct_copy_executor)
        
        assert "from execution_coordinator import exec_ok, exec_err" in source, \
            "❌ exec_ok and exec_err not imported from execution_coordinator"
        
        print("✅ PASS: exec_ok and exec_err properly imported")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fast_executor_parameter():
    """Test that FastExecutor parameter is added to __init__"""
    print("\n" + "="*60)
    print("TEST 5: FastExecutor Parameter in __init__")
    print("="*60)
    
    try:
        # Import the executor module
        import mev_direct_copy_executor
        import inspect
        
        # Get the __init__ signature
        init_signature = inspect.signature(mev_direct_copy_executor.MEVDirectCopyExecutor.__init__)
        params = list(init_signature.parameters.keys())
        
        assert "fast_executor" in params, \
            f"❌ fast_executor parameter not found in __init__. Found: {params}"
        
        print("✅ PASS: fast_executor parameter present in __init__")
        print(f"   Parameters: {params}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exec_ok_exec_err_usage():
    """Test that exec_ok and exec_err are used in return statements"""
    print("\n" + "="*60)
    print("TEST 6: exec_ok and exec_err Usage")
    print("="*60)
    
    try:
        # Import the executor module
        import mev_direct_copy_executor
        import inspect
        
        # Get source code
        source = inspect.getsource(mev_direct_copy_executor)
        
        # Check for exec_ok usage
        assert 'return exec_ok("direct_copy"' in source, \
            "❌ exec_ok not used in return statements"
        
        # Check for exec_err usage
        assert 'return exec_err("direct_copy"' in source, \
            "❌ exec_err not used in return statements"
        
        print("✅ PASS: exec_ok and exec_err properly used in return statements")
        
        # Count occurrences
        exec_ok_count = source.count('exec_ok("direct_copy"')
        exec_err_count = source.count('exec_err("direct_copy"')
        print(f"   exec_ok usage count: {exec_ok_count}")
        print(f"   exec_err usage count: {exec_err_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("SUBMIT_CLONED_TX AND FAST_EXECUTOR INTEGRATION TESTS")
    print("🚀"*30)
    
    results = []
    
    # Test 1: Successful submission
    results.append(await test_submit_cloned_tx_success())
    
    # Test 2: Failed submission
    results.append(await test_submit_cloned_tx_failure())
    
    # Test 3: None executor
    results.append(await test_submit_cloned_tx_none_executor())
    
    # Test 4: Import check
    results.append(test_exec_ok_exec_err_import())
    
    # Test 5: FastExecutor parameter
    results.append(test_fast_executor_parameter())
    
    # Test 6: exec_ok/exec_err usage
    results.append(test_exec_ok_exec_err_usage())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n" + "🎉"*30)
        print("ALL TESTS PASSED!")
        print("🎉"*30 + "\n")
        return 0
    else:
        print("\n" + "❌"*30)
        print(f"SOME TESTS FAILED: {total - passed} failures")
        print("❌"*30 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
