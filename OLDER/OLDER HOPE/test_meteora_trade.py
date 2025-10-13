#!/usr/bin/env python3
"""
Test script for Meteora trading bot
Using real pool values from analyzed transaction
"""

import asyncio
from solders.pubkey import Pubkey
from meteora_trading_bot import MeteoraTrader, MeteoraPoolConfig

async def main():
    # Initialize trader
    trader = MeteoraTrader()
    
    try:
        # Configure pool using values from the analyzed transaction
        pool_config = MeteoraPoolConfig(
            pool_state=Pubkey.from_string("8bnKeevCLsmbudhjkwg6GFMcsZpf78cs8pzRxzMqwZLa"),  # Pool state
            token_mint_a=Pubkey.from_string("So11111111111111111111111111111111111111112"),  # SOL
            token_mint_b=Pubkey.from_string("31rDjiE4pNm56HnNpA4ujCMbcZmh7E1FmTNnnB5jjups"),  # Target token
            token_vault_a=Pubkey.from_string("7XwqCd5jSisHvPaN1cNmQmZRRHHLSBhVoUdwBV8dXZnz"),  # SOL vault
            token_vault_b=Pubkey.from_string("G3Ln9At92KSLB87MSofagB6RnTiCoHFsejH1RVtzn5ck"),  # Token vault
            tick_array_lower=Pubkey.from_string("9PQNbkKHFCwcZVB8h48SRPEmKZgKUz28dyCMJfMedSJ7"),
            tick_array_upper=Pubkey.from_string("ERpnkz7bTLYHPds67agacnAgR1RDRebcaT2v9QXWmEV"),
            pool_authority=Pubkey.from_string("3rmHSu74h1ZcmAisVcWerTCiRDQbUrBKmcwptYGjHfet")
        )
        
        # Execute trade cycle with 0.005 SOL
        print("\nStarting Meteora trade cycle...")
        print(f"Pool: {pool_config.pool_state}")
        print(f"Token: {pool_config.token_mint_b}")
        
        success = await trader.execute_trade_cycle(
            pool_config=pool_config,
            amount_in_sol=0.005,  # Small test amount
            slippage_bps=100,     # 1% slippage
            hold_time=5.0         # 5 second hold
        )
        
        if success:
            print("\n✅ Trade cycle completed successfully!")
        else:
            print("\n❌ Trade cycle failed")
            
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
