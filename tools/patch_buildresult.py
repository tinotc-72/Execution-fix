#!/usr/bin/env python3
"""
BuildResult Enforcement Patcher

This script scans Python files for builder functions that return None
and replaces them with BuildResult(ok=False, tx=None, reason="builder failed (added by patch)").

Usage:
    python tools/patch_buildresult.py --root .
    git diff
    python tools/verify_readiness.py
"""

import os
import re
import sys
import argparse
from typing import List, Tuple, Dict, Set

# Patterns for detection
BUILDRESULT_IMPORT_PATTERN = re.compile(r'from models\.build_result import BuildResult')

# Pattern to identify builder functions (functions with 'build' in the name)
BUILDER_FUNCTION_PATTERN = re.compile(r'^\s*(?:async\s+)?def\s+(\w*build\w*)\s*\(', re.MULTILINE)

# Pattern to find return None statements
RETURN_NONE_PATTERN = re.compile(r'^\s*return\s+None\s*$', re.MULTILINE)

# Files to skip
SKIP_PATTERNS = [
    re.compile(r'(^|/)test_'),
    re.compile(r'(^|/)demo_'),
    re.compile(r'(^|/)validate_'),
    re.compile(r'(^|/)verify_'),
    re.compile(r'patch_buildresult\.py'),
    re.compile(r'__pycache__'),
]


def should_skip(path: str) -> bool:
    """Check if a file should be skipped"""
    for pattern in SKIP_PATTERNS:
        if pattern.search(path):
            return True
    return False


def find_builder_functions(content: str) -> List[Tuple[int, str]]:
    """
    Find all builder function definitions in the content.
    
    Returns:
        List of tuples (line_number, function_name)
    """
    builders = []
    for match in BUILDER_FUNCTION_PATTERN.finditer(content):
        func_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        builders.append((line_num, func_name))
    return builders


def find_return_none_in_function(content: str, func_start_line: int) -> List[int]:
    """
    Find all 'return None' statements within a function starting at func_start_line.
    
    Returns:
        List of line numbers where 'return None' appears
    """
    lines = content.split('\n')
    
    # Find the function's indentation level
    if func_start_line > len(lines):
        return []
    
    func_line = lines[func_start_line - 1]
    func_indent = len(func_line) - len(func_line.lstrip())
    
    return_nones = []
    in_function_body = False
    in_docstring = False
    docstring_char = None
    
    # Scan forward from the function start to find return None statements
    for i in range(func_start_line, len(lines)):
        line = lines[i]
        stripped = line.strip()
        
        # Skip completely empty lines
        if not stripped:
            continue
        
        # Get line indentation
        line_indent = len(line) - len(line.lstrip())
        
        # Check for docstring start/end (both """ and ''')
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                # Check if it's a single-line docstring
                if stripped.endswith(docstring_char) and len(stripped) > 6:
                    # Single line docstring
                    pass
                else:
                    # Multi-line docstring start
                    in_docstring = True
                continue
        else:
            # We're in a docstring, look for the end
            if docstring_char in stripped:
                in_docstring = False
                docstring_char = None
            continue
        
        # Skip comment lines
        if stripped.startswith('#'):
            continue
        
        # Check if we're entering the function body (first non-docstring line with greater indentation)
        if not in_function_body and line_indent > func_indent:
            in_function_body = True
        
        # Check if we've left the function (dedented to same or less indentation than function def)
        # Only check this after we've entered the body and we're not in a docstring
        if in_function_body and not in_docstring and line_indent <= func_indent:
            # Check if this is a decorator or another function/class definition
            if stripped.startswith('def ') or stripped.startswith('class ') or stripped.startswith('@'):
                # We've left the function
                break
        
        # Check for return None within the function body
        if in_function_body and not in_docstring and RETURN_NONE_PATTERN.match(line):
            return_nones.append(i + 1)  # Line numbers are 1-indexed
    
    return return_nones


def has_buildresult_import(content: str) -> bool:
    """Check if the file already imports BuildResult"""
    return bool(BUILDRESULT_IMPORT_PATTERN.search(content))


def inject_buildresult_import(content: str) -> str:
    """
    Inject BuildResult import into the file.
    Tries to add it near other model imports or at the top after other imports.
    """
    lines = content.split('\n')
    
    # Find the best place to inject the import
    # Look for existing imports from models or similar
    insert_after = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('from models'):
            insert_after = i
            break
        elif line.strip().startswith('from ') or line.strip().startswith('import '):
            insert_after = i
    
    if insert_after == -1:
        # No imports found, add at the top after docstring/comments
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                insert_after = i - 1
                break
    
    # Insert the import
    if insert_after >= 0:
        lines.insert(insert_after + 1, 'from models.build_result import BuildResult')
        return '\n'.join(lines)
    else:
        # Fallback: add at the very top
        return 'from models.build_result import BuildResult\n' + content


def patch_return_none(content: str, line_num: int, indent_level: int = None) -> str:
    """
    Replace 'return None' at line_num with a BuildResult failure.
    
    Args:
        content: File content
        line_num: Line number (1-indexed) to patch
        indent_level: Optional indentation level to use
    
    Returns:
        Patched content
    """
    lines = content.split('\n')
    
    if line_num < 1 or line_num > len(lines):
        return content
    
    line_idx = line_num - 1
    line = lines[line_idx]
    
    # Determine indentation
    if indent_level is None:
        indent_level = len(line) - len(line.lstrip())
    
    indent = ' ' * indent_level
    
    # Replace the line
    new_line = f'{indent}return BuildResult(ok=False, tx=None, reason="builder failed (added by patch)")'
    lines[line_idx] = new_line
    
    return '\n'.join(lines)


def patch_file(file_path: str, dry_run: bool = False) -> Dict[str, any]:
    """
    Patch a single file to enforce BuildResult returns.
    
    Args:
        file_path: Path to the file to patch
        dry_run: If True, only report changes without writing
    
    Returns:
        Dict with patch results
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
    except Exception as e:
        return {
            "path": file_path,
            "error": str(e),
            "patched": False
        }
    
    content = original_content
    
    # Find builder functions
    builders = find_builder_functions(content)
    
    if not builders:
        return {
            "path": file_path,
            "builders": 0,
            "return_nones": 0,
            "patched": False,
            "message": "No builder functions found"
        }
    
    # Find return None statements in builder functions
    all_return_nones = []
    seen_lines = set()
    for line_num, func_name in builders:
        return_nones = find_return_none_in_function(content, line_num)
        for rn_line in return_nones:
            if rn_line not in seen_lines:
                all_return_nones.append((rn_line, func_name))
                seen_lines.add(rn_line)
    
    if not all_return_nones:
        return {
            "path": file_path,
            "builders": len(builders),
            "return_nones": 0,
            "patched": False,
            "message": "No return None statements found in builder functions"
        }
    
    # Inject BuildResult import if needed
    needs_import = not has_buildresult_import(content)
    if needs_import:
        content = inject_buildresult_import(content)
    
    # Patch all return None statements (in reverse order to maintain line numbers)
    for line_num, func_name in sorted(all_return_nones, reverse=True):
        content = patch_return_none(content, line_num)
    
    # Write the patched content
    if not dry_run and content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            return {
                "path": file_path,
                "error": f"Failed to write: {e}",
                "patched": False
            }
    
    return {
        "path": file_path,
        "builders": len(builders),
        "return_nones": len(all_return_nones),
        "import_added": needs_import,
        "patched": content != original_content,
        "builder_names": [name for _, name in builders],
        "patched_lines": [line for line, _ in all_return_nones]
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
    parser = argparse.ArgumentParser(
        description='Patch Python files to enforce BuildResult returns in builder functions'
    )
    parser.add_argument('--root', default='.', help='Root directory to scan')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    root = os.path.abspath(args.root)
    
    print("=" * 80)
    print("🔧 BuildResult Enforcement Patcher")
    print("=" * 80)
    print(f"Root directory: {root}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # Find all Python files
    python_files = find_python_files(root)
    print(f"Found {len(python_files)} Python files to scan")
    print()
    
    # Patch each file
    results = []
    for file_path in python_files:
        result = patch_file(file_path, dry_run=args.dry_run)
        results.append(result)
        
        if args.verbose or result.get("patched"):
            rel_path = os.path.relpath(file_path, root)
            print(f"📄 {rel_path}")
            
            if result.get("error"):
                print(f"   ❌ Error: {result['error']}")
            elif result.get("patched"):
                print(f"   ✅ Patched!")
                print(f"      - Builders: {result['builders']}")
                print(f"      - Return Nones patched: {result['return_nones']}")
                if result.get("import_added"):
                    print(f"      - BuildResult import added")
                if result.get("patched_lines"):
                    print(f"      - Lines patched: {result['patched_lines']}")
            elif result.get("builders") > 0:
                print(f"   ℹ️  {result.get('message', 'No changes needed')}")
    
    # Summary
    patched_files = [r for r in results if r.get("patched")]
    files_with_builders = [r for r in results if r.get("builders", 0) > 0]
    total_return_nones = sum(r.get("return_nones", 0) for r in results)
    imports_added = sum(1 for r in results if r.get("import_added"))
    errors = [r for r in results if r.get("error")]
    
    print()
    print("=" * 80)
    print("📊 Patch Summary")
    print("=" * 80)
    print(f"Total files scanned: {len(results)}")
    print(f"Files with builder functions: {len(files_with_builders)}")
    print(f"Files patched: {len(patched_files)}")
    print(f"Total return None statements replaced: {total_return_nones}")
    print(f"BuildResult imports added: {imports_added}")
    
    if errors:
        print(f"Errors: {len(errors)}")
        for r in errors:
            print(f"  - {r['path']}: {r['error']}")
    
    print()
    
    if patched_files:
        print("=" * 80)
        print("✅ Patched Files")
        print("=" * 80)
        for r in patched_files:
            rel_path = os.path.relpath(r['path'], root)
            print(f"  - {rel_path}")
            if r.get("builder_names"):
                print(f"    Builders: {', '.join(r['builder_names'])}")
        print()
    
    if args.dry_run:
        print("=" * 80)
        print("🔍 DRY RUN - No files were modified")
        print("=" * 80)
        print("Run without --dry-run to apply changes")
        print()
    else:
        print("=" * 80)
        print("✅ PATCHING COMPLETE")
        print("=" * 80)
        print("Next steps:")
        print("  1. Review changes with: git diff")
        print("  2. Run verification: python tools/verify_readiness.py")
        print("  3. Run tests to ensure nothing breaks")
        print("=" * 80)
    
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
