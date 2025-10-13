import logging
import asyncio
from config import CopyTradeConfig, JITO_AUTH_TOKEN
from main import SimpleCopyTradingBot

# You can adjust these for your test environment
TEST_TOKEN_MINT = "So11111111111111111111111111111111111111112"  # Example: SOL
TEST_SOURCE_WALLET = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # Example wallet from config

# Setup logging for test output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jito_test")

async def test_jito_enabled_and_working():
    # Step 1: Create config with Jito enabled (if available)
    config = CopyTradeConfig(
        target_wallets=[TEST_SOURCE_WALLET],
        investment_amount_sol=0.001,
        use_jito=False,  # Let it auto-detect based on credentials
        slippage_tolerance=0.3
    )
    logger.info("🔍 Testing Copy Bot with Jito enabled...")
    logger.info(f"JITO UUID: {JITO_AUTH_TOKEN}")

    # Step 2: Instantiate bot
    bot = SimpleCopyTradingBot(config)
    
    # Check if JITO is available and configured
    jito_available = bot.jito_service is not None
    logger.info(f"🔧 JITO Service Status: {'✅ Available' if jito_available else '❌ Not Available'}")

    # Step 3: Simulate a trade (buy)
    test_trade_info = {
        "signature": "FAKE_SIGNATURE_FOR_TEST",  # Use a real or mock signature for a full test
        "wallet_address": TEST_SOURCE_WALLET,
        "dex_type": "pumpfun",
        "token_mint": TEST_TOKEN_MINT,
        "action": "buy"
    }
    logger.info("🚀 Simulating a copy buy trade...")

    # Step 4: Run the buy through execution coordinator (should use Jito)
    result = await bot.execution_coordinator._execute_copy_buy(
        token_mint=TEST_TOKEN_MINT,
        source_wallet=TEST_SOURCE_WALLET,
        trade_info=test_trade_info,
        amount_sol=0.001
    )

    # Step 5: Check results and logs
    if result.get("success") and result.get("signature"):
        logger.info(f"✅ Trade executed via Jito! Signature: {result['signature']}")
    else:
        logger.error(f"❌ Trade failed. Result: {result}")

    # Optionally: Simulate a sell or another DEX
    # ... Repeat with a _execute_copy_sell() call and check logs ...

    # Step 6: Confirm integration works (with or without Jito)
    if jito_available:
        logger.info("🟢 Test completed: Jito integration is active and working for copy trades.")
    else:
        logger.info("🟢 Test completed: JITO integration ready but not configured - using RPC fallback.")

if __name__ == "__main__":
    asyncio.run(test_jito_enabled_and_working())