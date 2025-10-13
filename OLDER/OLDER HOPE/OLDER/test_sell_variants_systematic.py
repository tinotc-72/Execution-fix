#!/usr/bin/env python3
"""
Systematic test of different account arrangements for sell instruction
Using the correct discriminator (33e685a4017f83ad) but testing account order
"""

import asyncio
import logging
from typing import List

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
SELL_DISCRIMINATOR = "33e685a4017f83ad"  # Correct Anchor discriminator for "sell"
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

def create_sell_instruction_variant(owner: Pubkey, token_amount: int, min_sol_out: int, variant: int) -> Instruction:
    """Create sell instruction with different account arrangements"""
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Base accounts from successful buy instruction
    config = AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False)
    pda = AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True)
    mint = AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False)
    token_vault = AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True)
    route_state = AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True)
    user_ata = AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True)
    user_wallet = AccountMeta(pubkey=owner, is_signer=True, is_writable=True)
    system_program = AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False)
    token_program = AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False)
    other_account = AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True)
    event_authority = AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False)
    program_id_account = AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False)
    
    # BUY order: config, pda, mint, token_vault, route_state, user_ata, user_wallet, system_program, token_program, other_account, event_authority, program_id
    buy_order = [config, pda, mint, token_vault, route_state, user_ata, user_wallet, system_program, token_program, other_account, event_authority, program_id_account]
    
    if variant == 1:
        # Variant 1: Swap token_vault and user_ata positions (positions 3 and 5)
        accounts = [config, pda, mint, user_ata, route_state, token_vault, user_wallet, system_program, token_program, other_account, event_authority, program_id_account]
        
    elif variant == 2:
        # Variant 2: Same as buy order (no changes)
        accounts = buy_order
        
    elif variant == 3:
        # Variant 3: Remove event_authority
        accounts = [config, pda, mint, user_ata, route_state, token_vault, user_wallet, system_program, token_program, other_account]
        
    elif variant == 4:
        # Variant 4: Minimal set
        accounts = [config, pda, mint, user_ata, token_vault, user_wallet, system_program, token_program]
        
    elif variant == 5:
        # Variant 5: Different order - user_ata before mint
        accounts = [config, pda, user_ata, mint, token_vault, route_state, user_wallet, system_program, token_program, other_account, event_authority, program_id_account]
        
    elif variant == 6:
        # Variant 6: token_vault first after pda
        accounts = [config, pda, token_vault, mint, user_ata, route_state, user_wallet, system_program, token_program, other_account, event_authority, program_id_account]
        
    elif variant == 7:
        # Variant 7: Reverse some core accounts
        accounts = [config, pda, mint, route_state, token_vault, user_ata, user_wallet, system_program, token_program, other_account, event_authority, program_id_account]
        
    elif variant == 8:
        # Variant 8: Put user_wallet before user_ata
        accounts = [config, pda, mint, token_vault, route_state, user_wallet, user_ata, system_program, token_program, other_account, event_authority, program_id_account]
        
    else:
        # Default: same as buy
        accounts = buy_order
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_sell_variants():
    """Test different sell instruction variants systematically"""
    logger.info("🧪 Testing sell instruction variants systematically")
    logger.info("=" * 60)
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check current token balance
            initial_balance = await get_token_account_balance(token_ata)
            logger.info(f"Initial token balance: {initial_balance:,} tokens")
            
            if initial_balance == 0:
                logger.warning("❌ No tokens to sell!")
                return
            
            # Test with a small amount first
            test_amount = min(1000, initial_balance)
            min_sol_out = 0  # Accept any amount of SOL
            
            logger.info(f"Testing sell with {test_amount:,} tokens")
            logger.info(f"Using discriminator: {SELL_DISCRIMINATOR}")
            
            # Test each variant
            for variant in range(1, 9):
                logger.info(f"\n🧪 Testing variant {variant}/8")
                
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
                    tx_sig = await executor.send_transaction(tx, [wallet])
                    
                    if tx_sig:
                        logger.info(f"✅ Transaction sent: {tx_sig}")
                        logger.info(f"🔗 Solscan: https://solscan.io/tx/{tx_sig}")
                        
                        # Wait and check result
                        await asyncio.sleep(3)
                        new_balance = await get_token_account_balance(token_ata)
                        
                        if new_balance < initial_balance:
                            tokens_sold = initial_balance - new_balance
                            logger.info(f"🎉 SUCCESS! Variant {variant} WORKED!")
                            logger.info(f"✅ Sold {tokens_sold:,} tokens!")
                            logger.info(f"🏆 Working variant: {variant}")
                            return variant  # Return the working variant
                        else:
                            logger.warning(f"⚠️  No tokens sold (balance: {new_balance:,})")
                    else:
                        logger.error(f"❌ Failed to send transaction")
                        
                except Exception as e:
                    logger.error(f"❌ Variant {variant} failed: {e}")
                    
                # Small delay between tests
                await asyncio.sleep(2)
            
            logger.warning("❌ No working variant found")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        raise

async def main():
    """Main function"""
    logger.info("🚀 Starting systematic sell variant testing")
    
    try:
        working_variant = await test_sell_variants()
        
        if working_variant:
            logger.info(f"\n🎉 SUCCESS! Working variant found: {working_variant}")
        else:
            logger.info("\n❌ No working variant found")
        
        logger.info("\n✅ Testing complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
