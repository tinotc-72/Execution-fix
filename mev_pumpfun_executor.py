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

import logging
import traceback
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

    
    # Router support (NEW)
    enable_router_programs: bool = True  # Enable router program support
    router_priority: bool = True  # Prefer router programs when detected
    supported_routers = [
        '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',  # Direct Pump.fun
        'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq',  # Router/Wrapper
        '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC'   # Alternative Router
    ]
    skip_preflight: bool = True  # MEV speed optimization
    
    # Compatibility with your existing system
    enable_buy: bool = True
    enable_sell: bool = True
    debug_mode: bool = False

class MEVPumpFunExecutor:
    """
    MEV-optimized Pump.fun executor that replaces pumpfun_CC_copy_executor
    Provides the same interface but with professional MEV capabilities
    """
    
    def __init__(self, private_key: str, config: MEVExecutorConfig = None):
        self.config = config or MEVExecutorConfig()
        self.private_key = private_key
        
        # Create MEV bot with optimized configuration
        mev_config = CompleteMEVConfig(
            buy_priority_fee=self.config.buy_priority_fee,
            buy_compute_limit=self.config.buy_compute_limit,
            buy_slippage_multiplier=self.config.buy_slippage_multiplier,
            sell_priority_fee=self.config.sell_priority_fee,
            sell_compute_limit=self.config.sell_compute_limit,
            sell_slippage_multiplier=self.config.sell_slippage_multiplier,
            skip_preflight=self.config.skip_preflight,
            use_mev_router=True
        )
        
        self.mev_bot = CompleteMEVBot(private_key, mev_config)
        
        # Stats tracking
        self.buy_attempts = 0
        self.buy_successes = 0
        self.sell_attempts = 0
        self.sell_successes = 0
        
        logger.info("🤖 MEV Pump.fun Executor initialized")
        logger.info(f"   Buy Priority: {self.config.buy_priority_fee:,} μ-lamports")
        logger.info(f"   Sell Priority: {self.config.sell_priority_fee:,} μ-lamports")
        

    async def execute_buy_copy(
        self,
        mint_address: str,
        sol_amount: float,
        transaction_logs: list = None,
        trade_info: dict = None,
        **kwargs
    ) -> BuildResult:
        """
        Execute MEV-optimized buy using CompleteMEVBot, passing router program/account metas/instruction data from trade_info.
        """
        self.buy_attempts += 1
        try:
            if not self.config.enable_buy:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="buy",
                    reason="Buy trades disabled"
                )
            if sol_amount < self.config.min_buy_sol:
                return BuildResult(
                    ok=False,
                    tx=None, 
                    dex="pumpfun",
                    action="buy",
                    reason=f"Buy amount too small: {sol_amount}"
                )
            if sol_amount > self.config.max_buy_sol:
                sol_amount = self.config.max_buy_sol
                logger.warning(f"⚠️ Capping buy amount to {self.config.max_buy_sol} SOL")
            logger.info(f"🎯 MEV Buy: {mint_address} for {sol_amount:.6f} SOL")
            # Extract router program/account metas/instruction data from trade_info
            router_program_id = None
            router_account_metas = None
            router_instruction_data = None
            if trade_info:
                router_program_id = trade_info.get('router_program_id')
                router_account_metas = trade_info.get('account_metas')  # Fixed field name
                router_instruction_data = trade_info.get('instruction_data')  # Fixed field name
                
                # ✅ CRITICAL FIX: Validate router program compatibility
                # Only use router data if it's from a compatible program (not Jupiter/other DEXs)
                jupiter_program_id = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
                if router_program_id == jupiter_program_id:
                    logger.warning(f"⚠️ [MEV BUY] Router data is from Jupiter ({jupiter_program_id[:8]}...), incompatible with Pump.fun - ignoring router data")
                    router_program_id = None
                    router_account_metas = None
                    router_instruction_data = None
                elif router_program_id and router_program_id not in [
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun program
                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Advanced MEV program
                    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"   # Another Pump.fun variant
                ]:
                    logger.warning(f"⚠️ [MEV BUY] Router data is from unknown program ({router_program_id[:8]}...), incompatible with Pump.fun - ignoring router data")
                    router_program_id = None
                    router_account_metas = None
                    router_instruction_data = None
                elif router_program_id:
                    logger.info(f"✅ [MEV BUY] Router data from compatible program: {router_program_id[:8]}...")
                else:
                    logger.info("ℹ️ [MEV BUY] No router data available, proceeding with standard Pump.fun execution")
                
                # Set these in config for CompleteMEVBot only if compatible
                self.mev_bot.config.router_program_id = router_program_id
                self.mev_bot.config.router_account_metas = router_account_metas
                self.mev_bot.config.router_instruction_data = router_instruction_data
                
            if not router_program_id:
                logger.warning(f"⚠️ [MEV BUY] Router data missing, falling back to default Pump.fun buy instruction")
            # Pass through original_trade_signature if provided
            original_trade_signature = kwargs.get('original_trade_signature')
            
            logger.info(f"🔧 Router configuration for MEV bot:")
            logger.info(f"   Router program ID: {router_program_id}")
            if router_account_metas is not None:
                logger.info(f"   Account metas count: {len(router_account_metas)}")
                expected_index = 0  # Change as needed for your logic
                if len(router_account_metas) <= expected_index:
                    logger.error("PumpFun: accounts_list too short, skipping executor.")
                    return {"success": False, "error": "Malformed transaction data"}
            else:
                logger.info(f"   Account metas count: 0")
            logger.info(f"   Instruction data: {router_instruction_data.hex() if router_instruction_data and hasattr(router_instruction_data, 'hex') else router_instruction_data}")

            logger.info(f"🚀 Executing MEV buy with CompleteMEVBot...")
            signature = await self.mev_bot.execute_buy(mint_address, sol_amount)

            if signature:
                logger.info(f"📡 MEV bot returned signature: {signature}")
                success = await self._verify_transaction_success(signature)
                if success:
                    self.buy_successes += 1
                    logger.info(f"✅ MEV Buy successful: {signature}")
                    return {
                        "success": True,
                        "signature": signature,
                        "sol_amount": sol_amount,
                        "mint": mint_address,
                        "execution_type": "MEV_OPTIMIZED"
                    }
                else:
                    logger.error(f"❌ MEV Buy failed on blockchain: {signature}")
                    return {
                        "success": False,
                        "error": "Transaction failed on blockchain",
                        "signature": signature
                    }
            else:
                logger.error(f"❌ MEV Buy failed for {mint_address} - no signature returned")
                logger.error(f"   This indicates transaction construction or send failure")
                return {"success": False, "error": "No result returned"}
        except Exception as e:
            logger.error(f"❌ MEV Buy exception: {e}", exc_info=True)
            if self.config.debug_mode:
                traceback.print_exc()
            return {"success": False, "error": str(e)}
            
    async def execute_sell_all(
        self,
        mint_address: str,
        transaction_logs: list = None,
        **kwargs
    ) -> BuildResult:
        """
        Execute MEV-optimized sell all tokens, router-aware. Always bundles ATA creation with sell if needed.
        """
        self.sell_attempts += 1
        try:
            if not self.config.enable_sell:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="sell_all",
                    reason="Sell trades disabled"
                )
            logger.info(f"🎯 MEV Sell All: {mint_address}")
            # Check token balance first
            balance = await self.mev_bot.get_token_balance(mint_address)
            if balance == 0:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="sell_all",
                    reason="No tokens to sell"
                )
            logger.info(f"   Selling {balance:,} tokens")
            # Detect router program from logs if provided
            program_id = self._detect_program_from_logs(transaction_logs) if transaction_logs else None
            if program_id and program_id in self.config.supported_routers:
                logger.info(f"🔄 Using router-specific sell for {program_id}")
                router_params = self._extract_router_params(transaction_logs)
                signature = await self.mev_bot._create_router_sell_instruction(
                    Pubkey.from_string(mint_address),
                    balance,
                    int(balance * 0.000001 * 1_000_000_000 * (1 - 0.05)),
                    program_id,
                    router_params
                )
            else:
                # Fallback to direct sell
                signature = await self.mev_bot.execute_sell(mint_address, balance)
            if signature:
                success = await self._verify_transaction_success(signature)
                if success:
                    self.sell_successes += 1
                    logger.info(f"✅ MEV Sell successful: {signature}")
                    return BuildResult(
                        ok=True,
                        tx=None,  # MEV Bot returns signature, not VersionedTransaction
                        dex="pumpfun",
                        action="sell_all",
                        reason=f"MEV Sell successful: {signature}"
                    )
                else:
                    logger.error(f"❌ MEV Sell failed on blockchain: {signature}")
                    return BuildResult(
                        ok=False,
                        tx=None,
                        dex="pumpfun",
                        action="sell_all",
                        reason=f"Transaction failed on blockchain: {signature}"
                    )
            else:
                logger.error(f"❌ MEV Sell failed for {mint_address}")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="sell_all",
                    reason="Transaction failed"
                )
        except Exception as e:
            logger.error(f"❌ MEV Sell exception: {e}")
            if self.config.debug_mode:
                traceback.print_exc()
            return BuildResult(
                ok=False,
                tx=None,
                dex="pumpfun",
                action="sell_all",
                reason=str(e)
            )
    
    async def _verify_transaction_success(self, signature: str) -> bool:
        """Verify transaction actually succeeded on blockchain"""
        try:
            # Use the underlying MEV bot's verification
            return await self.mev_bot.verify_transaction_success(signature)
        except Exception as e:
            logger.error(f"❌ Failed to verify transaction {signature}: {e}")
            return False
    
    # ROUTER SUPPORT METHODS
    def _detect_program_from_logs(self, transaction_logs: list) -> Optional[str]:
        """Detect which Pump.fun program was used from transaction logs"""
        if not transaction_logs:
            return None
            
        log_text = ' '.join(transaction_logs) if isinstance(transaction_logs, list) else str(transaction_logs)
        
        # Check for router programs first (prioritize routers)
        for program_id in self.config.supported_routers:
            if program_id in log_text:
                logger.info(f"🔍 Detected program: {program_id}")
                return program_id
                
        return None
    
    async def _execute_router_buy(self, mint_address: str, sol_amount: float, 
                                 program_id: str, transaction_logs: list) -> Optional[str]:
        """Execute buy using the detected router program"""
        try:
            logger.info(f"🔄 Executing router buy via {program_id}")
            
            # For now, route to the appropriate executor based on program ID
            if program_id == 'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq':
                return await self._execute_f5_router_buy(mint_address, sol_amount, transaction_logs)
            elif program_id == '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC':
                return await self._execute_6h_router_buy(mint_address, sol_amount, transaction_logs)
            else:
                # Fall back to direct execution
                logger.info(f"🎯 Using direct execution for {program_id}")
                return await self.mev_bot.execute_buy(mint_address, sol_amount, transaction_logs)
                
        except Exception as e:
            logger.error(f"❌ Router buy failed: {e}")
            # Fall back to direct execution
            return await self.mev_bot.execute_buy(mint_address, sol_amount, transaction_logs)
    
    async def _execute_f5_router_buy(self, mint_address: str, sol_amount: float, 
                                    transaction_logs: list) -> Optional[str]:
        """Execute buy using F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq router"""
        try:
            logger.info(f"🔄 Using F5 router for {mint_address}")
            
            # For now, analyze the transaction logs to understand the exact structure
            # and then modify the MEV bot to use that structure
            
            # Extract router-specific parameters from logs if available
            router_params = self._extract_router_params(transaction_logs)
            
            # Use MEV bot with router-aware configuration
            # This would need to be implemented in the CompleteMEVBot to support router calls
            return await self.mev_bot.execute_buy_with_router(
                mint_address, 
                sol_amount, 
                router_program='F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq',
                router_params=router_params
            )
            
        except Exception as e:
            logger.error(f"❌ F5 router buy failed: {e}")
            # Fall back to direct
            return await self.mev_bot.execute_buy(mint_address, sol_amount, transaction_logs)
    
    async def _execute_6h_router_buy(self, mint_address: str, sol_amount: float, 
                                    transaction_logs: list) -> Optional[str]:
        """Execute buy using 6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC router"""
        try:
            logger.info(f"🔄 Using 6H router for {mint_address}")
            
            # Similar to F5 router but potentially different parameters
            router_params = self._extract_router_params(transaction_logs)
            
            return await self.mev_bot.execute_buy_with_router(
                mint_address, 
                sol_amount, 
                router_program='6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC',
                router_params=router_params
            )
            
        except Exception as e:
            logger.error(f"❌ 6H router buy failed: {e}")
            # Fall back to direct
            return await self.mev_bot.execute_buy(mint_address, sol_amount, transaction_logs)
    
    def _extract_router_params(self, transaction_logs: list) -> Dict[str, Any]:
        """Extract router-specific parameters from transaction logs"""
        try:
            # This would analyze the logs to extract things like:
            # - Specific router instruction data
            # - Account structure differences
            # - Router-specific settings
            
            params = {
                "router_detected": True,
                "log_count": len(transaction_logs) if transaction_logs else 0,
                "use_router_structure": True
            }
            
            # Add more sophisticated parameter extraction here

            
        except Exception as e:
            logger.error(f"❌ Error verifying transaction {signature}: {e}")
            return False
            
    async def get_token_balance(self, mint_address: str) -> int:
        """Get token balance using MEV bot"""
        return await self.mev_bot.get_token_balance(mint_address)
        
    async def get_sol_balance(self) -> float:
        """Get SOL balance using MEV bot"""
        return await self.mev_bot.get_sol_balance()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        buy_rate = (self.buy_successes / self.buy_attempts * 100) if self.buy_attempts > 0 else 0
        sell_rate = (self.sell_successes / self.sell_attempts * 100) if self.sell_attempts > 0 else 0
        
        return {
            "buy_attempts": self.buy_attempts,
            "buy_successes": self.buy_successes,
            "buy_success_rate": f"{buy_rate:.1f}%",
            "sell_attempts": self.sell_attempts,
            "sell_successes": self.sell_successes,
            "sell_success_rate": f"{sell_rate:.1f}%",
            "total_attempts": self.buy_attempts + self.sell_attempts,
            "total_successes": self.buy_successes + self.sell_successes
        }

# Global MEV executor instance
_mev_executor = None

def get_mev_executor(private_key: str = None) -> MEVPumpFunExecutor:
    """Get or create the global MEV executor instance"""
    global _mev_executor
    
    if _mev_executor is None:
        if private_key is None:
            # Try to get private key from environment
            try:
                env = EnvKeys()
                private_key = env.PHANTOM_PRIVATE_KEY
            except Exception as e:
                logger.error(f"❌ Could not get private key: {e}")
                raise ValueError("Private key required for MEV executor")
                
        _mev_executor = MEVPumpFunExecutor(private_key)
        
    return _mev_executor

# Compatibility functions that match your existing interface
async def try_pumpfun_buy(
    mint_str: str,
    sol_amount: float,
    wallet: Keypair,
    **kwargs
) -> BuildResult:
    """
    MEV-optimized pump.fun buy (replaces old function)
    Returns BuildResult with transaction details
    """
    from models.build_result import BuildResult
    
    try:
        # Get private key from environment since that's what MEV bot expects
        from env_keys import EnvKeys
        env = EnvKeys()
        private_key = env.PHANTOM_PRIVATE_KEY
        
        # Get MEV executor
        executor = get_mev_executor(private_key)
        
        # Execute buy
        result = await executor.execute_buy_copy(mint_str, sol_amount, **kwargs)
        
        if result.ok:
            return BuildResult(
                ok=True,
                tx=result.tx,
                dex="pumpfun",
                action="buy",
                reason=result.reason
            )
        else:
            logger.error(f"MEV buy failed: {result.reason}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="pumpfun",
                action="buy",
                reason=result.reason or 'Unknown error'
            )
            
    except Exception as e:
        logger.error(f"❌ try_pumpfun_buy failed: {e}")
        return BuildResult(
            ok=False,
            tx=None,
            dex="pumpfun",
            action="buy",
            reason=str(e)
        )

async def try_pumpfun_sell_all(
    mint_str: str,
    wallet: Keypair,
    **kwargs
) -> BuildResult:
    """
    MEV-optimized pump.fun sell all (replaces old function)
    Returns BuildResult with transaction details
    """
    from models.build_result import BuildResult
    
    try:
        # Get private key from environment since that's what MEV bot expects
        from env_keys import EnvKeys
        env = EnvKeys()
        private_key = env.PHANTOM_PRIVATE_KEY
        
        # Get MEV executor
        executor = get_mev_executor(private_key)
        
        # Execute sell
        result = await executor.execute_sell_all(mint_str, **kwargs)
        
        if result.ok:
            return BuildResult(
                ok=True,
                tx=result.tx,
                dex="pumpfun",
                action="sell_all",
                reason=result.reason
            )
        else:
            logger.error(f"MEV sell failed: {result.reason}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="pumpfun",
                action="sell_all",
                reason=result.reason or 'Unknown error'
            )
            
    except Exception as e:
        logger.error(f"❌ try_pumpfun_sell_all failed: {e}")
        return BuildResult(
            ok=False,
            tx=None,
            dex="pumpfun",
            action="sell_all",
            reason=str(e)
        )

# Legacy class name for compatibility
class PumpFunCopyExecutor(MEVPumpFunExecutor):
    """Legacy class name for backward compatibility"""
    pass

# Test function
async def test_mev_executor():
    """Test the MEV executor"""
    try:
        env = EnvKeys()
        private_key = env.PHANTOM_PRIVATE_KEY
        
        if not private_key:
            print("❌ No private key found")
            return
            
        executor = MEVPumpFunExecutor(private_key)
        
        # Test balance check
        sol_balance = await executor.get_sol_balance()
        print(f"💰 SOL Balance: {sol_balance:.6f}")
        
        # Show stats
        stats = executor.get_stats()
        print(f"📊 Stats: {stats}")
        
        print("✅ MEV Executor test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mev_executor())
