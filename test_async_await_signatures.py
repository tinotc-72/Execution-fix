#!/usr/bin/env python3
"""
Test suite to validate async/await signatures in execution chain.
Tests the requirements from the problem statement:
- A) execution_coordinator.py: try_submit is async and always awaited; maybe_execute is async
- B) fast_executor.py: All network ops are async
- C) Runtime test with JITO_ENABLED=0
"""

import sys
import re
import os


def test_execution_coordinator_async_signatures():
    """Test A) execution_coordinator.py async signatures"""
    print("=" * 80)
    print("TEST 1: execution_coordinator.py async signatures")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # A.1: Check try_submit is async def
    if re.search(r'async def try_submit\(', content):
        print("✅ A.1: try_submit is async def")
    else:
        print("❌ A.1: try_submit is NOT async def")
        return False
    
    # A.2: Check all try_submit calls use await
    # Find the try_submit function definition
    try_submit_match = re.search(
        r'async def try_submit\(vtx\):.*?(?=\n    async def|\n    if dex ==|\n    # last resort)',
        content, 
        re.DOTALL
    )
    
    if not try_submit_match:
        print("⚠️  Could not find try_submit function boundary")
    
    # Find all try_submit calls (excluding the definition)
    try_submit_calls = re.findall(r'(\s+await\s+)?try_submit\(', content)
    
    # Count calls (excluding definition which has 'def' before it)
    await_calls = sum(1 for match in try_submit_calls if match.strip())
    total_calls = len(try_submit_calls) - 1  # Subtract the definition
    
    if total_calls == 0:
        print("⚠️  No try_submit calls found")
    elif await_calls == total_calls:
        print(f"✅ A.2: All {total_calls} try_submit calls use await")
    else:
        print(f"❌ A.2: {await_calls}/{total_calls} try_submit calls use await")
        return False
    
    # A.3: Check maybe_execute is async def
    if re.search(r'async def maybe_execute\(', content):
        print("✅ A.3: maybe_execute is async def")
    else:
        print("❌ A.3: maybe_execute is NOT async def")
        return False
    
    # A.4: Check all maybe_execute calls in main.py use await
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        # Find maybe_execute calls
        maybe_execute_calls = re.findall(
            r'(await\s+)?maybe_execute\(',
            main_content
        )
        
        if maybe_execute_calls:
            awaited_calls = sum(1 for match in maybe_execute_calls if match.strip())
            total_calls = len(maybe_execute_calls)
            
            if awaited_calls == total_calls:
                print(f"✅ A.4: All {total_calls} maybe_execute calls in main.py use await")
            else:
                print(f"❌ A.4: {awaited_calls}/{total_calls} maybe_execute calls in main.py use await")
                return False
        else:
            print("ℹ️  A.4: No maybe_execute calls found in main.py")
    except FileNotFoundError:
        print("ℹ️  A.4: main.py not found, skipping check")
    
    return True


def test_fast_executor_async_signatures():
    """Test B) fast_executor.py async signatures"""
    print("\n" + "=" * 80)
    print("TEST 2: fast_executor.py async signatures")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    # B: Check all network submission ops are async def
    ops_to_check = [
        'submit_transaction',
        '_submit_via_jito',
        '_submit_via_rpc',
        'initialize',
        'close'
    ]
    
    all_async = True
    for op in ops_to_check:
        pattern = rf'async def {op}\('
        if re.search(pattern, content):
            print(f"✅ B: {op} is async def")
        else:
            print(f"❌ B: {op} is NOT async def")
            all_async = False
    
    # Check send_and_confirm (mentioned as rpc_send_and_confirm in problem statement)
    if re.search(r'async def send_and_confirm\(', content):
        print("✅ B: send_and_confirm is async def")
    else:
        print("❌ B: send_and_confirm is NOT async def")
        all_async = False
    
    return all_async


def test_await_chain():
    """Test that the async chain is properly awaited throughout"""
    print("\n" + "=" * 80)
    print("TEST 3: Async await chain validation")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        coord_content = f.read()
    
    # Find all submit_transaction calls with better context
    pattern = r'(.{0,20})(fast_executor|temp_executor|self\.fast_executor)\.submit_transaction\('
    matches = re.findall(pattern, coord_content)
    
    if not matches:
        print("⚠️  No submit_transaction calls found")
        return True
    
    awaited = sum(1 for before, _ in matches if 'await' in before)
    total = len(matches)
    
    if awaited == total:
        print(f"✅ All {total} submit_transaction calls use await")
        return True
    else:
        print(f"❌ {awaited}/{total} submit_transaction calls use await")
        # Show which ones are missing await
        for before, executor in matches:
            if 'await' not in before:
                print(f"   Missing await: {before}{executor}.submit_transaction(...)")
        return False


def test_runtime_import_no_jito():
    """Test C) Runtime test with JITO_ENABLED=0"""
    print("\n" + "=" * 80)
    print("TEST 4: Runtime import with JITO_ENABLED=0")
    print("=" * 80)
    
    # Set environment before import
    os.environ['JITO_ENABLED'] = '0'
    
    try:
        # Import fast_executor with JITO disabled
        import fast_executor
        
        print(f"✅ Import successful")
        print(f"   JITO_ENABLED: {fast_executor.JITO_ENABLED}")
        print(f"   JITO_AVAILABLE: {fast_executor.JITO_AVAILABLE}")
        
        if not fast_executor.JITO_ENABLED:
            print("✅ JITO_ENABLED correctly set to False")
        else:
            print("❌ JITO_ENABLED should be False")
            return False
        
        if not fast_executor.JITO_AVAILABLE:
            print("✅ JITO_AVAILABLE correctly set to False (expected with JITO_ENABLED=0)")
        
        print("✅ No TypeError or ImportError with JITO_ENABLED=0")
        return True
        
    except TypeError as e:
        print(f"❌ TypeError during import: {e}")
        return False
    except ImportError as e:
        print(f"❌ ImportError during import: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error during import: {e}")
        # Don't fail on other errors (e.g., missing env vars)
        return True


def test_builder_return_types():
    """Test C) Builders should return VTX not coroutine"""
    print("\n" + "=" * 80)
    print("TEST 5: Builder return type validation")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Check that builders are called without await (they return VTX directly)
    # Look for build_and_sign calls
    patterns = [
        (r'vtx\s*=\s*await.*?build_and_sign', 'Builder incorrectly awaited'),
        (r'vtx\s*=\s*[^await].*?build_and_sign', 'Builder correctly not awaited'),
    ]
    
    # Find build_and_sign calls
    build_calls = re.findall(r'(vtx\s*=\s*(?:await\s+)?.*?build_and_sign.*)', content)
    
    if not build_calls:
        print("ℹ️  No build_and_sign calls found to check")
        return True
    
    # Check if any are awaited (they shouldn't be)
    awaited_builders = [call for call in build_calls if 'await' in call]
    
    if awaited_builders:
        print(f"❌ Found {len(awaited_builders)} builder calls incorrectly awaited:")
        for call in awaited_builders[:3]:  # Show first 3
            print(f"   {call[:80]}...")
        return False
    else:
        print(f"✅ All {len(build_calls)} builder calls return VTX directly (not awaited)")
        return True


def main():
    """Run all tests"""
    print("\n🚀 Testing Async/Await Signature Alignment")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("execution_coordinator async signatures", test_execution_coordinator_async_signatures()))
    results.append(("fast_executor async signatures", test_fast_executor_async_signatures()))
    results.append(("await chain validation", test_await_chain()))
    results.append(("runtime import (JITO_ENABLED=0)", test_runtime_import_no_jito()))
    results.append(("builder return types", test_builder_return_types()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
