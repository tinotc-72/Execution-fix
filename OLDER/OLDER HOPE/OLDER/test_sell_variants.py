#!/usr/bin/env python3
"""
Minimal sell-only test to debug the exact account structure
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
    f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_sell_instruction_v1(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Try sell instruction with EXACT same order as buy but positions 3&5 swapped"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # EXACT SAME AS BUY but swap positions 3 & 5
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 3: User token account (SWAPPED)
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state  
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 5: Token vault (SWAPPED)
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Other account
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # 10: Event authority
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Program ID
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

def create_sell_instruction_v2(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Try sell with completely different structure - remove some accounts"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Minimal structure
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # Token program
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # Event authority
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_sell_versions():
    """Test different sell instruction variants"""
    logger.info("🧪 Testing Sell Instruction Variants")
    logger.info("=" * 50)
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    # Check current balance
    current_balance = await get_token_account_balance(token_ata)
    logger.info(f"Current token balance: {current_balance:,} tokens")
    
    if not current_balance or current_balance <= 0:
        logger.error("No tokens to sell!")
        return
    
    # Test with smaller amount first
    sell_amount = min(1_000_000, current_balance)  # Sell 1M tokens or all if less
    logger.info(f"Testing sell of {sell_amount:,} tokens")
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        
        # === TEST VERSION 1 ===
        logger.info("\n🧪 TEST 1: Same as buy but positions 3&5 swapped")
        
        instructions_v1 = [
            create_compute_budget_ix(compute_units=300_000),
            create_sell_instruction_v1(wallet.pubkey(), sell_amount, 1)
        ]
        
        recent_blockhash = await executor.get_latest_blockhash()
        message_v1 = Message.new_with_blockhash(instructions_v1, wallet.pubkey(), recent_blockhash)
        tx_v1 = VersionedTransaction(message_v1, [wallet])
        
        logger.info("Sending test transaction v1...")
        sig_v1 = await executor.send_transaction(tx_v1, [wallet], original_instructions=instructions_v1)
        
        if sig_v1:
            logger.info(f"✅ V1 transaction sent: {sig_v1}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{sig_v1}")
            await asyncio.sleep(3)
            
            # Check if it worked
            new_balance = await get_token_account_balance(token_ata)
            if new_balance < current_balance:
                logger.info(f"🎉 SUCCESS! V1 worked! Sold {current_balance - new_balance:,} tokens")
                return
            else:
                logger.info("❌ V1 failed - no tokens sold")
        else:
            logger.info("❌ V1 transaction failed to send")
        
        # === TEST VERSION 2 ===
        logger.info("\n🧪 TEST 2: Minimal account structure")
        
        instructions_v2 = [
            create_compute_budget_ix(compute_units=300_000),
            create_sell_instruction_v2(wallet.pubkey(), sell_amount, 1)
        ]
        
        recent_blockhash2 = await executor.get_latest_blockhash()
        message_v2 = Message.new_with_blockhash(instructions_v2, wallet.pubkey(), recent_blockhash2)
        tx_v2 = VersionedTransaction(message_v2, [wallet])
        
        logger.info("Sending test transaction v2...")
        sig_v2 = await executor.send_transaction(tx_v2, [wallet], original_instructions=instructions_v2)
        
        if sig_v2:
            logger.info(f"✅ V2 transaction sent: {sig_v2}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{sig_v2}")
            await asyncio.sleep(3)
            
            # Check if it worked
            final_balance = await get_token_account_balance(token_ata)
            if final_balance < current_balance:
                logger.info(f"🎉 SUCCESS! V2 worked! Sold {current_balance - final_balance:,} tokens")
                return
            else:
                logger.info("❌ V2 failed - no tokens sold")
        else:
            logger.info("❌ V2 transaction failed to send")

if __name__ == "__main__":
    asyncio.run(test_sell_versions())
