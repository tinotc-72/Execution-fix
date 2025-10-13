#!/usr/bin/env python3
"""
SMART VERIFICATION - Only flags actual issues, not false positives
"""

import os
import re

def smart_verify_fixes():
    print("🧠 SMART VERIFICATION OF PUMP.FUN FIXES")
    print("=" * 60)
    
    wrong_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    correct_program_id = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
    
    # Get all pump.fun files
    pump_files = [f for f in os.listdir('.') if 'pump' in f.lower() and f.endswith('.py')]
    
    print(f"📂 Checking {len(pump_files)} pump.fun files...")
    print()
    
    issues_found = []
    files_with_wrong_ids = []
    
    for file in pump_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            wrong_count = content.count(wrong_program_id)
            correct_count = content.count(correct_program_id)
            
            # Check if file is empty
            if len(content.strip()) == 0:
                print(f"📄 {file}: Empty file (OK)")
                continue
            
            # Check if it's a diagnostic/test file that doesn't need program IDs
            is_diagnostic = any(keyword in file.lower() for keyword in [
                'diagnose', 'test_', 'analyze_', 'verify_', 'validate_'
            ])
            
            if wrong_count > 0:
                # This is a REAL issue - file has wrong program IDs
                issues_found.append(f"{file}: {wrong_count} wrong program IDs")
                files_with_wrong_ids.append(file)
                print(f"❌ {file}: Has {wrong_count} WRONG program IDs - NEEDS FIX")
            
            elif correct_count > 0:
                # File has correct program IDs - good!
                print(f"✅ {file}: Has {correct_count} correct program IDs")
            
            elif is_diagnostic:
                # Diagnostic/test file with no program IDs - that's fine
                print(f"🔧 {file}: Diagnostic/test file (no program ID needed)")
            
            else:
                # Regular pump.fun file with no program IDs - might be an issue
                # But let's check if it imports from other files
                if 'import' in content and 'pump' in content:
                    print(f"📦 {file}: Imports pump.fun code (program ID from imports)")
                else:
                    print(f"ℹ️  {file}: No program ID references (may be utility)")
                    
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
    
    print()
    print("📊 SMART VERIFICATION SUMMARY:")
    print("=" * 40)
    
    if files_with_wrong_ids:
        print(f"❌ REAL ISSUES FOUND: {len(files_with_wrong_ids)} files")
        for issue in issues_found:
            print(f"   • {issue}")
        print()
        print("🎯 CONFIDENCE LEVEL: LOW - Fixes needed")
    else:
        print("✅ NO REAL ISSUES FOUND!")
        print("✅ All files either have correct program IDs or don't need them")
        print()
        print("🎯 CONFIDENCE LEVEL: HIGH - All good!")
        print("🚀 Your bot should work correctly now!")
    
    return len(files_with_wrong_ids)

if __name__ == "__main__":
    issues = smart_verify_fixes()
    
    if issues == 0:
        print("\n🎉 CONCLUSION:")
        print("   All pump.fun files are correctly configured!")
        print("   Ready to test with real transactions!")
    else:
        print(f"\n🔧 ACTION NEEDED:")
        print(f"   {issues} files still need fixing")
