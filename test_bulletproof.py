#!/usr/bin/env python3
import asyncio
from trade_processor import TradeProcessor
from datetime import datetime, timezone
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def final_bulletproof_test():
    print('🔥 FINAL BULLETPROOF VERIFICATION TEST 🔥')
    target_wallets = ['A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB']  # Example wallet
    processor = TradeProcessor(target_wallets)
    
    # Configuration validation
    from trade_processor import TOKEN_PROGRAMS, DEX_PROGRAMS, CANONICAL_KNOWN_WALLETS
    print(f'📊 TOKEN_PROGRAMS: {len(TOKEN_PROGRAMS)}')
    print(f'📊 DEX_PROGRAMS: {len(DEX_PROGRAMS)}')
    print(f'📊 CANONICAL_KNOWN_WALLETS: {len(CANONICAL_KNOWN_WALLETS)}')
    
    # Test Token-2022 support
    from trade_processor import is_valid_solana_address
    test_2022 = 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    print(f'🆔 Token-2022 support: {"✅" if is_valid_solana_address(test_2022) else "❌"}')
    
    # Jupiter transaction test (previously working)
    jupiter_tx = {
        'transaction': {
            'message': {
                'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}]
            }
        },
        'meta': {
            'preTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '1000'}}
            ],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '500'}},
                {'owner': 'wallet123', 'mint': 'So11111111111111111111111111111111111111112', 'uiTokenAmount': {'amount': '500000000'}}
            ],
            'logMessages': ['Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]']
        }
    }
    
    print('🧪 Testing Jupiter detection...')
    start = datetime.now()
    jupiter_result = await processor.extract_token_info_fast(jupiter_tx, 'wallet123')
    jupiter_time = (datetime.now() - start).total_seconds() * 1000
    
    if jupiter_result and jupiter_result.get('token_mint'):
        print(f'✅ Jupiter working perfectly! Detected: {jupiter_result["token_mint"][:8]}... ({jupiter_time:.1f}ms)')
    else:
        print(f'❌ Jupiter detection failed: {jupiter_result}')
    
    # Safety test: Invalid mint addresses
    print('🧪 Testing safety with invalid mint...')
    invalid_tx = {
        'transaction': {'message': {'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}]}},
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'InvalidMintAddress', 'uiTokenAmount': {'amount': '100'}}
            ]
        }
    }
    
    invalid_result = await processor.extract_token_info_fast(invalid_tx, 'wallet123')
    if invalid_result and 'error' in invalid_result:
        print('✅ Safety working! Invalid mint properly rejected')
    else:
        print(f'❌ Safety failed! Should have rejected invalid mint: {invalid_result}')
    
    # Full pipeline safety test
    print('🧪 Testing full pipeline safety...')
    # Create a trade_info dict from the invalid tx for the full pipeline test
    trade_info_invalid = {'transaction': invalid_tx, 'signature': 'dummy_signature'}
    pipeline_result = await processor.analyze_and_route_trade(trade_info_invalid, 'wallet123')
    pipeline_safe = not pipeline_result.get('requires_execution', True)
    safe_emoji = '✅' if pipeline_safe else '❌'
    safe_status = 'SAFE' if pipeline_safe else 'UNSAFE'
    print(f'{safe_emoji} Full pipeline safety: {safe_status}')
    
    # DEX coverage test
    dex_coverage = 0
    test_dexes = ['pumpfun', 'jupiter', 'raydium_cpmm', 'raydium_clmm', 'orca_whirlpool', 'meteora']
    working_dexes = []
    for dex in test_dexes:
        try:
            test_result = await processor._dex_decode_mints(jupiter_tx, dex, 'wallet123')
            if test_result != (None, None):
                dex_coverage += 1
                working_dexes.append(dex)
        except Exception as e:
            print(f'  ❌ {dex} failed: {e}')
    print(f'  ✅ Working DEXes: {working_dexes}')
    
    coverage_percent = int((dex_coverage / len(test_dexes)) * 100)
    print(f'📊 DEX coverage: {coverage_percent}% ({dex_coverage}/{len(test_dexes)} working)')
    
    # Performance benchmark
    print('🧪 Performance benchmark (10 iterations)...')
    total_time = 0
    for i in range(10):
        start = datetime.now()
        await processor.extract_token_info_fast(jupiter_tx, 'wallet123')
        total_time += (datetime.now() - start).total_seconds() * 1000
    avg_time = total_time / 10
    
    print(f'⚡ Average processing time: {avg_time:.1f}ms')
    print(f'🚀 Throughput estimate: ~{int(1000/avg_time)} tx/second')
    
    # Final bulletproof status
    print('\n🔥 BULLETPROOF STATUS 🔥')
    checks = [
        (len(TOKEN_PROGRAMS) >= 2, 'Token Programs'),
        (len(DEX_PROGRAMS) >= 6, 'DEX Programs'), 
        (len(CANONICAL_KNOWN_WALLETS) >= 20, 'Known Wallets'),
        (is_valid_solana_address(test_2022), 'Token-2022 Support'),
        (jupiter_result and jupiter_result.get('token_mint'), 'Jupiter Detection'),
        (invalid_result and 'error' in invalid_result, 'Invalid Mint Safety'),
        (pipeline_safe, 'Full Pipeline Safety'),
        (coverage_percent >= 70, 'DEX Coverage'),
        (avg_time < 10, 'Performance')
    ]
    
    passed = sum(1 for check, _ in checks if check)
    total = len(checks)
    
    print(f'📊 Bulletproof Score: {passed}/{total} ({int(passed/total*100)}%)')
    
    for check, name in checks:
        status_emoji = '✅' if check else '❌'
        print(f'{status_emoji} {name}')
    
    if passed == total:
        print('\n🎯 STATUS: FULLY BULLETPROOF! Ready for production! 🚀')
    elif passed >= total - 1:
        print('\n⚡ STATUS: Near-bulletproof! Minor fixes needed 🔧')
    else:
        print(f'\n🔧 STATUS: {passed}/{total} checks passed. More work needed.')

if __name__ == "__main__":
    asyncio.run(final_bulletproof_test())