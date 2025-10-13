#!/usr/bin/env python3
"""
Test sell with properly derived PDAs instead of hardcoded addresses
"""

import asyncio
import logging
from typing import Optional, Tuple

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

# Configuration
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
SELL_DISCRIMINATOR = "33e685a4017f83ad"

# Constants from pump.fun
PUMP_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")

# RPC endpoints
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def find_pda_with_seeds(seeds: list, program_id: Pubkey) -> Tuple[Pubkey, int]:
    """Find PDA with given seeds"""
    return Pubkey.find_program_address(seeds, program_id)

def create_sell_instruction_pda(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """
    Create sell instruction with properly derived PDAs
    """
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_account = get_associated_token_address(owner, token_mint)
    
    # Derive PDAs using common pump.fun patterns
    # Bonding curve PDA
    bonding_curve, _ = find_pda_with_seeds(
        [b"bonding-curve", bytes(token_mint)],
        PUMP_PROGRAM
    )
    
    # Associated bonding curve (the curve's SOL account)
    associated_bonding_curve, _ = find_pda_with_seeds(
        [bytes(bonding_curve)],
        PUMP_PROGRAM
    )
    
    # Associated user (might be a different PDA)
    associated_user, _ = find_pda_with_seeds(
        [b"associated-user", bytes(owner)],
        PUMP_PROGRAM
    )
    
    # Bonding curve token account (curve's token account)
    bonding_curve_token_account = get_associated_token_address(bonding_curve, token_mint)
    
    logger.info(f"🔑 Derived PDAs:")
    logger.info(f"   Bonding curve: {bonding_curve}")
    logger.info(f"   Associated bonding curve: {associated_bonding_curve}")
    logger.info(f"   Associated user: {associated_user}")
    logger.info(f"   Bonding curve token account: {bonding_curve_token_account}")
    
    # Account structure based on successful transactions
    accounts = [
        AccountMeta(owner, is_signer=True, is_writable=True),                           # [0] User (signer)
        AccountMeta(user_token_account, is_signer=False, is_writable=True),           # [1] User token account
        AccountMeta(token_mint, is_signer=False, is_writable=False),                  # [2] Token mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),               # [3] Bonding curve
        AccountMeta(associated_bonding_curve, is_signer=False, is_writable=True),    # [4] Associated bonding curve
        AccountMeta(associated_user, is_signer=False, is_writable=True),             # [5] Associated user
        AccountMeta(bonding_curve_token_account, is_signer=False, is_writable=True), # [6] Bonding curve token account
        AccountMeta(SYSTEM_PROGRAM, is_signer=False, is_writable=False),             # [7] System program
        AccountMeta(TOKEN_PROGRAM, is_signer=False, is_writable=False),              # [8] Token program
        AccountMeta(RENT_SYSVAR, is_signer=False, is_writable=False),               # [9] Rent sysvar
        AccountMeta(EVENT_AUTHORITY, is_signer=False, is_writable=False),            # [10] Event authority
        AccountMeta(PUMP_PROGRAM, is_signer=False, is_writable=False),               # [11] Program
    ]
    
    return Instruction(
        program_id=PUMP_PROGRAM,
        accounts=accounts,
        data=instruction_data
    )

async def test_pda_sell():
    """Test sell with properly derived PDAs"""
    logger.info("🧪 Testing sell with properly derived PDAs")
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
    
    # Test with small amount
    sell_amount = min(1_000_000, initial_balance // 10)  # Sell 10% or 1M tokens
    min_sol_out = 1000  # Very small minimum SOL output
    
    logger.info(f"📊 Attempting to sell {sell_amount} tokens for minimum {min_sol_out} lamports")
    
    try:
        # Create sell instruction with derived PDAs
        sell_ix = create_sell_instruction_pda(owner, sell_amount, min_sol_out)
        
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            # Create transaction
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                logger.error("❌ Failed to get recent blockhash")
                return False
            
            # Add compute budget
            compute_ix = create_compute_budget_ix(400_000, 100_000)  # Increase limits
            
            instructions = [compute_ix, sell_ix]
            
            message = Message.new_with_blockhash(instructions, owner, recent_blockhash)
            tx = VersionedTransaction(message, [WALLET])
            
            # Execute transaction
            signature = await executor.send_transaction(tx, [WALLET])
            
            if signature:
                logger.info(f"✅ Transaction sent successfully!")
                logger.info(f"🔗 Signature: {signature}")
                
                # Wait for confirmation
                await asyncio.sleep(5)
                
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
                    logger.info(f"🔗 Check transaction: https://solscan.io/tx/{signature}")
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
    print("🔍 TESTING SELL WITH PROPERLY DERIVED PDAs")
    print("="*80)
    
    success = await test_pda_sell()
    
    if success:
        print("\n🎉 SELL TEST PASSED! The PDA derivation works!")
    else:
        print("\n❌ SELL TEST FAILED. Need to try different PDA seeds.")

if __name__ == "__main__":
    asyncio.run(main())
