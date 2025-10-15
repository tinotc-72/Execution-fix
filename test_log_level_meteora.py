#!/usr/bin/env python3
"""
Test to validate that MeteoraFastExecutor fallback message uses INFO log level.

This test verifies the problem statement requirement:
"Change the log level for '⚠️ MeteoraFastExecutor not available – using fallback.' 
from WARNING to INFO."
"""

import re


def test_meteora_fast_executor_log_level():
    """Verify MeteoraFastExecutor fallback uses INFO level"""
    print("\n" + "="*80)
    print("TEST: MeteoraFastExecutor Fallback Log Level")
    print("="*80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Find the _initialize_fast_executor method
    method_match = re.search(
        r'def _initialize_fast_executor\(self\):.*?(?=\n    def |\n    async def |\Z)',
        content,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ Could not find _initialize_fast_executor method")
        return False
    
    method_code = method_match.group(0)
    
    # Check that logger.info is used (not logger.warning)
    if 'logger.info("⚠️ MeteoraFastExecutor not available' in method_code:
        print("  ✅ Uses logger.info for MeteoraFastExecutor fallback")
    else:
        print("  ❌ Does not use logger.info for MeteoraFastExecutor fallback")
        return False
    
    # Ensure logger.warning is NOT used for this message
    if 'logger.warning("⚠️ MeteoraFastExecutor not available' in method_code:
        print("  ❌ Still uses logger.warning (should be logger.info)")
        return False
    else:
        print("  ✅ Does not use logger.warning (correctly changed)")
    
    # Verify emoji is preserved
    if '⚠️' in method_code and 'MeteoraFastExecutor not available' in method_code:
        print("  ✅ Emoji logging maintained (⚠️)")
    else:
        print("  ❌ Emoji logging not found")
        return False
    
    print("\n  Result: All checks passed ✅\n")
    return True


def main():
    """Run the validation test"""
    print("\nValidating MeteoraFastExecutor log level change...")
    
    if test_meteora_fast_executor_log_level():
        print("="*80)
        print("✅ TEST PASSED: Log level correctly changed to INFO")
        print("="*80)
        return 0
    else:
        print("="*80)
        print("❌ TEST FAILED: Log level not correctly changed")
        print("="*80)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
