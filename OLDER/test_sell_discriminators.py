#!/usr/bin/env python3
"""
Test different sell discriminators based on pump.fun patterns
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
    PUMP_TRADE_PROGRAM_KEY
)
from utils import get_token_account_balance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - using the successful token
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

# Different sell discriminators to try
SELL_DISCRIMINATORS = [
    "33e685a4017f83ad",  # Current assumption
    "b712469c946da122",  # Alternative 1
    "e445a52e51cb9a1d",  # Alternative 2
    "516e5c0b4c5d6c14",  # Alternative 3
    "a0d4b8b8b8b8b8b8",  # Alternative 4
]

def create_sell_instruction_variant(owner: Pubkey, token_amount: int, min_sol_out: int, discriminator: str, variant: int) -> Instruction:
    """Create sell instruction with different discriminator and account arrangement"""
    
    instruction_data = (
        bytes.fromhex(discriminator) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Base accounts that are consistent
    base_accounts = [
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
    
    # Try different account arrangements
    if variant == 1:
        # Swap user token account and token vault positions (like in buy vs sell)
        accounts = [
            base_accounts[0],  # Config
            base_accounts[1],  # PDA
            base_accounts[2],  # Token mint
            base_accounts[5],  # User token account (moved from position 5 to 3)
            base_accounts[4],  # Route state
            base_accounts[3],  # Token vault (moved from position 3 to 5)
            base_accounts[6],  # User wallet
            base_accounts[7],  # System program
            base_accounts[8],  # Token program
            base_accounts[9],  # Other account
            base_accounts[10], # Event authority
            base_accounts[11], # Program ID
        ]
    elif variant == 2:
        # Remove event authority (some sells might not use it)
        accounts = base_accounts[:-2]  # Remove event authority and program ID from end
        accounts.append(base_accounts[-1])  # Add program ID back
    elif variant == 3:
        # Minimal account set
        accounts = [
            base_accounts[0],  # Config
            base_accounts[1],  # PDA  
            base_accounts[2],  # Token mint
            base_accounts[5],  # User token account
            base_accounts[3],  # Token vault
            base_accounts[6],  # User wallet
            base_accounts[7],  # System program
            base_accounts[8],  # Token program
        ]
    else:
        # Default: same as buy but with positions 3 and 5 swapped
        accounts = base_accounts
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_sell_variants():
    """Test different sell instruction variants"""
    logger.info("🧪 Testing different sell instruction variants")
    logger.info("=" * 60)
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check current token balance
            current_balance = await get_token_account_balance(token_ata)
            logger.info(f"Current token balance: {current_balance:,} tokens")
            
            if current_balance == 0:
                logger.warning("❌ No tokens to sell!")
                return
            
            # Test amount: sell 1000 tokens (small test)
            test_amount = min(1000, current_balance)
            min_sol_out = 0  # Accept any amount of SOL
            
            logger.info(f"Testing with {test_amount:,} tokens")
            
            # Test each discriminator and variant combination
            for disc_idx, discriminator in enumerate(SELL_DISCRIMINATORS):
                for variant in range(1, 5):  # Test variants 1-4
                    logger.info(f"\n🧪 Testing discriminator {disc_idx+1}/{len(SELL_DISCRIMINATORS)}: {discriminator}, variant {variant}")
                    
                    try:
                        # Build transaction
                        instructions = []
                        
                        # Compute budget
                        compute_ix = create_compute_budget_ix(compute_units=300_000)
                        instructions.append(compute_ix)
                        
                        # Sell instruction
                        sell_ix = create_sell_instruction_variant(
                            wallet.pubkey(), 
                            test_amount, 
                            min_sol_out,
                            discriminator,
                            variant
                        )
                        instructions.append(sell_ix)
                        
                        # Create transaction
                        message = Message.new_with_blockhash(
                            instructions,
                            wallet.pubkey(),
                            await executor.get_latest_blockhash()
                        )
                        
                        tx = VersionedTransaction(message, [wallet])
                        
                        # Send transaction
                        tx_sig = await executor.send_transaction(tx)
                        logger.info(f"✅ Transaction sent: {tx_sig}")
                        logger.info(f"🔗 Solscan: https://solscan.io/tx/{tx_sig}")
                        
                        # Wait a moment then check if it worked
                        await asyncio.sleep(3)
                        new_balance = await get_token_account_balance(token_ata)
                        
                        if new_balance < current_balance:
                            logger.info(f"🎉 SUCCESS! Tokens sold: {current_balance - new_balance:,}")
                            logger.info(f"🏆 Working combination: Discriminator {discriminator}, Variant {variant}")
                            return
                        else:
                            logger.warning(f"⚠️  Transaction sent but no tokens sold")
                            
                    except Exception as e:
                        logger.error(f"❌ Failed: {e}")
                        
                    # Small delay between tests
                    await asyncio.sleep(1)
            
            logger.warning("❌ No working sell instruction found")
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        raise

async def main():
    """Main function"""
    logger.info("🚀 Starting sell instruction variant testing")
    
    try:
        await test_sell_variants()
        logger.info("\n✅ Testing complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
