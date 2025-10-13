"""
PumpFun Trade Executor - Official Solana Documentation Best Practices
Implements pump.fun trades using official Solana transaction patterns
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import struct
import asyncio
import logging

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction, VersionedTransaction
from solders.message import Message, MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed, Confirmed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from spl.token.constants import TOKEN_PROGRAM_ID

# Import official base executor
from base_solana_executor import BaseSolanaExecutor, SolanaExecutorConfig

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

class PumpFunTradeExecutor(BaseSolanaExecutor):
    """
    Pump.fun trade executor implementing official Solana best practices
    Inherits from BaseSolanaExecutor for consistent transaction handling
    """
    
    # Pump.fun program constants
    PUMP_PROGRAM = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
    GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
    FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV2Sg5K8xQhXYiGW8")
    SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
    TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    CREATOR_VAULT = Pubkey.from_string("HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL")
    
    # Pump.fun instruction discriminators
    BUY_DISCRIMINATOR = bytes([102, 6, 61, 18, 1, 218, 235, 234])
    SELL_DISCRIMINATOR = bytes([51, 230, 133, 164, 1, 127, 131, 173])
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: SolanaExecutorConfig = None):
        # Initialize base executor with official patterns
        super().__init__(wallet_keypair, rpc_url, config)
        
        logger.info(f"✅ PumpFun executor initialized with official Solana best practices")

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

class PumpFunTradeExecutor:
    """
    Core trading logic for executing trades on pump.fun
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: 'SolanaExecutorConfig' = None):
        self.config = config or SolanaExecutorConfig()
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        
        # Pump.fun program constants
        self.PUMP_PROGRAM = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        self.CREATOR_VAULT = Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD")
        
        # System program constants
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        # Instruction discriminators
        self.BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")
        self.SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")

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
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        # 🔍 STEP 1: CHECK IF ATA EXISTS
        logger.info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
        try:
            account_info = await self.client.get_account_info(ata, commitment=Confirmed)
            if account_info.value and account_info.value.owner == TOKEN_PROGRAM_ID:
                logger.info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as check_error:
            logger.debug(f"🔍 ATA check failed, will create: {check_error}")
        
        # 🔨 STEP 2: CREATE ATA ONLY IF IT DOESN'T EXIST
        logger.info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        
        from spl.token.instructions import create_associated_token_account
        
        create_ata_ix = create_associated_token_account(
            payer=self.wallet_pubkey,
            owner=self.wallet_pubkey,
            mint=token_mint
        )
        
        recent_blockhash = await self.client.get_latest_blockhash()
        transaction = Transaction.new_with_payer([create_ata_ix], self.wallet_pubkey)
        transaction.sign([self.wallet_keypair], recent_blockhash.value.blockhash)
        
        try:
            response = await self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Processed))
            logger.info(f"✅ ATA creation transaction sent: {response.value}")
            await self.client.confirm_transaction(response.value, commitment=Confirmed)
            logger.info(f"✅ ATA creation confirmed: {str(ata)[:8]}...")
            return ata
        except Exception as create_error:
            logger.error(f"❌ Failed to create ATA: {create_error}")
            raise Exception(f"Failed to create ATA for token {token_mint}: {create_error}")
    async def derive_bonding_curve(self, token_mint: Pubkey) -> Pubkey:
        """Derive bonding curve PDA using official Solana methods"""
        try:
            bonding_curve, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(token_mint)],
                self.PUMP_PROGRAM
            )
            return bonding_curve
        except Exception as e:
            logger.error(f"❌ Error deriving bonding curve: {e}")
            raise
    
    async def derive_bonding_curve_ata(self, token_mint: Pubkey, bonding_curve: Pubkey) -> Pubkey:
        """Derive bonding curve ATA using official methods"""
        try:
            return get_associated_token_address(bonding_curve, token_mint)
        except Exception as e:
            logger.error(f"❌ Error deriving bonding curve ATA: {e}")
            raise
    
    async def build_buy_instruction(self, token_mint: Pubkey, bonding_curve: Pubkey, 
                                   bonding_curve_ata: Pubkey, creator_vault: Pubkey,
                                   sol_amount: float, slippage_tolerance: float) -> Instruction:
        """Build buy instruction using official patterns"""
        try:
            # Build accounts list
            our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            accounts = [
                AccountMeta(self.GLOBAL_ACCOUNT, is_signer=False, is_writable=True),
                AccountMeta(self.FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(token_mint, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(creator_vault, is_signer=False, is_writable=True),
                AccountMeta(self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(self.PUMP_PROGRAM, is_signer=False, is_writable=False),
            ]
            
            # Create instruction data with slippage
            sol_amount_lamports = int(sol_amount * 1_000_000_000)
            max_sol_cost = int(sol_amount_lamports * (1 + slippage_tolerance))
            instruction_data = self.BUY_DISCRIMINATOR + struct.pack("<QQ", sol_amount_lamports, max_sol_cost)
            
            return Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error building buy instruction: {e}")
            raise
    
    async def build_sell_instruction(self, token_mint: Pubkey, bonding_curve: Pubkey,
                                    bonding_curve_ata: Pubkey, creator_vault: Pubkey,
                                    token_amount: int, min_sol_out: int) -> Instruction:
        """Build sell instruction using official patterns"""
        try:
            # Build accounts list
            our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            accounts = [
                AccountMeta(self.GLOBAL_ACCOUNT, is_signer=False, is_writable=True),
                AccountMeta(self.FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(token_mint, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(creator_vault, is_signer=False, is_writable=True),
                AccountMeta(self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(self.PUMP_PROGRAM, is_signer=False, is_writable=False),
            ]
            
            # Create sell instruction data
            instruction_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", token_amount, min_sol_out)
            
            return Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error building sell instruction: {e}")
            raise

    async def execute_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Execute buy trade using official Solana best practices
        Implements the base class abstract method
        """
        try:
            logger.info(f"🚀 OFFICIAL Pump.fun BUY: {amount_sol} SOL → {token_mint[:8]}...")
            
            # Official: Validate inputs
            if amount_sol < self.config.min_sol_amount:
                return {
                    'success': False,
                    'error': f'Amount too small: {amount_sol} SOL (min: {self.config.min_sol_amount})',
                    'signature': None
                }
            
            # Official: Validate SOL balance
            if not await self.validate_sol_balance(amount_sol):
                return {
                    'success': False,
                    'error': 'Insufficient SOL balance',
                    'signature': None
                }
            
            # Get token mint pubkey
            try:
                token_mint_pubkey = Pubkey.from_string(token_mint)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Invalid token mint: {e}',
                    'signature': None
                }
            
            # Derive bonding curve accounts
            bonding_curve = await self.derive_bonding_curve(token_mint_pubkey)
            bonding_curve_ata = await self.derive_bonding_curve_ata(token_mint_pubkey, bonding_curve)
            
            # Ensure our token account exists
            await self.ensure_token_account_exists(token_mint_pubkey)
            
            # Get optimal creator vault
            creator_vault = await self.get_optimal_creator_vault(token_mint_pubkey)
            
            # Build buy instruction using official patterns
            buy_instruction = await self.build_buy_instruction(
                token_mint_pubkey, bonding_curve, bonding_curve_ata, 
                creator_vault, amount_sol, kwargs.get('slippage_tolerance', self.config.default_slippage)
            )
            
            # Execute using official base class method
            return await self.execute_transaction_official([buy_instruction])
            
        except Exception as e:
            logger.error(f"❌ Pump.fun buy error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signature': None
            }
    
    async def execute_sell(self, token_mint: str, **kwargs) -> Dict[str, Any]:
        """
        Execute sell trade using official Solana best practices
        Implements the base class abstract method
        """
        try:
            logger.info(f"💸 OFFICIAL Pump.fun SELL: {token_mint[:8]}...")
            
            # Get token mint pubkey
            try:
                token_mint_pubkey = Pubkey.from_string(token_mint)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Invalid token mint: {e}',
                    'signature': None
                }
            
            # Check token balance
            token_balance = await self.get_token_balance(token_mint_pubkey)
            if token_balance <= 0:
                return {
                    'success': False,
                    'error': f'No tokens to sell: {token_balance}',
                    'signature': None
                }
            
            # Derive bonding curve accounts
            bonding_curve = await self.derive_bonding_curve(token_mint_pubkey)
            bonding_curve_ata = await self.derive_bonding_curve_ata(token_mint_pubkey, bonding_curve)
            
            # Get optimal creator vault
            creator_vault = await self.get_optimal_creator_vault(token_mint_pubkey)
            
            # Build sell instruction
            sell_instruction = await self.build_sell_instruction(
                token_mint_pubkey, bonding_curve, bonding_curve_ata,
                creator_vault, token_balance, kwargs.get('min_sol_out', 0)
            )
            
            # Execute using official base class method
            return await self.execute_transaction_official([sell_instruction])
            
        except Exception as e:
            logger.error(f"❌ Pump.fun sell error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signature': None
            }

    async def execute_sell_trade(
        self, 
        token_mint: Pubkey, 
        bonding_curve: Pubkey, 
        bonding_curve_ata: Pubkey,
        token_amount: int,
        min_sol_out: Optional[int] = None
    ) -> Optional[str]:
        """Execute a sell trade on pump.fun, returns the transaction signature or None"""
        min_sol_out = min_sol_out or 0
        logger.info(f"💸 Executing SELL trade: {token_amount:,} tokens for {token_mint}")
        
        try:
            # Verify balances
            initial_tokens = await self.get_token_balance(token_mint)
            
            if initial_tokens < token_amount:
                logger.error(f"❌ Insufficient tokens: have {initial_tokens:,}, need {token_amount:,}")
                return None
            
            # Get optimal creator vault
            creator_vault = await self.get_optimal_creator_vault(token_mint)
            logger.info(f"🔑 Using creator vault: {creator_vault} for token: {token_mint}")
            
            # Build accounts with optimal vault
            accounts = self._build_trade_accounts(token_mint, bonding_curve, bonding_curve_ata, creator_vault)
            
            # Create sell instruction data
            instruction_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", token_amount, min_sol_out)
            
            # Create instruction
            sell_instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
            # Execute with retries
            signature = None
            for attempt in range(self.config.max_retries):
                try:
                    # Get recent blockhash
                    recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                    
                    # Create and sign transaction
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=[sell_instruction],
                        recent_blockhash=recent_blockhash,
                        address_lookup_table_accounts=[]
                    )
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    
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
                        
                        # Return signature immediately after sending for async confirmation
                        return signature
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        
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

    async def get_optimal_creator_vault(self, token_mint: Pubkey) -> Pubkey:
        """Get the optimal creator vault for a token"""
        try:
            # Known mappings for router-based tokens
            if str(token_mint) == "766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump":
                return Pubkey.from_string("HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL")
            
            # Try multiple derivation patterns
            patterns = [
                [b"creator", bytes(token_mint)],
                [b"creator_vault", bytes(token_mint)],
                [bytes(token_mint), b"creator"],
                [bytes(token_mint), b"creator_vault"]
            ]
            
            for seeds in patterns:
                try:
                    creator_vault, _ = Pubkey.find_program_address(seeds, self.PUMP_PROGRAM)
                    if await self.validate_creator_vault(creator_vault):
                        logger.info(f"✅ Found valid creator vault: {creator_vault}")
                        return creator_vault
                except Exception:
                    continue
            
            return self.CREATOR_VAULT
            
        except Exception as e:
            logger.error(f"Error getting optimal creator vault: {e}")
            return self.CREATOR_VAULT

    async def validate_creator_vault(self, creator_vault: Pubkey) -> bool:
        """Validate if a creator vault exists on-chain"""
        try:
            response = await self.client.get_account_info(creator_vault)
            return response.value is not None
        except Exception:
            return False

    async def close(self):
        """Close the client connection"""
        await self.client.close()

"""""
To use it in your copy bot, you would:

from pumpfun_trade_executor import PumpFunTradeExecutor, TradeConfig

# Initialize the executor
executor = PumpFunTradeExecutor(
    wallet_keypair=your_wallet,
    rpc_url=your_rpc_url,
    config=TradeConfig(
        sol_amount=0.005,  # Customize these values
        slippage_tolerance=0.10,
        max_retries=1,
        confirmation_timeout=10.0
    )
)

# Execute a buy trade
buy_result = await executor.execute_buy_trade(
    token_mint=detected_token_mint,
    bonding_curve=detected_bonding_curve,
    bonding_curve_ata=detected_curve_ata,
    sol_amount=detected_sol_amount
)

# If buy successful, execute sell after your desired delay
if buy_result.result == TradeResult.SUCCESS:
    sell_result = await executor.execute_sell_trade(
        token_mint=detected_token_mint,
        bonding_curve=detected_bonding_curve,
        bonding_curve_ata=detected_curve_ata,
        token_amount=buy_result.tokens_amount
    )
    
    """