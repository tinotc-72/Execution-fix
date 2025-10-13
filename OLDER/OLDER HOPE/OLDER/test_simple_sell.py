#!/usr/bin/env python3
"""
Simple test to try the most likely sell discriminator based on common patterns
"""

import asyncio
import logging

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta

# Local imports
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    PUMP_TRADE_PROGRAM_KEY
)
from solders.message import Message
from solders.transaction import VersionedTransaction
from utils import get_token_account_balance
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

# Based on Anchor IDL patterns, sell is often just "sell" -> sha256 first 8 bytes
# Let's try the most common pattern for sell: b712469c946da122
SELL_DISCRIMINATOR_NEW = "b712469c946da122"

def create_sell_instruction_simple(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Create sell instruction with simpler approach"""
    
    # Try the more common sell discriminator pattern
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR_NEW) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Same account structure as buy, but with user_token_ata and token_vault swapped
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account (was position 5 in buy)
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault (was position 3 in buy)
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # Token program
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # Other account
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # Event authority
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # Program ID
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_simple_sell():
    """Test simple sell with new discriminator"""
    logger.info("🧪 Testing simple sell with new discriminator")
    logger.info("=" * 50)
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        logger.info(f"Wallet: {wallet.pubkey()}")
        logger.info(f"Token: {token_mint}")
        logger.info(f"Token ATA: {token_ata}")
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check current token balance
            current_balance = await get_token_account_balance(token_ata)
            logger.info(f"Current token balance: {current_balance:,} tokens")
            
            if current_balance == 0:
                logger.warning("❌ No tokens to sell!")
                return
            
            # Sell all tokens
            sell_amount = current_balance
            min_sol_out = 0  # Accept any amount of SOL
            
            logger.info(f"Attempting to sell {sell_amount:,} tokens")
            logger.info(f"Using discriminator: {SELL_DISCRIMINATOR_NEW}")
            
            # Build transaction
            instructions = []
            
            # Compute budget
            compute_ix = create_compute_budget_ix(compute_units=300_000)
            instructions.append(compute_ix)
            
            # Sell instruction
            sell_ix = create_sell_instruction_simple(
                wallet.pubkey(), 
                sell_amount, 
                min_sol_out
            )
            instructions.append(sell_ix)
            
            # Build and send transaction
            message = Message.new_with_blockhash(
                instructions,
                wallet.pubkey(),
                await executor.get_latest_blockhash()
            )
            
            tx = VersionedTransaction(message, [wallet])
            tx_sig = await executor.send_transaction(tx, [wallet])
            
            logger.info(f"✅ Transaction sent: {tx_sig}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{tx_sig}")
            
            # Wait and check result
            await asyncio.sleep(5)
            new_balance = await get_token_account_balance(token_ata)
            
            if new_balance < current_balance:
                tokens_sold = current_balance - new_balance
                logger.info(f"🎉 SUCCESS! Sold {tokens_sold:,} tokens!")
                logger.info(f"Remaining tokens: {new_balance:,}")
            else:
                logger.warning(f"⚠️  Transaction sent but no tokens sold")
                logger.warning(f"Balance unchanged: {new_balance:,} tokens")
                
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        raise

async def main():
    """Main function"""
    logger.info("🚀 Starting simple sell test")
    
    try:
        await test_simple_sell()
        logger.info("\n✅ Test complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
