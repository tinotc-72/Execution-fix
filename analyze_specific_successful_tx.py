#!/usr/bin/env python3
"""Analyze specific successful transaction to get exact account structure"""

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

async def analyze_successful_transaction():
    """Analyze the specific successful transaction"""
    
    # Transaction signature provided by user
    tx_sig = "2vfarAcNVQJVG5WMbKpzQBiJpmW4Eq4eGHcD7uAdxjTx1FDXuWFQrN3UnDTQn8bYgUUfY6QG1MP9bDBwJu3ECETF"
    
    rpc_url = os.getenv("HELIUS_RPC_URL")
    if not rpc_url:
        logger.error("HELIUS_RPC_URL not found in environment")
        return
    
    client = AsyncClient(rpc_url)
    
    try:
        signature = Signature.from_string(tx_sig)
        
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
        
        # Find the router instruction that calls Pump.fun
        router_program_id = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"  # Router program
        pump_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        
        router_instruction = None
        instruction_index = None
        
        for i, instruction in enumerate(transaction.transaction.message.instructions):
            if hasattr(instruction, 'program_id'):
                if str(instruction.program_id) == router_program_id:
                    router_instruction = instruction
                    instruction_index = i
                    break
        
        if not router_instruction:
            logger.error("Router instruction not found")
            return
            
        logger.info(f"Found Router instruction at index {instruction_index} with {len(router_instruction.accounts)} accounts")
        
        # Get all account keys from the message
        account_keys = []
        if hasattr(transaction.transaction.message, 'account_keys'):
            for key in transaction.transaction.message.account_keys:
                if hasattr(key, 'pubkey'):
                    account_keys.append(str(key.pubkey))
                else:
                    account_keys.append(str(key))
        
        logger.info(f"Total account keys in transaction: {len(account_keys)}")
        
        # Map account indices to actual addresses
        logger.info(f"\n=== EXACT {len(router_instruction.accounts)}-ACCOUNT STRUCTURE ===")
        for i, account_ref in enumerate(router_instruction.accounts):
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
        
        # Get instruction data
        if hasattr(router_instruction, 'data'):
            instruction_data = router_instruction.data
            logger.info(f"\n=== INSTRUCTION DATA ===")
            logger.info(f"Raw data: {instruction_data}")
            
            # Convert to bytes if it's a string
            if isinstance(instruction_data, str):
                import base58
                try:
                    data_bytes = base58.b58decode(instruction_data)
                    logger.info(f"Decoded hex: {data_bytes.hex()}")
                    logger.info(f"Length: {len(data_bytes)} bytes")
                except:
                    logger.info(f"Could not decode as base58, treating as raw string")
            else:
                logger.info(f"Hex: {instruction_data.hex()}")
                logger.info(f"Length: {len(instruction_data)} bytes")
        
        # Extract key accounts for bot implementation
        logger.info(f"\n=== KEY ACCOUNTS FOR BOT ===")
        if len(router_instruction.accounts) >= 10:
            for i in range(len(router_instruction.accounts)):
                account_ref = router_instruction.accounts[i]
                if isinstance(account_ref, int):
                    if account_ref < len(account_keys):
                        account_address = account_keys[account_ref]
                        logger.info(f"# Position [{i:2d}]: {account_address}")
                else:
                    account_address = str(account_ref)
                    logger.info(f"# Position [{i:2d}]: {account_address}")
        
        # Also check for mint address in the accounts
        logger.info(f"\n=== MINT AND TRANSACTION INFO ===")
        mint_candidates = []
        for i, account_ref in enumerate(router_instruction.accounts):
            if isinstance(account_ref, int) and account_ref < len(account_keys):
                account_address = account_keys[account_ref]
                # Check if this looks like a mint address (position 2 is usually mint)
                if i == 2:
                    logger.info(f"Likely mint address (position 2): {account_address}")
                    mint_candidates.append(account_address)
        
        # Look for Pump.fun program in the accounts (it's called by the router)
        pump_program_positions = []
        for i, account_ref in enumerate(router_instruction.accounts):
            if isinstance(account_ref, int) and account_ref < len(account_keys):
                account_address = account_keys[account_ref]
                if account_address == pump_program_id:
                    pump_program_positions.append(i)
                    logger.info(f"Pump.fun program found at position {i}")
        
        logger.info(f"Router program: {router_program_id}")
        logger.info(f"Pump.fun program positions in router call: {pump_program_positions}")
        
        # Check transaction signature and user
        logger.info(f"Transaction signature: {tx_sig}")
        if hasattr(transaction.transaction.message, 'account_keys') and len(transaction.transaction.message.account_keys) > 0:
            first_account = transaction.transaction.message.account_keys[0]
            if hasattr(first_account, 'pubkey'):
                logger.info(f"Transaction signer: {first_account.pubkey}")
            else:
                logger.info(f"Transaction signer: {first_account}")
                    
    except Exception as e:
        logger.error(f"Error analyzing transaction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_successful_transaction())