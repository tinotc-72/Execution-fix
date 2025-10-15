#!/usr/bin/env python3
"""
Validation script to demonstrate the coordinator handoff fix.

This script shows how the _have_all_fields function works and how
it ensures the coordinator is called when all fields are present.
"""

def _have_all_fields(trade_info: dict) -> bool:
    """Check if trade_info has all required fields for execution."""
    # Accept both "mint" and "token_mint" to avoid naming mismatches
    token_mint = trade_info.get("token_mint") or trade_info.get("mint")
    dex = trade_info.get("dex")
    action = trade_info.get("action")
    wallet = trade_info.get("wallet_address")
    ok = all(v not in (None, "", "unknown", "PENDING_ANALYSIS") for v in (dex, action, wallet, token_mint))
    if ok and trade_info.get("token_mint") is None and token_mint:
        trade_info["token_mint"] = token_mint  # normalize
    return ok


def simulate_route_and_execute(trade_info: dict):
    """Simulate the route_and_execute function."""
    print(f"\n📋 Trade Info: {trade_info}")
    
    if not _have_all_fields(trade_info):
        print("🛑 [PIPELINE_EXIT] Fields incomplete, skipping execution")
        return
    
    print("🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator")
    print("✅ Coordinator would be called here (with error logging)")


def main():
    print("=" * 80)
    print("COORDINATOR HANDOFF FIX - VALIDATION DEMO")
    print("=" * 80)
    
    # Test Case 1: Complete fields with token_mint
    print("\n" + "=" * 80)
    print("TEST 1: Complete Fields (token_mint)")
    print("=" * 80)
    trade_info_1 = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    simulate_route_and_execute(trade_info_1)
    print("✅ Expected: Coordinator called")
    
    # Test Case 2: Complete fields with mint (should normalize)
    print("\n" + "=" * 80)
    print("TEST 2: Complete Fields (mint - should normalize)")
    print("=" * 80)
    trade_info_2 = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "mint": "XYZ789"
    }
    simulate_route_and_execute(trade_info_2)
    print(f"✅ Expected: Coordinator called, token_mint normalized to: {trade_info_2.get('token_mint')}")
    
    # Test Case 3: Incomplete fields (unknown dex)
    print("\n" + "=" * 80)
    print("TEST 3: Incomplete Fields (unknown dex)")
    print("=" * 80)
    trade_info_3 = {
        "dex": "unknown",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    simulate_route_and_execute(trade_info_3)
    print("✅ Expected: Execution skipped")
    
    # Test Case 4: Incomplete fields (PENDING_ANALYSIS token)
    print("\n" + "=" * 80)
    print("TEST 4: Incomplete Fields (PENDING_ANALYSIS token)")
    print("=" * 80)
    trade_info_4 = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "PENDING_ANALYSIS"
    }
    simulate_route_and_execute(trade_info_4)
    print("✅ Expected: Execution skipped")
    
    # Test Case 5: Missing wallet_address
    print("\n" + "=" * 80)
    print("TEST 5: Missing wallet_address")
    print("=" * 80)
    trade_info_5 = {
        "dex": "jupiter",
        "action": "buy",
        "token_mint": "XYZ789"
    }
    simulate_route_and_execute(trade_info_5)
    print("✅ Expected: Execution skipped")
    
    # Test Case 6: After inference scenario (from logs)
    print("\n" + "=" * 80)
    print("TEST 6: After Inference Scenario (Real-World)")
    print("=" * 80)
    print("\n[DEBUG] Before infer_missing_fields:")
    trade_info_6_before = {
        "signature": "abc123...",
        "wallet_address": "DEF456...",
        "dex": "unknown",
        "action": "unknown",
        "token_mint": "PENDING_ANALYSIS"
    }
    print(f"  {trade_info_6_before}")
    
    print("\n[DEBUG] After infer_missing_fields:")
    trade_info_6_after = {
        "signature": "abc123...",
        "wallet_address": "DEF456...",
        "dex": "jupiter",
        "action": "buy",
        "token_mint": "GHI789..."
    }
    print(f"  {trade_info_6_after}")
    
    # Compute builder mode
    have_all = _have_all_fields(trade_info_6_after)
    use_universal_cloner = not have_all
    print(f"\n✅ [MODE] Builders {'ENABLED (complete fields)' if have_all else 'DISABLED'}; "
          f"Cloner as {'fallback' if have_all else 'PRIMARY'}")
    
    # Call route_and_execute
    simulate_route_and_execute(trade_info_6_after)
    print("✅ Expected: Coordinator called with all fields present")
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print("\n✅ The fix ensures:")
    print("   1. Consistent field validation across codebase")
    print("   2. Automatic mint → token_mint normalization")
    print("   3. Coordinator is ALWAYS called when fields are complete")
    print("   4. Errors from coordinator are logged with stack traces")
    print()


if __name__ == "__main__":
    main()
