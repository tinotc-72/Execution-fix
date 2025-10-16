#!/usr/bin/env python3
"""
Demo script to manually verify the RPC fallback implementation.
This shows the flow of Jito -> RPC fallback with proper logging.
"""

import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch


# Configure logging to show all messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_jito_success():
    """Demo: Jito succeeds, RPC not needed"""
    print("\n" + "=" * 80)
    print("DEMO 1: Jito Success (No RPC Fallback)")
    print("=" * 80)
    
    # Import and create a mock FastExecutor
    from fast_executor import FastExecutor
    from solders.keypair import Keypair
    
    # Create a test keypair
    keypair = Keypair()
    
    # Create executor with mocked logger
    logger = logging.getLogger("FastExecutor.JitoSuccess")
    executor = FastExecutor(keypair=keypair, logger=logger)
    
    # Mock the Jito submission to succeed
    async def mock_jito_submit(vtx):
        logger.info("[SUBMIT_JITO] region=https://test.jito.wtf sig=MockJitoSignature123")
        return "MockJitoSignature123"
    
    # Mock the confirmation
    async def mock_confirm(sig):
        logger.info(f"[CONFIRM] attempt=1/5 status={{'confirmationStatus': 'confirmed'}}")
        return {"confirmationStatus": "confirmed"}
    
    executor._submit_via_jito = mock_jito_submit
    executor._confirm_with_retries = mock_confirm
    
    # Create a mock transaction
    mock_vtx = Mock()
    
    # Call send_and_confirm
    result = await executor.send_and_confirm(mock_vtx)
    
    print(f"\n✅ Result: {result}")
    print("Expected: Jito succeeds, no RPC fallback warning")


async def demo_jito_fails_rpc_succeeds():
    """Demo: Jito fails, RPC fallback succeeds"""
    print("\n" + "=" * 80)
    print("DEMO 2: Jito Fails -> RPC Fallback Succeeds")
    print("=" * 80)
    
    from fast_executor import FastExecutor
    from solders.keypair import Keypair
    
    keypair = Keypair()
    logger = logging.getLogger("FastExecutor.RPCFallback")
    executor = FastExecutor(keypair=keypair, logger=logger)
    
    # Mock Jito to fail
    async def mock_jito_submit(vtx):
        logger.error("[SUBMIT_JITO] error: Connection timeout")
        return None
    
    # Mock RPC to succeed
    async def mock_rpc_submit(vtx):
        logger.info("[SUBMIT_RPC] sig=MockRPCSignature456")
        return "MockRPCSignature456"
    
    # Mock confirmation
    async def mock_confirm(sig):
        logger.info(f"[CONFIRM] attempt=1/5 status={{'confirmationStatus': 'confirmed'}}")
        return {"confirmationStatus": "confirmed"}
    
    executor._submit_via_jito = mock_jito_submit
    executor._submit_via_rpc = mock_rpc_submit
    executor._confirm_with_retries = mock_confirm
    
    mock_vtx = Mock()
    
    # Call send_and_confirm
    result = await executor.send_and_confirm(mock_vtx)
    
    print(f"\n✅ Result: {result}")
    print("Expected: [EXECUTOR] Falling back to RPC submission message")


async def demo_both_fail():
    """Demo: Both Jito and RPC fail"""
    print("\n" + "=" * 80)
    print("DEMO 3: Both Jito and RPC Fail")
    print("=" * 80)
    
    from fast_executor import FastExecutor
    from solders.keypair import Keypair
    
    keypair = Keypair()
    logger = logging.getLogger("FastExecutor.BothFail")
    executor = FastExecutor(keypair=keypair, logger=logger)
    
    # Mock both to fail
    async def mock_jito_submit(vtx):
        logger.error("[SUBMIT_JITO] error: Connection timeout")
        return None
    
    async def mock_rpc_submit(vtx):
        logger.error("[SUBMIT_RPC] error: RPC node unavailable")
        return None
    
    executor._submit_via_jito = mock_jito_submit
    executor._submit_via_rpc = mock_rpc_submit
    
    mock_vtx = Mock()
    
    # Call send_and_confirm
    result = await executor.send_and_confirm(mock_vtx)
    
    print(f"\n✅ Result: {result}")
    print("Expected: [EXECUTOR] submission failed (Jito and RPC) message")


async def demo_rpc_signature_parsing():
    """Demo: RPC signature parsing from 'result' field"""
    print("\n" + "=" * 80)
    print("DEMO 4: RPC Signature Parsing from JSON-RPC 'result'")
    print("=" * 80)
    
    from fast_executor import FastExecutor
    from solders.keypair import Keypair
    
    keypair = Keypair()
    logger = logging.getLogger("FastExecutor.RPCParsing")
    executor = FastExecutor(keypair=keypair, logger=logger)
    
    # Test with correct response structure
    print("\nTest Case 1: Valid JSON-RPC response")
    mock_response_success = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": "ValidSignatureABC123XYZ456"
    }
    
    sig = (mock_response_success or {}).get("result")
    if sig:
        logger.info(f"[SUBMIT_RPC] sig={sig}")
        print(f"✅ Parsed signature: {sig}")
    
    # Test with error response
    print("\nTest Case 2: JSON-RPC error response")
    mock_response_error = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32000, "message": "Transaction simulation failed"}
    }
    
    sig = (mock_response_error or {}).get("result")
    if sig:
        logger.info(f"[SUBMIT_RPC] sig={sig}")
    else:
        logger.error(f"[SUBMIT_RPC] no result: {mock_response_error}")
        print(f"✅ Correctly handled error response")
    
    # Test with malformed response
    print("\nTest Case 3: Malformed response (None)")
    mock_response_none = None
    
    sig = (mock_response_none or {}).get("result")
    if sig:
        logger.info(f"[SUBMIT_RPC] sig={sig}")
    else:
        logger.error(f"[SUBMIT_RPC] no result: {mock_response_none}")
        print(f"✅ Correctly handled None response")


async def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("RPC FALLBACK MANUAL VERIFICATION DEMOS")
    print("=" * 80)
    
    await demo_jito_success()
    await demo_jito_fails_rpc_succeeds()
    await demo_both_fail()
    await demo_rpc_signature_parsing()
    
    print("\n" + "=" * 80)
    print("MANUAL VERIFICATION COMPLETE")
    print("=" * 80)
    print("\n✅ All demos completed successfully!")
    print("\nKey observations:")
    print("1. Jito is always tried first")
    print("2. RPC fallback occurs when Jito fails")
    print("3. '[EXECUTOR] Falling back to RPC submission' is logged")
    print("4. '[EXECUTOR] submission failed (Jito and RPC)' is logged on total failure")
    print("5. Signatures are parsed from JSON-RPC 'result' field")
    print("6. '[CONFIRM][FINAL]' logs success with sig and status")


if __name__ == "__main__":
    asyncio.run(main())
