#!/usr/bin/env python3
"""
Test sell with realistic token amounts based on successful transactions
Key insight: Successful sells use MUCH larger token amounts (trillions, not millions)
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

def create_sell_instruction_realistic_amounts(owner: Pubkey, token_amount: int, min_sol_out: int = 0) -> Instruction:
    """
    Create sell instruction with realistic token amounts based on successful transactions
    """
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_account = get_associated_token_address(owner, token_mint)
    
    logger.info(f"🔧 Building sell instruction with realistic amounts")
    logger.info(f"   Token amount: {token_amount:,} tokens")
    logger.info(f"   Min SOL out: {min_sol_out:,} lamports")
    logger.info(f"   Instruction data: {instruction_data.hex()}")
    
    # Use exact account structure from successful transaction
    accounts = [
        AccountMeta(owner, is_signer=True, is_writable=True),                                                      # [0] User
        AccountMeta(user_token_account, is_signer=False, is_writable=True),                                      # [1] User token account
        AccountMeta(Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"), is_signer=False, is_writable=False),  # [2] Token mint
        AccountMeta(Pubkey.from_string("EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV"), is_signer=False, is_writable=True),   # [3] Bonding curve
        AccountMeta(Pubkey.from_string("AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ"), is_signer=False, is_writable=True),   # [4] Associated bonding curve
        AccountMeta(Pubkey.from_string("9DGQqtdBJHU4fN66cRE1JLVVVJq3KK4mYZxLoSZHqWKf"), is_signer=False, is_writable=True),   # [5] Associated user
        AccountMeta(Pubkey.from_string("DkYPayDaykVxT4RbpNoCct6ztG6kbcgZftjnS6cUb6U"), is_signer=False, is_writable=True),    # [6] Bonding curve token account
        AccountMeta(Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),                # [7] System program
        AccountMeta(Pubkey.from_string("VRbbTzD2HtSwYVtE8VdK5L641K7Zkrj5GgUfDWUJY9j"), is_signer=False, is_writable=False),     # [8] ?
        AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),     # [9] Token program
        AccountMeta(Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),   # [10] Event authority
        AccountMeta(Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"), is_signer=False, is_writable=False),   # [11] Program
    ]
    
    return Instruction(
        program_id=Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"),
        accounts=accounts,
        data=instruction_data
    )

async def test_realistic_sell_amounts():
    """Test sell with realistic token amounts based on successful transactions"""
    logger.info("🧪 Testing sell with REALISTIC token amounts")
    logger.info("📊 Analysis shows successful sells use trillions of tokens, not millions!")
    
    owner = WALLET.pubkey()
    token_mint = Pubkey.from_string(TOKEN_MINT)
    
    # Check initial token balance
    user_token_account = get_associated_token_address(owner, token_mint)
    initial_balance = await get_token_account_balance(user_token_account)
    
    if initial_balance == 0:
        logger.error("❌ No tokens to sell! Run a buy first.")
        return False
    
    logger.info(f"💰 Current token balance: {initial_balance:,}")
    logger.info(f"📈 Successful transactions sold: 20,261,667,116,266 and 3,137,677,000,000 tokens")
    
    # Test different amounts based on our balance
    test_amounts = [
        initial_balance,  # Sell all tokens (like successful transactions)
        initial_balance // 2,  # Sell half
        10_000_000,  # 10M tokens (still much larger than our previous 1M)
        5_000_000,   # 5M tokens
    ]
    
    for i, sell_amount in enumerate(test_amounts):
        if sell_amount <= 0:
            continue
            
        logger.info(f"\n🎯 TEST {i+1}: Selling {sell_amount:,} tokens")
        logger.info(f"   Percentage of balance: {(sell_amount/initial_balance)*100:.1f}%")
        
        # Use 0 min SOL out like successful transaction #2
        min_sol_out = 0
        
        try:
            # Create sell instruction
            sell_ix = create_sell_instruction_realistic_amounts(owner, sell_amount, min_sol_out)
            
            async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
                # Create transaction
                recent_blockhash = await executor.get_latest_blockhash()
                if not recent_blockhash:
                    logger.error("❌ Failed to get recent blockhash")
                    continue
                
                # Add compute budget
                compute_ix = create_compute_budget_ix(600_000, 200_000)  # Higher limits
                
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
                    logger.info(f"📊 Token balance change: {balance_change:,}")
                    
                    if balance_change > 0:
                        logger.info(f"🎉 SUCCESS! Sold {balance_change:,} tokens!")
                        logger.info(f"💰 Remaining balance: {final_balance:,}")
                        logger.info(f"🔗 Check transaction: https://solscan.io/tx/{signature}")
                        return True
                    else:
                        logger.warning(f"⚠️ Transaction succeeded but no tokens were sold")
                        logger.info(f"💰 Balance unchanged: {final_balance:,}")
                        logger.info(f"🔗 Check transaction: https://solscan.io/tx/{signature}")
                        
                        # Continue to next amount if this one didn't work
                        continue
                else:
                    logger.error(f"❌ Transaction failed for amount {sell_amount:,}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error selling {sell_amount:,} tokens: {e}")
            continue
    
    return False

async def main():
    """Main function"""
    print("="*80)
    print("🎯 TESTING REALISTIC SELL AMOUNTS")
    print("💡 Key Insight: Successful sells use TRILLIONS of tokens!")
    print("="*80)
    
    success = await test_realistic_sell_amounts()
    
    if success:
        print("\n🎉 BREAKTHROUGH! Found working sell amount!")
        print("The copy trading bot can now complete the buy-hold-sell cycle!")
    else:
        print("\n🔍 Still investigating... trying different approaches")

if __name__ == "__main__":
    asyncio.run(main())
