"""
Check if the PDA was created in the last transaction and test a buy-only transaction.
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from fast_executor import FastExecutor
from minimal_tx_builder import get_user_pda_with_bump
from env_keys import EnvKeys
from config import WALLET

# Load environment keys
keys = EnvKeys()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RPC endpoints
RPC_ENDPOINTS = [keys.HELIUS_RPC_URL, keys.PUBLIC_RPC_URL]

async def check_pda_status():
    """Check if the PDA was created after the last transaction."""
    try:
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            # Get the PDA
            user_pda, bump = get_user_pda_with_bump(WALLET.pubkey())
            logger.info(f"🔍 Checking User PDA: {user_pda}")
            
            # Get account info
            account = await executor.get_account_info(user_pda)
            if account:
                logger.info("✅ PDA account now exists!")
                logger.info(f"Owner: {account.get('owner')}")
                logger.info(f"Lamports: {account.get('lamports')}")
                data = account.get('data', [])
                if data and len(data) > 0:
                    logger.info(f"Data length: {len(data[0])} bytes")
                return True
            else:
                logger.info("❌ PDA account still does not exist")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error checking PDA: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(check_pda_status())
