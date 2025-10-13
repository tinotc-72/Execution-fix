"""
Simple Working MEV Bot - No Address Lookup Tables
Using only the essential accounts for Pump.fun trading
"""

import asyncio
import logging
from typing import Optional
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.hash import Hash
import httpx
from base58 import b58encode
import struct

from env_keys import EnvKeys

logger = logging.getLogger(__name__)

class SimpleMEVBot:
    """
    Simple working MEV bot for Pump.fun
    No address lookup tables - just the core accounts
    """
    
    def __init__(self, env_keys: EnvKeys):
        self.env = env_keys
        self.keypair = Keypair.from_base58_string(env_keys.PHANTOM_PRIVATE_KEY)
        self.wallet_address = self.keypair.pubkey()
        
        # Core programs
        self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Constants
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        
        # MEV priority
        self.PRIORITY_FEE = 500_000
        
    async def get_recent_blockhash(self) -> Hash:
        """Get recent blockhash"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.env.HELIUS_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "confirmed"}]
                }
            )
            
            data = response.json()
            if 'result' in data:
                blockhash_str = data['result']['value']['blockhash']
                return Hash.from_string(blockhash_str)
            
            raise Exception("Failed to get blockhash")
    
    def derive_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
        """Derive associated token address"""
        seeds = [
            bytes(owner),
            bytes(self.TOKEN_PROGRAM),
            bytes(mint)
        ]
        
        return Pubkey.find_program_address(
            seeds,
            self.ASSOCIATED_TOKEN_PROGRAM
        )[0]
    
    def derive_bonding_curve(self, mint: Pubkey) -> Pubkey:
        """Derive bonding curve"""
        return Pubkey.find_program_address(
            [b"bonding-curve", bytes(mint)],
            self.PUMP_FUN_PROGRAM
        )[0]
    
    async def simple_buy(self, mint_address: str, sol_amount: float) -> Optional[str]:
        """
        Simple buy using minimal account set
        """
        try:
            logger.info(f"🚀 Simple MEV buy: {sol_amount} SOL for {mint_address}")
            
            mint_pubkey = Pubkey.from_string(mint_address)
            sol_lamports = int(sol_amount * 1_000_000_000)
            
            # Derive core accounts
            bonding_curve = self.derive_bonding_curve(mint_pubkey)
            associated_bonding_curve = self.derive_associated_token_address(bonding_curve, mint_pubkey)
            user_token_account = self.derive_associated_token_address(self.wallet_address, mint_pubkey)
            
            # Instruction data
            buy_discriminator = bytes.fromhex("66063d1201daebea")
            max_sol_cost = int(sol_lamports * 1.06)
            instruction_data = buy_discriminator + struct.pack('<QQ', sol_lamports, max_sol_cost)
            
            # Minimal account set (based on successful transaction core accounts)
            account_metas = [
                AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),
                AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.wallet_address, is_signer=True, is_writable=True),
                AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.RENT_SYSVAR, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
            ]
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.PUMP_FUN_PROGRAM,
                accounts=account_metas,
                data=instruction_data
            )
            
            # Get recent blockhash
            recent_blockhash = await self.get_recent_blockhash()
            
            # Create transaction
            instructions = [
                set_compute_unit_price(self.PRIORITY_FEE),
                set_compute_unit_limit(400_000),
                buy_instruction
            ]
            
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],  # No lookup tables
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
            # Send transaction
            async with httpx.AsyncClient(timeout=30.0) as client:
                serialized = b58encode(bytes(transaction)).decode()
                
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            serialized,
                            {
                                "encoding": "base58",
                                "skipPreflight": False,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                
                result = response.json()
                
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ Simple MEV buy submitted: {signature}")
                    return signature
                else:
                    error = result.get('error', {})
                    logger.error(f"❌ Simple buy failed: {error}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Simple buy error: {e}")
            return None

async def test_simple_mev():
    """Test the simple MEV approach"""
    env = EnvKeys()
    bot = SimpleMEVBot(env)
    
    # Test parameters
    test_mint = "5rPVwsZ4KpPZ2Zt4FmYfMJuYe8PWRF2rXrBy2oG5pump"
    test_amount = 0.001  # Very small amount
    
    logger.info(f"🧪 Testing Simple MEV Bot")
    logger.info(f"   Mint: {test_mint}")
    logger.info(f"   Amount: {test_amount} SOL")
    
    signature = await bot.simple_buy(test_mint, test_amount)
    
    if signature:
        logger.info(f"🎉 SUCCESS! Simple MEV bot worked: {signature}")
        return True
    else:
        logger.error(f"❌ Simple MEV bot failed")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_simple_mev())
