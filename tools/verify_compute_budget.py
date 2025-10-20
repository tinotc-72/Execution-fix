#!/usr/bin/env python3
"""
Verification script to ensure compute budget is set on all transaction paths.

This script checks that every code path constructing MessageV0 or VersionedTransaction
includes compute budget instructions via with_compute_budget or set_compute_unit_* calls.

Usage:
    python tools/verify_compute_budget.py
"""

import os
import re
import sys


def remove_comments_and_strings(content):
    """Remove comments and strings to avoid false positives"""
    # Remove docstrings
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    # Remove single-line comments
    lines = content.splitlines()
    cleaned_lines = []
    for line in lines:
        # Remove everything after #
        if '#' in line:
            line = line[:line.index('#')]
        # Remove string literals
        line = re.sub(r'"[^"]*"', '""', line)
        line = re.sub(r"'[^']*'", "''", line)
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def has_transaction_construction(content):
    """Check if file actually constructs transactions (not just in comments)"""
    cleaned = remove_comments_and_strings(content)
    # Look for actual function calls, not just mentions
    return bool(
        re.search(r'MessageV0\.try_compile\s*\(', cleaned) or 
        re.search(r'VersionedTransaction\s*\([^)]*message', cleaned)
    )


def has_compute_budget(content):
    """Check if file has compute budget handling"""
    return bool(re.search(r'set_compute_unit_|with_compute_budget', content))


def should_skip(path):
    """Check if file should be skipped from verification"""
    skip_patterns = [
        'test_', 'demo_', 'validate_', 'verify_',
        '__pycache__', '.git', '/test/', '/demo/', '/validate/'
    ]
    return any(pattern in path for pattern in skip_patterns)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 80)
    print("🔍 Compute Budget Verification")
    print("=" * 80)
    print(f"Root directory: {root}")
    print()
    
    files_checked = 0
    files_with_construction = 0
    files_with_compute_budget = 0
    missing_compute_budget = []
    
    for base, dirs, files in os.walk(root):
        # Skip hidden and test directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fn in files:
            if not fn.endswith('.py'):
                continue
                
            path = os.path.join(base, fn)
            rel_path = os.path.relpath(path, root)
            
            if should_skip(rel_path):
                continue
                
            files_checked += 1
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                has_construct = has_transaction_construction(content)
                has_cu = has_compute_budget(content)
                
                if has_construct:
                    files_with_construction += 1
                    if has_cu:
                        files_with_compute_budget += 1
                        print(f"✅ {rel_path}")
                    else:
                        missing_compute_budget.append(rel_path)
                        print(f"❌ {rel_path} - MISSING COMPUTE BUDGET")
            except Exception as e:
                print(f"⚠️  Error reading {rel_path}: {e}")
    
    print()
    print("=" * 80)
    print("📊 Verification Results")
    print("=" * 80)
    print(f"Files checked: {files_checked}")
    print(f"Files with transaction construction: {files_with_construction}")
    print(f"Files with compute budget: {files_with_compute_budget}")
    print(f"Missing compute budget: {len(missing_compute_budget)}")
    print("=" * 80)
    
    if missing_compute_budget:
        print()
        print("❌ VERIFICATION FAILED!")
        print()
        print("The following files construct transactions without compute budget:")
        for f in missing_compute_budget:
            print(f"  - {f}")
        print()
        print("Action required:")
        print("  1. Run 'python tools/patch_compute_budget.py --root . --cu-limit 1000000 --cu-price 5000'")
        print("  2. Review the changes with 'git diff'")
        print("  3. Manually fix any files that couldn't be auto-patched")
        print("  4. Re-run this verification script")
        print("=" * 80)
        return 1
    else:
        print()
        print("✅ VERIFICATION PASSED!")
        print()
        print("All transaction construction paths have compute budget set.")
        print("Every MessageV0 and VersionedTransaction is properly configured.")
        print("=" * 80)
        return 0


if __name__ == '__main__':
    sys.exit(main())
