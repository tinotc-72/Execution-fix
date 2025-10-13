#!/usr/bin/env python3
"""
Direct Pump.fun Trading - Bypass Jupiter for direct Pump.fun trades
"""

import asyncio
import logging
import struct
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction, VersionedTransaction
from solders.message import MessageV0
from solders.system_program import transfer, TransferParams
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solana.rpc.types import TxOpts

logger = logging.getLogger(__name__)

class DirectPumpFunTrader:
    """Direct Pump.fun trading without Jupiter dependency"""
    
    # Pump.fun program constants (FIXED - CORRECT PROGRAM ID)
    PUMP_PROGRAM = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
    GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
    FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV3cnbxcUU5BC2qsJ")
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
    
    async def buy_token_direct(self, wallet: Keypair, token_mint: str, sol_amount: float) -> Dict[str, Any]:
        """Buy token directly on Pump.fun"""
        try:
            logger.info(f"🚀 Direct Pump.fun BUY: {sol_amount} SOL → {token_mint}")
            
            token_pubkey = Pubkey.from_string(token_mint)
            sol_lamports = int(sol_amount * 1e9)
            
            # Get token account
            from spl.token.instructions import get_associated_token_address
            token_account = get_associated_token_address(wallet.pubkey(), token_pubkey)
            
            # 🔍 CHECK IF TOKEN ACCOUNT EXISTS (ELIMINATES IllegalOwner errors)
            logger.info(f"🔍 Checking if ATA exists for token {token_mint[:8]}...")
            account_info = await self.rpc_client.get_account_info(token_account)
            
            if not account_info.value:
                # 🔨 ONLY CREATE IF IT DOESN'T EXIST
                logger.info("🔨 ATA doesn't exist, creating associated token account...")
                create_result = await self._create_token_account(wallet, token_pubkey)
                if not create_result['success']:
                    return {"success": False, "signature": "", "error": "Failed to create token account"}
            else:
                logger.info(f"✅ ATA already exists, skipping creation: {str(token_account)[:8]}...")
            
            # Build Pump.fun buy instruction
            buy_instruction = self._build_pump_buy_instruction(
                wallet.pubkey(),
                token_pubkey,
                token_account,
                sol_lamports
            )
            
            # CRITICAL FIX: Create transaction correctly with recent blockhash
            recent_blockhash = await self.rpc_client.get_latest_blockhash()
            
            # Create transaction using MessageV0 (proper way)
            message = MessageV0.try_compile(
                payer=wallet.pubkey(),
                instructions=[buy_instruction],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash.value.blockhash
            )
            
            # Create VersionedTransaction and sign it
            transaction = VersionedTransaction(message, [wallet])
            
            result = await self.rpc_client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=False, preflight_commitment=Processed)
            )
            
            if result.value:
                logger.info(f"✅ Direct Pump.fun buy successful: {result.value}")
                return {"success": True, "signature": str(result.value)}
            else:
                return {"success": False, "signature": "", "error": "Transaction failed"}
                
        except Exception as e:
            logger.error(f"❌ Direct Pump.fun buy error: {e}")
            return {"success": False, "signature": "", "error": str(e)}
    
    def _build_pump_buy_instruction(self, wallet_pubkey: Pubkey, token_mint: Pubkey, 
                                   token_account: Pubkey, sol_amount: int) -> Instruction:
        """Build Pump.fun buy instruction"""
        
        # Pump.fun buy discriminator
        discriminator = bytes.fromhex("66063d1201daebea")
        
        # Build instruction data
        data = discriminator + struct.pack("<Q", sol_amount) + struct.pack("<Q", 0)  # slippage
        
        # Build accounts
        accounts = [
            AccountMeta(self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(self.FEE_RECIPIENT, is_signer=False, is_writable=True),
            AccountMeta(token_mint, is_signer=False, is_writable=False),
            AccountMeta(wallet_pubkey, is_signer=True, is_writable=True),
            AccountMeta(token_account, is_signer=False, is_writable=True),
            AccountMeta(Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),
            AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),
            AccountMeta(Pubkey.from_string("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False),
        ]
        
        return Instruction(
            program_id=self.PUMP_PROGRAM,
            accounts=accounts,
            data=data
        )
    
    async def _create_token_account(self, wallet: Keypair, token_mint: Pubkey) -> Dict[str, Any]:
        """Create associated token account"""
        try:
            from spl.token.instructions import create_associated_token_account
            
            instruction = create_associated_token_account(
                payer=wallet.pubkey(),
                owner=wallet.pubkey(),
                mint=token_mint
            )
            
            # CRITICAL FIX: Create transaction correctly with recent blockhash
            recent_blockhash = await self.rpc_client.get_latest_blockhash()
            
            # Create transaction using MessageV0 (proper way)
            message = MessageV0.try_compile(
                payer=wallet.pubkey(),
                instructions=[instruction],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash.value.blockhash
            )
            
            # Create VersionedTransaction and sign it
            transaction = VersionedTransaction(message, [wallet])
            
            result = await self.rpc_client.send_transaction(transaction)
            
            if result.value:
                return {"success": True, "signature": str(result.value)}
            else:
                return {"success": False, "signature": "", "error": "Failed to create account"}
                
        except Exception as e:
            logger.error(f"Error creating token account: {e}")
            return {"success": False, "signature": "", "error": str(e)}

# Integration functions for main bot
async def try_direct_pumpfun_buy(wallet: Keypair, token_mint: str, amount_sol: float) -> Dict[str, Any]:
    """Direct Pump.fun buy function for integration"""
    from env_keys import kz
    
    client = AsyncClient(kz.HELIUS_RPC_URL)
    trader = DirectPumpFunTrader(client)
    
    try:
        result = await trader.buy_token_direct(wallet, token_mint, amount_sol)
        return result
    finally:
        await client.close()

async def try_direct_pumpfun_sell(wallet: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """Direct Pump.fun sell function for integration (placeholder)"""
    logger.info("💸 Direct Pump.fun sell not implemented, falling back to other DEXes...")
    return {"success": False, "signature": "", "error": "Direct sell not implemented"}
