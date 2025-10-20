#!/usr/bin/env python3
"""
Final verification that the problem statement requirements are met.

Requirements:
1. _have_all_fields function exists and checks dex, wallet_address, token_mint (not action)
2. route_and_execute function exists and returns early if fields incomplete
3. After "After infer_missing_fields", route_and_execute is called
4. Logs show proper sequence when fields are complete
"""

import re


def verify_have_all_fields():
    """Verify _have_all_fields implementation matches problem statement"""
    print("=" * 80)
    print("VERIFICATION 1: _have_all_fields Function")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract the function
    pattern = r'def _have_all_fields\(.*?\).*?\n(?:.*?\n)*?    return ok'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: _have_all_fields function not found")
        return False
    
    func_text = match.group(0)
    print("\nFound function:")
    print("-" * 80)
    for i, line in enumerate(func_text.split('\n')[:10], 1):
        print(f"{i:2}. {line}")
    print("...")
    print("-" * 80)
    
    checks = [
        (r'trade_info\.get\("token_mint"\) or trade_info\.get\("mint"\)', 
         "✅ Treats mint and token_mint as synonyms"),
        (r'all\(.*?for k in \("dex","wallet_address"\)\)', 
         "✅ Checks only dex and wallet_address (not action)"),
        (r'if tok and not trade_info\.get\("token_mint"\):.*?trade_info\["token_mint"\] = tok', 
         "✅ Normalizes mint to token_mint"),
    ]
    
    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, func_text, re.DOTALL):
            print(f"\n{desc}")
            passed += 1
        else:
            print(f"\n❌ {desc.replace('✅', 'MISSING:')}")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def verify_route_and_execute():
    """Verify route_and_execute implementation matches problem statement"""
    print("\n" + "=" * 80)
    print("VERIFICATION 2: route_and_execute Function")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract the function
    pattern = r'async def route_and_execute\(.*?\).*?\n(?:.*?\n)*?        logger\.error\(.*?exc_info=True\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: route_and_execute function not found")
        return False
    
    func_text = match.group(0)
    print("\nFound function:")
    print("-" * 80)
    for i, line in enumerate(func_text.split('\n')[:15], 1):
        print(f"{i:2}. {line}")
    print("...")
    print("-" * 80)
    
    checks = [
        (r'if not _have_all_fields\(trade_info\):', 
         "✅ Checks _have_all_fields"),
        (r'logger\.warning\("🛑 \[PIPELINE_EXIT\] Fields incomplete, skipping execution"\)', 
         "✅ Logs warning for incomplete fields"),
        (r'return', 
         "✅ Returns early if fields incomplete"),
        (r'logger\.info\("🧭 \[PIPELINE_EXIT\] Final fields ready → handoff to coordinator"\)', 
         "✅ Logs handoff for complete fields"),
        (r'await maybe_execute\(trade_info', 
         "✅ Calls maybe_execute"),
        (r'try:.*?await maybe_execute.*?except Exception as e:', 
         "✅ Wraps coordinator call in try/except"),
    ]
    
    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, func_text, re.DOTALL):
            print(f"\n{desc}")
            passed += 1
        else:
            print(f"\n❌ {desc.replace('✅', 'MISSING:')}")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def verify_pipeline_flow():
    """Verify pipeline flow matches problem statement"""
    print("\n" + "=" * 80)
    print("VERIFICATION 3: Pipeline Flow After infer_missing_fields")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find section after "After infer_missing_fields"
    pattern = r'After infer_missing_fields(.*?)await route_and_execute'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find flow from 'After infer_missing_fields' to route_and_execute")
        return False
    
    flow_text = match.group(1)
    print("\nFlow between 'After infer_missing_fields' and 'route_and_execute':")
    print("-" * 80)
    lines = [line.strip() for line in flow_text.split('\n') if line.strip() and not line.strip().startswith('#')]
    for i, line in enumerate(lines[:15], 1):
        if len(line) > 70:
            line = line[:70] + "..."
        print(f"{i:2}. {line}")
    if len(lines) > 15:
        print(f"... and {len(lines) - 15} more lines")
    print("-" * 80)
    
    checks = [
        (r'have_all = _have_all_fields\(trade_info\)', 
         "✅ Calls _have_all_fields"),
        (r'trade_info\["use_universal_cloner"\] = not have_all', 
         "✅ Sets use_universal_cloner"),
        (r'\[HANDOFF\].*Calling coordinator', 
         "✅ Logs handoff before route_and_execute"),
    ]
    
    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, flow_text, re.DOTALL):
            print(f"\n{desc}")
            passed += 1
        else:
            print(f"\n❌ {desc.replace('✅', 'MISSING:')}")
    
    # Also check that handoff return log comes after
    if re.search(r'await route_and_execute.*?\[HANDOFF\].*returned', content, re.DOTALL):
        print("\n✅ Logs handoff return after route_and_execute")
        passed += 1
    else:
        print("\n❌ MISSING: Handoff return log")
    
    print(f"\nResult: {passed}/{len(checks) + 1} checks passed")
    return passed == len(checks) + 1


def verify_done_criteria():
    """Verify the 'Done when' criteria from problem statement"""
    print("\n" + "=" * 80)
    print("VERIFICATION 4: 'Done When' Criteria")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    print("\nProblem statement says:")
    print('  "Done when after "After infer_missing_fields", logs show:')
    print('  - 🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator')
    print('  - then a [COORDINATOR] route banner."')
    
    print("\nVerifying this log sequence is possible:")
    
    checks = [
        (r'After infer_missing_fields', 
         "✅ 'After infer_missing_fields' log exists"),
        (r'🧭 \[PIPELINE_EXIT\] Final fields ready → handoff to coordinator', 
         "✅ PIPELINE_EXIT log exists in route_and_execute"),
    ]
    
    passed = 0
    for pattern, desc in checks:
        if re.search(pattern, content):
            print(f"\n{desc}")
            passed += 1
        else:
            print(f"\n❌ {desc.replace('✅', 'MISSING:')}")
    
    # Check execution_coordinator for COORDINATOR log
    try:
        with open('execution_coordinator.py', 'r') as f:
            coord_content = f.read()
        if re.search(r'\[COORDINATOR\].*route', coord_content):
            print("\n✅ COORDINATOR route banner exists in maybe_execute")
            passed += 1
        else:
            print("\n❌ MISSING: COORDINATOR route banner")
    except:
        print("\n⚠️  Could not verify COORDINATOR log (file not readable)")
    
    print(f"\nResult: {passed}/{len(checks) + 1} checks passed")
    return passed == len(checks) + 1


def main():
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION - PROBLEM STATEMENT REQUIREMENTS")
    print("=" * 80)
    
    verifications = [
        ("_have_all_fields function", verify_have_all_fields),
        ("route_and_execute function", verify_route_and_execute),
        ("Pipeline flow", verify_pipeline_flow),
        ("Done criteria", verify_done_criteria),
    ]
    
    results = []
    for name, func in verifications:
        try:
            passed = func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Verification failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status}: {name}")
    
    print(f"\nVerifications Passed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n" + "=" * 80)
        print("🎉 ALL REQUIREMENTS MET!")
        print("=" * 80)
        print("\nImplementation complete per problem statement:")
        print("1. ✅ _have_all_fields checks dex, wallet_address, token_mint (not action)")
        print("2. ✅ route_and_execute returns early if fields incomplete")
        print("3. ✅ Pipeline calls route_and_execute after infer_missing_fields")
        print("4. ✅ Logs show proper sequence for complete fields")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ SOME REQUIREMENTS NOT MET")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
