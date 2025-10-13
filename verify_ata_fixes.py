#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE ATA FIX VERIFICATION
Verifies all pump.fun executors have proper ATA existence checking implemented
"""
import os
import re
from typing import List, Dict, Tuple

def analyze_file_for_ata_fix(file_path: str) -> Dict:
    """Analyze a Python file for ATA existence checking patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': file_path,
            'error': f"Could not read file: {e}",
            'has_ensure_token_account_exists': False,
            'has_ata_existence_check': False,
            'has_early_return_pattern': False,
            'has_proper_logging': False,
            'analysis': 'ERROR'
        }
    
    # Check for key patterns
    has_ensure_method = 'ensure_token_account_exists' in content
    has_create_ata = 'create_associated_token_account' in content
    
    # Look for ATA existence checking patterns
    ata_check_patterns = [
        r'get_account_info.*ata',
        r'account_info\.value',
        r'ATA.*exists',
        r'already exists.*skipping',
        r'🔍.*Checking if ATA exists',
        r'✅.*ATA already exists'
    ]
    
    has_existence_check = any(re.search(pattern, content, re.IGNORECASE) for pattern in ata_check_patterns)
    
    # Look for early return pattern
    early_return_patterns = [
        r'if.*account_info.*return.*ata',
        r'return ata',
        r'skipping creation.*return'
    ]
    
    has_early_return = any(re.search(pattern, content, re.IGNORECASE) for pattern in early_return_patterns)
    
    # Look for proper logging
    logging_patterns = [
        r'🔍.*Checking',
        r'✅.*already exists',
        r'🔨.*creating',
        r'logger\.info.*ATA'
    ]
    
    has_proper_logging = any(re.search(pattern, content, re.IGNORECASE) for pattern in logging_patterns)
    
    # Analyze quality
    analysis = 'UNKNOWN'
    if has_ensure_method and has_existence_check and has_early_return and has_proper_logging:
        analysis = 'EXCELLENT'
    elif has_ensure_method and has_existence_check and has_early_return:
        analysis = 'GOOD'
    elif has_ensure_method and has_existence_check:
        analysis = 'BASIC'
    elif has_ensure_method:
        analysis = 'INCOMPLETE'
    elif has_create_ata:
        analysis = 'NEEDS_FIX'
    else:
        analysis = 'NO_ATA_LOGIC'
    
    return {
        'file': os.path.basename(file_path),
        'has_ensure_token_account_exists': has_ensure_method,
        'has_ata_existence_check': has_existence_check,
        'has_early_return_pattern': has_early_return,
        'has_proper_logging': has_proper_logging,
        'has_create_ata': has_create_ata,
        'analysis': analysis
    }

def main():
    """Main verification function"""
    print("🔍 COMPREHENSIVE ATA FIX VERIFICATION")
    print("=" * 60)
    
    # List of key pump.fun files to check
    pump_files = [
        'pumpfun_copy_executor.py',
        'pumpfun_executor.py',
        'pumpfun_trade_executor.py',
        'direct_pumpfun.py',
        '1_Pump.fun.py',
        'execution_coordinator.py'
    ]
    
    # Additional files that might have ATA logic
    additional_files = [
        'jupiter_copy_executor.py',
        'raydium_copy_executor.py',
        'raydium_clmm_copy_executor.py',
        'cpmm_copy_executor.py',
        'clmm_copy_executor.py'
    ]
    
    all_files = pump_files + additional_files
    
    results = []
    
    for filename in all_files:
        if os.path.exists(filename):
            result = analyze_file_for_ata_fix(filename)
            results.append(result)
        else:
            results.append({
                'file': filename,
                'analysis': 'NOT_FOUND',
                'has_ensure_token_account_exists': False,
                'has_ata_existence_check': False,
                'has_early_return_pattern': False,
                'has_proper_logging': False
            })
    
    # Print results
    print("\\n📊 ANALYSIS RESULTS:")
    print("-" * 60)
    
    excellent_files = []
    good_files = []
    basic_files = []
    needs_fix_files = []
    incomplete_files = []
    
    for result in results:
        status_emoji = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡', 
            'BASIC': '🟠',
            'INCOMPLETE': '🔴',
            'NEEDS_FIX': '🔴',
            'NO_ATA_LOGIC': '⚪',
            'NOT_FOUND': '⚫',
            'ERROR': '❌'
        }.get(result['analysis'], '❓')
        
        print(f"{status_emoji} {result['file']:<35} {result['analysis']}")
        
        if result['analysis'] == 'EXCELLENT':
            excellent_files.append(result['file'])
        elif result['analysis'] == 'GOOD':
            good_files.append(result['file'])
        elif result['analysis'] == 'BASIC':
            basic_files.append(result['file'])
        elif result['analysis'] == 'INCOMPLETE':
            incomplete_files.append(result['file'])
        elif result['analysis'] == 'NEEDS_FIX':
            needs_fix_files.append(result['file'])
    
    # Summary
    print("\\n📋 SUMMARY:")
    print("-" * 40)
    print(f"🟢 Excellent (Full ATA fix):     {len(excellent_files)}")
    print(f"🟡 Good (Basic ATA fix):         {len(good_files)}")
    print(f"🟠 Basic (Minimal ATA logic):    {len(basic_files)}")
    print(f"🔴 Incomplete (Missing logic):   {len(incomplete_files)}")
    print(f"🔴 Needs Fix (No existence chk): {len(needs_fix_files)}")
    
    if excellent_files:
        print(f"\\n✅ EXCELLENT FILES: {', '.join(excellent_files)}")
    
    if good_files:
        print(f"\\n👍 GOOD FILES: {', '.join(good_files)}")
    
    if incomplete_files or needs_fix_files:
        print(f"\\n⚠️ FILES NEEDING ATTENTION:")
        for file in incomplete_files + needs_fix_files:
            print(f"   🔴 {file}")
        print("\\n🔧 These files should have proper ATA existence checking added!")
    
    # Check the critical pump.fun files
    critical_pump_files = [f for f in results if f['file'].startswith('pumpfun') or f['file'] == 'direct_pumpfun.py']
    critical_good = [f for f in critical_pump_files if f['analysis'] in ['EXCELLENT', 'GOOD']]
    
    print(f"\\n🎯 CRITICAL PUMP.FUN FILES STATUS:")
    print(f"   Total critical files: {len(critical_pump_files)}")
    print(f"   Properly fixed: {len(critical_good)}")
    
    if len(critical_good) == len(critical_pump_files):
        print("   ✅ ALL CRITICAL PUMP.FUN FILES HAVE ATA FIXES!")
    else:
        print("   ⚠️ Some critical pump.fun files need fixing")
    
    print("\\n" + "=" * 60)
    print("🏁 ATA Fix Verification Complete!")

if __name__ == "__main__":
    main()
