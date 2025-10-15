#!/usr/bin/env python3
"""
Test to validate that infer_missing_fields calls properly reassign trade_info.

This test ensures the pattern described in the problem statement is followed:
  trade_info = infer_missing_fields(trade_info, rpc_client)  # ensure reassignment

The infer_missing_fields method both mutates the dict AND returns it.
Best practice is to always reassign to ensure consistency.
"""

import re

def test_inference_reassignment_pattern():
    """Verify that all calls to infer_missing_fields properly reassign the result."""
    
    print("=" * 80)
    print("Testing infer_missing_fields Reassignment Pattern")
    print("=" * 80)
    
    # Read main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find all lines with infer_missing_fields
    lines_with_infer = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'infer_missing_fields(' in line and not line.strip().startswith('#'):
            lines_with_infer.append((i, line.strip()))
    
    print(f"\nFound {len(lines_with_infer)} call(s) to infer_missing_fields")
    
    print(f"\n" + "=" * 80)
    print("Detailed Analysis:")
    print("=" * 80)
    
    all_correct = True
    for line_num, line in lines_with_infer:
        # Check if line has assignment pattern: var = ...infer_missing_fields(...)
        if '=' in line.split('infer_missing_fields')[0]:
            var_name = line.split('=')[0].strip()
            print(f"Line {line_num}: ✅ '{var_name} = ...' (CORRECT)")
        else:
            print(f"Line {line_num}: ❌ '{line}' (MISSING REASSIGNMENT)")
            all_correct = False
    
    print(f"\n" + "=" * 80)
    if all_correct:
        print("✅ SUCCESS: All calls properly reassign trade_info")
        print("The pattern ensures mutated dict is used after inference.")
    else:
        print("❌ FAILURE: Some calls missing reassignment")
    print("=" * 80)
    
    return all_correct

if __name__ == "__main__":
    success = test_inference_reassignment_pattern()
    exit(0 if success else 1)
