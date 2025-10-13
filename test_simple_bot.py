#!/usr/bin/env python3
"""
Quick dependency test for simplified copy trading bot
"""

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🧪 Testing Simple Copy Trading Bot Dependencies...")
    print("=" * 60)
    
    missing_deps = []
    available_deps = []
    
    # Test core imports
    dependencies = [
        ('websocket_handler', 'create_websocket_handler'),
        ('execution_coordinator', 'ExecutionCoordinator'),
        ('copy_trade_logger', 'get_copy_trade_logger'),
        ('official_wallet_perspective_analyzer', 'OfficialWalletPerspectiveAnalyzer'),
        ('env_keys', 'EnvKeys'),
        ('config', 'WALLET'),
        ('utils', 'get_transaction_with_logs'),
    ]
    
    for module_name, class_name in dependencies:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            available_deps.append(f"✅ {module_name}.{class_name}")
        except ImportError as e:
            missing_deps.append(f"❌ {module_name}.{class_name} - {e}")
        except AttributeError as e:
            missing_deps.append(f"❌ {module_name}.{class_name} - {e}")
    
    print("\n📋 Dependency Status:")
    for dep in available_deps:
        print(f"   {dep}")
    
    if missing_deps:
        print(f"\n🚨 Missing Dependencies ({len(missing_deps)}):")
        for dep in missing_deps:
            print(f"   {dep}")
        print(f"\n❌ Bot cannot run - {len(missing_deps)} dependencies missing")
        return False
    else:
        print(f"\n✅ All {len(available_deps)} dependencies available!")
        print("🎯 Your simple copy trading bot should work properly.")
        return True

def test_configuration():
    """Test if configuration is properly set"""
    print("\n🔧 Testing Configuration...")
    
    try:
        from main import CopyTradeConfig
        
        # Test configuration
        config = CopyTradeConfig(
            target_wallets=[
                "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
                "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
            ],
            investment_amount_sol=0.001,  # Fixed: MEV executor minimum requirement
            use_jito=True,
            slippage_tolerance=0.15
        )
        
        print("✅ Configuration class working")
        print(f"   🎯 Target wallets: {len(config.target_wallets)}")
        print(f"   💰 Investment amount: {config.investment_amount_sol} SOL")
        print(f"   🚀 Jito enabled: {config.use_jito}")
        print(f"   📊 Slippage tolerance: {config.slippage_tolerance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_bot_creation():
    """Test if the bot can be created without errors"""
    print("\n🤖 Testing Bot Creation...")
    
    try:
        from main import SimpleCopyTradingBot, CopyTradeConfig
        
        config = CopyTradeConfig(
            target_wallets=[
                "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
                "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
            ],
            investment_amount_sol=0.001  # Fixed: MEV executor minimum requirement
        )
        
        # Try to create bot instance
        bot = SimpleCopyTradingBot(config)
        
        print("✅ Bot created successfully")
        print(f"   🎯 Monitoring {len(bot.target_wallets)} wallets")
        print(f"   💰 Investment per trade: {config.investment_amount_sol} SOL")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 Simple Copy Trading Bot - Dependency Test")
    print("=" * 60)
    
    deps_ok = test_dependencies()
    config_ok = test_configuration()
    bot_ok = test_bot_creation()
    
    print("\n" + "=" * 60)
    if deps_ok and config_ok and bot_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your simple copy trading bot is ready to run!")
        print("\n📋 Next steps:")
        print("   1. Run: python3 main.py")
        print("   2. Watch for trade detections from your target wallets")
        print("   3. Monitor the copy executions")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please fix the issues above before running the bot")
