#!/usr/bin/env python3
"""
Complete buy-hold-sell script for pump.fun tokens
GOAL: Buy tokens, hold for 5 seconds, then sell 100%
"""

import asyncio
import logging
import time
from typing import List

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import VersionedTransaction

# Local imports
from env_keys import EnvKeys
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    create_associated_token_account,
    PUMP_BUY_DISCRIMINATOR,
    PUMP_SELL_DISCRIMINATOR,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import check_token_account_exists, get_token_account_balance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - using the successful token
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"  # Proven working token
AMOUNT_SOL = 0.01  # Small amount for testing  
AMOUNT_LAMPORTS = int(AMOUNT_SOL * 1e9)
SLIPPAGE_BPS = 500  # 5%
HOLD_TIME_SECONDS = 5

# Environment
keys = EnvKeys()
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_buy_instruction(owner: Pubkey, amount: int, min_amount_out: int) -> Instruction:
    """Create buy instruction using proven working account structure"""
    
    instruction_data = (
        PUMP_BUY_DISCRIMINATOR +
        amount.to_bytes(8, "little") +
        min_amount_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Proven working account structure
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

def create_sell_instruction(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """Create sell instruction using correct account structure for sell operations"""
    
    instruction_data = (
        PUMP_SELL_DISCRIMINATOR +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Account structure for SELL - Token program at position 8 EXACTLY like buy instruction
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 3: User token account (swapped for sell)
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 5: Token vault (swapped for sell)
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program (SAME POSITION AS BUY!)
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Other account
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # 10: Event authority
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Program ID
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def execute_buy_hold_sell():
    """Execute the complete buy-hold-sell sequence"""
    logger.info("🚀 Starting Buy-Hold-Sell Sequence")
    logger.info("=" * 50)
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        logger.info(f"Wallet: {wallet.pubkey()}")
        logger.info(f"Token: {token_mint}")
        logger.info(f"Buy Amount: {AMOUNT_SOL} SOL")
        logger.info(f"Hold Time: {HOLD_TIME_SECONDS} seconds")
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # === STEP 1: BUY ===
            logger.info("\n💰 STEP 1: BUYING TOKENS")
            logger.info("-" * 30)
            
            initial_balance = await executor.get_balance(wallet.pubkey())
            logger.info(f"Initial SOL balance: {initial_balance/1e9:.6f} SOL")
            
            # Check if token account exists
            token_account_exists = await check_token_account_exists(token_ata)
            logger.info(f"Token account exists: {token_account_exists}")
            
            # Build buy transaction
            instructions = []
            
            # Compute budget
            compute_ix = create_compute_budget_ix(compute_units=300_000)
            instructions.append(compute_ix)
            
            # Create token account if needed
            if not token_account_exists:
                ata_ix = create_associated_token_account(
                    payer=wallet.pubkey(),
                    owner=wallet.pubkey(),
                    mint=token_mint
                )
                instructions.append(ata_ix)
                logger.info("Added ATA creation instruction")
            
            # Buy instruction
            min_amount_out = max(1, int(AMOUNT_LAMPORTS * (1 - SLIPPAGE_BPS / 10000)))
            buy_ix = create_buy_instruction(wallet.pubkey(), AMOUNT_LAMPORTS, min_amount_out)
            instructions.append(buy_ix)
            logger.info("Added buy instruction")
            
            # Execute buy
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            logger.info("Sending buy transaction...")
            buy_sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
            
            if not buy_sig:
                logger.error("❌ Buy transaction failed")
                return False
                
            logger.info(f"✅ Buy transaction sent: {buy_sig}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{buy_sig}")
            
            # Wait for confirmation and check tokens received
            await asyncio.sleep(3)
            token_balance = await get_token_account_balance(token_ata)
            
            if not token_balance or token_balance <= 0:
                logger.error("❌ No tokens received from buy")
                return False
                
            logger.info(f"🎉 Successfully bought {token_balance:,} tokens!")
            
            # === STEP 2: HOLD ===
            logger.info(f"\n⏳ STEP 2: HOLDING FOR {HOLD_TIME_SECONDS} SECONDS")
            logger.info("-" * 30)
            
            for i in range(HOLD_TIME_SECONDS):
                logger.info(f"Holding... {i+1}/{HOLD_TIME_SECONDS} seconds")
                await asyncio.sleep(1)
            
            logger.info("✅ Hold period completed!")
            
            # === STEP 3: SELL ===
            logger.info("\n💸 STEP 3: SELLING ALL TOKENS")
            logger.info("-" * 30)
            
            # Check current token balance
            current_token_balance = await get_token_account_balance(token_ata)
            if not current_token_balance or current_token_balance <= 0:
                logger.error("❌ No tokens to sell")
                return False
                
            logger.info(f"Selling {current_token_balance:,} tokens")
            
            # Build sell transaction
            sell_instructions = []
            
            # Compute budget for sell
            sell_compute_ix = create_compute_budget_ix(compute_units=300_000)
            sell_instructions.append(sell_compute_ix)
            
            # Sell instruction (sell 100% of tokens)
            min_sol_out = 1  # Minimum 1 lamport (very low slippage tolerance)
            sell_ix = create_sell_instruction(wallet.pubkey(), current_token_balance, min_sol_out)
            sell_instructions.append(sell_ix)
            logger.info("Added sell instruction")
            
            # Execute sell
            sell_blockhash = await executor.get_latest_blockhash()
            sell_message = Message.new_with_blockhash(sell_instructions, wallet.pubkey(), sell_blockhash)
            sell_tx = VersionedTransaction(sell_message, [wallet])
            
            logger.info("Sending sell transaction...")
            sell_sig = await executor.send_transaction(sell_tx, [wallet], original_instructions=sell_instructions)
            
            if not sell_sig:
                logger.error("❌ Sell transaction failed")
                return False
                
            logger.info(f"✅ Sell transaction sent: {sell_sig}")
            logger.info(f"🔗 Solscan: https://solscan.io/tx/{sell_sig}")
            
            # Wait for confirmation and check results
            await asyncio.sleep(3)
            
            final_token_balance = await get_token_account_balance(token_ata)
            final_sol_balance = await executor.get_balance(wallet.pubkey())
            
            logger.info("\n🎯 FINAL RESULTS")
            logger.info("=" * 30)
            logger.info(f"Initial SOL: {initial_balance/1e9:.6f} SOL")
            logger.info(f"Final SOL: {final_sol_balance/1e9:.6f} SOL")
            logger.info(f"SOL difference: {(final_sol_balance - initial_balance)/1e9:.6f} SOL")
            logger.info(f"Final token balance: {final_token_balance or 0:,} tokens")
            
            if final_token_balance == 0:
                logger.info("🎉 SUCCESS: All tokens sold successfully!")
                logger.info("✅ Buy-Hold-Sell sequence completed!")
                return True
            else:
                logger.warning(f"⚠️ Some tokens remaining: {final_token_balance:,}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error during buy-hold-sell: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await execute_buy_hold_sell()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 🎉 BUY-HOLD-SELL SEQUENCE COMPLETED SUCCESSFULLY! 🎉 🎉")
    else:
        print("❌ ❌ BUY-HOLD-SELL SEQUENCE FAILED ❌ ❌")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
