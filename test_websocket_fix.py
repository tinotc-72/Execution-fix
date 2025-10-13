#!/usr/bin/env python3
"""
Quick Test: Verify our WebSocket fix works with the confirmed sell transaction
"""

import asyncio
from test_websocket_connection import OptimizedWebSocketMonitor

async def test_websocket_fix():
    """Test that our updated WebSocket correctly detects the sell transaction"""
    
    print("🧪 TESTING UPDATED WEBSOCKET DETECTION")
    print("=" * 50)
    
    # Create a mock transaction notification like what we'd receive from WebSocket
    target_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    sell_signature = "2oAemxGqPk3pY3A1hGrV3q91EeBtAVLJ1ez8LM2KrMeGwTT2Xa3pa9ZgzU5U7aMcyoDMPegpKhr1eZhGpAgsxEwW"
    
    # Test the new balance-based detection directly
    monitor = OptimizedWebSocketMonitor([target_wallet])
    
    print(f"🔍 Testing balance detection on confirmed SELL transaction:")
    print(f"   Signature: {sell_signature[:12]}...")
    print(f"   Wallet: {target_wallet[:8]}...")
    print()
    
    # Test the new method
    result = await monitor._get_proper_buy_sell_detection(sell_signature, target_wallet)
    
    print(f"\n🎯 RESULT: {result.upper()}")
    
    if result == 'sell':
        print("✅ SUCCESS! WebSocket will now correctly detect SELL transactions")
        print("🔧 Our balance-based fix works!")
    elif result == 'buy':
        print("❌ STILL WRONG! Need to debug further...")
    else:
        print("❓ INCONCLUSIVE: Returned 'trade' - need refinement")
    
    print(f"\n📋 SUMMARY:")
    print(f"   - Old method: WRONG (classified as BUY)")
    print(f"   - New method: {result.upper()}")
    print(f"   - Expected: SELL")
    print(f"   - Fixed: {'✅ YES' if result == 'sell' else '❌ NO'}")

if __name__ == "__main__":
    asyncio.run(test_websocket_fix())
