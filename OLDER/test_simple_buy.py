"""
Simple test script to try regular buy instruction without PDA initialization.
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Local imports
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import create_buy_instruction, get_associated_token_address
from env_keys import EnvKeys

# Load environment keys
keys = EnvKeys()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('simple_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
TARGET_TOKEN_MINT = "5qCtARHJfxANZyczUokjjSA8rthDoMBVBxoTosPfbonk"
AMOUNT_IN_LAMPORTS = 10_000_000  # 0.01 SOL
SLIPPAGE_BPS = 300  # 3%

# RPC endpoints
RPC_ENDPOINTS = [keys.HELIUS_RPC_URL, keys.PUBLIC_RPC_URL]

async def test_simple_buy():
    """Test a simple buy instruction without PDA initialization."""
    try:
        logger.info("🧪 Starting simple buy test")
        
        wallet = WALLET
        token_mint = Pubkey.from_string(TARGET_TOKEN_MINT)
        amount = AMOUNT_IN_LAMPORTS
        
        # Get token ATA
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        logger.info(f"Token ATA: {token_ata}")
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check balance
            balance = await executor.get_balance(wallet.pubkey())
            logger.info(f"Wallet balance: {balance/1e9:.6f} SOL")
            
            # Create simple buy instruction
            logger.info("Creating buy instruction...")
            buy_ix = await create_buy_instruction(
                token_mint=token_mint,
                owner=wallet.pubkey(),
                amount=amount,
                slippage_bps=SLIPPAGE_BPS,
                token_ata=token_ata
            )
            
            logger.info(f"Buy instruction created: {buy_ix}")
            logger.info(f"Program ID: {buy_ix.program_id}")
            logger.info(f"Data length: {len(buy_ix.data)}")
            logger.info(f"Data (hex): {buy_ix.data.hex()}")
            logger.info(f"Account count: {len(buy_ix.accounts)}")
            
            # Log accounts
            for i, acc in enumerate(buy_ix.accounts):
                logger.info(f"  Account {i}: {acc.pubkey} (signer={acc.is_signer}, writable={acc.is_writable})")
            
            logger.info("✅ Simple buy instruction test completed")
            
    except Exception as e:
        logger.error(f"❌ Error in simple buy test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_simple_buy())
