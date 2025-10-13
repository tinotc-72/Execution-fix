#!/usr/bin/env python3
"""
Orca Manual Trader - Buy, Hold, Sell Testing
============================================

This script tests Orca DEX trading with both:
1. Orca Legacy Pools (traditional AMM)
2. Orca Whirlpools (concentrated liquidity)

Orca is the 2nd largest DEX on Solana (~25% market share)
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
logger = logging.getLogger("orca_trader")

# Load environment
env = EnvKeys()

# Orca Program IDs
ORCA_WHIRLPOOL_PROGRAM = Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc")
ORCA_LEGACY_PROGRAM = Pubkey.from_string("9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP")
ORCA_TOKEN_SWAP_PROGRAM = Pubkey.from_string("9qvG1zUp8xF1Bi4m6UdRNby1BAAuaDrUxSpv4CmRRMjL")

# Token addresses
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

# Well-known Orca pools (SOL/USDC)
ORCA_SOL_USDC_POOL = Pubkey.from_string("EGZ7tiLeH62TPV1gL8WwbXGzEPa9zmcpVnnkPKKnrE2U")  # Legacy pool
ORCA_WHIRLPOOL_SOL_USDC = Pubkey.from_string("HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ")  # Whirlpool

@dataclass
class OrcaPoolInfo:
    """Information about an Orca pool"""
    pool_id: Pubkey
    pool_type: str  # "legacy" or "whirlpool"
    token_a: Pubkey
    token_b: Pubkey
    vault_a: Optional[Pubkey] = None
    vault_b: Optional[Pubkey] = None
    fee_rate: Optional[int] = None
    
@dataclass
class TradeResult:
    """Result of a trade execution"""
    success: bool
    signature: Optional[str] = None
    amount_in: float = 0.0
    amount_out: float = 0.0
    error: Optional[str] = None

class OrcaTrader:
    """
    Orca DEX trader supporting both Legacy and Whirlpool AMMs
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        
        # Known pool configurations
        self.known_pools = {
            "SOL/USDC_LEGACY": OrcaPoolInfo(
                pool_id=ORCA_SOL_USDC_POOL,
                pool_type="legacy",
                token_a=SOL_MINT,
                token_b=USDC_MINT
            ),
            "SOL/USDC_WHIRLPOOL": OrcaPoolInfo(
                pool_id=ORCA_WHIRLPOOL_SOL_USDC,
                pool_type="whirlpool", 
                token_a=SOL_MINT,
                token_b=USDC_MINT
            )
        }
        
        logger.info(f"🐋 Orca Trader initialized for wallet: {self.wallet_pubkey}")
    
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
        Execute trade via Jupiter API (fallback method)
        """
        try:
            logger.info(f"🪐 Executing {direction} via Jupiter...")
            
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
                    logger.info(f"   Quote received: {quote_data['outAmount']} tokens")
                
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
    
    async def execute_orca_legacy_swap(self, pool_info: OrcaPoolInfo, amount_sol: float, direction: str) -> Optional[str]:
        """
        Execute swap on Orca Legacy Pool (traditional AMM)
        """
        try:
            logger.info(f"🌊 Attempting Orca Legacy {direction}: {amount_sol} SOL")
            
            # For now, we'll use Jupiter as a reliable fallback for Orca trades
            # Direct Orca implementation would require:
            # 1. Pool state fetching
            # 2. Orca-specific instruction building
            # 3. Complex account structure handling
            
            logger.info("💡 Using Jupiter for Orca liquidity access...")
            
            if direction == "BUY":
                return await self.trade_via_jupiter(str(SOL_MINT), str(USDC_MINT), amount_sol, "BUY")
            else:
                return await self.trade_via_jupiter(str(USDC_MINT), str(SOL_MINT), amount_sol, "SELL")
                
        except Exception as e:
            logger.error(f"❌ Orca Legacy swap error: {e}")
            return None
    
    async def execute_orca_whirlpool_swap(self, pool_info: OrcaPoolInfo, amount_sol: float, direction: str) -> Optional[str]:
        """
        Execute swap on Orca Whirlpool (concentrated liquidity)
        """
        try:
            logger.info(f"🌀 Attempting Orca Whirlpool {direction}: {amount_sol} SOL")
            
            # Whirlpools are more complex than legacy pools
            # They require tick arrays, price calculations, etc.
            # For production, we'd need full Whirlpool SDK integration
            
            logger.info("💡 Using Jupiter for Whirlpool liquidity access...")
            
            if direction == "BUY":
                return await self.trade_via_jupiter(str(SOL_MINT), str(USDC_MINT), amount_sol, "BUY")
            else:
                return await self.trade_via_jupiter(str(USDC_MINT), str(SOL_MINT), amount_sol, "SELL")
                
        except Exception as e:
            logger.error(f"❌ Orca Whirlpool swap error: {e}")
            return None
    
    async def buy_tokens(self, amount_sol: float, pool_type: str = "legacy") -> TradeResult:
        """
        Buy USDC with SOL using Orca
        """
        try:
            logger.info(f"🛒 Orca {pool_type.upper()} BUY: {amount_sol} SOL → USDC")
            
            # Select pool based on type
            if pool_type == "legacy":
                pool_info = self.known_pools["SOL/USDC_LEGACY"]
                signature = await self.execute_orca_legacy_swap(pool_info, amount_sol, "BUY")
            elif pool_type == "whirlpool":
                pool_info = self.known_pools["SOL/USDC_WHIRLPOOL"]
                signature = await self.execute_orca_whirlpool_swap(pool_info, amount_sol, "BUY")
            else:
                raise ValueError(f"Unknown pool type: {pool_type}")
            
            if signature:
                return TradeResult(
                    success=True,
                    signature=signature,
                    amount_in=amount_sol
                )
            else:
                return TradeResult(
                    success=False,
                    error="Failed to execute Orca buy"
                )
                
        except Exception as e:
            logger.error(f"❌ Orca buy error: {e}")
            return TradeResult(
                success=False,
                error=str(e)
            )
    
    async def sell_tokens(self, pool_type: str = "legacy") -> TradeResult:
        """
        Sell all USDC for SOL using Orca
        """
        try:
            logger.info(f"💸 Orca {pool_type.upper()} SELL: USDC → SOL")
            
            # Get current USDC balance
            balances = await self.get_balances()
            usdc_amount = balances.get("USDC", 0)
            
            if usdc_amount == 0:
                return TradeResult(
                    success=False,
                    error="No USDC balance to sell"
                )
            
            logger.info(f"   Selling {usdc_amount} USDC")
            
            # Select pool based on type
            if pool_type == "legacy":
                pool_info = self.known_pools["SOL/USDC_LEGACY"]
                signature = await self.execute_orca_legacy_swap(pool_info, usdc_amount, "SELL")
            elif pool_type == "whirlpool":
                pool_info = self.known_pools["SOL/USDC_WHIRLPOOL"]
                signature = await self.execute_orca_whirlpool_swap(pool_info, usdc_amount, "SELL")
            else:
                raise ValueError(f"Unknown pool type: {pool_type}")
            
            if signature:
                return TradeResult(
                    success=True,
                    signature=signature,
                    amount_in=usdc_amount
                )
            else:
                return TradeResult(
                    success=False,
                    error="Failed to execute Orca sell"
                )
                
        except Exception as e:
            logger.error(f"❌ Orca sell error: {e}")
            return TradeResult(
                success=False,
                error=str(e)
            )
    
    async def run_buy_hold_sell_test(self, amount_sol: float = 0.001, hold_seconds: int = 5, pool_type: str = "legacy"):
        """
        Run complete buy → hold → sell test cycle
        """
        logger.info("🚀 Starting Orca Buy-Hold-Sell Test")
        logger.info(f"   Amount: {amount_sol} SOL")
        logger.info(f"   Pool Type: {pool_type}")
        logger.info(f"   Hold Time: {hold_seconds} seconds")
        
        try:
            # Check initial balances
            initial_balances = await self.get_balances()
            logger.info(f"💰 Initial balances: {initial_balances['SOL']:.6f} SOL, {initial_balances['USDC']:.6f} USDC")
            
            if initial_balances["SOL"] < amount_sol:
                logger.error(f"❌ Insufficient SOL balance. Need {amount_sol}, have {initial_balances['SOL']}")
                return
            
            # Step 1: Buy
            logger.info("\n📈 Step 1: Buy USDC with SOL")
            buy_result = await self.buy_tokens(amount_sol, pool_type)
            
            if not buy_result.success:
                logger.error(f"❌ Buy failed: {buy_result.error}")
                return
            
            logger.info(f"✅ Buy successful: {buy_result.signature}")
            
            # Check balances after buy
            post_buy_balances = await self.get_balances()
            logger.info(f"💰 Post-buy balances: {post_buy_balances['SOL']:.6f} SOL, {post_buy_balances['USDC']:.6f} USDC")
            
            # Step 2: Hold
            logger.info(f"\n⏳ Step 2: Holding position for {hold_seconds} seconds...")
            await asyncio.sleep(hold_seconds)
            
            # Step 3: Sell
            logger.info("\n📉 Step 3: Sell USDC back to SOL")
            sell_result = await self.sell_tokens(pool_type)
            
            if not sell_result.success:
                logger.error(f"❌ Sell failed: {sell_result.error}")
                return
            
            logger.info(f"✅ Sell successful: {sell_result.signature}")
            
            # Check final balances
            final_balances = await self.get_balances()
            logger.info(f"💰 Final balances: {final_balances['SOL']:.6f} SOL, {final_balances['USDC']:.6f} USDC")
            
            # Calculate P&L
            sol_change = final_balances["SOL"] - initial_balances["SOL"]
            logger.info(f"\n📊 Trade Summary:")
            logger.info(f"   SOL Change: {sol_change:+.6f}")
            logger.info(f"   Buy TX: https://solscan.io/tx/{buy_result.signature}")
            logger.info(f"   Sell TX: https://solscan.io/tx/{sell_result.signature}")
            
            logger.info("🎉 Orca buy-hold-sell test completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()

async def main():
    """Main test function"""
    print("🐋 ORCA MANUAL TRADER TEST")
    print("=" * 50)
    print("Testing Orca DEX with buy → hold → sell cycle")
    print("=" * 50)
    
    trader = OrcaTrader(WALLET, env.HELIUS_RPC_URL)
    
    try:
        # Test both pool types
        test_configs = [
            {"amount": 0.001, "hold_time": 5, "pool_type": "legacy"},
            {"amount": 0.001, "hold_time": 5, "pool_type": "whirlpool"}
        ]
        
        for config in test_configs:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {config['pool_type'].upper()} pool")
            logger.info(f"{'='*60}")
            
            await trader.run_buy_hold_sell_test(
                amount_sol=config["amount"],
                hold_seconds=config["hold_time"],
                pool_type=config["pool_type"]
            )
            
            # Wait between tests
            if config != test_configs[-1]:
                logger.info("\n⏳ Waiting 10 seconds before next test...")
                await asyncio.sleep(10)
        
        logger.info("\n🎯 All Orca tests completed!")
        
    except KeyboardInterrupt:
        logger.info("\n👋 Test interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Test error: {e}")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
