#!/usr/bin/env python3
"""
Test script for Raydium Trade Executor
Demonstrates how to use the RaydiumTradeExecutor in your copy bot
"""

import asyncio
from raydium_trade_executor import RaydiumTradeExecutor, TradeConfig
from env_keys import load_wallet_from_private_key, validate_env_vars
from solders.pubkey import Pubkey

async def test_raydium_executor():
    """Test the Raydium trade executor"""
    
    print("🧪 TESTING RAYDIUM TRADE EXECUTOR")
    print("=" * 50)
    
    try:
        # Load environment and wallet
        env_vars = validate_env_vars()
        wallet = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
        
        # Configure the executor
        config = TradeConfig(
            sol_amount=0.001,  # Very small amount for testing
            slippage_tolerance=0.05,
            max_retries=2,
            confirmation_timeout=30.0
        )
        
        # Initialize executor
        executor = RaydiumTradeExecutor(
            wallet_keypair=wallet,
            rpc_url=env_vars["RPC_URL"],
            config=config
        )
        
        print(f"👛 Wallet: {wallet.pubkey()}")
        print(f"💰 SOL Balance: {await executor.get_sol_balance():.6f} SOL")
        
        # Test token (USDC for example)
        test_token = executor.USDC_MINT
        print(f"🪙 Test token: {test_token}")
        
        # Check if we can find pool info
        pool_info = await executor.find_pool_for_token(test_token)
        if pool_info:
            print(f"✅ Found pool: {pool_info['pool_id']}")
            print(f"   Base vault: {pool_info['base_vault']}")
            print(f"   Quote vault: {pool_info['quote_vault']}")
        else:
            print("❌ No pool found")
            return
        
        # Test buy trade (small amount)
        print(f"\n🛒 Testing BUY trade: {config.sol_amount} SOL → USDC")
        buy_signature = await executor.execute_buy_trade(
            token_mint=test_token,
            sol_amount=config.sol_amount,
            pool_info=pool_info
        )
        
        if buy_signature:
            print(f"✅ Buy transaction sent: {buy_signature}")
            
            # Confirm the transaction
            print("⏳ Confirming transaction...")
            confirmed = await executor.confirm_transaction(buy_signature)
            if confirmed:
                print("✅ Buy transaction confirmed!")
                
                # Check token balance
                token_balance = await executor.get_token_balance(test_token)
                print(f"💰 Token balance: {token_balance:,} micro-USDC")
                
                if token_balance > 0:
                    # Test sell trade
                    print(f"\n💸 Testing SELL trade: {token_balance:,} tokens → SOL")
                    sell_signature = await executor.execute_sell_trade(
                        token_mint=test_token,
                        token_amount=token_balance,
                        pool_info=pool_info
                    )
                    
                    if sell_signature:
                        print(f"✅ Sell transaction sent: {sell_signature}")
                        
                        # Confirm sell
                        print("⏳ Confirming sell transaction...")
                        sell_confirmed = await executor.confirm_transaction(sell_signature)
                        if sell_confirmed:
                            print("✅ Sell transaction confirmed!")
                            print("🎉 Complete trade cycle successful!")
                        else:
                            print("❌ Sell transaction failed to confirm")
                    else:
                        print("❌ Sell transaction failed")
                else:
                    print("⚠️ No tokens received from buy")
            else:
                print("❌ Buy transaction failed to confirm")
        else:
            print("❌ Buy transaction failed")
        
        # Close the executor
        await executor.close()
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raydium_executor())
