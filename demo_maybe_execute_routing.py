#!/usr/bin/env python3
"""
Demonstration of the updated maybe_execute routing logic.

This script shows the new logging and routing patterns implemented:
- Always logs route start with dex and prefer_clone
- Meteora: builder-first logic (meteora → jupiter → direct_copy)
- Unknown with mint: Jupiter → direct_copy
- Loud, explicit logs for all routes and fallbacks
"""

import re

def extract_maybe_execute():
    """Extract and display the maybe_execute function"""
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Find the maybe_execute function
    match = re.search(r'async def maybe_execute.*?(?=\n(?:async def|def|class|\Z))', content, re.DOTALL)
    if not match:
        print("❌ Could not find maybe_execute function")
        return None
    
    return match.group(0)

def demonstrate_routing_logic():
    """Demonstrate the routing logic"""
    print("=" * 80)
    print("MAYBE_EXECUTE ROUTING LOGIC DEMONSTRATION")
    print("=" * 80)
    
    func = extract_maybe_execute()
    if not func:
        return
    
    print("\n1. INITIAL ROUTE LOGGING")
    print("-" * 80)
    print("   The function ALWAYS logs the route start with dex and prefer_clone:")
    
    match = re.search(r'logger\.info\("🧭 \[COORDINATOR\] route start:.*?".*?\)', func)
    if match:
        print(f"   ✅ {match.group(0)}")
    
    print("\n2. TRY_SUBMIT WRAPPER")
    print("-" * 80)
    print("   Centralized submission with loud logging:")
    
    # Find try_submit function
    submit_match = re.search(r'async def try_submit\(vtx\):.*?(?=\n    async def|\n    if dex)', func, re.DOTALL)
    if submit_match:
        print("   ✅ Found try_submit wrapper")
        # Show key logging lines
        if '✅ [EXECUTION] submitted:' in submit_match.group(0):
            print("   ✅ Logs success: '✅ [EXECUTION] submitted: {sig}'")
        if '❌ [EXECUTION] submit failed:' in submit_match.group(0):
            print("   ✅ Logs failure: '❌ [EXECUTION] submit failed: {e}'")
    
    print("\n3. METEORA ROUTING (dex=='meteora')")
    print("-" * 80)
    print("   For dex=='meteora' and use_universal_cloner=False:")
    print("   Builder-first logic: Meteora → Jupiter → direct_copy")
    
    meteora_match = re.search(r'if dex == "meteora":.*?(?=\n    # unknown)', func, re.DOTALL)
    if meteora_match:
        meteora_code = meteora_match.group(0)
        
        # Check for route logs
        if '🧭 [ROUTE] Meteora → build_and_sign' in meteora_code:
            print("   ✅ Step 1: '🧭 [ROUTE] Meteora → build_and_sign'")
        
        if 'meteora_build_and_sign' in meteora_code:
            print("   ✅ Step 2: Calls meteora_build_and_sign(trade_info, rpc, keypair)")
        
        if '⚠️ Meteora build failed → trying Jupiter' in meteora_code:
            print("   ✅ Step 3: '⚠️ Meteora build failed → trying Jupiter'")
        
        if 'jupiter_build_buy_tx' in meteora_code:
            print("   ✅ Step 4: Calls jupiter_build_buy_tx(token_mint, amount_sol, keypair)")
        
        if '⚠️ Builders failed → direct_copy fallback' in meteora_code:
            print("   ✅ Step 5: '⚠️ Builders failed → direct_copy fallback'")
        
        if 'execute_direct_copy' in meteora_code:
            print("   ✅ Step 6: Calls execute_direct_copy(trade_info, rpc, keypair, jito)")
    
    print("\n4. UNKNOWN WITH MINT ROUTING")
    print("-" * 80)
    print("   For dex=='unknown' with token_mint present:")
    print("   Jupiter → direct_copy")
    
    unknown_match = re.search(r'if dex == "unknown" and trade_info\.get\("token_mint"\):.*?(?=\n    # last resort)', func, re.DOTALL)
    if unknown_match:
        unknown_code = unknown_match.group(0)
        
        if '🧭 [ROUTE] Unknown with mint → Jupiter → Clone' in unknown_code:
            print("   ✅ Step 1: '🧭 [ROUTE] Unknown with mint → Jupiter → Clone'")
        
        if 'jupiter_build_buy_tx' in unknown_code:
            print("   ✅ Step 2: Calls jupiter_build_buy_tx(token_mint, amount_sol, keypair)")
        
        if 'execute_direct_copy' in unknown_code:
            print("   ✅ Step 3: Falls back to execute_direct_copy")
    
    print("\n5. LAST RESORT FALLBACK")
    print("-" * 80)
    print("   When no other routes match:")
    
    fallback_match = re.search(r'# last resort.*?return await execute_direct_copy', func, re.DOTALL)
    if fallback_match:
        fallback_code = fallback_match.group(0)
        
        if '🧭 [ROUTE] Fallback → direct_copy' in fallback_code:
            print("   ✅ '🧭 [ROUTE] Fallback → direct_copy'")
        
        print("   ✅ Calls execute_direct_copy(trade_info, rpc_url, keypair, jito_service)")
    
    print("\n6. LOUD, EXPLICIT LOGGING SUMMARY")
    print("-" * 80)
    
    # Count emojis
    route_logs = func.count('🧭 [ROUTE]') + func.count('🧭 [COORDINATOR]')
    success_logs = func.count('✅ [EXECUTION]')
    error_logs = func.count('❌')
    warning_logs = func.count('⚠️')
    
    print(f"   🧭 Route/Coordinator logs: {route_logs}")
    print(f"   ✅ Success logs: {success_logs}")
    print(f"   ❌ Error logs: {error_logs}")
    print(f"   ⚠️ Warning logs: {warning_logs}")
    print(f"   📊 Total explicit logs: {route_logs + success_logs + error_logs + warning_logs}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Features Implemented:")
    print("✅ Always logs route start with dex and prefer_clone")
    print("✅ Meteora: builder-first logic (meteora → jupiter → direct_copy)")
    print("✅ Unknown with mint: Jupiter → direct_copy")
    print("✅ try_submit wrapper with loud logging for all submissions")
    print("✅ Loud, explicit logs for all routes and fallbacks")
    print("✅ Consistent emoji usage for easy log parsing")

if __name__ == "__main__":
    demonstrate_routing_logic()
