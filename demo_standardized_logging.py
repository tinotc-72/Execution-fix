#!/usr/bin/env python3
"""
Demo script showing standardized submission logging in action.

This demonstrates how the log_submit_result helper produces consistent,
structured logs across all submission paths with real values (no placeholders).
"""

from executors.submit import SubmitResult
from utils.logs import log_submit_result


def demo_meteora_buy_success():
    """Simulate a successful Meteora buy transaction"""
    print("\n" + "=" * 80)
    print("DEMO 1: Meteora Buy Transaction (Success)")
    print("=" * 80)
    print("\nScenario: User buys tokens on Meteora DEX")
    print("Token Mint: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU")
    print("Amount: 0.1 SOL")
    print("\nSubmission Result:")
    
    res = SubmitResult(
        ok=True,
        signature="3ZqPx4KMo7L5NsJt2U8VwXyZ1AbC4DeFgHiJkL6MnOpQ",
        status="confirmed",
        confirmationStatus="confirmed"
    )
    
    log_submit_result(
        dex="meteora",
        action="buy",
        mint="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        res=res
    )


def demo_jupiter_sell_success():
    """Simulate a successful Jupiter sell transaction"""
    print("\n" + "=" * 80)
    print("DEMO 2: Jupiter Sell Transaction (Success)")
    print("=" * 80)
    print("\nScenario: User sells tokens via Jupiter aggregator")
    print("Token Mint: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v (USDC)")
    print("Amount: 100 tokens")
    print("\nSubmission Result:")
    
    res = SubmitResult(
        ok=True,
        signature="5j7s8k9L2mNpQrStUvWxYz3AbCdEfGhIjKlMnOpQrStUvWxYz",
        status="finalized",
        confirmationStatus="finalized"
    )
    
    log_submit_result(
        dex="jupiter",
        action="sell",
        mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        res=res
    )


def demo_raydium_buy_failed():
    """Simulate a failed Raydium buy transaction"""
    print("\n" + "=" * 80)
    print("DEMO 3: Raydium Buy Transaction (Failed)")
    print("=" * 80)
    print("\nScenario: Transaction submission failed due to slippage")
    print("Token Mint: So11111111111111111111111111111111111111112 (SOL)")
    print("Amount: 1.0 SOL")
    print("\nSubmission Result:")
    
    res = SubmitResult(
        ok=False,
        signature="2AbC3DeFgHiJ4KlM5NoPqR6StU7VwX8Yz9AbCdEfGhIj",
        status="failed",
        error="Transaction simulation failed: slippage tolerance exceeded"
    )
    
    log_submit_result(
        dex="raydium",
        action="buy",
        mint="So11111111111111111111111111111111111111112",
        res=res
    )


def demo_cloner_clone_success():
    """Simulate a successful transaction cloning"""
    print("\n" + "=" * 80)
    print("DEMO 4: Transaction Cloner (Success)")
    print("=" * 80)
    print("\nScenario: Successfully cloned and executed a transaction")
    print("Original Signature: 4AbC5DeFgHiJ6KlM7NoPqR8StU9VwXyZ1AbC2DeFgHi")
    print("\nSubmission Result:")
    
    res = SubmitResult(
        ok=True,
        signature="1mNpQr2StUv3WxYz4AbC5DeFgHi6JkLm7NoPqR8StUvW",
        status="confirmed",
        confirmationStatus="confirmed"
    )
    
    log_submit_result(
        dex="cloner",
        action="clone",
        mint="unknown",  # Cloner may not always know the mint
        res=res
    )


def demo_mev_buy_with_retry():
    """Simulate an MEV-protected buy with multiple attempts"""
    print("\n" + "=" * 80)
    print("DEMO 5: MEV Protected Buy (Success after Jito fallback)")
    print("=" * 80)
    print("\nScenario: MEV bot buys tokens with Jito protection")
    print("Token Mint: 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")
    print("Path: Jito → RPC fallback")
    print("\nSubmission Result:")
    
    res = SubmitResult(
        ok=True,
        signature="8AbC9DeFgHi1JkLm2NoPqR3StU4VwX5Yz6AbC7DeFgHi",
        status="confirmed",
        confirmationStatus="confirmed"
    )
    
    log_submit_result(
        dex="mev",
        action="buy",
        mint="4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        res=res
    )


def main():
    print("\n" + "=" * 80)
    print("STANDARDIZED SUBMISSION LOGGING DEMO")
    print("=" * 80)
    print("\nThis demo shows how all submission paths produce consistent,")
    print("structured logs with REAL values (no placeholders).")
    print("\nFormat: DEX={dex} action={action} mint={mint} sig={sig} status={status} ok={ok}")
    
    demo_meteora_buy_success()
    demo_jupiter_sell_success()
    demo_raydium_buy_failed()
    demo_cloner_clone_success()
    demo_mev_buy_with_retry()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\n✅ Key Benefits:")
    print("  1. Consistent log format across all DEXes and executors")
    print("  2. Real signature values (never placeholders or 'unknown')")
    print("  3. Real confirmation status from RPC")
    print("  4. Easy to parse for monitoring and analytics")
    print("  5. Handles both success and failure cases")
    print("  6. Graceful fallback for malformed results")
    print("\n")


if __name__ == "__main__":
    main()
