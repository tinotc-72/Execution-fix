"""
Test buying meme coin using exact PUMP router instruction from mainnet
"""

import asyncio
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Import core components
from fast_executor import FastExecutor
from minimal_tx_builder import build_meme_buy_tx, build_sell_tx, MEME_MINT

# Import config and setup logging
from config import WALLET_PRIVATE_KEY, HELIUS_RPC_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_execution.log')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Test buying using PUMP router with exact mainnet instruction"""
    print("\n🧪 Starting PUMP Buy Test")
    print("=" * 24)

    # Load wallet
    keypair = Keypair.from_bytes(WALLET_PRIVATE_KEY)
    logger.info(f"🔑 Wallet loaded: {keypair.pubkey()}")

    # Initialize executor
    async with FastExecutor(
        keypair=keypair,
        rpc_urls=[HELIUS_RPC_URL],
        health_check_timeout=10.0
    ) as executor:
        try:
            # Check SOL balance
            balance = await executor.get_balance(keypair.pubkey())
            logger.info(f"💰 SOL Balance: {balance / 1e9:.4f} SOL")

            if balance < 0.05 * 1e9:  # 0.05 SOL minimum
                raise ValueError("Insufficient SOL balance")

            # Amount to test with (0.01 SOL)
            amount = int(0.01 * 1e9)
            logger.info(f"🎯 Test amount: {amount / 1e9:.4f} SOL")

            # === BUY ===
            logger.info("🔧 Building meme coin BUY transaction...")
            tx = await build_meme_buy_tx(
                payer=keypair.pubkey(),
                keypair=keypair,
                executor=executor
            )

            if not tx:
                raise ValueError("Failed to build buy transaction")

            # Send and confirm BUY transaction
            logger.info("🚀 Sending BUY transaction...")
            result = await executor.send_and_confirm_transaction(
                transaction=tx,
                signers=[keypair],
                confirm_timeout=60
            )

            if "error" in result:
                logger.error(f"❌ BUY failed: {result['error']}")
                if "logs" in result:
                    logger.error("BUY transaction logs:")
                    for log in result["logs"]:
                        logger.error(f"  {log}")
            else:
                logger.info(f"✅ BUY succeeded! Signature: {result['signature']}")
                logger.info(f"🔍 Status: {result['confirmationStatus']}")
                if "logs" in result:
                    logger.info("BUY transaction logs:")
                    for log in result["logs"]:
                        logger.info(f"  {log}")

            # === SELL ===
            logger.info("🔧 Building meme coin SELL transaction...")
            # For demo, sell a small amount (e.g. 1 token, adjust decimals as needed)
            sell_amount = 1_000_000  # 1 token if 6 decimals
            tx_sell = await build_sell_tx(
                executor,
                Pubkey.from_string(MEME_MINT),
                sell_amount,
                keypair
            )

            if not tx_sell:
                raise ValueError("Failed to build sell transaction")

            # Send and confirm SELL transaction
            logger.info("🚀 Sending SELL transaction...")
            result_sell = await executor.send_and_confirm_transaction(
                transaction=tx_sell,
                signers=[keypair],
                confirm_timeout=60
            )

            if "error" in result_sell:
                logger.error(f"❌ SELL failed: {result_sell['error']}")
                if "logs" in result_sell:
                    logger.error("SELL transaction logs:")
                    for log in result_sell["logs"]:
                        logger.error(f"  {log}")
            else:
                logger.info(f"✅ SELL succeeded! Signature: {result_sell['signature']}")
                logger.info(f"🔍 Status: {result_sell['confirmationStatus']}")
                if "logs" in result_sell:
                    logger.info("SELL transaction logs:")
                    for log in result_sell["logs"]:
                        logger.info(f"  {log}")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
