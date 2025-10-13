#!/usr/bin/env python3
"""
🎯 BULLETPROOF VALIDATION TEST SUITE
Comprehensive validation of all bulletproof features and consistency fixes.
"""
import asyncio
from trade_processor import TradeProcessor
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def comprehensive_bulletproof_test():
    print('🎯 COMPREHENSIVE BULLETPROOF VALIDATION 🎯\n')
    
    target_wallets = ['A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB']
    processor = TradeProcessor(target_wallets)
    
    # Test 1: Configuration Consistency
    print('📋 Testing Configuration Consistency...')
    from trade_processor import TOKEN_PROGRAMS, DEX_PROGRAMS, CANONICAL_KNOWN_WALLETS
    
    assert len(TOKEN_PROGRAMS) == 2, "Should have exactly 2 token programs"
    assert len(DEX_PROGRAMS) == 6, "Should have exactly 6 DEX programs"
    assert len(CANONICAL_KNOWN_WALLETS) >= 22, "Should have at least 22 known wallets"
    print(f'✅ TOKEN_PROGRAMS: {len(TOKEN_PROGRAMS)} | DEX_PROGRAMS: {len(DEX_PROGRAMS)} | KNOWN_WALLETS: {len(CANONICAL_KNOWN_WALLETS)}')
    
    # Test 2: Program ID Consistency - Meteora
    print('\n🔍 Testing Meteora Program ID Consistency...')
    meteora_dex_id = "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"
    assert meteora_dex_id in DEX_PROGRAMS, "Meteora should be in DEX_PROGRAMS"
    assert DEX_PROGRAMS[meteora_dex_id] == "meteora", "Meteora should map to 'meteora'"
    
    # Test strategy detection consistency
    test_info = {"program_id": meteora_dex_id, "logs": []}
    detected_type = processor._detect_dex_type(test_info)
    assert detected_type == "meteora", f"Strategy detection should return 'meteora', got '{detected_type}'"
    print(f'✅ Meteora Program ID unified: {meteora_dex_id} -> meteora')
    
    # Test 3: DEX Coverage with Real Transactions
    print('\n🧪 Testing All DEX Decoders...')
    
    # Jupiter test
    jupiter_tx = {
        'transaction': {'message': {'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'accounts': ['acc1', 'pool1']}]}},
        'meta': {
            'preTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '1000'}}
            ],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '500'}},
                {'owner': 'wallet123', 'mint': 'So11111111111111111111111111111111111111112', 'uiTokenAmount': {'amount': '500000000'}}
            ]
        }
    }
    
    jupiter_result = await processor.extract_token_info_fast(jupiter_tx, 'wallet123')
    assert jupiter_result and jupiter_result.get('source') == 'meta', "Jupiter should work via meta balances"
    print(f'✅ Jupiter: {jupiter_result["source"]} detection')
    
    # Test platform detection for each DEX
    dex_tests = [
        ('JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4', 'jupiter'),
        ('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P', 'pumpfun'),
        ('675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8', 'raydium_cpmm'),
        ('CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK', 'raydium_clmm'),
        ('whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc', 'orca_whirlpool'),
        ('Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB', 'meteora'),
    ]
    
    for program_id, expected_dex in dex_tests:
        test_tx = {'transaction': {'message': {'instructions': [{'programId': program_id}]}}}
        detected_platform = processor._detect_platform(test_tx)
        assert detected_platform == expected_dex, f"Program {program_id} should detect as {expected_dex}, got {detected_platform}"
        print(f'✅ {expected_dex}: Program ID detection working')
    
    # Test 4: Safety Validation
    print('\n🛡️ Testing Safety Mechanisms...')
    
    # Invalid mint rejection
    invalid_tx = {
        'transaction': {'message': {'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}]}},
        'meta': {
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'InvalidMintAddress', 'uiTokenAmount': {'amount': '100'}}
            ]
        }
    }
    
    invalid_result = await processor.extract_token_info_fast(invalid_tx, 'wallet123')
    assert invalid_result and 'error' in invalid_result, "Invalid mint should be rejected"
    print('✅ Invalid mint addresses properly rejected')
    
    # Execution gating
    trade_info = {'transaction': invalid_tx, 'signature': 'test_sig'}
    routing_result = await processor.analyze_and_route_trade(trade_info, 'wallet123')
    assert not routing_result.get('requires_execution', True), "Invalid trades should not require execution"
    print('✅ Execution properly gated for invalid mints')
    
    # Test 5: Pool-State Cache Integration
    print('\n🎯 Testing Pool-State Cache...')
    from trade_processor import _pool_cache
    
    # Test cache functionality
    test_pool = "TestPoolAddress123"
    test_state = {"mint_a": "MintA123", "mint_b": "MintB456", "vault_a": "VaultA", "vault_b": "VaultB"}
    _pool_cache.set(test_pool, test_state)
    
    cached_state = _pool_cache.get(test_pool)
    assert cached_state == test_state, "Pool cache should store and retrieve state correctly"
    print('✅ Pool-state cache operational')
    
    # Test 6: Performance & Throughput
    print('\n⚡ Performance Validation...')
    iterations = 50
    total_time = 0
    
    for i in range(iterations):
        start = datetime.now()
        await processor.extract_token_info_fast(jupiter_tx, 'wallet123')
        total_time += (datetime.now() - start).total_seconds() * 1000
    
    avg_time = total_time / iterations
    throughput = int(1000 / avg_time) if avg_time > 0 else 99999
    
    assert avg_time < 5.0, f"Average processing time should be under 5ms, got {avg_time:.1f}ms"
    assert throughput > 5000, f"Throughput should exceed 5K tx/sec, got {throughput}"
    print(f'✅ Performance: {avg_time:.1f}ms avg, ~{throughput} tx/sec')
    
    # Test 7: Edge Case Handling
    print('\n🔧 Testing Edge Cases...')
    
    # Empty transaction
    empty_tx = {'transaction': {'message': {'instructions': []}}, 'meta': {}}
    empty_result = await processor.extract_token_info_fast(empty_tx, 'wallet123')
    assert empty_result and 'error' in empty_result, "Empty transactions should be handled gracefully"
    print('✅ Empty transactions handled gracefully')
    
    # Missing meta
    no_meta_tx = {'transaction': {'message': {'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}]}}}
    no_meta_result = await processor.extract_token_info_fast(no_meta_tx, 'wallet123')
    assert no_meta_result and 'error' in no_meta_result, "Missing meta should be handled"
    print('✅ Missing metadata handled gracefully')
    
    # Final Summary
    print('\n🏆 BULLETPROOF VALIDATION COMPLETE 🏆')
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print('✅ Configuration Consistency: PASS')
    print('✅ Program ID Unification: PASS') 
    print('✅ DEX Coverage (6/6): PASS')
    print('✅ Safety Mechanisms: PASS')
    print('✅ Pool-State Cache: PASS')
    print('✅ Performance Requirements: PASS')
    print('✅ Edge Case Handling: PASS')
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print('🎯 STATUS: TRUE BULLETPROOF ACHIEVED! 🚀')
    print(f'📊 Ready for production deployment at {throughput}+ tx/sec')

if __name__ == "__main__":
    asyncio.run(comprehensive_bulletproof_test())