# jito_tips.py
"""
Jito tipping functionality following official documentation
https://docs.jito.wtf/lowlatencytxnsend/#tips
"""

import asyncio
import random
from typing import List, Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solders.instruction import Instruction

class JitoTips:
    """Handle Jito tip creation and management"""
    
    # Official Jito tip accounts from documentation
    TIP_ACCOUNTS = [
        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
        "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe", 
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
        "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
        "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
        "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
        "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
    ]
    
    # Minimum tip required by Jito (1000 lamports)
    MIN_TIP_LAMPORTS = 1000
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
    
    def get_random_tip_account(self) -> Pubkey:
        """Get a random tip account to reduce contention as recommended"""
        tip_account_str = random.choice(self.TIP_ACCOUNTS)
        return Pubkey.from_string(tip_account_str)
    
    async def create_tip_instruction(self, 
                                   payer: Keypair, 
                                   tip_lamports: int = MIN_TIP_LAMPORTS) -> Instruction:
        """Create a tip instruction following Jito best practices"""
        try:
            # Ensure minimum tip
            if tip_lamports < self.MIN_TIP_LAMPORTS:
                tip_lamports = self.MIN_TIP_LAMPORTS
                print(f"⚠️ Tip increased to minimum: {tip_lamports} lamports")
            
            # Get random tip account
            tip_account = self.get_random_tip_account()
            
            print(f"💡 Creating tip: {tip_lamports} lamports to {tip_account}")
            
            # Create transfer instruction
            tip_instruction = transfer(
                TransferParams(
                    from_pubkey=payer.pubkey(),
                    to_pubkey=tip_account,
                    lamports=tip_lamports
                )
            )
            
            return tip_instruction
            
        except Exception as e:
            print(f"❌ Error creating tip instruction: {e}")
            raise
    
    async def add_tip_to_transaction(self, 
                                   transaction: VersionedTransaction,
                                   payer: Keypair,
                                   tip_lamports: int = MIN_TIP_LAMPORTS) -> VersionedTransaction:
        """Add tip instruction to existing transaction (preferred method)"""
        try:
            print(f"💡 Adding {tip_lamports} lamport tip to transaction...")
            
            # Create tip instruction
            tip_instruction = await self.create_tip_instruction(payer, tip_lamports)
            
            # Get existing message
            existing_message = transaction.message
            
            # Create new instructions list with tip added
            existing_instructions = list(existing_message.instructions)
            existing_instructions.append(tip_instruction)
            
            # Get recent blockhash
            recent_blockhash_resp = await self.rpc_client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Create new message with tip instruction included
            new_message = MessageV0.try_compile(
                payer=payer.pubkey(),
                instructions=existing_instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            # Create new versioned transaction
            tipped_transaction = VersionedTransaction(new_message, [payer])
            
            print(f"✅ Tip added successfully to transaction")
            return tipped_transaction
            
        except Exception as e:
            print(f"❌ Error adding tip to transaction: {e}")
            raise
    
    async def create_standalone_tip_transaction(self, 
                                              payer: Keypair,
                                              tip_lamports: int = MIN_TIP_LAMPORTS) -> VersionedTransaction:
        """Create standalone tip transaction (use with caution per documentation)"""
        try:
            print(f"💡 Creating standalone tip transaction: {tip_lamports} lamports")
            
            # Create tip instruction
            tip_instruction = await self.create_tip_instruction(payer, tip_lamports)
            
            # Get recent blockhash
            recent_blockhash_resp = await self.rpc_client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Create message
            message = MessageV0.try_compile(
                payer=payer.pubkey(),
                instructions=[tip_instruction],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            # Create and sign transaction
            tip_transaction = VersionedTransaction(message, [payer])
            
            print(f"✅ Standalone tip transaction created")
            return tip_transaction
            
        except Exception as e:
            print(f"❌ Error creating standalone tip transaction: {e}")
            raise
    
    @staticmethod
    def calculate_recommended_tip(priority_fee_lamports: int) -> int:
        """Calculate recommended tip based on priority fee (for sendTransaction method)"""
        # Documentation recommends 70/30 split for sendTransaction
        # But for sendBundle, only Jito tip matters
        recommended_tip = max(JitoTips.MIN_TIP_LAMPORTS, int(priority_fee_lamports * 0.3))
        return recommended_tip
    
    @staticmethod
    def get_tip_accounts() -> List[str]:
        """Get all official Jito tip accounts"""
        return JitoTips.TIP_ACCOUNTS.copy()
