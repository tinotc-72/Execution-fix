#!/usr/bin/env python3
"""
Test token compatibility validation
"""

import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from env_keys import EnvKeys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_token_compatibility():
    """Test token compatibility for the problematic token"""
    try:
        env = EnvKeys()
        rpc_client = AsyncClient(env.HELIUS_RPC_URL)
        
        # Test with the problematic token from the logs
        token_mint = "5eYKhMfyHtdTbCsW2qUUQomdgsHft5GMazjjy7nowVgb"
        
        logger.info(f"🧪 Testing token compatibility for: {token_mint}")
        
        token_pubkey = Pubkey.from_string(token_mint)
        
        # Get token account info
        account_info = await rpc_client.get_account_info(token_pubkey)
        
        if not account_info.value:
            logger.error("❌ Token account does not exist")
            return False
        
        logger.info(f"✅ Token account exists")
        logger.info(f"   Owner: {account_info.value.owner}")
        logger.info(f"   Data length: {len(account_info.value.data)}")
        
        # Check if owned by Token Program
        token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        if account_info.value.owner == token_program:
            logger.info("✅ Token is owned by SPL Token Program")
        else:
            logger.warning(f"⚠️  Token is NOT owned by SPL Token Program")
            logger.warning(f"   Actual owner: {account_info.value.owner}")
        
        await rpc_client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Token compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_token_compatibility())
    if success:
        print("🎉 Token compatibility test completed!")
    else:
        print("❌ Token compatibility test failed")
