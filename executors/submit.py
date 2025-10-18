"""
Single, reliable RPC submitter with robust confirmation polling and structured results.

This module provides send_and_confirm_v0_tx(), a unified transaction submission helper
that all executors should use for consistent, reliable transaction submission.

Features:
- Robust RPC submission with proper error handling
- Confirmation polling with real signature tracking
- Structured results with signature and final status
- No placeholders or None returns on success
"""

import asyncio
import base64
import logging
from typing import Optional, Dict, Any
import httpx

try:
    from solders.transaction import VersionedTransaction
    from solders.signature import Signature
except ImportError:
    # Allow import without solders for testing
    VersionedTransaction = None
    Signature = None

logger = logging.getLogger(__name__)


async def send_and_confirm_v0_tx(
    vtx: VersionedTransaction,
    rpc_url: str,
    max_retries: int = 5,
    retry_delay: float = 0.8,
    timeout: float = 15.0
) -> Dict[str, Any]:
    """
    Send a VersionedTransaction to the RPC and confirm it.
    
    This is the single, reliable submitter that all executors should use.
    
    Args:
        vtx: The VersionedTransaction to submit (must be signed)
        rpc_url: The RPC endpoint URL
        max_retries: Number of confirmation retry attempts (default: 5)
        retry_delay: Delay between confirmation attempts in seconds (default: 0.8)
        timeout: HTTP request timeout in seconds (default: 15.0)
    
    Returns:
        A structured result dictionary with:
        - success (bool): True if transaction was submitted and confirmed
        - signature (str): The transaction signature (always present on success)
        - status (dict): The final confirmation status from getSignatureStatuses
        - error (str): Error message (only present on failure)
        
    Example success result:
        {
            "success": True,
            "signature": "5j7s...",
            "status": {"confirmationStatus": "confirmed", "err": None}
        }
        
    Example failure result:
        {
            "success": False,
            "error": "Transaction submission failed: <reason>"
        }
    """
    if not rpc_url:
        logger.error("[SUBMIT_RPC] No RPC URL provided")
        return {
            "success": False,
            "error": "No RPC URL configured"
        }
    
    if not isinstance(vtx, VersionedTransaction):
        logger.error(f"[SUBMIT_RPC] Invalid transaction type: {type(vtx)}")
        return {
            "success": False,
            "error": f"Invalid transaction type: {type(vtx)}"
        }
    
    # Step 1: Submit the transaction
    try:
        raw = bytes(vtx)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                base64.b64encode(raw).decode(),
                {
                    "encoding": "base64",
                    "skipPreflight": True,
                    "preflightCommitment": "processed",
                    "maxRetries": 1
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(rpc_url, json=payload)
            r.raise_for_status()
            data = r.json()
        
        # Extract signature from response
        sig = data.get("result")
        if not sig:
            error_info = data.get("error", {})
            error_msg = error_info.get("message", "Unknown error") if isinstance(error_info, dict) else str(error_info)
            logger.error(f"[SUBMIT_RPC] Transaction submission failed: {error_msg}")
            return {
                "success": False,
                "error": f"Transaction submission failed: {error_msg}"
            }
        
        logger.info(f"[SUBMIT_RPC] Transaction submitted successfully: {sig}")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"[SUBMIT_RPC] HTTP error during submission: {e}")
        return {
            "success": False,
            "error": f"HTTP error: {e}"
        }
    except Exception as e:
        logger.error(f"[SUBMIT_RPC] Unexpected error during submission: {e}")
        return {
            "success": False,
            "error": f"Submission error: {e}"
        }
    
    # Step 2: Confirm the transaction with retries
    final_status = None
    for attempt in range(1, max_retries + 1):
        try:
            confirm_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignatureStatuses",
                "params": [[sig], {"searchTransactionHistory": True}]
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(rpc_url, json=confirm_payload)
                r.raise_for_status()
                confirm_data = r.json()
            
            # Extract status from response
            result = confirm_data.get("result", {})
            value = result.get("value", [])
            status = value[0] if value else None
            
            logger.info(f"[CONFIRM] attempt={attempt}/{max_retries} sig={sig} status={status}")
            
            if status:
                # Transaction is confirmed (err could be None or an error object)
                final_status = status
                confirmation_status = status.get("confirmationStatus")
                error = status.get("err")
                
                if error:
                    logger.warning(f"[CONFIRM][FINAL] sig={sig} confirmed with error: {error}")
                    return {
                        "success": False,
                        "signature": sig,
                        "status": status,
                        "error": f"Transaction failed on chain: {error}"
                    }
                else:
                    logger.info(f"[CONFIRM][FINAL] sig={sig} status={confirmation_status}")
                    return {
                        "success": True,
                        "signature": sig,
                        "status": status
                    }
            
        except Exception as e:
            logger.warning(f"[CONFIRM] attempt={attempt}/{max_retries} error: {e}")
        
        # Wait before next retry (unless this is the last attempt)
        if attempt < max_retries:
            await asyncio.sleep(retry_delay)
    
    # If we get here, confirmation timed out
    logger.warning(f"[CONFIRM] Timeout after {max_retries} attempts for sig={sig}")
    return {
        "success": False,
        "signature": sig,
        "error": f"Confirmation timeout after {max_retries} attempts"
    }
