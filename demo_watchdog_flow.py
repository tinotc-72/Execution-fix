#!/usr/bin/env python3
"""
Demonstration of the watchdog-wrapped infer_missing_fields flow.

This demonstrates:
1. Inference wrapping with DebugSpan and run_with_watchdog
2. Continuation to coordinator regardless of inference outcome
3. Validation checks before coordinator execution
"""

import asyncio
import logging
import sys
import time  # For blocking sleep simulation in tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add current directory to path
sys.path.insert(0, '.')

from utils.async_timeout import run_with_watchdog
from debug_utils import DebugSpan, set_span_id


class MockTradeProcessor:
    """Mock trade processor for demonstration."""
    
    def infer_missing_fields(self, trade_info):
        """Simulate inference that might timeout or fail."""
        scenario = trade_info.get('scenario', 'success')
        
        if scenario == 'timeout':
            # Simulate long-running inference (intentionally blocking for test)
            # Note: Using time.sleep() instead of asyncio.sleep() to simulate
            # a blocking operation that the watchdog should handle
            time.sleep(5.0)
            return {**trade_info, 'action': 'buy', 'token_mint': 'inferred_mint'}
        elif scenario == 'error':
            # Simulate inference error
            raise ValueError("Inference failed - missing required data")
        else:
            # Simulate successful inference (intentionally blocking for test)
            time.sleep(0.1)
            return {**trade_info, 'action': 'buy', 'token_mint': 'inferred_mint'}


class MockExecutionCoordinator:
    """Mock execution coordinator for demonstration."""
    
    async def _execute_copy_buy(self, token_mint, source_wallet, trade_info, amount_sol=0.001):
        """Simulate coordinator buy execution."""
        print(f"    💰 [COORDINATOR] Executing BUY: {token_mint[:12]}... for {amount_sol} SOL")
        await asyncio.sleep(0.1)
        return {'success': True, 'signature': 'mock_sig_12345'}
    
    async def _execute_copy_sell(self, token_mint, source_wallet, trade_info):
        """Simulate coordinator sell execution."""
        print(f"    💰 [COORDINATOR] Executing SELL: {token_mint[:12]}...")
        await asyncio.sleep(0.1)
        return {'success': True, 'signature': 'mock_sig_67890'}


async def demonstrate_flow(scenario_name: str, trade_info: dict):
    """Demonstrate the complete flow with watchdog protection."""
    print(f"\n{'='*70}")
    print(f"Scenario: {scenario_name}")
    print(f"{'='*70}")
    
    # Set correlation ID
    sig = trade_info.get('signature', 'unknown')
    correlation_id = sig[:12] if len(sig) >= 12 else sig
    set_span_id(correlation_id)
    
    # Mock instances
    trade_processor = MockTradeProcessor()
    execution_coordinator = MockExecutionCoordinator()
    target_wallets = ['wallet1', 'wallet2']
    
    print(f"📥 [INPUT] Trade info: {trade_info}")
    
    # STEP 1: Wrapped inference with timeout protection
    print(f"\n🔍 [INFERENCE] Starting inference with watchdog protection...")
    original_trade_info = trade_info.copy()
    
    with DebugSpan("infer_missing_fields", input_data={"signature": sig[:12]}):
        async def run_inference():
            return await asyncio.to_thread(
                trade_processor.infer_missing_fields,
                trade_info
            )
        
        trade_info = await run_with_watchdog(
            run_inference(),
            timeout_seconds=2.0,
            operation_name="infer_missing_fields",
            fallback_value=original_trade_info,
            log_timeout=True,
            log_error=True
        )
    
    print(f"✅ [INFERENCE] Completed (with timeout protection)")
    
    # Format token_mint for display
    token_mint_display = trade_info.get('token_mint', 'UNKNOWN')
    if token_mint_display and token_mint_display != 'UNKNOWN':
        token_mint_display = token_mint_display[:12] + '...'
    
    print(f"📤 [OUTPUT] Trade info after inference: action={trade_info.get('action')}, token_mint={token_mint_display}")
    
    # STEP 2: Continue to validation and coordinator handoff
    print(f"\n🔍 [VALIDATION] Checking trade intent...")
    
    # Get source wallet
    source_wallet = trade_info.get('wallet_address') or target_wallets[0]
    
    # Extract action and token_mint
    action = trade_info.get('action', 'unknown')
    token_mint = trade_info.get('token_mint', 'UNKNOWN')
    
    # Validate
    valid_actions = {'buy', 'sell', 'swap', 'swap_in', 'swap_out'}
    
    if action == 'unknown' or action not in valid_actions:
        print(f"⚠️ [VALIDATION] Cannot determine trade direction: {action}")
        print(f"📋 [SKIP] Skipping ambiguous trade (direction cannot be parsed)")
        return {'status': 'skipped', 'reason': 'unknown action'}
    
    if token_mint == 'UNKNOWN':
        print(f"⚠️ [VALIDATION] Cannot extract token mint")
        print(f"📋 [SKIP] Skipping ambiguous trade (token cannot be identified)")
        return {'status': 'skipped', 'reason': 'unknown mint'}
    
    print(f"✅ [VALIDATION] Trade intent reconstructed: action={action}, mint={token_mint[:12]}...")
    
    # STEP 3: Hand off to coordinator
    print(f"\n🚀 [COORDINATOR_HANDOFF] Executing trade via coordinator...")
    
    if action in ('buy', 'swap_in', 'swap'):
        result = await execution_coordinator._execute_copy_buy(
            token_mint=token_mint,
            source_wallet=source_wallet,
            trade_info=trade_info,
            amount_sol=0.001
        )
        print(f"✅ [SUCCESS] BUY executed: {result}")
        return {'status': 'executed', 'action': 'buy', 'result': result}
    
    elif action in ('sell', 'swap_out'):
        result = await execution_coordinator._execute_copy_sell(
            token_mint=token_mint,
            source_wallet=source_wallet,
            trade_info=trade_info
        )
        print(f"✅ [SUCCESS] SELL executed: {result}")
        return {'status': 'executed', 'action': 'sell', 'result': result}
    
    return {'status': 'no_action'}


async def main():
    """Run demonstrations."""
    print("="*70)
    print("Demonstration: Watchdog-Protected infer_missing_fields Flow")
    print("="*70)
    
    # Scenario 1: Successful inference
    await demonstrate_flow(
        "Success - Inference completes normally",
        {
            'signature': 'success_sig_123456',
            'wallet_address': 'wallet1',
            'scenario': 'success',
            'action': 'unknown',
            'token_mint': 'UNKNOWN'
        }
    )
    
    # Scenario 2: Timeout - fallback to original data
    await demonstrate_flow(
        "Timeout - Inference exceeds 2s, returns original trade_info",
        {
            'signature': 'timeout_sig_789012',
            'wallet_address': 'wallet1',
            'scenario': 'timeout',
            'action': 'unknown',
            'token_mint': 'UNKNOWN'
        }
    )
    
    # Scenario 3: Error - fallback to original data
    await demonstrate_flow(
        "Error - Inference fails, returns original trade_info",
        {
            'signature': 'error_sig_345678',
            'wallet_address': 'wallet1',
            'scenario': 'error',
            'action': 'unknown',
            'token_mint': 'UNKNOWN'
        }
    )
    
    # Scenario 4: Successful inference with complete data
    await demonstrate_flow(
        "Success with complete data - Inference fills fields, execution proceeds",
        {
            'signature': 'complete_sig_901234',
            'wallet_address': 'wallet1',
            'scenario': 'success',
            'action': 'unknown',
            'token_mint': 'UNKNOWN'
        }
    )
    
    print(f"\n{'='*70}")
    print("Summary:")
    print("="*70)
    print("✅ Watchdog protection ensures inference never blocks indefinitely")
    print("✅ On timeout/error, original trade_info is preserved")
    print("✅ Pipeline continues to validation regardless of inference outcome")
    print("✅ Coordinator is called only if validation passes")
    print("✅ Incomplete trades are logged and skipped (intelligent execution mode)")


if __name__ == "__main__":
    asyncio.run(main())
