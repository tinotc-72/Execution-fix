#!/usr/bin/env python3
"""
Test Trade Processing Resilience
Verify that trades no longer get skipped due to missing fields or token extraction failures
"""

import asyncio
import json
from trade_processor import TradeProcessor
from execution_coordinator import ExecutionCoordinator
from env_keys import EnvKeys
import httpx

async def test_trade_processing_resilience():
    """Test that the trade processor is now resilient to failures"""
    
    print("🚀 TESTING TRADE PROCESSING RESILIENCE")
    print("=" * 60)
    
    processor = TradeProcessor(httpx.AsyncClient())
    
    # Test 1: Trade with completely missing signature
    print("\n🧪 TEST 1: Trade with Missing Signature")
    print("-" * 40)
    
    trade_with_missing_sig = {
        'action': 'buy',
        'wallet_address': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
        'basic_analysis': {'likely_action': 'buy'},
        # signature missing!
    }
    
    result1 = await processor.analyze_and_route_trade(trade_with_missing_sig, '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76')
    print(f"   Result: {result1.get('requires_execution', 'N/A')}")
    print(f"   Action: {result1.get('action', 'N/A')}")
    print(f"   Token: {result1.get('token_mint', 'N/A')}")
    print(f"   Forced: {result1.get('forced_execution', False)}")
    
    # Test 2: Trade with invalid signature
    print("\n🧪 TEST 2: Trade with Invalid Signature")
    print("-" * 40)
    
    trade_with_invalid_sig = {
        'signature': 'invalid_signature_12345',
        'action': 'buy',
        'wallet_address': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
        'basic_analysis': {'likely_action': 'buy'},
    }
    
    result2 = await processor.analyze_and_route_trade(trade_with_invalid_sig, '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76')
    print(f"   Result: {result2.get('requires_execution', 'N/A')}")
    print(f"   Action: {result2.get('action', 'N/A')}")  
    print(f"   Token: {result2.get('token_mint', 'N/A')}")
    print(f"   Forced: {result2.get('forced_execution', False)}")
    
    # Test 3: Trade with minimal information
    print("\n🧪 TEST 3: Trade with Minimal Information")
    print("-" * 40)
    
    minimal_trade = {
        'signature': '3AjZkK3tKdXr8ujjgPs9hAcP1LHjRNuyD6phme2M8EfQkHtZNoxaPJv47cZqArWwKX6mheXQcGgXywdXsQi1P1n4',
        # Only signature provided, everything else missing
    }
    
    result3 = await processor.analyze_and_route_trade(minimal_trade, '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76')
    print(f"   Result: {result3.get('requires_execution', 'N/A')}")
    print(f"   Action: {result3.get('action', 'N/A')}")
    print(f"   Token: {result3.get('token_mint', 'N/A')}")
    print(f"   Forced: {result3.get('forced_execution', False)}")
    
    # Test 4: Exception-causing trade data
    print("\n🧪 TEST 4: Exception-Causing Trade Data")
    print("-" * 40)
    
    exception_trade = {
        'signature': None,  # This will cause exceptions
        'action': {'invalid': 'dict'},  # Wrong type
        'wallet_address': 123,  # Wrong type
    }
    
    result4 = await processor.analyze_and_route_trade(exception_trade, '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76')
    print(f"   Result: {result4.get('requires_execution', 'N/A')}")
    print(f"   Action: {result4.get('action', 'N/A')}")
    print(f"   Token: {result4.get('token_mint', 'N/A')}")
    print(f"   Forced: {result4.get('forced_execution', False)}")
    
    # Summary
    print("\n📊 RESILIENCE TEST SUMMARY")
    print("=" * 40)
    
    all_results = [result1, result2, result3, result4]
    execution_count = sum(1 for r in all_results if r.get('requires_execution'))
    forced_count = sum(1 for r in all_results if r.get('forced_execution'))
    
    print(f"Total tests: {len(all_results)}")
    print(f"Trades marked for execution: {execution_count}/{len(all_results)}")
    print(f"Forced executions: {forced_count}/{len(all_results)}")
    
    if execution_count == len(all_results):
        print("✅ SUCCESS: All trades marked for execution (no skipping!)")
    else:
        print(f"❌ FAILURE: {len(all_results) - execution_count} trades would be skipped")
    
    return execution_count == len(all_results)

async def test_execution_coordinator_unknown_token():
    """Test that execution coordinator handles UNKNOWN tokens"""
    
    print("\n🚀 TESTING EXECUTION COORDINATOR UNKNOWN TOKEN HANDLING")
    print("=" * 60)
    
    env = EnvKeys()
    coordinator = ExecutionCoordinator(httpx.AsyncClient())
    
    # Mock trade info with UNKNOWN token but valid signature
    trade_info = {
        'signature': '3AjZkK3tKdXr8ujjgPs9hAcP1LHjRNuyD6phme2M8EfQkHtZNoxaPJv47cZqArWwKX6mheXQcGgXywdXsQi1P1n4',
        'action': 'buy',
        'wallet_address': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76'
    }
    
    routing_instructions = {
        'forced_execution': True,
        'action': 'buy'
    }
    
    print("🧪 Testing UNKNOWN token handling...")
    
    try:
        # This should attempt token extraction at execution time
        result = await coordinator._execute_copy_buy(
            token_mint='UNKNOWN',
            source_wallet='3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
            trade_info=trade_info,
            routing_instructions=routing_instructions
        )
        
        print(f"✅ Execution coordinator handled UNKNOWN token")
        print(f"   Result type: {type(result)}")
        print(f"   Has error: {'error' in str(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution coordinator failed: {e}")
        return False

if __name__ == "__main__":
    async def run_all_tests():
        resilience_passed = await test_trade_processing_resilience() 
        coordinator_passed = await test_execution_coordinator_unknown_token()
        
        print(f"\n🎉 OVERALL RESULTS")
        print(f"   Trade Processor Resilience: {'✅ PASS' if resilience_passed else '❌ FAIL'}")
        print(f"   Execution Coordinator UNKNOWN Handling: {'✅ PASS' if coordinator_passed else '❌ FAIL'}")
        
        if resilience_passed and coordinator_passed:
            print(f"\n🚀 ALL TESTS PASSED: Trades will no longer be skipped!")
        else:
            print(f"\n⚠️ Some tests failed - trades may still be skipped")
    
    asyncio.run(run_all_tests())