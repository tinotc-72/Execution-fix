#!/usr/bin/env python3
"""
Final attempt at correct sell structure based on program analysis
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import VersionedTransaction

from env_keys import EnvKeys
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    PUMP_SELL_DISCRIMINATOR,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import get_token_account_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"

# Environment
keys = EnvKeys()
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
]

def create_final_sell_instruction(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Final sell instruction - informed by error analysis"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # The error shows token_program account is expected to be TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
    # but we're providing Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1 (Event Authority)
    # This suggests the sell instruction expects tokens program in a DIFFERENT position than buy
    
    # HYPOTHESIS: Sell instruction has completely different structure
    # Let's try putting token_program earlier in the list
    
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 3: User token account 
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 5: Token vault 
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program (same position as buy)
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Other account
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # 10: Event authority
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Program ID
    ]
    
    logger.info("Account layout for sell instruction:")
    for i, acc in enumerate(accounts):
        logger.info(f"  {i}: {acc.pubkey} (signer={acc.is_signer}, writable={acc.is_writable})")
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_final_sell():
    """Final sell test with all our tokens"""
    logger.info("🎯 FINAL SELL TEST")
    logger.info("=" * 50)
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    # Check current balance
    current_balance = await get_token_account_balance(token_ata)
    logger.info(f"Current token balance: {current_balance:,} tokens")
    
    if not current_balance or current_balance <= 0:
        logger.error("No tokens to sell!")
        return False
    
    # Sell ALL tokens
    logger.info(f"Attempting to sell ALL {current_balance:,} tokens")
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        initial_sol = await executor.get_balance(wallet.pubkey())
        logger.info(f"Initial SOL balance: {initial_sol/1e9:.6f} SOL")
        
        instructions = [
            create_compute_budget_ix(compute_units=300_000),
            create_final_sell_instruction(wallet.pubkey(), current_balance, 1)
        ]
        
        recent_blockhash = await executor.get_latest_blockhash()
        message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
        tx = VersionedTransaction(message, [wallet])
        
        logger.info("Sending FINAL sell transaction...")
        sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
        
        if sig:
            logger.info(f"✅ FINAL transaction sent: {sig}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{sig}")
            
            # Wait and check results
            await asyncio.sleep(5)
            
            final_token_balance = await get_token_account_balance(token_ata)
            final_sol = await executor.get_balance(wallet.pubkey())
            
            logger.info(f"\n🎯 FINAL RESULTS:")
            logger.info(f"Initial SOL: {initial_sol/1e9:.6f} SOL")
            logger.info(f"Final SOL: {final_sol/1e9:.6f} SOL")
            logger.info(f"SOL change: {(final_sol - initial_sol)/1e9:.6f} SOL")
            logger.info(f"Token balance: {current_balance:,} → {final_token_balance or 0:,}")
            
            tokens_sold = current_balance - (final_token_balance or 0)
            if tokens_sold > 0:
                logger.info(f"🎉 SUCCESS! Sold {tokens_sold:,} tokens!")
                return True
            else:
                logger.info("❌ No tokens were sold")
                return False
        else:
            logger.info("❌ Transaction failed to send")
            return False

if __name__ == "__main__":
    asyncio.run(test_final_sell())
