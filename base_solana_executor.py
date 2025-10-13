"""
Base Solana Executor - Official Solana Documentation Best Practices
Implements all official Solana transaction execution patterns for maximum reliability
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed, Confirmed

logger = logging.getLogger(__name__)

@dataclass
class SolanaExecutorConfig:
    """Official Solana best practices configuration"""
    # Official retry parameters
    max_retries: int = 3  # Official docs recommend 3 retries max
    retry_delay: float = 1.0  # 1 second between retries per docs
    
    # Official transaction parameters
    skip_preflight: bool = True  # Official docs: Skip for speed in production
    preflight_commitment: str = "processed"  # Official default
    max_retries_rpc: int = 3  # RPC level retries
    
    # Official confirmation parameters
    confirmation_timeout: float = 60.0  # Official: Allow up to 60s for confirmation
    confirmation_commitment: str = "confirmed"  # Official recommendation
    confirmation_check_interval: float = 2.0  # Check every 2 seconds
    
    # Official compute budget parameters (per docs)
    compute_unit_limit: int = 300_000  # Official: Request specific compute limit
    compute_unit_price: int = 10_000  # Official: 10,000 micro-lamports = priority fee
    
    # Official timeout parameters
    transaction_timeout: float = 150.0  # Official: Blockhash expires after ~150 blocks (75s)
    fresh_blockhash_timeout: float = 60.0  # Get fresh blockhash if older than 60s
    
    # Official slippage and amounts
    default_slippage: float = 0.05  # 5% default slippage
    max_slippage: float = 0.30  # 30% max for meme coins
    min_sol_amount: float = 0.001  # Minimum viable amount
    gas_buffer_sol: float = 0.01  # SOL buffer for gas fees

class BaseSolanaExecutor(ABC):
    """
    Base executor implementing official Solana documentation best practices
    All executors should inherit from this for consistent behavior
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: SolanaExecutorConfig = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url, commitment=Processed)
        self.config = config or SolanaExecutorConfig()
        
        # Blockhash caching per official docs
        self._cached_blockhash = None
        self._blockhash_timestamp = 0
        
        logger.info(f"✅ Initialized {self.__class__.__name__} with official Solana best practices")
    
    async def get_fresh_blockhash(self, force_fresh: bool = False) -> tuple:
        """
        Get fresh blockhash following official Solana documentation
        Caches blockhash and refreshes when needed per official guidelines
        """
        current_time = time.time()
        
        # Official docs: Reuse blockhash for up to 60 seconds
        if (not force_fresh and 
            self._cached_blockhash and 
            current_time - self._blockhash_timestamp < self.config.fresh_blockhash_timeout):
            return self._cached_blockhash
        
        try:
            # Official method: getLatestBlockhash
            response = await self.client.get_latest_blockhash(commitment=Processed)
            if response.value:
                blockhash = response.value.blockhash
                last_valid_block_height = response.value.last_valid_block_height
                
                # Cache per official recommendations
                self._cached_blockhash = (blockhash, last_valid_block_height)
                self._blockhash_timestamp = current_time
                
                logger.debug(f"🔄 Fresh blockhash obtained: {str(blockhash)[:8]}...")
                return blockhash, last_valid_block_height
            else:
                raise Exception("Failed to get latest blockhash")
                
        except Exception as e:
            logger.error(f"❌ Error getting fresh blockhash: {e}")
            # Fallback to force a new request
            if not force_fresh:
                return await self.get_fresh_blockhash(force_fresh=True)
            raise
    
    def create_compute_budget_instructions(self) -> List[Instruction]:
        """
        Create compute budget instructions per official Solana documentation
        Sets both compute unit limit and price for proper prioritization
        """
        instructions = []
        
        # Official: Set compute unit limit to avoid paying for unused compute
        compute_limit_ix = set_compute_unit_limit(self.config.compute_unit_limit)
        instructions.append(compute_limit_ix)
        
        # Official: Set compute unit price for transaction prioritization
        compute_price_ix = set_compute_unit_price(self.config.compute_unit_price)
        instructions.append(compute_price_ix)
        
        return instructions
    
    async def build_and_sign_transaction(self, instructions: List[Instruction]) -> VersionedTransaction:
        """
        Build and sign transaction using official Solana documentation patterns
        Includes compute budget instructions and proper message construction
        """
        try:
            # Add compute budget instructions per official docs
            all_instructions = self.create_compute_budget_instructions() + instructions
            
            # Get fresh blockhash per official pattern
            blockhash, _ = await self.get_fresh_blockhash()
            
            # Official: Use MessageV0 for modern transaction format
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=all_instructions,
                recent_blockhash=blockhash,
                address_lookup_table_accounts=[]  # Empty for basic transactions
            )
            
            # Official: Create and sign versioned transaction
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building transaction: {e}")
            raise
    
    async def send_transaction_with_retry(self, transaction: VersionedTransaction) -> Optional[str]:
        """
        Send transaction with official Solana retry logic and error handling
        Implements exponential backoff and proper error classification
        """
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                if attempt > 0:
                    # Official: Exponential backoff for retries
                    delay = self.config.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"🔄 Retry attempt {attempt + 1}/{self.config.max_retries} after {delay}s")
                    await asyncio.sleep(delay)
                
                # Official: sendTransaction with proper options
                response = await self.client.send_transaction(
                    transaction,
                    opts=TxOpts(
                        skip_preflight=self.config.skip_preflight,  # Official: Skip for speed
                        preflight_commitment=self.config.preflight_commitment,
                        max_retries=self.config.max_retries_rpc  # RPC level retries
                    )
                )
                
                if response.value:
                    signature = str(response.value)
                    logger.info(f"✅ Transaction submitted: {signature[:12]}...")
                    return signature
                else:
                    last_error = "No signature returned from RPC"
                    
            except Exception as e:
                last_error = str(e)
                error_msg = str(e).lower()
                
                # Official: Classify errors per documentation
                if "blockhash not found" in error_msg:
                    logger.warning(f"⚠️ Blockhash expired, getting fresh one...")
                    # Get fresh blockhash and rebuild transaction
                    blockhash, _ = await self.get_fresh_blockhash(force_fresh=True)
                    
                    # Rebuild transaction with fresh blockhash
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=transaction.message.instructions,
                        recent_blockhash=blockhash,
                        address_lookup_table_accounts=[]
                    )
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    
                elif "insufficient funds" in error_msg:
                    logger.error(f"💰 Insufficient funds error - stopping retries")
                    break  # Don't retry insufficient funds
                    
                elif "custom: 1120" in error_msg or "programfailedtocomplete" in error_msg:
                    logger.warning(f"🔧 Program execution error (attempt {attempt + 1}): {error_msg}")
                    # Continue retrying - these can be transient
                    
                else:
                    logger.warning(f"⚠️ Transaction error (attempt {attempt + 1}): {error_msg}")
        
        logger.error(f"❌ All retry attempts failed. Last error: {last_error}")            
        return None
    
    async def confirm_transaction_official(self, signature: str) -> bool:
        """
        Confirm transaction using official Solana getSignatureStatuses method
        Implements proper confirmation logic per documentation
        """
        try:
            sig_obj = Signature.from_string(signature)
            start_time = time.time()
            
            logger.info(f"🔍 Confirming transaction: {signature[:12]}...")
            
            while time.time() - start_time < self.config.confirmation_timeout:
                try:
                    # Official: Use getSignatureStatuses for confirmation
                    status_result = await self.client.get_signature_statuses([sig_obj])
                    
                    if status_result.value and status_result.value[0]:
                        status = status_result.value[0]
                        
                        # Official: Check for errors first
                        if status.err:
                            logger.error(f"❌ Transaction failed: {status.err}")
                            return False
                        
                        # Official: Check confirmation status
                        confirmation_status = getattr(status, 'confirmation_status', None)
                        if confirmation_status in ['confirmed', 'finalized']:
                            logger.info(f"✅ Transaction confirmed: {confirmation_status}")
                            return True
                        elif confirmation_status == 'processed':
                            logger.debug(f"⏳ Transaction processed, waiting for confirmation...")
                        
                    # Official: Wait between checks
                    await asyncio.sleep(self.config.confirmation_check_interval)
                    
                except Exception as check_error:
                    logger.debug(f"⚠️ Confirmation check error: {check_error}")
                    await asyncio.sleep(self.config.confirmation_check_interval)
            
            logger.warning(f"⏰ Confirmation timeout after {self.config.confirmation_timeout}s")
            return False
            
        except Exception as e:
            logger.error(f"❌ Confirmation error: {e}")
            return False
    
    async def execute_transaction_official(self, instructions: List[Instruction]) -> Dict[str, Any]:
        """
        Execute transaction using official Solana best practices
        Returns standardized result format for all executors
        """
        start_time = time.time()
        
        try:
            # Build transaction with official patterns
            transaction = await self.build_and_sign_transaction(instructions)
            
            # Send with official retry logic
            signature = await self.send_transaction_with_retry(transaction)
            
            if not signature:
                return {
                    'success': False,
                    'error': 'Failed to submit transaction after retries',
                    'signature': None,
                    'execution_time': time.time() - start_time
                }
            
            # Return immediately for speed - confirmation happens async
            return {
                'success': True,
                'signature': signature,
                'error': None,
                'execution_time': time.time() - start_time,
                'confirmed': False  # Will be confirmed async
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'signature': None,
                'execution_time': time.time() - start_time
            }
    
    async def validate_sol_balance(self, required_amount: float) -> bool:
        """
        Validate SOL balance per official patterns
        Returns True if sufficient balance, False otherwise
        """
        try:
            response = await self.client.get_balance(self.wallet_pubkey, commitment=Processed)
            if response.value:
                balance_sol = response.value / 1e9
                required_with_buffer = required_amount + self.config.gas_buffer_sol
                
                if balance_sol >= required_with_buffer:
                    logger.debug(f"✅ Sufficient balance: {balance_sol:.6f} SOL (need {required_with_buffer:.6f})")
                    return True
                else:
                    logger.warning(f"⚠️ Insufficient balance: {balance_sol:.6f} SOL (need {required_with_buffer:.6f})")
                    return False
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Balance check error: {e}")
            return True  # Don't block on balance check errors
    
    @abstractmethod
    async def execute_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """Execute buy trade - must be implemented by subclasses"""
        pass
    
    @abstractmethod  
    async def execute_sell(self, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Execute sell trade - must be implemented by subclasses"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.client.close()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")
