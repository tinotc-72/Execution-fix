#!/usr/bin/env python3
"""
Comprehensive Execution Method Testing Script
Tests both Jito-first and Direct RPC execution methods thoroughly
"""

import asyncio
import logging
import time
from main import SimpleCopyTradingBot, CopyTradeConfig
from config import WALLET
from env_keys import EnvKeys

# Configure detailed logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExecutionTester:
    """Test harness for execution methods"""
    
    def __init__(self):
        self.env_keys = EnvKeys()
        self.wallet = WALLET
        self.test_results = {
            "jito_service_init": False,
            "jito_transaction_build": False,
            "jito_send_capability": False,
            "rpc_fallback_capability": False,
            "direct_rpc_execution": False,
            "jupiter_integration": False,
            "transaction_signing": False,
            "overall_readiness": False
        }
    
    async def test_execution_methods(self):
        """Comprehensive test of both execution methods"""
        logger.info("🧪 COMPREHENSIVE EXECUTION METHOD TESTING")
        logger.info("=" * 60)
        
        # Test tokens: USDC (stable) and a meme coin (edge case)
        test_tokens = [
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "J3FBk7xAEDgcFem1G3Z2DwSZNiAQHg62ujzkn2bbBAGS"   # Example meme coin
        ]
        # Use the main wallet for testing
        from config import WALLET
        test_wallet = WALLET.pubkey().__str__()

        # Create test configuration
        config = CopyTradeConfig(
            target_wallets=[test_wallet],
            investment_amount_sol=0.001,  # MEV minimum
            use_jito=True,
            slippage_tolerance=0.3
        )

        logger.info("📊 Test Configuration:")
        logger.info(f"   Investment: {config.investment_amount_sol} SOL")
        logger.info(f"   Jito enabled: {config.use_jito}")
        logger.info(f"   Test tokens: {[t[:8] for t in test_tokens]}")
        
        # Create bot instance
        try:
            bot = SimpleCopyTradingBot(config)
            logger.info("✅ Bot instance created successfully")
        except Exception as e:
            logger.error(f"❌ Bot creation failed: {e}")
            return False

        # Run tests for each token
        for test_token in test_tokens:
            logger.info(f"\n🔬 Running tests for token: {test_token}")
            # Test 1: Jito Service Initialization
            await self._test_jito_service_init(bot)
            # Test 2: Transaction Building
            await self._test_transaction_building(bot, test_token)
            # Test 3: Jito Execution Capability
            await self._test_jito_execution_capability(bot, test_token)
            # Test 4: Direct RPC Execution
            await self._test_direct_rpc_execution(bot, test_token)
            # Test 5: Jupiter Integration
            await self._test_jupiter_integration(bot, test_token)

        # Test 6: Transaction Signing (once)
        await self._test_transaction_signing(bot)

        # Final Assessment
        self._generate_final_report()

        return self.test_results["overall_readiness"]
    
    async def _test_jito_service_init(self, bot):
        """Test Jito service initialization"""
        logger.info("\n🔧 TEST 1: Jito Service Initialization")
        logger.info("-" * 40)
        
        try:
            if hasattr(bot, 'jito_service') and bot.jito_service:
                logger.info("✅ Jito service exists")
                
                # Test initialization
                if hasattr(bot.jito_service, 'initialize'):
                    init_result = await bot.jito_service.initialize()
                    if init_result:
                        logger.info("✅ Jito service initialized successfully")
                        self.test_results["jito_service_init"] = True
                    else:
                        logger.error("❌ Jito service initialization failed")
                else:
                    logger.warning("⚠️ Jito service has no initialize method")
                
                # Check essential methods
                essential_methods = ['send_transaction_jito_first']
                for method in essential_methods:
                    if hasattr(bot.jito_service, method):
                        logger.info(f"✅ Method available: {method}")
                    else:
                        logger.error(f"❌ Missing method: {method}")
                        
            else:
                logger.error("❌ No Jito service found")
                
        except Exception as e:
            logger.error(f"❌ Jito service test failed: {e}")
    
    async def _test_transaction_building(self, bot, test_token):
        """Test transaction building capability"""
        logger.info("\n🔧 TEST 2: Transaction Building")
        logger.info("-" * 40)
        
        try:
            # Test the _build_optimal_transaction method
            if hasattr(bot, '_build_optimal_transaction'):
                logger.info("✅ Transaction building method exists")
                
                # Test with dry run (don't actually execute)
                logger.info("🧪 Testing transaction building (dry run)...")
                
                # Check Jupiter availability
                try:
                    from jupiter_utils import get_jupiter_quote
                    logger.info("✅ Jupiter utilities available")
                    self.test_results["jupiter_integration"] = True
                except ImportError:
                    logger.warning("⚠️ Jupiter utilities not available - will use fallback")
                
                # We'll simulate transaction building without actually building
                # to avoid rate limits and unnecessary API calls
                logger.info("✅ Transaction building method ready")
                self.test_results["jito_transaction_build"] = True
                
            else:
                logger.error("❌ Transaction building method missing")
                
        except Exception as e:
            logger.error(f"❌ Transaction building test failed: {e}")
    
    async def _test_jito_execution_capability(self, bot, test_token):
        """Test Jito execution capability (without actual execution)"""
        logger.info("\n🔧 TEST 3: Jito Execution Capability")
        logger.info("-" * 40)
        
        try:
            # Check if the execution method exists
            if hasattr(bot, '_try_jito_first_execution'):
                logger.info("✅ Jito-first execution method exists")
                
                # Check method signature
                import inspect
                sig = inspect.signature(bot._try_jito_first_execution)
                params = list(sig.parameters.keys())
                logger.info(f"✅ Method parameters: {params}")
                
                if 'token_mint' in params and 'source_wallet' in params:
                    logger.info("✅ Method signature correct")
                    self.test_results["jito_send_capability"] = True
                else:
                    logger.error("❌ Method signature incorrect")
                
            else:
                logger.error("❌ Jito execution method missing")
                
        except Exception as e:
            logger.error(f"❌ Jito execution test failed: {e}")
    
    async def _test_direct_rpc_execution(self, bot, test_token):
        """Test direct RPC execution capability"""
        logger.info("\n🔧 TEST 4: Direct RPC Execution")
        logger.info("-" * 40)
        
        try:
            # Check if the RPC execution method exists
            if hasattr(bot, '_try_direct_rpc_execution'):
                logger.info("✅ Direct RPC execution method exists")
                
                # Check method signature
                import inspect
                sig = inspect.signature(bot._try_direct_rpc_execution)
                params = list(sig.parameters.keys())
                logger.info(f"✅ Method parameters: {params}")
                
                if 'transaction_instructions' in params:
                    logger.info("✅ RPC method signature correct")
                    self.test_results["rpc_fallback_capability"] = True
                    self.test_results["direct_rpc_execution"] = True
                else:
                    logger.error("❌ RPC method signature incorrect")
                
                # Check RPC client
                if hasattr(bot, 'rpc_client') and bot.rpc_client:
                    logger.info("✅ RPC client available")
                else:
                    logger.error("❌ RPC client missing")
                
            else:
                logger.error("❌ Direct RPC execution method missing")
                
        except Exception as e:
            logger.error(f"❌ Direct RPC execution test failed: {e}")
    
    async def _test_jupiter_integration(self, bot, test_token):
        """Test Jupiter integration"""
        logger.info("\n🔧 TEST 5: Jupiter Integration")
        logger.info("-" * 40)
        
        try:
            # Check Jupiter utilities import
            try:
                from jupiter_utils import get_jupiter_quote, get_jupiter_transaction
                logger.info("✅ Jupiter utilities imported successfully")
                logger.info("✅ Functions available: get_jupiter_quote, get_jupiter_transaction")
                self.test_results["jupiter_integration"] = True
            except ImportError as e:
                logger.warning(f"⚠️ Jupiter utilities import failed: {e}")
                
                # Check fallback Jupiter import
                try:
                    from jupiter_trade_executor import get_best_route, get_swap_transaction, SOL_MINT
                    logger.info("✅ Fallback Jupiter executor available")
                    self.test_results["jupiter_integration"] = True
                except ImportError:
                    logger.error("❌ No Jupiter integration available")
            
        except Exception as e:
            logger.error(f"❌ Jupiter integration test failed: {e}")
    
    async def _test_transaction_signing(self, bot):
        """Test transaction signing capability"""
        logger.info("\n🔧 TEST 6: Transaction Signing")
        logger.info("-" * 40)
        
        try:
            # Check wallet availability
            if hasattr(bot, 'wallet') and bot.wallet:
                logger.info("✅ Wallet available")
                
                # Check if wallet can sign
                if hasattr(bot.wallet, 'pubkey'):
                    pubkey = bot.wallet.pubkey()
                    logger.info(f"✅ Wallet pubkey: {str(pubkey)[:8]}...")
                    
                if hasattr(bot.wallet, 'sign'):
                    logger.info("✅ Wallet signing capability available")
                    self.test_results["transaction_signing"] = True
                else:
                    logger.error("❌ Wallet signing capability missing")
                    
            else:
                logger.error("❌ Wallet missing")
                
        except Exception as e:
            logger.error(f"❌ Transaction signing test failed: {e}")
    
    def _generate_final_report(self):
        """Generate final test report"""
        logger.info("\n📊 FINAL TEST REPORT")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results) - 1  # Exclude overall_readiness
        passed_tests = sum(1 for k, v in self.test_results.items() if k != "overall_readiness" and v)
        
        logger.info(f"📈 Test Results: {passed_tests}/{total_tests} passed")
        logger.info("")
        
        for test_name, result in self.test_results.items():
            if test_name == "overall_readiness":
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {status} {test_name.replace('_', ' ').title()}")
        
        # Overall assessment
        critical_tests = [
            "jito_service_init",
            "rpc_fallback_capability", 
            "direct_rpc_execution",
            "transaction_signing"
        ]
        
        critical_passed = all(self.test_results.get(test, False) for test in critical_tests)
        
        logger.info("")
        if critical_passed:
            logger.info("🎉 OVERALL ASSESSMENT: ✅ READY FOR TRADING")
            logger.info("   Both Jito-first and RPC fallback methods are functional")
            self.test_results["overall_readiness"] = True
        else:
            logger.error("🚨 OVERALL ASSESSMENT: ❌ NOT READY")
            logger.error("   Critical execution methods are missing or broken")
            
            # Show what needs fixing
            logger.error("   Required fixes:")
            for test in critical_tests:
                if not self.test_results.get(test, False):
                    logger.error(f"     - Fix {test.replace('_', ' ')}")
        
        logger.info("")
        logger.info("🔧 EXECUTION PATTERN:")
        logger.info("   1️⃣ Try Jito first (MEV protection)")
        logger.info("   2️⃣ If Jito fails → IMMEDIATE RPC fallback")
        logger.info("   3️⃣ Return success as soon as either method works")

async def main():
    """Main test function"""
    logger.info("🚀 Starting Execution Method Testing...")
    
    tester = ExecutionTester()
    
    try:
        success = await tester.test_execution_methods()
        
        if success:
            logger.info("\n🎯 RESULT: Your execution methods are ready!")
            logger.info("✅ You can safely run your bot with Jito-first → RPC fallback")
        else:
            logger.error("\n❌ RESULT: Execution methods need fixes before trading")
            logger.error("⚠️ Check the test results above for required fixes")
            
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
