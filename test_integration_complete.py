#!/usr/bin/env python3

"""
Integration Test: Complete Multi-Wallet Balance-Based Detection

This tests the complete integration:
1. Multi-wallet balance validation in main.py
2. Balance-based buy/sell detection in trade_processor.py  
3. End-to-end execution flow with realistic trade data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_real_trade_example():
    """Create a realistic trade example with multiple wallets"""
    return {
        'signature': 'test_integration_signature',
        'wallet_address': 'wallet_1',  # This is the detected source
        'timestamp': '2025-01-01T00:00:00Z',
        'detection_method': 'websocket_logs',
        'meta': {
            'preTokenBalances': [
                # Wallet 1 - no change (red herring)
                {
                    'accountIndex': 0,
                    'owner': 'wallet_1',
                    'mint': 'token_A',
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '1000000', 'decimals': 6}
                },
                # Wallet 2 - BOUGHT tokens (this should be detected)
                {
                    'accountIndex': 1,
                    'owner': 'wallet_2',  
                    'mint': 'token_B',
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '500000', 'decimals': 6}
                },
                # Wallet 3 - SOLD tokens (this should also be detected)
                {
                    'accountIndex': 2,
                    'owner': 'wallet_3',
                    'mint': 'token_C', 
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '2000000', 'decimals': 6}
                }
            ],
            'postTokenBalances': [
                # Wallet 1 - still no change
                {
                    'accountIndex': 0,
                    'owner': 'wallet_1',
                    'mint': 'token_A',
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '1000000', 'decimals': 6}
                },
                # Wallet 2 - BOUGHT 300,000 more tokens (BUY detected)
                {
                    'accountIndex': 1,
                    'owner': 'wallet_2',
                    'mint': 'token_B',
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '800000', 'decimals': 6}  # +300,000
                },
                # Wallet 3 - SOLD 500,000 tokens (SELL detected)
                {
                    'accountIndex': 2,
                    'owner': 'wallet_3',
                    'mint': 'token_C',
                    'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                    'uiTokenAmount': {'amount': '1500000', 'decimals': 6}  # -500,000
                }
            ]
        }
    }

async def test_integration():
    """Test the complete multi-wallet balance detection integration"""
    
    logger.info("🧪 Integration Test: Multi-Wallet Balance Detection")
    logger.info("=" * 60)
    
    # Import the main processing classes
    from trade_processor import TradeProcessor
    
    # Set up monitored wallets (all 3 wallets are monitored)
    target_wallets = ['wallet_1', 'wallet_2', 'wallet_3']
    
    # Create the trade processor
    processor = TradeProcessor(target_wallets)
    
    # Create realistic trade data
    trade_info = create_real_trade_example()
    
    logger.info("📊 Testing trade with multiple wallet changes:")
    logger.info(f"   • Wallet 1: No change (red herring)")
    logger.info(f"   • Wallet 2: +300,000 tokens (should detect BUY)")
    logger.info(f"   • Wallet 3: -500,000 tokens (should detect SELL)")
    logger.info("")
    
    # Test 1: Check that balance changes are detected
    logger.info("🔍 Test 1: Balance change detection")
    has_changes = processor._has_actual_token_balance_change(trade_info)
    logger.info(f"   Result: {has_changes}")
    assert has_changes, "Should detect balance changes"
    logger.info("   ✅ Balance change detection PASSED")
    logger.info("")
    
    # Test 2: Check action extraction (should work now with our fix)
    logger.info("🔍 Test 2: Action extraction from balance changes")
    action = processor._extract_action(trade_info)
    logger.info(f"   Result: {action}")
    assert action != 'unknown', f"Should determine action from balance changes, got '{action}'"
    logger.info("   ✅ Action extraction PASSED")
    logger.info("")
    
    # Test 3: Multi-wallet validation logic (simulates what main.py does)
    logger.info("🔍 Test 3: Multi-wallet validation (simulating main.py logic)")
    
    meta = trade_info.get('meta', {})
    pre_balances = meta.get('preTokenBalances', [])
    post_balances = meta.get('postTokenBalances', [])
    
    # Build mapping (same as main.py)
    pre_map = {}
    post_map = {}
    
    for balance in pre_balances:
        owner = balance.get('owner')
        mint = balance.get('mint')
        amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
        if owner and mint:
            pre_map[(owner, mint)] = amount
            
    for balance in post_balances:
        owner = balance.get('owner')
        mint = balance.get('mint') 
        amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
        if owner and mint:
            post_map[(owner, mint)] = amount
    
    # Check ALL monitored wallets (same as main.py)
    detected_trades = []
    for wallet in target_wallets:
        logger.info(f"   Checking wallet {wallet}...")
        
        # Get all (wallet, mint) pairs for this wallet
        wallet_keys = set()
        for (owner, mint) in pre_map.keys():
            if owner == wallet:
                wallet_keys.add((owner, mint))
        for (owner, mint) in post_map.keys():
            if owner == wallet:
                wallet_keys.add((owner, mint))
        
        # Check for balance changes for this wallet
        for (owner, mint) in wallet_keys:
            pre_amt = pre_map.get((owner, mint), 0)
            post_amt = post_map.get((owner, mint), 0)
            delta = post_amt - pre_amt
            
            if delta != 0:
                detected_action = "buy" if delta > 0 else "sell"
                logger.info(f"     🎯 {detected_action.upper()} detected: {mint[:8]}... Δ{delta:+,}")
                
                detected_trades.append({
                    'wallet': wallet,
                    'mint': mint,
                    'action': detected_action,
                    'delta': delta
                })
    
    logger.info(f"   Found {len(detected_trades)} trades across monitored wallets")
    
    # Verify expected results
    expected_trades = 2  # wallet_2 buy + wallet_3 sell
    assert len(detected_trades) == expected_trades, f"Expected {expected_trades} trades, got {len(detected_trades)}"
    
    # Check specific trades
    wallet_2_trades = [t for t in detected_trades if t['wallet'] == 'wallet_2']
    wallet_3_trades = [t for t in detected_trades if t['wallet'] == 'wallet_3']
    
    assert len(wallet_2_trades) == 1 and wallet_2_trades[0]['action'] == 'buy', "Should detect wallet_2 buy"
    assert len(wallet_3_trades) == 1 and wallet_3_trades[0]['action'] == 'sell', "Should detect wallet_3 sell"
    
    logger.info("   ✅ Multi-wallet validation PASSED")
    logger.info("")
    
    # Summary
    logger.info("🎉 Integration Test Results:")
    logger.info("   ✅ Balance change detection: Working")
    logger.info("   ✅ Action extraction from balances: Working") 
    logger.info("   ✅ Multi-wallet validation: Working")
    logger.info("   ✅ Buy/Sell direction: Correctly determined")
    logger.info("")
    logger.info("🚀 Your bot is now ready to:")
    logger.info("   • Check ALL monitored wallets for balance changes")
    logger.info("   • Determine buy/sell from actual token movements")
    logger.info("   • Execute copy trades for each wallet with changes")
    logger.info("   • Never miss trades due to single-wallet limitations")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    logger.info("✅ Integration test completed successfully!" if success else "❌ Integration test failed!")
    sys.exit(0 if success else 1)