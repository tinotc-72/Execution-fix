#!/usr/bin/env python3
"""
Automated patcher to replace raw transaction submission with unified submit helper.

This script scans Python files for raw JSON-RPC submission patterns and replaces them
with imports and calls to send_and_confirm_v0_tx_sync from executors.submit.

Usage:
    python tools/patch_unified_submit.py --root . --rpc-env RPC_URL
"""

import os
import re
import sys
import argparse
from typing import List, Tuple

# Pattern to match raw sendTransaction/sendRawTransaction calls
# Matches both requests.post and httpx/aiohttp patterns
RAW_SUBMIT_RX = re.compile(
    r'(requests\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'client\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'session\.post\([^)]*send(?:Transaction|RawTransaction)[^)]*\)|'
    r'"method"\s*:\s*"send(?:Transaction|RawTransaction)")',
    re.I | re.S
)

# Pattern to check if file already uses the helper
HAS_HELPER_RX = re.compile(r'\bsend_and_confirm_v0_tx(?:_sync)?\b')

# Pattern to check if file is in test or demo directories
TEST_FILE_RX = re.compile(r'(^|/)test_|demo_|validate_|verify_')


def should_skip_file(path: str) -> Tuple[bool, str]:
    """
    Determine if a file should be skipped.
    
    Returns:
        Tuple of (should_skip, reason)
    """
    # Skip test files
    if TEST_FILE_RX.search(path):
        return True, "test/demo/validation file"
    
    # Skip the patcher itself
    if 'patch_unified_submit.py' in path:
        return True, "patcher script"
    
    # Skip verify script
    if 'verify_readiness.py' in path:
        return True, "verification script"
    
    # Skip executors/submit.py (the helper itself)
    if path.endswith('executors/submit.py'):
        return True, "submit helper module"
    
    # Skip jito_service.py (Jito-first is optional per requirements)
    if 'jito_service.py' in path:
        return True, "Jito service (optional Jito-first path)"
    
    return False, ""


def analyze_file(path: str) -> dict:
    """
    Analyze a file to understand its structure and raw submission patterns.
    
    Returns:
        Dict with analysis results
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            src = f.read()
    except Exception as e:
        return {"error": str(e)}
    
    has_raw_submit = bool(RAW_SUBMIT_RX.search(src))
    has_helper = bool(HAS_HELPER_RX.search(src))
    has_async_def = 'async def' in src
    has_await = 'await' in src
    
    # Find specific patterns
    raw_matches = list(RAW_SUBMIT_RX.finditer(src))
    
    return {
        "has_raw_submit": has_raw_submit,
        "has_helper": has_helper,
        "has_async_def": has_async_def,
        "has_await": has_await,
        "raw_match_count": len(raw_matches),
        "needs_patching": has_raw_submit and not has_helper
    }


def add_import_if_missing(src: str) -> str:
    """Add the unified submit helper import if not already present"""
    if 'from executors.submit import send_and_confirm_v0_tx_sync' in src:
        return src
    
    # Find a good place to add the import
    # Try to add after other executors imports, or after other imports
    lines = src.split('\n')
    insert_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith('from executors') or line.startswith('from models'):
            insert_idx = i + 1
        elif line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
    
    # Insert the import
    import_line = 'from executors.submit import send_and_confirm_v0_tx_sync, SubmitResult'
    lines.insert(insert_idx, import_line)
    
    return '\n'.join(lines)


def add_os_import_if_missing(src: str) -> str:
    """Add os import if not already present (needed for os.getenv)"""
    if re.search(r'^import os\b', src, re.MULTILINE):
        return src
    if re.search(r'^from os import ', src, re.MULTILINE):
        return src
    
    # Find a good place to add the import
    lines = src.split('\n')
    insert_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith('import ') and not line.startswith('import logging'):
            insert_idx = i
            break
    
    lines.insert(insert_idx, 'import os')
    return '\n'.join(lines)


def create_replacement_code(rpc_env: str, context: str = "") -> str:
    """
    Create replacement code for raw submission.
    
    Args:
        rpc_env: Environment variable name for RPC URL
        context: Surrounding code context for better replacement
    """
    return f"""# Replaced raw submission with unified helper
# NOTE: Ensure you have a VersionedTransaction object named 'versioned_tx' or 'vtx'
# and variables: dex (str), action (str), mint (str)
try:
    res = send_and_confirm_v0_tx_sync(os.getenv("{rpc_env}"), versioned_tx)
    logger.info(f"[SUBMIT] DEX={{dex}} action={{action}} mint={{mint}} sig={{res.signature}} status={{res.confirmationStatus}} ok={{res.ok}}")
except NameError:
    # If versioned_tx doesn't exist, try vtx
    res = send_and_confirm_v0_tx_sync(os.getenv("{rpc_env}"), vtx)
    logger.info(f"[SUBMIT] DEX={{dex}} action={{action}} mint={{mint}} sig={{res.signature}} status={{res.confirmationStatus}} ok={{res.ok}}")
# Original code (commented out): """


def process_file(path: str, rpc_env: str, dry_run: bool = False) -> bool:
    """
    Process a single file, replacing raw submission patterns.
    
    Returns:
        True if file was modified, False otherwise
    """
    # Check if should skip
    should_skip, reason = should_skip_file(path)
    if should_skip:
        return False
    
    # Analyze file
    analysis = analyze_file(path)
    if "error" in analysis:
        print(f"  ⚠️  Error analyzing {path}: {analysis['error']}")
        return False
    
    if not analysis["needs_patching"]:
        return False
    
    # Read source
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            src = f.read()
    except Exception as e:
        print(f"  ⚠️  Error reading {path}: {e}")
        return False
    
    # Add imports
    src = add_import_if_missing(src)
    src = add_os_import_if_missing(src)
    
    # Replace raw submission patterns with comments and helper calls
    # This is a conservative approach - we comment out the old code
    # and add a template for the new code
    replacement = create_replacement_code(rpc_env)
    
    # Use a simple comment-out approach to preserve original code
    def replace_with_comment(match):
        original = match.group(0)
        lines = original.split('\n')
        commented = '\n'.join('# ' + line for line in lines)
        return replacement + commented
    
    # Apply replacement
    modified_src = RAW_SUBMIT_RX.sub(replace_with_comment, src)
    
    if dry_run:
        print(f"  📝 Would modify: {path}")
        return True
    
    # Write back
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified_src)
        print(f"  ✅ Patched: {path}")
        return True
    except Exception as e:
        print(f"  ❌ Error writing {path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Replace raw transaction submission with unified helper'
    )
    parser.add_argument(
        '--root',
        required=True,
        help='Root directory to scan for Python files'
    )
    parser.add_argument(
        '--rpc-env',
        default='RPC_URL',
        help='Environment variable name for RPC URL (default: RPC_URL)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    args = parser.parse_args()
    
    print("=" * 80)
    print("🔧 Unified Submit Helper Patcher")
    print("=" * 80)
    print(f"Root directory: {args.root}")
    print(f"RPC environment variable: {args.rpc_env}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # Walk through all Python files
    edited_files = []
    skipped_files = []
    error_files = []
    
    for base, dirs, files in os.walk(args.root):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for fn in files:
            if not fn.endswith('.py'):
                continue
            
            p = os.path.join(base, fn)
            rel_path = os.path.relpath(p, args.root)
            
            # Check if should skip
            should_skip, reason = should_skip_file(rel_path)
            if should_skip:
                skipped_files.append((rel_path, reason))
                continue
            
            try:
                if process_file(p, args.rpc_env, args.dry_run):
                    edited_files.append(rel_path)
            except Exception as e:
                error_files.append((rel_path, str(e)))
                print(f"  ❌ Error processing {rel_path}: {e}")
    
    # Print summary
    print()
    print("=" * 80)
    print("📊 Summary")
    print("=" * 80)
    print(f"✅ Files patched: {len(edited_files)}")
    print(f"⏭️  Files skipped: {len(skipped_files)}")
    print(f"❌ Errors: {len(error_files)}")
    print()
    
    if edited_files:
        print("Patched files:")
        for f in edited_files:
            print(f"  - {f}")
        print()
    
    if error_files:
        print("Errors:")
        for f, err in error_files:
            print(f"  - {f}: {err}")
        print()
    
    print("=" * 80)
    print("✅ Patching complete!")
    print()
    print("Next steps:")
    print("  1. Run 'git diff' to review changes")
    print("  2. Run 'python tools/verify_readiness.py' to verify")
    print("  3. Search for any remaining raw submissions:")
    print("     grep -r 'sendTransaction\\|sendRawTransaction' --include='*.py' .")
    print("=" * 80)
    
    return 0 if not error_files else 1


if __name__ == '__main__':
    sys.exit(main())
