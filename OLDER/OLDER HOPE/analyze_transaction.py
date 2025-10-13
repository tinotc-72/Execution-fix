#!/usr/bin/env python3
"""
Script to analyze Solana transactions using a provided transaction signature.
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transaction_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def analyze_transaction(signature: str):
    """Analyze a Solana transaction using its signature."""
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)

    try:
        logger.info(f"🔍 Analyzing transaction: {signature}")

        # Convert signature to bytes
        signature_bytes = bytes.fromhex(signature)

        # Fetch transaction details
        transaction_details = await client.get_transaction(signature_bytes)

        if not transaction_details.value:
            logger.error(f"❌ Transaction not found: {signature}")
            return None

        logger.info("✅ Transaction details fetched successfully")

        # Extract relevant information
        transaction_info = transaction_details.value
        meta = transaction_info.get('meta', {})
        pre_balances = meta.get('preBalances', [])
        post_balances = meta.get('postBalances', [])
        token_balances = meta.get('postTokenBalances', [])

        logger.info(f"Pre-balances: {pre_balances}")
        logger.info(f"Post-balances: {post_balances}")
        logger.info(f"Token balances: {token_balances}")

        # Return structured analysis
        return {
            'signature': signature,
            'pre_balances': pre_balances,
            'post_balances': post_balances,
            'token_balances': token_balances,
            'status': meta.get('status', {}).get('Ok', 'Failed')
        }

    except Exception as e:
        logger.error(f"❌ Error analyzing transaction: {e}")
        return None

    finally:
        await client.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze_transaction.py <transaction_signature>")
        sys.exit(1)

    signature = sys.argv[1]

    asyncio.run(analyze_transaction(signature))
