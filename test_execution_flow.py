#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE EXECUTION FLOW TEST
Tests the complete trading pipeline from trade detection to execution
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CopyTradingBot
from config import CopyTradeConfig

class ExecutionFlowTester:
    """Test the complete execution pipeline"""
    
    def __init__(self):
        self.config = CopyTradeConfig()
        self.bot = None
        self.test_results = {}
        
    async def run_comprehensive_test(self):
        """Run complete execution flow test"""
        print("🧪 STARTING COMPREHENSIVE EXECUTION FLOW TEST")
        print("=" * 60)
        
        try:
            # Step 1: Initialize bot
            await self.test_bot_initialization()
            
            # Step 2: Test validation pipeline
            await self.test_validation_pipeline()
            
            # Step 3: Test execution pipeline with simulated trade
            await self.test_execution_pipeline()
            
            # Step 4: Test position tracking
            await self.test_position_tracking()
            
            # Step 5: Display results
            self.display_test_results()
            
        except Exception as e:
            print(f"❌ CRITICAL TEST FAILURE: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.bot:
                print("\n🧹 Cleaning up bot resources...")

    async def test_bot_initialization(self):
        """Test 1: Bot initialization and executor loading"""
        print("\n🧪 TEST 1: Bot Initialization")
        print("-" * 40)
        
        start_time = time.time()
        try:
            self.bot = CopyTradingBot(self.config)
            init_time = time.time() - start_time
            
            print(f"✅ Bot initialized successfully in {init_time:.2f}s")
            print(f"   📊 Loaded executors: {len(self.bot.dex_executors)}")
            print(f"   🎯 Target wallets: {len(self.bot.target_wallets)}")
            print(f"   💰 Investment amount: {self.bot.config.investment_amount_sol} SOL")
            
            # Test executor availability
            enabled_executors = sum(1 for dex, enabled in self.bot.config.enable_dexes.items() if enabled)
            print(f"   🏭 Enabled executors: {enabled_executors}")
            
            for dex_name, (buy_func, sell_func) in self.bot.dex_executors.items():
                if self.bot.config.enable_dexes.get(dex_name, False):
                    print(f"      ✅ {dex_name}: {buy_func.__name__}")
            
            self.test_results['initialization'] = {
                'success': True,
                'time': init_time,
                'executors_loaded': len(self.bot.dex_executors),
                'enabled_executors': enabled_executors
            }
            
        except Exception as e:
            print(f"❌ Bot initialization failed: {e}")
            self.test_results['initialization'] = {
                'success': False,
                'error': str(e)
            }
            raise

    async def test_validation_pipeline(self):
        """Test 2: Trade validation logic"""
        print("\n🧪 TEST 2: Validation Pipeline")
        print("-" * 40)
        
        # Test valid trade info
        valid_trade = {
            'action': 'buy',
            'wallet_address': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'signature': '5J7Hk2eG9Xj8vP3mN4cB6qE2dF9kT8nW7rL1sQ4mH6gA',
            'token_mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
            'dex': 'jupiter',
            'timestamp': datetime.now(timezone.utc)
        }
        
        # Test invalid trade info (missing fields)
        invalid_trade = {
            'action': 'buy',
            'wallet_address': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB'
            # Missing signature and token_mint
        }
        
        # Test system program (should be rejected)
        system_program_trade = {
            'action': 'buy',
            'wallet_address': 'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',
            'signature': '5J7Hk2eG9Xj8vP3mN4cB6qE2dF9kT8nW7rL1sQ4mH6gA',
            'token_mint': '11111111111111111111111111111111',  # System Program
            'dex': 'jupiter'
        }
        
        validation_results = {}
        
        # Test valid trade
        try:
            result = self.bot._validate_trade_info(valid_trade)
            print(f"✅ Valid trade validation: {result}")
            validation_results['valid_trade'] = result
        except Exception as e:
            print(f"❌ Valid trade validation failed: {e}")
            validation_results['valid_trade'] = False
        
        # Test invalid trade
        try:
            result = self.bot._validate_trade_info(invalid_trade)
            print(f"⚠️ Invalid trade validation: {result} (should be False)")
            validation_results['invalid_trade'] = result
        except Exception as e:
            print(f"✅ Invalid trade correctly rejected: {e}")
            validation_results['invalid_trade'] = False
        
        # Test system program
        try:
            result = self.bot._validate_trade_info(system_program_trade)
            print(f"⚠️ System program validation: {result} (should be False)")
            validation_results['system_program'] = result
        except Exception as e:
            print(f"✅ System program correctly rejected: {e}")
            validation_results['system_program'] = False
        
        self.test_results['validation'] = validation_results

    async def test_execution_pipeline(self):
        """Test 3: Complete execution pipeline with simulated trade"""
        print("\n🧪 TEST 3: Execution Pipeline")
        print("-" * 40)
        
        # Create a realistic test trade (using a well-known token)
        test_trade = {
            'action': 'buy',
            'wallet_address': 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',  # Test wallet
            'signature': 'test_signature_12345',
            'token_mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC for safety
            'dex': 'jupiter',
            'timestamp': datetime.now(timezone.utc),
            'extraction_method': 'test_simulation',
            'confidence': 10
        }
        
        print(f"🎯 Simulating BUY trade for token: {test_trade['token_mint'][:8]}...")
        print(f"   📝 Source wallet: {test_trade['wallet_address'][:8]}...")
        print(f"   🏪 DEX: {test_trade['dex']}")
        print(f"   💰 Amount: {self.bot.config.investment_amount_sol} SOL")
        
        execution_start = time.time()
        
        try:
            # Test the complete pipeline
            print("\n📋 STEP 1: Validation...")
            validation_result = self.bot._validate_trade_info(test_trade)
            print(f"   ✅ Validation result: {validation_result}")
            
            if validation_result:
                print("\n⚡ STEP 2: Processing detected trade...")
                
                # Test the main processing method
                result = await self.bot._process_detected_trade(
                    test_trade, 
                    test_trade['wallet_address']
                )
                
                execution_time = time.time() - execution_start
                print(f"   🎯 Processing result: {result}")
                print(f"   ⏱️ Total execution time: {execution_time:.2f}s")
                
                self.test_results['execution'] = {
                    'success': result if result is not None else False,
                    'time': execution_time,
                    'validation_passed': validation_result
                }
            else:
                print("❌ Validation failed - skipping execution")
                self.test_results['execution'] = {
                    'success': False,
                    'error': 'Validation failed'
                }
                
        except Exception as e:
            execution_time = time.time() - execution_start
            print(f"❌ Execution pipeline failed after {execution_time:.2f}s: {e}")
            import traceback
            traceback.print_exc()
            
            self.test_results['execution'] = {
                'success': False,
                'error': str(e),
                'time': execution_time
            }

    async def test_position_tracking(self):
        """Test 4: Position tracking functionality"""
        print("\n🧪 TEST 4: Position Tracking")
        print("-" * 40)
        
        test_token = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
        test_wallet = 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH'
        test_dex = 'jupiter'
        
        try:
            print(f"📊 Testing position tracking for token: {test_token[:8]}...")
            
            # Test position creation
            initial_positions = len(self.bot.positions)
            print(f"   📈 Initial positions: {initial_positions}")
            
            # Simulate successful buy
            self.bot._update_position_after_buy_success(test_token, test_wallet, test_dex)
            
            final_positions = len(self.bot.positions)
            print(f"   📈 Final positions: {final_positions}")
            
            if test_token in self.bot.positions:
                position = self.bot.positions[test_token]
                print(f"   ✅ Position created successfully:")
                print(f"      💰 Amount: {position.current_amount} SOL")
                print(f"      🏪 Entry DEX: {position.entry_dex}")
                print(f"      👤 Source wallet: {position.source_wallet[:8]}...")
                print(f"      ⏰ Timestamp: {position.timestamp}")
                
                self.test_results['position_tracking'] = {
                    'success': True,
                    'position_created': True,
                    'amount': position.current_amount
                }
            else:
                print(f"❌ Position not found in tracking")
                self.test_results['position_tracking'] = {
                    'success': False,
                    'error': 'Position not created'
                }
                
        except Exception as e:
            print(f"❌ Position tracking test failed: {e}")
            self.test_results['position_tracking'] = {
                'success': False,
                'error': str(e)
            }

    def display_test_results(self):
        """Display comprehensive test results"""
        print("\n🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        print(f"📊 OVERALL: {passed_tests}/{total_tests} tests passed")
        print()
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"{status} {test_name.upper().replace('_', ' ')}")
            
            if result.get('success', False):
                if 'time' in result:
                    print(f"    ⏱️ Execution time: {result['time']:.2f}s")
                if 'executors_loaded' in result:
                    print(f"    🏭 Executors loaded: {result['executors_loaded']}")
                if 'enabled_executors' in result:
                    print(f"    ⚡ Enabled executors: {result['enabled_executors']}")
                if 'position_created' in result:
                    print(f"    📊 Position tracking: Working")
            else:
                if 'error' in result:
                    print(f"    ❌ Error: {result['error']}")
            print()
        
        # Performance summary
        total_time = sum(result.get('time', 0) for result in self.test_results.values())
        print(f"⚡ PERFORMANCE SUMMARY:")
        print(f"   Total test time: {total_time:.2f}s")
        
        if self.test_results.get('initialization', {}).get('success'):
            print(f"   Bot startup time: {self.test_results['initialization']['time']:.2f}s")
        
        if self.test_results.get('execution', {}).get('success'):
            print(f"   Execution pipeline: {self.test_results['execution']['time']:.2f}s")
        
        # Bot status summary
        print(f"\n🤖 BOT STATUS SUMMARY:")
        if self.bot:
            print(f"   ✅ Bot initialized: True")
            print(f"   🎯 Target wallets: {len(self.bot.target_wallets)}")
            print(f"   💰 Investment per trade: {self.bot.config.investment_amount_sol} SOL")
            print(f"   📊 Current positions: {len(self.bot.positions)}")
            print(f"   🏭 Available executors: {len(self.bot.dex_executors)}")
            
            enabled_dexes = [dex for dex, enabled in self.bot.config.enable_dexes.items() if enabled]
            print(f"   ⚡ Enabled DEXes: {', '.join(enabled_dexes)}")
        
        print(f"\n🎯 CONCLUSION:")
        if passed_tests == total_tests:
            print("   ✅ ALL TESTS PASSED - Bot is ready for live trading!")
            print("   🚀 Execution pipeline is working correctly")
            print("   📊 Position tracking is functional")
            print("   🔧 All critical components verified")
        else:
            print(f"   ⚠️ {total_tests - passed_tests} test(s) failed - review issues before live trading")
            print("   🔧 Check error messages above for specific problems")

async def main():
    """Run the comprehensive execution flow test"""
    print("🧪 EXECUTION FLOW TEST STARTING...")
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    tester = ExecutionFlowTester()
    await tester.run_comprehensive_test()
    
    print(f"\n⏰ Test completed at: {datetime.now()}")
    print("🧪 EXECUTION FLOW TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
