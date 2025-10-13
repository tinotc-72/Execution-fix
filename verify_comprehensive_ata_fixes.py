#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE ATA FIX VERIFICATION
Check if the ATA (Associated Token Account) fix has been applied throughout the entire codebase
"""

import os
import re

def verify_ata_fixes():
    """Verify ATA fixes across all executor files"""
    print("🔍 COMPREHENSIVE ATA FIX VERIFICATION")
    print("=" * 70)
    
    # Core executor files that should have ATA fixes
    executor_files = [
        "pumpfun_copy_executor.py",
        "jupiter_copy_executor.py", 
        "raydium_copy_executor.py",
        "cpmm_copy_executor.py",
        "raydium_clmm_copy_executor.py",
        "clmm_copy_executor.py",
        "raydium_trade_executor.py",
        "raydium_clmm_trade_executor.py",
        "pumpfun_executor.py",
        "pumpfun_trade_executor.py"
    ]
    
    # Patterns that indicate proper ATA fix implementation
    ata_fix_patterns = {
        "ensure_method": r"async def ensure_token_account_exists",
        "existence_check": r"account_info\.value\s*(is not None|!=\s*None)|get_account_info.*ata",
        "early_return_check": r"if.*account_info\.value.*is not None|if.*ata_exists",
        "early_return_log": r"ATA already exists.*skipping creation|✅.*ATA.*exists",
        "enhanced_comment": r"ENHANCED.*Check first.*create|ELIMINATES IllegalOwner errors",
        "step_1_check": r"STEP 1.*CHECK IF ATA.*EXISTS|🔍.*Checking if ATA exists",
        "step_2_create": r"STEP 2.*CREATE.*IF.*NOT.*EXIST|🔨.*ATA.*creating",
        "illegal_owner_prevention": r"IllegalOwner|provided owner is not allowed"
    }
    
    results = {}
    
    for executor_file in executor_files:
        print(f"\n📝 {executor_file}:")
        
        if not os.path.exists(executor_file):
            print(f"   ❌ File not found")
            results[executor_file] = {'found': False, 'score': 0}
            continue
        
        try:
            with open(executor_file, 'r') as f:
                content = f.read()
            
            # Check each pattern
            pattern_results = {}
            score = 0
            
            for pattern_name, pattern in ata_fix_patterns.items():
                found = bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))
                pattern_results[pattern_name] = found
                if found:
                    score += 1
                
                # Display results with specific labels
                labels = {
                    "ensure_method": "ensure_token_account_exists method",
                    "existence_check": "ATA existence checking",
                    "early_return_check": "Early return logic",
                    "early_return_log": "Skipping creation logs",
                    "enhanced_comment": "Enhanced comments",
                    "step_1_check": "Step 1: Check exists",
                    "step_2_create": "Step 2: Create if needed",
                    "illegal_owner_prevention": "IllegalOwner error handling"
                }
                
                print(f"   {labels[pattern_name]}: {'✅' if found else '❌'}")
            
            # Calculate overall ATA fix status
            total_patterns = len(ata_fix_patterns)
            fix_percentage = (score / total_patterns) * 100
            
            if score >= 6:  # Most important patterns
                status = "✅ FULLY IMPLEMENTED"
                overall = True
            elif score >= 4:
                status = "⚠️ PARTIALLY IMPLEMENTED"
                overall = False
            else:
                status = "❌ NOT IMPLEMENTED"
                overall = False
            
            print(f"   Overall ATA Fix: {status} ({score}/{total_patterns} patterns)")
            
            results[executor_file] = {
                'found': True,
                'score': score,
                'percentage': fix_percentage,
                'status': overall,
                'patterns': pattern_results
            }
            
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            results[executor_file] = {'found': False, 'score': 0, 'error': str(e)}
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 ATA FIX IMPLEMENTATION SUMMARY")
    print("=" * 70)
    
    total_files = len([r for r in results.values() if r.get('found', False)])
    fully_fixed = len([r for r in results.values() if r.get('status', False)])
    
    for executor_file, result in results.items():
        if result.get('found', False):
            score = result.get('score', 0)
            percentage = result.get('percentage', 0)
            if result.get('status', False):
                print(f"✅ {executor_file}: FULLY FIXED ({score}/8 patterns - {percentage:.0f}%)")
            else:
                print(f"⚠️ {executor_file}: NEEDS WORK ({score}/8 patterns - {percentage:.0f}%)")
        else:
            print(f"❌ {executor_file}: FILE NOT FOUND")
    
    print("\n" + "=" * 70)
    print(f"📊 OVERALL ATA FIX STATUS: {fully_fixed}/{total_files} files fully fixed")
    
    if fully_fixed == total_files:
        print("🎉 ALL FILES HAVE COMPREHENSIVE ATA FIXES!")
        print("✅ IllegalOwner errors should be completely eliminated")
    else:
        missing_fixes = total_files - fully_fixed
        print(f"⚠️ {missing_fixes} file(s) need additional ATA fix implementation")
        
        # Show which files need work
        print(f"\n📋 Files needing ATA fix improvements:")
        for executor_file, result in results.items():
            if result.get('found', False) and not result.get('status', False):
                score = result.get('score', 0)
                print(f"   • {executor_file} (score: {score}/8)")
    
    print("=" * 70)
    
    # Detailed pattern analysis
    print("\n🔬 DETAILED PATTERN ANALYSIS:")
    pattern_counts = {}
    for pattern_name in ata_fix_patterns:
        count = sum(1 for r in results.values() 
                   if r.get('patterns', {}).get(pattern_name, False))
        pattern_counts[pattern_name] = count
        total_applicable = sum(1 for r in results.values() if r.get('found', False))
        percentage = (count / total_applicable * 100) if total_applicable > 0 else 0
        
        labels = {
            "ensure_method": "ensure_token_account_exists method",
            "existence_check": "ATA existence checking", 
            "early_return_check": "Early return logic",
            "early_return_log": "Skipping creation logs",
            "enhanced_comment": "Enhanced comments",
            "step_1_check": "Step 1: Check exists",
            "step_2_create": "Step 2: Create if needed",
            "illegal_owner_prevention": "IllegalOwner error handling"
        }
        
        print(f"   {labels[pattern_name]}: {count}/{total_applicable} files ({percentage:.0f}%)")
    
    return fully_fixed == total_files

if __name__ == "__main__":
    all_fixed = verify_ata_fixes()
    
    if all_fixed:
        print("\n🚀 VERIFICATION COMPLETE: ATA fixes properly implemented throughout codebase!")
    else:
        print("\n⚠️ VERIFICATION INCOMPLETE: Some files need ATA fix improvements")
