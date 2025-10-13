#!/usr/bin/env python3
"""
Test sell instruction using the SAME PDA derivation as the working buy instruction
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
    derive_config_pda,
    derive_route_params_pda,
    derive_route_state_pda,
    derive_token_vault_pda,
    get_metadata_address,
    PUMP_TRADE_PROGRAM_KEY,
    PUMP_FEE_ACCOUNT_KEY,
    PUMP_WSOL_VAULT_KEY,
    TOKEN_PROGRAM_KEY,
    SYS_PROGRAM_ID,
    METADATA_PROGRAM_KEY
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

def create_sell_instruction_same_pdas(
    token_mint: Pubkey,
    owner: Pubkey,
    token_amount: int,
    min_sol_out: int,
    token_ata: Pubkey
) -> Instruction:
    """
    Create sell instruction using the SAME PDA derivation as the working buy instruction
    """
    
    logger.info("🔧 Building sell instruction with same PDAs as buy")
    logger.info(f"Token mint: {token_mint}")
    logger.info(f"Owner: {owner}")
    logger.info(f"Token amount: {token_amount}")
    logger.info(f"Min SOL out: {min_sol_out}")
    
    instruction_data = (
        bytes.fromhex(SELL_DISCRIMINATOR) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    # Use the SAME PDA derivation as the working buy instruction
    config_pda = derive_config_pda()
    route_params_pda = derive_route_params_pda(token_mint)
    route_state_pda = derive_route_state_pda(token_mint)
    token_vault_pda = derive_token_vault_pda(token_mint)
    metadata_key = get_metadata_address(token_mint)
    
    logger.info(f"🔑 Derived PDAs:")
    logger.info(f"   Config PDA: {config_pda}")
    logger.info(f"   Route params PDA: {route_params_pda}")
    logger.info(f"   Route state PDA: {route_state_pda}")
    logger.info(f"   Token vault PDA: {token_vault_pda}")
    logger.info(f"   Metadata key: {metadata_key}")
    
    # Use the SAME account structure as the working buy instruction
    # Just swap the position of user and token_ata since sell is opposite of buy
    accounts = [
        AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),  # 0: Config/authority
        AccountMeta(pubkey=PUMP_FEE_ACCOUNT_KEY, is_signer=False, is_writable=True),  # 1: Fee account  
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
        AccountMeta(pubkey=token_vault_pda, is_signer=False, is_writable=True),  # 3: Token vault
        AccountMeta(pubkey=route_state_pda, is_signer=False, is_writable=True),  # 4: Route state
        AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),  # 5: User token account
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet (signer)
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # 7: System program
        AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),  # 8: Token program
        AccountMeta(pubkey=PUMP_WSOL_VAULT_KEY, is_signer=False, is_writable=True),  # 9: WSOL vault
        AccountMeta(pubkey=METADATA_PROGRAM_KEY, is_signer=False, is_writable=False),  # 10: Metadata program
        AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Trade program
    ]
    
    logger.info("📊 Sell instruction accounts:")
    for i, acc in enumerate(accounts):
        writable_status = '[writable]' if acc.is_writable else ''
        signer_status = '[signer]' if acc.is_signer else ''
        logger.info(f"  {i}: {acc.pubkey} {signer_status} {writable_status}")
    
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,
        accounts=accounts,
        data=instruction_data
    )

async def test_sell_same_pdas():
    """Test sell with same PDA derivation as working buy"""
    logger.info("🧪 Testing sell with SAME PDA derivation as working buy instruction")
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
    sell_amount = min(1_000_000, initial_balance // 10)  # Sell 10% or 1M tokens
    min_sol_out = 1000  # Very small minimum SOL output
    
    logger.info(f"📊 Attempting to sell {sell_amount} tokens for minimum {min_sol_out} lamports")
    
    try:
        # Create sell instruction using same PDAs as buy
        sell_ix = create_sell_instruction_same_pdas(
            token_mint, owner, sell_amount, min_sol_out, user_token_account
        )
        
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            # Create transaction
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                logger.error("❌ Failed to get recent blockhash")
                return False
            
            # Add compute budget
            compute_ix = create_compute_budget_ix(400_000, 100_000)
            
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
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("="*80)
    print("🔍 TESTING SELL WITH SAME PDA DERIVATION AS WORKING BUY")
    print("="*80)
    
    success = await test_sell_same_pdas()
    
    if success:
        print("\n🎉 SELL TEST PASSED! The same PDA derivation works!")
    else:
        print("\n❌ SELL TEST FAILED. Still working on finding the correct structure.")

if __name__ == "__main__":
    asyncio.run(main())
