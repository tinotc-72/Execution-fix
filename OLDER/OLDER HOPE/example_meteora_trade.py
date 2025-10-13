#!/usr/bin/env python3
"""
Example usage of the Meteora Trading Bot
Demonstrates how to execute trades on Meteora's concentrated liquidity pools
"""

import asyncio
from solders.pubkey import Pubkey
from meteora_trading_bot import MeteoraTrader, TradeConfig, MeteoraPoolConfig

async def main():
    # Create trading configuration
    config = TradeConfig(
        sol_amount=0.1,  # Trade with 0.1 SOL
        slippage_tolerance=0.02,  # 2% slippage tolerance
        max_retries=3,
        retry_delay=1.0,
        confirmation_timeout=30.0,
        hold_time=5.0  # Hold for 5 seconds between buy and sell
    )
    
    # Initialize the trader
    trader = MeteoraTrader(config)
    
    try:
        # Example pool configuration (replace with actual pool values)
        pool_config = MeteoraPoolConfig(
            pool_id=Pubkey.from_string("YOUR_POOL_ID"),
            token_mint_a=Pubkey.from_string("So11111111111111111111111111111111111111112"),  # SOL
            token_mint_b=Pubkey.from_string("YOUR_TOKEN_MINT"),  # Target token
            token_vault_a=Pubkey.from_string("POOL_VAULT_A"),
            token_vault_b=Pubkey.from_string("POOL_VAULT_B"),
            tick_array_lower=Pubkey.from_string("TICK_ARRAY_LOWER"),
            tick_array_upper=Pubkey.from_string("TICK_ARRAY_UPPER"),
            pool_state=Pubkey.from_string("POOL_STATE")
        )
        
        # Execute trade cycle
        buy_result, sell_result = await trader.execute_trade_cycle(
            pool_config=pool_config,
            sol_amount=0.1  # Override config amount if needed
        )
        
        # Print results
        print("\nTrade Results:")
        print("-------------")
        print("Buy Transaction:")
        print(f"Success: {buy_result.success}")
        print(f"Signature: {buy_result.signature}")
        print(f"Amount In: {buy_result.amount_in / 1e9:.6f} SOL")
        if buy_result.amount_out:
            print(f"Tokens Received: {buy_result.amount_out}")
        if buy_result.error:
            print(f"Error: {buy_result.error}")
            
        if sell_result:
            print("\nSell Transaction:")
            print(f"Success: {sell_result.success}")
            print(f"Signature: {sell_result.signature}")
            print(f"Tokens Sold: {sell_result.amount_in}")
            if sell_result.amount_out:
                print(f"SOL Received: {sell_result.amount_out / 1e9:.6f}")
            if sell_result.error:
                print(f"Error: {sell_result.error}")
    
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
