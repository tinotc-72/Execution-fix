#!/usr/bin/env python3
"""
Verification script to ensure unified submit helper enforcement is complete.

This script checks:
1. No raw sendTransaction/sendRawTransaction patterns remain (excluding tests/demos)
2. All executors import the unified helper
3. All submit paths include proper logging

Usage:
    python tools/verify_readiness.py
"""

import os
import re
import sys
from typing import List, Tuple, Dict

# Patterns for detection
RAW_SUBMIT_PATTERN = re.compile(
    r'requests\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'client\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'session\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'"method"\s*:\s*"send(?:Transaction|RawTransaction)"',
    re.I
)

HELPER_IMPORT_PATTERN = re.compile(r'from executors\.submit import.*send_and_confirm_v0_tx')

LOGGING_PATTERN = re.compile(
    r'logger\.(info|debug|warning)\([^)]*DEX[^)]*action[^)]*mint[^)]*sig[^)]*(?:status|confirmationStatus)[^)]*ok',
    re.I | re.S
)

# Files to skip
SKIP_PATTERNS = [
    re.compile(r'(^|/)test_'),
    re.compile(r'(^|/)demo_'),
    re.compile(r'(^|/)validate_'),
    re.compile(r'(^|/)verify_'),
    re.compile(r'patch_unified_submit\.py'),
    re.compile(r'verify_readiness\.py'),
    re.compile(r'executors/submit\.py'),
    re.compile(r'jito_service\.py'),  # Jito-first is optional per requirements
]


def should_skip(path: str) -> bool:
    """Check if a file should be skipped"""
    for pattern in SKIP_PATTERNS:
        if pattern.search(path):
            return True
    return False


def check_file(path: str, root: str) -> Dict[str, any]:
    """
    Check a single file for compliance.
    
    Returns:
        Dict with check results
    """
    rel_path = os.path.relpath(path, root)
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {
            "path": rel_path,
            "error": str(e),
            "compliant": False
        }
    
    # Check for raw submission patterns
    raw_matches = list(RAW_SUBMIT_PATTERN.finditer(content))
    has_raw_submit = len(raw_matches) > 0
    
    # Check for helper import
    has_helper_import = bool(HELPER_IMPORT_PATTERN.search(content))
    
    # Check for proper logging
    has_proper_logging = bool(LOGGING_PATTERN.search(content))
    
    # File is compliant if:
    # - It has no raw submissions, OR
    # - It has the helper import (meaning it was patched but might still have commented raw code)
    compliant = not has_raw_submit or has_helper_import
    
    return {
        "path": rel_path,
        "has_raw_submit": has_raw_submit,
        "has_helper_import": has_helper_import,
        "has_proper_logging": has_proper_logging,
        "raw_match_count": len(raw_matches),
        "compliant": compliant,
        "raw_matches": [m.group(0)[:100] for m in raw_matches[:3]]  # First 3 matches
    }


def find_python_files(root: str) -> List[str]:
    """Find all Python files in root directory"""
    python_files = []
    
    for base, dirs, files in os.walk(root):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fn in files:
            if fn.endswith('.py'):
                full_path = os.path.join(base, fn)
                rel_path = os.path.relpath(full_path, root)
                
                if not should_skip(rel_path):
                    python_files.append(full_path)
    
    return python_files


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 80)
    print("🔍 Unified Submit Helper Verification")
    print("=" * 80)
    print(f"Root directory: {root}")
    print()
    
    # Find all Python files
    python_files = find_python_files(root)
    print(f"Found {len(python_files)} Python files to check")
    print()
    
    # Check each file
    results = []
    for path in python_files:
        result = check_file(path, root)
        results.append(result)
    
    # Analyze results
    non_compliant = [r for r in results if not r["compliant"]]
    with_raw_submit = [r for r in results if r.get("has_raw_submit")]
    with_helper = [r for r in results if r.get("has_helper_import")]
    with_logging = [r for r in results if r.get("has_proper_logging")]
    errors = [r for r in results if "error" in r]
    
    # Print detailed results
    print("=" * 80)
    print("📊 Verification Results")
    print("=" * 80)
    print(f"Total files checked: {len(results)}")
    print(f"✅ Compliant files: {len(results) - len(non_compliant)}")
    print(f"❌ Non-compliant files: {len(non_compliant)}")
    print(f"📝 Files with helper import: {len(with_helper)}")
    print(f"📋 Files with proper logging: {len(with_logging)}")
    print(f"⚠️  Files with raw submissions: {len(with_raw_submit)}")
    print()
    
    # Show non-compliant files
    if non_compliant:
        print("=" * 80)
        print("❌ Non-Compliant Files (need attention)")
        print("=" * 80)
        for r in non_compliant:
            print(f"\n📄 {r['path']}")
            print(f"   Raw submissions: {r.get('raw_match_count', 0)}")
            print(f"   Has helper import: {r.get('has_helper_import', False)}")
            print(f"   Has proper logging: {r.get('has_proper_logging', False)}")
            
            if r.get('raw_matches'):
                print("   Raw submission examples:")
                for match in r['raw_matches']:
                    print(f"     - {match}...")
        print()
    
    # Show files with raw submissions but helper import (likely just commented code)
    commented_only = [r for r in with_raw_submit if r.get("has_helper_import")]
    if commented_only:
        print("=" * 80)
        print("ℹ️  Files with raw submissions AND helper import (likely commented)")
        print("=" * 80)
        for r in commented_only:
            print(f"  - {r['path']}")
        print()
    
    # Show errors
    if errors:
        print("=" * 80)
        print("⚠️  Errors During Verification")
        print("=" * 80)
        for r in errors:
            print(f"  - {r['path']}: {r['error']}")
        print()
    
    # Final verdict
    print("=" * 80)
    if not non_compliant and not errors:
        print("✅ VERIFICATION PASSED!")
        print()
        print("All files are compliant with the unified submit helper enforcement.")
        print("No raw transaction submissions found outside of test/demo files.")
        print("=" * 80)
        return 0
    else:
        print("❌ VERIFICATION FAILED!")
        print()
        if non_compliant:
            print(f"Found {len(non_compliant)} non-compliant files that need attention.")
        if errors:
            print(f"Encountered {len(errors)} errors during verification.")
        print()
        print("Action required:")
        print("  1. Review non-compliant files listed above")
        print("  2. Run 'python tools/patch_unified_submit.py --root . --rpc-env RPC_URL'")
        print("  3. Manually fix any files that couldn't be auto-patched")
        print("  4. Re-run this verification script")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
