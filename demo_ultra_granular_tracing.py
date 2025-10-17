#!/usr/bin/env python3
"""
Demo script to showcase ultra-granular step tracing and timing.

This demo simulates the inference pipeline with DebugSpan tracing to show:
1. START/OK/FAIL logging for each step
2. Elapsed time tracking
3. Input/output keys logging
4. Correlation ID propagation
5. Stack trace capture on errors
"""

import time
import logging
from debug_utils import DebugSpan, set_span_id, get_span_id

# Configure logging to see the trace output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def simulate_inference_pipeline(trade_info: dict):
    """
    Simulate the inference pipeline with DebugSpan tracing.
    
    This mimics what happens in trade_processor.infer_missing_fields()
    """
    # Generate correlation ID (like in _process_detected_trade)
    sig = trade_info.get("signature", "")
    if sig and sig != "unknown":
        correlation_id = sig[:12] if len(sig) >= 12 else sig
    else:
        import uuid
        correlation_id = f"uuid_{str(uuid.uuid4())[:8]}"
    
    # Set correlation ID for this thread
    set_span_id(correlation_id)
    
    # Log correlation context (like in main.py)
    logger.info(
        "🪪 [CTX] corr=%s, dex=%s, wallet=%s",
        correlation_id,
        trade_info.get("dex", "unknown"),
        trade_info.get("wallet_address", "unknown")
    )
    
    # Start inference
    corr_id = get_span_id()
    logger.info("🔍 [FIELD_INFERENCE] Starting comprehensive field inference... | corr=%s", corr_id)
    
    # Step 1: Ensure meta
    with DebugSpan("ensure_meta", input_data={"has_meta": bool(trade_info.get("meta"))}):
        time.sleep(0.02)  # Simulate work
        if not trade_info.get("meta"):
            trade_info["meta"] = {"placeholder": "meta_data"}
    
    # Step 2: Annotate source failure
    with DebugSpan("annotate_source_failure", input_data={"has_err": bool(trade_info.get("meta", {}).get("err"))}):
        time.sleep(0.01)  # Simulate work
        if trade_info.get("meta", {}).get("err"):
            trade_info["source_failed"] = True
    
    # Step 3: Last chance fetch (if needed)
    if not trade_info.get("logs") and trade_info.get("signature"):
        sig_val = trade_info.get("signature", "")
        sig_short = sig_val[:12] if len(sig_val) >= 12 else sig_val
        with DebugSpan("last_chance_fetch", input_data={"signature": sig_short}):
            time.sleep(0.05)  # Simulate RPC call
            trade_info["logs"] = ["Program log: Simulated log", "Program log: Instruction: Swap"]
    
    # Step 4: Infer signature
    if not trade_info.get("signature"):
        with DebugSpan("infer_signature", input_data={"has_transaction": bool(trade_info.get("transaction"))}):
            time.sleep(0.015)  # Simulate work
            trade_info["signature"] = "SimulatedSignature123"
    
    # Step 5: Infer wallet
    if not trade_info.get("wallet_address"):
        with DebugSpan("infer_wallet", input_data={"has_transaction": bool(trade_info.get("transaction"))}):
            time.sleep(0.03)  # Simulate work
            trade_info["wallet_address"] = "WalletAddress123"
    
    # Step 6: Infer action
    if not trade_info.get("action"):
        with DebugSpan("infer_action", input_data={"has_logs": bool(trade_info.get("logs"))}):
            time.sleep(0.025)  # Simulate work
            if trade_info.get("logs"):
                # Simulate action detection
                trade_info["action"] = "swap"
    
    # Step 7: Infer DEX
    if not trade_info.get("dex"):
        with DebugSpan("infer_dex", input_data={"has_logs": bool(trade_info.get("logs"))}):
            time.sleep(0.02)  # Simulate work
            trade_info["dex"] = "jupiter"
    
    # Step 8: Infer token mint
    if not trade_info.get("token_mint"):
        with DebugSpan("infer_token_mint", input_data={"has_logs": bool(trade_info.get("logs")), "has_meta": bool(trade_info.get("meta"))}):
            time.sleep(0.04)  # Simulate work
            trade_info["token_mint"] = "TokenMintAddress123"
    
    logger.info("✅ [FIELD_INFERENCE] Completed inference | corr=%s", corr_id)
    return trade_info


def simulate_error_scenario(trade_info: dict):
    """Simulate an error scenario to show stack trace capture."""
    set_span_id("error-scenario-001")
    
    logger.info("🪪 [CTX] corr=error-scenario-001, dex=%s, wallet=%s", 
                trade_info.get("dex", "unknown"),
                trade_info.get("wallet_address", "unknown"))
    
    try:
        with DebugSpan("error_prone_step", input_data={"test": "data"}):
            time.sleep(0.01)
            # Simulate an error
            raise ValueError("Simulated error: RPC timeout")
    except ValueError as e:
        logger.info("Error was caught and logged with stack trace")


def main():
    """Run the demo."""
    print("\n" + "=" * 80)
    print("ULTRA-GRANULAR STEP TRACING DEMO")
    print("=" * 80)
    
    # Demo 1: Complete inference pipeline
    print("\n" + "-" * 80)
    print("Demo 1: Complete Inference Pipeline with Tracing")
    print("-" * 80)
    
    trade_info = {
        "signature": "5KqZ7Nx8mN...",  # Will be used for correlation ID
        "dex": "jupiter",
        "wallet_address": "ABC123xyz...",
        "logs": None,  # Will trigger last_chance_fetch
    }
    
    result = simulate_inference_pipeline(trade_info)
    
    print("\nInference Result:")
    print(f"  - Signature: {result.get('signature')}")
    print(f"  - Action: {result.get('action')}")
    print(f"  - DEX: {result.get('dex')}")
    print(f"  - Token Mint: {result.get('token_mint')}")
    
    # Demo 2: Error handling with stack trace
    print("\n" + "-" * 80)
    print("Demo 2: Error Handling with Stack Trace")
    print("-" * 80)
    
    error_trade = {
        "dex": "raydium",
        "wallet_address": "XYZ789abc...",
    }
    
    simulate_error_scenario(error_trade)
    
    # Demo 3: Show nested spans
    print("\n" + "-" * 80)
    print("Demo 3: Nested Spans")
    print("-" * 80)
    
    set_span_id("nested-demo-123")
    
    with DebugSpan("outer_processing", input_data={"stage": "outer"}):
        time.sleep(0.02)
        
        with DebugSpan("inner_validation", input_data={"stage": "inner"}):
            time.sleep(0.03)
            logger.info("Inner validation complete")
        
        logger.info("Outer processing complete")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✅ START/OK/FAIL logging for each step")
    print("  ✅ Elapsed time tracking (in milliseconds)")
    print("  ✅ Input keys logging")
    print("  ✅ Correlation ID propagation across all steps")
    print("  ✅ Stack trace capture on errors")
    print("  ✅ Nested span support")
    print("\nUse Case:")
    print("  This tracing helps debug the inference pipeline by showing:")
    print("  - Which steps are slow (timing)")
    print("  - Which steps fail (error logging)")
    print("  - What data each step receives (input keys)")
    print("  - How events are correlated (correlation ID)")
    print()


if __name__ == "__main__":
    main()
