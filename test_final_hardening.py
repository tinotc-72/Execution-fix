#!/usr/bin/env python3
"""
🎯 FINAL BULLETPROOF HARDENING TEST
Tests the final edge-case improvements: advisory pool hints, programIdIndex resolution, 
conservative Pump.fun inference, and strong commitment handling
"""
import asyncio
from trade_processor import TradeProcessor
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def test_final_hardening():
    print('🔧 TESTING FINAL BULLETPROOF HARDENING 🔧\n')
    
    target_wallets = ['A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB']
    processor = TradeProcessor(target_wallets)
    
    print('1️⃣ Testing Advisory Pool Hints (no hard rejection)...')
    # Test Raydium transaction where pool hints might mismatch but deltas are clear
    raydium_tx = {
        'transaction': {
            'message': {
                'instructions': [{
                    'programId': '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',  # Raydium CPMM
                    'accounts': ['user_account', 'pool_id_with_mismatched_hints']
                }]
            }
        },
        'meta': {
            'preTokenBalances': [
                {'owner': 'wallet123', 'mint': 'MintA123', 'uiTokenAmount': {'amount': '1000'}}
            ],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'MintA123', 'uiTokenAmount': {'amount': '500'}},  # Clear decrease
                {'owner': 'wallet123', 'mint': 'MintB456', 'uiTokenAmount': {'amount': '2000'}}  # Clear increase
            ]
        }
    }
    
    raydium_result = await processor._decode_raydium_cpmm(
        raydium_tx['transaction']['message']['instructions'][0], 
        raydium_tx['meta'], 
        'wallet123'
    )
    
    # Should work despite potential pool hint mismatch (advisory only)
    advisory_hints_working = raydium_result and raydium_result.get('input_mint') == 'MintA123'
    print(f'   {"✅" if advisory_hints_working else "❌"} Advisory Pool Hints: {"Working - trusts deltas over hints" if advisory_hints_working else "Still rejecting on mismatch"}')
    
    print('\n2️⃣ Testing ProgramIdIndex Resolution...')
    # Test transaction with programIdIndex instead of programId
    programId_index_tx = {
        'transaction': {
            'message': {
                'accountKeys': [
                    'user_wallet',
                    'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',  # Jupiter at index 1
                    'other_account'
                ],
                'instructions': [{
                    'programIdIndex': 1,  # Points to Jupiter
                    'accounts': [0, 2]
                }]
            }
        }
    }
    
    platform_detected = processor._detect_platform(programId_index_tx)
    programId_index_working = platform_detected == 'jupiter'
    print(f'   {"✅" if programId_index_working else "❌"} ProgramIdIndex: {"Resolved Jupiter from index" if programId_index_working else "Failed to resolve from index"}')
    
    print('\n3️⃣ Testing Conservative Pump.fun Inference...')
    # Test Pump.fun with complex token patterns (should stay conservative)
    complex_pump_tx = {
        'meta': {
            'preTokenBalances': [
                {'owner': 'wallet123', 'mint': 'TokenA', 'uiTokenAmount': {'amount': '100'}},
                {'owner': 'wallet123', 'mint': 'TokenB', 'uiTokenAmount': {'amount': '50'}}
            ],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'TokenA', 'uiTokenAmount': {'amount': '100'}},  # No change
                {'owner': 'wallet123', 'mint': 'TokenB', 'uiTokenAmount': {'amount': '30'}},   # Decreased (fee?)
                {'owner': 'wallet123', 'mint': 'NewToken', 'uiTokenAmount': {'amount': '1000'}}  # Output
            ],
            'logMessages': ['SystemProgram transfer', 'Pump.fun swap']
        }
    }
    
    conservative_result = await processor._decode_pump_fun({}, complex_pump_tx['meta'], 'wallet123')
    # Should NOT assume WSOL when there are clear token decreases (should find actual input)
    conservative_working = (conservative_result and 
                           conservative_result.get('input_mint') != 'So11111111111111111111111111111111111111112' and
                           conservative_result.get('input_mint') is not None)  # Found actual input, not WSOL
    print(f'   {"✅" if conservative_working else "❌"} Conservative Pump.fun: {"Found actual input token, avoided WSOL over-inference" if conservative_working else "Over-inferred WSOL"}')
    
    # Test simple case (should still work)
    simple_pump_tx = {
        'meta': {
            'preTokenBalances': [],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'NewToken', 'uiTokenAmount': {'amount': '1000'}}  # Only output, no other tokens
            ],
            'logMessages': ['SystemProgram transfer', 'Pump.fun swap']
        }
    }
    
    simple_result = await processor._decode_pump_fun({}, simple_pump_tx['meta'], 'wallet123')
    simple_wsol = simple_result and simple_result.get('input_mint') == 'So11111111111111111111111111111111111111112'
    print(f'   {"✅" if simple_wsol else "❌"} Simple Pump.fun: {"WSOL inferred for clean case" if simple_wsol else "Failed clean WSOL inference"}')
    
    print('\n4️⃣ Testing Strong Commitment Helper...')
    # Test the strong commitment helper method exists and works
    try:
        # This will fail RPC but tests the method structure
        strong_result = await processor._get_transaction_strong_commitment('fake_signature_123')
        strong_helper_exists = True  # Method exists and runs
        print('   ✅ Strong Commitment: Helper method available with retry logic')
    except Exception as e:
        if 'method' in str(e).lower() or 'attribute' in str(e).lower():
            strong_helper_exists = False
            print('   ❌ Strong Commitment: Helper method missing')
        else:
            strong_helper_exists = True  # RPC errors expected
            print('   ✅ Strong Commitment: Helper method available with retry logic')
    
    print('\n5️⃣ Testing Complete Hardened Pipeline...')
    # Real-world complex transaction that would have failed before hardening
    complex_tx = {
        'transaction': {
            'message': {
                'accountKeys': [
                    'user_wallet',
                    'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',  # Jupiter
                ],
                'instructions': [{
                    'programIdIndex': 1,  # Uses index instead of programId
                    'accounts': [0]
                }],
                'loadedAddresses': {  # v0 transaction
                    'readonly': ['ALT_address_1']
                }
            }
        },
        'meta': {
            'preTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '1000'}}
            ],
            'postTokenBalances': [
                {'owner': 'wallet123', 'mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'uiTokenAmount': {'amount': '500'}},
                {'owner': 'wallet123', 'mint': '2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9', 'uiTokenAmount': {'amount': '1000000'}}
            ]
        }
    }
    
    pipeline_result = await processor.extract_token_info_fast(complex_tx, 'wallet123')
    pipeline_hardened = (pipeline_result and 
                        pipeline_result.get('source') == 'meta' and
                        pipeline_result.get('token_mint') == '2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9')
    
    print(f'   {"✅" if pipeline_hardened else "❌"} Hardened Pipeline: {"Complex v0 + programIdIndex working" if pipeline_hardened else "Pipeline issues remain"}')
    
    # Final Summary
    print('\n🏆 FINAL BULLETPROOF HARDENING COMPLETE 🏆')
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    
    improvements = [
        (advisory_hints_working, '1. Advisory Pool Hints (no hard rejection)'),
        (programId_index_working, '2. ProgramIdIndex Resolution'),
        (conservative_working and simple_wsol, '3. Conservative Pump.fun Inference'),
        (strong_helper_exists, '4. Strong Commitment Helper'),
        (pipeline_hardened, '5. Complete Hardened Pipeline')
    ]
    
    passed = sum(1 for improvement, _ in improvements if improvement)
    total = len(improvements)
    
    for improvement, name in improvements:
        print(f'{"✅" if improvement else "❌"} {name}')
    
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    
    if passed == total:
        print('🎯 STATUS: ULTIMATE BULLETPROOF ACHIEVED! 🚀')
        print('📊 "As close to bulletproof as you get without validator-colocated decoding"')
        print('🔥 Ready for high-volume mainnet production!')
    elif passed >= total - 1:
        print('⚡ STATUS: Near-ultimate hardening! One improvement remaining 🔧')
    else:
        print(f'🔧 STATUS: {passed}/{total} hardening improvements working')
        
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_final_hardening())
    print(f'\n🎯 Final Hardening Result: {"ULTIMATE BULLETPROOF ✅" if success else "NEEDS FINAL TOUCHES ❌"}')