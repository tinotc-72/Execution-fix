#!/usr/bin/env python3
"""
Test sell instruction using the EXACT structure from successful sell transaction
Based on transaction: 3cVhmonakERwheg7Jidg9aTdTAPNqWG6T37Nfwrb8S5dABbEzvwd8wFqcXAmg4Z1rhuv3q3L3AQvF5TtuHMnHmTV
"""

import asyncio
import logging
from typing import Optional

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import VersionedTransaction

# Local imports
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import get_token_account_balance
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - using the same token from our successful buy
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
SELL_DISCRIMINATOR = "33e685a4017f83ad"  # Confirmed from real transactions

# RPC endpoints
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_sell_instruction_exact(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """
    Create sell instruction using the EXACT structure from successful transaction
    Based on: 3cVhmonakERwheg7Jidg9aTdTAPNqWG6T37Nfwrb8S5dABbEzvwd8wFqcXAmg4Z1rhuv3q3L3AQvF5TtuHMnHmTV
    """
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    
    # Get the exact account structure from successful transaction
    # [0] User (owner)
    # [1] Token account (user's ATA for this token)  
    # [2] Token mint
    # [3] Bonding curve
    # [4] Associated bonding curve  
    # [5] Associated user
    # [6] Bonding curve token account
    # [7] System program
    # [8] Token program
    # [9] Rent sysvar  
    # [10] Event authority
    # [11] Program
    
    user_token_account = get_associated_token_address(owner, token_mint)
    
    # These are the EXACT accounts from the successful transaction
    accounts = [
        AccountMeta(owner, is_signer=True, is_writable=True),                                                    # [0] User
        AccountMeta(user_token_account, is_signer=False, is_writable=True),                                    # [1] User token account
        AccountMeta(token_mint, is_signer=False, is_writable=False),                                           # [2] Token mint
        AccountMeta(Pubkey.from_string("EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV"), is_signer=False, is_writable=True),   # [3] Bonding curve
        AccountMeta(Pubkey.from_string("AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ"), is_signer=False, is_writable=True),   # [4] Associated bonding curve
        AccountMeta(Pubkey.from_string("9DGQqtdBJHU4fN66cRE1JLVVVJq3KK4mYZxLoSZHqWKf"), is_signer=False, is_writable=True),   # [5] Associated user
        AccountMeta(Pubkey.from_string("DkYPayDaykVxT4RbpNoCct6ztG6kbcgZftjnS6cUb6U"), is_signer=False, is_writable=True),    # [6] Bonding curve token account
        AccountMeta(Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),              # [7] System program
        AccountMeta(Pubkey.from_string("VRbbTzD2HtSwYVtE8VdK5L641K7Zkrj5GgUfDWUJY9j"), is_signer=False, is_writable=False),   # [8] Token program??
        AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),   # [9] Token program
        AccountMeta(Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False), # [10] Event authority
        AccountMeta(PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),                               # [11] Program
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_exact_sell():
    """Test the exact sell structure from successful transaction"""
    logger.info("🧪 Testing EXACT sell structure from successful transaction")
    logger.info(f"Token: {TOKEN_MINT}")
    logger.info(f"Discriminator: {SELL_DISCRIMINATOR}")
    
    owner = WALLET.pubkey()
    
    # Check initial token balance
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_account = get_associated_token_address(owner, token_mint)
    initial_balance = await get_token_account_balance(user_token_account)
    
    if initial_balance == 0:
        logger.error("❌ No tokens to sell! Run a buy first.")
        return False
    
    logger.info(f"💰 Current token balance: {initial_balance}")
    
    # Test with small amount (10% of balance)
    sell_amount = min(1_000_000, initial_balance // 10)  # Sell 10% or 1M tokens, whichever is smaller
    min_sol_out = 1000  # Very small minimum SOL output (0.000001 SOL)
    
    logger.info(f"📊 Attempting to sell {sell_amount} tokens for minimum {min_sol_out} lamports")
    
    try:
        # Create sell instruction
        sell_ix = create_sell_instruction_exact(owner, sell_amount, min_sol_out)
        
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            # Create transaction
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                logger.error("❌ Failed to get recent blockhash")
                return False
            
            # Add compute budget
            compute_ix = create_compute_budget_ix(300_000, 50_000)
            
            instructions = [compute_ix, sell_ix]
            
            message = Message.new_with_blockhash(instructions, owner, recent_blockhash)
            tx = VersionedTransaction(message, [WALLET])
            
            # Execute transaction
            signature = await executor.send_transaction(tx, [WALLET])
            
            if signature:
                logger.info(f"✅ Transaction sent successfully!")
                logger.info(f"🔗 Signature: {signature}")
                
                # Wait a bit for confirmation
                await asyncio.sleep(3)
                
                # Check if token balance changed
                final_balance = await get_token_account_balance(user_token_account)
                
                balance_change = initial_balance - final_balance
                logger.info(f"📊 Token balance change: {balance_change}")
                
                if balance_change > 0:
                    logger.info(f"🎉 SUCCESS! Sold {balance_change} tokens!")
                    logger.info(f"💰 Remaining balance: {final_balance}")
                    return True
                else:
                    logger.warning(f"⚠️ Transaction succeeded but no tokens were sold")
                    logger.info(f"💰 Balance unchanged: {final_balance}")
                    return False
            else:
                logger.error(f"❌ Transaction failed")
                return False
            
    except Exception as e:
        logger.error(f"❌ Error during sell: {e}")
        return False

async def main():
    """Main function"""
    print("="*80)
    print("🔍 TESTING EXACT SELL STRUCTURE FROM SUCCESSFUL TRANSACTION")
    print("="*80)
    
    success = await test_exact_sell()
    
    if success:
        print("\n🎉 SELL TEST PASSED! The exact structure works!")
    else:
        print("\n❌ SELL TEST FAILED. Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(main())
