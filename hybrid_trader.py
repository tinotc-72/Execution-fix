#!/usr/bin/env python3
"""
Hybrid Trading Module for Copy Bots
====================================

This module provides a clean, reusable trader class that implements:
1. CLMM first execution (fastest, lowest fees)
2. Jupiter API fallback (maximum reliability)
3. Official Solana transaction confirmation
4. Proper error handling and logging

Usage in Copy Bot:
-----------------
from hybrid_trader import HybridTrader

# Initialize trader
trader = HybridTrader()

# Execute buy trade
buy_signature = await trader.buy_token(
    input_mint="So11111111111111111111111111111111111111112",  # SOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount_sol=0.01
)

# Execute sell trade
sell_signature = await trader.sell_token(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount_usdc=1.5
)

# Close connection when done
await trader.close()
"""

import asyncio
import json
import aiohttp
import base64
import base58
import os
import logging
from typing import Optional, Dict, Any
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed, Finalized, Processed
from solders.signature import Signature
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridTrader:
    """
    Hybrid trader that tries CLMM first, then falls back to Jupiter
    Perfect for copy bots that need maximum reliability with optimal performance
    """
    
    def __init__(self, enable_clmm: bool = True, slippage_bps: int = 300):
        """
        Initialize the hybrid trader
        
        Args:
            enable_clmm: Whether to attempt CLMM trades (set False to use Jupiter only)
            slippage_bps: Slippage tolerance in basis points (300 = 3%)
        """
        # Load environment
        self.env = EnvKeys()
        self.client = AsyncClient(self.env.HELIUS_RPC_URL)
        
        # Configuration
        self.enable_clmm = enable_clmm
        self.slippage_bps = slippage_bps
        
        # Common token mints
        self.sol_mint = "So11111111111111111111111111111111111111112"
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        self.clmm_program_id = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
        
        # Load wallet
        self._load_wallet()
        
        logger.info(f"🚀 Hybrid Trader initialized")
        logger.info(f"   Wallet: {self.wallet_pubkey}")
        logger.info(f"   CLMM Enabled: {self.enable_clmm}")
        logger.info(f"   Slippage: {self.slippage_bps/100}%")
    
    def _load_wallet(self):
        """Load wallet from environment"""
        try:
            private_key_b58 = os.getenv('PHANTOM_PRIVATE_KEY')
            if not private_key_b58:
                raise ValueError("PHANTOM_PRIVATE_KEY not found in .env file")
            
            decoded_key = base58.b58decode(private_key_b58)
            self.wallet_keypair = Keypair.from_bytes(decoded_key)
            self.wallet_pubkey = self.wallet_keypair.pubkey()
            
        except Exception as e:
            logger.error(f"❌ Could not load wallet: {e}")
            raise
    
    async def confirm_transaction(self, signature: str, max_retries: int = 30) -> bool:
        """
        Confirm transaction using official Solana documentation method
        """
        try:
            logger.info(f"📋 Confirming transaction: {signature}")
            signature_obj = Signature.from_string(signature)
            
            for attempt in range(max_retries):
                try:
                    # Use getSignatureStatuses as recommended by official docs
                    statuses = await self.client.get_signature_statuses([signature_obj])
                    
                    if statuses.value and statuses.value[0]:
                        status = statuses.value[0]
                        
                        if status.err:
                            logger.error(f"❌ Transaction failed: {status.err}")
                            return False
                        
                        if status.confirmation_status:
                            confirmation_status = str(status.confirmation_status)
                            
                            # Accept both confirmed and finalized status
                            if ("confirmed" in confirmation_status.lower() or 
                                "finalized" in confirmation_status.lower()):
                                logger.info(f"✅ Transaction confirmed: {confirmation_status}")
                                return True
                    
                    # Wait before next attempt
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Confirmation attempt {attempt + 1} error: {e}")
                    await asyncio.sleep(2)
            
            logger.error(f"❌ Transaction confirmation timeout after {max_retries} attempts")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error confirming transaction: {e}")
            return False
    
    async def get_token_balance(self, mint_address: str) -> float:
        """Get balance for a specific token mint"""
        try:
            if mint_address == self.sol_mint:
                # SOL balance
                balance = await self.client.get_balance(self.wallet_pubkey)
                return balance.value / 1_000_000_000 if balance.value else 0.0
            else:
                # SPL token balance
                token_ata = get_associated_token_address(
                    self.wallet_pubkey, 
                    Pubkey.from_string(mint_address)
                )
                try:
                    balance = await self.client.get_token_account_balance(token_ata)
                    # Most tokens use 6 decimals, but this could be made dynamic
                    return float(balance.value.amount) / 1_000_000 if balance.value else 0.0
                except:
                    return 0.0
                    
        except Exception as e:
            logger.error(f"❌ Error getting token balance: {e}")
            return 0.0
    
    async def ensure_token_account(self, mint_address: str) -> bool:
        """Ensure token account exists for the given mint"""
        try:
            if mint_address == self.sol_mint:
                return True  # SOL account always exists
            
            token_ata = get_associated_token_address(
                self.wallet_pubkey, 
                Pubkey.from_string(mint_address)
            )
            
            # Check if account exists
            account_info = await self.client.get_account_info(token_ata)
            if account_info.value:
                return True
            
            # Create token account
            logger.info(f"🏦 Creating token account for {mint_address}")
            create_ix = create_associated_token_account(
                self.wallet_pubkey,
                self.wallet_pubkey,
                Pubkey.from_string(mint_address)
            )
            
            # Build and send transaction
            recent_blockhash = await self.client.get_latest_blockhash()
            tx = VersionedTransaction(
                MessageV0.try_compile(
                    self.wallet_pubkey,
                    [create_ix],
                    [],
                    recent_blockhash.value.blockhash
                )
            )
            tx.sign([self.wallet_keypair])
            
            response = await self.client.send_transaction(tx)
            signature = str(response.value)
            
            if await self.confirm_transaction(signature):
                logger.info("✅ Token account created successfully")
                return True
            else:
                logger.error("❌ Failed to create token account")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ensuring token account: {e}")
            return False
    
    async def execute_clmm_trade(self, input_mint: str, output_mint: str, amount: float) -> Optional[str]:
        """
        Execute CLMM trade directly
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address  
            amount: Amount to trade
            
        Returns:
            Transaction signature if successful, None if failed
        """
        try:
            logger.info(f"🔄 Attempting direct CLMM trade")
            logger.info(f"   Input: {input_mint}")
            logger.info(f"   Output: {output_mint}")
            logger.info(f"   Amount: {amount}")
            
            # TODO: Implement actual CLMM swap_v2 instruction building
            # This would require:
            # 1. Finding the correct CLMM pool for the token pair
            # 2. Building swap_v2 instruction with proper accounts
            # 3. Calculating price impact and slippage
            # 4. Handling observation account initialization if needed
            
            # For now, simulate failure to demonstrate fallback
            raise Exception("CLMM implementation not yet complete - falling back to Jupiter")
            
        except Exception as e:
            logger.warning(f"❌ CLMM trade failed: {e}")
            return None
    
    async def execute_jupiter_trade(self, input_mint: str, output_mint: str, amount: float, amount_type: str = "input") -> Optional[str]:
        """
        Execute trade via Jupiter API
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to trade
            amount_type: "input" or "output" - whether amount refers to input or output token
            
        Returns:
            Transaction signature if successful, None if failed
        """
        try:
            logger.info(f"🚀 Jupiter trade: {amount} {amount_type}")
            
            # Convert amount to correct decimals
            if input_mint == self.sol_mint:
                amount_units = int(amount * 1_000_000_000)  # SOL has 9 decimals
            else:
                amount_units = int(amount * 1_000_000)  # Most tokens have 6 decimals
            
            async with aiohttp.ClientSession() as session:
                # Get quote from Jupiter
                quote_url = "https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(amount_units),
                    "slippageBps": str(self.slippage_bps)
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        logger.error(f"❌ Jupiter quote failed: {response.status}")
                        return None
                    
                    quote_data = await response.json()
                    
                    if 'outAmount' not in quote_data:
                        logger.error(f"❌ Invalid quote response: {quote_data}")
                        return None
                    
                    logger.info(f"   Quote: {quote_data['outAmount']} output tokens")
                    
                    # Get swap transaction
                    swap_url = "https://quote-api.jup.ag/v6/swap"
                    swap_data = {
                        "quoteResponse": quote_data,
                        "userPublicKey": str(self.wallet_pubkey),
                        "wrapAndUnwrapSol": True,
                        "dynamicComputeUnitLimit": True,
                        "prioritizationFeeLamports": 1000000
                    }
                    
                    async with session.post(swap_url, json=swap_data) as swap_response:
                        if swap_response.status != 200:
                            logger.error(f"❌ Jupiter swap failed: {swap_response.status}")
                            return None
                        
                        swap_result = await swap_response.json()
                        
                        if "swapTransaction" not in swap_result:
                            logger.error(f"❌ No swap transaction in response")
                            return None
                        
                        # Decode and sign transaction
                        tx_bytes = base64.b64decode(swap_result["swapTransaction"])
                        tx = VersionedTransaction.from_bytes(tx_bytes)
                        tx = VersionedTransaction(tx.message, [self.wallet_keypair])
                        
                        # Send transaction
                        logger.info(f"📡 Sending Jupiter transaction...")
                        response = await self.client.send_transaction(tx)
                        
                        if response.value:
                            signature = str(response.value)
                            logger.info(f"✅ Jupiter transaction sent: {signature}")
                            
                            # Confirm transaction
                            if await self.confirm_transaction(signature):
                                logger.info(f"✅ Jupiter trade confirmed!")
                                return signature
                            else:
                                logger.error(f"❌ Jupiter trade confirmation failed")
                                return None
                        else:
                            logger.error(f"❌ Failed to send Jupiter transaction")
                            return None
                            
        except Exception as e:
            logger.error(f"❌ Jupiter trade error: {e}")
            return None
    
    async def buy_token(self, input_mint: str, output_mint: str, amount_sol: float) -> Optional[str]:
        """
        Buy token using hybrid approach (CLMM first, Jupiter fallback)
        
        Args:
            input_mint: Input token mint (usually SOL)
            output_mint: Output token mint (token to buy)
            amount_sol: Amount of SOL to spend
            
        Returns:
            Transaction signature if successful, None if failed
        """
        logger.info(f"🛒 HYBRID BUY: {amount_sol} SOL worth of token")
        logger.info(f"   From: {input_mint}")
        logger.info(f"   To: {output_mint}")
        
        # Ensure output token account exists
        if not await self.ensure_token_account(output_mint):
            logger.error("❌ Failed to ensure output token account")
            return None
        
        # Method 1: Try CLMM first (if enabled)
        if self.enable_clmm:
            logger.info("1️⃣ Attempting CLMM trade...")
            clmm_signature = await self.execute_clmm_trade(input_mint, output_mint, amount_sol)
            if clmm_signature:
                logger.info(f"✅ CLMM buy successful: {clmm_signature}")
                return clmm_signature
        
        # Method 2: Fallback to Jupiter
        logger.info("2️⃣ Using Jupiter API...")
        jupiter_signature = await self.execute_jupiter_trade(input_mint, output_mint, amount_sol)
        if jupiter_signature:
            logger.info(f"✅ Jupiter buy successful: {jupiter_signature}")
            return jupiter_signature
        
        logger.error("❌ Both CLMM and Jupiter failed")
        return None
    
    async def sell_token(self, input_mint: str, output_mint: str, amount_tokens: float = None) -> Optional[str]:
        """
        Sell token using hybrid approach (CLMM first, Jupiter fallback)
        
        Args:
            input_mint: Input token mint (token to sell)
            output_mint: Output token mint (usually SOL)
            amount_tokens: Amount of tokens to sell (if None, sells 95% of balance)
            
        Returns:
            Transaction signature if successful, None if failed
        """
        # Auto-detect amount if not specified
        if amount_tokens is None:
            current_balance = await self.get_token_balance(input_mint)
            amount_tokens = current_balance * 0.95  # Use 95% to account for fees
        
        logger.info(f"💰 HYBRID SELL: {amount_tokens:.6f} tokens")
        logger.info(f"   From: {input_mint}")
        logger.info(f"   To: {output_mint}")
        
        # Method 1: Try CLMM first (if enabled)
        if self.enable_clmm:
            logger.info("1️⃣ Attempting CLMM trade...")
            clmm_signature = await self.execute_clmm_trade(input_mint, output_mint, amount_tokens)
            if clmm_signature:
                logger.info(f"✅ CLMM sell successful: {clmm_signature}")
                return clmm_signature
        
        # Method 2: Fallback to Jupiter
        logger.info("2️⃣ Using Jupiter API...")
        jupiter_signature = await self.execute_jupiter_trade(input_mint, output_mint, amount_tokens)
        if jupiter_signature:
            logger.info(f"✅ Jupiter sell successful: {jupiter_signature}")
            return jupiter_signature
        
        logger.error("❌ Both CLMM and Jupiter failed")
        return None
    
    async def copy_trade(self, token_mint: str, action: str, amount: float) -> Optional[str]:
        """
        Execute a copy trade (buy or sell)
        
        Args:
            token_mint: The token to trade
            action: "buy" or "sell"
            amount: Amount to trade (SOL for buy, tokens for sell)
            
        Returns:
            Transaction signature if successful, None if failed
        """
        try:
            if action.lower() == "buy":
                return await self.buy_token(self.sol_mint, token_mint, amount)
            elif action.lower() == "sell":
                return await self.sell_token(token_mint, self.sol_mint, amount)
            else:
                logger.error(f"❌ Invalid action: {action}. Use 'buy' or 'sell'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Copy trade error: {e}")
            return None
    
    async def close(self):
        """Close the RPC client connection"""
        try:
            await self.client.close()
            logger.info("🔌 RPC connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing connection: {e}")

# Example usage function
async def example_usage():
    """Example of how to use the HybridTrader in a copy bot"""
    
    # Initialize trader
    trader = HybridTrader(enable_clmm=True, slippage_bps=300)
    
    try:
        # Example: Buy USDC with SOL
        print("\n💰 Example: Buy USDC with 0.01 SOL")
        buy_signature = await trader.buy_token(
            input_mint=trader.sol_mint,      # SOL
            output_mint=trader.usdc_mint,    # USDC
            amount_sol=0.01
        )
        
        if buy_signature:
            print(f"✅ Buy successful: {buy_signature}")
            
            # Wait a moment
            await asyncio.sleep(3)
            
            # Example: Sell all USDC back to SOL
            print("\n💰 Example: Sell USDC back to SOL")
            sell_signature = await trader.sell_token(
                input_mint=trader.usdc_mint,     # USDC
                output_mint=trader.sol_mint,     # SOL
                amount_tokens=None               # Auto-detect amount
            )
            
            if sell_signature:
                print(f"✅ Sell successful: {sell_signature}")
            else:
                print("❌ Sell failed")
        else:
            print("❌ Buy failed")
            
    finally:
        # Always close connection
        await trader.close()

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
