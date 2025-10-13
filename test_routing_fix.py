#!/usr/bin/env python3
"""
Test script to verify the routing fix for Raydium V4 transactions
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from execution_coordinator import ExecutionCoordinator
from config import WALLET, RPC_CLIENT
from jito_service import JitoService

async def test_routing_fix():
    """Test that raydium_v4 is now routed to meteora_damm_v2"""
    print("🧪 Testing Routing Fix for Raydium V4 -> Meteora DAMM v2")
    print("=" * 60)
    
    # Initialize coordinator
    jito_service = JitoService(WALLET)
    coordinator = ExecutionCoordinator(WALLET, RPC_CLIENT, jito_service)
    
    # Test cases
    test_cases = [
        {
            'dex_type': 'raydium_v4',
            'expected': 'meteora_damm_v2',
            'description': 'Raydium V4 should route to Meteora DAMM v2'
        },
        {
            'dex_type': 'raydium_cpmm', 
            'expected': 'meteora_damm_v2',
            'description': 'Raydium CPMM should route to Meteora DAMM v2'
        },
        {
            'dex_type': 'pumpfun',
            'expected': 'pumpfun',
            'description': 'Pump.fun should route to Pump.fun'
        },
        {
            'dex_type': 'jupiter',
            'expected': 'pumpfun',
            'description': 'Jupiter should route to Pump.fun (fallback)'
        }
    ]
    
    # Test each case
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"   Input DEX: {test_case['dex_type']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Create trade_info with dex_type
        trade_info = {'dex_type': test_case['dex_type']}
        
        # Test the routing
        result = await coordinator._detect_token_platform('dummy_token', trade_info)
        
        print(f"   Actual: {result}")
        
        if result == test_case['expected']:
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED - Expected {test_case['expected']}, got {result}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Routing fix is working correctly.")
        print("✅ Raydium V4 transactions will now use Meteora DAMM v2 executor")
        print("✅ This should resolve the failed transaction issue!")
    else:
        print("❌ SOME TESTS FAILED! Please check the routing logic.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_routing_fix())
