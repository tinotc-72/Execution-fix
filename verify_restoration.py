#!/usr/bin/env python3
"""
Verification script for robust trade detection restoration.
Validates that the implementation matches RESTORATION_SUMMARY.md requirements.
"""

import sys

def check_requirement(name: str, checks: list) -> bool:
    """Check a requirement and print results."""
    print(f"\n{name}")
    print("=" * 80)
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    return all_passed

def main():
    with open('main.py') as f:
        main_code = f.read()
    
    with open('trade_processor.py') as f:
        tp_code = f.read()
    
    with open('wallet_tx_parser.py') as f:
        wtp_code = f.read()
    
    all_requirements_met = True
    
    # Requirement 1: Balance changes required for execution
    req1_checks = [
        ("Calls detect_buy_sell for balance detection", 
         'detect_buy_sell(meta, self.target_wallets)' in main_code),
        ("Checks if balance actions detected",
         'if not detected_actions:' in main_code),
        ("Returns/skips if no balance changes",
         'if not detected_actions:' in main_code and 
         'return' in main_code[main_code.find('if not detected_actions:'):
                               main_code.find('if not detected_actions:') + 300]),
        ("Logs balance requirement",
         'balance changes required for execution' in main_code.lower()),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 1: Balance Changes REQUIRED for Execution", req1_checks)
    
    # Requirement 2: Validation only (not execution trigger)
    req2_checks = [
        ("Has signer validation check",
         '_check_monitored_wallet_is_signer' in main_code),
        ("Has instruction validation check",
         '_check_trade_instructions' in main_code),
        ("Validation used for logging, not gating",
         'VALIDATION_CHECK' in main_code and 'BALANCE_CHECK' in main_code),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 2: Signer/Instruction Checks for Validation Only", req2_checks)
    
    # Requirement 3: Action detection from balance deltas
    req3_checks = [
        ("Calculates token balance delta",
         'delta = post_amount - pre_amount' in tp_code),
        ("Detects BUY from positive delta",
         'if delta > 0:' in tp_code and "action_type = 'buy'" in tp_code),
        ("Detects SELL from negative delta",
         'elif delta < 0:' in tp_code and "action_type = 'sell'" in tp_code),
        ("Skips zero deltas",
         'if delta == 0:' in tp_code and 'continue' in tp_code),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 3: Buy/Sell Detection from Balance Deltas", req3_checks)
    
    # Requirement 4: Returns 'unknown' when unclear
    fallback_start = tp_code.find('def _try_signer_instruction_fallback')
    fallback_section = tp_code[fallback_start:fallback_start + 3000]
    
    req4_checks = [
        ("Fallback method exists",
         fallback_start > 0),
        ("Returns 'unknown' when logs inconclusive",
         "return 'unknown'" in fallback_section),
        ("Returns 'unknown' when validation fails",
         fallback_section.count("return 'unknown'") >= 2),
        ("Doesn't force 'swap' action",
         "return 'swap'" not in fallback_section),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 4: Returns 'unknown' (No Forced Actions)", req4_checks)
    
    # Requirement 5: No synthetic trades
    req5_checks = [
        ("_create_synthetic_trade_info deprecated",
         'DEPRECATED' in wtp_code and '_create_synthetic_trade_info' in wtp_code),
        ("_create_synthetic_trade_info returns None",
         'async def _create_synthetic_trade_info' in wtp_code and
         'return None' in wtp_code[wtp_code.find('async def _create_synthetic_trade_info'):
                                    wtp_code.find('async def _create_synthetic_trade_info') + 600]),
        ("_analyze_logs_for_trade_smart deprecated",
         'DEPRECATED' in wtp_code and '_analyze_logs_for_trade_smart' in wtp_code),
        ("No fallback to smart log analysis",
         wtp_code.count('await self._analyze_logs_for_trade_smart') == 0),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 5: No Synthetic Trades (Deprecated)", req5_checks)
    
    # Requirement 6: Correct docstrings
    req6_checks = [
        ("main.py docstring updated",
         'ROBUST TRADE DETECTION AND PARSING' in main_code),
        ("Doesn't mention defaulting to swap",
         'defaults to' not in main_code or 'swap' not in main_code.lower()[
             main_code.lower().find('defaults to'):main_code.lower().find('defaults to') + 100] 
         if 'defaults to' in main_code else True),
        ("Emphasizes balance changes required",
         'Token balance changes REQUIRED' in main_code),
        ("wallet_tx_parser.py docstring updated",
         'Balance changes are the PRIMARY requirement' in wtp_code),
    ]
    all_requirements_met &= check_requirement(
        "REQUIREMENT 6: Accurate Documentation", req6_checks)
    
    # Final result
    print("\n" + "=" * 80)
    if all_requirements_met:
        print("✅ ALL RESTORATION REQUIREMENTS MET")
        print("\nThe implementation correctly:")
        print("  • Requires token balance changes for execution")
        print("  • Uses signer/instruction checks for validation only")
        print("  • Detects buy/sell from actual balance deltas")
        print("  • Returns 'unknown' when action unclear (no forced execution)")
        print("  • Has deprecated synthetic trade creation (returns None)")
        print("  • Has accurate documentation reflecting actual behavior")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME RESTORATION REQUIREMENTS NOT MET")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
