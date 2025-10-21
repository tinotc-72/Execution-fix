"""
Jupiter Aggregator Trading Implementation
========================================

This module implements trading via Jupiter aggregator API.
Jupiter provides best price routing across multiple DEXs including Raydium.

API: https://quote-api.jup.ag/v6/
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

import asyncio
import logging
from typing import Optional, Tuple, Dict, Any
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
import httpx
import json
import base64
import time

logger = logging.getLogger(__name__)

# Constants
LAMPORTS_PER_SOL = 1_000_000_000
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

# Jupiter API endpoints
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"
JUPITER_PRICE_API = "https://price.jup.ag/v4/price"

class JupiterTrader:
    """Jupiter aggregator trading implementation"""
    
    def __init__(self, client: AsyncClient, wallet_keypair: Keypair):
        self.client = client
        self.wallet_keypair = wallet_keypair
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
        
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Get quote from Jupiter API"""
        try:
            start_time = time.time()
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(slippage_bps),
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            logger.info(f"🔍 Getting Jupiter quote: {amount} {input_mint[:8]}... -> {output_mint[:8]}...")
            
            response = await self.http_client.get(JUPITER_QUOTE_API, params=params)
            response.raise_for_status()
            
            quote_data = response.json()
            
            # Log quote details
            quote_time = time.time() - start_time
            input_amount = int(quote_data["inAmount"])
            output_amount = int(quote_data["outAmount"])
            
            logger.info(f"✅ Quote received in {quote_time:.3f}s:")
            logger.info(f"   Input: {input_amount}")
            logger.info(f"   Output: {output_amount}")
            logger.info(f"   Route: {' -> '.join([r['swapInfo']['label'] for r in quote_data.get('routePlan', [])])}")
            
            return quote_data
            
        except Exception as e:
            logger.error(f"❌ Error getting Jupiter quote: {e}")
            return None
            
    async def get_swap_transaction(
        self,
        quote_data: Dict[str, Any],
        user_public_key: str,
        wrap_unwrap_sol: bool = True
    ) -> Optional[VersionedTransaction]:
        """Get swap transaction from Jupiter API"""
        try:
            start_time = time.time()
            
            payload = {
                "quoteResponse": quote_data,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": wrap_unwrap_sol,
                "useSharedAccounts": True,
                "feeAccount": None,
                "trackingAccount": None,
                "asLegacyTransaction": False
            }
            
            logger.info("🔄 Getting swap transaction from Jupiter...")
            
            response = await self.http_client.post(
                JUPITER_SWAP_API,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            swap_data = response.json()
            
            # Decode transaction
            tx_data = swap_data["swapTransaction"]
            tx_bytes = base64.b64decode(tx_data)
            
            # Parse versioned transaction
            tx = VersionedTransaction.from_bytes(tx_bytes)
            
            # Check if transaction needs signing (Jupiter returns unsigned transaction)
            needs_signing = str(tx.signatures[0]) == "1111111111111111111111111111111111111111111111111111111111111111"
            
            swap_time = time.time() - start_time
            logger.info(f"✅ Swap transaction received in {swap_time:.3f}s")
            logger.info(f"📝 Transaction has {len(tx.signatures)} signatures")
            logger.info(f"🔐 Needs signing: {needs_signing}")
            
            return tx
            
        except Exception as e:
            logger.error(f"❌ Error getting swap transaction: {e}")
            return None
            
    async def execute_jupiter_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 100
    ) -> BuildResult:
        """Execute a complete Jupiter swap using PR-02 transaction patterns"""
        try:
            start_time = time.time()
            
            # Get quote
            quote_data = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
            if not quote_data:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="swap",
                    reason="Failed to get quote"
                )
                
            # Get swap transaction
            tx = await self.get_swap_transaction(
                quote_data,
                str(self.wallet_keypair.pubkey()),
                wrap_unwrap_sol=True
            )
            
            if not tx:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="swap",
                    reason="Failed to get swap transaction"
                )
            
            # Apply PR-02 transaction patterns
            logger.info("� Applying PR-02 transaction patterns...")
            
            # 1. Add compute budget
            budget_ixs = with_compute_budget()
            
            # 2. Ensure ATA instructions
            ata_ixs = await ensure_ata_ixs(
                self.wallet_keypair.pubkey(),
                [Pubkey.from_string(input_mint), Pubkey.from_string(output_mint)]
            )
            
            # 3. Combine all instructions
            all_instructions = budget_ixs + ata_ixs + list(tx.message.instructions)
            
            # 4. Build ALTs from tables
            recent_blockhash = await get_recent_blockhash()
            alts = await build_alts_from_tables(tx.message.address_table_lookups)
            
            # 5. Compile MessageV0
            try:
                final_message = MessageV0.try_compile(
                    payer=self.wallet_keypair.pubkey(),
                    instructions=all_instructions,
                    address_lookup_table_accounts=alts,
                    recent_blockhash=recent_blockhash
                )
            except Exception as compile_error:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="swap",
                    reason=f"Failed to compile MessageV0: {compile_error}"
                )
            
            # 6. Create VersionedTransaction
            final_tx = VersionedTransaction(final_message, [])
            
            # 7. Send and confirm using PR-02 patterns
            result = await send_and_confirm_v0_tx(
                final_tx,
                [self.wallet_keypair],
                commitment="confirmed"
            )
            
            # 8. Log result
            log_submit_result(result, "jupiter_swap")
            
            if result.ok:
                total_time = time.time() - start_time
                output_amount = int(quote_data["outAmount"])
                
                logger.info(f"✅ Jupiter swap successful in {total_time:.3f}s")
                logger.info(f"   Output: {output_amount}")
                
                return BuildResult(
                    ok=True,
                    tx=result.tx,
                    dex="jupiter",
                    action="swap",
                    reason=f"Swap successful in {total_time:.3f}s"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="swap",
                    reason=result.reason or "Transaction failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Jupiter swap execution failed: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="jupiter",
                action="swap",
                reason=str(e)
            )
            
    async def execute_buy(self, amount: int, target_mint: str = str(USDC_MINT)) -> BuildResult:
        """Execute a buy trade (SOL -> Token)"""
        try:
            logger.info(f"🔄 Executing Jupiter buy: {amount/LAMPORTS_PER_SOL:.6f} SOL -> {target_mint[:8]}...")
            
            result = await self.execute_jupiter_swap(
                input_mint=str(NATIVE_MINT),
                output_mint=target_mint,
                amount=amount,
                slippage_bps=100  # 1% slippage
            )
            
            if result.ok:
                logger.info(f"✅ Jupiter buy successful")
                return BuildResult(
                    ok=True,
                    tx=result.tx,
                    dex="jupiter",
                    action="buy",
                    reason="Buy successful"
                )
            else:
                logger.error("❌ Jupiter buy failed")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="buy",
                    reason=result.reason or "Buy failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Jupiter buy execution failed: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="jupiter",
                action="buy",
                reason=str(e)
            )
            
    async def execute_sell(self, amount: int, source_mint: str = str(USDC_MINT)) -> BuildResult:
        """Execute a sell trade (Token -> SOL)"""
        try:
            logger.info(f"🔄 Executing Jupiter sell: {amount} {source_mint[:8]}... -> SOL")
            
            result = await self.execute_jupiter_swap(
                input_mint=source_mint,
                output_mint=str(NATIVE_MINT),
                amount=amount,
                slippage_bps=100  # 1% slippage
            )
            
            if result.ok:
                logger.info(f"✅ Jupiter sell successful")
                return BuildResult(
                    ok=True,
                    tx=result.tx,
                    dex="jupiter",
                    action="sell",
                    reason="Sell successful"
                )
            else:
                logger.error("❌ Jupiter sell failed")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="sell",
                    reason=result.reason or "Sell failed"
                )
                
        except Exception as e:
            logger.error(f"❌ Jupiter sell execution failed: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="jupiter",
                action="sell",
                reason=str(e)
            )
            
    async def get_token_price(self, mint: str) -> Optional[float]:
        """Get token price from Jupiter API"""
        try:
            params = {"ids": mint}
            response = await self.http_client.get(JUPITER_PRICE_API, params=params)
            response.raise_for_status()
            
            price_data = response.json()
            
            if "data" in price_data and mint in price_data["data"]:
                price = price_data["data"][mint]["price"]
                logger.info(f"💰 Price for {mint[:8]}...: ${price}")
                return float(price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting token price: {e}")
            return None
            
    async def get_supported_tokens(self) -> Optional[list]:
        """Get list of supported tokens"""
        try:
            response = await self.http_client.get("https://token.jup.ag/strict")
            response.raise_for_status()
            
            tokens = response.json()
            logger.info(f"📋 Jupiter supports {len(tokens)} tokens")
            
            return tokens
            
        except Exception as e:
            logger.error(f"Error getting supported tokens: {e}")
            return None
            
    async def simulate_trade(
        self,
        input_mint: str,
        output_mint: str,
        amount: int
    ) -> Optional[Dict[str, Any]]:
        """Simulate a trade without executing"""
        try:
            quote_data = await self.get_quote(input_mint, output_mint, amount)
            
            if quote_data:
                return {
                    "input_amount": int(quote_data["inAmount"]),
                    "output_amount": int(quote_data["outAmount"]),
                    "price_impact": float(quote_data.get("priceImpactPct", 0)),
                    "routes": [r["swapInfo"]["label"] for r in quote_data.get("routePlan", [])],
                    "market_infos": quote_data.get("marketInfos", [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return None

# Example usage
async def test_jupiter_trading():
    """Test Jupiter trading"""
    from env_keys import load_wallet_from_private_key, validate_env_vars
    
    # Load environment
    env_vars = validate_env_vars()
    wallet_keypair = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
    
    async with AsyncClient(env_vars["RPC_URL"]) as client:
        async with JupiterTrader(client, wallet_keypair) as trader:
            
            # Test quote
            quote = await trader.get_quote(
                input_mint=str(NATIVE_MINT),
                output_mint=str(USDC_MINT),
                amount=1_000_000,  # 0.001 SOL
                slippage_bps=100
            )
            
            if quote:
                logger.info("✅ Jupiter quote successful")
                
                # Simulate trade
                simulation = await trader.simulate_trade(
                    str(NATIVE_MINT),
                    str(USDC_MINT),
                    1_000_000
                )
                
                if simulation:
                    logger.info(f"📊 Trade simulation:")
                    logger.info(f"   Input: {simulation['input_amount']}")
                    logger.info(f"   Output: {simulation['output_amount']}")
                    logger.info(f"   Price Impact: {simulation['price_impact']:.4f}%")
                    logger.info(f"   Routes: {', '.join(simulation['routes'])}")
                
                # Execute buy
                buy_success, token_amount = await trader.execute_buy(1_000_000)
                
                if buy_success:
                    # Hold for 5 seconds
                    await asyncio.sleep(5)
                    
                    # Execute sell
                    sell_success, sol_amount = await trader.execute_sell(token_amount)
                    
                    if sell_success:
                        logger.info(f"✅ Jupiter complete cycle successful")
                        logger.info(f"   Net result: {(sol_amount - 1_000_000)/LAMPORTS_PER_SOL:.6f} SOL")
                    else:
                        logger.error("❌ Jupiter sell failed")
                else:
                    logger.error("❌ Jupiter buy failed")
            else:
                logger.error("❌ Jupiter quote failed")

if __name__ == "__main__":
    asyncio.run(test_jupiter_trading())
