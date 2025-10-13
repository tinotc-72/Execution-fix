#!/usr/bin/env python3
"""
Generic Solana Trading Bot
Complete autonomous trading system with buy, hold, and sell capabilities
Supports trading on any Solana program with configurable program IDs and instructions
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
import struct

from config import WALLET
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"

class TradeResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class TradeConfig:
    """Trading configuration parameters"""
    sol_amount: float = 0.005  # SOL amount to spend per trade
    slippage_tolerance: float = 0.10  # 10% slippage tolerance
    max_retries: int = 1  # Minimal retries
    retry_delay: float = 0.0  # No delay between retries
    confirmation_timeout: float = 10.0  # Quick timeout
    max_balance_checks: int = 1  # Single balance check
    initial_wait_time: float = 0.0  # No initial wait

@dataclass
class TradeExecutionResult:
    """Result of a trade execution"""
    action: TradeAction
    result: TradeResult
    signature: Optional[str]
    tokens_amount: int
    sol_amount: float
    timestamp: datetime
    error_message: Optional[str] = None

@dataclass
class ProgramConfig:
    """Configuration for a specific Solana program"""
    program_id: Pubkey
    buy_discriminator: bytes
    sell_discriminator: bytes
    required_accounts: Dict[str, Pubkey]

class SolanaTradingBot:
    """
    Generic Solana trading bot with configurable program support
    """
    
    def __init__(self, program_config: ProgramConfig, trade_config: TradeConfig = None):
        self.program_config = program_config
        self.config = trade_config or TradeConfig()
        self.wallet_keypair = WALLET
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        self.client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
        
        # System program constants
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        logger.info(f"🤖 Solana Trading Bot initialized")
        logger.info(f"📱 Wallet: {self.wallet_pubkey}")
        logger.info(f"💰 SOL per trade: {self.config.sol_amount}")
        logger.info(f"🔧 Program ID: {self.program_config.program_id}")

    async def get_sol_balance(self) -> float:
        """Get current SOL balance"""
        try:
            balance = await self.client.get_balance(self.wallet_pubkey)
            return balance.value / 1_000_000_000 if balance.value else 0.0
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get current token balance for a specific mint"""
        try:
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            balance_result = await self.client.get_token_account_balance(token_account)
            if balance_result.value:
                return int(balance_result.value.amount)
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
        """Ensure Associated Token Account exists, create if needed"""
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        try:
            # Check if ATA exists
            account_info = await self.client.get_account_info(ata)
            if account_info.value:
                return ata
        except:
            pass
        
        logger.info(f"🔨 Creating ATA for token: {token_mint}")
        
        # Create ATA instruction
        create_ata_ix = create_associated_token_account(
            payer=self.wallet_pubkey,
            owner=self.wallet_pubkey,
            mint=token_mint
        )
        
        try:
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([create_ata_ix], self.wallet_pubkey, recent_blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], recent_blockhash)
            
            result = await self.client.send_transaction(transaction)
            if result.value:
                logger.info(f"✅ ATA created: {ata}")
                await asyncio.sleep(3)  # Wait for confirmation
            return ata
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            return ata

    def _build_trade_accounts(self, token_mint: Pubkey, **kwargs) -> list[AccountMeta]:
        """Build the account list for trade instructions"""
        our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        # Basic accounts that are always needed
        accounts = [
            AccountMeta(token_mint, is_signer=False, is_writable=True),
            AccountMeta(our_token_account, is_signer=False, is_writable=True),
            AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
            AccountMeta(self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(self.program_config.program_id, is_signer=False, is_writable=False),
        ]
        
        # Add any program-specific required accounts
        for name, pubkey in self.program_config.required_accounts.items():
            is_signer = kwargs.get(f"{name}_is_signer", False)
            is_writable = kwargs.get(f"{name}_is_writable", True)
            accounts.append(AccountMeta(pubkey, is_signer=is_signer, is_writable=is_writable))
            
        return accounts

    async def execute_buy_trade(
        self, 
        token_mint: Pubkey,
        sol_amount: Optional[float] = None,
        **kwargs
    ) -> TradeExecutionResult:
        """Execute a buy trade using the configured program"""
        
        sol_amount = sol_amount or self.config.sol_amount
        logger.info(f"🛒 Executing BUY trade: {sol_amount} SOL for {token_mint}")
        
        start_time = datetime.now()
        
        try:
            # Verify all required accounts exist
            for name, pubkey in self.program_config.required_accounts.items():
                account_info = await self.client.get_account_info(pubkey)
                if not account_info.value:
                    raise Exception(f"Required account {name} ({pubkey}) not found")

            # Ensure token account exists
            await self.ensure_token_account_exists(token_mint)
            
            # Get initial balances
            initial_tokens = await self.get_token_balance(token_mint)
            
            # Build trade accounts
            accounts = self._build_trade_accounts(token_mint, **kwargs)
            
            # Create buy instruction data
            sol_amount_lamports = int(sol_amount * 1_000_000_000)
            max_sol_cost = int(sol_amount_lamports * (1 + self.config.slippage_tolerance))
            
            instruction_data = self.program_config.buy_discriminator + struct.pack("<QQ", sol_amount_lamports, max_sol_cost)
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.program_config.program_id,
                accounts=accounts,
                data=instruction_data
            )
            
            # Execute transaction with retries
            signature = None
            
            for attempt in range(self.config.max_retries):
                try:
                    # Get recent blockhash
                    recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                    
                    # Create and sign transaction
                    message = Message.new_with_blockhash([buy_instruction], self.wallet_pubkey, recent_blockhash)
                    transaction = Transaction.new_unsigned(message)
                    transaction.sign([self.wallet_keypair], recent_blockhash)
                    
                    # Send transaction
                    response = await self.client.send_transaction(
                        transaction,
                        opts=TxOpts(
                            skip_preflight=True,
                            preflight_commitment=Processed,
                            max_retries=3
                        )
                    )
        
                    if response.value:
                        signature = str(response.value)
                        logger.info(f"✅ Buy transaction sent: {signature}")
                        
                        if await self.confirm_transaction(signature, self.config.confirmation_timeout):
                            final_tokens = await self.get_token_balance(token_mint)
                            tokens_received = final_tokens - initial_tokens
                            
                            if tokens_received > 0:
                                logger.info(f"🎉 Buy SUCCESS: Received {tokens_received:,} tokens")
                                return TradeExecutionResult(
                                    action=TradeAction.BUY,
                                    result=TradeResult.SUCCESS,
                                    signature=signature,
                                    tokens_amount=tokens_received,
                                    sol_amount=sol_amount,
                                    timestamp=start_time
                                )
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        
                except Exception as e:
                    logger.error(f"❌ Buy attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            error_msg = "All retry attempts failed"
            if signature:
                error_msg += f" (last tx: {signature})"
                
            return TradeExecutionResult(
                action=TradeAction.BUY,
                result=TradeResult.FAILED,
                signature=signature,
                tokens_amount=0,
                sol_amount=sol_amount,
                timestamp=start_time,
                error_message=error_msg
            )
            
        except Exception as e:
            logger.error(f"❌ Buy trade error: {e}")
            return TradeExecutionResult(
                action=TradeAction.BUY,
                result=TradeResult.FAILED,
                signature=None,
                tokens_amount=0,
                sol_amount=sol_amount,
                timestamp=start_time,
                error_message=str(e)
            )

    async def execute_sell_trade(
        self, 
        token_mint: Pubkey,
        token_amount: int,
        min_sol_out: Optional[int] = None,
        **kwargs
    ) -> TradeExecutionResult:
        """Execute a sell trade using the configured program"""
        
        min_sol_out = min_sol_out or 0
        logger.info(f"💸 Executing SELL trade: {token_amount:,} tokens for {token_mint}")
        
        start_time = datetime.now()
        
        try:
            # Verify balances and accounts
            initial_sol = await self.get_sol_balance()
            initial_tokens = await self.get_token_balance(token_mint)
            
            if initial_tokens < token_amount:
                error_msg = f"Insufficient token balance: have {initial_tokens:,}, need {token_amount:,}"
                logger.error(f"❌ {error_msg}")
                return TradeExecutionResult(
                    action=TradeAction.SELL,
                    result=TradeResult.FAILED,
                    signature=None,
                    tokens_amount=0,
                    sol_amount=0.0,
                    timestamp=start_time,
                    error_message=error_msg
                )
            
            # Build trade accounts
            accounts = self._build_trade_accounts(token_mint, **kwargs)
            
            # Create sell instruction data
            instruction_data = self.program_config.sell_discriminator + struct.pack("<QQ", token_amount, min_sol_out)
            
            # Create instruction
            sell_instruction = Instruction(
                program_id=self.program_config.program_id,
                accounts=accounts,
                data=instruction_data
            )
            
            # Execute transaction with retries
            signature = None
            
            for attempt in range(self.config.max_retries):
                try:
                    # Get recent blockhash
                    recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                    
                    # Create and sign transaction
                    message = Message.new_with_blockhash([sell_instruction], self.wallet_pubkey, recent_blockhash)
                    transaction = Transaction.new_unsigned(message)
                    transaction.sign([self.wallet_keypair], recent_blockhash)
                    
                    # Send transaction
                    response = await self.client.send_transaction(
                        transaction,
                        opts=TxOpts(
                            skip_preflight=True,
                            preflight_commitment=Processed,
                            max_retries=3
                        )
                    )
        
                    if response.value:
                        signature = str(response.value)
                        logger.info(f"✅ Sell transaction sent: {signature}")
                        
                        if await self.confirm_transaction(signature, self.config.confirmation_timeout):
                            final_tokens = await self.get_token_balance(token_mint)
                            final_sol = await self.get_sol_balance()
                            
                            tokens_sold = initial_tokens - final_tokens
                            sol_received = final_sol - initial_sol
                            
                            if tokens_sold > 0:
                                logger.info(f"🎉 Sell SUCCESS: Sold {tokens_sold:,} tokens, received {sol_received:.6f} SOL")
                                return TradeExecutionResult(
                                    action=TradeAction.SELL,
                                    result=TradeResult.SUCCESS,
                                    signature=signature,
                                    tokens_amount=tokens_sold,
                                    sol_amount=sol_received,
                                    timestamp=start_time
                                )
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        
                except Exception as e:
                    logger.error(f"❌ Sell attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            error_msg = "All retry attempts failed"
            if signature:
                error_msg += f" (last tx: {signature})"
                
            return TradeExecutionResult(
                action=TradeAction.SELL,
                result=TradeResult.FAILED,
                signature=signature,
                tokens_amount=0,
                sol_amount=0.0,
                timestamp=start_time,
                error_message=error_msg
            )
            
        except Exception as e:
            logger.error(f"❌ Sell trade error: {e}")
            return TradeExecutionResult(
                action=TradeAction.SELL,
                result=TradeResult.FAILED,
                signature=None,
                tokens_amount=0,
                sol_amount=0.0,
                timestamp=start_time,
                error_message=str(e)
            )

    async def execute_complete_trade_cycle(
        self, 
        token_mint: Pubkey,
        hold_duration: float = 5.0,  # Default 5 second hold
        buy_amount: Optional[float] = None,
        **kwargs
    ) -> Dict[str, TradeExecutionResult]:
        """Execute a complete buy-hold-sell trading cycle"""
        
        logger.info(f"🚀 Starting complete trade cycle for {token_mint}")
        results = {}
        
        try:
            # Step 1: Buy
            buy_result = await self.execute_buy_trade(token_mint, buy_amount, **kwargs)
            results['buy'] = buy_result
            
            if buy_result.result != TradeResult.SUCCESS:
                logger.error("❌ Buy failed, aborting trade cycle")
                return results
            
            # Step 2: Hold
            logger.info(f"⏳ Holding for {hold_duration} seconds...")
            await asyncio.sleep(hold_duration)
            
            # Step 3: Sell
            sell_result = await self.execute_sell_trade(
                token_mint=token_mint,
                token_amount=buy_result.tokens_amount,
                **kwargs
            )
            results['sell'] = sell_result
            
            # Summary
            if buy_result.result == TradeResult.SUCCESS and sell_result.result == TradeResult.SUCCESS:
                net_sol = sell_result.sol_amount - buy_result.sol_amount
                logger.info(f"🎉 Complete cycle SUCCESS! Net SOL: {net_sol:+.6f}")
            else:
                logger.warning("⚠️ Incomplete cycle")
                
            return results
            
        except Exception as e:
            logger.error(f"❌ Trade cycle error: {e}")
            return results

    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with minimal delay"""
        try:
            sig = Signature(signature)
            resp = await self.client.confirm_transaction(
                sig,
                commitment="confirmed",
                sleep_seconds=0.1,
                last_valid_block_height=None,
                timeout=timeout
            )
            
            if resp.value.err:
                logging.error(f"Transaction failed: {resp.value.err}")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Error confirming transaction: {str(e)}")
            return False

    async def close(self):
        """Close the client connection"""
        await self.client.close()
