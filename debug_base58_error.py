#!/usr/bin/env python3
"""Debug Base58 error in account structure"""

import logging
from solders.pubkey import Pubkey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_account_addresses():
    """Test all account addresses for Base58 validity"""
    
    addresses = {
        "global_account": "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",
        "fee_recipient": "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP",
        "second_fee_recipient": "8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt",
        "fee_config": "Dq9gcfQLqpnu7M7kWBzmR2vYdWBCZm6nxgmbxXPCsqzc",
        "extra_fee_account": "Hq2wp8uJ9jCPsYgNHex8RtqdvMPfVGoYwjvF1ATiwn2Y",
        "invalid_final_fee": "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VrojVZ",
        "system_program": "11111111111111111111111111111111",
        "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "pump_program": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
        "creator_vault": "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ",
        "mint": "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump"
    }
    
    logger.info("Testing all addresses for Base58 validity...")
    
    for name, address in addresses.items():
        try:
            pubkey = Pubkey.from_string(address)
            logger.info(f"✅ {name}: {address} - VALID")
        except Exception as e:
            logger.error(f"❌ {name}: {address} - INVALID: {e}")
    
    # Test if invalid final fee is the issue
    logger.info("\n=== Testing substitution for invalid final fee ===")
    try:
        # Use fee_config as substitute for final position
        substitute = Pubkey.from_string("Dq9gcfQLqpnu7M7kWBzmR2vYdWBCZm6nxgmbxXPCsqzc")
        logger.info(f"✅ Using fee_config as substitute: {substitute}")
    except Exception as e:
        logger.error(f"❌ Fee config substitute failed: {e}")

if __name__ == "__main__":
    test_account_addresses()