"""
Test buying token using exact PUMP router accounts from mainnet.
"""

import asyncio
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Import core components
from fast_executor import FastExecutor
from pump_trade import (
    build_buy_tx,
    TARGET_TOKEN_MINT,
    PUMP_ROUTER_STATE,
    PUMP_TOKEN_VAULT
)

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
    logger.info(f"🎯 Target token: {TARGET_TOKEN_MINT}")
    logger.info(f"📊 Using PUMP router: {PUMP_ROUTER_STATE}")
    logger.info(f"🏦 Token vault: {PUMP_TOKEN_VAULT}")

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

            # Build transaction with mainnet-exact accounts
            logger.info(f"🔧 Building transaction for {TARGET_TOKEN_MINT}...")
            tx = build_buy_tx(
                payer=keypair.pubkey(),
                amount=amount,
                slippage=0.30  # 30% slippage
            )

            if not tx:
                raise ValueError("Failed to build transaction")

            # Send and confirm
            logger.info("🚀 Sending transaction...")
            result = await executor.send_and_confirm_transaction(
                transaction=tx,
                signers=[keypair],
                confirm_timeout=60
            )

            if "error" in result:
                logger.error(f"❌ Transaction failed: {result['error']}")
                if "logs" in result:
                    logger.error("Transaction logs:")
                    for log in result["logs"]:
                        logger.error(f"  {log}")
            else:
                logger.info(f"✅ Transaction succeeded!")
                logger.info(f"📝 Signature: {result['signature']}")
                logger.info(f"🔍 Status: {result['confirmationStatus']}")
                if "logs" in result:
                    logger.info("Transaction logs:")
                    for log in result["logs"]:
                        logger.info(f"  {log}")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
