#!/usr/bin/env python3
"""Get exact 16-account structure from successful transaction"""

import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey
from solders.signature import Signature
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_exact_account_structure():
    """Get the exact 16-account structure from successful transaction"""
    
    # Use the successful transaction we found earlier
    successful_tx_sig = "4ocpfga6nVxwf9YpfzG3GzK6qHg2yBF7wUxzQ8SJTSMrhu2V7J7PViX5NYAPF9CVMR2WA4ERfRLujJVC7MbCXo51"
    
    rpc_url = os.getenv("HELIUS_RPC_URL")
    if not rpc_url:
        logger.error("HELIUS_RPC_URL not found in environment")
        return
    
    client = AsyncClient(rpc_url)
    
    try:
        signature = Signature.from_string(successful_tx_sig)
        
        # Get transaction details with max supported version
        response = await client.get_transaction(
            signature,
            encoding="jsonParsed",
            commitment=Commitment("confirmed"),
            max_supported_transaction_version=0
        )
        
        if not response.value:
            logger.error("Transaction not found")
            return
            
        transaction = response.value.transaction
        
        # Find the Pump.fun buy instruction
        pump_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        buy_instruction = None
        
        for instruction in transaction.transaction.message.instructions:
            if hasattr(instruction, 'program_id'):
                if str(instruction.program_id) == pump_program_id:
                    buy_instruction = instruction
                    break
        
        if not buy_instruction:
            logger.error("Pump.fun buy instruction not found")
            return
            
        logger.info(f"Found Pump.fun instruction with {len(buy_instruction.accounts)} accounts")
        
        # Get all account keys from the message
        account_keys = []
        if hasattr(transaction.transaction.message, 'account_keys'):
            for key in transaction.transaction.message.account_keys:
                if hasattr(key, 'pubkey'):
                    account_keys.append(str(key.pubkey))
                else:
                    account_keys.append(str(key))
        
        # Map account indices to actual addresses
        logger.info("\n=== EXACT 16-ACCOUNT STRUCTURE ===")
        for i, account_ref in enumerate(buy_instruction.accounts):
            # Handle both index-based and direct pubkey references
            if isinstance(account_ref, int):
                if account_ref < len(account_keys):
                    account_address = account_keys[account_ref]
                    logger.info(f"[{i:2d}] {account_address}")
                else:
                    logger.warning(f"[{i:2d}] Index {account_ref} out of range")
            else:
                # Direct pubkey reference
                account_address = str(account_ref)
                logger.info(f"[{i:2d}] {account_address}")
        
        # Provide the exact structure for the bot
        if len(buy_instruction.accounts) >= 16:
            logger.info("\n=== ACCOUNT STRUCTURE FOR BOT ===")
            logger.info("# Use these exact account addresses in positions [12-15]:")
            
            for i in range(12, min(16, len(buy_instruction.accounts))):
                account_ref = buy_instruction.accounts[i]
                if isinstance(account_ref, int):
                    if account_ref < len(account_keys):
                        account_address = account_keys[account_ref]
                        logger.info(f"# Position [{i}]: {account_address}")
                else:
                    account_address = str(account_ref)
                    logger.info(f"# Position [{i}]: {account_address}")
                    
        else:
            logger.warning(f"Expected 16 accounts, found {len(buy_instruction.accounts)}")
            
    except Exception as e:
        logger.error(f"Error analyzing transaction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_exact_account_structure())