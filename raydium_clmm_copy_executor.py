"""
Raydium CLMM Copy Executor - Execute CLMM trades from extracted transaction data
Takes trade information from detected CLMM transactions and executes the same trade with your wallet
Uses real CLMM program ID and pool structure for concentrated liquidity trading
"""

import asyncio
import struct
import logging
import json
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
import aiohttp
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Raydium CLMM program and constants
CLMM_PROGRAM = Pubkey.from_string("CLMMmSrhDDP8DR4egBy7AxFLt1DRpMkC5BRGzbswKxCU")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# CLMM instruction discriminators  
SWAP_V2_DISCRIMINATOR = bytes.fromhex("09d277cf4b8b30e4")  # Official SwapV2 8-byte discriminator for CLMM

@dataclass
class CopyExecutorConfig:
    """Configuration for CLMM copy trade execution"""
    slippage_tolerance: float = 0.05  # 5% slippage tolerance
    max_retries: int = 2
    retry_delay: float = 0.5
    confirmation_timeout: float = 30.0
    compute_unit_limit: int = 300_000  # Higher for CLMM complexity
    compute_unit_price: int = 2

@dataclass
class ExtractedCLMMTradeInfo:
    """Information extracted from a detected CLMM transaction"""
    token_mint: str
    is_buy: bool  # True if SOL->Token, False if Token->SOL
    amount_in: int
    pool_info: Dict[str, str]  # CLMM pool accounts
    original_signature: str
    wallet_address: str
    tick_spacing: int
    sqrt_price_limit: Optional[int] = None

@dataclass
class CLMMPoolInfo:
    """Complete CLMM pool information"""
    pool_id: Pubkey
    amm_config: Pubkey
    token_mint_0: Pubkey
    token_mint_1: Pubkey
    token_vault_0: Pubkey
    token_vault_1: Pubkey
    observation_state: Pubkey
    tick_array_lower: Pubkey
    tick_array_upper: Pubkey
    tick_spacing: int
    current_tick: int
    sqrt_price_x64: int

class RaydiumCLMMCopyExecutor:
    """
    Raydium CLMM copy executor for executing the same trade as detected transactions
    Takes extracted CLMM trade information and builds/executes with your wallet
    Handles concentrated liquidity mechanics including tick arrays and position management
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CopyExecutorConfig = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = None  # Placeholder for compatibility; use aiohttp for requests
        self.config = config or CopyExecutorConfig()
        # Cache for pool addresses and tick arrays
        self.pool_cache = {}
        self.tick_array_cache = {}
        
    async def execute_copy_trade(self, trade_info: ExtractedCLMMTradeInfo, copy_amount: Optional[float] = None) -> Optional[str]:
        """
        Execute a copy trade based on extracted CLMM trade information
        copy_amount: Amount in SOL to use for the copy trade (overrides original amount for buys)
        Returns transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🔄 Executing CLMM copy trade: {trade_info.token_mint}")
            logger.info(f"   Trade type: {'BUY' if trade_info.is_buy else 'SELL'}")
            logger.info(f"   Original tx: {trade_info.original_signature}")
            logger.info(f"   Original wallet: {trade_info.wallet_address}")
            logger.info(f"   Tick spacing: {trade_info.tick_spacing}")
            
            if trade_info.is_buy:
                # Use copy amount if provided, otherwise use original amount
                sol_amount = copy_amount if copy_amount else trade_info.amount_in / 1_000_000_000
                return await self.execute_buy_copy(trade_info, sol_amount)
            else:
                return await self.execute_sell_copy(trade_info)
                
        except Exception as e:
            logger.error(f"❌ CLMM copy trade execution error: {e}")
            return None
    
    async def execute_buy_copy(self, trade_info: ExtractedCLMMTradeInfo, sol_amount: float) -> Optional[str]:
        """Execute a buy copy trade on CLMM"""
        try:
            logger.info(f"🛒 Executing CLMM BUY copy: {sol_amount} SOL for {trade_info.token_mint}")
            
            # Convert to lamports
            amount_lamports = int(sol_amount * 1_000_000_000)
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Ensure token account exists
            await self.ensure_token_account_exists(token_mint)
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build CLMM swap instruction
            swap_instruction = self.build_clmm_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_wsol_ata,
                user_output_token=user_token_ata,
                amount_in=amount_lamports,
                is_buy=True,
                tick_spacing=trade_info.tick_spacing,
                sqrt_price_limit=trade_info.sqrt_price_limit
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ CLMM buy copy executed: {signature}")
            
            return signature
            
        except Exception as e:
            logger.error(f"❌ CLMM buy copy error: {e}")
            return None
    
    async def execute_sell_copy(self, trade_info: ExtractedCLMMTradeInfo, sell_percentage: float = 100.0) -> Optional[str]:
        """Execute a sell copy trade on CLMM"""
        try:
            logger.info(f"💸 Executing CLMM SELL copy: {trade_info.token_mint}")
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Get token balance
            token_balance = await self.get_token_balance(token_mint)
            
            if token_balance <= 0:
                logger.error(f"❌ No tokens to sell for {trade_info.token_mint}")
                return None
            
            # Use all available tokens for sell
            # Proportional sell calculation
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {sell_percentage}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            amount_to_sell = int(token_balance * (sell_percentage / 100.0))
            logger.info(f"🎯 PROPORTIONAL SELL:\n   Total balance: {token_balance} tokens\n   Amount to sell: {amount_to_sell} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            # Build CLMM swap instruction (reversed for sell)
            swap_instruction = self.build_clmm_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_token_ata,
                user_output_token=user_wsol_ata,
                amount_in=amount_to_sell,
                is_buy=False,
                tick_spacing=trade_info.tick_spacing,
                sqrt_price_limit=trade_info.sqrt_price_limit
            )
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            if signature:
                logger.info(f"✅ CLMM sell copy executed: {signature}")
            return signature
        except Exception as e:
            logger.error(f"❌ CLMM sell copy error: {e}")
            return None
    
    def build_clmm_swap_instruction(
        self,
        pool_info: Dict[str, str],
        user_input_token: Pubkey,
        user_output_token: Pubkey,
        amount_in: int,
        is_buy: bool,
        tick_spacing: int,
        sqrt_price_limit: Optional[int] = None
    ) -> Instruction:
        """Build a CLMM SwapV2 instruction"""
        
        # Convert pool info strings to Pubkeys
        pool_pubkeys = {key: Pubkey.from_string(value) for key, value in pool_info.items()}
        
        # Calculate minimum output with slippage
        if is_buy:
            # For SOL->Token: estimate based on current price
            estimated_out = amount_in * 150  # ~$150 per SOL estimate for tokens
        else:
            # For Token->SOL: rough estimate
            estimated_out = amount_in // 150
        
        min_amount_out = int(estimated_out * (1 - self.config.slippage_tolerance))
        min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
        
        # Set price limit (use provided or default)
        sqrt_price_limit_value = sqrt_price_limit if sqrt_price_limit else 4295048016
        
        # CLMM SwapV2 instruction data format
        # [discriminator(1), amount_in(8), min_amount_out(8), sqrt_price_limit(8), is_base_input(1)]
        is_base_input = is_buy
        
        instruction_data = (
            SWAP_V2_DISCRIMINATOR +
            struct.pack("<QQQ?", amount_in, min_amount_out, sqrt_price_limit_value, is_base_input)
        )
        
        # Build CLMM accounts structure
        accounts = [
            # Core accounts
            AccountMeta(self.wallet_pubkey, True, True),                    # 0: Payer/authority
            AccountMeta(pool_pubkeys["amm_config"], False, False),          # 1: AMM config
            AccountMeta(pool_pubkeys["pool_state"], False, True),           # 2: Pool state
            AccountMeta(user_input_token, False, True),                     # 3: Input token account
            AccountMeta(user_output_token, False, True),                    # 4: Output token account
            AccountMeta(pool_pubkeys["input_vault"], False, True),          # 5: Input vault
            AccountMeta(pool_pubkeys["output_vault"], False, True),         # 6: Output vault
            AccountMeta(pool_pubkeys["tick_array_lower"], False, True),     # 7: Tick array lower
            AccountMeta(pool_pubkeys["tick_array_upper"], False, True),     # 8: Tick array upper
            AccountMeta(pool_pubkeys["observation_state"], False, True),    # 9: Observation state
            
            # Program accounts
            AccountMeta(TOKEN_PROGRAM_ID, False, False),                    # 10: Token program
            AccountMeta(pool_pubkeys["input_token_mint"], False, False),    # 11: Input token mint
            AccountMeta(pool_pubkeys["output_token_mint"], False, False),   # 12: Output token mint
        ]
        
        return Instruction(
            program_id=CLMM_PROGRAM,
            accounts=accounts,
            data=instruction_data
        )
    
    def derive_tick_array_address(self, pool_id: Pubkey, start_tick_index: int) -> Pubkey:
        """Derive tick array address from pool ID and start tick index"""
        try:
            # Convert start_tick_index to bytes
            start_tick_bytes = struct.pack('<i', start_tick_index)
            
            # Find PDA for tick array
            tick_array_pda, _ = Pubkey.find_program_address(
                [b"tick_array", bytes(pool_id), start_tick_bytes],
                CLMM_PROGRAM
            )
            
            return tick_array_pda
            
        except Exception as e:
            logger.error(f"Error deriving tick array address: {e}")
            return Pubkey.from_string("11111111111111111111111111111111")
    
    async def execute_instruction(self, instruction: Instruction) -> Optional[str]:
        """Execute an instruction with retries"""
        try:
            # Execute with retries
            for attempt in range(self.config.max_retries):
                try:
                    # Get recent blockhash
                    recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                    
                    # Create transaction
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=[
                            set_compute_unit_limit(self.config.compute_unit_limit),
                            set_compute_unit_price(self.config.compute_unit_price),
                            instruction
                        ],
                        recent_blockhash=recent_blockhash,
                        address_lookup_table_accounts=[]
                    )
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    
                    # Simulate first
                    sim_result = await self.client.simulate_transaction(transaction)
                    if sim_result.value.err:
                        logger.error(f"❌ Simulation failed: {sim_result.value.err}")
                        if hasattr(sim_result.value, 'logs') and sim_result.value.logs:
                            for log in sim_result.value.logs:
                                logger.error(f"   Log: {log}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                        return None
                    
                    # Send transaction via RPC
                    try:
                        import base64
                        serialized_tx = base64.b64encode(transaction.serialize()).decode("utf-8")
                        from base64 import b64encode
                        tx_bytes_b64 = b64encode(serialized_tx).decode('utf-8')
                        
                        # Send transaction
                        async with aiohttp.ClientSession() as session:
                            payload = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "sendTransaction",
                                "params": [tx_bytes_b64, {"encoding": "base64", "skipPreflight": False}]
                            }
                            async with session.post(self.rpc_url, json=payload) as response:
                                result = await response.json()
                                if 'result' in result:
                                    signature = result['result']
                                    logger.info(f"✅ CLMM transaction sent: {signature}")
                                    return signature
                                else:
                                    logger.error(f"❌ Transaction failed: {result.get('error', 'Unknown error')}")
                                    return None
                    except Exception as send_error:
                        logger.error(f"❌ Send transaction error: {send_error}")
                        return None
                except Exception as e:
                    logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error executing instruction: {e}")
            return None
    
    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
        """
        ENHANCED: Check first, create only if needed - ELIMINATES IllegalOwner errors
        """
        # Calculate ATA address
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        # 🔍 STEP 1: CHECK IF ATA ALREADY EXISTS
        logger.info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
        try:
            account_info = await self.client.get_account_info(ata)
            if account_info.value is not None:
                logger.info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as e:
            logger.debug(f"Error checking ATA existence: {e}")
        
        # 🔨 STEP 2: CREATE ATA ONLY IF IT DOESN'T EXIST
        logger.info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        
        logger.info(f"🔨 Creating ATA for token: {token_mint}")
        
        # Create ATA instruction
        create_ata_ix = create_associated_token_account(
            payer=self.wallet_pubkey,
            owner=self.wallet_pubkey,
            mint=token_mint
        )
        
        try:
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[
                    set_compute_unit_limit(self.config.compute_unit_limit),
                    set_compute_unit_price(self.config.compute_unit_price),
                    create_ata_ix
                ],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            result = await self.client.send_transaction(transaction)
            if result.value:
                logger.info(f"✅ ATA created: {ata}")
                await asyncio.sleep(2)  # Wait for confirmation
            return ata
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            return ata
    
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
    
    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            sig = Signature.from_string(signature)
            
            for i in range(int(timeout)):
                try:
                    status = await self.client.get_transaction(sig, max_supported_transaction_version=0)
                    if status.value:
                        if hasattr(status.value, 'meta') and status.value.meta and status.value.meta.err:
                            logger.error(f"Transaction failed: {status.value.meta.err}")
                            return False
                        else:
                            logger.info(f"✅ Transaction confirmed: {signature}")
                            return True
                except:
                    pass
                await asyncio.sleep(1)
            
            logger.warning("⚠️ Transaction confirmation timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error confirming transaction: {e}")
            return False
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()

# Example usage:
"""
from solders.keypair import Keypair

# Initialize the CLMM copy executor
clmm_copy = RaydiumCLMMCopyExecutor(
    wallet_keypair=your_wallet_keypair,
    rpc_url="https://api.mainnet-beta.solana.com",
    config=CopyExecutorConfig(
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0,
        compute_unit_limit=300_000
    )
)

# When you detect a CLMM trade from another wallet:
# Extract the trade information from the detected transaction
pool_info = {
    "amm_config": "amm_config_address",
    "pool_state": "pool_state_address",
    "input_vault": "input_vault_address",
    "output_vault": "output_vault_address",
    "tick_array_lower": "tick_array_lower_address",
    "tick_array_upper": "tick_array_upper_address",
    "observation_state": "observation_state_address",
    "input_token_mint": "input_token_mint_address",
    "output_token_mint": "output_token_mint_address"
}

extracted_trade = ExtractedCLMMTradeInfo(
    token_mint="token_mint_address",
    is_buy=True,
    amount_in=1000000,  # 0.001 SOL in lamports
    pool_info=pool_info,
    original_signature="detected_transaction_signature",
    wallet_address="wallet_you_are_copying",
    tick_spacing=60,  # Common tick spacing
    sqrt_price_limit=4295048016  # Optional price limit
)

# Execute the copy trade
signature = await clmm_copy.execute_copy_trade(extracted_trade, copy_amount=0.001)

# Confirm the transaction
if signature:
    confirmed = await clmm_copy.confirm_transaction(signature)
    if confirmed:
        print("✅ CLMM copy trade confirmed!")
"""
