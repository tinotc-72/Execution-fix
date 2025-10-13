#!/usr/bin/env python3
"""
Test the fixed Jito-first execution
This script tests whether the _build_optimal_transaction fix resolves the issue
"""

import asyncio
import logging
from config import WALLET
from main import CopyTradingBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_jito_fix():
    """Test the Jito-first execution fix"""
    try:
        print("🧪 Testing Jito-first execution fix...")
        
        # Initialize the bot with default config
        from dataclasses import dataclass, field
        from typing import List, Dict
        
        @dataclass
        class TestConfig:
            target_wallets: List[str] = field(default_factory=lambda: ["test_wallet"])
            investment_amount_sol: float = 0.001
            max_positions: int = 10
            min_sell_threshold: float = 0.1
            use_jito: bool = True
            jito_timeout: float = 10.0
            slippage_tolerance: float = 0.30
            slippage_bps: int = 3000
            enable_dexes: Dict[str, bool] = field(default_factory=lambda: {
                "jupiter": True,
                "pumpfun": True,
                "orca": True,
                "raydium": True
            })
        
        config = TestConfig()
        bot = CopyTradingBot(config)
        await bot.initialize()
        
        # Test token mint (using a known token)
        test_token = "So11111111111111111111111111111111111111112"  # SOL mint for testing
        
        print(f"🔍 Testing _build_optimal_transaction...")
        
        # Test the fixed _build_optimal_transaction method
        transaction = await bot._build_optimal_transaction(test_token)
        
        if transaction:
            print(f"✅ SUCCESS: _build_optimal_transaction returned a transaction!")
            print(f"   📊 Transaction type: {type(transaction)}")
            print(f"   🔧 This means Jito-first execution will now work!")
        else:
            print(f"❌ ISSUE: _build_optimal_transaction still returns None")
            print(f"   💡 This means we need to check Jupiter route availability")
        
        print(f"\n🔍 Testing _try_jito_first_execution...")
        
        # Test the full Jito execution method
        extra_params = {}
        jito_result = await bot._try_jito_first_execution(
            test_token, "test_wallet", None, extra_params
        )
        
        if jito_result:
            print(f"✅ SUCCESS: _try_jito_first_execution returned result!")
            print(f"   📊 Result: {jito_result}")
        else:
            print(f"❌ ISSUE: _try_jito_first_execution returned None")
            print(f"   💡 This means Jupiter route building failed")
            
        await bot.close()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jito_fix())
