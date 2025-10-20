"""
Complete MEV Bot - Production Ready Implementation
Provides CompleteMEVBot and CompleteMEVConfig classes for direct copy execution
"""

import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction  
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.hash import Hash
import httpx
from base58 import b58encode
import struct

from env_keys import EnvKeys
from utils.fees import with_compute_budget

logger = logging.getLogger(__name__)

@dataclass
class CompleteMEVConfig:
    """Configuration for Complete MEV Bot"""
    priority_fee: int = 500_000
    compute_limit: int = 400_000
    max_slippage: float = 0.06
    timeout: float = 30.0
    verify_transactions: bool = True

class CompleteMEVBot:
    """
    Complete MEV Bot - Production ready implementation with full account structure
    """
    
    def __init__(self, env_keys: EnvKeys, config: Optional[CompleteMEVConfig] = None):
        self.env = env_keys
        self.config = config or CompleteMEVConfig()
        self.keypair = Keypair.from_base58_string(env_keys.PHANTOM_PRIVATE_KEY)
        self.wallet_address = self.keypair.pubkey()
        
        # Core programs
        self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Protocol constants
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5XLdTukHvfFhA7s8BPg2SB9JMLvjDFYUkLKJGQhU")
        
    async def get_recent_blockhash(self) -> Hash:
        """Get recent blockhash"""
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
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
    
    async def execute_buy(self, mint_address: str, sol_amount: float) -> Optional[str]:
        """
        Execute buy transaction with complete account structure
        """
        try:
            logger.info(f"🎯 CompleteMEVBot buy: {sol_amount} SOL for {mint_address}")
            
            mint_pubkey = Pubkey.from_string(mint_address)
            sol_lamports = int(sol_amount * 1_000_000_000)
            
            # Derive required accounts
            bonding_curve = self.derive_bonding_curve(mint_pubkey)
            associated_bonding_curve = self.derive_associated_token_address(bonding_curve, mint_pubkey)
            user_token_account = self.derive_associated_token_address(self.wallet_address, mint_pubkey)
            
            # Buy instruction data
            buy_discriminator = bytes.fromhex("66063d1201daebea")
            max_sol_cost = int(sol_lamports * (1 + self.config.max_slippage))
            instruction_data = buy_discriminator + struct.pack('<QQ', sol_lamports, max_sol_cost)
            
            # Complete working account structure - 13 accounts
            account_metas = [
                AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),           # 0: Global
                AccountMeta(pubkey=self.FEE_RECIPIENT, is_signer=False, is_writable=False),            # 1: Fee config
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),                  # 2: Mint
                AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),                 # 3: Bonding curve
                AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),      # 4: Associated bonding curve
                AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),            # 5: User token account
                AccountMeta(pubkey=self.wallet_address, is_signer=True, is_writable=True),            # 6: User (signer)
                AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),          # 7: System program
                AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),           # 8: Token program
                AccountMeta(pubkey=self.RENT_SYSVAR, is_signer=False, is_writable=False),             # 9: Rent sysvar
                AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),         # 10: Event authority
                AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),        # 11: Pump.fun program
                AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False), # 12: ATA program
            ]
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.PUMP_FUN_PROGRAM,
                accounts=account_metas,
                data=instruction_data
            )
            
            # Get blockhash
            recent_blockhash = await self.get_recent_blockhash()
            
            # Create transaction with compute budget
            instructions = with_compute_budget(
                [buy_instruction],
                compute_unit_limit=self.config.compute_limit,
                compute_unit_price=self.config.priority_fee
            )
            
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
            # Submit transaction using unified helper
            from executors.submit import send_and_confirm_v0_tx
            
            result = await send_and_confirm_v0_tx(transaction, self.env.HELIUS_RPC_URL)
            
            if result["success"]:
                signature = result["signature"]
                status = result["status"].get("confirmationStatus", "unknown")
                # Use standardized logging helper
                from utils.logs import log_submit_result
                from executors.submit import SubmitResult
                submit_res = SubmitResult(
                    ok=True,
                    signature=signature,
                    status=status,
                    confirmationStatus=status
                )
                log_submit_result("mev", "buy", str(token_mint), submit_res)
                logger.info(f"✅ CompleteMEVBot buy success: {signature}")
                
                # Verify transaction if enabled
                if self.config.verify_transactions:
                    await asyncio.sleep(5)
                    success = await self.verify_transaction(signature)
                    if success:
                        logger.info(f"✅ Transaction {signature} verified on-chain")
                
                return signature
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ CompleteMEVBot buy failed: {error_msg}")
                # Log failed submission
                from utils.logs import log_submit_result
                from executors.submit import SubmitResult
                submit_res = SubmitResult(
                    ok=False,
                    signature=result.get("signature"),
                    status="failed",
                    error=error_msg
                )
                log_submit_result("mev", "buy", str(token_mint), submit_res)
                return None
                    
        except Exception as e:
            logger.error(f"❌ CompleteMEVBot buy error: {e}")
            return None
    
    async def verify_transaction(self, signature: str) -> bool:
        """Verify transaction success"""
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {
                                "encoding": "json",
                                "commitment": "confirmed",
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    }
                )
                
                data = response.json()
                if 'result' in data and data['result']:
                    tx = data['result']
                    error = tx.get('meta', {}).get('err')
                    
                    if error is None:
                        return True
                    else:
                        logger.error(f"❌ Transaction failed on-chain: {error}")
                        return False
                else:
                    logger.warning(f"⏳ Transaction still pending")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return False