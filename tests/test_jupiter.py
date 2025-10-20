#!/usr/bin/env python3
"""
Minimal Jupiter DEX Test - Simulate or Submit 0.001 SOL Buy Transaction

This script builds a 0.001 SOL buy transaction on Jupiter DEX using a known liquid token (USDC).
It supports two modes:
- --simulate: Prints the transaction result without submitting (dry-run)
- --submit: Signs and submits the transaction to the blockchain

Usage:
    python tests/test_jupiter.py --simulate
    python tests/test_jupiter.py --submit
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from mev_jupiter_executor import get_best_route, get_swap_transaction
from executors.submit import send_and_confirm_v0_tx, SubmitResult
from env_keys import load_wallet_from_private_key, EnvKeys
from utils.logs import log_submit_result
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Known liquid tokens
SOL_MINT = "So11111111111111111111111111111111111111112"  # Wrapped SOL
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC

# Test amount: 0.001 SOL
TEST_AMOUNT_SOL = 0.001
TEST_AMOUNT_LAMPORTS = int(TEST_AMOUNT_SOL * 1_000_000_000)


async def build_jupiter_buy_tx(wallet: Keypair, amount_lamports: int) -> VersionedTransaction:
    """
    Build a Jupiter buy transaction (SOL -> USDC).
    
    Args:
        wallet: Wallet keypair for signing
        amount_lamports: Amount of SOL to swap in lamports
    
    Returns:
        VersionedTransaction ready to be submitted
    """
    logger.info(f"[JUPITER_TEST] Building buy transaction...")
    logger.info(f"[JUPITER_TEST] Amount: {amount_lamports / 1e9:.6f} SOL ({amount_lamports} lamports)")
    logger.info(f"[JUPITER_TEST] Input: SOL -> Output: USDC")
    
    # Step 1: Get quote from Jupiter
    logger.info("[JUPITER_TEST] Step 1: Getting quote from Jupiter...")
    route = get_best_route(
        input_mint=SOL_MINT,
        output_mint=USDC_MINT,
        amount=amount_lamports,
        slippage_bps=300  # 3% slippage
    )
    
    if not route:
        raise Exception("Failed to get route from Jupiter")
    
    logger.info(f"[JUPITER_TEST] ✅ Quote received: {route.get('inAmount')} -> {route.get('outAmount')}")
    
    # Step 2: Get swap transaction
    logger.info("[JUPITER_TEST] Step 2: Getting swap transaction...")
    swap_tx_b64 = get_swap_transaction(route, wallet.pubkey())
    
    if not swap_tx_b64:
        raise Exception("Failed to get swap transaction from Jupiter")
    
    logger.info(f"[JUPITER_TEST] ✅ Swap transaction received (length: {len(swap_tx_b64)} chars)")
    
    # Step 3: Deserialize and sign transaction
    logger.info("[JUPITER_TEST] Step 3: Deserializing and signing transaction...")
    tx_bytes = base64.b64decode(swap_tx_b64)
    vtx = VersionedTransaction.from_bytes(tx_bytes)
    
    # Sign the transaction
    signed_vtx = VersionedTransaction(vtx.message, [wallet])
    
    logger.info(f"[JUPITER_TEST] ✅ Transaction signed and ready")
    
    return signed_vtx


async def simulate_transaction(vtx: VersionedTransaction):
    """
    Simulate the transaction without submitting.
    
    Args:
        vtx: The VersionedTransaction to simulate
    """
    logger.info("[JUPITER_TEST] === SIMULATION MODE ===")
    logger.info(f"[JUPITER_TEST] Transaction details:")
    logger.info(f"[JUPITER_TEST]   - Message: {vtx.message}")
    logger.info(f"[JUPITER_TEST]   - Signatures: {len(vtx.signatures)}")
    logger.info(f"[JUPITER_TEST]   - Size: {len(bytes(vtx))} bytes")
    logger.info("[JUPITER_TEST] ✅ Transaction built successfully (not submitted)")


async def submit_transaction(vtx: VersionedTransaction, rpc_url: str):
    """
    Submit the transaction to the blockchain.
    
    Args:
        vtx: The VersionedTransaction to submit
        rpc_url: RPC endpoint URL
    """
    logger.info("[JUPITER_TEST] === SUBMIT MODE ===")
    logger.info(f"[JUPITER_TEST] Submitting transaction to: {rpc_url}")
    
    # Submit using the standard submitter
    result_dict = await send_and_confirm_v0_tx(vtx, rpc_url)
    
    # Convert dict result to SubmitResult for consistent logging
    result = SubmitResult.from_dict(result_dict)
    
    # Print signature and final status via log_submit_result
    log_submit_result(dex="Jupiter", action="buy", mint=USDC_MINT, res=result)
    
    if result.ok:
        logger.info(f"[JUPITER_TEST] ✅ TRANSACTION SUCCESSFUL!")
        logger.info(f"[JUPITER_TEST] Signature: {result.signature}")
        logger.info(f"[JUPITER_TEST] Status: {result.confirmationStatus}")
        logger.info(f"[JUPITER_TEST] Explorer: https://solscan.io/tx/{result.signature}")
    else:
        logger.error(f"[JUPITER_TEST] ❌ TRANSACTION FAILED: {result.error}")
        if result.signature:
            logger.error(f"[JUPITER_TEST] Signature: {result.signature}")


async def main(args):
    """Main test function."""
    try:
        # Load wallet and environment
        logger.info("[JUPITER_TEST] Loading wallet and environment...")
        env_keys = EnvKeys()
        wallet = load_wallet_from_private_key()
        rpc_url = env_keys.HELIUS_RPC_URL
        
        logger.info(f"[JUPITER_TEST] Wallet: {wallet.pubkey()}")
        logger.info(f"[JUPITER_TEST] RPC: {rpc_url[:50]}...")
        
        # Determine amount to use
        amount_lamports = int(args.amount * 1_000_000_000) if hasattr(args, 'amount') else TEST_AMOUNT_LAMPORTS
        logger.info(f"[JUPITER_TEST] Amount: {amount_lamports / 1e9:.6f} SOL ({amount_lamports} lamports)")
        
        # Build transaction
        vtx = await build_jupiter_buy_tx(wallet, amount_lamports)
        
        # Execute based on mode
        if args.simulate:
            await simulate_transaction(vtx)
        elif args.submit:
            await submit_transaction(vtx, rpc_url)
        else:
            logger.error("[JUPITER_TEST] ❌ Must specify either --simulate or --submit")
            return 1
        
        logger.info("[JUPITER_TEST] Test completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"[JUPITER_TEST] ❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jupiter DEX minimal test")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--simulate", action="store_true", help="Simulate transaction (dry-run)")
    group.add_argument("--submit", action="store_true", help="Submit transaction to blockchain")
    parser.add_argument("--amount", type=float, default=TEST_AMOUNT_SOL, 
                       help=f"Amount in SOL to swap (default: {TEST_AMOUNT_SOL})")
    
    args = parser.parse_args()
    
    exit_code = asyncio.run(main(args))
    sys.exit(exit_code)
