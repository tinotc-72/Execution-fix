#!/usr/bin/env python3
"""
Test Enhanced Jupiter Balance Analysis
"""

import asyncio
from trade_processor import TradeProcessor
import httpx

def create_mock_jupiter_transaction():
    """
    Create a mock Jupiter transaction with clear balance changes
    This simulates a real Jupiter swap where tokens actually change
    """
    return {
        'meta': {
            'preTokenBalances': [
                {
                    'accountIndex': 5,
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL (will be excluded)
                    'owner': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
                    'uiTokenAmount': {
                        'amount': '50000000',  # 0.05 SOL
                        'decimals': 9,
                        'uiAmount': 0.05
                    }
                },
                {
                    'accountIndex': 6,
                    'mint': 'CKfatsPMUf8SkiURsDXs7eK6GWb4Jsd6UDbs7twMCWxo',  # Target token
                    'owner': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
                    'uiTokenAmount': {
                        'amount': '0',  # No tokens before
                        'decimals': 6,
                        'uiAmount': 0.0
                    }
                }
            ],
            'postTokenBalances': [
                {
                    'accountIndex': 5,
                    'mint': 'So11111111111111111111111111111111111111112',  # WSOL (decreased)
                    'owner': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
                    'uiTokenAmount': {
                        'amount': '10000000',  # 0.01 SOL left
                        'decimals': 9,
                        'uiAmount': 0.01
                    }
                },
                {
                    'accountIndex': 6,
                    'mint': 'CKfatsPMUf8SkiURsDXs7eK6GWb4Jsd6UDbs7twMCWxo',  # Target token
                    'owner': '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76',
                    'uiTokenAmount': {
                        'amount': '1500000000',  # 1,500 tokens received
                        'decimals': 6,
                        'uiAmount': 1500.0
                    }
                },
                # Add another wallet's changes to test multi-wallet analysis
                {
                    'accountIndex': 7,
                    'mint': 'CKfatsPMUf8SkiURsDXs7eK6GWb4Jsd6UDbs7twMCWxo',  # Same token, different wallet
                    'owner': 'AnotherWallet1234567890123456789012345678901',
                    'uiTokenAmount': {
                        'amount': '500000000',  # 500 tokens
                        'decimals': 6,
                        'uiAmount': 500.0
                    }
                }
            ]
        }
    }

async def test_enhanced_jupiter_analysis():
    """Test the enhanced Jupiter balance change analysis"""
    
    processor = TradeProcessor(httpx.AsyncClient())
    target_wallet = '3LoAYHuSd7Gh8d7RTFnhvYtiTiefdZ5ByamU42vkzd76'
    
    mock_transaction = create_mock_jupiter_transaction()
    
    print("🚀 TESTING ENHANCED JUPITER ANALYSIS")
    print("=" * 50)
    
    print(f"🎯 Target Wallet: {target_wallet[:12]}...")
    print(f"📊 Transaction has {len(mock_transaction['meta']['preTokenBalances'])} pre-balances")
    print(f"📊 Transaction has {len(mock_transaction['meta']['postTokenBalances'])} post-balances")
    print()
    
    # Test 1: Wallet-specific analysis
    print("🧪 TEST 1: Wallet-Specific Analysis")
    print("-" * 30)
    
    wallet_token = await processor._extract_jupiter_token_with_wallet_context(mock_transaction, target_wallet)
    if wallet_token:
        print(f"✅ Wallet-specific token: {wallet_token[:8]}...")
        
        # Test action determination
        action = await processor._determine_action_for_wallet(mock_transaction, target_wallet, wallet_token)
        print(f"   Action for wallet: {action}")
    else:
        print("❌ No wallet-specific token found")
    
    print()
    
    # Test 2: Advanced multi-wallet analysis
    print("🧪 TEST 2: Advanced Multi-Wallet Analysis")
    print("-" * 30)
    
    advanced_token = await processor._extract_jupiter_token_from_balance_changes(mock_transaction)
    if advanced_token:
        print(f"✅ Advanced analysis token: {advanced_token[:8]}...")
    else:
        print("❌ No token from advanced analysis")
    
    print()
    
    # Test 3: Compare results
    print("📋 COMPARISON")
    print("-" * 30)
    print(f"Wallet-specific:  {wallet_token[:8] if wallet_token else 'None'}...")
    print(f"Advanced analysis: {advanced_token[:8] if advanced_token else 'None'}...")
    print(f"Match: {'✅ Yes' if wallet_token == advanced_token else '❌ Different'}")
    
    return wallet_token

if __name__ == "__main__":
    result = asyncio.run(test_enhanced_jupiter_analysis())
    print(f"\n🎉 Final Result: {result[:8] if result else 'None'}...")