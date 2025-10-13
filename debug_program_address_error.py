#!/usr/bin/env python3
"""
Debug the InvalidProgramAddress error by testing different account configurations
"""

import asyncio
import json
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.sysvar import RENT as RENT_SYSVAR_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from spl.token.instructions import get_associated_token_address
from env_keys import EnvKeys
import struct

async def debug_account_structure():
    """Debug which account is causing the InvalidProgramAddress error"""
    
    env_keys = EnvKeys()
    client = AsyncClient(env_keys.API_URL, commitment=Confirmed)
    
    # Load wallet
    with open("test_wallet.json", "r") as f:
        wallet_data = json.load(f)
    wallet_keypair = Keypair.from_bytes(wallet_data)
    wallet_pubkey = wallet_keypair.pubkey()
    
    print(f"=== Debugging InvalidProgramAddress Error ===")
    print(f"Wallet: {wallet_pubkey}")
    
    # Constants
    AMM_PROGRAM_ID = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
    POOL_STATE = Pubkey.from_string("58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2")
    POOL_COIN_VAULT = Pubkey.from_string("7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5")
    POOL_PC_VAULT = Pubkey.from_string("GzitgXCvQF23rjsC2EoMb95NJfXYS3qgfSiP6ZKDSKMm")
    WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
    USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    
    # Calculate correct AMM authority
    amm_authority, bump = Pubkey.find_program_address(
        [bytes([5]), bytes(POOL_STATE)], AMM_PROGRAM_ID
    )
    
    # Calculate ATAs
    user_wsol_ata = get_associated_token_address(wallet_pubkey, WSOL_MINT)
    user_usdc_ata = get_associated_token_address(wallet_pubkey, USDC_MINT)
    
    print(f"AMM Authority: {amm_authority} (bump: {bump})")
    print(f"User WSOL ATA: {user_wsol_ata}")
    print(f"User USDC ATA: {user_usdc_ata}")
    
    # Test different account configurations to isolate the problem
    test_configs = [
        # Test 1: Minimal 10-account structure (known to give WrongAccountsNumber)
        {
            "name": "Minimal 10 accounts",
            "accounts": [
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, True),
                AccountMeta(amm_authority, False, False),
                AccountMeta(POOL_COIN_VAULT, False, True),
                AccountMeta(POOL_PC_VAULT, False, True),
                AccountMeta(WSOL_MINT, False, False),
                AccountMeta(USDC_MINT, False, False),
                AccountMeta(user_wsol_ata, False, True),
                AccountMeta(user_usdc_ata, False, True),
                AccountMeta(wallet_pubkey, True, False),
            ]
        },
        
        # Test 2: Test with different AMM authority (from pool state parsing)
        {
            "name": "17 accounts with pool-parsed authority",
            "accounts": [
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, True),
                AccountMeta(Pubkey.from_string("2aPAELzdrHZ8uRaoY1FQ97jnRzgr3PncQsLhgmKvrDxU"), False, False),  # Old authority
                AccountMeta(POOL_COIN_VAULT, False, True),
                AccountMeta(POOL_PC_VAULT, False, True),
                AccountMeta(WSOL_MINT, False, False),
                AccountMeta(USDC_MINT, False, False),
                AccountMeta(user_wsol_ata, False, True),
                AccountMeta(user_usdc_ata, False, True),
                AccountMeta(wallet_pubkey, True, False),
                AccountMeta(SYSTEM_PROGRAM_ID, False, False),
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, False),
                AccountMeta(Pubkey.from_string("2aPAELzdrHZ8uRaoY1FQ97jnRzgr3PncQsLhgmKvrDxU"), False, False),
                AccountMeta(POOL_COIN_VAULT, False, False),
                AccountMeta(POOL_PC_VAULT, False, False),
                AccountMeta(wallet_pubkey, False, False),
            ]
        },
        
        # Test 3: Try with different vault addresses (maybe we have the wrong vaults)
        {
            "name": "17 accounts with alternative vaults",
            "accounts": [
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, True),
                AccountMeta(amm_authority, False, False),
                # Try swapping the vaults
                AccountMeta(POOL_PC_VAULT, False, True),   # PC vault as coin vault
                AccountMeta(POOL_COIN_VAULT, False, True), # Coin vault as PC vault
                AccountMeta(WSOL_MINT, False, False),
                AccountMeta(USDC_MINT, False, False),
                AccountMeta(user_wsol_ata, False, True),
                AccountMeta(user_usdc_ata, False, True),
                AccountMeta(wallet_pubkey, True, False),
                AccountMeta(SYSTEM_PROGRAM_ID, False, False),
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, False),
                AccountMeta(amm_authority, False, False),
                AccountMeta(POOL_PC_VAULT, False, False),
                AccountMeta(POOL_COIN_VAULT, False, False),
                AccountMeta(wallet_pubkey, False, False),
            ]
        },
        
        # Test 4: Try without some of the duplicate accounts
        {
            "name": "14 accounts - reduced duplicates",
            "accounts": [
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(POOL_STATE, False, True),
                AccountMeta(amm_authority, False, False),
                AccountMeta(POOL_COIN_VAULT, False, True),
                AccountMeta(POOL_PC_VAULT, False, True),
                AccountMeta(WSOL_MINT, False, False),
                AccountMeta(USDC_MINT, False, False),
                AccountMeta(user_wsol_ata, False, True),
                AccountMeta(user_usdc_ata, False, True),
                AccountMeta(wallet_pubkey, True, False),
                AccountMeta(SYSTEM_PROGRAM_ID, False, False),
                AccountMeta(RENT_SYSVAR_ID, False, False),
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(amm_authority, False, False),
            ]
        }
    ]
    
    # Test each configuration
    for i, config in enumerate(test_configs):
        print(f"\n=== Test {i+1}: {config['name']} ===")
        print(f"Account count: {len(config['accounts'])}")
        
        try:
            # Create instruction data
            discriminator = 9
            amount_in = 5000000
            min_amount_out = 712500
            instruction_data = struct.pack("<BQQ", discriminator, amount_in, min_amount_out)
            
            # Create instruction
            swap_instruction = Instruction(
                program_id=AMM_PROGRAM_ID,
                accounts=config['accounts'],
                data=instruction_data,
            )
            
            # Get recent blockhash
            recent_blockhash = await client.get_latest_blockhash()
            
            # Create message
            message = MessageV0.try_compile(
                payer=wallet_pubkey,
                instructions=[swap_instruction],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash.value.blockhash,
            )
            
            # Create transaction
            tx = VersionedTransaction(message, [wallet_keypair])
            
            # Simulate the transaction
            simulation_result = await client.simulate_transaction(tx)
            
            if simulation_result.value:
                if simulation_result.value.err:
                    error_str = str(simulation_result.value.err)
                    print(f"  ❌ Simulation failed: {error_str}")
                    
                    # Analyze the error
                    if "WrongAccountsNumber" in error_str:
                        print(f"  📊 Still getting WrongAccountsNumber with {len(config['accounts'])} accounts")
                    elif "InvalidProgramAddress" in error_str:
                        print(f"  🎯 InvalidProgramAddress error - this configuration has address issues")
                    elif "Custom(1)" in error_str:
                        print(f"  🎯 Custom error 1 (InvalidProgramAddress) - address problem confirmed")
                    else:
                        print(f"  🔍 Different error type: {error_str}")
                    
                    # Show logs for debugging
                    if simulation_result.value.logs:
                        print(f"  📝 Logs:")
                        for log in simulation_result.value.logs[-3:]:  # Show last 3 logs
                            print(f"    {log}")
                else:
                    print(f"  ✅ Simulation successful!")
                    print(f"  💰 Compute units used: {simulation_result.value.units_consumed}")
                    print(f"  🎉 FOUND WORKING CONFIGURATION!")
                    break
            else:
                print(f"  ❌ No simulation result")
                
        except Exception as e:
            print(f"  ❌ Error during simulation: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(debug_account_structure())
