"""
Meteora Trading Bot
Complete autonomous trading system for Meteora DEX
Supports concentrated liquidity AMM trading
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from da            swap_ix = Instruction(
                program_id=self.METEORA_PROGRAM,
                accounts=accounts,
                data=self.SWAP_IX_DATA
            )import dataclass
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
        logging.FileHandler('meteora_trading.log'),
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
    max_retries: int = 1  # Number of retry attempts
    retry_delay: float = 0.0  # Delay between retries
    confirmation_timeout: float = 10.0  # Transaction confirmation timeout
    max_balance_checks: int = 1  # Single balance check
    initial_wait_time: float = 0.0  # No initial wait
    hold_time: float = 5.0  # Hold time between buy and sell

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
class MeteoraPoolConfig:
    """Configuration for a Meteora concentrated liquidity pool"""
    pool_state: Pubkey  # Pool state account
    token_mint_a: Pubkey  # Usually SOL or USDC
    token_mint_b: Pubkey  # Usually the meme token
    token_vault_a: Pubkey  # Pool's vault for token A
    token_vault_b: Pubkey  # Pool's vault for token B
    tick_array_lower: Pubkey  # Lower tick array account
    tick_array_upper: Pubkey  # Upper tick array account
    pool_authority: Pubkey  # Pool authority account

class MeteoraTrader:
    """Trading bot for Meteora DEX"""
    
    # Program IDs
    METEORA_PROGRAM = Pubkey.from_string("dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN")
    SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
    TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    
    # Swap instruction data (from successful transaction)
    SWAP_IX_DATA = b"PgQWtn8ozix6cpwcwUNzHq8uXgNGK4tPZ"
    
    # Test token configuration (from successful transaction)
    TEST_TOKEN_CONFIG = MeteoraPoolConfig(
        pool_state=Pubkey.from_string("FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"),  # Pool state
        token_mint_a=Pubkey.from_string("So11111111111111111111111111111111111111112"),  # SOL
        token_mint_b=Pubkey.from_string("48yyMgABcAewsxP5kNYCQbBPtzeiW56VRmKGUq4KRrB7"),  # New meme token
        token_vault_a=Pubkey.from_string("8crbEXjs6M79TLoeSDEFjHQCnsyVCQ8Pp64hvSaUdHdx"),  # SOL vault
        token_vault_b=Pubkey.from_string("KAC6EWXwMK4V2He9egprPTHQdB98ctsxq7RRWgCvgN3"),  # Token vault
        tick_array_lower=Pubkey.from_string("BwdseMFNNmBeUkiHEFs1GVrggTUX4ZeeMvMnYwV41Etu"),  # Lower tick array
        tick_array_upper=Pubkey.from_string("BLTGHwKPVz8cCwDaXa59zvCr9kkjAm7vxo1NuDe2WUGa"),  # Upper tick array
        pool_authority=Pubkey.from_string("8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF")  # Pool authority
    )
    
    def __init__(self, trade_config: TradeConfig = None):
        self.config = trade_config or TradeConfig()
        self.wallet_keypair = WALLET
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        self.client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
        self.wallet = self.wallet_keypair  # For compatibility
        
        logger.info(f"🤖 Meteora Trading Bot initialized")
        logger.info(f"📱 Wallet: {self.wallet_pubkey}")
        logger.info(f"💰 SOL per trade: {self.config.sol_amount}")
        logger.info(f"⚙️ Slippage: {self.config.slippage_tolerance*100}%")
        logger.info(f"⏱️ Hold time: {self.config.hold_time}s")

    def _build_swap_accounts(self, pool_config: MeteoraPoolConfig, is_buy: bool) -> list[AccountMeta]:
        """Build account list for Meteora swap instruction"""
        # Get user's token accounts
        user_token_a = get_associated_token_address(self.wallet_pubkey, pool_config.token_mint_a)
        user_token_b = get_associated_token_address(self.wallet_pubkey, pool_config.token_mint_b)
        
        # Build accounts list based on transaction analysis
        accounts = [
            # Pool accounts (order matters)
            AccountMeta(pool_config.pool_state, False, True),      # Pool state
            AccountMeta(pool_config.token_vault_a, False, True),   # Token A vault
            AccountMeta(pool_config.token_vault_b, False, True),   # Token B vault
            AccountMeta(pool_config.tick_array_lower, False, True),# Lower tick array
            AccountMeta(pool_config.tick_array_upper, False, True),# Upper tick array
            
            # User accounts
            AccountMeta(self.wallet_pubkey, True, True),          # User (signer)
            AccountMeta(user_token_a if is_buy else user_token_b, False, True),  # Input token account
            AccountMeta(user_token_b if is_buy else user_token_a, False, True),  # Output token account
            
            # Program accounts
            AccountMeta(self.TOKEN_PROGRAM, False, False),        # Token program
            AccountMeta(pool_config.pool_authority, False, False),# Pool authority
        ]
        
        return accounts

    async def ensure_token_account(self, token_mint: Pubkey) -> Pubkey:
        """Create token account if it doesn't exist"""
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        try:
            info = await self.client.get_account_info(ata)
            if info.value:
                return ata
                
            # Create ATA
            create_ix = create_associated_token_account(
                payer=self.wallet_pubkey,
                owner=self.wallet_pubkey,
                mint=token_mint
            )
            
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([create_ix], self.wallet_pubkey, recent_blockhash)
            transaction = Transaction(
                from_keypairs=[self.wallet_keypair],
                message=message,
                recent_blockhash=recent_blockhash
            )
            
            await self.client.send_transaction(transaction)
            await asyncio.sleep(1)  # Wait for confirmation
            
            return ata
        except Exception as e:
            logger.error(f"Error creating token account: {e}")
            raise

    async def execute_swap(self,
        pool_config: MeteoraPoolConfig,
        amount_in: int,
        min_amount_out: int,
        is_buy: bool
    ) -> bool:
        """Execute a direct Meteora swap using exact production transaction structure"""
        try:
            # 1. Set up compute budget (exact from successful tx)
            compute_budget_ix1 = Instruction(
                program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
                accounts=[],
                data=bytes.fromhex("4c454a444537")  # "LEJDE7" in hex
            )
            compute_budget_ix2 = Instruction(
                program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
                accounts=[],
                data=bytes.fromhex("334c576765507937656d6a64")  # "3LWgePy7emjd" in hex
            )

            # 2. Create ephemeral token account
            input_mint = pool_config.token_mint_a if is_buy else pool_config.token_mint_b
            output_mint = pool_config.token_mint_b if is_buy else pool_config.token_mint_a
            
            # Generate ephemeral keypair with random seed
            ephemeral_key = Keypair()
            space = 165  # Token account size
            lamports = (await self.client.get_minimum_balance_for_rent_exemption(space)).value
            
            # Create account instruction
            create_account_ix = Instruction(
                program_id=self.SYSTEM_PROGRAM,
                accounts=[
                    AccountMeta(self.wallet_pubkey, True, True),
                    AccountMeta(ephemeral_key.pubkey(), True, True)
                ],
                data=bytes([0]) + lamports.to_bytes(8, 'little') + space.to_bytes(8, 'little') + bytes(self.TOKEN_PROGRAM)
            )

            # Initialize token account
            init_token_ix = Instruction(
                program_id=self.TOKEN_PROGRAM,
                accounts=[
                    AccountMeta(ephemeral_key.pubkey(), True, True),
                    AccountMeta(output_mint, False, False),
                    AccountMeta(self.wallet_pubkey, True, False),
                    AccountMeta(self.SYSTEM_PROGRAM, False, False)
                ],
                data=bytes([1])  # InitializeAccount instruction
            )

            # 3. Build swap instruction accounts list
            accounts = [
                AccountMeta(pool_config.pool_state, False, False),       # Pool state
                AccountMeta(pool_config.token_vault_a, False, True),     # Vault A
                AccountMeta(pool_config.token_vault_b, False, True),     # Vault B
                AccountMeta(pool_config.tick_array_lower, False, True),  # Lower tick array
                AccountMeta(pool_config.tick_array_upper, False, True),  # Upper tick array
                AccountMeta(get_associated_token_address(self.wallet_pubkey, input_mint), False, True),  # Input token
                AccountMeta(input_mint, False, False),                   # Input mint
                AccountMeta(output_mint, False, False),                  # Output mint
                AccountMeta(self.wallet_pubkey, True, True),            # User (signer)
                AccountMeta(self.TOKEN_PROGRAM, False, False),          # Token program
                AccountMeta(self.TOKEN_PROGRAM, False, False),          # Token program (transfers)
                AccountMeta(ephemeral_key.pubkey(), True, True),       # Ephemeral output account
                AccountMeta(pool_config.pool_authority, False, False),  # Pool authority
                AccountMeta(self.METEORA_PROGRAM, False, False),       # Meteora program
            ]

            # 4. Build swap instruction
            swap_ix = Instruction(
                program_id=self.METEORA_PROGRAM,
                accounts=accounts,
                data=(
                    self.SWAP_IX_DATA +
                    amount_in.to_bytes(8, 'little') +
                    min_amount_out.to_bytes(8, 'little') +
                    bytes([1 if is_buy else 0])
                )
            )

            # 5. Add cleanup instructions
            close_token_ix = Instruction(
                program_id=self.TOKEN_PROGRAM,
                accounts=[
                    AccountMeta(ephemeral_key.pubkey(), False, True),
                    AccountMeta(get_associated_token_address(self.wallet_pubkey, output_mint), False, True),
                    AccountMeta(self.wallet_pubkey, True, False)
                ],
                data=bytes([9])  # CloseAccount instruction
            )

            # 6. Build and send transaction
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash(
                [
                    compute_budget_ix1,      # Set priority fee
                    compute_budget_ix2,      # Set compute unit limit
                    create_account_ix,       # Create ephemeral account
                    init_token_ix,           # Initialize as token account
                    swap_ix,                 # Execute swap
                    close_token_ix           # Cleanup
                ],
                self.wallet_pubkey,
                blockhash
            )
            
            transaction = Transaction(
                from_keypairs=[self.wallet_keypair, ephemeral_key],  # Both keys needed
                message=message,
                recent_blockhash=blockhash
            )
            
            # Send with optimized options
            result = await self.client.send_transaction(
                transaction,
                opts=TxOpts(
                    skip_preflight=True,
                    preflight_commitment=Processed,
                    max_retries=0
                )
            )
            
            if not result.value:
                return False

            try:
                await asyncio.wait_for(
                    self.client.confirm_transaction(result.value),
                    timeout=2.0
                )
                logger.info(f"✅ Transaction confirmed: {result.value}")
            except asyncio.TimeoutError:
                logger.info(f"Transaction sent: {result.value}")
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"Swap error: {e}")
            return False

    async def execute_trade_cycle(self,
        pool_config: MeteoraPoolConfig,
        amount_in_sol: float,
        slippage_bps: int = 1000,  # 10% default slippage
        hold_time: float = 5.0
    ) -> bool:
        """Quick buy-hold-sell test cycle with enhanced debugging"""
        try:
            # Log pool configuration
            logger.info("🏊 Pool Configuration:")
            logger.info(f"Pool State: {pool_config.pool_state}")
            logger.info(f"Token A (SOL): {pool_config.token_mint_a}")
            logger.info(f"Token B (Meme): {pool_config.token_mint_b}")
            
            # Calculate amounts with very aggressive slippage for testing
            amount_in_lamports = int(amount_in_sol * 1e9)
            slippage_bps = 2000  # 20% slippage for testing
            min_out_ratio = (10000 - slippage_bps) / 10000
            min_token_out = 1  # Accept any amount for testing
            
            logger.info(f"🚀 Starting test cycle...")
            logger.info(f"Input: {amount_in_sol} SOL ({amount_in_lamports} lamports)")
            logger.info(f"Slippage: {slippage_bps/100}%")
            
            # Pre-create token accounts
            logger.info("🏦 Creating token accounts if needed...")
            await self.ensure_token_account(pool_config.token_mint_a)  # SOL
            await self.ensure_token_account(pool_config.token_mint_b)  # Meme token
            
            # Check initial balances
            logger.info("💰 Initial balances:")
            sol_balance = await self.get_token_balance(pool_config.token_mint_a)
            token_balance = await self.get_token_balance(pool_config.token_mint_b)
            logger.info(f"SOL: {sol_balance/1e9:.9f}")
            logger.info(f"Token: {token_balance}")
            
            # Execute buy with more retries
            logger.info("💸 Executing buy...")
            max_retries = 3
            for attempt in range(max_retries):
                buy_success = await self.execute_swap(
                    pool_config=pool_config,
                    amount_in=amount_in_lamports,
                    min_amount_out=min_token_out,
                    is_buy=True
                )
                
                if not buy_success:
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying buy (attempt {attempt + 2}/{max_retries})...")
                        await asyncio.sleep(1)  # Longer delay between retries
                        continue
                    logger.error("Buy failed after all retries!")
                    return False
                break
            
            # Wait longer for balance update
            logger.info("⏳ Waiting for token balance update...")
            await asyncio.sleep(3)  # Increased wait time
            
            # Check token balance with more retries and detailed logging
            for attempt in range(5):
                logger.info(f"\n=== Balance Check Attempt {attempt + 1}/5 ===")
                token_balance = await self.get_token_balance(pool_config.token_mint_b)
                
                if token_balance > 0:
                    logger.info(f"✅ Buy success! Received {token_balance} tokens")
                    break
                    
                logger.info(f"No tokens yet, waiting...")
                await asyncio.sleep(1.5)  # Increased interval between checks
            else:
                logger.error("❌ Buy failed - no tokens received after all attempts")
                return False
            
            # Hold
            logger.info(f"⏳ Holding for {hold_time}s...")
            await asyncio.sleep(hold_time)
            
            # Execute sell
            logger.info("💱 Selling tokens...")
            min_sol_out = 1  # Accept any amount for testing
            
            sell_success = await self.execute_swap(
                pool_config=pool_config,
                amount_in=token_balance,
                min_amount_out=min_sol_out,
                is_buy=False
            )
            
            if sell_success:
                logger.info("✅ Test cycle completed!")
            else:
                logger.error("❌ Sell failed")
            
            return sell_success
            
        except Exception as e:
            logger.error(f"Test cycle error: {e}")
            return False

    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get token balance with detailed logging"""
        try:
            ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Debug logging
            logger.info(f"🪙 Target mint: {token_mint}")
            logger.info(f"👛 Wallet: {self.wallet_pubkey}")
            logger.info(f"🎯 ATA: {ata}")
            
            # Check if ATA exists
            ata_info = await self.client.get_account_info(ata)
            if not ata_info.value:
                logger.warning(f"❌ ATA does not exist for mint {token_mint}")
                return 0
                
            # Get balance
            balance = await self.client.get_token_account_balance(ata)
            logger.info(f"📦 Token balance response: {balance}")
            
            return int(balance.value.amount) if balance.value else 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def close(self):
        """Close client connection"""
        await self.client.close()

async def main():
    """Test entry point for the Meteora trading bot"""
    # Create trading bot instance with production parameters
    trade_config = TradeConfig(
        sol_amount=0.001,  # 0.001 SOL per trade (smaller test amount)
        slippage_tolerance=0.10,  # 10% slippage tolerance
        max_retries=1,
        retry_delay=0.0,
        confirmation_timeout=10.0,
        max_balance_checks=1,
        initial_wait_time=0.0,
        hold_time=5.0  # 5 second hold time
    )
    
    bot = MeteoraTrader(trade_config)
    
    try:
        logger.info("🚀 Starting test trade cycle for meme token...")
        
        # Execute complete trade cycle
        success = await bot.execute_trade_cycle(
            pool_config=MeteoraTrader.TEST_TOKEN_CONFIG,
            amount_in_sol=trade_config.sol_amount,
            slippage_bps=int(trade_config.slippage_tolerance * 10000),  # Convert to basis points
            hold_time=trade_config.hold_time
        )
        
        if success:
            logger.info("✅ Test trade cycle completed successfully!")
        else:
            logger.error("❌ Test trade cycle failed")
            
    except Exception as e:
        logger.error(f"❌ Error during test: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    # Run the test
    asyncio.run(main())
