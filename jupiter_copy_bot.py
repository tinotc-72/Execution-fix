"""
Jupiter Trade Executor - Execute trades through Jupiter aggregator
Takes extracted trade information and executes the same transaction with your wallet
"""

import asyncio
import base64
import struct
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import requests
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed, Confirmed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Jupiter API endpoints
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# Program IDs
JUPITER_PROGRAM = Pubkey.from_string("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

class TradeResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class TradeConfig:
    """Configuration for trade execution"""
    slippage_tolerance: float = 0.05  # 5% slippage tolerance
    max_retries: int = 2
    retry_delay: float = 0.5
    confirmation_timeout: float = 30.0

@dataclass
class JupiterTradeInfo:
    """Information needed to execute a Jupiter trade"""
    input_mint: Pubkey
    output_mint: Pubkey
    amount_in: int
    is_buy: bool  # True if SOL->Token, False if Token->SOL

class JupiterTradeExecutor:
    """
    Jupiter Copy Bot - Copy trades executed through Jupiter aggregator
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CopyTradeConfig = None):
        self.wallet = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        self.config = config or CopyTradeConfig()
        
        # Track copied trades to avoid duplicates
        self.copied_signatures = set()
        self.copied_tokens = set()
        self.daily_copy_count = 0
        
        logger.info(f"🤖 Jupiter Copy Bot initialized for wallet: {self.wallet_pubkey}")
    
    async def detect_jupiter_trade(self, transaction_signature: str) -> Optional[DetectedTrade]:
        """
        Detect if a transaction is a Jupiter trade and extract trade details
        """
        try:
            # Get transaction details
            tx_info = await self.client.get_transaction(
                Signature.from_string(transaction_signature), 
                max_supported_transaction_version=0
            )
            
            if not tx_info or not tx_info.value:
                return None
            
            transaction = tx_info.value
            
            # Check if transaction contains Jupiter program
            if not self._contains_jupiter_program(transaction):
                return None
            
            # Extract trade details
            trade_details = self._extract_trade_details(transaction)
            if not trade_details:
                return None
            
            # Get wallet address from transaction
            wallet_address = self._get_transaction_wallet(transaction)
            
            return DetectedTrade(
                signature=transaction_signature,
                wallet_address=wallet_address,
                input_mint=trade_details['input_mint'],
                output_mint=trade_details['output_mint'],
                amount_in=trade_details['amount_in'],
                amount_out=trade_details['amount_out'],
                is_buy=trade_details['is_buy'],
                timestamp=datetime.now(),
                program_id=JUPITER_PROGRAM
            )
            
        except Exception as e:
            logger.error(f"❌ Error detecting Jupiter trade {transaction_signature}: {e}")
            return None
    
    def _contains_jupiter_program(self, transaction) -> bool:
        """Check if transaction contains Jupiter program interactions"""
        try:
            if hasattr(transaction, 'transaction'):
                instructions = transaction.transaction.message.instructions
                for instruction in instructions:
                    if str(instruction.program_id) == str(JUPITER_PROGRAM):
                        return True
            return False
        except Exception:
            return False
    
    def _extract_trade_details(self, transaction) -> Optional[Dict]:
        """Extract trade details from Jupiter transaction"""
        try:
            # Analyze token balance changes to determine trade direction and amounts
            pre_balances = getattr(transaction.meta, 'pre_token_balances', [])
            post_balances = getattr(transaction.meta, 'post_token_balances', [])
            
            # Find the significant balance changes
            balance_changes = self._analyze_balance_changes(pre_balances, post_balances)
            
            if len(balance_changes) < 2:
                return None
            
            # Determine input and output based on balance changes
            input_change = None
            output_change = None
            
            for change in balance_changes:
                if change['change'] < 0:  # Decreased balance (input)
                    input_change = change
                elif change['change'] > 0:  # Increased balance (output)
                    output_change = change
            
            if not input_change or not output_change:
                return None
            
            # Determine if this is a buy (SOL->Token) or sell (Token->SOL)
            is_buy = str(input_change['mint']) == str(SOL_MINT)
            
            return {
                'input_mint': Pubkey.from_string(input_change['mint']),
                'output_mint': Pubkey.from_string(output_change['mint']),
                'amount_in': abs(input_change['change']),
                'amount_out': abs(output_change['change']),
                'is_buy': is_buy
            }
            
        except Exception as e:
            logger.error(f"Error extracting trade details: {e}")
            return None
    
    def _analyze_balance_changes(self, pre_balances: List, post_balances: List) -> List[Dict]:
        """Analyze token balance changes to determine trade amounts"""
        try:
            balance_changes = []
            
            # Create lookup for pre-balances
            pre_lookup = {}
            for balance in pre_balances:
                key = f"{balance.get('owner', '')}-{balance.get('mint', '')}"
                pre_lookup[key] = int(balance.get('uiTokenAmount', {}).get('amount', 0))
            
            # Calculate changes
            for post_balance in post_balances:
                key = f"{post_balance.get('owner', '')}-{post_balance.get('mint', '')}"
                post_amount = int(post_balance.get('uiTokenAmount', {}).get('amount', 0))
                pre_amount = pre_lookup.get(key, 0)
                
                change = post_amount - pre_amount
                if abs(change) > 1000:  # Only significant changes
                    balance_changes.append({
                        'mint': post_balance.get('mint'),
                        'owner': post_balance.get('owner'),
                        'change': change,
                        'pre_amount': pre_amount,
                        'post_amount': post_amount
                    })
            
            return balance_changes
            
        except Exception as e:
            logger.error(f"Error analyzing balance changes: {e}")
            return []
    
    def _get_transaction_wallet(self, transaction) -> Pubkey:
        """Extract the wallet address from transaction"""
        try:
            if hasattr(transaction, 'transaction'):
                message = transaction.transaction.message
                if hasattr(message, 'account_keys') and message.account_keys:
                    # First account is usually the fee payer/wallet
                    return message.account_keys[0]
            return None
        except Exception:
            return None
    
    async def should_copy_trade(self, detected_trade: DetectedTrade) -> bool:
        """
        Determine if a detected trade should be copied based on filters and risk management
        """
        try:
            # Check if already copied
            if detected_trade.signature in self.copied_signatures:
                logger.debug(f"Trade already copied: {detected_trade.signature}")
                return False
            
            # Check daily copy limit
            if self.daily_copy_count >= self.config.max_tokens_to_copy:
                logger.info(f"Daily copy limit reached: {self.daily_copy_count}")
                return False
            
            # Check if token already copied
            target_mint = detected_trade.output_mint if detected_trade.is_buy else detected_trade.input_mint
            if target_mint in self.copied_tokens:
                logger.debug(f"Token already copied: {target_mint}")
                return False
            
            # Check minimum trade size
            if detected_trade.is_buy:
                sol_amount = detected_trade.amount_in / 1_000_000_000
                if sol_amount < self.config.min_copy_amount_sol:
                    logger.debug(f"Trade too small: {sol_amount} SOL")
                    return False
            
            # Check if it's a reasonable trade (not too large)
            if detected_trade.is_buy:
                sol_amount = detected_trade.amount_in / 1_000_000_000
                if sol_amount > self.config.max_copy_amount_sol * 10:  # 10x max copy as filter
                    logger.debug(f"Trade too large: {sol_amount} SOL")
                    return False
            
            logger.info(f"✅ Trade approved for copying: {detected_trade.signature}")
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating trade: {e}")
            return False
    
    def _calculate_copy_amount(self, detected_trade: DetectedTrade) -> float:
        """Calculate the amount to copy based on original trade size"""
        try:
            if detected_trade.is_buy:
                original_sol = detected_trade.amount_in / 1_000_000_000
                copy_amount = original_sol * self.config.copy_percentage
                
                # Apply limits
                copy_amount = max(copy_amount, self.config.min_copy_amount_sol)
                copy_amount = min(copy_amount, self.config.max_copy_amount_sol)
                
                return copy_amount
            else:
                # For sells, we'll sell a percentage of our holdings
                return 0.0  # Will be calculated based on our token balance
                
        except Exception as e:
            logger.error(f"Error calculating copy amount: {e}")
            return self.config.min_copy_amount_sol
    
    async def get_jupiter_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[Dict]:
        """Get Jupiter quote for a trade"""
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(int(self.config.slippage_tolerance * 10000)),
                "onlyDirectRoutes": "false",
                "maxAccounts": "20"
            }
            
            response = requests.get(JUPITER_QUOTE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            quote = response.json()
            if "inAmount" not in quote or "outAmount" not in quote:
                logger.error(f"Invalid Jupiter quote: {quote}")
                return None
            
            return quote
            
        except Exception as e:
            logger.error(f"Error getting Jupiter quote: {e}")
            return None
    
    async def get_jupiter_swap_transaction(self, quote: Dict) -> Optional[VersionedTransaction]:
        """Get Jupiter swap transaction from quote"""
        try:
            body = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet_pubkey),
                "wrapAndUnwrapSol": True,
                "useSharedAccounts": True,
                "asLegacyTransaction": False,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": 1000
            }
            
            response = requests.post(JUPITER_SWAP_URL, json=body, timeout=10)
            response.raise_for_status()
            
            tx_data = response.json()
            
            # Extract transaction data
            swap_tx_b64 = None
            if "swapTransaction" in tx_data:
                swap_tx_b64 = tx_data["swapTransaction"]
            elif "transaction" in tx_data:
                swap_tx_b64 = tx_data["transaction"]
            
            if not swap_tx_b64:
                logger.error(f"No transaction in Jupiter response: {tx_data}")
                return None
            
            # Decode transaction
            tx = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
            return tx
            
        except Exception as e:
            logger.error(f"Error getting Jupiter swap transaction: {e}")
            return None
    
    async def ensure_token_account(self, token_mint: Pubkey) -> bool:
        """Ensure token account exists for the mint"""
        try:
            ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Check if exists
            account_info = await self.client.get_account_info(ata)
            if account_info.value:
                return True
            
            # Create ATA
            logger.info(f"📝 Creating ATA for {token_mint}")
            create_ata_ix = create_associated_token_account(
                payer=self.wallet_pubkey,
                owner=self.wallet_pubkey,
                mint=token_mint
            )
            
            # Send transaction
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[create_ata_ix],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            tx = VersionedTransaction(message, [self.wallet])
            result = await self.client.send_transaction(tx)
            
            if result.value:
                logger.info(f"✅ ATA created: {ata}")
                await asyncio.sleep(1)  # Wait for confirmation
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error ensuring token account: {e}")
            return False
    
    async def copy_buy_trade(self, detected_trade: DetectedTrade) -> Optional[str]:
        """Copy a buy trade (SOL -> Token)"""
        try:
            copy_amount = self._calculate_copy_amount(detected_trade)
            logger.info(f"🛒 Copying BUY trade: {copy_amount} SOL -> {detected_trade.output_mint}")
            
            # Ensure token account exists
            if not await self.ensure_token_account(detected_trade.output_mint):
                logger.error("Failed to create token account")
                return None
            
            # Get Jupiter quote
            amount_lamports = int(copy_amount * 1_000_000_000)
            quote = await self.get_jupiter_quote(
                str(SOL_MINT),
                str(detected_trade.output_mint),
                amount_lamports
            )
            
            if not quote:
                logger.error("Failed to get Jupiter quote")
                return None
            
            # Get swap transaction
            tx = await self.get_jupiter_swap_transaction(quote)
            if not tx:
                logger.error("Failed to get Jupiter swap transaction")
                return None
            
            # Send transaction
            signature = await self._send_transaction(tx)
            if signature:
                logger.info(f"✅ Buy trade copied: {signature}")
                self.copied_signatures.add(detected_trade.signature)
                self.copied_tokens.add(detected_trade.output_mint)
                self.daily_copy_count += 1
            
            return signature
            
        except Exception as e:
            logger.error(f"❌ Error copying buy trade: {e}")
            return None
    
    async def copy_sell_trade(self, detected_trade: DetectedTrade) -> Optional[str]:
        """Copy a sell trade (Token -> SOL)"""
        try:
            logger.info(f"💸 Copying SELL trade: {detected_trade.input_mint} -> SOL")
            
            # Get our token balance
            token_ata = get_associated_token_address(self.wallet_pubkey, detected_trade.input_mint)
            
            try:
                balance_result = await self.client.get_token_account_balance(token_ata)
                if not balance_result.value:
                    logger.warning(f"No balance found for token: {detected_trade.input_mint}")
                    return None
                
                token_balance = int(balance_result.value.amount)
                if token_balance <= 0:
                    logger.warning(f"Zero token balance for: {detected_trade.input_mint}")
                    return None
                
                # Sell a percentage of our holdings
                sell_amount = int(token_balance * self.config.copy_percentage)
                sell_amount = max(sell_amount, 1)  # At least 1 token
                
            except Exception as e:
                logger.error(f"Error getting token balance: {e}")
                return None
            
            # Get Jupiter quote
            quote = await self.get_jupiter_quote(
                str(detected_trade.input_mint),
                str(SOL_MINT),
                sell_amount
            )
            
            if not quote:
                logger.error("Failed to get Jupiter quote for sell")
                return None
            
            # Get swap transaction
            tx = await self.get_jupiter_swap_transaction(quote)
            if not tx:
                logger.error("Failed to get Jupiter swap transaction for sell")
                return None
            
            # Send transaction
            signature = await self._send_transaction(tx)
            if signature:
                logger.info(f"✅ Sell trade copied: {signature}")
                self.copied_signatures.add(detected_trade.signature)
            
            return signature
            
        except Exception as e:
            logger.error(f"❌ Error copying sell trade: {e}")
            return None
    
    async def _send_transaction(self, tx: VersionedTransaction) -> Optional[str]:
        """Send transaction with retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                # Simulate first
                sim_result = await self.client.simulate_transaction(tx)
                if sim_result.value.err:
                    logger.error(f"❌ Simulation failed: {sim_result.value.err}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    return None
                
                # Send transaction
                opts = TxOpts(
                    skip_preflight=True,
                    preflight_commitment=Processed,
                    max_retries=1
                )
                
                result = await self.client.send_transaction(tx, opts=opts)
                
                if result.value:
                    return str(result.value)
                
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    
            except Exception as e:
                logger.error(f"❌ Send attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                
        return None
    
    async def copy_detected_trade(self, detected_trade: DetectedTrade) -> CopyTradeResult:
        """
        Main method to copy a detected trade
        """
        try:
            logger.info(f"📋 Processing detected Jupiter trade: {detected_trade.signature}")
            
            # Check if should copy
            if not await self.should_copy_trade(detected_trade):
                return CopyTradeResult.SKIPPED
            
            # Copy based on trade direction
            signature = None
            if detected_trade.is_buy:
                signature = await self.copy_buy_trade(detected_trade)
            else:
                signature = await self.copy_sell_trade(detected_trade)
            
            if signature:
                logger.info(f"✅ Successfully copied trade: {signature}")
                return CopyTradeResult.SUCCESS
            else:
                logger.error(f"❌ Failed to copy trade: {detected_trade.signature}")
                return CopyTradeResult.FAILED
                
        except Exception as e:
            logger.error(f"❌ Error copying detected trade: {e}")
            return CopyTradeResult.FAILED
    
    async def process_transaction(self, transaction_signature: str) -> CopyTradeResult:
        """
        Process a transaction signature to detect and copy Jupiter trades
        """
        try:
            # Detect if this is a Jupiter trade
            detected_trade = await self.detect_jupiter_trade(transaction_signature)
            
            if not detected_trade:
                return CopyTradeResult.SKIPPED
            
            # Copy the trade
            return await self.copy_detected_trade(detected_trade)
            
        except Exception as e:
            logger.error(f"❌ Error processing transaction {transaction_signature}: {e}")
            return CopyTradeResult.FAILED
    
    async def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        try:
            # Get SOL balance
            sol_balance = await self.client.get_balance(self.wallet_pubkey)
            
            return {
                "sol_balance": sol_balance.value / 1_000_000_000 if sol_balance.value else 0,
                "copied_trades": len(self.copied_signatures),
                "copied_tokens": len(self.copied_tokens),
                "daily_copy_count": self.daily_copy_count,
                "max_daily_copies": self.config.max_tokens_to_copy
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio status: {e}")
            return {}
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()

# Example usage
async def main():
    """Example usage of Jupiter Copy Bot"""
    
    # Initialize (you would load your actual wallet and RPC)
    # wallet_keypair = load_your_wallet()
    # rpc_url = "your_rpc_url"
    
    # config = CopyTradeConfig(
    #     max_copy_amount_sol=0.01,
    #     copy_percentage=0.1,
    #     slippage_tolerance=0.05
    # )
    
    # copy_bot = JupiterCopyBot(wallet_keypair, rpc_url, config)
    
    # Process a detected transaction
    # result = await copy_bot.process_transaction("transaction_signature")
    # print(f"Copy result: {result}")
    
    # Get portfolio status
    # status = await copy_bot.get_portfolio_status()
    # print(f"Portfolio: {status}")
    
    print("🤖 Jupiter Copy Bot Ready!")
    print("Usage:")
    print("1. Initialize with your wallet and RPC")
    print("2. Call process_transaction() with detected signatures")
    print("3. Bot will detect Jupiter trades and copy them")
    print("4. Configure copy amounts and risk limits")

if __name__ == "__main__":
    asyncio.run(main())
