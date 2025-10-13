# raydium_trade_executor.py - trading logic for Raydium V4 AMM

"""
Raydium V4 AMM Trade Executor - Core trading logic for Raydium V4 AMM trades
Handles transaction construction and execution for direct Raydium V4 AMM trades
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import struct
import asyncio
import logging

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction, VersionedTransaction
from solders.message import Message, MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    slippage_tolerance: float = 0.05  # 5% slippage tolerance
    max_retries: int = 2  # Number of retries
    retry_delay: float = 1.0  # Delay between retries
    confirmation_timeout: float = 30.0  # Confirmation timeout
    compute_unit_limit: int = 200_000  # Compute units
    compute_unit_price: int = 1  # Micro-lamports per compute unit

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

class RaydiumTradeExecutor:
    """
    Core trading logic for executing trades on Raydium V4 AMM
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: TradeConfig = None):
        self.config = config or TradeConfig()
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = None  # Placeholder for aiohttp/solders logic
        # Raydium V4 AMM Program
        self.RAYDIUM_V4_AMM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
        # System program constants
        self.TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
        self.NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        # Common tokens
        self.USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        # SOL-USDC pool (for reference - will be detected dynamically)
        self.SOL_USDC_POOL = Pubkey.from_string("58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2")
        # Cache for pool addresses
        self.pool_cache = {}

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

    async def find_pool_for_token(self, token_mint: Pubkey) -> Optional[Dict[str, Pubkey]]:
        """Find the Raydium V4 AMM pool for a given token"""
        # Check cache first
        cache_key = str(token_mint)
        if cache_key in self.pool_cache:
            return self.pool_cache[cache_key]
        
        try:
            # For most tokens, we'll try to find a pool paired with SOL or USDC
            # This is a simplified approach - in a full implementation you'd query
            # the Raydium API or scan the blockchain for pools
            
            # Try SOL-TOKEN pool first (most common)
            sol_token_pool = await self._find_pool_by_mints(self.NATIVE_MINT, token_mint)
            if sol_token_pool:
                self.pool_cache[cache_key] = sol_token_pool
                return sol_token_pool
            
            # Try USDC-TOKEN pool
            usdc_token_pool = await self._find_pool_by_mints(self.USDC_MINT, token_mint)
            if usdc_token_pool:
                self.pool_cache[cache_key] = usdc_token_pool
                return usdc_token_pool
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding pool for token {token_mint}: {e}")
            return None

    async def _find_pool_by_mints(self, mint_a: Pubkey, mint_b: Pubkey) -> Optional[Dict[str, Pubkey]]:
        """Find a specific pool by mint pair (simplified implementation)"""
        # This is a simplified implementation
        # In a full implementation, you would:
        # 1. Query Raydium API for pool info
        # 2. Or scan the blockchain for pools
        # 3. Or use a pre-built pool database
        
        # For now, return known pools
        if (str(mint_a) == str(self.NATIVE_MINT) and str(mint_b) == str(self.USDC_MINT)) or \
           (str(mint_a) == str(self.USDC_MINT) and str(mint_b) == str(self.NATIVE_MINT)):
            return {
                "pool_id": self.SOL_USDC_POOL,
                "base_mint": self.NATIVE_MINT,
                "quote_mint": self.USDC_MINT,
                "base_vault": Pubkey.from_string("DQyrAcCrDXQ7NeoqGgDCZwBvWDcYmFCjSb9JtteuvPpz"),
                "quote_vault": Pubkey.from_string("HLmqeL62xR1QoZ1HKKbXRrdN1p3phKpxRMb2VVopvBBz"),
                "amm_authority": Pubkey.from_string("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"),
                "open_orders": Pubkey.from_string("HRk9CMrpq7Jn9sh7mzxE8CChHG2dGZyk6dwqnkirkein"),
                "target_orders": Pubkey.from_string("4UzK7Sgm84xQwr51rtygVuHUXZTjPrkJRfbDtw9AYUjg"),
                "market_id": Pubkey.from_string("9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT"),
                "market_bids": Pubkey.from_string("14ivtgssEBoBjuZJtSAPKYWpuuttqKNDbbQMUQy9cDge"),
                "market_asks": Pubkey.from_string("CEQdAFKdycHugujQg9nDiNMRf2KwWb9jA9eCL6Btt2vV"),
                "market_event_queue": Pubkey.from_string("8CvwxZ9Db6XbLD46NZwwmVDZZRDy7eydFcAGkXKh9axa"),
                "market_base_vault": Pubkey.from_string("36c6YqAwyGKQG66XEp2dJc5JqjaBNv7sVghEtJv4c7u6"),
                "market_quote_vault": Pubkey.from_string("8CFo8bL8mZQK8abbFyypFMwEDd8tVJjHTTojMLgQTUSZ"),
                "market_authority": Pubkey.from_string("F8Vyqk3unwxkXukZFQeYyGmFfTG3CAX4v24iyrjEYBJV"),
                "serum_program": Pubkey.from_string("srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX")
            }
        
        return None

    def _build_raydium_swap_accounts(self, pool_info: Dict[str, Pubkey], user_input_token: Pubkey, 
                                   user_output_token: Pubkey) -> list[AccountMeta]:
        """Build the 18-account structure for Raydium V4 AMM swap"""
        return [
            # AMM accounts (7)
            AccountMeta(self.TOKEN_PROGRAM_ID, False, False),          # 0: Token program
            AccountMeta(pool_info["pool_id"], False, True),            # 1: AMM pool ID
            AccountMeta(pool_info["amm_authority"], False, False),     # 2: AMM authority
            AccountMeta(pool_info["open_orders"], False, True),        # 3: AMM open orders
            AccountMeta(pool_info["target_orders"], False, True),      # 4: AMM target orders
            AccountMeta(pool_info["base_vault"], False, True),         # 5: AMM base vault
            AccountMeta(pool_info["quote_vault"], False, True),        # 6: AMM quote vault
            
            # Serum market accounts (8)
            AccountMeta(pool_info["serum_program"], False, False),     # 7: Serum program
            AccountMeta(pool_info["market_id"], False, True),          # 8: Market ID
            AccountMeta(pool_info["market_bids"], False, True),        # 9: Market bids
            AccountMeta(pool_info["market_asks"], False, True),        # 10: Market asks
            AccountMeta(pool_info["market_event_queue"], False, True), # 11: Market event queue
            AccountMeta(pool_info["market_base_vault"], False, True),  # 12: Market base vault
            AccountMeta(pool_info["market_quote_vault"], False, True), # 13: Market quote vault
            AccountMeta(pool_info["market_authority"], False, False),  # 14: Market authority
            
            # User accounts (3)
            AccountMeta(user_input_token, False, True),                # 15: User input token
            AccountMeta(user_output_token, False, True),               # 16: User output token
            AccountMeta(self.wallet_pubkey, True, False),              # 17: User wallet (signer)
        ]

    async def execute_buy_trade(
        self, 
        token_mint: Pubkey, 
        sol_amount: Optional[float] = None,
        pool_info: Optional[Dict[str, Pubkey]] = None
    ) -> Optional[str]:
        """Execute a buy trade on Raydium V4 AMM, returns the transaction signature or None"""
        sol_amount = sol_amount or self.config.sol_amount
        logger.info(f"🛒 Executing Raydium BUY trade: {sol_amount} SOL for {token_mint}")
        
        try:
            # Find pool if not provided
            if not pool_info:
                pool_info = await self.find_pool_for_token(token_mint)
                if not pool_info:
                    logger.error(f"❌ No pool found for token {token_mint}")
                    return None
            
            # Ensure token account exists
            await self.ensure_token_account_exists(token_mint)
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, self.NATIVE_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build accounts for swap
            accounts = self._build_raydium_swap_accounts(pool_info, user_wsol_ata, user_token_ata)
            
            # Calculate amounts
            amount_in = int(sol_amount * 1_000_000_000)  # Convert to lamports
            # For SOL->USDC: roughly 1 SOL = 150 USDC, so 0.001 SOL = ~0.15 USDC
            # Apply slippage protection: expect less output to account for slippage
            estimated_usdc_out = (amount_in * 150) // 1_000_000_000  # Rough estimate in micro-USDC
            min_amount_out = int(estimated_usdc_out * (1 - self.config.slippage_tolerance))
            min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
            
            # Build instruction data: discriminator 9, amount_in, min_amount_out
            instruction_data = struct.pack("<BQQ", 9, amount_in, min_amount_out)
            
            # Create swap instruction
            swap_instruction = Instruction(
                program_id=self.RAYDIUM_V4_AMM,
                accounts=accounts,
                data=instruction_data
            )
            
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
                            swap_instruction
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
                    
                    # Send transaction
                    # TODO: Replace with aiohttp/solders logic to send transaction
                    raise NotImplementedError("send_transaction must be implemented with aiohttp/Solders")
                except Exception as e:
                    logger.error(f"❌ Buy attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Buy trade error: {e}")
            return None

    async def execute_sell_trade(
        self, 
        token_mint: Pubkey, 
        token_amount: Optional[int] = None,
        pool_info: Optional[Dict[str, Pubkey]] = None,
        **kwargs
    ) -> Optional[str]:
        """Execute a sell trade on Raydium V4 AMM with proportional selling support"""
        logger.info(f"💸 Executing Raydium SELL trade: {token_amount or 'ALL'} tokens for {token_mint}")
        
        try:
            # Get token balance if amount not specified
            if token_amount is None:
                token_amount = await self.get_token_balance(token_mint)
                
            if token_amount <= 0:
                logger.error(f"❌ No tokens to sell for {token_mint}")
                return None

            # Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {sell_percentage}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            proportional_amount = int(token_amount * (sell_percentage / 100.0))
            logger.info(f"🎯 RAYDIUM PROPORTIONAL SELL:\n   Total balance: {token_amount} tokens\n   Amount to sell: {proportional_amount} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Use proportional amount
            token_amount = proportional_amount
            
            # Find pool if not provided
            if not pool_info:
                pool_info = await self.find_pool_for_token(token_mint)
                if not pool_info:
                    logger.error(f"❌ No pool found for token {token_mint}")
                    return None
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, self.NATIVE_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build accounts for swap (reversed for sell)
            accounts = self._build_raydium_swap_accounts(pool_info, user_token_ata, user_wsol_ata)
            
            # Calculate minimum output with slippage
            # For token->SOL: rough estimate based on token amount
            # In practice, you'd query the pool for actual rates
            estimated_sol_out = token_amount // 1000  # Very rough estimate
            min_amount_out = int(estimated_sol_out * (1 - self.config.slippage_tolerance))
            min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
            
            # Build instruction data: discriminator 9, amount_in, min_amount_out
            instruction_data = struct.pack("<BQQ", 9, token_amount, min_amount_out)
            
            # Create swap instruction
            swap_instruction = Instruction(
                program_id=self.RAYDIUM_V4_AMM,
                accounts=accounts,
                data=instruction_data
            )
            
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
                            swap_instruction
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
                    
                    # Send transaction
                    # TODO: Replace with aiohttp/solders logic to send transaction
                    raise NotImplementedError("send_transaction must be implemented with aiohttp/Solders")
                except Exception as e:
                    logger.error(f"❌ Sell attempt {attempt + 1} error: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Sell trade error: {e}")
            return None

    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            sig = Signature.from_string(signature)
            
            # Simple confirmation by checking transaction status
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

    async def get_pool_info_for_transaction(self, token_mint: Pubkey, 
                                          transaction_accounts: list[Pubkey]) -> Optional[Dict[str, Pubkey]]:
        """
        Extract pool information from a detected transaction's accounts
        This is useful when copying trades - you can extract the pool info from the original transaction
        """
        try:
            # This is a simplified implementation
            # In practice, you'd analyze the transaction accounts to identify:
            # - Pool ID
            # - Vaults
            # - Market accounts
            # - etc.
            
            # For now, try to find the pool normally
            return await self.find_pool_for_token(token_mint)
            
        except Exception as e:
            logger.error(f"Error extracting pool info from transaction: {e}")
            return None

    async def copy_trade_from_transaction(self, 
                                        original_transaction: Any,
                                        copy_amount: Optional[float] = None) -> Optional[str]:
        """
        Copy a trade from an original transaction
        This is the main function your copy bot would use
        """
        try:
            # Extract trade details from original transaction
            # This would need to be implemented based on your transaction parsing logic
            
            # For now, this is a placeholder that shows the structure
            # You would implement transaction parsing here
            
            logger.info("🔄 Copying Raydium trade from detected transaction")
            
            # Extract:
            # - Token mint
            # - Trade direction (buy/sell)
            # - Pool information
            # - Original amounts
            
            # Example implementation:
            # trade_details = self.parse_raydium_transaction(original_transaction)
            # if trade_details['action'] == 'buy':
            #     return await self.execute_buy_trade(
            #         trade_details['token_mint'],
            #         copy_amount or self.config.sol_amount,
            #         trade_details['pool_info']
            #     )
            # else:
            #     return await self.execute_sell_trade(
            #         trade_details['token_mint'],
            #         None,  # Sell all
            #         trade_details['pool_info']
            #     )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error copying trade: {e}")
            return None

    async def close(self):
        """Close the client connection"""
        await self.client.close()

# Example usage in your copy bot:
"""
# Initialize the executor
raydium_executor = RaydiumTradeExecutor(
    wallet_keypair=your_wallet,
    rpc_url=your_rpc_url,
    config=TradeConfig(
        sol_amount=0.005,
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
)

# When you detect a Raydium trade to copy:
if detected_program_id == raydium_executor.RAYDIUM_V4_AMM:
    # Copy the trade
    signature = await raydium_executor.copy_trade_from_transaction(
        original_transaction=detected_transaction,
        copy_amount=0.01  # Amount to copy with
    )
    
    if signature:
        print(f"✅ Raydium trade copied: {signature}")
        
        # Confirm the transaction
        confirmed = await raydium_executor.confirm_transaction(signature)
        if confirmed:
            print(f"✅ Trade confirmed!")
    else:
        print("❌ Failed to copy Raydium trade")

# Or execute direct trades:
# Buy trade
buy_signature = await raydium_executor.execute_buy_trade(
    token_mint=Pubkey.from_string("your_token_mint"),
    sol_amount=0.01
)

# Sell trade
sell_signature = await raydium_executor.execute_sell_trade(
    token_mint=Pubkey.from_string("your_token_mint"),
    token_amount=None  # Sell all tokens
)
"""
