#!/usr/bin/env python3
"""
Final sell test: Use exact account structure from successful transaction
but replace user-specific accounts (wallet and token account) with ours
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

# Configuration
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
SELL_DISCRIMINATOR = "33e685a4017f83ad"

# RPC endpoints
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_sell_instruction_exact_mapping(owner: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
    """
    Create sell instruction using exact account structure from successful transaction
    From: 3cVhmonakERwheg7Jidg9aTdTAPNqWG6T37Nfwrb8S5dABbEzvwd8wFqcXAmg4Z1rhuv3q3L3AQvF5TtuHMnHmTV
    
    Replace only the user and token account, keep everything else exactly the same
    """
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_account = get_associated_token_address(owner, token_mint)
    
    logger.info(f"🔄 Replacing user accounts:")
    logger.info(f"   Our wallet: {owner}")
    logger.info(f"   Our token account: {user_token_account}")
    
    # Exact account structure from successful transaction with our accounts substituted
    accounts = [
        AccountMeta(owner, is_signer=True, is_writable=True),                                                      # [0] User (our wallet)
        AccountMeta(user_token_account, is_signer=False, is_writable=True),                                      # [1] User token account (our ATA)
        AccountMeta(Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"), is_signer=False, is_writable=False),  # [2] Token mint (exact)
        AccountMeta(Pubkey.from_string("EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV"), is_signer=False, is_writable=True),   # [3] Bonding curve (exact)
        AccountMeta(Pubkey.from_string("AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ"), is_signer=False, is_writable=True),   # [4] Associated bonding curve (exact)
        AccountMeta(Pubkey.from_string("9DGQqtdBJHU4fN66cRE1JLVVVJq3KK4mYZxLoSZHqWKf"), is_signer=False, is_writable=True),   # [5] Associated user (exact)
        AccountMeta(Pubkey.from_string("DkYPayDaykVxT4RbpNoCct6ztG6kbcgZftjnS6cUb6U"), is_signer=False, is_writable=True),    # [6] Bonding curve token account (exact)
        AccountMeta(Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),                # [7] System program (exact)
        AccountMeta(Pubkey.from_string("VRbbTzD2HtSwYVtE8VdK5L641K7Zkrj5GgUfDWUJY9j"), is_signer=False, is_writable=False),     # [8] ? (exact)
        AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),     # [9] Token program (exact)
        AccountMeta(Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),   # [10] Event authority (exact)
        AccountMeta(Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"), is_signer=False, is_writable=False),   # [11] Program (exact)
    ]
    
    logger.info("📊 Final sell instruction accounts:")
    for i, acc in enumerate(accounts):
        writable_status = '[writable]' if acc.is_writable else ''
        signer_status = '[signer]' if acc.is_signer else ''
        modified = '[MODIFIED]' if i in [0, 1] else '[EXACT]'
        logger.info(f"  {i}: {acc.pubkey} {signer_status} {writable_status} {modified}")
    
    return Instruction(
        program_id=Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"),
        accounts=accounts,
        data=instruction_data
    )

async def test_exact_mapping_sell():
    """Test sell with exact account mapping from successful transaction"""
    logger.info("🧪 Testing sell with EXACT account mapping (substituting only user accounts)")
    logger.info(f"Token: {TOKEN_MINT}")
    logger.info(f"Discriminator: {SELL_DISCRIMINATOR}")
    
    owner = WALLET.pubkey()
    token_mint = Pubkey.from_string(TOKEN_MINT)
    
    # Check initial token balance
    user_token_account = get_associated_token_address(owner, token_mint)
    initial_balance = await get_token_account_balance(user_token_account)
    
    if initial_balance == 0:
        logger.error("❌ No tokens to sell! Run a buy first.")
        return False
    
    logger.info(f"💰 Current token balance: {initial_balance}")
    
    # Test with small amount
    sell_amount = min(500_000, initial_balance // 20)  # Sell 5% or 500K tokens
    min_sol_out = 100  # Very small minimum SOL output
    
    logger.info(f"📊 Attempting to sell {sell_amount} tokens for minimum {min_sol_out} lamports")
    
    try:
        # Create sell instruction with exact mapping
        sell_ix = create_sell_instruction_exact_mapping(owner, sell_amount, min_sol_out)
        
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            # Create transaction
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                logger.error("❌ Failed to get recent blockhash")
                return False
            
            # Add compute budget
            compute_ix = create_compute_budget_ix(500_000, 200_000)  # Increase even more
            
            instructions = [compute_ix, sell_ix]
            
            message = Message.new_with_blockhash(instructions, owner, recent_blockhash)
            tx = VersionedTransaction(message, [WALLET])
            
            # Execute transaction
            signature = await executor.send_transaction(tx, [WALLET])
            
            if signature:
                logger.info(f"✅ Transaction sent successfully!")
                logger.info(f"🔗 Signature: {signature}")
                
                # Wait for confirmation
                await asyncio.sleep(8)  # Wait longer
                
                # Check if token balance changed
                final_balance = await get_token_account_balance(user_token_account)
                
                balance_change = initial_balance - final_balance
                logger.info(f"📊 Token balance change: {balance_change}")
                
                if balance_change > 0:
                    logger.info(f"🎉 SUCCESS! Sold {balance_change} tokens!")
                    logger.info(f"💰 Remaining balance: {final_balance}")
                    
                    # Check SOL balance change
                    logger.info("💰 Checking SOL balance increase...")
                    return True
                else:
                    logger.warning(f"⚠️ Transaction succeeded but no tokens were sold")
                    logger.info(f"💰 Balance unchanged: {final_balance}")
                    logger.info(f"🔗 Transaction details: https://solscan.io/tx/{signature}")
                    
                    # Show transaction success but no token movement
                    logger.info("❓ This suggests the instruction structure is correct but the execution path is different")
                    return False
            else:
                logger.error(f"❌ Transaction failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error during sell: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("="*80)
    print("🎯 FINAL SELL TEST: EXACT ACCOUNT MAPPING")
    print("="*80)
    
    success = await test_exact_mapping_sell()
    
    if success:
        print("\n🎉 BREAKTHROUGH! SELL WORKS WITH EXACT ACCOUNT MAPPING!")
        print("The copy trading bot can now complete the buy-hold-sell cycle!")
    else:
        print("\n💭 ANALYSIS: Transaction succeeds but tokens don't move.")
        print("This suggests we need to investigate:")
        print("1. Different instruction parameters")
        print("2. Token account state requirements") 
        print("3. Pump.fun protocol state changes")
        print("4. Alternative sell methods (Jupiter aggregator)")

if __name__ == "__main__":
    asyncio.run(main())
