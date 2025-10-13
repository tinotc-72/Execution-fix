#!/usr/bin/env python3
"""
Comprehensive test for the enhanced aggressive fallback system
in mint extraction functionality.
"""

import sys
import asyncio
import logging
from trade_processor import TradeProcessor
from solana.rpc.async_api import AsyncClient

# Enable comprehensive logging to see all fallback stages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s - %(message)s')
logger = logging.getLogger('fallback_test')

async def test_comprehensive_fallback():
    """Test all stages of the aggressive fallback system."""
    print('🧪 COMPREHENSIVE AGGRESSIVE FALLBACK TEST')
    print('=' * 60)
    
    target_wallets = ['A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB']
    rpc_client = AsyncClient('https://api.mainnet-beta.solana.com')
    processor = TradeProcessor(target_wallets, rpc_client)
    
    results = []
    
    # Test Case 1: Logs extraction fallback
    print('\n📊 TEST 1: Logs Extraction Fallback')
    print('-' * 40)
    mock_tx_logs = {
        'transaction': {
            'signatures': ['logs_fallback_test_12345'],
            'message': {
                'accountKeys': ['11111111111111111111111111111111']  # Only system program
            }
        },
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [],
            'logMessages': [
                'Program 11111111111111111111111111111111 invoke [1]',
                'Transfer EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v amount=1000',
                'Program success'
            ]
        }
    }
    
    try:
        result1 = await processor._extract_sophisticated_token_mint(mock_tx_logs, target_wallets[0])
        print(f'✅ TEST 1 RESULT: {result1}')
        results.append(('Logs Extraction', result1, True))
    except Exception as e:
        print(f'❌ TEST 1 ERROR: {e}')
        results.append(('Logs Extraction', None, False))
    
    # Test Case 2: Account key ultra-aggressive fallback
    print('\n🔑 TEST 2: Account Key Ultra-Aggressive Fallback') 
    print('-' * 50)
    mock_tx_accounts = {
        'transaction': {
            'signatures': ['account_fallback_test_67890'],
            'message': {
                'accountKeys': [
                    '11111111111111111111111111111111',                    # System (excluded)
                    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',       # Token Program (excluded)
                    'ComputeBudget111111111111111111111111111111',       # Compute Budget (excluded)
                    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',       # USDC (should be found)
                    'So11111111111111111111111111111111111111112'        # SOL (should be found)
                ]
            }
        },
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [],
            'logMessages': []  # Empty logs to force account key fallback
        }
    }
    
    try:
        result2 = await processor._extract_sophisticated_token_mint(mock_tx_accounts, target_wallets[0])
        print(f'✅ TEST 2 RESULT: {result2}')
        results.append(('Account Key Ultra', result2, True))
    except Exception as e:
        print(f'❌ TEST 2 ERROR: {e}')
        results.append(('Account Key Ultra', None, False))
    
    # Test Case 3: Complete failure (all system programs)
    print('\n❌ TEST 3: Complete Failure Case (All System Programs)')
    print('-' * 55)
    mock_tx_failure = {
        'transaction': {
            'signatures': ['failure_test_99999'],
            'message': {
                'accountKeys': [
                    '11111111111111111111111111111111',                # System Program
                    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',   # Token Program
                    'ComputeBudget111111111111111111111111111111'    # Compute Budget Program
                ]
            }
        },
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [],
            'logMessages': []
        }
    }
    
    try:
        result3 = await processor._extract_sophisticated_token_mint(mock_tx_failure, target_wallets[0])
        print(f'✅ TEST 3 RESULT: {result3}')
        results.append(('Complete Failure', result3, True))
    except Exception as e:
        print(f'❌ TEST 3 ERROR: {e}')
        results.append(('Complete Failure', None, False))
    
    await rpc_client.close()
    
    # Summary
    print('\n' + '=' * 60)
    print('📈 FALLBACK TEST SUMMARY:')
    for test_name, result, success in results:
        if test_name == "Complete Failure":
            # For complete failure test, None is the expected/correct result
            status = "✅ HANDLED" if success and result is None else "❌ UNEXPECTED" if success else "💥 ERROR"
        else:
            status = "✅ SUCCESS" if success and result else "❌ FAILED" if success else "💥 ERROR"
        print(f'  • {test_name}: {status} - {result}')
    
    print('\n🎯 KEY OBSERVATIONS:')
    print('  • Logs extraction should find USDC mint from log messages')
    print('  • Account key fallback should find valid token from account keys')  
    print('  • Complete failure should return None gracefully')
    print('  • All stages should have comprehensive DEBUG logging')
    print('=' * 60)

if __name__ == "__main__":
    asyncio.run(test_comprehensive_fallback())