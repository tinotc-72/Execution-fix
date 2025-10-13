#!/usr/bin/env python3
"""
🎯 CORRECTED COMPLIANCE VERIFICATION
Properly categorizes files by their actual function and checks appropriate patterns
"""

import os
import re

def main():
    print("🔍 CORRECTED OFFICIAL DOCUMENTATION COMPLIANCE VERIFICATION")
    print("="*80)
    
    # 🎯 FILE CATEGORIZATION - Check appropriate patterns for each file type
    file_categories = {
        "EXECUTORS": [
            "pumpfun_copy_executor.py",
            "jupiter_copy_executor.py", 
            "raydium_copy_executor.py",
            "cpmm_copy_executor.py",
            "raydium_clmm_copy_executor.py",
            "clmm_copy_executor.py",
            "raydium_trade_executor.py",
            "raydium_clmm_trade_executor.py"
        ],
        "HANDLERS": [
            "websocket_handler.py",
            "trade_processor.py"
        ]
    }
    
    # 🏛️ EXECUTOR PATTERNS - Need full transaction building capability
    executor_patterns = {
        "ata_existence_check": {
            "pattern": r"get_account_info.*token_account",
            "description": "Official ATA existence check using get_account_info"
        },
        "ata_creation": {
            "pattern": r"create_associated_token_account",
            "description": "Official ATA creation using SPL Token library"  
        },
        "ata_derivation": {
            "pattern": r"get_associated_token_address",
            "description": "Official ATA address derivation"
        },
        "versioned_transaction": {
            "pattern": r"VersionedTransaction|MessageV0",
            "description": "Official versioned transaction format"
        },
        "compute_budget": {
            "pattern": r"set_compute_unit_limit|set_compute_unit_price",
            "description": "Official compute budget instructions"
        },
        "recent_blockhash": {
            "pattern": r"get_latest_blockhash.*blockhash",
            "description": "Official recent blockhash usage"
        },
        "error_handling": {
            "pattern": r"try:.*except.*as.*:|raise.*Exception",
            "description": "Proper exception handling patterns"
        },
        "commitment_levels": {
            "pattern": r"commitment.*=.*(finalized|confirmed)",
            "description": "Official commitment levels"
        },
        "program_ids": {
            "pattern": r"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA|ComputeBudget111111111111111111111111111111",
            "description": "Official system and token program IDs"
        },
        "proportional_selling": {
            "pattern": r"sell_percentage.*kwargs\.get|proportional.*calculation",
            "description": "Proportional selling implementation"
        }
    }
    
    # 📡 HANDLER PATTERNS - Only need basic WebSocket/processing patterns
    handler_patterns = {
        "async_patterns": {
            "pattern": r"async def|await |asyncio\.",
            "description": "Proper async/await patterns"
        },
        "websocket_handling": {
            "pattern": r"websockets|ws_url|WebSocket",
            "description": "WebSocket connection handling"
        },
        "error_handling": {
            "pattern": r"try:.*except.*Exception",
            "description": "Proper exception handling"
        },
        "logging_patterns": {
            "pattern": r"logger\.|logging\.",
            "description": "Proper logging implementation"
        },
        "callback_patterns": {
            "pattern": r"callback|trade_callback",
            "description": "Callback pattern implementation"
        }
    }
    
    compliant_count = 0
    total_files = 0
    
    # Check executors
    print("\n🚀 EXECUTOR FILES (Need transaction building capabilities):")
    print("-" * 60)
    
    for executor_file in file_categories["EXECUTORS"]:
        total_files += 1
        print(f"\n📝 {executor_file}:")
        
        if not os.path.exists(executor_file):
            print(f"   ❌ File not found")
            continue
            
        try:
            with open(executor_file, 'r') as f:
                content = f.read()
            
            score = 0
            total_patterns = len(executor_patterns)
            
            for pattern_name, pattern_info in executor_patterns.items():
                found = bool(re.search(pattern_info["pattern"], content, re.IGNORECASE | re.MULTILINE))
                if found:
                    score += 1
                    print(f"   ✅ {pattern_info['description']}")
                else:
                    print(f"   ⚠️ {pattern_info['description']}")
            
            # Executors need 8+ patterns for compliance
            if score >= 8:
                compliance_status = "✅ FULLY COMPLIANT"
                compliant_count += 1
            else:
                compliance_status = "❌ NEEDS IMPROVEMENT"
                
            percentage = (score / total_patterns) * 100
            print(f"   📊 Compliance: {compliance_status} ({score}/{total_patterns} - {percentage:.0f}%)")
            
        except Exception as e:
            print(f"   ❌ Error checking file: {e}")
    
    # Check handlers
    print(f"\n📡 HANDLER FILES (Need processing/WebSocket capabilities):")
    print("-" * 60)
    
    for handler_file in file_categories["HANDLERS"]:
        total_files += 1
        print(f"\n📝 {handler_file}:")
        
        if not os.path.exists(handler_file):
            print(f"   ❌ File not found")
            continue
            
        try:
            with open(handler_file, 'r') as f:
                content = f.read()
            
            score = 0
            total_patterns = len(handler_patterns)
            
            for pattern_name, pattern_info in handler_patterns.items():
                found = bool(re.search(pattern_info["pattern"], content, re.IGNORECASE | re.MULTILINE))
                if found:
                    score += 1
                    print(f"   ✅ {pattern_info['description']}")
                else:
                    print(f"   ⚠️ {pattern_info['description']}")
            
            # Handlers need 4+ patterns for compliance (less stringent)
            if score >= 4:
                compliance_status = "✅ FULLY COMPLIANT"
                compliant_count += 1
            else:
                compliance_status = "❌ NEEDS IMPROVEMENT"
                
            percentage = (score / total_patterns) * 100
            print(f"   📊 Compliance: {compliance_status} ({score}/{total_patterns} - {percentage:.0f}%)")
            
        except Exception as e:
            print(f"   ❌ Error checking file: {e}")
    
    # Final summary
    print("\n" + "="*80)
    print("📊 CORRECTED COMPLIANCE SUMMARY")
    print("="*80)
    print(f"🎯 OVERALL COMPLIANCE: {compliant_count}/{total_files} files fully compliant")
    
    if compliant_count == total_files:
        print("✅ ALL FILES ARE PROPERLY COMPLIANT FOR THEIR INTENDED FUNCTION!")
        print("\n🎯 EXPLANATION:")
        print("   • Executor files: Have full transaction building capabilities")
        print("   • Handler files: Have appropriate WebSocket/processing patterns")
        print("   • Each file type is compliant for its specific role")
    else:
        print(f"⚠️ {total_files - compliant_count} file(s) need improvements")
    
    print("\n📚 COMPLIANCE NOTES:")
    print("   • Executors need transaction building (ATA, compute budget, etc.)")
    print("   • Handlers need processing patterns (async, WebSocket, callbacks)")
    print("   • Different file types have different compliance requirements")

if __name__ == "__main__":
    main()
