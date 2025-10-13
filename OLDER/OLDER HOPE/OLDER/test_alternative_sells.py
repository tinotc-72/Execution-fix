#!/usr/bin/env python3
"""
Alternative approach: Use a completely different sell instruction structure
Based on analysis of pump.fun program behavior
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

keys = EnvKeys()
RPC_ENDPOINTS = [f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"]

def create_alternative_sell_v1(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Alternative 1: Minimal account structure based on typical AMM patterns"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Minimal approach: only essential accounts
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # Fee account
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User source
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault destination  
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # User wallet
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # Token program
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # System program
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

def create_alternative_sell_v2(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Alternative 2: Reverse the token vault and user account positions"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Try completely different ordering
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # Fee account
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault FIRST
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account AFTER vault
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

def create_alternative_sell_v3(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Alternative 3: Try different discriminator - maybe we have wrong sell discriminator"""
    
    # Try the buy discriminator instead (maybe sell uses same discriminator with different params)
    from minimal_tx_builder import PUMP_BUY_DISCRIMINATOR
    
    instruction_data = (
        PUMP_BUY_DISCRIMINATOR +  # Using BUY discriminator instead!
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Use exact buy structure but with sell amounts
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account
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

async def test_alternative_approaches():
    """Test completely different sell approaches"""
    logger.info("🔬 TESTING ALTERNATIVE SELL APPROACHES")
    logger.info("=" * 60)
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    current_balance = await get_token_account_balance(token_ata)
    logger.info(f"Current token balance: {current_balance:,} tokens")
    
    if not current_balance or current_balance <= 0:
        logger.error("No tokens to sell!")
        return False
    
    test_amount = min(500_000, current_balance)  # 500k tokens
    logger.info(f"Testing with {test_amount:,} tokens per approach")
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        
        # Test Alternative 1: Minimal structure
        logger.info(f"\n🧪 ALTERNATIVE 1: Minimal account structure")
        logger.info("-" * 50)
        
        instructions_v1 = [
            create_compute_budget_ix(compute_units=300_000),
            create_alternative_sell_v1(wallet.pubkey(), test_amount, 1)
        ]
        
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions_v1, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions_v1)
            if sig:
                logger.info(f"✅ V1 sent: {sig}")
                await asyncio.sleep(3)
                new_balance = await get_token_account_balance(token_ata)
                if new_balance < current_balance:
                    logger.info(f"🎉 SUCCESS! V1 worked! Sold {current_balance - new_balance:,} tokens")
                    return True
                else:
                    logger.info("❌ V1 failed")
        except Exception as e:
            logger.error(f"❌ V1 error: {e}")
        
        # Test Alternative 2: Different ordering
        logger.info(f"\n🧪 ALTERNATIVE 2: Reversed vault/user order")
        logger.info("-" * 50)
        
        instructions_v2 = [
            create_compute_budget_ix(compute_units=300_000),
            create_alternative_sell_v2(wallet.pubkey(), test_amount, 1)
        ]
        
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions_v2, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions_v2)
            if sig:
                logger.info(f"✅ V2 sent: {sig}")
                await asyncio.sleep(3)
                new_balance = await get_token_account_balance(token_ata)
                if new_balance < current_balance:
                    logger.info(f"🎉 SUCCESS! V2 worked! Sold {current_balance - new_balance:,} tokens")
                    return True
                else:
                    logger.info("❌ V2 failed")
        except Exception as e:
            logger.error(f"❌ V2 error: {e}")
            
        # Test Alternative 3: Different discriminator
        logger.info(f"\n🧪 ALTERNATIVE 3: Buy discriminator with sell params")
        logger.info("-" * 50)
        
        instructions_v3 = [
            create_compute_budget_ix(compute_units=300_000),
            create_alternative_sell_v3(wallet.pubkey(), test_amount, 1)
        ]
        
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions_v3, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions_v3)
            if sig:
                logger.info(f"✅ V3 sent: {sig}")
                await asyncio.sleep(3)
                new_balance = await get_token_account_balance(token_ata)
                if new_balance < current_balance:
                    logger.info(f"🎉 SUCCESS! V3 worked! Sold {current_balance - new_balance:,} tokens")
                    return True
                else:
                    logger.info("❌ V3 failed")
        except Exception as e:
            logger.error(f"❌ V3 error: {e}")
    
    logger.info(f"\n❌ All alternatives failed")
    return False

async def main():
    success = await test_alternative_approaches()
    
    if success:
        logger.info(f"\n🎉 FOUND WORKING SELL APPROACH!")
    else:
        logger.info(f"\n❌ Need to investigate pump.fun program further")

if __name__ == "__main__":
    asyncio.run(main())
