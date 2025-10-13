#!/usr/bin/env python3
"""
Debug Raydium account structure systematically
Testing different account counts and orders to find the correct structure
"""

import asyncio
import struct
import logging
from typing import Optional
from env_keys import load_wallet_from_private_key, validate_env_vars
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import AccountMeta, Instruction
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from spl.token.instructions import get_associated_token_address

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
RAYDIUM_V4_AMM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")

# Pool addresses
POOL_STATE = Pubkey.from_string("58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2")
SOL_VAULT = Pubkey.from_string("7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5")
USDC_VAULT = Pubkey.from_string("GzitgXCvQF23rjsC2EoMb95NJfXYS3qgfSiP6ZKDSKMm")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

def get_amm_authority(pool_state: Pubkey) -> Pubkey:
    """Get AMM authority PDA"""
    authority, _ = Pubkey.find_program_address([bytes([5]), bytes(pool_state)], RAYDIUM_V4_AMM)
    return authority

async def test_account_structure(client: AsyncClient, wallet: Keypair, test_name: str, accounts: list[AccountMeta]) -> bool:
    """Test a specific account structure"""
    logger.info(f"\n🧪 Testing {test_name} ({len(accounts)} accounts)")
    
    # Build instruction data
    amount_in = 1000000
    min_out = 142500
    side = 0
    data = struct.pack("<BQQ", 2, amount_in, min_out) + bytes([side])
    
    # Create instruction
    swap_ix = Instruction(
        program_id=RAYDIUM_V4_AMM,
        data=data,
        accounts=accounts
    )
    
    # Build transaction
    try:
        resp = await client.get_latest_blockhash()
        message = MessageV0.try_compile(
            payer=wallet.pubkey(),
            instructions=[
                set_compute_unit_limit(200_000),
                set_compute_unit_price(1),
                swap_ix
            ],
            address_lookup_table_accounts=[],
            recent_blockhash=resp.value.blockhash
        )
        
        tx = VersionedTransaction(message, [wallet])
        
        # Simulate transaction
        result = await client.simulate_transaction(tx)
        
        if result.value.err is None:
            logger.info(f"✅ {test_name} - SIMULATION SUCCESSFUL!")
            return True
        else:
            error_msg = str(result.value.err)
            logger.info(f"❌ {test_name} - Error: {error_msg}")
            
            # Log specific errors
            if "WrongAccountsNumber" in error_msg or "0x18" in error_msg:
                logger.info(f"   Wrong account count (expected different number)")
            elif "InvalidProgramAddress" in error_msg or "0x1" in error_msg:
                logger.info(f"   Invalid program address (wrong account address)")
            elif "InsufficientFunds" in error_msg:
                logger.info(f"   Insufficient funds (expected for simulation)")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ {test_name} - Exception: {e}")
        return False

async def main():
    """Test different account structures"""
    # Load wallet
    env_vars = validate_env_vars()
    wallet = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
    
    # User accounts
    user_wallet = wallet.pubkey()
    wsol_ata = get_associated_token_address(user_wallet, NATIVE_MINT)
    usdc_ata = get_associated_token_address(user_wallet, USDC_MINT)
    amm_authority = get_amm_authority(POOL_STATE)
    
    logger.info(f"👛 Wallet: {user_wallet}")
    logger.info(f"🪙 WSOL ATA: {wsol_ata}")
    logger.info(f"💰 USDC ATA: {usdc_ata}")
    logger.info(f"🏛️ AMM Authority: {amm_authority}")
    
    async with AsyncClient(env_vars["RPC_URL"]) as client:
        # Test 1: 11 accounts (from working implementation)
        accounts_11 = [
            AccountMeta(user_wallet, True, True),         # 0: User wallet (signer)
            AccountMeta(wsol_ata, False, True),          # 1: User WSOL account
            AccountMeta(usdc_ata, False, True),          # 2: User USDC account
            AccountMeta(POOL_STATE, False, True),        # 3: Pool state
            AccountMeta(amm_authority, False, False),    # 4: Pool authority
            AccountMeta(SOL_VAULT, False, True),         # 5: SOL vault
            AccountMeta(USDC_VAULT, False, True),        # 6: USDC vault
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 7: Token program
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 8: Token program (duplicate)
            AccountMeta(NATIVE_MINT, False, False),      # 9: WSOL mint
            AccountMeta(USDC_MINT, False, False),        # 10: USDC mint
        ]
        
        success = await test_account_structure(client, wallet, "11 Accounts (from working impl)", accounts_11)
        if success:
            logger.info("🎉 Found working structure!")
            return
        
        # Test 2: 10 accounts (remove duplicate token program)
        accounts_10 = [
            AccountMeta(user_wallet, True, True),         # 0: User wallet (signer)
            AccountMeta(wsol_ata, False, True),          # 1: User WSOL account
            AccountMeta(usdc_ata, False, True),          # 2: User USDC account
            AccountMeta(POOL_STATE, False, True),        # 3: Pool state
            AccountMeta(amm_authority, False, False),    # 4: Pool authority
            AccountMeta(SOL_VAULT, False, True),         # 5: SOL vault
            AccountMeta(USDC_VAULT, False, True),        # 6: USDC vault
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 7: Token program
            AccountMeta(NATIVE_MINT, False, False),      # 8: WSOL mint
            AccountMeta(USDC_MINT, False, False),        # 9: USDC mint
        ]
        
        success = await test_account_structure(client, wallet, "10 Accounts (no duplicate token program)", accounts_10)
        if success:
            logger.info("🎉 Found working structure!")
            return
            
        # Test 3: 9 accounts (remove user wallet as it's already payer)
        accounts_9 = [
            AccountMeta(wsol_ata, False, True),          # 0: User WSOL account
            AccountMeta(usdc_ata, False, True),          # 1: User USDC account
            AccountMeta(POOL_STATE, False, True),        # 2: Pool state
            AccountMeta(amm_authority, False, False),    # 3: Pool authority
            AccountMeta(SOL_VAULT, False, True),         # 4: SOL vault
            AccountMeta(USDC_VAULT, False, True),        # 5: USDC vault
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 6: Token program
            AccountMeta(NATIVE_MINT, False, False),      # 7: WSOL mint
            AccountMeta(USDC_MINT, False, False),        # 8: USDC mint
        ]
        
        success = await test_account_structure(client, wallet, "9 Accounts (no user wallet)", accounts_9)
        if success:
            logger.info("🎉 Found working structure!")
            return
            
        # Test 4: Different order - token program first
        accounts_11_alt = [
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 0: Token program
            AccountMeta(POOL_STATE, False, True),        # 1: Pool state
            AccountMeta(amm_authority, False, False),    # 2: Pool authority
            AccountMeta(SOL_VAULT, False, True),         # 3: SOL vault
            AccountMeta(USDC_VAULT, False, True),        # 4: USDC vault
            AccountMeta(NATIVE_MINT, False, False),      # 5: WSOL mint
            AccountMeta(USDC_MINT, False, False),        # 6: USDC mint
            AccountMeta(wsol_ata, False, True),          # 7: User WSOL account
            AccountMeta(usdc_ata, False, True),          # 8: User USDC account
            AccountMeta(user_wallet, True, True),        # 9: User wallet (signer)
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 10: Token program (duplicate)
        ]
        
        success = await test_account_structure(client, wallet, "11 Accounts (different order)", accounts_11_alt)
        if success:
            logger.info("🎉 Found working structure!")
            return
            
        # Test 5: Try with 8 accounts (minimal)
        accounts_8 = [
            AccountMeta(user_wallet, True, True),        # 0: User wallet (signer)
            AccountMeta(wsol_ata, False, True),          # 1: User WSOL account
            AccountMeta(usdc_ata, False, True),          # 2: User USDC account
            AccountMeta(POOL_STATE, False, True),        # 3: Pool state
            AccountMeta(amm_authority, False, False),    # 4: Pool authority
            AccountMeta(SOL_VAULT, False, True),         # 5: SOL vault
            AccountMeta(USDC_VAULT, False, True),        # 6: USDC vault
            AccountMeta(TOKEN_PROGRAM_ID, False, False), # 7: Token program
        ]
        
        success = await test_account_structure(client, wallet, "8 Accounts (minimal)", accounts_8)
        if success:
            logger.info("🎉 Found working structure!")
            return
            
        logger.info("❌ No working structure found in these tests")
        logger.info("💡 The issue might be:")
        logger.info("   - Wrong instruction discriminator (we're using 2)")
        logger.info("   - Wrong pool addresses")
        logger.info("   - Wrong AMM authority derivation")
        logger.info("   - Different instruction format needed")

if __name__ == "__main__":
    asyncio.run(main())
