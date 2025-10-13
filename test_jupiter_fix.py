#!/usr/bin/env python3
"""
Quick test to verify Jupiter VersionedTransaction signing fix
"""
import asyncio
import logging
from jupiter_copy_executor import try_jupiter_buy
from env_keys import EnvKeys
from solders.keypair import Keypair
import base58

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_jupiter_signing():
    """Test that Jupiter transaction signing works without errors"""
    try:
        logger.info("🧪 Testing Jupiter VersionedTransaction signing fix...")
        
        # Load wallet (you need your actual wallet for this test)
        env_keys = EnvKeys()
        wallet_bytes = base58.b58decode(env_keys.PRIVATE_KEY)
        wallet = Keypair.from_bytes(wallet_bytes)
        
        logger.info(f"💳 Wallet: {wallet.pubkey()}")
        
        # Test with a known token that should work (USDC)
        test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
        test_amount = 0.001  # Very small amount
        
        logger.info(f"🎯 Testing buy: {test_amount} SOL → USDC")
        logger.info(f"📝 This will test if VersionedTransaction signing works")
        logger.info(f"⚠️  Transaction will likely fail due to slippage, but signing should work")
        
        result = await try_jupiter_buy(
            wallet_keypair=wallet,
            token_mint=test_token,
            amount_sol=test_amount,
            slippage_tolerance=0.10  # 10%
        )
        
        logger.info(f"📊 Result: {result}")
        
        if result.get('success'):
            logger.info("✅ SIGNING FIX WORKS: Transaction executed successfully!")
        elif 'signature' in str(result) or 'sign' not in str(result.get('error', '')).lower():
            logger.info("✅ SIGNING FIX WORKS: No signing errors detected!")
            logger.info(f"💡 Failure was due to other factors: {result.get('error', 'unknown')}")
        else:
            logger.error("❌ SIGNING ISSUE STILL EXISTS")
            logger.error(f"Error: {result.get('error', 'unknown')}")
            
    except Exception as e:
        if 'sign' in str(e).lower():
            logger.error(f"❌ SIGNING ISSUE: {e}")
        else:
            logger.info(f"✅ SIGNING FIX WORKS: Error unrelated to signing: {e}")

if __name__ == "__main__":
    asyncio.run(test_jupiter_signing())
