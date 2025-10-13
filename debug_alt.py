#!/usr/bin/env python3
"""
Debug ALT support specifically
"""
import asyncio
from trade_processor import TradeProcessor
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def debug_alt_support():
    print('🔍 DEBUGGING ALT SUPPORT 🔍\n')
    
    target_wallets = ['A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB']
    processor = TradeProcessor(target_wallets)
    
    # Test with properly formatted base58 addresses
    alt_tx = {
        'transaction': {'message': {'accountKeys': ['11111111111111111111111111111111']}},
        'meta': {
            'loadedAddresses': {
                'writable': ['6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'],
                'readonly': ['So11111111111111111111111111111111111111112', '2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9']
            }
        }
    }
    
    print('Input transaction structure:')
    print(f'  accountKeys: {alt_tx["transaction"]["message"]["accountKeys"]}')
    print(f'  loadedAddresses.writable: {alt_tx["meta"]["loadedAddresses"]["writable"]}')
    print(f'  loadedAddresses.readonly: {alt_tx["meta"]["loadedAddresses"]["readonly"]}')
    print()
    
    # Call the method and debug step by step
    result = processor._candidates_from_atas(alt_tx, 'test_wallet')
    print(f'Result: {result}')
    print(f'Result type: {type(result)}')
    
    if result:
        print(f'Candidate 1: {result[0]}')
        print(f'Candidate 2: {result[1] if len(result) > 1 and result[1] else "None"}')
        
        # Check which addresses should be included
        expected = ['6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 
                   'So11111111111111111111111111111111111111112', '2wmVCSfPxGPjrnMMn7rchp4uaeoTqN39mXFC2zhPdri9']
        
        print('\nExpected ALT addresses that should be found:')
        for addr in expected:
            found = addr in [result[0], result[1]] if result[1] else addr == result[0]
            print(f'  {addr}: {"✅ Found" if found else "❌ Missing"}')
    else:
        print('❌ No candidates returned')

if __name__ == "__main__":
    asyncio.run(debug_alt_support())