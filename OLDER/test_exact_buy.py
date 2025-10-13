#!/usr/bin/env python3
"""
Test buy transaction using exact accounts from successful transaction
"""

import asyncio
import logging
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
    PUMP_TRADE_PROGRAM_KEY
)
from utils import check_token_account_exists, get_token_account_balance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - using the exact token from successful transaction
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"  # Successful tx token
AMOUNT_SOL = 0.01
AMOUNT_LAMPORTS = int(AMOUNT_SOL * 1e9)
SLIPPAGE_BPS = 500

# Load environment
keys = EnvKeys()
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_exact_buy_instruction(owner: Pubkey, amount: int, min_amount_out: int) -> Instruction:
    """Create buy instruction using exact accounts from successful transaction"""
    
    logger.info("Creating buy instruction with exact accounts from successful transaction")
    
    # Instruction data
    instruction_data = (
        PUMP_BUY_DISCRIMINATOR +
        amount.to_bytes(8, "little") +
        min_amount_out.to_bytes(8, "little")
    )
    
    # Exact accounts from successful transaction (but replace user accounts with ours)
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # 0: Config/global  
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # 1: Some PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # 3: Token vault
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # 4: Route state
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # 5: User token account (OUR account)
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet (OUR wallet)
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # 8: Token program
        AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # 9: Some account
        AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # 10: Event authority
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Program ID
    ]
    
    logger.info(f"Created instruction with {len(accounts)} accounts")
    logger.info(f"User wallet: {owner}")
    logger.info(f"User token ATA: {user_token_ata}")
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_exact_buy():
    """Test buy using exact account structure"""
    logger.info("=== Testing Buy with Exact Accounts ===")
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        logger.info(f"Wallet: {wallet.pubkey()}")
        logger.info(f"Token: {token_mint}")
        logger.info(f"Amount: {AMOUNT_SOL} SOL")
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check initial state
            balance = await executor.get_balance(wallet.pubkey())
            logger.info(f"Initial balance: {balance/1e9:.6f} SOL")
            
            token_account_exists = await check_token_account_exists(token_ata)
            logger.info(f"Token account exists: {token_account_exists}")
            
            # Build transaction
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
                logger.info("Added ATA creation")
            
            # Buy instruction with exact accounts
            min_amount_out = max(1, int(AMOUNT_LAMPORTS * (1 - SLIPPAGE_BPS / 10000)))
            buy_ix = create_exact_buy_instruction(wallet.pubkey(), AMOUNT_LAMPORTS, min_amount_out)
            instructions.append(buy_ix)
            logger.info("Added buy instruction")
            
            # Create and send transaction
            recent_blockhash = await executor.get_latest_blockhash()
            message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
            tx = VersionedTransaction(message, [wallet])
            
            logger.info("Sending transaction...")
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
            
            if sig:
                logger.info(f"✅ Transaction sent: {sig}")
                logger.info(f"🔗 Solscan: https://solscan.io/tx/{sig}")
                
                # Wait and check result
                await asyncio.sleep(3)
                
                final_balance = await executor.get_balance(wallet.pubkey())
                logger.info(f"Final balance: {final_balance/1e9:.6f} SOL")
                logger.info(f"SOL spent: {(balance - final_balance)/1e9:.6f} SOL")
                
                # Check token balance
                final_token_exists = await check_token_account_exists(token_ata)
                if final_token_exists:
                    token_balance = await get_token_account_balance(token_ata)
                    logger.info(f"Token balance: {token_balance}")
                    
                    if token_balance and token_balance > 0:
                        logger.info("🎉 SUCCESS: Buy completed and tokens received!")
                        return True
                    else:
                        logger.warning("Token account exists but no tokens received")
                else:
                    logger.error("Token account was not created")
                
                return False
            else:
                logger.error("Transaction failed to send")
                return False
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_exact_buy()
    if success:
        print("\n✅ EXACT BUY TEST PASSED!")
    else:
        print("\n❌ EXACT BUY TEST FAILED!")

if __name__ == "__main__":
    asyncio.run(main())
