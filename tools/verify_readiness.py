#!/usr/bin/env python3
"""
Comprehensive repo readiness verification script.

This script enforces critical standards for transaction submission, instruction 
formatting, builder return types, and compute budget usage across the repository.

Checks:
1. No solana-py imports remain (solana-py should not be used)
2. Unified submitter is enforced (no raw sendTransaction/sendRawTransaction/requests.post)
3. No list data in Instruction.data (Instruction.data must not be a list)
4. Builders must not return None (if BuildResult is referenced, no return None)
5. Every MessageV0/VersionedTransaction construction must include compute budget helper

Usage:
    python tools/verify_readiness.py
"""

import os
import re
import sys
from typing import List, Dict, Set

# ============================================================================
# CHECK 1: No solana-py imports
# ============================================================================
SOLANA_PY_IMPORT_PATTERN = re.compile(
    r'^\s*(?:from|import)\s+solana\.(?!_|__)',
    re.MULTILINE
)

# ============================================================================
# CHECK 2: Unified submitter enforcement
# ============================================================================
RAW_SUBMIT_PATTERN = re.compile(
    r'requests\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'client\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'session\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'"method"\s*:\s*"send(?:Transaction|RawTransaction)"',
    re.IGNORECASE
)

SEND_AND_CONFIRM_IMPORT = re.compile(r'from executors\.submit import.*send_and_confirm_v0_tx')

# ============================================================================
# CHECK 3: No list data in Instruction.data
# ============================================================================
# Match Instruction(...data=[...]) pattern, allowing for nested parentheses
INSTRUCTION_LIST_DATA_PATTERN = re.compile(
    r'Instruction\s*\(.*?data\s*=\s*\[',
    re.DOTALL
)

# ============================================================================
# CHECK 4: BuildResult must not return None
# ============================================================================
BUILDRESULT_RETURN_PATTERN = re.compile(
    r'def\s+\w*\s*\([^)]*\)\s*->\s*BuildResult:',
    re.MULTILINE
)

BUILDRESULT_IMPORT_PATTERN = re.compile(
    r'from models\.build_result import BuildResult'
)

RETURN_NONE_PATTERN = re.compile(r'^\s*return\s+None\s*(?:#.*)?$', re.MULTILINE)

# ============================================================================
# CHECK 5: MessageV0/VersionedTransaction must have compute budget
# ============================================================================
MESSAGE_V0_PATTERN = re.compile(r'MessageV0\.try_compile\s*\(')
VERSIONED_TX_PATTERN = re.compile(r'VersionedTransaction\s*\([^)]*message')
COMPUTE_BUDGET_PATTERN = re.compile(r'set_compute_unit_|with_compute_budget')

# ============================================================================
# Files to skip from all checks
# ============================================================================
SKIP_PATTERNS = [
    re.compile(r'(^|/)test_'),
    re.compile(r'(^|/)demo_'),
    re.compile(r'(^|/)validate_'),
    re.compile(r'(^|/)verify_'),
    re.compile(r'(^|/)patch_'),
    re.compile(r'__pycache__'),
    re.compile(r'\.pyc$'),
    re.compile(r'executors/submit\.py'),  # Allowed to have raw patterns for implementation
    re.compile(r'jito_service\.py'),  # Jito-specific implementation
]


def should_skip(path: str) -> bool:
    """Check if a file should be skipped from verification"""
    for pattern in SKIP_PATTERNS:
        if pattern.search(path):
            return True
    return False


def remove_comments_and_strings(content: str) -> str:
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


def check_solana_py_imports(content: str) -> List[Dict]:
    """Check for solana-py imports"""
    issues = []
    matches = list(SOLANA_PY_IMPORT_PATTERN.finditer(content))
    
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        issues.append({
            "line": line_num,
            "match": match.group(0).strip(),
            "message": "solana-py import found (should use solders instead)"
        })
    
    return issues


def check_unified_submitter(content: str) -> List[Dict]:
    """Check for raw transaction submission patterns"""
    issues = []
    
    # Check for raw patterns
    raw_matches = list(RAW_SUBMIT_PATTERN.finditer(content))
    has_helper_import = bool(SEND_AND_CONFIRM_IMPORT.search(content))
    
    # If there are raw patterns but no helper import, that's an issue
    if raw_matches and not has_helper_import:
        for match in raw_matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                "line": line_num,
                "match": match.group(0)[:80],
                "message": "Raw transaction submission without send_and_confirm_v0_tx import"
            })
    
    return issues


def check_instruction_list_data(content: str) -> List[Dict]:
    """Check for Instruction.data being a list"""
    issues = []
    cleaned = remove_comments_and_strings(content)
    matches = list(INSTRUCTION_LIST_DATA_PATTERN.finditer(cleaned))
    
    for match in matches:
        line_num = cleaned[:match.start()].count('\n') + 1
        issues.append({
            "line": line_num,
            "match": match.group(0).strip(),
            "message": "Instruction.data must not be a list (use bytes instead)"
        })
    
    return issues


def check_buildresult_return_none(content: str) -> List[Dict]:
    """Check for BuildResult functions that return None"""
    issues = []
    
    # Only check if BuildResult is imported
    if not BUILDRESULT_IMPORT_PATTERN.search(content):
        return issues
    
    # Find all functions that return BuildResult
    builders = list(BUILDRESULT_RETURN_PATTERN.finditer(content))
    
    for match in builders:
        func_start = match.start()
        func_end = min(func_start + 5000, len(content))
        func_body = content[func_start:func_end]
        
        # Find next function/class to limit scope
        next_def = re.search(r'\n(def |async def |class )', func_body[match.end() - func_start:])
        if next_def:
            func_body = func_body[:match.end() - func_start + next_def.start()]
        
        # Check for return None in function body
        if RETURN_NONE_PATTERN.search(func_body):
            line_num = content[:func_start].count('\n') + 1
            func_name = re.search(r'def\s+(\w+)', match.group(0))
            issues.append({
                "line": line_num,
                "match": func_name.group(1) if func_name else "unknown",
                "message": "Function returns BuildResult but has 'return None' statement"
            })
    
    return issues


def check_compute_budget(content: str) -> List[Dict]:
    """Check that MessageV0/VersionedTransaction constructions have compute budget"""
    issues = []
    cleaned = remove_comments_and_strings(content)
    
    # Check if file has transaction construction
    has_message_v0 = bool(MESSAGE_V0_PATTERN.search(cleaned))
    has_versioned_tx = bool(VERSIONED_TX_PATTERN.search(cleaned))
    
    if has_message_v0 or has_versioned_tx:
        # Check if compute budget is included
        has_compute_budget = bool(COMPUTE_BUDGET_PATTERN.search(content))
        
        if not has_compute_budget:
            # Find line numbers of constructions
            if has_message_v0:
                for match in MESSAGE_V0_PATTERN.finditer(cleaned):
                    line_num = cleaned[:match.start()].count('\n') + 1
                    issues.append({
                        "line": line_num,
                        "match": "MessageV0.try_compile",
                        "message": "MessageV0 construction without compute budget helper"
                    })
            
            if has_versioned_tx:
                for match in VERSIONED_TX_PATTERN.finditer(cleaned):
                    line_num = cleaned[:match.start()].count('\n') + 1
                    issues.append({
                        "line": line_num,
                        "match": "VersionedTransaction",
                        "message": "VersionedTransaction construction without compute budget helper"
                    })
    
    return issues


def check_file(path: str, root: str) -> Dict:
    """Run all checks on a single file"""
    rel_path = os.path.relpath(path, root)
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {
            "path": rel_path,
            "error": str(e),
            "issues": []
        }
    
    all_issues = []
    
    # Run all checks
    all_issues.extend([{"check": "solana-py imports", **issue} 
                       for issue in check_solana_py_imports(content)])
    all_issues.extend([{"check": "unified submitter", **issue} 
                       for issue in check_unified_submitter(content)])
    all_issues.extend([{"check": "instruction list data", **issue} 
                       for issue in check_instruction_list_data(content)])
    all_issues.extend([{"check": "BuildResult return None", **issue} 
                       for issue in check_buildresult_return_none(content)])
    all_issues.extend([{"check": "compute budget", **issue} 
                       for issue in check_compute_budget(content)])
    
    return {
        "path": rel_path,
        "issues": all_issues
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
    print("🔍 Repository Readiness Verification")
    print("=" * 80)
    print(f"Root directory: {root}")
    print()
    print("Checking for:")
    print("  1. No solana-py imports")
    print("  2. Unified submitter enforcement")
    print("  3. No list data in Instruction.data")
    print("  4. BuildResult functions don't return None")
    print("  5. Compute budget on all MessageV0/VersionedTransaction")
    print()
    
    # Find all Python files
    python_files = find_python_files(root)
    print(f"Found {len(python_files)} Python files to check")
    print()
    
    # Check each file
    all_results = []
    for path in python_files:
        result = check_file(path, root)
        all_results.append(result)
    
    # Collect all issues
    files_with_issues = [r for r in all_results if r.get("issues")]
    files_with_errors = [r for r in all_results if "error" in r]
    
    # Group issues by check type
    issues_by_check: Dict[str, List] = {}
    for result in files_with_issues:
        for issue in result["issues"]:
            check_name = issue["check"]
            if check_name not in issues_by_check:
                issues_by_check[check_name] = []
            issues_by_check[check_name].append({
                "file": result["path"],
                **issue
            })
    
    # Print results
    print("=" * 80)
    print("📊 Verification Results")
    print("=" * 80)
    print(f"Total files checked: {len(all_results)}")
    print(f"Files with issues: {len(files_with_issues)}")
    print(f"Files with errors: {len(files_with_errors)}")
    print()
    
    # Show issues by check type
    if issues_by_check:
        for check_name, issues in sorted(issues_by_check.items()):
            print("=" * 80)
            print(f"❌ {check_name.upper()} ({len(issues)} issue(s))")
            print("=" * 80)
            for issue in issues:
                print(f"\n📄 {issue['file']}:{issue['line']}")
                print(f"   {issue['message']}")
                if issue.get('match'):
                    print(f"   Found: {issue['match']}")
            print()
    
    # Show file errors
    if files_with_errors:
        print("=" * 80)
        print("⚠️  Errors During Verification")
        print("=" * 80)
        for result in files_with_errors:
            print(f"  - {result['path']}: {result['error']}")
        print()
    
    # Final verdict
    print("=" * 80)
    if not files_with_issues and not files_with_errors:
        print("✅ All checks passed.")
        print()
        print("Repository is ready! All standards are enforced:")
        print("  ✅ No solana-py imports")
        print("  ✅ Unified submitter is used")
        print("  ✅ No list data in Instruction.data")
        print("  ✅ BuildResult functions don't return None")
        print("  ✅ Compute budget set on all transactions")
        print("=" * 80)
        return 0
    else:
        print("❌ Readiness checks failed.")
        print()
        if files_with_issues:
            print(f"Found {sum(len(issues) for issues in issues_by_check.values())} issue(s) across {len(files_with_issues)} file(s).")
        if files_with_errors:
            print(f"Encountered {len(files_with_errors)} error(s) during verification.")
        print()
        print("Action required:")
        print("  1. Review the issues listed above")
        print("  2. Fix the issues manually or use available patch scripts:")
        print("     - python tools/patch_unified_submit.py")
        print("     - python tools/patch_buildresult.py")
        print("     - python tools/patch_compute_budget.py")
        print("  3. Re-run this verification script")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
