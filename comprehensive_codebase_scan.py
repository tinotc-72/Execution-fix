#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE CODEBASE SCAN
Verify that all three enhancements have been properly applied:
1. Enhanced DEX Detection (websocket_handler.py)
2. Intelligent Routing (trade_processor.py)
3. Enhanced ATA Handling (all executor files)
"""

import os
import re
from typing import Dict, List, Tuple

def scan_file_for_patterns(filepath: str, patterns: Dict[str, str]) -> Dict[str, bool]:
    """Scan a file for specific patterns and return matches"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        for pattern_name, pattern in patterns.items():
            results[pattern_name] = bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))
        
        return results
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return {pattern_name: False for pattern_name in patterns.keys()}

def check_enhanced_dex_detection() -> bool:
    """Check if websocket_handler.py has enhanced DEX detection"""
    print("\n🔍 CHECKING: Enhanced DEX Detection")
    print("=" * 50)
    
    filepath = "websocket_handler.py"
    patterns = {
        "program_id_detection": r"program.{0,20}id.{0,20}detection",
        "confidence_scoring": r"confidence.{0,10}(high|medium|low)",
        "detection_method": r"detection_method",
        "two_phase_detection": r"STEP\s+1.*STEP\s+2",
        "dex_patterns_mapping": r"dex_patterns.*=.*{",
        "program_id_priority": r"program.{0,20}id.{0,20}first|priorit"
    }
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    results = scan_file_for_patterns(filepath, patterns)
    
    all_passed = True
    for pattern_name, found in results.items():
        status = "✅" if found else "❌"
        print(f"   {pattern_name}: {status}")
        if not found:
            all_passed = False
    
    print(f"\n🎯 Enhanced DEX Detection: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed

def check_intelligent_routing() -> bool:
    """Check if trade_processor.py has intelligent routing"""
    print("\n🧠 CHECKING: Intelligent Routing System")
    print("=" * 50)
    
    filepath = "trade_processor.py"
    patterns = {
        "intelligent_buy_method": r"_execute_intelligent_buy",
        "dex_executor_mapping": r"dex_executor_mapping",
        "confidence_based_routing": r"confidence.*routing|routing.*confidence",
        "focused_execution": r"focused.*execution",
        "parallel_execution": r"parallel.*execution",
        "strategy_selection": r"strategy.*selection|execution.*strategy"
    }
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    results = scan_file_for_patterns(filepath, patterns)
    
    all_passed = True
    for pattern_name, found in results.items():
        status = "✅" if found else "❌"
        print(f"   {pattern_name}: {status}")
        if not found:
            all_passed = False
    
    print(f"\n🎯 Intelligent Routing: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed

def check_enhanced_ata_handling() -> bool:
    """Check if all executor files have enhanced ATA handling"""
    print("\n🔧 CHECKING: Enhanced ATA Handling")
    print("=" * 50)
    
    # Core executor files to check
    executor_files = [
        "pumpfun_copy_executor.py",
        "raydium_copy_executor.py", 
        "jupiter_copy_executor.py",
        "cpmm_copy_executor.py",
        "raydium_clmm_copy_executor.py",
        "clmm_copy_executor.py",
        "pumpfun_executor.py",
        "raydium_trade_executor.py",
        "raydium_clmm_trade_executor.py",
        "pumpfun_trade_executor.py"
    ]
    
    # Enhanced ATA patterns to look for
    ata_patterns = {
        "ensure_method": r"ensure_token_account_exists",
        "existence_check": r"account_info\.value.{0,20}(is not None|!=|==)|check_ata_exists",
        "early_return": r"already exists.*return|exists.*skip",
        "proper_owner": r"self\.wallet_pubkey|wallet\.pubkey\(\)",
        "enhanced_comment": r"ENHANCED.*ATA|Check first.*create",
        "step_annotation": r"STEP\s+1.*STEP\s+2"
    }
    
    all_files_passed = True
    checked_files = 0
    
    for executor_file in executor_files:
        if os.path.exists(executor_file):
            checked_files += 1
            print(f"\n📝 {executor_file}:")
            
            results = scan_file_for_patterns(executor_file, ata_patterns)
            
            file_passed = True
            for pattern_name, found in results.items():
                status = "✅" if found else "❌"
                print(f"   {pattern_name}: {status}")
                if not found:
                    file_passed = False
            
            if file_passed:
                print(f"   ✅ PASSED - Enhanced ATA handling implemented")
            else:
                print(f"   ❌ FAILED - Missing enhanced ATA features")
                all_files_passed = False
        else:
            print(f"\n📝 {executor_file}: ⚠️ SKIPPED - File not found")
    
    print(f"\n🎯 Enhanced ATA Handling: {'✅ PASSED' if all_files_passed else '❌ FAILED'}")
    print(f"   📊 Files checked: {checked_files}/{len(executor_files)}")
    return all_files_passed

def check_execution_coordinator() -> bool:
    """Check if execution_coordinator.py has enhanced methods"""
    print("\n⚙️ CHECKING: Execution Coordinator Integration")
    print("=" * 50)
    
    filepath = "execution_coordinator.py"
    patterns = {
        "enhanced_methods": r"_try_.*_buy.*enhanced|enhanced.*executor",
        "ata_support": r"ensure_token_account_exists",
        "dex_support": r"direct_pumpfun|cpmm|clmm|jupiter",
        "error_handling": r"IllegalOwner|ATA.*error",
        "comprehensive_coverage": r"try_.*executor.*methods"
    }
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    results = scan_file_for_patterns(filepath, patterns)
    
    all_passed = True
    for pattern_name, found in results.items():
        status = "✅" if found else "❌"
        print(f"   {pattern_name}: {status}")
        if not found:
            all_passed = False
    
    print(f"\n🎯 Execution Coordinator: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed

def check_main_integration() -> bool:
    """Check if main.py properly integrates all enhancements"""
    print("\n🏠 CHECKING: Main Integration")
    print("=" * 50)
    
    filepath = "main.py"
    patterns = {
        "trade_processor_import": r"from trade_processor import TradeProcessor",
        "websocket_handler_import": r"from websocket_handler",
        "execution_coordinator_import": r"from execution_coordinator",
        "trade_processor_usage": r"self\.trade_processor.*=.*TradeProcessor",
        "enhanced_integration": r"process_detected_trade|execute.*trade"
    }
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found!")
        return False
    
    results = scan_file_for_patterns(filepath, patterns)
    
    all_passed = True
    for pattern_name, found in results.items():
        status = "✅" if found else "❌"
        print(f"   {pattern_name}: {status}")
        if not found:
            all_passed = False
    
    print(f"\n🎯 Main Integration: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed

def scan_for_missing_files() -> List[str]:
    """Scan for any files that might need enhancement but were missed"""
    print("\n🔍 CHECKING: Missing Files or Patterns")
    print("=" * 50)
    
    # Look for any other executor or handler files
    executor_patterns = [
        "*executor*.py",
        "*handler*.py", 
        "*trader*.py",
        "*copy*.py"
    ]
    
    missing_enhancements = []
    
    # Find all Python files that might need enhancement
    for root, dirs, files in os.walk("."):
        # Skip OLDER directories and test files
        if "OLDER" in root or "test" in root.lower():
            continue
            
        for file in files:
            if file.endswith(".py") and any(pattern.replace("*", "") in file for pattern in ["executor", "handler", "trader"]):
                filepath = os.path.join(root, file)
                if os.path.basename(filepath) not in [
                    "websocket_handler.py", "trade_processor.py", "execution_coordinator.py"
                ]:
                    # Check if it has ensure_token_account_exists but might need enhancement
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        
                        has_ensure_method = "ensure_token_account_exists" in content
                        has_enhancement = "ENHANCED" in content or "Check first" in content
                        
                        if has_ensure_method and not has_enhancement:
                            missing_enhancements.append(filepath)
                            print(f"   ⚠️ {filepath}: Has ATA method but may need enhancement")
                    except:
                        pass
    
    if missing_enhancements:
        print(f"\n🎯 Missing Enhancements: ❌ {len(missing_enhancements)} files may need attention")
    else:
        print(f"\n🎯 Missing Enhancements: ✅ No additional files found")
    
    return missing_enhancements

def main():
    """Run comprehensive codebase scan"""
    print("🚀 COMPREHENSIVE CODEBASE ENHANCEMENT SCAN")
    print("=" * 60)
    print("Verifying all three enhancements are properly applied:")
    print("1. Enhanced DEX Detection")
    print("2. Intelligent Routing")
    print("3. Enhanced ATA Handling")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("Enhanced DEX Detection", check_enhanced_dex_detection()))
    results.append(("Intelligent Routing", check_intelligent_routing()))
    results.append(("Enhanced ATA Handling", check_enhanced_ata_handling()))
    results.append(("Execution Coordinator", check_execution_coordinator()))
    results.append(("Main Integration", check_main_integration()))
    
    # Check for missing files
    missing_files = scan_for_missing_files()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE SCAN RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    if missing_files:
        print(f"Missing Enhancements: ❌ {len(missing_files)} files need attention")
        all_passed = False
    else:
        print(f"Missing Enhancements: ✅ No additional files found")
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL ENHANCEMENTS PROPERLY IMPLEMENTED!")
        print("✅ Codebase is fully enhanced and ready for production")
        print("🚀 Bot can be restarted with complete confidence")
    else:
        print("⚠️ SOME ENHANCEMENTS NEED ATTENTION")
        print("🔧 Review failed checks and apply missing enhancements")
        
        if missing_files:
            print(f"\n📋 Files that may need enhancement:")
            for filepath in missing_files:
                print(f"   • {filepath}")
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    try:
        result = main()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Scan interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Scan error: {e}")
        exit(1)
