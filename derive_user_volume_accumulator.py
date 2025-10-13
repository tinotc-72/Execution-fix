#!/usr/bin/env python3
"""Derive user_volume_accumulator PDA for the specific user"""

import logging
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
import os
from dotenv import load_dotenv
import base58

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def derive_user_volume_accumulator():
    """Derive user_volume_accumulator PDA"""
    
    # Get user's public key
    private_key_b58 = os.getenv("PHANTOM_PRIVATE_KEY")
    if not private_key_b58:
        logger.error("PHANTOM_PRIVATE_KEY not found in environment")
        return
        
    private_key_bytes = base58.b58decode(private_key_b58)
    from solders.keypair import Keypair
    keypair = Keypair.from_bytes(private_key_bytes)
    user_pubkey = keypair.pubkey()
    
    logger.info(f"User pubkey: {user_pubkey}")
    
    # Pump.fun program ID
    pump_program_id = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    # Try different seed combinations for user_volume_accumulator
    logger.info("Testing different seed combinations...")
    
    # Common patterns for user volume tracking
    seed_patterns = [
        [b"user-volume", bytes(user_pubkey)],
        [b"volume", bytes(user_pubkey)],
        [b"user_volume", bytes(user_pubkey)],
        [b"user-accumulator", bytes(user_pubkey)],
        [b"accumulator", bytes(user_pubkey)],
        [b"user_volume_accumulator", bytes(user_pubkey)],
    ]
    
    expected_address = "87KRgKb3dXCvMaEFk2WWaPNuf7JTVutMFjVBA3SqW9A"
    
    for i, seeds in enumerate(seed_patterns):
        try:
            pda, bump = Pubkey.find_program_address(seeds, pump_program_id)
            logger.info(f"Pattern {i+1}: {pda}")
            
            if str(pda) == expected_address:
                logger.info(f"✅ MATCH FOUND! Pattern {i+1}")
                logger.info(f"   Seeds: {[seed.decode() if isinstance(seed, bytes) and all(32 <= b <= 126 for b in seed) else seed.hex() for seed in seeds]}")
                logger.info(f"   Bump: {bump}")
                return pda, seeds, bump
                
        except Exception as e:
            logger.error(f"Pattern {i+1} failed: {e}")
    
    logger.error(f"❌ Could not derive expected address: {expected_address}")
    logger.info("The account might use a different seed pattern or additional parameters")

if __name__ == "__main__":
    derive_user_volume_accumulator()