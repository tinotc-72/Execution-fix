#!/usr/bin/env python3
"""
Test sell instruction only (we already have tokens)
"""

import asyncio
import logging
from complete_buy_hold_sell import create_sell_instruction, TOKEN_MINT
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import get_associated_token_address, create_compute_budget_ix
from utils import get_token_account_balance
from solders.pubkey import Pubkey
from solders.message import Message
from solders.transaction import VersionedTransaction
from env_keys import EnvKeys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

keys = EnvKeys()
RPC_ENDPOINTS = [f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"]

async def test_sell_only():
    """Test selling existing tokens"""
    logger.info("=== Testing Sell Only ===")
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        # Check current token balance
        token_balance = await get_token_account_balance(token_ata)
        logger.info(f"Current token balance: {token_balance:,} tokens")
        
        if not token_balance or token_balance <= 0:
            logger.error("No tokens to sell")
            return False
        
        # Initial SOL balance
        initial_sol = await executor.get_balance(wallet.pubkey())
        logger.info(f"Initial SOL: {initial_sol/1e9:.6f} SOL")
        
        # Create sell transaction
        instructions = []
        
        # Compute budget
        compute_ix = create_compute_budget_ix(compute_units=300_000)
        instructions.append(compute_ix)
        
        # Sell instruction (sell all tokens)
        min_sol_out = 1  # Very low minimum
        sell_ix = create_sell_instruction(wallet.pubkey(), token_balance, min_sol_out)
        instructions.append(sell_ix)
        
        # Execute
        blockhash = await executor.get_latest_blockhash()
        message = Message.new_with_blockhash(instructions, wallet.pubkey(), blockhash)
        tx = VersionedTransaction(message, [wallet])
        
        logger.info("Sending sell transaction...")
        sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
        
        if sig:
            logger.info(f"✅ Sell transaction sent: {sig}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{sig}")
            
            # Wait and check results
            await asyncio.sleep(5)
            
            final_token_balance = await get_token_account_balance(token_ata)
            final_sol = await executor.get_balance(wallet.pubkey())
            
            logger.info(f"Final token balance: {final_token_balance or 0:,} tokens")
            logger.info(f"Final SOL: {final_sol/1e9:.6f} SOL")
            logger.info(f"SOL gained: {(final_sol - initial_sol)/1e9:.6f} SOL")
            
            if final_token_balance == 0:
                logger.info("🎉 SUCCESS: All tokens sold!")
                return True
            else:
                logger.warning(f"⚠️ Some tokens remaining: {final_token_balance:,}")
                return False
        else:
            logger.error("❌ Sell transaction failed")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_sell_only())
    print(f"\nSell test: {'✅ PASSED' if success else '❌ FAILED'}")
