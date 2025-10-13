#!/usr/bin/env python3
"""
Debug Transaction Analysis
=========================

This script will analyze recent transactions from the target wallets to see
what program IDs are actually being used in their trades.
"""

import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.commitment import Confirmed
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_tx")

# Load environment
env = EnvKeys()

TARGET_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
    "HKwCgqkgBjkpuv3b8ZcEJ3oNxsR7Sf4WtbDLoyjkT26J"
]

async def analyze_recent_transactions():
    """Analyze recent transactions from target wallets"""
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    for wallet_address in TARGET_WALLETS:
        logger.info(f"\n🔍 Analyzing recent transactions for: {wallet_address}")
        
        try:
            # Get recent transactions
            response = await client.get_signatures_for_address(
                Pubkey.from_string(wallet_address),
                limit=10
            )
            
            if not response.value:
                logger.info("No transactions found")
                continue
                
            for i, tx_info in enumerate(response.value[:3]):  # Just analyze first 3
                signature = str(tx_info.signature)
                logger.info(f"\n📋 Transaction {i+1}: {signature}")
                
                # Get transaction details
                try:
                    sig_obj = Signature.from_string(signature)
                    tx_response = await client.get_transaction(
                        sig_obj,
                        encoding="jsonParsed",
                        commitment=Confirmed,
                        max_supported_transaction_version=0
                    )
                    
                    if not tx_response or not tx_response.value:
                        logger.warning(f"Transaction not found: {signature}")
                        continue
                        
                    tx = tx_response.value
                    
                    # Analyze transaction structure
                    if hasattr(tx, 'transaction'):
                        tx_data = tx.transaction
                    else:
                        tx_data = tx
                        
                    if hasattr(tx_data, 'message'):
                        tx_message = tx_data.message
                    elif hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
                        tx_message = tx_data.transaction.message
                    else:
                        logger.error(f"Cannot find transaction message")
                        continue
                        
                    instructions = tx_message.instructions
                    logger.info(f"   Instructions: {len(instructions)}")
                    
                    # Analyze each instruction
                    for j, instruction in enumerate(instructions):
                        try:
                            program_id = None
                            if hasattr(instruction, 'program_id'):
                                program_id = str(instruction.program_id)
                            elif hasattr(instruction, 'program_id_index'):
                                if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
                                    program_id = str(tx_message.account_keys[instruction.program_id_index])
                            
                            if program_id:
                                logger.info(f"     Instruction {j}: {program_id}")
                                
                                # Check if it's a known DEX
                                dex_programs = {
                                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                                    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
                                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                                    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
                                    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
                                    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                                    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
                                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
                                    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun Program",
                                    "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump": "Pump.fun Trading",
                                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
                                    "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Global",
                                    "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
                                    "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
                                    "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
                                    "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity",
                                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program",
                                    "11111111111111111111111111111112": "System Program",
                                    "ComputeBudget111111111111111111111111111111": "Compute Budget"
                                }
                                
                                if program_id in dex_programs:
                                    logger.info(f"       🎯 KNOWN DEX: {dex_programs[program_id]}")
                                else:
                                    logger.info(f"       ❓ Unknown program: {program_id}")
                                    
                            else:
                                logger.warning(f"     Instruction {j}: No program ID found")
                                
                        except Exception as e:
                            logger.error(f"Error processing instruction {j}: {e}")
                    
                    # Check for token balance changes
                    if hasattr(tx, 'meta') and tx.meta:
                        meta = tx.meta
                        if hasattr(meta, 'pre_token_balances') and hasattr(meta, 'post_token_balances'):
                            pre_tokens = len(meta.pre_token_balances)
                            post_tokens = len(meta.post_token_balances)
                            logger.info(f"   Token balances: {pre_tokens} pre → {post_tokens} post")
                            
                            # Check for wallet-specific changes
                            wallet_pre = [b for b in meta.pre_token_balances if hasattr(b, 'owner') and str(b.owner) == wallet_address]
                            wallet_post = [b for b in meta.post_token_balances if hasattr(b, 'owner') and str(b.owner) == wallet_address]
                            
                            if wallet_pre or wallet_post:
                                logger.info(f"   Wallet token changes: {len(wallet_pre)} pre → {len(wallet_post)} post")
                                
                                for balance in wallet_pre:
                                    amount = float(balance.ui_token_amount.ui_amount or 0)
                                    logger.info(f"     PRE: {balance.mint[:8]}... = {amount}")
                                    
                                for balance in wallet_post:
                                    amount = float(balance.ui_token_amount.ui_amount or 0)
                                    logger.info(f"     POST: {balance.mint[:8]}... = {amount}")
                        
                except Exception as e:
                    logger.error(f"Error analyzing transaction {signature}: {e}")
                    
        except Exception as e:
            logger.error(f"Error getting transactions for {wallet_address}: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_recent_transactions())
