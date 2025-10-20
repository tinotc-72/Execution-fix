#!/usr/bin/env python3
"""
Demonstration of Fail-Open Coordinator Behavior

This script shows how the fail-open coordinator handles various edge cases
where the parser cannot infer DEX, amount, or other critical fields.
"""

import asyncio
import logging
from typing import Dict, Any

# Configure clean logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def demo_normalization():
    """Demonstrate field normalization"""
    from execution_coordinator import normalize_dex
    from config import INVESTMENT_PER_TRADE_SOL
    
    logger.info("=" * 70)
    logger.info("FAIL-OPEN COORDINATOR DEMONSTRATION")
    logger.info("=" * 70)
    
    logger.info("\n1️⃣  DEX NORMALIZATION")
    logger.info("-" * 70)
    
    test_dexes = [
        ("jupiter", "Known DEX"),
        ("jup", "DEX Alias"),
        ("some_new_protocol", "Unknown Protocol"),
        ("", "Empty String"),
        (None, "None/Missing"),
    ]
    
    for dex_input, description in test_dexes:
        normalized = normalize_dex(dex_input)
        logger.info(f"  {description:20s}: {repr(dex_input):20s} → {repr(normalized)}")
    
    logger.info("\n2️⃣  AMOUNT NORMALIZATION")
    logger.info("-" * 70)
    logger.info(f"  Config Default: INVESTMENT_PER_TRADE_SOL = {INVESTMENT_PER_TRADE_SOL} SOL")
    logger.info(f"  Used when:")
    logger.info(f"    - amount_sol is missing from trade_info")
    logger.info(f"    - amount_sol is invalid (negative, zero, non-numeric)")
    logger.info(f"    - Parser failed to extract amount")
    
    logger.info("\n3️⃣  ACTION NORMALIZATION")
    logger.info("-" * 70)
    logger.info(f"  Default Action: 'buy'")
    logger.info(f"  Used when:")
    logger.info(f"    - action is missing from trade_info")
    logger.info(f"    - action is invalid or unrecognized")


def demo_routing():
    """Demonstrate routing logic"""
    from execution_coordinator import ROUTE_MAP
    
    logger.info("\n4️⃣  ROUTING LOGIC")
    logger.info("-" * 70)
    
    for dex, route in ROUTE_MAP.items():
        logger.info(f"  {dex:15s}: {' → '.join(route)}")
    
    logger.info("\n  Fallback Behavior:")
    logger.info(f"    When DEX is unknown, uses: {' → '.join(ROUTE_MAP['unknown'])}")


def demo_scenarios():
    """Demonstrate specific scenarios"""
    logger.info("\n5️⃣  FAIL-OPEN SCENARIOS")
    logger.info("-" * 70)
    
    scenarios = [
        {
            "name": "Missing Amount",
            "input": {
                "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "dex": "jupiter",
                "signature": "abc123..."
            },
            "behavior": [
                "✓ Normalizes amount to 0.001 SOL (config default)",
                "✓ Proceeds with Jupiter execution",
                "✓ Logs normalization decision"
            ]
        },
        {
            "name": "Unknown DEX with Mint",
            "input": {
                "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "dex": "new_protocol_xyz",
                "amount_sol": 0.005
            },
            "behavior": [
                "✓ Normalizes DEX to 'unknown'",
                "✓ Uses fallback route: direct_copy → jupiter → raydium → meteora",
                "✓ Tries each executor until one succeeds"
            ]
        },
        {
            "name": "Missing Action",
            "input": {
                "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "dex": "raydium",
                "amount_sol": 0.01
            },
            "behavior": [
                "✓ Normalizes action to 'buy'",
                "✓ Proceeds with Raydium buy execution",
                "✓ Logs default action used"
            ]
        },
        {
            "name": "Signature Only (No Mint)",
            "input": {
                "signature": "xyz789...",
                "dex": "unknown"
            },
            "behavior": [
                "✓ Attempts direct_copy using signature",
                "✓ Clones original transaction structure",
                "✓ No mint required for signature-based clone"
            ]
        },
        {
            "name": "Everything Missing",
            "input": {
                "signature": "minimal_info_only..."
            },
            "behavior": [
                "✓ Normalizes DEX to 'unknown'",
                "✓ Normalizes action to 'buy'",
                "✓ Normalizes amount to 0.001 SOL",
                "✓ Attempts direct_copy with signature",
                "✗ Fails only if both mint AND signature missing"
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n  Scenario {i}: {scenario['name']}")
        logger.info(f"  {'─' * 66}")
        logger.info(f"  Input:")
        for key, value in scenario['input'].items():
            logger.info(f"    {key:15s}: {value}")
        logger.info(f"  Behavior:")
        for behavior in scenario['behavior']:
            logger.info(f"    {behavior}")


def demo_benefits():
    """Show benefits of fail-open approach"""
    logger.info("\n6️⃣  BENEFITS OF FAIL-OPEN COORDINATOR")
    logger.info("-" * 70)
    
    benefits = [
        ("Higher Execution Rate", "No stalls on missing/unparseable fields"),
        ("Better Reliability", "Sensible defaults prevent unnecessary failures"),
        ("Improved Observability", "Comprehensive logging of all decisions"),
        ("Reduced Latency", "Immediate fallback to working executors"),
        ("Graceful Degradation", "System continues functioning with partial info"),
        ("Future-Proof", "Handles new/unknown DEXes automatically"),
    ]
    
    for benefit, description in benefits:
        logger.info(f"  ✓ {benefit:25s}: {description}")


def main():
    """Run all demonstrations"""
    demo_normalization()
    demo_routing()
    demo_scenarios()
    demo_benefits()
    
    logger.info("\n" + "=" * 70)
    logger.info("END OF DEMONSTRATION")
    logger.info("=" * 70)
    logger.info("\nTo see this in action with real trades, check the execution logs")
    logger.info("Look for: [FAIL-OPEN] markers in the coordinator output")
    logger.info("")


if __name__ == "__main__":
    main()
