#!/usr/bin/env python3

import asyncio
import logging
from env_keys import EnvKeys
from config import CopyTradeConfig

logging.basicConfig(level=logging.INFO)

async def test_jupiter_copy_pipeline():
    """Test the Jupiter copy trading pipeline from main.py to execution coordinator"""
    print("\n🎯 TESTING JUPITER COPY PIPELINE")
    print("=" * 50)
    try:
        from main import SimpleCopyTradingBot
        env_keys = EnvKeys()
        config = CopyTradeConfig(
            target_wallets=['3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv'],
            investment_amount_sol=0.001,
            use_jito=False,
            slippage_tolerance=0.3
        )
        bot = SimpleCopyTradingBot(config)
        coordinator = bot.execution_coordinator
        print(f"✅ SimpleCopyTradingBot and ExecutionCoordinator initialized")
        # Simulate a Jupiter trade copy
        test_token = "So11111111111111111111111111111111111111112"  # SOL mint (for test)
        test_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"
        fake_signature = "5Qw1e2r3t4y5u6i7o8p9a0s1d2f3g4h5j6k7l8z9x0c1v2b3n4m5q6w7e8r9t0y1u2i3o4p5"  # Replace with real Jupiter tx signature for live test
        trade_info = {
            'dex': 'jupiter',
            'signature': fake_signature
        }
        print(f"\n🔍 Routing Jupiter copy trade through pipeline...")
        result = await coordinator._execute_copy_buy(
            token_mint=test_token,
            source_wallet=test_wallet,
            trade_info=trade_info,
            detected_dex='jupiter',
            amount_sol=0.001
        )
        print(f"\n📊 PIPELINE RESULT:")
        print(result)
        if result.get('success'):
            print(f"✅ Jupiter copy pipeline executed successfully!")
        else:
            print(f"❌ Jupiter copy pipeline failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jupiter_copy_pipeline())
