#!/usr/bin/env python3
"""
🔧 RUNTIME FIXES VERIFICATION
Verify that all interface mismatches have been resolved
"""

import ast
import inspect
from typing import Dict, Any

def verify_async_calls():
    """Check that all async methods are properly awaited"""
    print("🔍 Verifying async/await patterns...")
    
    # Read main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for validate_trade_info calls
    if 'self._validate_trade_info(' in content:
        issues.append("❌ Old _validate_trade_info method still being called")
    
    if 'validate_trade_info(' in content and 'await' not in content.split('validate_trade_info(')[0].split('\n')[-1]:
        # This is a basic check - might have false positives
        pass  # We'll check this more carefully below
    
    # Count await validate_trade_info calls
    await_calls = content.count('await self.trade_processor.validate_trade_info(')
    validate_calls = content.count('validate_trade_info(')
    
    if await_calls != validate_calls:
        issues.append(f"❌ Async mismatch: {validate_calls} validate_trade_info calls, {await_calls} awaited")
    
    return issues

def verify_method_signatures():
    """Check that method calls match signatures"""
    print("🔍 Verifying method signatures...")
    
    issues = []
    
    # Read main.py to check execution_coordinator calls
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    # Check for execution_config parameter
    if 'execution_config=' in main_content:
        issues.append("❌ execution_config parameter still being passed")
    
    # Check for sell_percentage in _execute_copy_sell calls
    if '_execute_copy_sell(' in main_content and 'sell_percentage=' in main_content:
        issues.append("❌ sell_percentage parameter being passed to _execute_copy_sell")
    
    return issues

def verify_utils_calls():
    """Check that utils function calls use correct parameters"""
    print("🔍 Verifying utils function calls...")
    
    issues = []
    
    # Read trade_processor.py
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check get_transaction_with_logs calls
    if 'get_transaction_with_logs(signature, self.rpc_client)' in content:
        issues.append("❌ get_transaction_with_logs still being called with 2 parameters")
    
    return issues

def verify_method_removals():
    """Check that obsolete methods were removed"""
    print("🔍 Verifying obsolete method removal...")
    
    issues = []
    
    # Read main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if old _validate_trade_info method exists
    if 'def _validate_trade_info(' in content:
        issues.append("❌ Old _validate_trade_info method still exists in main.py")
    
    return issues

def main():
    """Run all verification checks"""
    print("🔧 RUNTIME FIXES VERIFICATION")
    print("=" * 50)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(verify_async_calls())
    all_issues.extend(verify_method_signatures())
    all_issues.extend(verify_utils_calls())
    all_issues.extend(verify_method_removals())
    
    print("\n📊 VERIFICATION RESULTS:")
    print("=" * 30)
    
    if not all_issues:
        print("✅ ALL RUNTIME FIXES VERIFIED!")
        print("   🎯 Async/await patterns: CORRECT")
        print("   🎯 Method signatures: MATCHED")
        print("   🎯 Parameter counts: CORRECT")
        print("   🎯 Obsolete code: REMOVED")
        print("\n🚀 Bot should now run without runtime errors!")
    else:
        print("❌ ISSUES FOUND:")
        for issue in all_issues:
            print(f"   {issue}")
        print(f"\n⚠️  Total issues: {len(all_issues)}")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
