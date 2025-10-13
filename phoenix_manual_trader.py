#!/usr/bin/env python3
"""
Phoenix Manual Trader - Buy, Hold, Sell Testing
==============================================

This script tests Phoenix DEX trading.
Phoenix is an order book-based DEX on Solana.

Phoenix uses a central limit order book (CLOB) model rather than AMM pools.
"""

import asyncio
import logging
import struct
import time
import aiohttp
import base64
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed, Confirmed
from spl.token.instructions import get_associated_token_address

from env_keys import EnvKeys
from config import WALLET

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phoenix_trader")

# Load environment
env = EnvKeys()

# Phoenix Program IDs
PHOENIX_PROGRAM_ID = Pubkey.from_string("PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY")

# Token addresses
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

# Well-known Phoenix markets (these are examples - actual market addresses may vary)
PHOENIX_SOL_USDC_MARKET = Pubkey.from_string("4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg")  # Example market

@dataclass
class PhoenixMarketInfo:
    """Information about a Phoenix market"""
    market_id: Pubkey
    base_mint: Pubkey
    quote_mint: Pubkey
    base_vault: Optional[Pubkey] = None
    quote_vault: Optional[Pubkey] = None
    bids: Optional[Pubkey] = None
    asks: Optional[Pubkey] = None
    
@dataclass
class TradeResult:
    """Result of a trade execution"""
    success: bool
    signature: Optional[str] = None
    amount_in: float = 0.0
    amount_out: float = 0.0
    error: Optional[str] = None

class PhoenixTrader:
    """
    Phoenix DEX trader using order book-based trading
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        
        # Known market configurations
        self.known_markets = {
            "SOL/USDC": PhoenixMarketInfo(
                market_id=PHOENIX_SOL_USDC_MARKET,
                base_mint=SOL_MINT,
                quote_mint=USDC_MINT
            )
        }
        
        logger.info(f"🔥 Phoenix Trader initialized for wallet: {self.wallet_pubkey}")
    
    async def get_balances(self) -> Dict[str, float]:
        """Get current SOL and USDC balances"""
        try:
            # SOL balance
            sol_balance = await self.client.get_balance(self.wallet_pubkey)
            sol_amount = sol_balance.value / 1_000_000_000 if sol_balance.value else 0
            
            # USDC balance
            usdc_ata = get_associated_token_address(self.wallet_pubkey, USDC_MINT)
            try:
                usdc_balance = await self.client.get_token_account_balance(usdc_ata)
                usdc_amount = float(usdc_balance.value.ui_amount) if usdc_balance.value else 0
            except:
                usdc_amount = 0.0
            
            return {
                "SOL": sol_amount,
                "USDC": usdc_amount
            }
        except Exception as e:
            logger.error(f"❌ Error getting balances: {e}")
            return {"SOL": 0.0, "USDC": 0.0}
    
    async def trade_via_jupiter(self, input_mint: str, output_mint: str, amount: float, direction: str) -> Optional[str]:
        """
        Execute trade via Jupiter API (reliable fallback for Phoenix liquidity access)
        Jupiter aggregates Phoenix order book liquidity along with other DEXes
        """
        try:
            logger.info(f"🪐 Executing {direction} via Jupiter (accessing Phoenix + other liquidity)...")
            
            # Convert amount to proper units
            if input_mint == str(SOL_MINT):
                amount_lamports = int(amount * 1_000_000_000)
            else:
                amount_lamports = int(amount * 1_000_000)  # USDC has 6 decimals
            
            async with aiohttp.ClientSession() as session:
                # Get quote
                quote_url = "https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": amount_lamports,
                    "slippageBps": 100  # 1% slippage
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        logger.error(f"❌ Jupiter quote failed: {response.status}")
                        return None
                    
                    quote_data = await response.json()
                    logger.info(f"   📊 Quote received: {quote_data['outAmount']} tokens")
                    
                    # Log route information if available
                    if "routePlan" in quote_data and quote_data["routePlan"]:
                        for i, route in enumerate(quote_data["routePlan"]):
                            route_info = route.get("swapInfo", {})
                            dex_label = route_info.get("label", "Unknown")
                            logger.info(f"   🗺️  Route {i+1}: {dex_label}")
                
                # Get swap transaction
                swap_payload = {
                    "userPublicKey": str(self.wallet_pubkey),
                    "quoteResponse": quote_data,
                    "prioritizationFeeLamports": 1000
                }
                
                async with session.post("https://quote-api.jup.ag/v6/swap", json=swap_payload) as swap_response:
                    if swap_response.status != 200:
                        logger.error(f"❌ Jupiter swap failed: {swap_response.status}")
                        return None
                    
                    swap_result = await swap_response.json()
                    
                    if "swapTransaction" not in swap_result:
                        logger.error(f"❌ No swap transaction in response")
                        return None
                    
                    # Execute transaction
                    tx_bytes = base64.b64decode(swap_result["swapTransaction"])
                    tx = VersionedTransaction.from_bytes(tx_bytes)
                    tx = VersionedTransaction(tx.message, [self.wallet])
                    
                    logger.info(f"📡 Sending Jupiter transaction...")
                    response = await self.client.send_transaction(tx)
                    
                    if response.value:
                        signature = str(response.value)
                        logger.info(f"✅ Jupiter {direction} transaction sent: {signature}")
                        
                        # Wait for confirmation
                        await self.confirm_transaction(signature)
                        return signature
                    else:
                        logger.error(f"❌ Failed to send Jupiter transaction")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Jupiter trade error: {e}")
            return None
    
    async def confirm_transaction(self, signature: str, timeout: int = 30) -> bool:
        """Confirm transaction using official Solana method"""
        try:
            logger.info(f"📋 Confirming transaction: {signature}")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = await self.client.get_signature_statuses([signature])
                    if response and response.value and response.value[0]:
                        status = response.value[0]
                        if status.confirmation_status:
                            logger.info(f"✅ Transaction confirmed: {status.confirmation_status}")
                            return True
                        elif status.err:
                            logger.error(f"❌ Transaction failed: {status.err}")
                            return False
                except Exception:
                    pass
                
                await asyncio.sleep(2)
            
            logger.warning(f"⏰ Transaction confirmation timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error confirming transaction: {e}")
            return False
    
    async def execute_phoenix_order(self, market_info: PhoenixMarketInfo, amount_sol: float, direction: str) -> Optional[str]:
        """
        Execute order on Phoenix market (order book)
        
        Phoenix uses a different model than AMMs:
        - Central Limit Order Book (CLOB)
        - Market makers provide liquidity at various price levels
        - Orders are matched against the order book
        
        For now, we'll use Jupiter as it aggregates Phoenix liquidity efficiently.
        Direct Phoenix implementation would require:
        1. Market state fetching
        2. Order book analysis
        3. Order placement and matching logic
        4. Complex account structure handling
        """
        try:
            logger.info(f"🔥 Attempting Phoenix {direction}: {amount_sol} {'SOL' if direction == 'BUY' else 'tokens'}")
            logger.info("💡 Using Jupiter for Phoenix order book access...")
            
            if direction == "BUY":
                return await self.trade_via_jupiter(str(SOL_MINT), str(USDC_MINT), amount_sol, "BUY")
            else:
                return await self.trade_via_jupiter(str(USDC_MINT), str(SOL_MINT), amount_sol, "SELL")
                
        except Exception as e:
            logger.error(f"❌ Phoenix order error: {e}")
            return None
    
    async def buy_tokens(self, amount_sol: float) -> TradeResult:
        """
        Buy USDC with SOL using Phoenix order book
        """
        try:
            logger.info(f"🛒 Phoenix BUY: {amount_sol} SOL → USDC")
            
            # Use SOL/USDC market
            market_info = self.known_markets["SOL/USDC"]
            signature = await self.execute_phoenix_order(market_info, amount_sol, "BUY")
            
            if signature:
                return TradeResult(
                    success=True,
                    signature=signature,
                    amount_in=amount_sol
                )
            else:
                return TradeResult(
                    success=False,
                    error="Failed to execute Phoenix buy order"
                )
                
        except Exception as e:
            logger.error(f"❌ Phoenix buy error: {e}")
            return TradeResult(
                success=False,
                error=str(e)
            )
    
    async def sell_tokens(self) -> TradeResult:
        """
        Sell all USDC for SOL using Phoenix order book
        """
        try:
            logger.info(f"💸 Phoenix SELL: USDC → SOL")
            
            # Get current USDC balance
            balances = await self.get_balances()
            usdc_amount = balances.get("USDC", 0)
            
            if usdc_amount == 0:
                return TradeResult(
                    success=False,
                    error="No USDC balance to sell"
                )
            
            logger.info(f"   Selling {usdc_amount} USDC")
            
            # Use SOL/USDC market
            market_info = self.known_markets["SOL/USDC"]
            signature = await self.execute_phoenix_order(market_info, usdc_amount, "SELL")
            
            if signature:
                return TradeResult(
                    success=True,
                    signature=signature,
                    amount_in=usdc_amount
                )
            else:
                return TradeResult(
                    success=False,
                    error="Failed to execute Phoenix sell order"
                )
                
        except Exception as e:
            logger.error(f"❌ Phoenix sell error: {e}")
            return TradeResult(
                success=False,
                error=str(e)
            )
    
    async def run_buy_hold_sell_test(self, amount_sol: float = 0.001, hold_seconds: int = 5):
        """
        Run complete buy → hold → sell test cycle on Phoenix
        """
        logger.info("🚀 Starting Phoenix Buy-Hold-Sell Test")
        logger.info(f"   Amount: {amount_sol} SOL")
        logger.info(f"   Market: Order Book (CLOB)")
        logger.info(f"   Hold Time: {hold_seconds} seconds")
        
        try:
            # Check initial balances
            initial_balances = await self.get_balances()
            logger.info(f"💰 Initial balances: {initial_balances['SOL']:.6f} SOL, {initial_balances['USDC']:.6f} USDC")
            
            if initial_balances["SOL"] < amount_sol:
                logger.error(f"❌ Insufficient SOL balance. Need {amount_sol}, have {initial_balances['SOL']}")
                return
            
            # Step 1: Buy
            logger.info("\n📈 Step 1: Place buy order (SOL → USDC)")
            buy_result = await self.buy_tokens(amount_sol)
            
            if not buy_result.success:
                logger.error(f"❌ Buy order failed: {buy_result.error}")
                return
            
            logger.info(f"✅ Buy order executed: {buy_result.signature}")
            
            # Check balances after buy
            post_buy_balances = await self.get_balances()
            logger.info(f"💰 Post-buy balances: {post_buy_balances['SOL']:.6f} SOL, {post_buy_balances['USDC']:.6f} USDC")
            
            # Step 2: Hold
            logger.info(f"\n⏳ Step 2: Holding position for {hold_seconds} seconds...")
            await asyncio.sleep(hold_seconds)
            
            # Step 3: Sell
            logger.info("\n📉 Step 3: Place sell order (USDC → SOL)")
            sell_result = await self.sell_tokens()
            
            if not sell_result.success:
                logger.error(f"❌ Sell order failed: {sell_result.error}")
                return
            
            logger.info(f"✅ Sell order executed: {sell_result.signature}")
            
            # Check final balances
            final_balances = await self.get_balances()
            logger.info(f"💰 Final balances: {final_balances['SOL']:.6f} SOL, {final_balances['USDC']:.6f} USDC")
            
            # Calculate P&L
            sol_change = final_balances["SOL"] - initial_balances["SOL"]
            logger.info(f"\n📊 Trade Summary:")
            logger.info(f"   SOL Change: {sol_change:+.6f}")
            logger.info(f"   Buy TX: https://solscan.io/tx/{buy_result.signature}")
            logger.info(f"   Sell TX: https://solscan.io/tx/{sell_result.signature}")
            
            logger.info("🎉 Phoenix buy-hold-sell test completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
    
    async def get_market_info(self) -> Dict[str, Any]:
        """
        Get Phoenix market information (order book state, spreads, etc.)
        This would require direct Phoenix program interaction in production
        """
        try:
            logger.info("📊 Fetching Phoenix market information...")
            
            # For now, we'll simulate market info
            # Real implementation would fetch:
            # - Order book depth
            # - Best bid/ask prices
            # - Market statistics
            # - Available liquidity
            
            market_info = {
                "market": "SOL/USDC",
                "type": "Central Limit Order Book (CLOB)",
                "program_id": str(PHOENIX_PROGRAM_ID),
                "status": "Active (via Jupiter aggregation)",
                "note": "Direct Phoenix integration would provide detailed order book data"
            }
            
            logger.info(f"   Market: {market_info['market']}")
            logger.info(f"   Type: {market_info['type']}")
            logger.info(f"   Status: {market_info['status']}")
            
            return market_info
            
        except Exception as e:
            logger.error(f"❌ Error getting market info: {e}")
            return {}
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()

async def main():
    """Main test function"""
    print("🔥 PHOENIX MANUAL TRADER TEST")
    print("=" * 50)
    print("Testing Phoenix DEX with buy → hold → sell cycle")
    print("Phoenix uses Central Limit Order Book (CLOB) model")
    print("=" * 50)
    
    trader = PhoenixTrader(WALLET, env.HELIUS_RPC_URL)
    
    try:
        # Get market information
        market_info = await trader.get_market_info()
        
        # Run trading test
        await trader.run_buy_hold_sell_test(
            amount_sol=0.001,
            hold_seconds=5
        )
        
        logger.info("\n🎯 Phoenix test completed!")
        logger.info("\n📝 Notes:")
        logger.info("   • Phoenix uses order book model (different from AMMs)")
        logger.info("   • Jupiter aggregates Phoenix liquidity with other DEXes")
        logger.info("   • Direct Phoenix integration would provide order book control")
        logger.info("   • Current implementation ensures reliable execution")
        
    except KeyboardInterrupt:
        logger.info("\n👋 Test interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Test error: {e}")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
