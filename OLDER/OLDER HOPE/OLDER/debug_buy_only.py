#!/usr/bin/env python3
"""
Debug script to test ONLY the buy transaction
Focus on ensuring ATA creation and token receipt
"""

import asyncio
import logging
import json
from typing import Optional

from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import VersionedTransaction

# Local imports
from env_keys import EnvKeys
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_buy_instruction,
    create_compute_budget_ix,
    create_associated_token_account,
    PUMP_ROUTER,
    NATIVE_MINT_KEY
)
from utils import check_token_account_exists, get_token_account_balance

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN_MINT = "EC2HXAzNYC7fsdYUdqpJgntS6tsxAv7eUqcyfaSFpump"  # Recent active token
AMOUNT_SOL = 0.01  # Small amount for testing
AMOUNT_LAMPORTS = int(AMOUNT_SOL * 1e9)
SLIPPAGE_BPS = 500  # 5%

# Load environment
keys = EnvKeys()
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

async def debug_buy_transaction():
    """Test buy transaction step by step with detailed debugging"""
    logger.info("=== Buy Transaction Debug Test ===")
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        logger.info(f"Wallet: {wallet.pubkey()}")
        logger.info(f"Token Mint: {token_mint}")
        logger.info(f"Token ATA: {token_ata}")
        logger.info(f"Buy Amount: {AMOUNT_SOL} SOL ({AMOUNT_LAMPORTS} lamports)")
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # 1. Check initial state
            logger.info("\n=== Step 1: Initial State Check ===")
            balance = await executor.get_balance(wallet.pubkey())
            logger.info(f"Wallet balance: {balance/1e9:.6f} SOL")
            
            # Check if token account exists
            token_account_exists = await check_token_account_exists(token_ata)
            logger.info(f"Token account exists: {token_account_exists}")
            
            if token_account_exists:
                initial_token_balance = await get_token_account_balance(token_ata)
                logger.info(f"Initial token balance: {initial_token_balance}")
            else:
                logger.info("Token account does not exist - will be created")
            
            # 2. Build transaction
            logger.info("\n=== Step 2: Build Transaction ===")
            instructions = []
            
            # Add compute budget
            compute_ix = create_compute_budget_ix(compute_units=300_000)
            instructions.append(compute_ix)
            logger.info("✅ Added compute budget instruction")
            
            # Add ATA creation if needed
            if not token_account_exists:
                logger.info("Creating token account instruction...")
                ata_ix = create_associated_token_account(
                    payer=wallet.pubkey(),
                    owner=wallet.pubkey(),
                    mint=token_mint
                )
                instructions.append(ata_ix)
                logger.info("✅ Added ATA creation instruction")
            
            # Create buy instruction
            logger.info("Creating buy instruction...")
            buy_ix = await create_buy_instruction(
                token_mint=token_mint,
                owner=wallet.pubkey(),
                amount=AMOUNT_LAMPORTS,
                slippage_bps=SLIPPAGE_BPS,
                token_ata=token_ata
            )
            instructions.append(buy_ix)
            logger.info("✅ Added buy instruction")
            
            # 3. Create and send transaction
            logger.info("\n=== Step 3: Execute Transaction ===")
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                raise ValueError("Failed to get recent blockhash")
            
            # Build message and transaction
            message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            # Debug transaction details
            logger.info(f"Transaction instructions: {len(instructions)}")
            for i, ix in enumerate(instructions):
                logger.info(f"Instruction {i}: {ix.program_id} ({len(ix.accounts)} accounts)")
            
            # Send transaction
            logger.info("Sending transaction...")
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
            
            if not sig:
                logger.error("❌ Transaction failed to send")
                return False
                
            logger.info(f"✅ Transaction sent: {sig}")
            logger.info(f"🔗 View on Solscan: https://solscan.io/tx/{sig}")
            
            # 4. Wait and check result
            logger.info("\n=== Step 4: Check Transaction Result ===")
            
            # Wait a bit for transaction to process
            await asyncio.sleep(3)
            
            # Check final state
            final_balance = await executor.get_balance(wallet.pubkey())
            logger.info(f"Final wallet balance: {final_balance/1e9:.6f} SOL")
            logger.info(f"SOL spent: {(balance - final_balance)/1e9:.6f} SOL")
            
            # Check token account status
            token_account_exists_after = await check_token_account_exists(token_ata)
            logger.info(f"Token account exists after: {token_account_exists_after}")
            
            if token_account_exists_after:
                final_token_balance = await get_token_account_balance(token_ata)
                logger.info(f"Final token balance: {final_token_balance}")
                
                if final_token_balance and final_token_balance > 0:
                    logger.info("🎉 SUCCESS: Tokens received!")
                    return True
                else:
                    logger.warning("⚠️ Token account exists but no tokens received")
                    return False
            else:
                logger.error("❌ Token account was not created")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error during buy test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main execution function"""
    success = await debug_buy_transaction()
    if success:
        print("\n✅ Buy transaction test PASSED")
    else:
        print("\n❌ Buy transaction test FAILED")

if __name__ == "__main__":
    asyncio.run(main())
