"""
🧪 MODULE VALIDATION SCRIPT
Tests that all modular components can be imported and initialized
Run this before using the new system to ensure everything works
"""

import asyncio
import logging
import traceback
from typing import Dict, Any

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModuleValidator:
    """Validates all modular components"""
    
    def __init__(self):
        self.results = {}
        self.all_passed = True
    
    def test_import(self, module_name: str, import_func):
        """Test importing a module"""
        try:
            result = import_func()
            self.results[module_name] = {
                'status': 'PASS',
                'message': 'Successfully imported',
                'details': result
            }
            logger.info(f"✅ {module_name}: PASS")
            return True
        except Exception as e:
            self.results[module_name] = {
                'status': 'FAIL', 
                'message': str(e),
                'details': traceback.format_exc()
            }
            logger.error(f"❌ {module_name}: FAIL - {e}")
            self.all_passed = False
            return False
    
    def test_config_availability(self):
        """Test configuration imports"""
        def import_config():
            from config import CopyTradeConfig, EnvKeys, WALLET
            return {
                'CopyTradeConfig': CopyTradeConfig,
                'EnvKeys': EnvKeys, 
                'WALLET': WALLET
            }
        
        return self.test_import("Configuration (config.py)", import_config)
    
    def test_trading_coordinator(self):
        """Test trading coordinator import"""
        def import_coordinator():
            from trading_coordinator import TradingCoordinator, create_trading_coordinator
            return {
                'TradingCoordinator': TradingCoordinator,
                'create_trading_coordinator': create_trading_coordinator
            }
        
        return self.test_import("Trading Coordinator", import_coordinator)
    
    def test_socket_detector(self):
        """Test socket trade detector import"""
        def import_socket():
            from socket_trade_detector import SocketTradeDetector
            return {'SocketTradeDetector': SocketTradeDetector}
        
        return self.test_import("Socket Trade Detector", import_socket)
    
    def test_jito_executor(self):
        """Test Jito trade executor import"""
        def import_jito():
            from jito_trade_executor import JitoTradeExecutor, JitoTradeExecutorManager
            return {
                'JitoTradeExecutor': JitoTradeExecutor,
                'JitoTradeExecutorManager': JitoTradeExecutorManager
            }
        
        return self.test_import("Jito Trade Executor", import_jito)
    
    def test_modular_executor(self):
        """Test modular executor manager import"""
        def import_modular():
            from modular_executor_manager import ModularExecutorManager, create_executor_manager
            return {
                'ModularExecutorManager': ModularExecutorManager,
                'create_executor_manager': create_executor_manager
            }
        
        return self.test_import("Modular Executor Manager", import_modular)
    
    def test_transaction_analyzer(self):
        """Test transaction analyzer import"""
        def import_analyzer():
            from transaction_analyzer import TransactionAnalyzer, create_transaction_analyzer
            return {
                'TransactionAnalyzer': TransactionAnalyzer,
                'create_transaction_analyzer': create_transaction_analyzer
            }
        
        return self.test_import("Transaction Analyzer", import_analyzer)
    
    def test_existing_executors(self):
        """Test your existing executor imports"""
        executors = [
            ("Pump.fun Executor", lambda: __import__('pumpfun_copy_executor')),
            ("Jupiter Executor", lambda: __import__('jupiter_copy_executor')),
            ("Raydium Executor", lambda: __import__('raydium_copy_executor')),
            ("CPMM Executor", lambda: __import__('cpmm_copy_executor')),
            ("CLMM Executor", lambda: __import__('clmm_copy_executor')),
            ("Orca Executor", lambda: __import__('orca_copy_executor')),
            ("Phoenix Executor", lambda: __import__('phoenix_copy_executor')),
            ("Fast Executor", lambda: __import__('fast_executor'))
        ]
        
        for name, import_func in executors:
            self.test_import(name, import_func)
    
    def test_supporting_modules(self):
        """Test supporting module imports"""
        supporting = [
            ("Official Wallet Analyzer", lambda: __import__('official_wallet_perspective_analyzer')),
            ("Wallet TX Parser", lambda: __import__('wallet_tx_parser')),
            ("Copy Trade Logger", lambda: __import__('copy_trade_logger')),
            ("Jito Enhanced Service", lambda: __import__('jito_enhanced_service'))
        ]
        
        for name, import_func in supporting:
            self.test_import(name, import_func)
    
    async def test_basic_initialization(self):
        """Test basic initialization of key components"""
        logger.info("\n🔧 Testing basic component initialization...")
        
        try:
            # Test config creation
            from config import CopyTradeConfig
            test_config = CopyTradeConfig(
                target_wallets=["test_wallet"],
                investment_amount_sol=0.001,
                use_jito=True,
                enable_dexes={"pumpfun": True}
            )
            logger.info("✅ Config creation: PASS")
            
            # Test RPC client creation
            from solana.rpc.async_api import AsyncClient
            rpc_client = AsyncClient("https://api.devnet.solana.com")
            logger.info("✅ RPC client creation: PASS")
            
            # Clean up
            await rpc_client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Basic initialization: FAIL - {e}")
            return False
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 MODULE VALIDATION SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        total = len(self.results)
        
        print(f"\n📈 Results: {passed}/{total} modules passed ({passed/total*100:.1f}%)")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print(f"\n❌ FAILED MODULES:")
            for name, result in self.results.items():
                if result['status'] == 'FAIL':
                    print(f"   • {name}: {result['message']}")
        
        print(f"\n{'🎉 ALL MODULES READY!' if self.all_passed else '⚠️ SOME MODULES NEED ATTENTION'}")
        
        if self.all_passed:
            print("\n✅ Your modular system is ready to use!")
            print("   You can now replace your main.py with clean_main_v2.py")
            print("   Remember to update target wallets and investment amounts")
        else:
            print("\n❌ Please fix the failed modules before proceeding")
            print("   Check import paths and missing dependencies")

async def main():
    """Run module validation"""
    print("🧪 MODULAR SYSTEM VALIDATION")
    print("=" * 40)
    print("Testing all modules for your clean copy trading system...")
    print()
    
    validator = ModuleValidator()
    
    # Test all modules
    logger.info("🔍 Testing core configuration...")
    validator.test_config_availability()
    
    logger.info("\n🔍 Testing new modular components...")
    validator.test_trading_coordinator()
    validator.test_socket_detector()
    validator.test_jito_executor()
    validator.test_modular_executor()
    validator.test_transaction_analyzer()
    
    logger.info("\n🔍 Testing existing executors...")
    validator.test_existing_executors()
    
    logger.info("\n🔍 Testing supporting modules...")
    validator.test_supporting_modules()
    
    logger.info("\n🔍 Testing basic initialization...")
    await validator.test_basic_initialization()
    
    # Print summary
    validator.print_summary()
    
    return validator.all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
