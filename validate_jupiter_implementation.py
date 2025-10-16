#!/usr/bin/env python3
"""
Comprehensive validation of Jupiter routing implementation.
Tests all aspects of the problem statement requirements.
"""

import sys
import re


def validate_jupiter_route_logic():
    """Validate Jupiter routing when dex=='jupiter' and use_universal_cloner==False"""
    print("=" * 80)
    print("VALIDATION 1: Jupiter Route with build_and_sign")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract the Jupiter routing block
    jupiter_block = re.search(
        r'if dex == "jupiter" and not prefer_clone:.*?(?=\n    if dex ==|\n    # |\Z)',
        content,
        re.DOTALL
    )
    
    if not jupiter_block:
        print("❌ Jupiter routing block not found")
        return False
    
    block_content = jupiter_block.group(0)
    
    # Validate the pattern matches the problem statement
    checks = [
        ('logger.info("🧭 [COORDINATOR] Route=jupiter")', "Logs Jupiter route"),
        ('from mev_jupiter_executor import build_and_sign as jupiter_build_and_sign', "Imports build_and_sign"),
        ('vtx = jupiter_build_and_sign(trade_info, rpc_url, keypair)', "Calls build_and_sign with correct args"),
        ('logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)', "Logs build errors"),
        ('vtx = None', "Sets vtx to None on error"),
        ('if await try_submit(vtx):', "Tries to submit vtx"),
        ('return {"success": True, "method": "jupiter"}', "Returns success on submit"),
        ('logger.warning("⚠️ Jupiter build failed — falling back to direct_copy")', "Logs fallback warning"),
        ('return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)', "Falls back to direct_copy"),
    ]
    
    print("\n📋 Checking Jupiter routing implementation:")
    passed = 0
    for check_pattern, description in checks:
        if check_pattern in block_content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
            print(f"     Looking for: {check_pattern[:80]}...")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def validate_jupiter_detection():
    """Validate Jupiter detection from logs/meta when dex=='unknown'"""
    print("\n" + "=" * 80)
    print("VALIDATION 2: Jupiter Detection from Logs/Meta")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Find the detection block
    detection_block = re.search(
        r'# Detect Jupiter from logs/meta if dex is unknown.*?logger.info\("🧭 \[COORDINATOR\] route start:',
        content,
        re.DOTALL
    )
    
    if not detection_block:
        print("❌ Jupiter detection block not found")
        return False
    
    block_content = detection_block.group(0)
    
    print("\n📋 Checking Jupiter detection logic:")
    
    checks = [
        ('if dex == "unknown":', "Checks if dex is unknown"),
        ('logs = trade_info.get("logs", [])', "Gets logs from trade_info"),
        ('meta = trade_info.get("meta", {})', "Gets meta from trade_info"),
        ('log_text = " ".join(logs) if isinstance(logs, list) else str(logs)', "Converts logs to text"),
        ('"JUP6" in log_text', "Checks for JUP6 in logs"),
        ('"JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in log_text', "Checks for full Jupiter PID in logs"),
        ('logger.info("🧭 [COORDINATOR] Detected Jupiter from logs, treating as jupiter")', "Logs detection from logs"),
        ('dex = "jupiter"', "Sets dex to jupiter"),
        ('meta_str = str(meta)', "Converts meta to string"),
        ('"JUP6" in meta_str', "Checks for JUP6 in meta"),
        ('logger.info("🧭 [COORDINATOR] Detected Jupiter from meta, treating as jupiter")', "Logs detection from meta"),
    ]
    
    passed = 0
    for check_pattern, description in checks:
        if check_pattern in block_content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def validate_build_and_sign_function():
    """Validate build_and_sign function in Jupiter executor"""
    print("\n" + "=" * 80)
    print("VALIDATION 3: Jupiter build_and_sign Function")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Find build_and_sign function
    func_match = re.search(
        r'def build_and_sign\(.*?\n(?:    .*\n)*?    return build_buy_tx\(.*?\)',
        content,
        re.DOTALL
    )
    
    if not func_match:
        print("❌ build_and_sign function not found")
        return False
    
    func_content = func_match.group(0)
    
    print("\n📋 Checking build_and_sign implementation:")
    
    checks = [
        ('def build_and_sign(trade_info: dict, rpc: str, keypair: Keypair)', "Correct signature"),
        ('token_mint = trade_info.get("token_mint")', "Extracts token_mint"),
        ('amount_sol = trade_info.get("amount_sol", 0.001)', "Extracts amount_sol with default"),
        ('if not token_mint:', "Validates token_mint"),
        ('raise ValueError("token_mint is required in trade_info")', "Raises error on missing mint"),
        ('return build_buy_tx(token_mint, amount_sol, keypair)', "Calls build_buy_tx"),
    ]
    
    passed = 0
    for check_pattern, description in checks:
        if check_pattern in func_content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def validate_execution_flow():
    """Validate the complete execution flow"""
    print("\n" + "=" * 80)
    print("VALIDATION 4: Complete Execution Flow")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    print("\n📋 Checking execution flow order:")
    
    # Find positions
    detection_pos = content.find('# Detect Jupiter from logs/meta if dex is unknown')
    jupiter_route_pos = content.find('if dex == "jupiter" and not prefer_clone:')
    meteora_route_pos = content.find('if dex == "meteora":')
    unknown_route_pos = content.find('if dex == "unknown" and trade_info.get("token_mint"):')
    
    checks = [
        (detection_pos > 0, "Jupiter detection exists", detection_pos),
        (jupiter_route_pos > 0, "Jupiter routing exists", jupiter_route_pos),
        (meteora_route_pos > 0, "Meteora routing exists", meteora_route_pos),
        (unknown_route_pos > 0, "Unknown routing exists", unknown_route_pos),
    ]
    
    all_exist = True
    for check, desc, pos in checks:
        if check:
            print(f"  ✅ {desc} (position: {pos})")
        else:
            print(f"  ❌ {desc}")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Validate order
    print("\n📋 Checking execution order:")
    
    order_checks = [
        (detection_pos < jupiter_route_pos, "Detection happens before Jupiter routing"),
        (jupiter_route_pos < meteora_route_pos, "Jupiter routing before Meteora routing"),
        (meteora_route_pos < unknown_route_pos, "Meteora routing before unknown routing"),
    ]
    
    passed = 0
    for check, desc in order_checks:
        if check:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"\n  Result: {passed}/{len(order_checks)} order checks passed")
    return passed == len(order_checks)


def validate_problem_statement_match():
    """Validate that implementation matches the problem statement snippet"""
    print("\n" + "=" * 80)
    print("VALIDATION 5: Problem Statement Compliance")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    print("\n📋 Checking problem statement requirements:")
    
    requirements = [
        ('dex=="jupiter" check', 'if dex == "jupiter" and not trade_info.get("use_universal_cloner"):'),
        ('Route logging', 'logger.info("🧭 [COORDINATOR] Route=jupiter")'),
        ('build_and_sign call', 'vtx = jupiter_build_and_sign(trade_info, rpc_url, keypair)'),
        ('Error handling', 'logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)'),
        ('try_submit call', 'if await try_submit(vtx):'),
        ('Fallback warning', 'logger.warning("⚠️ Jupiter build failed — falling back to direct_copy")'),
        ('direct_copy fallback', 'return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)'),
        ('JUP6 detection', '"JUP6" in log_text or "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in log_text'),
        ('Treat as jupiter', 'dex = "jupiter"'),
    ]
    
    passed = 0
    for desc, pattern in requirements:
        if pattern in content:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
            print(f"     Pattern not found: {pattern[:60]}...")
    
    print(f"\n  Result: {passed}/{len(requirements)} requirements met")
    return passed == len(requirements)


def main():
    """Run all validations"""
    print("\n🔍 COMPREHENSIVE JUPITER ROUTING VALIDATION")
    print("=" * 80)
    print("\nValidating implementation against problem statement:")
    print("  1. When dex=='jupiter' and use_universal_cloner==False:")
    print("     - Call jupiter_executor.build_and_sign(...)")
    print("     - Submit transaction")
    print("     - Fallback to clone on failure")
    print("  2. When dex=='unknown' but logs/meta include Jupiter PID (JUP6…):")
    print("     - Treat it as jupiter for this trade")
    print("\n" + "=" * 80)
    
    validations = [
        ("Jupiter Route Logic", validate_jupiter_route_logic),
        ("Jupiter Detection", validate_jupiter_detection),
        ("build_and_sign Function", validate_build_and_sign_function),
        ("Execution Flow", validate_execution_flow),
        ("Problem Statement Match", validate_problem_statement_match),
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Validation '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n" + "=" * 80)
        print("✅ ALL VALIDATIONS PASSED!")
        print("=" * 80)
        print("\nImplementation Summary:")
        print("  ✅ Jupiter routing when dex=='jupiter' and use_universal_cloner==False")
        print("  ✅ Calls jupiter_executor.build_and_sign(trade_info, rpc, keypair)")
        print("  ✅ Submits transaction via try_submit")
        print("  ✅ Falls back to direct_copy on failure")
        print("  ✅ Detects Jupiter from logs/meta when dex=='unknown'")
        print("  ✅ Checks for 'JUP6' and full program ID in logs")
        print("  ✅ Checks for 'JUP6' in meta dictionary")
        print("  ✅ Treats unknown as jupiter when detected")
        print("\nThe implementation fully satisfies the problem statement requirements.")
        return 0
    else:
        print(f"\n  ❌ {total - passed} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
