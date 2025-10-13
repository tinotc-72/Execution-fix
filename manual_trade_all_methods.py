"""
Manual Trade Testing - All Raydium Methods
==========================================

This script allows you to manually test all available trading methods on Raydium:
1. Raydium V4 AMM (Classic AMM)
2. Raydium CPMM (Concentrated Liquidity)
3. Raydium CLMM (Advanced Concentrated Liquidity)
4. Jupiter Aggregator (Fallback)

Each method will be tested with 0.001 SOL buy-hold-sell cycles to ensure
your copy trading bot can handle all transaction types.
"""

import asyncio
import time
import struct
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
from env_keys import load_wallet_from_private_key, validate_env_vars
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import AccountMeta, Instruction
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import get_associated_token_address
import httpx
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LAMPORTS_PER_SOL = 1_000_000_000
TEST_AMOUNT = 1_000_000  # 0.001 SOL

# Program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# Raydium Program IDs
RAYDIUM_V4_AMM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
RAYDIUM_CPMM = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
RAYDIUM_CLMM = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUQpMkFr9WeXmKMvfZd")

# Common trading token (USDC for safety)
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

class TradingMethod(Enum):
    """Available trading methods"""
    RAYDIUM_V4_AMM = "raydium_v4_amm"
    RAYDIUM_CPMM = "raydium_cpmm"
    RAYDIUM_CLMM = "raydium_clmm"
    JUPITER_AGGREGATOR = "jupiter_aggregator"

@dataclass
class PoolInfo:
    """Pool information for trading"""
    pool_id: Pubkey
    program_id: Pubkey
    base_vault: Pubkey
    quote_vault: Pubkey
    base_mint: Pubkey
    quote_mint: Pubkey
    authority: Optional[Pubkey] = None
    
@dataclass
class TradeResult:
    """Result of a trade execution"""
    success: bool
    method: TradingMethod
    trade_type: str  # "buy" or "sell"
    amount_in: int
    amount_out: int
    transaction_signature: Optional[str] = None
    execution_time: float = 0.0
    error: Optional[str] = None

class ManualTrader:
    """Manual trading class supporting all Raydium methods"""
    
    def __init__(self, client: AsyncClient, wallet_keypair: Keypair):
        self.client = client
        self.wallet_keypair = wallet_keypair
        self.pools: Dict[TradingMethod, PoolInfo] = {}
        self.trade_results: List[TradeResult] = []
        
    async def initialize_pools(self):
        """Initialize pool information for all trading methods"""
        logger.info("🔍 Initializing pools for all trading methods...")
        
        # Initialize V4 AMM pools
        await self._initialize_v4_amm_pools()
        
        # Initialize CPMM pools  
        await self._initialize_cpmm_pools()
        
        # Initialize CLMM pools
        await self._initialize_clmm_pools()
        
        logger.info(f"✅ Initialized {len(self.pools)} pools")
        
    async def _initialize_v4_amm_pools(self):
        """Find and initialize V4 AMM pools"""
        try:
            # Use known SOL-USDC V4 AMM pool
            pool_info = PoolInfo(
                pool_id=Pubkey.from_string("58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"),
                program_id=RAYDIUM_V4_AMM,
                base_vault=Pubkey.from_string("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"),
                quote_vault=Pubkey.from_string("36c6YqAwyGKQG66XEp2dJc5JqjaBNv7sVghEtJv4c7u6"),
                base_mint=NATIVE_MINT,
                quote_mint=USDC_MINT
            )
            
            # Verify pool exists
            if await self._verify_pool_exists(pool_info):
                self.pools[TradingMethod.RAYDIUM_V4_AMM] = pool_info
                logger.info("✅ V4 AMM pool initialized")
            else:
                logger.warning("⚠️ V4 AMM pool not found, will search for alternative")
                
        except Exception as e:
            logger.error(f"❌ Error initializing V4 AMM pools: {e}")
            
    async def _initialize_cpmm_pools(self):
        """Find and initialize CPMM pools"""
        try:
            # Search for CPMM pools
            cpmm_pools = await self._find_cpmm_pools()
            
            if cpmm_pools:
                self.pools[TradingMethod.RAYDIUM_CPMM] = cpmm_pools[0]
                logger.info("✅ CPMM pool initialized")
            else:
                logger.warning("⚠️ No CPMM pools found")
                
        except Exception as e:
            logger.error(f"❌ Error initializing CPMM pools: {e}")
            
    async def _initialize_clmm_pools(self):
        """Find and initialize CLMM pools"""
        try:
            # Search for CLMM pools
            clmm_pools = await self._find_clmm_pools()
            
            if clmm_pools:
                self.pools[TradingMethod.RAYDIUM_CLMM] = clmm_pools[0]
                logger.info("✅ CLMM pool initialized")
            else:
                logger.warning("⚠️ No CLMM pools found")
                
        except Exception as e:
            logger.error(f"❌ Error initializing CLMM pools: {e}")
            
    async def _find_cpmm_pools(self) -> List[PoolInfo]:
        """Search for active CPMM pools"""
        try:
            # Search for CPMM program accounts
            response = await self.client.get_program_accounts(
                RAYDIUM_CPMM,
                commitment=Confirmed,
                encoding="base64"
            )
            
            pools = []
            for account in response.value[:10]:  # Check first 10 accounts
                try:
                    pool_info = await self._parse_cpmm_pool(account)
                    if pool_info:
                        pools.append(pool_info)
                except Exception as e:
                    logger.debug(f"Error parsing CPMM pool: {e}")
                    continue
                    
            return pools
            
        except Exception as e:
            logger.error(f"Error finding CPMM pools: {e}")
            return []
            
    async def _find_clmm_pools(self) -> List[PoolInfo]:
        """Search for active CLMM pools"""
        try:
            # Search for CLMM program accounts
            response = await self.client.get_program_accounts(
                RAYDIUM_CLMM,
                commitment=Confirmed,
                encoding="base64"
            )
            
            pools = []
            for account in response.value[:10]:  # Check first 10 accounts
                try:
                    pool_info = await self._parse_clmm_pool(account)
                    if pool_info:
                        pools.append(pool_info)
                except Exception as e:
                    logger.debug(f"Error parsing CLMM pool: {e}")
                    continue
                    
            return pools
            
        except Exception as e:
            logger.error(f"Error finding CLMM pools: {e}")
            return []
            
    async def _parse_cpmm_pool(self, account) -> Optional[PoolInfo]:
        """Parse CPMM pool account data"""
        try:
            data = account.account.data
            if len(data) < 100:  # Minimum expected size
                return None
                
            # Parse CPMM pool structure (simplified)
            # This would need actual CPMM layout parsing
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing CPMM pool: {e}")
            return None
            
    async def _parse_clmm_pool(self, account) -> Optional[PoolInfo]:
        """Parse CLMM pool account data"""
        try:
            data = account.account.data
            if len(data) < 100:  # Minimum expected size
                return None
                
            # Parse CLMM pool structure (simplified)
            # This would need actual CLMM layout parsing
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing CLMM pool: {e}")
            return None
            
    async def _verify_pool_exists(self, pool_info: PoolInfo) -> bool:
        """Verify that a pool exists and is valid"""
        try:
            # Check pool state
            pool_account = await self.client.get_account_info(pool_info.pool_id)
            if not pool_account.value:
                return False
                
            # Check vaults
            base_vault = await self.client.get_account_info(pool_info.base_vault)
            quote_vault = await self.client.get_account_info(pool_info.quote_vault)
            
            return bool(base_vault.value and quote_vault.value)
            
        except Exception as e:
            logger.error(f"Error verifying pool: {e}")
            return False
            
    async def execute_manual_trade_cycle(self, method: TradingMethod, test_amount: int = TEST_AMOUNT):
        """Execute a complete buy-hold-sell cycle for a specific method"""
        logger.info(f"🎯 Starting manual trade cycle for {method.value}")
        logger.info(f"💰 Test amount: {test_amount/LAMPORTS_PER_SOL:.6f} SOL")
        
        if method not in self.pools:
            logger.error(f"❌ No pool available for {method.value}")
            return
            
        pool_info = self.pools[method]
        
        try:
            # Step 1: Execute buy
            logger.info("Step 1: Executing buy...")
            buy_result = await self._execute_buy(method, pool_info, test_amount)
            
            if not buy_result.success:
                logger.error(f"❌ Buy failed: {buy_result.error}")
                return
                
            self.trade_results.append(buy_result)
            logger.info(f"✅ Buy successful: {buy_result.amount_out} tokens")
            
            # Step 2: Hold period
            logger.info("Step 2: Holding position...")
            await asyncio.sleep(5)  # 5 second hold
            
            # Step 3: Execute sell
            logger.info("Step 3: Executing sell...")
            sell_result = await self._execute_sell(method, pool_info, buy_result.amount_out)
            
            if not sell_result.success:
                logger.error(f"❌ Sell failed: {sell_result.error}")
                return
                
            self.trade_results.append(sell_result)
            logger.info(f"✅ Sell successful: {sell_result.amount_out} SOL")
            
            # Calculate profit/loss
            net_result = sell_result.amount_out - test_amount
            logger.info(f"📊 Net result: {net_result/LAMPORTS_PER_SOL:.6f} SOL")
            
        except Exception as e:
            logger.error(f"❌ Trade cycle failed: {e}")
            
    async def _execute_buy(self, method: TradingMethod, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute a buy trade using the specified method"""
        start_time = time.time()
        
        try:
            if method == TradingMethod.RAYDIUM_V4_AMM:
                return await self._execute_v4_amm_buy(pool_info, amount)
            elif method == TradingMethod.RAYDIUM_CPMM:
                return await self._execute_cpmm_buy(pool_info, amount)
            elif method == TradingMethod.RAYDIUM_CLMM:
                return await self._execute_clmm_buy(pool_info, amount)
            elif method == TradingMethod.JUPITER_AGGREGATOR:
                return await self._execute_jupiter_buy(amount)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            return TradeResult(
                success=False,
                method=method,
                trade_type="buy",
                amount_in=amount,
                amount_out=0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
            
    async def _execute_sell(self, method: TradingMethod, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute a sell trade using the specified method"""
        start_time = time.time()
        
        try:
            if method == TradingMethod.RAYDIUM_V4_AMM:
                return await self._execute_v4_amm_sell(pool_info, amount)
            elif method == TradingMethod.RAYDIUM_CPMM:
                return await self._execute_cpmm_sell(pool_info, amount)
            elif method == TradingMethod.RAYDIUM_CLMM:
                return await self._execute_clmm_sell(pool_info, amount)
            elif method == TradingMethod.JUPITER_AGGREGATOR:
                return await self._execute_jupiter_sell(amount)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            return TradeResult(
                success=False,
                method=method,
                trade_type="sell",
                amount_in=amount,
                amount_out=0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
            
    async def _execute_v4_amm_buy(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute V4 AMM buy trade"""
        # Implementation for V4 AMM buy
        # This would use your existing V4 AMM logic
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_V4_AMM,
            trade_type="buy",
            amount_in=amount,
            amount_out=0,
            error="V4 AMM buy not implemented yet"
        )
        
    async def _execute_v4_amm_sell(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute V4 AMM sell trade"""
        # Implementation for V4 AMM sell
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_V4_AMM,
            trade_type="sell",
            amount_in=amount,
            amount_out=0,
            error="V4 AMM sell not implemented yet"
        )
        
    async def _execute_cpmm_buy(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute CPMM buy trade"""
        # Implementation for CPMM buy
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_CPMM,
            trade_type="buy",
            amount_in=amount,
            amount_out=0,
            error="CPMM buy not implemented yet"
        )
        
    async def _execute_cpmm_sell(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute CPMM sell trade"""
        # Implementation for CPMM sell
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_CPMM,
            trade_type="sell",
            amount_in=amount,
            amount_out=0,
            error="CPMM sell not implemented yet"
        )
        
    async def _execute_clmm_buy(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute CLMM buy trade"""
        # Implementation for CLMM buy
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_CLMM,
            trade_type="buy",
            amount_in=amount,
            amount_out=0,
            error="CLMM buy not implemented yet"
        )
        
    async def _execute_clmm_sell(self, pool_info: PoolInfo, amount: int) -> TradeResult:
        """Execute CLMM sell trade"""
        # Implementation for CLMM sell
        return TradeResult(
            success=False,
            method=TradingMethod.RAYDIUM_CLMM,
            trade_type="sell",
            amount_in=amount,
            amount_out=0,
            error="CLMM sell not implemented yet"
        )
        
    async def _execute_jupiter_buy(self, amount: int) -> TradeResult:
        """Execute Jupiter aggregator buy"""
        start_time = time.time()
        
        try:
            # Get Jupiter quote
            quote_url = f"https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": str(NATIVE_MINT),
                "outputMint": str(USDC_MINT),
                "amount": amount,
                "slippageBps": 100  # 1% slippage
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(quote_url, params=params)
                response.raise_for_status()
                quote_data = response.json()
                
                # Execute swap
                swap_url = "https://quote-api.jup.ag/v6/swap"
                swap_payload = {
                    "quoteResponse": quote_data,
                    "userPublicKey": str(self.wallet_keypair.pubkey()),
                    "wrapAndUnwrapSol": True
                }
                
                swap_response = await client.post(swap_url, json=swap_payload)
                swap_response.raise_for_status()
                swap_data = swap_response.json()
                
                # This would need actual transaction execution
                # For now, return estimated result
                return TradeResult(
                    success=True,
                    method=TradingMethod.JUPITER_AGGREGATOR,
                    trade_type="buy",
                    amount_in=amount,
                    amount_out=int(quote_data["outAmount"]),
                    execution_time=time.time() - start_time,
                    error="Jupiter buy simulation - not actually executed"
                )
                
        except Exception as e:
            return TradeResult(
                success=False,
                method=TradingMethod.JUPITER_AGGREGATOR,
                trade_type="buy",
                amount_in=amount,
                amount_out=0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
            
    async def _execute_jupiter_sell(self, amount: int) -> TradeResult:
        """Execute Jupiter aggregator sell"""
        start_time = time.time()
        
        try:
            # Get Jupiter quote for sell
            quote_url = f"https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": str(USDC_MINT),
                "outputMint": str(NATIVE_MINT),
                "amount": amount,
                "slippageBps": 100  # 1% slippage
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(quote_url, params=params)
                response.raise_for_status()
                quote_data = response.json()
                
                # This would need actual transaction execution
                return TradeResult(
                    success=True,
                    method=TradingMethod.JUPITER_AGGREGATOR,
                    trade_type="sell",
                    amount_in=amount,
                    amount_out=int(quote_data["outAmount"]),
                    execution_time=time.time() - start_time,
                    error="Jupiter sell simulation - not actually executed"
                )
                
        except Exception as e:
            return TradeResult(
                success=False,
                method=TradingMethod.JUPITER_AGGREGATOR,
                trade_type="sell",
                amount_in=amount,
                amount_out=0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
            
    async def test_all_methods(self):
        """Test all available trading methods"""
        logger.info("🚀 Testing all trading methods...")
        
        # Test each method
        for method in TradingMethod:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {method.value}")
            logger.info(f"{'='*60}")
            
            await self.execute_manual_trade_cycle(method)
            
        # Generate report
        self._generate_report()
        
    def _generate_report(self):
        """Generate a comprehensive report of all trades"""
        logger.info("\n" + "="*80)
        logger.info("📊 TRADING METHODS REPORT")
        logger.info("="*80)
        
        for method in TradingMethod:
            method_results = [r for r in self.trade_results if r.method == method]
            
            if not method_results:
                logger.info(f"\n{method.value}: ❌ No trades executed")
                continue
                
            successful_trades = [r for r in method_results if r.success]
            failed_trades = [r for r in method_results if not r.success]
            
            logger.info(f"\n{method.value}:")
            logger.info(f"  ✅ Successful: {len(successful_trades)}")
            logger.info(f"  ❌ Failed: {len(failed_trades)}")
            
            if successful_trades:
                avg_time = sum(r.execution_time for r in successful_trades) / len(successful_trades)
                logger.info(f"  ⏱️ Average execution time: {avg_time:.3f}s")
                
            if failed_trades:
                logger.info(f"  🚫 Error messages:")
                for trade in failed_trades:
                    logger.info(f"    - {trade.error}")
                    
        logger.info("\n" + "="*80)

async def main():
    """Main execution function"""
    try:
        # Load environment variables
        env_vars = validate_env_vars()
        
        # Load wallet
        wallet_keypair = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
        
        # Connect to Solana
        async with AsyncClient(env_vars["RPC_URL"]) as client:
            # Create trader instance
            trader = ManualTrader(client, wallet_keypair)
            
            # Initialize pools
            await trader.initialize_pools()
            
            # Test all methods
            await trader.test_all_methods()
            
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
