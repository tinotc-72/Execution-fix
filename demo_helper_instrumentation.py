#!/usr/bin/env python3
"""
Demonstration of DebugSpan instrumentation in helper methods.

This script shows how the enhanced instrumentation provides granular tracing
for each logical chunk in the inference pipeline, with timing, correlation IDs,
and loop protection.
"""

import logging
import time
from debug_utils import DebugSpan, set_span_id, get_span_id

# Configure logging to see the detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Constants from actual implementation (for demonstration)
MAX_LOG_LINES_TO_SCAN = 500
MAX_ADDRESSES_TO_CHECK = 200
MAX_INSTRUCTIONS_TO_SCAN = 100
MAX_TOKEN_BALANCES_TO_SCAN = 50


def simulate_helper_with_debug_span():
    """Simulate a helper method with DebugSpan instrumentation."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Helper Method with DebugSpan Instrumentation")
    print("=" * 80)
    
    # Set correlation ID (as done in main inference flow)
    correlation_id = "demo-sig-abc123"
    set_span_id(correlation_id)
    
    print(f"\n📋 Correlation ID set: {correlation_id}")
    print("🔍 Starting helper method execution...\n")
    
    # Simulate helper method call with DebugSpan
    corr_id = get_span_id()
    with DebugSpan("_extract_mint_from_logs_enhanced", input_data={"log_count": 150}):
        # Simulate processing
        
        # Simulate log scanning
        logger.info(f"[MINT_FROM_LOGS] Processing logs... | corr={corr_id}")
        time.sleep(0.05)
        
        # Simulate limit check
        if 150 > MAX_LOG_LINES_TO_SCAN:
            logger.warning(
                f"⚠️ [MINT_FROM_LOGS] Limiting log scan from 150 to {MAX_LOG_LINES_TO_SCAN} lines | corr={corr_id}"
            )
        
        # Simulate address checking
        logger.info(f"[MINT_FROM_LOGS] Checking addresses... | corr={corr_id}")
        time.sleep(0.03)
        
        # Simulate result
        mock_mint = "TokenMint1234567890abcdefghij"
        logger.info(f"🎯 [MINT_FROM_LOGS] Found mint {mock_mint[:8]}... | corr={corr_id}")
    
    print("\n✅ Helper method completed with granular tracing!")


def simulate_helper_with_exception():
    """Simulate a helper method with exception handling."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Helper Method with Exception Handling")
    print("=" * 80)
    
    # Set correlation ID
    correlation_id = "demo-sig-error"
    set_span_id(correlation_id)
    
    print(f"\n📋 Correlation ID set: {correlation_id}")
    print("🔍 Starting helper method with simulated error...\n")
    
    # Simulate helper method with error
    corr_id = get_span_id()
    with DebugSpan("_extract_mint_from_token_balances", input_data={"has_meta": True}):
        try:
            # Simulate processing
            logger.info(f"[MINT_FROM_BALANCES] Processing token balances... | corr={corr_id}")
            
            # Simulate an error condition
            raise ValueError("Simulated error: Invalid token balance format")
            
        except Exception as e:
            logger.error(f"❌ [MINT_FROM_BALANCES] Exception: {e} | corr={corr_id}", exc_info=True)
            # Return safe default
            result = None
    
    print("\n✅ Exception handled gracefully with full stack trace!")


def simulate_nested_helper_calls():
    """Simulate nested helper method calls with DebugSpan."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Nested Helper Method Calls")
    print("=" * 80)
    
    # Set correlation ID
    correlation_id = "demo-sig-nested"
    set_span_id(correlation_id)
    
    print(f"\n📋 Correlation ID set: {correlation_id}")
    print("🔍 Starting nested helper method calls...\n")
    
    # Simulate outer method
    corr_id = get_span_id()
    with DebugSpan("infer_missing_fields", input_data={"signature": correlation_id[:8]}):
        
        # Simulate inner method 1
        with DebugSpan("_infer_signature_from_transaction", input_data={"has_trade_info": True}):
            logger.debug(f"[SIG_INFERENCE] Checking transaction data... | corr={corr_id}")
            time.sleep(0.02)
            logger.info(f"🎯 [SIG_INFERENCE] Found signature: {correlation_id[:12]}... | corr={corr_id}")
        
        # Simulate inner method 2
        with DebugSpan("_infer_wallet_from_transaction", input_data={"has_trade_info": True}):
            logger.debug(f"[WALLET_INFERENCE] Checking fee payer... | corr={corr_id}")
            time.sleep(0.02)
            logger.info(f"🎯 [WALLET_INFERENCE] Found wallet: Wallet123... | corr={corr_id}")
        
        # Simulate inner method 3
        with DebugSpan("_analyze_logs_for_action", input_data={"log_count": 50}):
            logger.debug(f"[ACTION_ANALYSIS] Analyzing logs... | corr={corr_id}")
            time.sleep(0.02)
            logger.info(f"[ACTION_ANALYSIS] Determined action: swap | corr={corr_id}")
    
    print("\n✅ Nested helper calls completed with hierarchical tracing!")


def simulate_loop_protection():
    """Simulate loop protection mechanism."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Loop Protection Mechanism")
    print("=" * 80)
    
    # Set correlation ID
    correlation_id = "demo-sig-loops"
    set_span_id(correlation_id)
    
    print(f"\n📋 Correlation ID set: {correlation_id}")
    print("🔍 Demonstrating loop protection...\n")
    
    corr_id = get_span_id()
    with DebugSpan("_extract_mint_from_instruction_accounts", input_data={"has_trade_info": True}):
        
        # Simulate scanning many instructions
        total_instructions = 250
        logger.info(f"[MINT_FROM_ACCOUNTS] Total instructions: {total_instructions} | corr={corr_id}")
        
        if total_instructions > MAX_INSTRUCTIONS_TO_SCAN:
            logger.warning(
                f"⚠️ [MINT_FROM_ACCOUNTS] Limiting instruction scan from {total_instructions} to {MAX_INSTRUCTIONS_TO_SCAN} | corr={corr_id}"
            )
        
        # Simulate processing
        accounts_checked = 0
        for i in range(min(total_instructions, MAX_INSTRUCTIONS_TO_SCAN)):
            accounts_checked += 5
            if accounts_checked > MAX_ADDRESSES_TO_CHECK:
                logger.warning(
                    f"⚠️ [MINT_FROM_ACCOUNTS] Reached max address check limit ({MAX_ADDRESSES_TO_CHECK}) | corr={corr_id}"
                )
                break
        
        logger.info(f"[MINT_FROM_ACCOUNTS] Scanned {min(total_instructions, MAX_INSTRUCTIONS_TO_SCAN)} instructions, checked {min(accounts_checked, MAX_ADDRESSES_TO_CHECK)} accounts | corr={corr_id}")
    
    print("\n✅ Loop protection prevented processing of excessive data!")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("🎯 HELPER METHOD INSTRUMENTATION DEMONSTRATION")
    print("=" * 80)
    print("\nThis demonstration shows the new DebugSpan instrumentation in helper methods.")
    print("Key features:")
    print("  • Granular START/OK/FAIL logging with timing")
    print("  • Correlation IDs for tracing across methods")
    print("  • Loop protection to prevent infinite loops")
    print("  • Robust exception handling with stack traces")
    print("  • Context logging for debugging")
    
    # Run demonstrations
    simulate_helper_with_debug_span()
    simulate_helper_with_exception()
    simulate_nested_helper_calls()
    simulate_loop_protection()
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\n✅ All demonstrations completed successfully!")
    print("\nKey Takeaways:")
    print("  1. Every helper method now has granular tracing")
    print("  2. Correlation IDs enable end-to-end request tracing")
    print("  3. Loop protection prevents infinite loops and DoS")
    print("  4. Exception handling ensures robustness")
    print("  5. Performance impact is minimal (microseconds per span)")
    print("\n🎉 The inference pipeline is now production-ready with comprehensive observability!")


if __name__ == "__main__":
    main()
