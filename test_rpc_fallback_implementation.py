#!/usr/bin/env python3
"""
Test script to validate RPC fallback implementation requirements.

Requirements from problem statement:
1. _submit_via_rpc returns signature from resp['result']
2. _submit_via_rpc has robust error logs
3. send_and_confirm falls back to RPC on Jito failure
4. send_and_confirm logs "[EXECUTOR] Falling back to RPC submission"
5. send_and_confirm logs "[EXECUTOR] submission failed (Jito and RPC)" on total failure
6. send_and_confirm logs "[CONFIRM][FINAL] sig=... status=..." on success
"""

import sys
import re


def test_submit_via_rpc_signature_parsing():
    """Test that _submit_via_rpc parses signature from result field"""
    print("=" * 80)
    print("TEST 1: _submit_via_rpc Signature Parsing from result")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'async def _submit_via_rpc\(self, vtx\) -> str \| None:', 
         "✅ _submit_via_rpc method exists with correct signature"),
        (r'sig = \(data or \{\}\)\.get\("result"\)', 
         "✅ Parses signature from data['result']"),
        (r'if sig:\s+self\.logger\.info\(f"\[SUBMIT_RPC\] sig=\{sig\}"\)\s+return sig', 
         "✅ Returns signature and logs [SUBMIT_RPC] sig=..."),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_submit_via_rpc_error_logging():
    """Test that _submit_via_rpc has robust error logging"""
    print("=" * 80)
    print("TEST 2: _submit_via_rpc Robust Error Logging")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'self\.logger\.error\(f"\[SUBMIT_RPC\] no result: \{data\}"\)', 
         "✅ Logs error when no result field present"),
        (r'except Exception as e:\s+self\.logger\.error\(f"\[SUBMIT_RPC\] error: \{e\}"\)\s+return None', 
         "✅ Logs exception and returns None on error"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_send_and_confirm_jito_rpc_fallback():
    """Test that send_and_confirm tries Jito first, then RPC"""
    print("=" * 80)
    print("TEST 3: send_and_confirm Jito → RPC Fallback Order")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    # Check for key patterns
    patterns = [
        (r'sig = await self\._submit_via_jito\(vtx\)', 
         "✅ Tries Jito submission first"),
        (r'if not sig:.*self\.logger\.warning\("\[EXECUTOR\] Falling back to RPC submission"\).*sig = await self\._submit_via_rpc\(vtx\)', 
         "✅ Falls back to RPC with warning log on Jito failure"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    # Also check order: Jito before RPC
    jito_match = re.search(r'sig = await self\._submit_via_jito\(vtx\)', content)
    rpc_match = re.search(r'sig = await self\._submit_via_rpc\(vtx\)', content)
    
    if jito_match and rpc_match and jito_match.start() < rpc_match.start():
        print(f"  ✅ Jito call comes before RPC call in execution order")
        passed += 1
    else:
        print(f"  ❌ Jito call comes before RPC call in execution order")
    
    print(f"\n  Result: {passed}/{len(patterns) + 1} checks passed\n")
    return passed == len(patterns) + 1


def test_send_and_confirm_failure_logging():
    """Test that send_and_confirm logs total failure"""
    print("=" * 80)
    print("TEST 4: send_and_confirm Total Failure Logging")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'if not sig:\s+self\.logger\.error\("\[EXECUTOR\] submission failed \(Jito and RPC\)"\)\s+return None', 
         "✅ Logs error when both Jito and RPC fail"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_send_and_confirm_success_logging():
    """Test that send_and_confirm logs final confirmation status"""
    print("=" * 80)
    print("TEST 5: send_and_confirm Final Confirmation Logging")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'status = await self\._confirm_with_retries\(sig\)', 
         "✅ Calls _confirm_with_retries on successful submission"),
        (r'self\.logger\.info\(f"\[CONFIRM\]\[FINAL\] sig=\{sig\} status=\{status\}"\)', 
         "✅ Logs [CONFIRM][FINAL] with sig and status"),
        (r'return sig', 
         "✅ Returns signature after confirmation"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_json_rpc_payload_format():
    """Test that _submit_via_rpc uses correct JSON-RPC payload format"""
    print("=" * 80)
    print("TEST 6: _submit_via_rpc JSON-RPC Payload Format")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'payload = \{[^}]*"jsonrpc": "2\.0"', 
         "✅ Uses JSON-RPC 2.0 format"),
        (r'"method": "sendTransaction"', 
         "✅ Uses sendTransaction method"),
        (r'base64\.b64encode\(raw\)\.decode\(\)', 
         "✅ Encodes transaction as base64"),
        (r'"encoding": "base64"', 
         "✅ Specifies base64 encoding in params"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_httpx_client_usage():
    """Test that _submit_via_rpc uses httpx.AsyncClient"""
    print("=" * 80)
    print("TEST 7: _submit_via_rpc Uses httpx.AsyncClient")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'async with httpx\.AsyncClient\(timeout=15\.0\) as client:', 
         "✅ Uses httpx.AsyncClient with 15 second timeout"),
        (r'r = await client\.post\(self\._rpc_url, json=payload\)', 
         "✅ POSTs to RPC URL with JSON payload"),
        (r'r\.raise_for_status\(\)', 
         "✅ Raises on HTTP error status"),
        (r'data = r\.json\(\)', 
         "✅ Parses response as JSON"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("RPC FALLBACK IMPLEMENTATION VALIDATION TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_submit_via_rpc_signature_parsing(),
        test_submit_via_rpc_error_logging(),
        test_send_and_confirm_jito_rpc_fallback(),
        test_send_and_confirm_failure_logging(),
        test_send_and_confirm_success_logging(),
        test_json_rpc_payload_format(),
        test_httpx_client_usage(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL RPC FALLBACK REQUIREMENTS MET!")
        print("\n  Implementation summary:")
        print("  ✅ _submit_via_rpc parses signature from JSON-RPC 'result' field")
        print("  ✅ Robust error logging in _submit_via_rpc")
        print("  ✅ send_and_confirm tries Jito first, then RPC fallback")
        print("  ✅ Logs '[EXECUTOR] Falling back to RPC submission' on Jito failure")
        print("  ✅ Logs '[EXECUTOR] submission failed (Jito and RPC)' on total failure")
        print("  ✅ Logs '[CONFIRM][FINAL] sig=... status=...' on success")
        print("  ✅ Uses httpx.AsyncClient with 15s timeout")
        print("  ✅ Correct JSON-RPC 2.0 payload format")
        print()
        return 0
    else:
        print("\n  ❌ SOME REQUIREMENTS NOT MET")
        print("  ❌ Review implementation against problem statement")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
