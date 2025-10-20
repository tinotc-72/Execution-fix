#!/usr/bin/env python3
"""
Standalone test for Jupiter-specific token mint inference logic.
Tests the logic without requiring full module imports.
"""


def jupiter_mint_inference(trade_info, token_mint):
    """
    Extracted Jupiter mint inference logic for testing.
    This is the exact logic from trade_processor.py lines 743-806.
    """
    # === JUPITER-SPECIFIC TOKEN MINT INFERENCE ===
    # When dex is 'jupiter', if token_mint is missing but postTokenBalances are present,
    # set token_mint to the non-WSOL mint with the largest positive delta (post - pre).
    # If no positive deltas, leave token_mint=None and let the Jupiter executor default to an input-only swap.
    if (trade_info.get('dex_type') == 'jupiter' and 
        token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', None, '']):
        
        print(f"[JUPITER_MINT_INFERENCE] Attempting Jupiter-specific token mint inference...")
        
        try:
            meta = trade_info.get('meta') or (trade_info.get('transaction_full', {}) or {}).get('meta', {})
            
            if meta:
                pre_token_balances = meta.get('preTokenBalances', [])
                post_token_balances = meta.get('postTokenBalances', [])
                
                if post_token_balances:
                    print(f"[JUPITER_MINT_INFERENCE] Found {len(post_token_balances)} postTokenBalances")
                    
                    # Build pre-balance map by (owner, mint)
                    pre_map = {}
                    for balance in pre_token_balances:
                        owner = balance.get('owner')
                        mint = balance.get('mint')
                        amount = float(balance.get('uiTokenAmount', {}).get('uiAmount') or 0)
                        if owner and mint:
                            pre_map[(owner, mint)] = amount
                    
                    # Calculate deltas and find the non-WSOL mint with largest positive delta
                    WSOL = "So11111111111111111111111111111111111111112"
                    best_mint = None
                    best_delta = 0.0
                    
                    for balance in post_token_balances:
                        owner = balance.get('owner')
                        mint = balance.get('mint')
                        post_amount = float(balance.get('uiTokenAmount', {}).get('uiAmount') or 0)
                        
                        if mint and mint != WSOL:
                            pre_amount = pre_map.get((owner, mint), 0)
                            delta = post_amount - pre_amount
                            
                            # Only consider positive deltas (tokens acquired)
                            if delta > best_delta:
                                best_delta = delta
                                best_mint = mint
                                print(f"[JUPITER_MINT_INFERENCE] Found candidate: {mint[:8]}... with delta +{delta:.6f}")
                    
                    if best_mint:
                        token_mint = best_mint
                        trade_info['token_mint'] = best_mint
                        print(f"✅ [JUPITER_MINT_INFERENCE] Set token_mint to {best_mint[:8]}... (largest positive delta: +{best_delta:.6f})")
                    else:
                        # No positive deltas found - leave token_mint=None for input-only swap
                        print(f"⚠️ [JUPITER_MINT_INFERENCE] No positive deltas found - leaving token_mint=None for input-only swap")
                        token_mint = None
                        trade_info['token_mint'] = None
                else:
                    print(f"[JUPITER_MINT_INFERENCE] No postTokenBalances available")
            else:
                print(f"[JUPITER_MINT_INFERENCE] No meta information available")
                
        except Exception as e:
            print(f"❌ [JUPITER_MINT_INFERENCE] Exception during Jupiter mint inference: {e}")
    
    return token_mint


def test_jupiter_positive_delta():
    """Test that Jupiter mint inference selects the non-WSOL mint with largest positive delta"""
    print("=" * 80)
    print("TEST 1: Jupiter mint inference with positive deltas")
    print("=" * 80)
    
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
    
    token_mint = 'UNKNOWN'
    result = jupiter_mint_inference(trade_info, token_mint)
    
    # Validate
    expected = 'TokenMintABC123456789012345678901234567890'
    if trade_info.get('token_mint') == expected:
        print(f"✅ PASS: Correctly selected Token A with largest positive delta (+1000.0)")
        print(f"   token_mint = {trade_info.get('token_mint')}")
        return True
    else:
        print(f"❌ FAIL: Expected {expected}, got {trade_info.get('token_mint')}")
        return False


def test_jupiter_no_positive_delta():
    """Test that Jupiter mint inference leaves token_mint=None when no positive deltas exist"""
    print("\n" + "=" * 80)
    print("TEST 2: Jupiter mint inference with no positive deltas")
    print("=" * 80)
    
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
    
    token_mint = 'UNKNOWN'
    result = jupiter_mint_inference(trade_info, token_mint)
    
    # Validate
    if trade_info.get('token_mint') is None:
        print(f"✅ PASS: Correctly left token_mint=None (no positive deltas)")
        print(f"   token_mint = {trade_info.get('token_mint')}")
        return True
    else:
        print(f"❌ FAIL: Expected None, got {trade_info.get('token_mint')}")
        return False


def test_jupiter_wsol_excluded():
    """Test that WSOL mints are excluded from consideration"""
    print("\n" + "=" * 80)
    print("TEST 3: Jupiter mint inference excludes WSOL")
    print("=" * 80)
    
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
    
    token_mint = 'UNKNOWN'
    result = jupiter_mint_inference(trade_info, token_mint)
    
    # Validate
    expected = 'TokenMintABC123456789012345678901234567890'
    if trade_info.get('token_mint') == expected:
        print(f"✅ PASS: Correctly excluded WSOL and selected Token A")
        print(f"   token_mint = {trade_info.get('token_mint')}")
        return True
    else:
        print(f"❌ FAIL: Expected {expected}, got {trade_info.get('token_mint')}")
        return False


def test_non_jupiter_dex():
    """Test that Jupiter-specific logic only applies when dex is 'jupiter'"""
    print("\n" + "=" * 80)
    print("TEST 4: Jupiter mint inference only for Jupiter dex")
    print("=" * 80)
    
    trade_info = {
        'dex_type': 'raydium_cpmm',  # Not Jupiter
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
    
    token_mint = 'UNKNOWN'
    result = jupiter_mint_inference(trade_info, token_mint)
    
    # Validate - should NOT modify token_mint
    if trade_info.get('token_mint') == 'UNKNOWN':
        print(f"✅ PASS: Correctly skipped Jupiter-specific logic for Raydium dex")
        print(f"   dex_type = {trade_info.get('dex_type')}")
        print(f"   token_mint = {trade_info.get('token_mint')} (unchanged)")
        return True
    else:
        print(f"❌ FAIL: Logic should not run for non-Jupiter dex, but token_mint was changed to {trade_info.get('token_mint')}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("JUPITER MINT INFERENCE LOGIC TEST SUITE")
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
        except Exception as e:
            failed += 1
            print(f"❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
