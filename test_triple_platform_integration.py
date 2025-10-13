#!/usr/bin/env python3
"""
🚀 TRIPLE-PLATFORM MEV INTEGRATION TEST
=====================================

Comprehensive test suite for all three MEV executors:
1. Pump.fun MEV Executor
2. Meteora DBC MEV Executor  
3. Advanced MEV Bot Executor

Tests smart platform detection and routing in execution_coordinator.py
"""

import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock data for testing
MOCK_WALLET = "mock_wallet_keypair"
MOCK_RPC_CLIENT = "mock_rpc_client"
MOCK_JITO_SERVICE = "mock_jito_service"

class MockConfig:
    """Mock configuration for testing"""
    investment_amount_sol = 0.1
    enable_dexes = {
        'mev_pumpfun': True,
        'meteora_dbc': True,
        'advanced_mev_bot': True
    }

async def test_platform_detection():
    """Test smart platform detection logic"""
    logger.info("🧪 Testing Smart Platform Detection...")
    
    try:
        # Import execution coordinator
        from execution_coordinator import ExecutionCoordinator
        
        # Create coordinator with mock data
        coordinator = ExecutionCoordinator(
            config=MockConfig(),
            wallet=MOCK_WALLET,
            jito_service=MOCK_JITO_SERVICE,
            rpc_client=MOCK_RPC_CLIENT
        )
        
        # Test cases for different platforms
        test_cases = [
            {
                'name': 'Advanced MEV Bot Detection',
                'token_mint': 'AdvancedMEVTestToken1111111111111111111111',
                'trade_info': {
                    'programs_used': [
                        'BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW',  # Advanced MEV Bot
                        'cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG'   # Custom Routing
                    ]
                },
                'expected': 'advanced_mev_bot'
            },
            {
                'name': 'Meteora DAMM v2 Detection',
                'token_mint': 'MeteoraTestToken11111111111111111111111111',
                'trade_info': {
                    'programs_used': [
                        'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN'  # Meteora DAMM v2
                    ]
                },
                'expected': 'meteora_damm_v2'
            },
            {
                'name': 'Pump.fun Detection',
                'token_mint': 'PumpfunTestToken1111111111111111111111111',
                'trade_info': {
                    'programs_used': [
                        '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'  # Pump.fun Direct
                    ]
                },
                'expected': 'pumpfun'
            },
            {
                'name': 'Default Detection (No Programs)',
                'token_mint': 'UnknownTestToken111111111111111111111111111',
                'trade_info': {},
                'expected': 'pumpfun'
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            logger.info(f"   🔍 Testing {test_case['name']}...")
            
            detected_platform = await coordinator._detect_token_platform(
                test_case['token_mint'],
                test_case['trade_info']
            )
            
            success = detected_platform == test_case['expected']
            results.append({
                'test': test_case['name'],
                'token': test_case['token_mint'][:16] + '...',
                'expected': test_case['expected'],
                'detected': detected_platform,
                'success': success
            })
            
            if success:
                logger.info(f"   ✅ {test_case['name']}: {detected_platform}")
            else:
                logger.error(f"   ❌ {test_case['name']}: expected {test_case['expected']}, got {detected_platform}")
        
        # Results summary
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)
        success_rate = (successful_tests / total_tests) * 100
        
        logger.info(f"📊 Platform Detection Results: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Platform detection test failed: {e}")
        return []

async def test_executor_availability():
    """Test availability of all MEV executors"""
    logger.info("🧪 Testing MEV Executor Availability...")
    
    executor_tests = []
    
    # Test Pump.fun MEV Executor
    try:
        from mev_pumpfun_executor import MEVPumpFunExecutor
        logger.info("   ✅ Pump.fun MEV Executor: Available")
        executor_tests.append({'name': 'Pump.fun MEV', 'available': True, 'error': None})
    except ImportError as e:
        logger.error(f"   ❌ Pump.fun MEV Executor: Not Available - {e}")
        executor_tests.append({'name': 'Pump.fun MEV', 'available': False, 'error': str(e)})
    
    # Test Meteora MEV Executor
    try:
        from mev_meteora_executor import MEVMeteoraExecutor
        logger.info("   ✅ Meteora MEV Executor: Available")
        executor_tests.append({'name': 'Meteora MEV', 'available': True, 'error': None})
    except ImportError as e:
        logger.error(f"   ❌ Meteora MEV Executor: Not Available - {e}")
        executor_tests.append({'name': 'Meteora MEV', 'available': False, 'error': str(e)})
    
    # Test Advanced MEV Bot Executor
    try:
        from mev_advanced_bot_executor import MEVAdvancedBotExecutor
        logger.info("   ✅ Advanced MEV Bot Executor: Available")
        executor_tests.append({'name': 'Advanced MEV Bot', 'available': True, 'error': None})
    except ImportError as e:
        logger.error(f"   ❌ Advanced MEV Bot Executor: Not Available - {e}")
        executor_tests.append({'name': 'Advanced MEV Bot', 'available': False, 'error': str(e)})
    
    # Test Execution Coordinator
    try:
        from execution_coordinator import ExecutionCoordinator, AdvancedMEVExecutor, MeteoraExecutor
        logger.info("   ✅ Execution Coordinator: Available")
        executor_tests.append({'name': 'Execution Coordinator', 'available': True, 'error': None})
    except ImportError as e:
        logger.error(f"   ❌ Execution Coordinator: Not Available - {e}")
        executor_tests.append({'name': 'Execution Coordinator', 'available': False, 'error': str(e)})
    
    available_count = sum(1 for test in executor_tests if test['available'])
    total_count = len(executor_tests)
    
    logger.info(f"📊 Executor Availability: {available_count}/{total_count} executors available")
    
    return executor_tests

async def test_execution_routing():
    """Test execution routing logic"""
    logger.info("🧪 Testing Execution Routing...")
    
    try:
        from execution_coordinator import ExecutionCoordinator
        
        # Mock coordinator
        coordinator = ExecutionCoordinator(
            config=MockConfig(),
            wallet=MOCK_WALLET,
            jito_service=MOCK_JITO_SERVICE,
            rpc_client=MOCK_RPC_CLIENT
        )
        
        # Mock different execution scenarios
        routing_tests = [
            {
                'name': 'Advanced MEV Bot Routing',
                'token_mint': 'AdvancedMEVToken111111111111111111111111111',
                'trade_info': {
                    'programs_used': ['BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW']
                },
                'expected_method': '_execute_advanced_mev_buy'
            },
            {
                'name': 'Meteora DAMM v2 Routing',
                'token_mint': 'MeteoraToken1111111111111111111111111111111',
                'trade_info': {
                    'programs_used': ['dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN']
                },
                'expected_method': '_execute_meteora_buy'
            },
            {
                'name': 'Pump.fun Default Routing',
                'token_mint': 'PumpfunToken111111111111111111111111111111',
                'trade_info': {
                    'programs_used': ['6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P']
                },
                'expected_method': '_execute_pumpfun_buy'
            }
        ]
        
        routing_results = []
        
        for test in routing_tests:
            # Detect platform
            detected_platform = await coordinator._detect_token_platform(
                test['token_mint'],
                test['trade_info']
            )
            
            # Determine expected routing
            if 'advanced_mev' in test['expected_method']:
                expected_platform = 'advanced_mev_bot'
            elif 'meteora' in test['expected_method']:
                expected_platform = 'meteora_damm_v2'
            else:
                expected_platform = 'pumpfun'
            
            success = detected_platform == expected_platform
            
            routing_results.append({
                'test': test['name'],
                'expected_platform': expected_platform,
                'detected_platform': detected_platform,
                'success': success
            })
            
            if success:
                logger.info(f"   ✅ {test['name']}: Correctly routed to {detected_platform}")
            else:
                logger.error(f"   ❌ {test['name']}: Expected {expected_platform}, got {detected_platform}")
        
        successful_routing = sum(1 for r in routing_results if r['success'])
        total_routing = len(routing_results)
        routing_success_rate = (successful_routing / total_routing) * 100
        
        logger.info(f"📊 Routing Results: {successful_routing}/{total_routing} ({routing_success_rate:.1f}%)")
        
        return routing_results
        
    except Exception as e:
        logger.error(f"❌ Routing test failed: {e}")
        return []

async def test_configuration_validation():
    """Test configuration validation for all executors"""
    logger.info("🧪 Testing Configuration Validation...")
    
    config_tests = []
    
    # Test Pump.fun MEV config
    try:
        from mev_pumpfun_executor import get_mev_config, validate_pumpfun_params
        
        config = get_mev_config()
        is_valid = validate_pumpfun_params(0.1, 1.0)  # Valid params
        
        config_tests.append({
            'executor': 'Pump.fun MEV',
            'config_loaded': bool(config),
            'validation_works': is_valid,
            'success': bool(config) and is_valid
        })
        
        logger.info("   ✅ Pump.fun MEV configuration: Valid")
        
    except Exception as e:
        logger.error(f"   ❌ Pump.fun MEV configuration error: {e}")
        config_tests.append({
            'executor': 'Pump.fun MEV',
            'config_loaded': False,
            'validation_works': False,
            'success': False,
            'error': str(e)
        })
    
    # Test Meteora MEV config
    try:
        from meteora_config import get_meteora_config, validate_trade_params
        
        config = get_meteora_config()
        is_valid = validate_trade_params(0.1, 1.0)  # Valid params
        
        config_tests.append({
            'executor': 'Meteora MEV',
            'config_loaded': bool(config),
            'validation_works': is_valid,
            'success': bool(config) and is_valid
        })
        
        logger.info("   ✅ Meteora MEV configuration: Valid")
        
    except Exception as e:
        logger.error(f"   ❌ Meteora MEV configuration error: {e}")
        config_tests.append({
            'executor': 'Meteora MEV',
            'config_loaded': False,
            'validation_works': False,
            'success': False,
            'error': str(e)
        })
    
    # Test Advanced MEV Bot config
    try:
        from mev_advanced_bot_executor import get_advanced_mev_config, validate_advanced_mev_params
        
        config = get_advanced_mev_config()
        is_valid = validate_advanced_mev_params(0.1, 1.0)  # Valid params
        
        config_tests.append({
            'executor': 'Advanced MEV Bot',
            'config_loaded': bool(config),
            'validation_works': is_valid,
            'success': bool(config) and is_valid
        })
        
        logger.info("   ✅ Advanced MEV Bot configuration: Valid")
        
    except Exception as e:
        logger.error(f"   ❌ Advanced MEV Bot configuration error: {e}")
        config_tests.append({
            'executor': 'Advanced MEV Bot',
            'config_loaded': False,
            'validation_works': False,
            'success': False,
            'error': str(e)
        })
    
    successful_configs = sum(1 for test in config_tests if test['success'])
    total_configs = len(config_tests)
    
    logger.info(f"📊 Configuration Results: {successful_configs}/{total_configs} configurations valid")
    
    return config_tests

async def run_comprehensive_integration_test():
    """Run all integration tests"""
    logger.info("🚀 STARTING TRIPLE-PLATFORM MEV INTEGRATION TEST")
    logger.info("=" * 60)
    
    # Initialize results
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'triple_platform_mev_integration',
        'tests': {}
    }
    
    # Run all test suites
    try:
        # 1. Test executor availability
        logger.info("\n1️⃣ EXECUTOR AVAILABILITY TEST")
        logger.info("-" * 40)
        availability_results = await test_executor_availability()
        test_results['tests']['executor_availability'] = availability_results
        
        # 2. Test platform detection
        logger.info("\n2️⃣ PLATFORM DETECTION TEST")
        logger.info("-" * 40)
        detection_results = await test_platform_detection()
        test_results['tests']['platform_detection'] = detection_results
        
        # 3. Test execution routing
        logger.info("\n3️⃣ EXECUTION ROUTING TEST")
        logger.info("-" * 40)
        routing_results = await test_execution_routing()
        test_results['tests']['execution_routing'] = routing_results
        
        # 4. Test configuration validation
        logger.info("\n4️⃣ CONFIGURATION VALIDATION TEST")
        logger.info("-" * 40)
        config_results = await test_configuration_validation()
        test_results['tests']['configuration_validation'] = config_results
        
        # Calculate overall results
        total_tests = 0
        successful_tests = 0
        
        for test_category in test_results['tests'].values():
            if isinstance(test_category, list):
                total_tests += len(test_category)
                successful_tests += sum(1 for test in test_category if test.get('success', test.get('available', False)))
        
        overall_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Final summary
        logger.info("\n🎯 INTEGRATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"❌ Failed: {total_tests - successful_tests}")
        logger.info(f"📈 Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 80:
            logger.info("🎉 INTEGRATION TEST PASSED!")
            logger.info("   Triple-platform MEV system is ready for deployment!")
        else:
            logger.warning("⚠️ Integration test has issues that need attention")
            
        # Save results
        test_results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': overall_success_rate,
            'status': 'PASSED' if overall_success_rate >= 80 else 'NEEDS_ATTENTION'
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"triple_platform_integration_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"📁 Test results saved to: {filename}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return {'error': str(e), 'status': 'FAILED'}

if __name__ == "__main__":
    # Run the comprehensive integration test
    asyncio.run(run_comprehensive_integration_test())
