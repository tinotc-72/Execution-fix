# Add logger setup at the top


# === MEV EXECUTOR PIPELINE TESTS ONLY ===
import logging
from mev_pumpfun_executor import MEVPumpFunExecutor
from mev_raydium_executor import MEVRaydiumExecutor
from mev_meteora_executor import MEVMeteoraExecutor, MeteoraTradeParams
from solders.keypair import Keypair
from solders.pubkey import Pubkey

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mev_executor_pipeline():
    logger.info("\n=== MEV EXECUTOR PIPELINE TESTS ===")
    # --- Pump.fun ONLY ---
    logger.info("\n--- Pump.fun Executor ---")
    import os
    from config import WALLET
    private_key = os.getenv("PHANTOM_PRIVATE_KEY")
    pumpfun_executor = MEVPumpFunExecutor(private_key)
    pumpfun_mint = "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump"  # Real Pump.fun meme coin mint
    sol_amount = float(os.getenv("TEST_AMOUNT", "0.001"))
    # Provide the original transaction signature for proper account extraction
    original_signature = "2zwXd6Ddv4xkDTBUmT3H9xd46ufwwx6Q1gMoqisYhV42UPzdE1JXv4Kp9GhcL6Vn8k6qT6LWVtKoXNSVK1pcqgGG"
    logger.info("Testing Pump.fun BUY...")
    buy_result = await pumpfun_executor.execute_buy_copy(pumpfun_mint, sol_amount, original_trade_signature=original_signature)
    logger.info(f"Pump.fun BUY result: {buy_result}")
    logger.info("Testing Pump.fun SELL...")
    sell_result = await pumpfun_executor.execute_sell_all(pumpfun_mint)
    logger.info(f"Pump.fun SELL result: {sell_result}")

async def main():
    await test_mev_executor_pipeline()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
