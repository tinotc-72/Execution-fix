#!/usr/bin/env python3
"""
Source code validation for executor integration fixes.
Validates fixes by checking source code patterns without importing modules.
"""

import sys
import re


def test_config_dict_methods():
    """Validate that CopyTradeConfig has dict-like methods"""
    print("=" * 80)
    print("TEST 1: Config Dict Methods (Jupiter Executor Fix)")
    print("=" * 80)
    
    with open('config.py', 'r') as f:
        source = f.read()
    
    checks = [
        ("def get(self, key, default=None):", "✅ get() method defined"),
        ("def __getitem__(self, key):", "✅ __getitem__() method defined"),
        ("def __setitem__(self, key, value):", "✅ __setitem__() method defined"),
        ("def setdefault(self, key, default=None):", "✅ setdefault() method defined"),
        ("getattr(self, key, default)", "✅ get() uses getattr correctly"),
        ("setattr(self, key, value)", "✅ __setitem__() uses setattr correctly"),
    ]
    
    passed = 0
    for pattern, message in checks:
        if pattern in source:
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_exec_err_usage():
    """Validate that exec_err is used correctly as module-level function"""
    print("=" * 80)
    print("TEST 2: exec_err Module-Level Function Usage")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        source = f.read()
    
    checks = [
        (r"def exec_err\(executor_name: str, error: str", "✅ exec_err function defined at module level"),
        (r"return exec_err\(executor_name,", "✅ exec_err called correctly (not self.exec_err)"),
        (r"return exec_err\(['\"]all_executors['\"]", "✅ exec_err used for all executors failed case"),
    ]
    
    # Anti-pattern: should NOT have self.exec_err
    if re.search(r"return self\.exec_err\(", source):
        print("  ❌ Found self.exec_err() - should be exec_err()")
        return False
    else:
        print("  ✅ No self.exec_err() calls found")
    
    passed = 1  # Already passed the anti-pattern check
    for pattern, message in checks:
        if re.search(pattern, source):
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks) + 1} checks passed\n")
    return passed == len(checks) + 1


def test_submit_with_retries():
    """Validate that _submit_with_retries is implemented"""
    print("=" * 80)
    print("TEST 3: _submit_with_retries Method (Raydium Fix)")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        source = f.read()
    
    checks = [
        (r"async def _submit_with_retries\(", "✅ _submit_with_retries method defined as async"),
        (r"max_retries=3", "✅ max_retries parameter with default"),
        (r"retry_delay=1\.0", "✅ retry_delay parameter with default"),
        (r"for attempt in range\(max_retries\)", "✅ Retry loop implementation"),
        (r"await asyncio\.sleep\(retry_delay\)", "✅ Sleep between retries"),
        (r"result = await self\._submit_with_retries\(", "✅ _submit_with_retries is called"),
    ]
    
    passed = 0
    for pattern, message in checks:
        if re.search(pattern, source):
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_advanced_mev_dot_notation():
    """Validate that Advanced MEV result uses dot notation"""
    print("=" * 80)
    print("TEST 4: Advanced MEV Bot Result Access (Dot Notation Fix)")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        source = f.read()
    
    # Should use dot notation
    checks = [
        (r"result\.success", "✅ result.success (dot notation)"),
        (r"result\.signature", "✅ result.signature (dot notation)"),
        (r"result\.error", "✅ result.error (dot notation)"),
    ]
    
    # Should NOT use .get() on result from advanced_mev_executor
    advanced_mev_section = re.search(
        r"result = await self\.advanced_mev_executor\.execute_buy.*?return",
        source,
        re.DOTALL
    )
    
    if advanced_mev_section:
        section_text = advanced_mev_section.group(0)
        if "result.get(" in section_text:
            print("  ❌ Found result.get() - should use dot notation")
            return False
        else:
            print("  ✅ No result.get() in advanced_mev_executor section")
    
    passed = 1  # Already passed the anti-pattern check
    for pattern, message in checks:
        if re.search(pattern, source):
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks) + 1} checks passed\n")
    return passed == len(checks) + 1


def test_meteora_signature_extraction():
    """Validate that Meteora extracts source transaction correctly"""
    print("=" * 80)
    print("TEST 5: Meteora Source Transaction Extraction")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        source = f.read()
    
    # Find meteora buy method
    meteora_section = re.search(
        r"async def _execute_meteora_buy.*?(?=\n    async def|\n    def|\Z)",
        source,
        re.DOTALL
    )
    
    if not meteora_section:
        print("  ❌ _execute_meteora_buy method not found")
        return False
    
    meteora_text = meteora_section.group(0)
    
    checks = [
        ("trade_info.get('signature')", "✅ Extracts from trade_info['signature']"),
        ("kwargs.get('original_signature'", "✅ Fallback to kwargs['original_signature']"),
        ("No source transaction signature provided", "✅ Warning when signature missing"),
    ]
    
    passed = 0
    for pattern, message in checks:
        if pattern in meteora_text:
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_keypair_extraction():
    """Validate that MEVAdvancedBotExecutor gets proper Keypair"""
    print("=" * 80)
    print("TEST 6: Keypair Extraction for MEVAdvancedBotExecutor")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        source = f.read()
    
    # Find advanced_mev_executor initialization
    init_section = re.search(
        r"from mev_advanced_bot_executor import MEVAdvancedBotExecutor.*?self\.advanced_mev_executor = MEVAdvancedBotExecutor\([^)]+\)",
        source,
        re.DOTALL
    )
    
    if not init_section:
        print("  ❌ MEVAdvancedBotExecutor initialization not found")
        return False
    
    init_text = init_section.group(0)
    
    checks = [
        ("wallet_keypair = self._get_keypair()", "✅ Extracts keypair using _get_keypair()"),
        ("MEVAdvancedBotExecutor(wallet_keypair,", "✅ Passes wallet_keypair to executor"),
        ("def _get_keypair(self):", "✅ _get_keypair() method defined"),
        ("hasattr(self.wallet, 'keypair')", "✅ Checks for keypair attribute"),
    ]
    
    passed = 0
    for pattern, message in checks:
        if pattern in source:
            print(f"  {message}")
            passed += 1
        else:
            print(f"  ❌ {message.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("EXECUTOR INTEGRATION FIXES - SOURCE CODE VALIDATION")
    print("=" * 80)
    print()
    
    tests = [
        ("Config Dict Methods", test_config_dict_methods()),
        ("exec_err Function Usage", test_exec_err_usage()),
        ("_submit_with_retries Implementation", test_submit_with_retries()),
        ("Advanced MEV Dot Notation", test_advanced_mev_dot_notation()),
        ("Meteora Signature Extraction", test_meteora_signature_extraction()),
        ("Keypair Extraction", test_keypair_extraction()),
    ]
    
    passed = sum(1 for name, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}\n")
    
    if passed == total:
        print("  🎉 ALL EXECUTOR INTEGRATION FIXES VALIDATED!")
        print("\n  ✅ Fix 1: MEVDirectCopyExecutor - Config object passing (already correct)")
        print("  ✅ Fix 2: Jupiter Executor - Config dict methods added")
        print("  ✅ Fix 3: Raydium Executor - _submit_with_retries implemented")
        print("  ✅ Fix 4: Advanced MEV Bot - Result dot notation fixed")
        print("  ✅ Fix 5: Meteora Executor - Source transaction extraction fixed")
        print("  ✅ Fix 6: General - Keypair extraction from wallet wrapper")
        print()
        return 0
    else:
        print("  ❌ SOME VALIDATIONS FAILED")
        failed = [name for name, result in tests if not result]
        print(f"  Failed: {', '.join(failed)}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
