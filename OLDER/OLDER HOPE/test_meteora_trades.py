#!/usr/bin/env python3
"""
Test trading script for Meteora
Using same parameters and structure as production pump trading bot
"""

import asyncio
import logging
from datetime import datetime
from meteora_trading_bot import MeteoraTrader, TradeConfig, TradeAction, TradeResult

async def run_test_trades():
    # Initialize with same parameters as production bot
    config = TradeConfig(
        sol_amount=0.005,          # 0.005 SOL per trade
        slippage_tolerance=0.10,   # 10% slippage tolerance
        max_retries=1,            # Single attempt
        retry_delay=0.0,          # No delay between retries
        confirmation_timeout=10.0, # 10s timeout
        max_balance_checks=1,      # Single balance check
        initial_wait_time=0.0,    # No initial wait
        hold_time=5.0             # 5s hold time
    )
    
    trader = MeteoraTrader(config)
    
    try:
        # Use the test token configuration that's built into the trader
        pool_config = trader.TEST_TOKEN_CONFIG
        
        print("\n=== Meteora Trading Test ===")
        print(f"Token: {pool_config.token_mint_b}")
        print(f"Pool: {pool_config.pool_state}")
        
        # Check initial balances
        initial_sol = await trader.get_token_balance(pool_config.token_mint_a)
        initial_tokens = await trader.get_token_balance(pool_config.token_mint_b)
        
        print(f"\nInitial Balances:")
        print(f"SOL: {initial_sol / 1e9:.6f}")
        print(f"Token: {initial_tokens}")
        
        # Execute buy
        print("\nExecuting buy...")
        buy_result = await trader.execute_swap(
            pool_config=pool_config,
            amount_in=int(config.sol_amount * 1e9),  # Convert SOL to lamports
            min_amount_out=0,  # Accept any amount of tokens
            is_buy=True
        )
        
        if buy_result:
            # Check tokens received
            tokens = await trader.get_token_balance(pool_config.token_mint_b)
            tokens_received = tokens - initial_tokens
            print(f"Buy successful! Received {tokens_received} tokens")
            
            # Hold period
            print(f"\nHolding for {config.hold_time} seconds...")
            await asyncio.sleep(config.hold_time)
            
            # Execute sell
            print("\nExecuting sell...")
            sell_result = await trader.execute_swap(
                pool_config=pool_config,
                amount_in=tokens_received,
                min_amount_out=int(config.sol_amount * 0.9 * 1e9),  # Minimum 90% of input SOL
                is_buy=False
            )
            
            if sell_result:
                # Check final balances
                final_sol = await trader.get_token_balance(pool_config.token_mint_a)
                final_tokens = await trader.get_token_balance(pool_config.token_mint_b)
                
                print(f"\nTrade cycle completed!")
                print(f"Final SOL: {final_sol / 1e9:.6f}")
                print(f"Final Tokens: {final_tokens}")
                print(f"SOL Change: {(final_sol - initial_sol) / 1e9:+.6f}")
            else:
                print("\n❌ Sell failed")
        else:
            print("\n❌ Buy failed")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(run_test_trades())
