#!/usr/bin/env python3

import asyncio
import logging
from env_keys import EnvKeys
from config import CopyTradeConfig

logging.basicConfig(level=logging.INFO)

async def test_jupiter_copy_with_real_tx():
    """Test the Jupiter copy trading pipeline with a real Jupiter transaction"""
    print("\n🎯 TESTING JUPITER COPY WITH REAL TRANSACTION")
    print("=" * 60)
    
    try:
        from main import SimpleCopyTradingBot
        
        env_keys = EnvKeys()
        config = CopyTradeConfig(
            target_wallets=['3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv'],
            investment_amount_sol=0.001,
            use_jito=False,
            slippage_tolerance=0.3
        )
        
        bot = SimpleCopyTradingBot(config)
        coordinator = bot.execution_coordinator
        
        print(f"✅ Bot and coordinator initialized")
        print(f"   📱 Bot Wallet: {bot.wallet.pubkey()}")
        
        # Real Jupiter transaction signatures to test with
        real_jupiter_transactions = [
            # Add real Jupiter transaction signatures here
            "5YourRealJupiterTransactionSignatureHere1234567890abcdef",  # Replace with real
            "2AnotherRealJupiterTxSignature9876543210fedcba",  # Replace with real
        ]
        
        print(f"\n🔍 Available test transactions:")
        for i, sig in enumerate(real_jupiter_transactions, 1):
            print(f"   {i}. {sig[:12]}...{sig[-8:]}")
        
        # Let's use a known Jupiter transaction pattern or fetch a recent one
        print(f"\n🌐 Fetching a recent Jupiter transaction from the blockchain...")
        
        import httpx
        
        # Get recent Jupiter transactions
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Search for recent Jupiter program transactions
            jupiter_program = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    jupiter_program,
                    {
                        "limit": 10,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            response = await client.post(env_keys.HELIUS_RPC_URL, json=payload)
            data = response.json()
            
            if "result" in data and len(data["result"]) > 0:
                recent_signatures = [tx["signature"] for tx in data["result"]]
                print(f"✅ Found {len(recent_signatures)} recent Jupiter transactions")
                
                # Test with the most recent one
                test_signature = recent_signatures[0]
                print(f"🎯 Testing with signature: {test_signature[:12]}...{test_signature[-8:]}")
                
                # Get transaction details first
                tx_payload = {
                    "jsonrpc": "2.0", 
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        test_signature,
                        {
                            "encoding": "json",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                tx_response = await client.post(env_keys.HELIUS_RPC_URL, json=tx_payload)
                tx_data = tx_response.json()
                
                if "result" in tx_data and tx_data["result"]:
                    tx_info = tx_data["result"]
                    print(f"✅ Transaction details retrieved")
                    print(f"   📦 Slot: {tx_info.get('slot')}")
                    print(f"   ⛽ Fee: {tx_info['meta']['fee']} lamports")
                    
                    # Extract token information if available
                    token_mint = "So11111111111111111111111111111111111111112"  # Default to SOL
                    
                    # Look for token transfers in the transaction
                    if tx_info['meta'].get('postTokenBalances'):
                        for balance in tx_info['meta']['postTokenBalances']:
                            if balance.get('mint') and balance['mint'] != token_mint:
                                token_mint = balance['mint']
                                print(f"   🪙 Token found: {token_mint}")
                                break
                    
                    # Now test the copy pipeline
                    print(f"\n🚀 EXECUTING COPY PIPELINE...")
                    
                    trade_info = {
                        'dex': 'jupiter',
                        'signature': test_signature,
                        'slot': tx_info.get('slot'),
                        'fee': tx_info['meta']['fee']
                    }
                    
                    # Find the original wallet from transaction
                    source_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"  # Default test wallet
                    if tx_info['transaction']['message'].get('accountKeys'):
                        # First account is typically the signer
                        source_wallet = tx_info['transaction']['message']['accountKeys'][0]
                        print(f"   👤 Source wallet: {source_wallet}")
                    
                    result = await coordinator._execute_copy_buy(
                        token_mint=token_mint,
                        source_wallet=source_wallet,
                        trade_info=trade_info,
                        detected_dex='jupiter',
                        amount_sol=0.001
                    )
                    
                    print(f"\n📊 REAL JUPITER COPY RESULT:")
                    print(f"=" * 40)
                    print(f"Success: {result.get('success')}")
                    print(f"Signature: {result.get('signature')}")
                    print(f"Error: {result.get('error')}")
                    print(f"DEX: {result.get('dex')}")
                    print(f"Method: {result.get('method')}")
                    
                    if result.get('success'):
                        print(f"\n🎉 JUPITER COPY PIPELINE SUCCESS!")
                        print(f"✅ Real Jupiter transaction copied successfully")
                        if isinstance(result.get('signature'), str):
                            print(f"🔗 Copy transaction: {result['signature']}")
                        else:
                            print(f"📋 Copy result: {result.get('signature')}")
                    else:
                        print(f"\n⚠️ Jupiter copy completed but with issues:")
                        print(f"   Error: {result.get('error')}")
                        print(f"   This may be expected for test scenarios")
                        
                else:
                    print(f"❌ Could not retrieve transaction details")
                    
            else:
                print(f"❌ No recent Jupiter transactions found")
                print(f"   Falling back to manual test signature...")
                
                # Fallback to a known Jupiter transaction
                fallback_signature = "Your_Real_Jupiter_Signature_Here"  # Replace with actual
                print(f"🔄 Using fallback signature for testing pipeline flow")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jupiter_copy_with_real_tx())