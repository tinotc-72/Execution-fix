#!/usr/bin/env python3
"""
Copy Bot System Status - Comprehensive Integration Check
"""

import sys
import traceback

def test_core_system():
    """Test core system components"""
    print("🔍 COPY BOT SYSTEM STATUS REPORT")
    print("=" * 60)
    
    issues = []
    successes = []
    
    # Test 1: Core Imports
    print("\n1. 📦 CORE IMPORTS")
    print("-" * 30)
    
    try:
        from main import SimpleCopyTradingBot, CopyTradeConfig
        successes.append("✅ Main bot classes")
        print("✅ Main bot classes imported")
    except Exception as e:
        issues.append(f"❌ Main bot classes: {e}")
        print(f"❌ Main bot classes: {e}")
    
    try:
        from execution_coordinator import ExecutionCoordinator
        successes.append("✅ Execution coordinator")
        print("✅ Execution coordinator imported")
    except Exception as e:
        issues.append(f"❌ Execution coordinator: {e}")
        print(f"❌ Execution coordinator: {e}")
    
    try:
        from trade_processor import TradeProcessor
        successes.append("✅ Trade processor")
        print("✅ Trade processor imported")
    except Exception as e:
        issues.append(f"❌ Trade processor: {e}")
        print(f"❌ Trade processor: {e}")
    
    # Test 2: Executor Imports
    print("\n2. ⚡ EXECUTOR IMPORTS")
    print("-" * 30)
    
    executors_to_test = [
        ("Pump.fun MEV", "pumpfun_CC_copy_executor", "try_pumpfun_buy"),
        ("Raydium", "raydium_copy_executor", "try_raydium_buy"),
        ("Jupiter", "official_executor_wrappers", "try_jupiter_buy"),
        ("Orca", "official_executor_wrappers", "try_orca_buy"),
        ("Phoenix", "official_executor_wrappers", "try_phoenix_buy"),
    ]
    
    for name, module, function in executors_to_test:
        try:
            exec(f"from {module} import {function}")
            successes.append(f"✅ {name} executor")
            print(f"✅ {name} executor imported")
        except Exception as e:
            issues.append(f"❌ {name} executor: {e}")
            print(f"❌ {name} executor: {e}")
    
    # Test 3: System Services
    print("\n3. 🔧 SYSTEM SERVICES")
    print("-" * 30)
    
    try:
        from env_keys import EnvKeys
        env = EnvKeys()
        successes.append("✅ Environment configuration")
        print("✅ Environment configuration loaded")
        print(f"   🔗 RPC: {env.HELIUS_RPC_URL[:50]}...")
        print(f"   📡 WebSocket: {env.HELIUS_WS_URL[:50]}...")
    except Exception as e:
        issues.append(f"❌ Environment configuration: {e}")
        print(f"❌ Environment configuration: {e}")
    
    try:
        from websocket_handler import WebSocketHandler
        successes.append("✅ WebSocket handler")
        print("✅ WebSocket handler imported")
    except Exception as e:
        issues.append(f"❌ WebSocket handler: {e}")
        print(f"❌ WebSocket handler: {e}")
    
    try:
        from config import WALLET
        successes.append("✅ Wallet configuration")
        print("✅ Wallet configuration loaded")
        print(f"   📱 Public Key: {WALLET.pubkey()}")
    except Exception as e:
        issues.append(f"❌ Wallet configuration: {e}")
        print(f"❌ Wallet configuration: {e}")
    
    # Test 4: Bot Creation
    print("\n4. 🤖 BOT CREATION TEST")
    print("-" * 30)
    
    try:
        config = CopyTradeConfig(
            target_wallets=['suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK'],
            investment_amount_sol=0.001,
            use_jito=True
        )
        bot = SimpleCopyTradingBot(config)
        successes.append("✅ Bot instance creation")
        print("✅ Bot instance created successfully")
        print(f"   🎯 Target wallets: {len(config.target_wallets)}")
        print(f"   💰 Investment: {config.investment_amount_sol} SOL")
        print(f"   🚀 Jito enabled: {config.use_jito}")
        print(f"   🛡️ MEV protection: {'✅' if bot.jito_service else '❌'}")
        
        # Test components
        if hasattr(bot, 'execution_coordinator') and bot.execution_coordinator:
            successes.append("✅ Execution coordinator initialized")
            print("✅ Execution coordinator initialized")
        else:
            issues.append("❌ Execution coordinator not initialized")
            print("❌ Execution coordinator not initialized")
            
        if hasattr(bot, 'trade_processor') and bot.trade_processor:
            successes.append("✅ Trade processor initialized")
            print("✅ Trade processor initialized")
        else:
            issues.append("❌ Trade processor not initialized")
            print("❌ Trade processor not initialized")
            
    except Exception as e:
        issues.append(f"❌ Bot creation: {e}")
        print(f"❌ Bot creation: {e}")
        print(f"Error details: {traceback.format_exc()}")
    
    # Test 5: Integration Mapping
    print("\n5. 🔗 INTEGRATION MAPPING")
    print("-" * 30)
    
    try:
        from trading_pattern_analyzer import TradingPatternAnalyzer
        analyzer = TradingPatternAnalyzer()
        
        # Check if LaunchLab is mapped
        if "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj" in analyzer.programs:
            successes.append("✅ LaunchLab integration")
            print("✅ LaunchLab integration verified")
        else:
            issues.append("❌ LaunchLab not mapped")
            print("❌ LaunchLab not mapped")
            
        # Check if Meteora is mapped
        if "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN" in analyzer.programs:
            successes.append("✅ Meteora integration")
            print("✅ Meteora integration verified")
        else:
            issues.append("❌ Meteora not mapped")
            print("❌ Meteora not mapped")
            
    except Exception as e:
        issues.append(f"❌ Pattern analyzer: {e}")
        print(f"❌ Pattern analyzer: {e}")
    
    # Final Report
    print("\n" + "=" * 60)
    print("📊 FINAL SYSTEM STATUS")
    print("=" * 60)
    
    print(f"\n✅ SUCCESSES ({len(successes)}):")
    for success in successes:
        print(f"   {success}")
    
    if issues:
        print(f"\n❌ ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n🎉 NO ISSUES FOUND!")
    
    # Overall Status
    success_rate = len(successes) / (len(successes) + len(issues)) * 100 if (len(successes) + len(issues)) > 0 else 0
    
    print(f"\n🎯 OVERALL SYSTEM STATUS:")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("   Status: 🟢 EXCELLENT - Ready for production")
    elif success_rate >= 75:
        print("   Status: 🟡 GOOD - Minor issues to resolve")
    elif success_rate >= 50:
        print("   Status: 🟠 FAIR - Several issues need attention")
    else:
        print("   Status: 🔴 POOR - Major fixes required")
    
    print(f"\n💡 RECOMMENDATION:")
    if issues:
        print("   🔧 Address the issues listed above before running the bot")
    else:
        print("   🚀 System is ready for live trading!")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_core_system()
    sys.exit(0 if success else 1)
