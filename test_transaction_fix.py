#!/usr/bin/env python3
"""
Test Transaction constructor fix
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from spl.token.instructions import create_associated_token_account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_transaction_creation():
    """Test if Transaction creation works with the new API"""
    try:
        # Create a dummy wallet and token mint
        wallet = Keypair()
        token_mint = Pubkey.from_string("5eYKhMfyHtdTbCsW2qUUQomdgsHft5GMazjjy7nowVgb")
        
        logger.info("🧪 Testing Transaction creation...")
        
        # Create an instruction (ATA creation)
        instruction = create_associated_token_account(
            payer=wallet.pubkey(),
            owner=wallet.pubkey(),
            mint=token_mint
        )
        
        logger.info("✅ Instruction created successfully")
        
        # Test new Transaction API
        transaction = Transaction.new_with_payer(
            instructions=[instruction],
            payer=wallet.pubkey()
        )
        
        logger.info("✅ Transaction created successfully with new API")
        logger.info(f"   Transaction type: {type(transaction)}")
        logger.info(f"   Payer: {transaction.message.payer if hasattr(transaction, 'message') else 'N/A'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Transaction creation failed: {e}")
        logger.error(f"   Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_transaction_creation())
    if success:
        print("🎉 Transaction constructor fix works!")
    else:
        print("❌ Transaction constructor still has issues")
