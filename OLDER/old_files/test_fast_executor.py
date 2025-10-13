"""
Test suite for FastExecutor with comprehensive fallback testing
"""

import pytest
import asyncio
from typing import Optional
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction
from solders.message import MessageV0

from fast_executor import FastExecutor
from config import COMPUTE_UNIT_LIMIT, COMPUTE_UNIT_PRICE

@pytest.fixture
async def executor():
    """Create FastExecutor instance for testing"""
    keypair = Keypair()
    executor = FastExecutor(keypair)
    await executor.initialize()
    yield executor
    await executor.cleanup()

@pytest.mark.asyncio
async def test_rpc_health_checking(executor):
    """Test RPC health checking and endpoint selection"""
    endpoints = await executor.get_healthy_rpcs()
    assert len(endpoints) > 0
    for endpoint in endpoints:
        assert "url" in endpoint
        assert "name" in endpoint
        assert "latency" in endpoint
        assert endpoint["latency"] > 0

@pytest.mark.asyncio
async def test_jito_timeout_and_fallback(executor):
    """Test that Jito timeout triggers fast RPC fallback"""
    # Create a test transaction
    tx = VersionedTransaction(MessageV0())
    
    # Force Jito to timeout
    executor.jito_timeout = 0.001  # 1ms timeout
    
    start_time = asyncio.get_event_loop().time()
    sig = await executor.submit_transaction(tx)
    end_time = asyncio.get_event_loop().time()
    
    # Verify quick fallback
    assert end_time - start_time < 0.1  # Should fall back within 100ms
    assert sig is not None

@pytest.mark.asyncio
async def test_multiple_rpc_fallback(executor):
    """Test fallback through multiple RPCs"""
    # Create a test transaction
    instructions = [
        transfer(
            TransferParams(
                from_pubkey=executor.keypair.pubkey(),
                to_pubkey=Keypair().pubkey(),
                lamports=1000
            )
        )
    ]
    
    # Force first RPC to fail by using invalid URL
    executor.rpc_url = "http://invalid"
    
    # Should still succeed via fallback RPCs
    sig = await executor.submit_with_retries(
        VersionedTransaction(MessageV0())
    )
    assert sig is not None

@pytest.mark.asyncio
async def test_parallel_confirmation_checking(executor):
    """Test parallel confirmation checking across RPCs"""
    # Create and submit a test transaction
    instructions = [
        transfer(
            TransferParams(
                from_pubkey=executor.keypair.pubkey(),
                to_pubkey=Keypair().pubkey(),
                lamports=1000
            )
        )
    ]
    tx = VersionedTransaction(MessageV0())
    
    # Submit transaction
    sig = await executor.submit_transaction(tx)
    assert sig is not None
    
    # Check confirmation with timeout
    result = await executor.confirm_transaction(sig, timeout=10)
    assert result is not None
    assert "error" not in result

@pytest.mark.asyncio
async def test_error_handling(executor):
    """Test error handling and recovery"""
    # Try submitting invalid transaction
    invalid_tx = "not a transaction"
    with pytest.raises(Exception):
        await executor.submit_transaction(invalid_tx)
    
    # Verify executor is still usable
    endpoints = await executor.get_healthy_rpcs()
    assert len(endpoints) > 0

@pytest.mark.asyncio
async def test_retry_logic(executor):
    """Test retry logic with failing RPCs"""
    tx = VersionedTransaction(MessageV0())
    
    # Make first attempts fail
    original_request = executor._rpc_request
    fail_count = 0
    
    async def mock_request(*args, **kwargs):
        nonlocal fail_count
        if fail_count < 2:
            fail_count += 1
            return {"error": "mock error"}
        return await original_request(*args, **kwargs)
    
    executor._rpc_request = mock_request
    
    # Should succeed on third attempt
    sig = await executor.submit_with_retries(tx)
    assert sig is not None
    assert fail_count == 2  # Verify first two attempts failed

if __name__ == "__main__":
    pytest.main([__file__])
