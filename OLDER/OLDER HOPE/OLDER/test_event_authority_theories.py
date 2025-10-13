#!/usr/bin/env python3
"""
Final attempt: Replace Event Authority with Token Program entirely
Based on error analysis showing they're mutually exclusive in sell operations
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

def create_no_event_authority_sell(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Sell instruction WITHOUT Event Authority - replace it with Token Program"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # CRITICAL INSIGHT: Remove Event Authority completely, Token Program takes its place
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 3: User token account 
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 5: Token vault 
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Other account
        # NO EVENT AUTHORITY - Token program replaces it!
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 10: Program ID
    ]
    
    logger.info("NO EVENT AUTHORITY sell account structure:")
    for i, acc in enumerate(accounts):
        logger.info(f"  {i}: {acc.pubkey}")
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

def create_double_token_program_sell(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Sell instruction with Token Program in BOTH positions 8 and 10"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Try Token Program in BOTH where it is in buy AND where Event Authority was
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 3: User token account 
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 5: Token vault 
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Other account
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 10: Token program AGAIN!
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Program ID
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_event_authority_theories():
    """Test theories about Event Authority vs Token Program conflict"""
    logger.info("🔬 TESTING EVENT AUTHORITY THEORIES")
    logger.info("=" * 60)
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    current_balance = await get_token_account_balance(token_ata)
    logger.info(f"Current token balance: {current_balance:,} tokens")
    
    if not current_balance or current_balance <= 0:
        logger.error("No tokens to sell!")
        return False
    
    test_amount = min(250_000, current_balance)  # 250k tokens
    logger.info(f"Testing with {test_amount:,} tokens per theory")
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        initial_balance = current_balance
        
        # Theory 1: Remove Event Authority completely
        logger.info(f"\n🧪 THEORY 1: No Event Authority")
        logger.info("-" * 40)
        
        instructions1 = [
            create_compute_budget_ix(compute_units=300_000),
            create_no_event_authority_sell(wallet.pubkey(), test_amount, 1)
        ]
        
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions1, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions1)
            if sig:
                logger.info(f"✅ Theory 1 sent: {sig}")
                logger.info(f"🔗 https://solscan.io/tx/{sig}")
                await asyncio.sleep(4)
                
                new_balance = await get_token_account_balance(token_ata)
                if new_balance < current_balance:
                    tokens_sold = current_balance - new_balance
                    logger.info(f"🎉 BREAKTHROUGH! Theory 1 worked! Sold {tokens_sold:,} tokens")
                    logger.info(f"📍 SOLUTION: Remove Event Authority from sell instruction!")
                    return True
                else:
                    logger.info("❌ Theory 1 failed")
                    current_balance = new_balance  # Update for next test
            else:
                logger.info("❌ Theory 1 - transaction failed to send")
        except Exception as e:
            logger.error(f"❌ Theory 1 error: {e}")
        
        # Theory 2: Double Token Program
        logger.info(f"\n🧪 THEORY 2: Token Program in both positions")
        logger.info("-" * 40)
        
        instructions2 = [
            create_compute_budget_ix(compute_units=300_000),
            create_double_token_program_sell(wallet.pubkey(), test_amount, 1)
        ]
        
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions2, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions2)
            if sig:
                logger.info(f"✅ Theory 2 sent: {sig}")
                logger.info(f"🔗 https://solscan.io/tx/{sig}")
                await asyncio.sleep(4)
                
                new_balance = await get_token_account_balance(token_ata)
                if new_balance < current_balance:
                    tokens_sold = current_balance - new_balance
                    logger.info(f"🎉 BREAKTHROUGH! Theory 2 worked! Sold {tokens_sold:,} tokens")
                    logger.info(f"📍 SOLUTION: Token Program in both positions!")
                    return True
                else:
                    logger.info("❌ Theory 2 failed")
            else:
                logger.info("❌ Theory 2 - transaction failed to send")
        except Exception as e:
            logger.error(f"❌ Theory 2 error: {e}")
    
    logger.info(f"\n❌ Both theories failed")
    return False

async def main():
    success = await test_event_authority_theories()
    
    if success:
        logger.info(f"\n🎉🎉🎉 SELL INSTRUCTION WORKING! 🎉🎉🎉")
        logger.info("=" * 60)
        logger.info("✅ Ready to implement full buy-hold-sell cycle!")
    else:
        logger.info(f"\n❌ Still investigating pump.fun sell mechanics...")

if __name__ == "__main__":
    asyncio.run(main())
