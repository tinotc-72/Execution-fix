#!/usr/bin/env python3
"""
MASS FIX - Replace ALL wrong Pump.fun program IDs with the correct one
"""

import os
import re

def fix_all_program_ids():
    print("🔧 MASS FIXING ALL PUMP.FUN PROGRAM IDS")
    print("=" * 60)
    
    # The IDs
    wrong_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    correct_program_id = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
    
    print(f"❌ Wrong ID:  {wrong_program_id}")
    print(f"✅ Correct ID: {correct_program_id}")
    print()
    
    # Get all Python files with pump in the name
    pump_files = []
    for file in os.listdir('.'):
        if 'pump' in file.lower() and file.endswith('.py'):
            pump_files.append(file)
    
    print(f"📂 Found {len(pump_files)} pump.fun files to check:")
    for file in pump_files:
        print(f"   • {file}")
    print()
    
    total_fixes = 0
    files_fixed = 0
    
    for file in pump_files:
        try:
            # Read the file
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count occurrences
            wrong_count = content.count(wrong_program_id)
            
            if wrong_count > 0:
                print(f"🔧 Fixing {file}:")
                print(f"   Found {wrong_count} instances of wrong program ID")
                
                # Replace all occurrences
                new_content = content.replace(wrong_program_id, correct_program_id)
                
                # Verify the replacement worked
                verify_wrong = new_content.count(wrong_program_id)
                verify_correct = new_content.count(correct_program_id)
                
                if verify_wrong == 0:
                    # Write the fixed file
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"   ✅ Fixed! Now has {verify_correct} correct program IDs")
                    total_fixes += wrong_count
                    files_fixed += 1
                else:
                    print(f"   ❌ Error: Still has {verify_wrong} wrong IDs after fix")
            else:
                print(f"✅ {file}: Already correct (no wrong IDs found)")
                
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")
    
    print()
    print("📊 MASS FIX SUMMARY:")
    print(f"   Files processed: {len(pump_files)}")
    print(f"   Files fixed: {files_fixed}")
    print(f"   Total wrong IDs replaced: {total_fixes}")
    print()
    
    if total_fixes > 0:
        print("🎉 ALL PUMP.FUN FILES NOW HAVE CORRECT PROGRAM ID!")
        print("✅ This should resolve ALL the issues in the verification")
        print("✅ Your bot should now work correctly")
    else:
        print("ℹ️  No fixes needed - all files already correct")
    
    return total_fixes

if __name__ == "__main__":
    fixes_applied = fix_all_program_ids()
    
    if fixes_applied > 0:
        print("\n🚀 RECOMMENDATION:")
        print("   Run the verification script again to confirm all fixes")
        print("   python3 verify_all_fixes.py")
    else:
        print("\n✅ ALL GOOD:")
        print("   No wrong program IDs found in any pump.fun files")
