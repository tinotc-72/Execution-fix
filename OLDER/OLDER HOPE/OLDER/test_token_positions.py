#!/usr/bin/env python3
"""
Systematic test to find correct token program position for sell instruction
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

def create_sell_test(owner: Pubkey, token_amount: int, min_sol_out: int, token_program_position: int) -> Instruction:
    """Create sell instruction with token program at specific position"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Base accounts in buy order
    base_accounts = [
        Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"),  # 0: Config
        Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"),  # 1: PDA
        token_mint,  # 2: Token mint
        user_token_ata,  # 3: User token account (swapped for sell)
        Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"),  # 4: Route state
        Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"),  # 5: Token vault (swapped for sell)
        owner,  # 6: User wallet
        Pubkey.from_string("11111111111111111111111111111111"),  # 7: System program
        Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"),  # 8: Other account
        Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"),  # 9: Event authority
        PUMP_TRADE_PROGRAM_KEY,  # 10: Program ID
    ]
    
    # Account metadata flags
    writables = [False, True, False, True, True, True, True, False, True, False, False]
    signers = [False, False, False, False, False, False, True, False, False, False, False]
    
    # Insert Token program at specified position
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    
    # Create accounts list with token program at specified position
    accounts = []
    for i in range(len(base_accounts) + 1):  # +1 for token program
        if i == token_program_position:
            accounts.append(AccountMeta(pubkey=token_program, is_signer=False, is_writable=False))
        elif i < token_program_position:
            accounts.append(AccountMeta(pubkey=base_accounts[i], is_signer=signers[i], is_writable=writables[i]))
        else:
            accounts.append(AccountMeta(pubkey=base_accounts[i-1], is_signer=signers[i-1], is_writable=writables[i-1]))
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_all_positions():
    """Test token program at each possible position"""
    logger.info("🔬 SYSTEMATIC TOKEN PROGRAM POSITION TEST")
    logger.info("=" * 60)
    
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    # Check current balance
    current_balance = await get_token_account_balance(token_ata)
    logger.info(f"Current token balance: {current_balance:,} tokens")
    
    if not current_balance or current_balance <= 0:
        logger.error("No tokens to sell!")
        return False
    
    # Test with small amount
    test_amount = min(100_000, current_balance)  # 100k tokens for testing
    logger.info(f"Testing with {test_amount:,} tokens per position")
    
    async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
        initial_balance = current_balance
        
        # Test positions 0 through 11
        for position in range(12):
            logger.info(f"\n🧪 TESTING POSITION {position}")
            logger.info("-" * 40)
            
            # Check if we still have tokens
            current_tokens = await get_token_account_balance(token_ata)
            if not current_tokens or current_tokens < test_amount:
                logger.warning(f"Not enough tokens remaining. Current: {current_tokens or 0}")
                break
            
            instructions = [
                create_compute_budget_ix(compute_units=300_000),
                create_sell_test(wallet.pubkey(), test_amount, 1, position)
            ]
            
            try:
                recent_blockhash = await executor.get_latest_blockhash()
                message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
                tx = VersionedTransaction(message, [wallet])
                
                logger.info(f"Sending test with token program at position {position}...")
                sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
                
                if sig:
                    logger.info(f"✅ Transaction sent: {sig}")
                    logger.info(f"🔗 https://solscan.io/tx/{sig}")
                    
                    # Wait and check if tokens were sold
                    await asyncio.sleep(3)
                    new_balance = await get_token_account_balance(token_ata)
                    
                    if new_balance < current_tokens:
                        tokens_sold = current_tokens - new_balance
                        logger.info(f"🎉 SUCCESS! Position {position} worked! Sold {tokens_sold:,} tokens")
                        logger.info(f"📍 WINNING POSITION: {position}")
                        return position
                    else:
                        logger.info(f"❌ Position {position} failed - no tokens sold")
                else:
                    logger.info(f"❌ Position {position} - transaction failed to send")
                    
            except Exception as e:
                logger.error(f"❌ Position {position} error: {e}")
                continue
                
            # Small delay between tests
            await asyncio.sleep(1)
        
        logger.info(f"\n❌ No successful position found after testing 0-11")
        return None

async def main():
    winning_position = await test_all_positions()
    
    if winning_position is not None:
        logger.info(f"\n🎉 FOUND WORKING POSITION: {winning_position}")
        logger.info("=" * 60)
        logger.info("✅ Sell instruction working! Ready for production use.")
    else:
        logger.info("\n❌ No working position found. Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(main())
