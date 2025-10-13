import asyncio
import logging
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from solders.instruction import Instruction

from config import kz
from fast_executor import FastExecutor
from jito_service import JitoClient
from wallet_tx_parser import WalletTransactionParser
from tx_builder import TransactionBuilder
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Sample Pump.fun DEX transaction logs for testing
SAMPLE_PUMP_LOGS = [
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]",
    "Program log: Instruction: Transfer",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4678 of 200000 compute units",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
    "Program 11111111111111111111111111111111 invoke [1]",
    "Program 11111111111111111111111111111111 success",
]

async def test_integrated():
    """
    Test the entire system integration:
    1. Basic RPC connectivity
    2. Jito service connectivity
    3. FastExecutor parallel submission
    4. Transaction parsing
    5. DEX trade detection and building
    6. Token amount extraction
    7. Balance tracking and confirmation
    """
    try:
        # Load wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        decoded_key = base58.b58decode(key)
        keypair = Keypair.from_bytes(decoded_key[:64])
        logger.info(f"\n🔑 Loaded wallet: {keypair.pubkey()}")

        # Initialize all components
        logger.info("\n🔄 Initializing components...")
        
        # 1. Initialize Jito Client
        jito_client = JitoClient()
        logger.info("\n📡 Testing Jito connectivity...")
        try:
            auth_status = await jito_client.test_auth()
            logger.info(f"Jito auth status: {auth_status}")
            regions = await jito_client.get_available_regions()
            logger.info(f"Available Jito regions: {regions}")
        except Exception as e:
            logger.error(f"Jito auth error: {str(e)}")

        # 2. Initialize FastExecutor
        executor = FastExecutor(keypair)
        await executor.initialize()
        
        # 3. Get initial balance
        balance = await executor.get_balance(keypair.pubkey())
        logger.info(f"\n💰 Initial balance: {balance/1e9:.4f} SOL")
        
        # 4. Test transaction parsing
        logger.info("\n🔍 Testing transaction parsing...")
        parser = WalletTransactionParser()
        parsed_trade = parser.parse_transaction_logs(SAMPLE_PUMP_LOGS)
        logger.info(f"Parsed trade result: {parsed_trade}")
        
        # 5. Test DEX trade building
        logger.info("\n🏗️ Testing DEX trade construction...")
        tx_builder = TransactionBuilder(keypair)
        
        # Create test DEX trade params
        test_params = {
            "token": "So11111111111111111111111111111111111111112",  # SOL
            "amount": 1_000_000,  # 0.001 SOL
            "is_buy": True
        }
        
        # Build DEX trade
        trade_tx = await tx_builder.build_pump_trade(
            token_address=test_params["token"],
            amount=test_params["amount"],
            is_buy=test_params["is_buy"]
        )
        
        if not trade_tx:
            raise Exception("Failed to build DEX trade transaction")
            
        logger.info(f"Built DEX trade transaction successfully")
        
        # 6. Test Jito bundle submission
        logger.info("\n📦 Testing Jito bundle submission...")
        bundle = await jito_client.create_bundle([trade_tx])
        bundle_submission = await jito_client.send_bundle(bundle)
        logger.info(f"Bundle submission result: {bundle_submission}")
        
        # 7. Test parallel RPC submission
        logger.info("\n🚀 Testing parallel RPC submission...")
        parallel_result = await executor.submit_parallel(trade_tx)
        logger.info(f"Parallel submission result: {parallel_result}")
        
        # 8. Test confirmation tracking
        logger.info("\n✅ Testing confirmation tracking...")
        confirmation = await executor.confirm_transaction(parallel_result.signature)
        logger.info(f"Transaction confirmation result: {confirmation}")
        
        logger.info("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_integrated())
