#!/usr/bin/env python3
"""
🔍 PROPORTIONAL SELLING SCAN
Check if all 8 core executors have proportional selling implemented
"""

import os
import re

def check_proportional_selling():
    """Check each executor for proportional selling support"""
    print("🔍 SCANNING FOR PROPORTIONAL SELLING IMPLEMENTATION")
    print("=" * 70)
    
    # The 8 core executor files to check
    executor_files = [
        "pumpfun_copy_executor.py",
        "jupiter_copy_executor.py", 
        "raydium_copy_executor.py",
        "cpmm_copy_executor.py",
        "raydium_clmm_copy_executor.py",
        "clmm_copy_executor.py",
        "raydium_trade_executor.py",
        "raydium_clmm_trade_executor.py"
    ]
    
    # Also check the wrapper file that might have proportional logic
    wrapper_file = "official_executor_wrappers.py"
    
    results = {}
    
    for executor_file in executor_files:
        print(f"\n📝 {executor_file}:")
        
        if not os.path.exists(executor_file):
            print(f"   ❌ File not found")
            results[executor_file] = False
            continue
        
        try:
            with open(executor_file, 'r') as f:
                content = f.read()
            
            # Check for proportional selling patterns
            patterns = {
                "sell_percentage_param": r"sell_percentage",
                "proportional_calculation": r"sell_percentage.*100|100.*sell_percentage|token_balance.*sell_percentage|sell_percentage.*token_balance",
                "percentage_validation": r"sell_percentage.*100|sell_percentage.*<=.*0|sell_percentage.*>.*100",
                "sell_method": r"execute_sell|sell_copy",
                "kwargs_sell_percentage": r"kwargs\.get.*sell_percentage"
            }
            
            found_patterns = {}
            for pattern_name, pattern in patterns.items():
                found_patterns[pattern_name] = bool(re.search(pattern, content, re.IGNORECASE))
            
            # Analyze results
            has_sell_percentage = found_patterns["sell_percentage_param"]
            has_calculation = found_patterns["proportional_calculation"] 
            has_validation = found_patterns["percentage_validation"]
            has_sell_method = found_patterns["sell_method"]
            has_kwargs = found_patterns["kwargs_sell_percentage"]
            
            print(f"   sell_percentage parameter: {'✅' if has_sell_percentage else '❌'}")
            print(f"   Proportional calculation: {'✅' if has_calculation else '❌'}")
            print(f"   Percentage validation: {'✅' if has_validation else '❌'}")
            print(f"   Sell method: {'✅' if has_sell_method else '❌'}")
            print(f"   kwargs.get support: {'✅' if has_kwargs else '❌'}")
            
            # Determine if proportional selling is implemented
            has_proportional = (has_sell_percentage and has_calculation) or (has_kwargs and has_sell_method)
            
            if has_proportional:
                print(f"   Overall: ✅ PROPORTIONAL SELLING IMPLEMENTED")
                results[executor_file] = True
            else:
                print(f"   Overall: ❌ MISSING PROPORTIONAL SELLING")
                results[executor_file] = False
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            results[executor_file] = False
    
    # Check wrapper file for additional proportional support
    print(f"\n📝 {wrapper_file} (Wrapper Functions):")
    
    if os.path.exists(wrapper_file):
        try:
            with open(wrapper_file, 'r') as f:
                content = f.read()
            
            # Look for wrapper functions with proportional support
            wrapper_functions = [
                "try_jupiter_sell_all",
                "try_cpmm_sell_all", 
                "try_clmm_sell_all",
                "try_orca_sell_all",
                "try_pumpfun_sell_all"
            ]
            
            wrapper_results = {}
            for func_name in wrapper_functions:
                # Check if this function has proportional selling
                func_pattern = rf"async def {func_name}.*?(?=async def|\Z)"
                func_match = re.search(func_pattern, content, re.DOTALL)
                
                if func_match:
                    func_content = func_match.group(0)
                    has_proportional = ("sell_percentage" in func_content and 
                                      ("100.0" in func_content or "percentage" in func_content))
                    wrapper_results[func_name] = has_proportional
                    print(f"   {func_name}: {'✅' if has_proportional else '❌'}")
                else:
                    wrapper_results[func_name] = False
                    print(f"   {func_name}: ❌ (not found)")
            
        except Exception as e:
            print(f"   ❌ Error reading wrapper file: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 PROPORTIONAL SELLING SUMMARY:")
    print("=" * 70)
    
    implemented_count = sum(1 for has_it in results.values() if has_it)
    total_count = len(results)
    
    for executor_file, has_proportional in results.items():
        status = "✅ IMPLEMENTED" if has_proportional else "❌ MISSING"
        print(f"{executor_file}: {status}")
    
    print("=" * 70)
    if implemented_count == total_count:
        print("🎉 ALL EXECUTORS HAVE PROPORTIONAL SELLING!")
        print("✅ Complete proportional selling coverage across all executors")
    else:
        missing_count = total_count - implemented_count
        print(f"⚠️ PROPORTIONAL SELLING STATUS: {implemented_count}/{total_count} executors")
        print(f"🔧 {missing_count} executor(s) need proportional selling implementation")
        
        # List the missing ones
        print(f"\n📋 Missing proportional selling:")
        for executor_file, has_proportional in results.items():
            if not has_proportional:
                print(f"   • {executor_file}")
    
    print("=" * 70)
    return implemented_count == total_count

if __name__ == "__main__":
    check_proportional_selling()
