#!/usr/bin/env python3 - this is the bot meant to be buying and selling
"""
Generic Solana Trading Bot
Complete autonomous trading system with buy, hold, and sell capabilities
Supports trading on any Solana program with configurable program IDs and instructions
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
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
        logging.FileHandler('pump_trading_bot.log'),
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
        
        # System program constants (these are universal)
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        logger.info(f"🤖 Solana Trading Bot initialized")
        logger.info(f"📱 Wallet: {self.wallet_pubkey}")
        logger.info(f"💰 SOL per trade: {self.config.sol_amount}")
        logger.info(f"🔧 Program ID: {self.program_config.program_id}")
        logger.info(f"📱 Wallet: {self.wallet_pubkey}")
        logger.info(f"💰 SOL per trade: {self.config.sol_amount}")

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

    def _build_buy_accounts(self, token_mint: Pubkey, bonding_curve: Pubkey, bonding_curve_ata: Pubkey, creator_vault: Pubkey = None) -> list[AccountMeta]:
        """Build account list specifically for buy operations"""
        our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
        vault_to_use = creator_vault or self.CREATOR_VAULT
        
        return [
            AccountMeta(self.GLOBAL_ACCOUNT, is_signer=False, is_writable=True),  # Global state account (must be first)
            AccountMeta(self.FEE_RECIPIENT, is_signer=False, is_writable=True),  # Fee recipient
            AccountMeta(token_mint, is_signer=False, is_writable=True),  # Token mint
            AccountMeta(bonding_curve, is_signer=False, is_writable=True),  # Bonding curve account
            AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),  # Bonding curve token account
            AccountMeta(our_token_account, is_signer=False, is_writable=True),  # Our token account
            AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),  # User wallet (must be signer)
            AccountMeta(self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),  # System program
            AccountMeta(self.TOKEN_PROGRAM, is_signer=False, is_writable=False),  # Token program
            AccountMeta(vault_to_use, is_signer=False, is_writable=True),  # Creator vault
            AccountMeta(self.EVENT_AUTHORITY, is_signer=False, is_writable=False),  # Event authority
            AccountMeta(self.PUMP_PROGRAM, is_signer=False, is_writable=False),  # Program ID
        ]

    def _build_sell_accounts(self, token_mint: Pubkey, bonding_curve: Pubkey, bonding_curve_ata: Pubkey, creator_vault: Pubkey = None) -> list[AccountMeta]:
        """Build account list specifically for sell operations"""
        our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
        vault_to_use = creator_vault or self.CREATOR_VAULT
        
        return [
            AccountMeta(self.GLOBAL_ACCOUNT, is_signer=False, is_writable=True),  # Global state account
            AccountMeta(self.FEE_RECIPIENT, is_signer=False, is_writable=True),  # Fee recipient
            AccountMeta(token_mint, is_signer=False, is_writable=True),  # Token mint
            AccountMeta(bonding_curve, is_signer=False, is_writable=True),  # Bonding curve account
            AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),  # Bonding curve token account
            AccountMeta(our_token_account, is_signer=False, is_writable=True),  # Our token account
            AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),  # User wallet (must be signer)
            AccountMeta(self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),  # System program
            AccountMeta(vault_to_use, is_signer=False, is_writable=True),  # Creator vault
            AccountMeta(self.TOKEN_PROGRAM, is_signer=False, is_writable=False),  # Token program
            AccountMeta(self.EVENT_AUTHORITY, is_signer=False, is_writable=False),  # Event authority
            AccountMeta(self.PUMP_PROGRAM, is_signer=False, is_writable=False),  # Program ID
        ]

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
            initial_sol = await self.get_sol_balance()
            initial_tokens = await self.get_token_balance(token_mint)
            
            # Get optimal creator vault for this token
            creator_vault = await self.get_optimal_creator_vault(token_mint)
            logger.info(f"🔑 Using creator vault: {creator_vault} for token: {token_mint}")
            
            # Build trade accounts
            accounts = self._build_trade_accounts(token_mint, **kwargs)
            
            # Create buy instruction data
            sol_amount_lamports = int(sol_amount * 1_000_000_000)
            max_sol_cost = int(sol_amount_lamports * (1 + self.config.slippage_tolerance))
            
            instruction_data = self.program_config.buy_discriminator + struct.pack("<QQ", sol_amount_lamports, max_sol_cost)
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
            # Execute transaction with retries and exponential backoff
            base_delay = self.config.retry_delay
            signature = None
            
            for attempt in range(self.config.max_retries):
                try:
                    current_delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Buy attempt {attempt + 1}/{self.config.max_retries} (delay: {current_delay:.1f}s)")
                    
                    # Get recent blockhash with retries
                    for _ in range(3):
                        try:
                            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                            break
                        except Exception as e:
                            logger.warning(f"Error getting blockhash: {e}, retrying...")
                            await asyncio.sleep(1)
                    else:
                        raise Exception("Could not get recent blockhash after 3 attempts")
                    
                    # Create and sign transaction
                    message = Message.new_with_blockhash([buy_instruction], self.wallet_pubkey, recent_blockhash)
                    transaction = Transaction.new_unsigned(message)
                    transaction.sign([self.wallet_keypair], recent_blockhash)
                    
                    # Send the transaction with proper options
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
                        
                        # Wait for confirmation with timeout
                        if await self.confirm_transaction(signature, self.config):
                            # Single immediate balance check
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
                            
                            logger.warning(f"⚠️ Transaction confirmed but no tokens received yet")
                        else:
                            logger.error(f"❌ Transaction confirmation timeout")
                    
                    # Add delay before next attempt
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(current_delay)
                        
                except Exception as e:
                    logger.error(f"❌ Buy attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(current_delay)
                        continue
                    raise e
            
            # All retries failed
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
        """Execute a sell trade on pump.fun"""
        
        min_sol_out = min_sol_out or 0  # Accept any amount of SOL
        logger.info(f"💸 Executing SELL trade: {token_amount:,} tokens for {token_mint}")
        
        start_time = datetime.now()
        
        try:
            # Verify balances and accounts first
            initial_sol = await self.get_sol_balance()
            initial_tokens = await self.get_token_balance(token_mint)
            
            if initial_tokens < token_amount:
                logger.error(f"❌ Insufficient tokens: have {initial_tokens:,}, need {token_amount:,}")
                return TradeExecutionResult(
                    action=TradeAction.SELL,
                    result=TradeResult.FAILED,
                    signature=None,
                    tokens_amount=0,
                    sol_amount=0.0,
                    timestamp=start_time,
                    error_message=f"Insufficient token balance: have {initial_tokens:,}, need {token_amount:,}"
                )
            
            # Verify token account exists
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            account_info = await self.client.get_account_info(token_account)
            if not account_info.value:
                raise Exception(f"Token account {token_account} not found")
            
            # Get optimal creator vault for this token
            creator_vault = await self.get_optimal_creator_vault(token_mint)
            logger.info(f"🔑 Using creator vault: {creator_vault} for token: {token_mint}")
            
            # Build trade accounts
            accounts = self._build_trade_accounts(token_mint, **kwargs)
            
            # Create sell instruction data
            instruction_data = self.program_config.sell_discriminator + struct.pack("<QQ", token_amount, min_sol_out)
            
            # Create instruction
            sell_instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
            # Execute transaction with retries and exponential backoff
            base_delay = self.config.retry_delay
            signature = None
            
            for attempt in range(self.config.max_retries):
                try:
                    current_delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Sell attempt {attempt + 1}/{self.config.max_retries} (delay: {current_delay:.1f}s)")
                    
                    # Get recent blockhash with retries
                    for _ in range(3):
                        try:
                            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                            break
                        except Exception as e:
                            logger.warning(f"Error getting blockhash: {e}, retrying...")
                            await asyncio.sleep(1)
                    else:
                        raise Exception("Could not get recent blockhash after 3 attempts")
                    
                    # Create and sign transaction
                    message = Message.new_with_blockhash([sell_instruction], self.wallet_pubkey, recent_blockhash)
                    transaction = Transaction.new_unsigned(message)
                    transaction.sign([self.wallet_keypair], recent_blockhash)
                    
                    # Send the transaction with proper options
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
                        
                        # Wait for confirmation with timeout
                        if await self.confirm_transaction(signature, self.config):
                            # Single immediate balance check
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
                            
                            logger.warning(f"⚠️ Transaction confirmed but no tokens sold yet")
                        else:
                            logger.error(f"❌ Transaction confirmation timeout")
                    
                    # Add delay before next attempt
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(current_delay)
                        
                except Exception as e:
                    logger.error(f"❌ Sell attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(current_delay)
                        continue
                    raise e
            
            # All retries failed
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
        bonding_curve: Pubkey, 
        bonding_curve_ata: Pubkey,
        hold_duration: float = 10.0,
        buy_amount: Optional[float] = None
    ) -> Dict[str, TradeExecutionResult]:
        """Execute a complete buy-hold-sell trading cycle"""
        
        logger.info(f"🚀 Starting complete trade cycle for {token_mint}")
        
        results = {}
        
        try:
            # Step 1: Buy
            buy_result = await self.execute_buy_trade(token_mint, bonding_curve, bonding_curve_ata, buy_amount)
            results['buy'] = buy_result
            
            if buy_result.result != TradeResult.SUCCESS:
                logger.error("❌ Buy failed, aborting trade cycle")
                return results
            
            # Step 2: Hold
            logger.info(f"⏳ Holding for {hold_duration} seconds...")
            await asyncio.sleep(hold_duration)
            
            # Step 3: Sell
            sell_result = await self.execute_sell_trade(
                token_mint, 
                bonding_curve, 
                bonding_curve_ata, 
                buy_result.tokens_amount
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

    # Convenience methods for the working test token
    async def buy_test_token(self, sol_amount: Optional[float] = None) -> TradeExecutionResult:
        """Buy the working test token"""
        return await self.execute_buy_trade(
            self.WORKING_TOKEN_MINT,
            self.WORKING_BONDING_CURVE,
            self.WORKING_BONDING_CURVE_ATA,
            sol_amount
        )

    async def sell_test_token(self, token_amount: int) -> TradeExecutionResult:
        """Sell the working test token"""
        return await self.execute_sell_trade(
            self.WORKING_TOKEN_MINT,
            self.WORKING_BONDING_CURVE,
            self.WORKING_BONDING_CURVE_ATA,
            token_amount
        )

    async def test_token_cycle(self, hold_duration: float = 10.0) -> Dict[str, TradeExecutionResult]:
        """Execute complete cycle on the working test token"""
        return await self.execute_complete_trade_cycle(
            self.WORKING_TOKEN_MINT,
            self.WORKING_BONDING_CURVE,
            self.WORKING_BONDING_CURVE_ATA,
            hold_duration
        )

    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        sol_balance = await self.get_sol_balance()
        test_token_balance = await self.get_token_balance(self.WORKING_TOKEN_MINT)
        
        return {
            'sol_balance': sol_balance,
            'test_token_balance': test_token_balance,
            'test_token_mint': str(self.WORKING_TOKEN_MINT),
            'wallet': str(self.wallet_pubkey),
            'timestamp': datetime.now().isoformat()
        }

    async def close(self):
        """Close the client connection"""
        await self.client.close()

    def derive_creator_vault(self, token_mint: Pubkey) -> Pubkey:
        """
        Derive the creator vault for a specific token
        Each token has its own creator vault derived from the token mint
        """
        try:
            token_str = str(token_mint)
            
            # Check cache first for known router-based tokens
            if token_str == "766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump":
                return Pubkey.from_string("HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL")
            
            # Attempt dynamic derivation for router-based tokens
            # Creator vault is typically derived from: [creator_address, token_mint]
            try:
                # Try common patterns for creator vault derivation
                patterns = [
                    [b"creator", bytes(token_mint)],
                    [b"creator_vault", bytes(token_mint)],
                    [bytes(token_mint), b"creator"],
                    [bytes(token_mint), b"creator_vault"]
                ]
                
                for seeds in patterns:
                    try:
                        creator_vault, _ = Pubkey.find_program_address(seeds, self.PUMP_PROGRAM)
                        # Try to validate this by checking if it exists on-chain
                        # For now, we'll use the first derivation that doesn't throw an error
                        logger.debug(f"Derived creator vault candidate: {creator_vault} for token: {token_mint}")
                        return creator_vault
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.debug(f"Dynamic derivation failed for {token_mint}: {e}")
            
            # For standard pump.fun tokens, use the default creator vault
            return self.CREATOR_VAULT
            
        except Exception as e:
            logger.error(f"Error deriving creator vault for {token_mint}: {e}")
            return self.CREATOR_VAULT

    async def validate_creator_vault(self, creator_vault: Pubkey) -> bool:
        """
        Validate if a creator vault exists on-chain
        """
        try:
            response = await self.client.get_account_info(creator_vault)
            return response.value is not None
        except Exception as e:
            logger.debug(f"Error validating creator vault {creator_vault}: {e}")
            return False

    async def get_optimal_creator_vault(self, token_mint: Pubkey) -> Pubkey:
        """
        Get the optimal creator vault for a token by trying multiple derivation patterns
        and validating them on-chain
        """
        try:
            token_str = str(token_mint)
            
            # Known mappings for router-based tokens
            if token_str == "766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump":
                return Pubkey.from_string("HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL")
            
            # Try multiple derivation patterns
            patterns = [
                [b"creator", bytes(token_mint)],
                [b"creator_vault", bytes(token_mint)], 
                [bytes(token_mint), b"creator"],
                [bytes(token_mint), b"creator_vault"],
                [b"vault", bytes(token_mint)]
            ]
            
            for seeds in patterns:
                try:
                    creator_vault, _ = Pubkey.find_program_address(seeds, self.PUMP_PROGRAM)
                    
                    # Validate this derivation on-chain
                    if await self.validate_creator_vault(creator_vault):
                        logger.info(f"✅ Found valid creator vault: {creator_vault} for token: {token_mint}")
                        return creator_vault
                    else:
                        logger.debug(f"❌ Invalid creator vault: {creator_vault} for token: {token_mint}")
                        
                except Exception as e:
                    logger.debug(f"Pattern {seeds} failed: {e}")
                    continue
            
            # If no derived vault works, use the default
            logger.warning(f"⚠️ Using default creator vault for token: {token_mint}")
            return self.CREATOR_VAULT
            
        except Exception as e:
            logger.error(f"Error getting optimal creator vault for {token_mint}: {e}")
            return self.CREATOR_VAULT

    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with minimal delay"""
        try:
            # Convert string signature to Signature object
            sig = Signature(signature)
            
            # Wait for confirmation with timeout
            resp = await self.client.confirm_transaction(
                sig,
                commitment="confirmed",
                sleep_seconds=0.1,  # Quick polling
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

    async def buy_token(self, token_mint: str) -> bool:
        """Buy token with minimal delay"""
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            
            # Ensure token account exists
            token_account = await self._ensure_token_account(token_mint_pubkey)
            
            # Get initial balance for comparison
            initial_balance = await self._get_token_balance(token_account)
            
            # Build and send buy transaction
            tx = await self._build_buy_transaction(token_mint_pubkey, token_account)
            signature = await self._send_and_confirm_transaction(tx)
            if not signature:
                return False
                
            # Single quick balance check to verify success
            final_balance = await self._get_token_balance(token_account)
            success = final_balance > initial_balance
            
            if success:
                logging.info(f"Buy successful: {final_balance - initial_balance} tokens received")
            else:
                logging.error("Buy failed: No tokens received")
                
            return success
            
        except Exception as e:
            logging.error(f"Buy failed: {str(e)}")
            return False

    async def sell_token(self, token_mint: str) -> bool:
        """Sell token with minimal delay"""
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
            
            # Get initial balance
            initial_balance = await self._get_token_balance(token_account)
            if initial_balance == 0:
                logging.error("No tokens to sell")
                return False
            
            # Build and send sell transaction
            tx = await self._build_sell_transaction(token_mint_pubkey, token_account)
            signature = await self._send_and_confirm_transaction(tx)
            if not signature:
                return False
            
            # Single quick balance check to verify success
            final_balance = await self._get_token_balance(token_account)
            success = final_balance < initial_balance
            
            if success:
                logging.info(f"Sell successful: {initial_balance - final_balance} tokens sold")
            else:
                logging.error("Sell failed: Tokens not sold")
            
            return success
            
        except Exception as e:
            logging.error(f"Sell failed: {str(e)}")
            return False

    async def _send_and_confirm_transaction(self, transaction: Transaction) -> Optional[str]:
        """Send and confirm transaction with minimal delay"""
        try:
            # Send transaction
            opts = TxOpts(skip_preflight=True, max_retries=self.config.max_retries)
            signature = await self.client.send_transaction(transaction, opts=opts)
            
            # Wait for confirmation with timeout
            start_time = time.time()
            while time.time() - start_time < self.config.confirmation_timeout:
                resp = await self.client.get_signature_statuses([signature.value])
                if resp.value[0] is not None:
                    if resp.value[0].err:
                        logging.error(f"Transaction failed: {resp.value[0].err}")
                        return None
                    return signature.value
                await asyncio.sleep(0.1)  # Minimal sleep between checks
                
            logging.error("Transaction confirmation timeout")
            return None
            
        except Exception as e:
            logging.error(f"Transaction error: {str(e)}")
            return None

    async def _get_token_balance(self, token_account: Pubkey) -> int:
        """Get token balance with no retries"""
        try:
            resp = await self.client.get_token_account_balance(token_account)
            return int(resp.value.amount)
        except Exception as e:
            logging.error(f"Balance check failed: {str(e)}")
            return 0

    async def execute_trade(self, token_mint: str) -> bool:
        """Execute a full trade cycle: buy, hold for exactly 5 seconds, sell"""
        try:
            buy_start = time.time()
            logging.info(f"Starting trade cycle for token {token_mint}")
            
            # Execute buy with no delays
            if not await self.buy_token(token_mint):
                logging.error("Buy failed")
                return False
                
            buy_duration = time.time() - buy_start
            logging.info(f"Buy completed in {buy_duration:.2f} seconds")
            
            # Hold for exactly 5 seconds (required holding period)
            hold_time = max(5.0 - (time.time() - buy_start), 0.0)
            logging.info(f"Holding position for {hold_time:.2f} seconds...")
            await asyncio.sleep(hold_time)
            
            sell_start = time.time()
            # Execute sell immediately after hold period
            if not await self.sell_token(token_mint):
                logging.error("Sell failed")
                return False
                
            sell_duration = time.time() - sell_start
            total_duration = time.time() - buy_start
            
            logging.info(f"Sell completed in {sell_duration:.2f} seconds")
            logging.info(f"Total trade cycle completed in {total_duration:.2f} seconds")
            return True
            
        except Exception as e:
            logging.error(f"Trade execution error: {str(e)}")
            return False

    async def fast_copy_trade(self, token_mint: str) -> bool:
        """Execute fast copy trade: buy → 5s hold → sell"""
        try:
            # Convert mint string to pubkey
            token_mint_pubkey = Pubkey.from_string(token_mint)
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
            
            # Buy
            buy_start = time.time()
            logger.info("Executing buy...")
            
            # Build and send buy tx
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            buy_accounts = self._build_buy_accounts(token_mint_pubkey, self.WORKING_BONDING_CURVE, self.WORKING_BONDING_CURVE_ATA)
            
            # Create buy instruction
            sol_amount_lamports = int(0.005 * 1_000_000_000)  # 0.005 SOL
            max_cost = int(sol_amount_lamports * 1.1)  # 10% slippage
            buy_data = self.BUY_DISCRIMINATOR + struct.pack("<QQ", sol_amount_lamports, max_cost)
            
            buy_ix = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=buy_accounts,
                data=buy_data
            )
            
            message = Message.new_with_blockhash([buy_ix], self.wallet_pubkey, blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], blockhash)
            
            # Send with minimal options
            buy_sig = await self.client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=True, max_retries=1)
            )
            
            if not buy_sig.value:
                logger.error("Buy failed")
                return False
                
            logger.info(f"Buy sent in {time.time() - buy_start:.2f}s")
            
            # Hold exactly 5 seconds
            logger.info("Holding 5 seconds...")
            await asyncio.sleep(5.0)
            
            # Sell
            sell_start = time.time()
            logger.info("Executing sell...")
            
            # Build and send sell tx
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            sell_accounts = self._build_sell_accounts(token_mint_pubkey, self.WORKING_BONDING_CURVE, self.WORKING_BONDING_CURVE_ATA)
            
            # Get balance to sell
            balance = await self._get_token_balance(token_account)
            if balance == 0:
                logger.error("No tokens to sell")
                return False
                
            # Create sell instruction
            sell_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", balance, 0)  # Sell all, accept any amount
            
            sell_ix = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=sell_accounts,
                data=sell_data
            )
            
            message = Message.new_with_blockhash([sell_ix], self.wallet_pubkey, blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], blockhash)
            
            # Send with minimal options
            sell_sig = await self.client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=True, max_retries=1)
            )
            
            if not sell_sig.value:
                logger.error("Sell failed")
                return False
                
            logger.info(f"Sell sent in {time.time() - sell_start:.2f}s")
            logger.info(f"Complete cycle in {time.time() - buy_start:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Trade error: {str(e)}")
            return False

# Example usage and testing functions
async def demo_trading_bot():
    """Demo the generic trading bot with a specific program"""
    # Example program configuration (this would be different for each program)
    program_config = ProgramConfig(
        program_id=Pubkey.from_string("YOUR_PROGRAM_ID"),  # Replace with actual program ID
        buy_discriminator=bytes.fromhex("YOUR_BUY_DISCRIMINATOR"),  # Replace with actual discriminator
        sell_discriminator=bytes.fromhex("YOUR_SELL_DISCRIMINATOR"),  # Replace with actual discriminator
        required_accounts={
            # Add any program-specific accounts needed
            "pool": Pubkey.from_string("POOL_ADDRESS"),  # Example
            "vault": Pubkey.from_string("VAULT_ADDRESS"),  # Example
        }
    )
    
    # Trading configuration
    trade_config = TradeConfig(
        sol_amount=0.005,  # 0.005 SOL per trade
        slippage_tolerance=0.10,  # 10% slippage tolerance
        max_retries=1,
        confirmation_timeout=10.0
    )
    
    # Initialize bot
    bot = SolanaTradingBot(program_config, trade_config)
    
    try:
        # Example token to trade
        token_mint = Pubkey.from_string("YOUR_TOKEN_MINT")  # Replace with actual token mint
        
        # Execute buy trade
        buy_result = await bot.execute_buy_trade(token_mint)
        
        if buy_result.result == TradeResult.SUCCESS:
            logger.info(f"Buy successful, holding for 5 seconds...")
            await asyncio.sleep(5)  # 5 second hold
            
            # Execute sell trade
            sell_result = await bot.execute_sell_trade(
                token_mint=token_mint,
                token_amount=buy_result.tokens_amount
            )
            
            if sell_result.result == TradeResult.SUCCESS:
                net_sol = sell_result.sol_amount - buy_result.sol_amount
                logger.info(f"Complete cycle finished! Net SOL: {net_sol:+.6f}")
            else:
                logger.error(f"Sell failed: {sell_result.error_message}")
        else:
            logger.error(f"Buy failed: {buy_result.error_message}")
            
    finally:
        await bot.close()
    """Demonstrate the trading bot functionality"""
    
    print("🤖 PUMP.FUN TRADING BOT DEMONSTRATION")
    print("="*80)
    
    # Initialize bot with minimal settings
    config = TradeConfig(
        sol_amount=0.002,  # Amount to trade
        slippage_tolerance=0.10,  # 10% slippage
        max_retries=1,  # No retries
        retry_delay=0.0,  # No delay
        confirmation_timeout=30.0,  # Need enough time to confirm
        initial_wait_time=0.0,  # No initial wait
        max_balance_checks=1  # Single balance check
    )
    bot = PumpFunTradingBot(config)
    
    try:
        # Show initial portfolio
        portfolio = await bot.get_portfolio_summary()
        print(f"\n📊 Initial Portfolio:")
        print(f"💰 SOL Balance: {portfolio['sol_balance']:.6f}")
        print(f"🪙 Test Token Balance: {portfolio['test_token_balance']:,}")
        
        # Execute a complete trading cycle with longer hold time
        print(f"\n🚀 Executing complete trading cycle...")
        results = await bot.test_token_cycle(hold_duration=5.0)  # Reduced hold time
        
        # Show results
        print(f"\n📋 Trading Results:")
        for action, result in results.items():
            print(f"{action.upper()}: {result.result.value}")
            if result.signature:
                print(f"  TX: https://solscan.io/tx/{result.signature}")
                try:
                    # Convert string signature to Signature object
                    sig = Signature.from_string(result.signature)
                    
                    # Get transaction details using getTransaction
                    tx_info = await bot.client.get_transaction(sig)
                    
                    # Extract transaction metadata if available
                    if tx_info.value and hasattr(tx_info.value, 'meta'):
                        meta = tx_info.value.meta
                        if meta and hasattr(meta, 'err') and meta.err:
                            print(f"  Error: {meta.err}")
                            logger.error(f"Transaction error details: {meta}")
                except ValueError as ve:
                    print(f"  Invalid signature format: {ve}")
                except Exception as e:
                    print(f"  Could not fetch transaction details: {str(e)}")
                    logger.error(f"Transaction lookup error: {str(e)}")
        
        # Show final portfolio
        final_portfolio = await bot.get_portfolio_summary()
        print(f"\n📊 Final Portfolio:")
        print(f"💰 SOL Balance: {final_portfolio['sol_balance']:.6f}")
        print(f"🪙 Test Token Balance: {final_portfolio['test_token_balance']:,}")
        
        # Calculate net change
        sol_change = final_portfolio['sol_balance'] - portfolio['sol_balance']
        token_change = final_portfolio['test_token_balance'] - portfolio['test_token_balance']
        print(f"\n📈 Net Changes:")
        print(f"💰 SOL: {sol_change:+.6f}")
        print(f"🪙 Tokens: {token_change:+,}")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        
    finally:
        await bot.close()

async def demo(mint_address: str):
    """Demo function to test buy and sell with 5-second hold"""
    try:
        # Initialize bot with minimal config
        config = TradeConfig(
            max_retries=1,
            retry_delay=0.0,
            confirmation_timeout=30.0,
            max_balance_checks=1,
            initial_wait_time=0.0
        )
        
        bot = PumpFunTradingBot()
        
        # Execute buy
        logging.info("Executing buy transaction...")
        buy_sig = await bot.buy_token(mint_address, config)
        if not buy_sig:
            logging.error("Buy transaction failed")
            return
            
        logging.info("Buy successful, holding for 5 seconds...")
        await asyncio.sleep(5.0)  # Exactly 5-second hold
        
        # Execute sell
        logging.info("Executing sell transaction...")
        sell_sig = await bot.sell_token(mint_address, config)
        if not sell_sig:
            logging.error("Sell transaction failed")
            return
            
        logging.info("Trade cycle completed successfully")
        
    except Exception as e:
        logging.error(f"Error in demo: {str(e)}")
    finally:
        await bot.close()

async def test_optimized_trading():
    """Test the optimized trading cycle"""
    config = TradeConfig(
        sol_amount=0.005,
        slippage_tolerance=0.10,
        max_retries=1,
        retry_delay=0.0,
        confirmation_timeout=10.0,
        max_balance_checks=1,
        initial_wait_time=0.0
    )
    
    bot = PumpFunTradingBot(config)
    token_mint = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"  # Test token
    
    logging.info("Starting optimized trading test")
    start_time = time.time()
    
    success = await bot.execute_trade(token_mint)
    
    duration = time.time() - start_time
    if success:
        logging.info(f"Test completed successfully in {duration:.2f} seconds")
    else:
        logging.error(f"Test failed after {duration:.2f} seconds")
    
    await bot.client.close()

    async def _build_buy_transaction(self, token_mint: Pubkey, token_account: Pubkey) -> Transaction:
        """Build a buy transaction with minimal checks"""
        try:
            # Get minimal transaction data
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            bonding_curve = self.WORKING_BONDING_CURVE
            bonding_curve_ata = self.WORKING_BONDING_CURVE_ATA
            
            # Build accounts list
            accounts = self._build_buy_accounts(token_mint, bonding_curve, bonding_curve_ata)
            
            # Create buy instruction data
            sol_amount_lamports = int(self.config.sol_amount * 1_000_000_000)
            max_sol_cost = int(sol_amount_lamports * (1 + self.config.slippage_tolerance))
            instruction_data = self.BUY_DISCRIMINATOR + struct.pack("<QQ", sol_amount_lamports, max_sol_cost)
            
            # Create and sign transaction
            instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            message = Message.new_with_blockhash([instruction], self.wallet_pubkey, blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], blockhash)
            
            return transaction
            
        except Exception as e:
            logging.error(f"Error building buy transaction: {str(e)}")
            raise

    async def _build_sell_transaction(self, token_mint: Pubkey, token_account: Pubkey) -> Transaction:
        """Build a sell transaction with minimal checks"""
        try:
            # Get minimal transaction data
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            bonding_curve = self.WORKING_BONDING_CURVE
            bonding_curve_ata = self.WORKING_BONDING_CURVE_ATA
            
            # Get current token balance
            token_amount = await self._get_token_balance(token_account)
            if token_amount == 0:
                raise Exception("No tokens to sell")
            
            # Build accounts list
            accounts = self._build_sell_accounts(token_mint, bonding_curve, bonding_curve_ata)
            
            # Create sell instruction data (min_sol_out=0 accepts any amount)
            instruction_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", token_amount, 0)
            
            # Create and sign transaction
            instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            message = Message.new_with_blockhash([instruction], self.wallet_pubkey, blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], blockhash)
            
            return transaction
            
        except Exception as e:
            logging.error(f"Error building sell transaction: {str(e)}")
            raise

    async def _ensure_token_account(self, token_mint: Pubkey) -> Pubkey:
        """Ensure token account exists, create if needed"""
        token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        try:
            # Quick check if account exists
            await self.client.get_account_info(token_account)
            return token_account
        except:
            # Create if not exists
            ix = create_associated_token_account(
                payer=self.wallet_pubkey,
                owner=self.wallet_pubkey,
                mint=token_mint
            )
            
            # Build and send transaction
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([ix], self.wallet_pubkey, blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], blockhash)
            
            await self.client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=True, max_retries=1)
            )
            
            return token_account

if __name__ == "__main__":
    # Test token mint
    TEST_TOKEN = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
    
    async def test():
        bot = PumpFunTradingBot()
        await bot.fast_copy_trade(TEST_TOKEN)
        await bot.close()
        
    asyncio.run(test())
