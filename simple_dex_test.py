#!/usr/bin/env python3
"""
Simple test to verify DEX program detection is working
"""
import asyncio
from main import CopyTradingBot, CopyTradeConfig

async def test_dex_detection():
    """Test DEX program detection with a simple transaction"""
    print("🧪 Testing DEX Program Detection with Official Solana Method")
    
    # Initialize bot
    config = CopyTradeConfig()
    config.target_wallets = ["suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"]
    
    bot = CopyTradingBot(config)
    
    # Try to get recent transactions 
    try:
        print("📡 Connecting to RPC...")
        from solders.pubkey import Pubkey
        from solana.rpc.commitment import Confirmed
        
        wallet_pubkey = Pubkey.from_string("suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK")
        
        # Get just 1 recent transaction
        response = await bot.rpc_client.get_signatures_for_address(
            wallet_pubkey,
            limit=1
        )
        
        if response.value:
            signature = str(response.value[0].signature)
            print(f"🔍 Testing with transaction: {signature}")
            
            # Analyze the transaction
            await bot.analyze_transaction(signature, "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK")
        else:
            print("❌ No transactions found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.rpc_client.close()

if __name__ == "__main__":
    asyncio.run(test_dex_detection())
