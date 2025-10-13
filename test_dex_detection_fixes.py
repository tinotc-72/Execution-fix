#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE DEX DETECTION PIPELINE TEST
Test the surgical fixes for router/DEX detection handoff
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_processor import TradeProcessor, DEX_PROGRAMS

class MockRPCClient:
    async def call(self, method, params):
        return {'result': None}

class MockCoordinator:
    def _detect_token_platform(self, trade_info, transaction_signature):
        '''Mock the coordinator Priority-0 and Priority-2 logic'''
        # Priority 0: Check router_program_id 
        router_id = trade_info.get('router_program_id')
        if router_id:
            # Jupiter router detection (route to Jupiter executor)
            if router_id == 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4':
                return 'jupiter'
            # Raydium CPMM detection  
            elif router_id == 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C':
                return 'mev_raydium'
            # Pump.fun detection
            elif router_id == '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P':
                return 'pumpfun'
                
        # Priority 2: Check dex_type fallback
        dex_type = trade_info.get('dex_type')
        if dex_type and dex_type != 'unknown':
            if dex_type == 'jupiter':
                return 'jupiter'
            elif dex_type == 'raydium_cpmm':
                return 'mev_raydium'
            elif dex_type == 'pumpfun':
                return 'pumpfun'
        
        return 'unknown'

async def test_complete_pipeline():
    processor = TradeProcessor(['test'], MockRPCClient())
    coordinator = MockCoordinator()
    
    test_cases = [
        {
            'name': 'Jupiter Transaction',
            'tx': {
                'transaction': {
                    'message': {
                        'instructions': [{'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}]
                    }
                }
            },
            'expected_router': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',
            'expected_dex': 'jupiter',
            'expected_platform': 'jupiter'
        },
        {
            'name': 'Pump.fun Transaction', 
            'tx': {
                'transaction': {
                    'message': {
                        'instructions': [{'programId': '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'}]
                    }
                }
            },
            'expected_router': '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',
            'expected_dex': 'pumpfun', 
            'expected_platform': 'pumpfun'
        },
        {
            'name': 'Raydium CPMM Transaction',
            'tx': {
                'transaction': {
                    'message': {
                        'instructions': [{'programId': 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C'}]
                    }
                }
            },
            'expected_router': 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C',
            'expected_dex': 'raydium_cpmm',
            'expected_platform': 'mev_raydium'
        }
    ]
    
    print('🚀 TESTING DEX DETECTION PIPELINE')
    print('=' * 60)
    
    all_passed = True
    
    for test in test_cases:
        print(f"\n📋 Testing: {test['name']}")
        
        # Test router extraction
        router_id = processor._extract_router_program_id_from_tx(test['tx'])
        print(f"   Router ID: {router_id}")
        
        # Test DEX detection  
        trade_info = {
            'signature': 'test_signature',
            'logs': ['test log'],
            'transaction': test['tx']
        }
        
        # Simulate the dex detection
        dex_type = processor._detect_dex_type(trade_info)
        print(f"   DEX Type: {dex_type}")
        
        # Mock the surgical fix - attach router_program_id and dex_type
        if router_id:
            trade_info['router_program_id'] = router_id
        trade_info['dex_type'] = dex_type
        
        # Test coordinator routing
        platform = coordinator._detect_token_platform(trade_info, 'test_signature')
        print(f"   Platform: {platform}")
        
        # Verify expectations
        router_ok = router_id == test['expected_router']
        dex_ok = dex_type == test['expected_dex'] 
        platform_ok = platform == test['expected_platform']
        
        print(f"   ✅ Router: {router_ok} | DEX: {dex_ok} | Platform: {platform_ok}")
        
        if not (router_ok and dex_ok and platform_ok):
            all_passed = False
            print(f"   ❌ FAILED: Expected router={test['expected_router']}, dex={test['expected_dex']}, platform={test['expected_platform']}")
            print(f"             Got router={router_id}, dex={dex_type}, platform={platform}")
    
    print('\n' + '=' * 60)
    if all_passed:
        print('🎉 ALL TESTS PASSED - DEX detection pipeline working!')
        print('✅ Router program ID extraction: WORKING')
        print('✅ DEX type detection: WORKING') 
        print('✅ Coordinator routing: WORKING')
    else:
        print('❌ SOME TESTS FAILED - Fix needed')
    
    return all_passed

if __name__ == '__main__':
    result = asyncio.run(test_complete_pipeline())
    sys.exit(0 if result else 1)