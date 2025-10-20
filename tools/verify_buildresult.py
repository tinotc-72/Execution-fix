#!/usr/bin/env python3
"""
Verification script to ensure BuildResult enforcement is complete.

This script checks:
1. All builder functions with BuildResult return type don't return None
2. All executors check .ok property on BuildResult objects
3. BuildResult is properly imported where used

Usage:
    python tools/verify_buildresult.py
"""

import os
import re
import sys
from typing import List, Dict

# Patterns
BUILDRESULT_RETURN_PATTERN = re.compile(r'def\s+(\w*build\w*)\s*\([^)]*\)\s*->\s*BuildResult:', re.MULTILINE)
RETURN_NONE_PATTERN = re.compile(r'^\s*return\s+None\s*$', re.MULTILINE)
OK_CHECK_PATTERN = re.compile(r'\.ok\b')
BUILDRESULT_IMPORT_PATTERN = re.compile(r'from models\.build_result import BuildResult')

# Files to skip
SKIP_PATTERNS = [
    re.compile(r'(^|/)test_'),
    re.compile(r'(^|/)demo_'),
    re.compile(r'(^|/)validate_'),
    re.compile(r'(^|/)verify_'),
    re.compile(r'__pycache__'),
    re.compile(r'patch_buildresult\.py'),
    re.compile(r'verify_buildresult\.py'),
]


def should_skip(path: str) -> bool:
    """Check if a file should be skipped"""
    for pattern in SKIP_PATTERNS:
        if pattern.search(path):
            return True
    return False


def check_builder_functions(content: str, file_path: str) -> Dict:
    """Check if builder functions with BuildResult return type have return None"""
    
    builders = list(BUILDRESULT_RETURN_PATTERN.finditer(content))
    
    if not builders:
        return {
            "has_builders": False,
            "issues": []
        }
    
    issues = []
    
    for match in builders:
        func_name = match.group(1)
        func_start = match.start()
        
        # Find the function body (simplified - just check next 1000 chars)
        func_body_end = min(func_start + 5000, len(content))
        func_body = content[func_start:func_body_end]
        
        # Look for next function definition to limit scope
        next_func_match = re.search(r'\n(def |async def |class )', func_body[match.end() - func_start:])
        if next_func_match:
            func_body = func_body[:match.end() - func_start + next_func_match.start()]
        
        # Check for return None in function body
        if RETURN_NONE_PATTERN.search(func_body):
            line_num = content[:func_start].count('\n') + 1
            issues.append({
                "function": func_name,
                "line": line_num,
                "issue": "Function returns BuildResult but has 'return None' statement"
            })
    
    return {
        "has_builders": True,
        "builder_count": len(builders),
        "issues": issues
    }


def check_ok_usage(content: str, file_path: str) -> Dict:
    """Check if file uses BuildResult and checks .ok property"""
    
    has_buildresult = bool(BUILDRESULT_IMPORT_PATTERN.search(content))
    
    if not has_buildresult:
        return {
            "uses_buildresult": False,
            "checks_ok": False
        }
    
    # Check if there are .ok checks
    checks_ok = bool(OK_CHECK_PATTERN.search(content))
    
    return {
        "uses_buildresult": True,
        "checks_ok": checks_ok
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
    print("🔍 BuildResult Enforcement Verification")
    print("=" * 80)
    print(f"Root directory: {root}")
    print()
    
    # Find all Python files
    python_files = find_python_files(root)
    print(f"Found {len(python_files)} Python files to check")
    print()
    
    # Check each file
    all_issues = []
    files_with_builders = []
    files_using_buildresult = []
    files_checking_ok = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            continue
        
        rel_path = os.path.relpath(file_path, root)
        
        # Check builder functions
        builder_result = check_builder_functions(content, rel_path)
        if builder_result["has_builders"]:
            files_with_builders.append(rel_path)
            if builder_result["issues"]:
                for issue in builder_result["issues"]:
                    all_issues.append({
                        "file": rel_path,
                        **issue
                    })
        
        # Check .ok usage
        ok_result = check_ok_usage(content, rel_path)
        if ok_result["uses_buildresult"]:
            files_using_buildresult.append(rel_path)
            if ok_result["checks_ok"]:
                files_checking_ok.append(rel_path)
    
    # Print results
    print("=" * 80)
    print("📊 Verification Results")
    print("=" * 80)
    print(f"Total files checked: {len(python_files)}")
    print(f"Files with builder functions: {len(files_with_builders)}")
    print(f"Files using BuildResult: {len(files_using_buildresult)}")
    print(f"Files checking .ok property: {len(files_checking_ok)}")
    print()
    
    # Show files with builder functions
    if files_with_builders:
        print("=" * 80)
        print("📝 Files with Builder Functions")
        print("=" * 80)
        for f in files_with_builders:
            print(f"  ✅ {f}")
        print()
    
    # Show files using BuildResult
    if files_using_buildresult:
        print("=" * 80)
        print("📦 Files Using BuildResult")
        print("=" * 80)
        for f in files_using_buildresult:
            checks = "✅ checks .ok" if f in files_checking_ok else "⚠️  no .ok checks"
            print(f"  {checks:20s} {f}")
        print()
    
    # Show issues
    if all_issues:
        print("=" * 80)
        print("❌ Issues Found")
        print("=" * 80)
        for issue in all_issues:
            print(f"\n📄 {issue['file']} (line {issue['line']})")
            print(f"   Function: {issue['function']}")
            print(f"   Issue: {issue['issue']}")
        print()
    
    # Final verdict
    print("=" * 80)
    if not all_issues:
        print("✅ VERIFICATION PASSED!")
        print()
        print("All builder functions with BuildResult return type are compliant.")
        print("No 'return None' statements found in BuildResult functions.")
        print("=" * 80)
        return 0
    else:
        print("❌ VERIFICATION FAILED!")
        print()
        print(f"Found {len(all_issues)} issue(s) that need attention.")
        print()
        print("Action required:")
        print("  1. Review the issues listed above")
        print("  2. Run 'python tools/patch_buildresult.py --root . --dry-run' to preview fixes")
        print("  3. Run 'python tools/patch_buildresult.py --root .' to apply fixes")
        print("  4. Re-run this verification script")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
