#!/usr/bin/env python3
"""
Automatic patcher to inject compute budget calls into transaction builders.

This script scans Python files for usage of MessageV0 or VersionedTransaction
without an existing compute budget call, then injects the necessary import and
wraps the last `ixs =` assignment with a compute budget call.

Usage:
    python tools/patch_compute_budget.py --root . --cu-limit 1000000 --cu-price 5000
"""
import os
import re
import sys
import argparse

# Pattern to detect actual transaction construction, not just imports
MSG_CONSTRUCT_RX = re.compile(r'MessageV0\.try_compile\(|VersionedTransaction\([^)]')
HAS_CU_RX = re.compile(r'set_compute_unit_|with_compute_budget')
INSERT_IMPORT = 'from utils.fees import with_compute_budget\n'

def process_file(path, cu_limit, cu_price, verbose=False):
    """
    Process a single Python file to inject compute budget calls.
    
    Args:
        path: Path to the Python file
        cu_limit: Compute unit limit to use
        cu_price: Compute unit price to use
        verbose: Print debug information
        
    Returns:
        True if file was modified, False otherwise
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()

    # Skip files that don't actually construct MessageV0 or VersionedTransaction
    if not MSG_CONSTRUCT_RX.search(src):
        if verbose:
            print(f"  DEBUG: {path} - No transaction construction found")
        return False
    
    # Skip files that already have compute budget handling
    if HAS_CU_RX.search(src):
        if verbose:
            print(f"  DEBUG: {path} - Already has compute budget")
        return False
    
    if verbose:
        print(f"  DEBUG: {path} - Needs patching")

    # Add import if not already present
    if 'with_compute_budget' not in src:
        # Insert after initial docstring if present, otherwise at top
        lines = src.splitlines()
        insert_pos = 0
        
        # Skip shebang and initial docstrings
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and stripped.startswith('#!'):
                insert_pos = i + 1
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    if stripped.endswith('"""') or stripped.endswith("'''"):
                        in_docstring = False
                        insert_pos = i + 1
                elif in_docstring:
                    in_docstring = False
                    insert_pos = i + 1
            elif not in_docstring and stripped and not stripped.startswith('#'):
                break
        
        lines.insert(insert_pos, INSERT_IMPORT.rstrip())
        src = '\n'.join(lines)

    # Find instruction list assignments before MessageV0.try_compile or VersionedTransaction
    lines = src.splitlines()
    modified = False
    
    # Look for patterns where instructions are passed to MessageV0 or VersionedTransaction
    for i in range(len(lines)):
        line = lines[i]
        # Check if this line has MessageV0.try_compile or VersionedTransaction construction
        if 'MessageV0.try_compile' in line or ('VersionedTransaction(' in line and 'message' in line.lower()):
            if verbose:
                print(f"    Found construction at line {i}: {line.strip()[:60]}")
            # Look backwards for the last instruction assignment
            for j in range(i-1, max(0, i-20), -1):
                # Match various patterns: ixs =, instructions =, new_instructions =
                match = re.search(r'^\s*(ixs|instructions|new_instructions)\s*=\s*(.+)', lines[j])
                if match:
                    var_name = match.group(1)
                    value = match.group(2)
                    if verbose:
                        print(f"    Found instruction assignment at line {j}: {var_name} = {value.strip()[:40]}")
                    # Don't wrap if it's already calling with_compute_budget or if it's just an empty list
                    if 'with_compute_budget' not in value and value.strip() != '[]':
                        # Insert compute budget call after this assignment
                        indent = ' ' * (len(lines[j]) - len(lines[j].lstrip()))
                        lines.insert(j+1, f'{indent}{var_name} = with_compute_budget({var_name}, cu_limit={cu_limit}, cu_price={cu_price})')
                        if verbose:
                            print(f"    Inserted compute budget call after line {j}")
                        modified = True
                    else:
                        if verbose:
                            print(f"    Skipping: already has compute budget or is empty list")
                    break
            else:
                if verbose:
                    print(f"    No instruction assignment found within 20 lines before construction")
    
    if not modified:
        # If we couldn't find a simple assignment, don't modify
        if verbose:
            print(f"    No modifications made")
        return False
    
    src = "\n".join(lines)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    return True

def main():
    ap = argparse.ArgumentParser(
        description='Inject compute budget calls into transaction builders'
    )
    ap.add_argument('--root', required=True, help='Root directory to scan')
    ap.add_argument('--cu-limit', type=int, default=1000000, help='Compute unit limit')
    ap.add_argument('--cu-price', type=int, default=5000, help='Compute unit price (micro-lamports)')
    ap.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    args = ap.parse_args()

    print(f"🔍 Scanning for files in {args.root}...")
    print(f"   CU Limit: {args.cu_limit}")
    print(f"   CU Price: {args.cu_price}")
    print()

    edited = 0
    skipped = 0
    errors = 0
    
    for base, _, files in os.walk(args.root):
        # Skip test, demo, validate, and hidden directories
        if any(x in base for x in ['test', 'demo', 'validate', '__pycache__', '.git']):
            continue
            
        for fn in files:
            if not fn.endswith('.py'):
                continue
                
            # Skip test, demo, and validation files
            if fn.startswith('test_') or fn.startswith('demo_') or fn.startswith('validate_'):
                continue
                
            p = os.path.join(base, fn)
            try:
                if process_file(p, args.cu_limit, args.cu_price, args.verbose):
                    print(f"✅ Patched: {p}")
                    edited += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"❌ Error processing {p}: {e}")
                errors += 1
    
    print()
    print("=" * 80)
    print(f"📊 Summary:")
    print(f"   Patched files: {edited}")
    print(f"   Skipped files: {skipped}")
    print(f"   Errors: {errors}")
    print("=" * 80)
    
    if edited > 0:
        print()
        print("✅ Patching complete! Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Test changes: python tools/verify_readiness.py")
        print("   3. Run tests to ensure nothing broke")
    
    return 0 if errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
