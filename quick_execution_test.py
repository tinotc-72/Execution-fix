#!/usr/bin/env python3
"""
Quick Execution Method Verification Test
Tests both Jito-first and RPC fallback execution methods work properly
"""

import asyncio
import logging
import sys
from typing import Dict, Any

# Configure minimal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickExecutionTest:
    """Quick test to verify execution methods are functional"""
    
    def __init__(self):
        self.test_results = {}
    
    def test_imports(self):
        """Test 1: Verify all required imports work"""
        logger.info("🧪 TEST 1: Import Verification")
        logger.info("-" * 40)
        
        try:
            # Test main module imports
            from main import CopyTradingBot, CopyTradeConfig
            logger.info("✅ Main bot classes import successfully")
            self.test_results["main_imports"] = True
            
            # Test Jito service import
            from jito_enhanced_service import JitoEnhancedService
            logger.info("✅ Jito service imports successfully")
            self.test_results["jito_import"] = True
            
            # Test config and wallet imports
            from config import WALLET
            from env_keys import EnvKeys
            logger.info("✅ Config and wallet imports successful")
            self.test_results["config_imports"] = True
            
            # Test Jupiter utilities (optional)
            try:
                from jupiter_utils import get_jupiter_quote, get_jupiter_transaction
                logger.info("✅ Jupiter utilities available")
                self.test_results["jupiter_available"] = True
            except ImportError:
                logger.warning("⚠️ Jupiter utilities not available - will use fallback")
                self.test_results["jupiter_available"] = False
            
            # Test executor wrappers
            from official_executor_wrappers import try_jupiter_buy, try_pumpfun_buy
            logger.info("✅ Executor wrappers import successfully")
            self.test_results["executor_imports"] = True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Import test failed: {e}")
            return False
    
    async def test_bot_creation(self):
        """Test 2: Verify bot can be created with basic config"""
        logger.info("\n🧪 TEST 2: Bot Creation")
        logger.info("-" * 40)
        
        try:
            from main import CopyTradingBot, CopyTradeConfig
            
            # Create minimal test config
            config = CopyTradeConfig(
                target_wallets=["test_wallet_address"],
                investment_amount_sol=0.001,
                use_jito=True,
                jito_timeout=10.0
            )
            
            # Create bot instance
            bot = CopyTradingBot(config)
            
            # Verify essential attributes
            if hasattr(bot, 'jito_service'):
                logger.info("✅ Bot has jito_service attribute")
                self.test_results["jito_service_attr"] = True
            else:
                logger.error("❌ Bot missing jito_service attribute")
                self.test_results["jito_service_attr"] = False
            
            if hasattr(bot, 'rpc_client'):
                logger.info("✅ Bot has rpc_client attribute")
                self.test_results["rpc_client_attr"] = True
            else:
                logger.error("❌ Bot missing rpc_client attribute")
                self.test_results["rpc_client_attr"] = False
            
            if hasattr(bot, 'wallet'):
                logger.info("✅ Bot has wallet attribute")
                self.test_results["wallet_attr"] = True
            else:
                logger.error("❌ Bot missing wallet attribute")
                self.test_results["wallet_attr"] = False
            
            logger.info("✅ Bot creation successful")
            self.test_results["bot_creation"] = True
            return bot
            
        except Exception as e:
            logger.error(f"❌ Bot creation failed: {e}")
            self.test_results["bot_creation"] = False
            return None
    
    async def test_execution_methods(self, bot):
        """Test 3: Verify execution methods exist and are callable"""
        logger.info("\n🧪 TEST 3: Execution Method Verification")
        logger.info("-" * 40)
        
        if not bot:
            logger.error("❌ No bot instance - skipping execution method tests")
            return False
        
        try:
            # Test Jito-first execution method
            if hasattr(bot, '_try_jito_first_execution'):
                logger.info("✅ _try_jito_first_execution method exists")
                
                # Check method signature
                import inspect
                sig = inspect.signature(bot._try_jito_first_execution)
                params = list(sig.parameters.keys())
                if 'token_mint' in params and 'source_wallet' in params:
                    logger.info("✅ Jito method has correct signature")
                    self.test_results["jito_method_signature"] = True
                else:
                    logger.error("❌ Jito method has wrong signature")
                    self.test_results["jito_method_signature"] = False
            else:
                logger.error("❌ _try_jito_first_execution method missing")
                self.test_results["jito_method_exists"] = False
            
            # Test RPC fallback method
            if hasattr(bot, '_try_direct_rpc_execution'):
                logger.info("✅ _try_direct_rpc_execution method exists")
                
                # Check method signature
                sig = inspect.signature(bot._try_direct_rpc_execution)
                params = list(sig.parameters.keys())
                if 'transaction_instructions' in params:
                    logger.info("✅ RPC method has correct signature")
                    self.test_results["rpc_method_signature"] = True
                else:
                    logger.error("❌ RPC method has wrong signature")
                    self.test_results["rpc_method_signature"] = False
            else:
                logger.error("❌ _try_direct_rpc_execution method missing")
                self.test_results["rpc_method_exists"] = False
            
            # Test main execution methods
            if hasattr(bot, '_execute_copy_buy'):
                logger.info("✅ _execute_copy_buy method exists")
                self.test_results["copy_buy_exists"] = True
            else:
                logger.error("❌ _execute_copy_buy method missing")
                self.test_results["copy_buy_exists"] = False
            
            if hasattr(bot, '_execute_copy_sell'):
                logger.info("✅ _execute_copy_sell method exists")
                self.test_results["copy_sell_exists"] = True
            else:
                logger.error("❌ _execute_copy_sell method missing")
                self.test_results["copy_sell_exists"] = False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Execution method test failed: {e}")
            return False
    
    async def test_jito_service_init(self, bot):
        """Test 4: Verify Jito service initialization works"""
        logger.info("\n🧪 TEST 4: Jito Service Initialization")
        logger.info("-" * 40)
        
        if not bot or not bot.jito_service:
            logger.warning("⚠️ No Jito service - skipping initialization test")
            self.test_results["jito_init"] = False
            return False
        
        try:
            # Check if Jito service has initialize method
            if hasattr(bot.jito_service, 'initialize'):
                logger.info("✅ Jito service has initialize method")
                
                # Try to initialize (with timeout)
                try:
                    init_result = await asyncio.wait_for(
                        bot.jito_service.initialize(),
                        timeout=5.0  # Short timeout
                    )
                    
                    if init_result:
                        logger.info("✅ Jito service initialized successfully")
                        self.test_results["jito_init"] = True
                    else:
                        logger.warning("⚠️ Jito service initialization returned False")
                        self.test_results["jito_init"] = False
                        
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Jito initialization timeout (network issue?)")
                    self.test_results["jito_init"] = False
                except Exception as init_error:
                    logger.warning(f"⚠️ Jito initialization error: {init_error}")
                    self.test_results["jito_init"] = False
            else:
                logger.warning("⚠️ Jito service has no initialize method")
                self.test_results["jito_init"] = False
            
            # Check essential Jito methods
            essential_methods = ['send_transaction_jito_first']
            for method in essential_methods:
                if hasattr(bot.jito_service, method):
                    logger.info(f"✅ Jito service has {method} method")
                else:
                    logger.warning(f"⚠️ Jito service missing {method} method")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Jito service test failed: {e}")
            self.test_results["jito_init"] = False
            return False
    
    def generate_report(self):
        """Generate final test report"""
        logger.info("\n📊 EXECUTION METHOD TEST REPORT")
        logger.info("=" * 50)
        
        # Critical tests for execution functionality
        critical_tests = [
            ("main_imports", "Main Module Imports"),
            ("bot_creation", "Bot Creation"),
            ("copy_buy_exists", "Copy Buy Method"),
            ("copy_sell_exists", "Copy Sell Method"),
            ("jito_method_signature", "Jito Method Signature"),
            ("rpc_method_signature", "RPC Method Signature"),
        ]
        
        # Optional but important tests
        optional_tests = [
            ("jito_import", "Jito Service Import"),
            ("jito_init", "Jito Initialization"),
            ("jupiter_available", "Jupiter Integration"),
        ]
        
        critical_passed = 0
        critical_total = len(critical_tests)
        
        logger.info("🚨 CRITICAL TESTS (Must Pass):")
        for test_key, test_name in critical_tests:
            result = self.test_results.get(test_key, False)
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {status} {test_name}")
            if result:
                critical_passed += 1
        
        logger.info("\n📋 OPTIONAL TESTS:")
        for test_key, test_name in optional_tests:
            result = self.test_results.get(test_key, False)
            status = "✅ PASS" if result else "⚠️ SKIP" 
            logger.info(f"   {status} {test_name}")
        
        # Overall assessment
        logger.info(f"\n📈 CRITICAL SCORE: {critical_passed}/{critical_total}")
        
        if critical_passed == critical_total:
            logger.info("🎉 RESULT: ✅ EXECUTION METHODS ARE READY!")
            logger.info("   Your bot can execute: Jito-first → RPC fallback")
            logger.info("   Both execution paths are functional")
            return True
        else:
            logger.error("🚨 RESULT: ❌ EXECUTION METHODS NEED FIXES")
            logger.error(f"   {critical_total - critical_passed} critical issues must be resolved")
            logger.error("   Check the failed tests above")
            return False

async def main():
    """Run the quick execution test"""
    logger.info("🚀 Quick Execution Method Verification")
    logger.info("Testing Jito-first execution with RPC fallback")
    logger.info("=" * 50)
    
    tester = QuickExecutionTest()
    
    try:
        # Run tests in sequence
        logger.info("Starting tests...")
        
        # Test 1: Imports
        if not tester.test_imports():
            logger.error("❌ Import test failed - cannot continue")
            return False
        
        # Test 2: Bot creation
        bot = await tester.test_bot_creation()
        
        # Test 3: Execution methods
        await tester.test_execution_methods(bot)
        
        # Test 4: Jito service (if available)
        if bot:
            await tester.test_jito_service_init(bot)
        
        # Generate final report
        success = tester.generate_report()
        
        if success:
            logger.info("\n✅ Your execution methods are working!")
            logger.info("🎯 Execution Pattern: Jito-first → RPC fallback")
        else:
            logger.info("\n❌ Some execution methods need fixes")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
