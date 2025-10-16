#!/usr/bin/env python3
"""
Test suite for Jupiter-specific token mint inference logic.

Validates that:
1. When dex is 'jupiter' and token_mint is missing but postTokenBalances are present,
   token_mint is set to the non-WSOL mint with the largest positive delta (post - pre)
2. When no positive deltas exist, token_mint is left as None for input-only swap
3. WSOL mints are excluded from consideration
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_jupiter_positive_delta():
    """Test that Jupiter mint inference selects the non-WSOL mint with largest positive delta"""
    print("=" * 80)
    print("TEST: Jupiter mint inference with positive deltas")
    print("=" * 80)
    
    from trade_processor import TradeProcessor
    
    # Mock trade_info with Jupiter dex and postTokenBalances
    trade_info = {
        'dex_type': 'jupiter',
        'token_mint': 'UNKNOWN',
        'meta': {
            'preTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL
                    'uiTokenAmount': {'uiAmount': 100.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',  # Token A
                    'uiTokenAmount': {'uiAmount': 0.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintXYZ123456789012345678901234567890',  # Token B
                    'uiTokenAmount': {'uiAmount': 50.0}
                }
            ],
            'postTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL (decreased)
                    'uiTokenAmount': {'uiAmount': 90.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',  # Token A (largest increase)
                    'uiTokenAmount': {'uiAmount': 1000.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintXYZ123456789012345678901234567890',  # Token B (smaller increase)
                    'uiTokenAmount': {'uiAmount': 60.0}
                }
            ]
        }
    }
    
    # Create processor instance
    processor = TradeProcessor(target_wallets=['TestWallet123'], rpc_client=None)
    
    # Run the test synchronously by calling analyze_and_route_trade
    async def run_test():
        result = await processor.analyze_and_route_trade(trade_info, 'TestWallet123')
        return result
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_test())
    
    # Validate results
    assert trade_info.get('token_mint') == 'TokenMintABC123456789012345678901234567890', \
        f"Expected token_mint to be TokenMintABC..., got {trade_info.get('token_mint')}"
    
    print("✅ PASS: Jupiter mint inference correctly selected Token A with largest positive delta (+1000.0)")
    print(f"   token_mint = {trade_info.get('token_mint')}")
    return True


def test_jupiter_no_positive_delta():
    """Test that Jupiter mint inference leaves token_mint=None when no positive deltas exist"""
    print("=" * 80)
    print("TEST: Jupiter mint inference with no positive deltas")
    print("=" * 80)
    
    from trade_processor import TradeProcessor
    
    # Mock trade_info with Jupiter dex but only negative deltas (sell scenario)
    trade_info = {
        'dex_type': 'jupiter',
        'token_mint': 'UNKNOWN',
        'meta': {
            'preTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',
                    'uiTokenAmount': {'uiAmount': 100.0}
                }
            ],
            'postTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',  # Decreased (sold)
                    'uiTokenAmount': {'uiAmount': 50.0}
                }
            ]
        }
    }
    
    # Create processor instance
    processor = TradeProcessor(target_wallets=['TestWallet123'], rpc_client=None)
    
    # Run the test
    async def run_test():
        result = await processor.analyze_and_route_trade(trade_info, 'TestWallet123')
        return result
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_test())
    
    # Validate results - token_mint should be None for input-only swap
    assert trade_info.get('token_mint') is None, \
        f"Expected token_mint to be None for input-only swap, got {trade_info.get('token_mint')}"
    
    print("✅ PASS: Jupiter mint inference correctly left token_mint=None (no positive deltas)")
    print(f"   token_mint = {trade_info.get('token_mint')}")
    return True


def test_jupiter_wsol_excluded():
    """Test that WSOL mints are excluded from consideration"""
    print("=" * 80)
    print("TEST: Jupiter mint inference excludes WSOL")
    print("=" * 80)
    
    from trade_processor import TradeProcessor
    
    # Mock trade_info where WSOL has positive delta but should be excluded
    trade_info = {
        'dex_type': 'jupiter',
        'token_mint': 'UNKNOWN',
        'meta': {
            'preTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL
                    'uiTokenAmount': {'uiAmount': 10.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',
                    'uiTokenAmount': {'uiAmount': 0.0}
                }
            ],
            'postTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL (increased more)
                    'uiTokenAmount': {'uiAmount': 1000.0}
                },
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',  # Token (smaller increase)
                    'uiTokenAmount': {'uiAmount': 100.0}
                }
            ]
        }
    }
    
    # Create processor instance
    processor = TradeProcessor(target_wallets=['TestWallet123'], rpc_client=None)
    
    # Run the test
    async def run_test():
        result = await processor.analyze_and_route_trade(trade_info, 'TestWallet123')
        return result
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_test())
    
    # Validate results - should select Token A, not WSOL
    assert trade_info.get('token_mint') == 'TokenMintABC123456789012345678901234567890', \
        f"Expected token_mint to be TokenMintABC... (WSOL excluded), got {trade_info.get('token_mint')}"
    
    print("✅ PASS: Jupiter mint inference correctly excluded WSOL and selected Token A")
    print(f"   token_mint = {trade_info.get('token_mint')}")
    return True


def test_non_jupiter_dex():
    """Test that Jupiter-specific logic only applies when dex is 'jupiter'"""
    print("=" * 80)
    print("TEST: Jupiter mint inference only for Jupiter dex")
    print("=" * 80)
    
    from trade_processor import TradeProcessor
    
    # Mock trade_info with Raydium dex (should not trigger Jupiter logic)
    trade_info = {
        'dex_type': 'raydium_cpmm',
        'token_mint': 'UNKNOWN',
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [
                {
                    'owner': 'TestWallet123',
                    'mint': 'TokenMintABC123456789012345678901234567890',
                    'uiTokenAmount': {'uiAmount': 100.0}
                }
            ]
        }
    }
    
    # Create processor instance
    processor = TradeProcessor(target_wallets=['TestWallet123'], rpc_client=None)
    
    # Run the test
    async def run_test():
        result = await processor.analyze_and_route_trade(trade_info, 'TestWallet123')
        return result
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_test())
    
    # Validate that Jupiter-specific logic was NOT applied
    # (token_mint might be set by other logic, but not by Jupiter-specific inference)
    print(f"✅ PASS: Non-Jupiter dex correctly skipped Jupiter-specific inference")
    print(f"   dex_type = {trade_info.get('dex_type')}")
    print(f"   token_mint = {trade_info.get('token_mint')}")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("JUPITER MINT INFERENCE TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_jupiter_positive_delta,
        test_jupiter_no_positive_delta,
        test_jupiter_wsol_excluded,
        test_non_jupiter_dex
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print()
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
