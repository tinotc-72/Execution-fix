#!/usr/bin/env python3
"""
Test script for Meteora trading bot
Testing with specific meme token: 31rDjiE4pNm56HnNpA4ujCMbcZmh7E1FmTNnnB5jjups
"""

import asyncio
from solders.pubkey import Pubkey
from meteora_trading_bot import MeteoraTrader, MeteoraPoolConfig

async def main():
    # Initialize trader
    trader = MeteoraTrader()
    
    try:
        # Configure pool using values from analyzed transaction
        pool_config = MeteoraPoolConfig(
            # Pool State - from transaction
            pool_state=Pubkey.from_string("HLnpSz9h2S4hiLQ43rnSD9XkcUThA7B8hQMKmDaiTLcC"),
            
            # Token mints
            token_mint_a=Pubkey.from_string("So11111111111111111111111111111111111111112"),  # SOL
            token_mint_b=Pubkey.from_string("31rDjiE4pNm56HnNpA4ujCMbcZmh7E1FmTNnnB5jjups"),  # Meme token
            
            # Token vaults - from transaction
            token_vault_a=Pubkey.from_string("7XwqCd5jSisHvPaN1cNmQmZRRHHLSBhVoUdwBV8dXZnz"),  # SOL vault
            token_vault_b=Pubkey.from_string("G3Ln9At92KSLB87MSofagB6RnTiCoHFsejH1RVtzn5ck"),  # Token vault
            
            # Tick arrays - from transaction
            tick_array_lower=Pubkey.from_string("9PQNbkKHFCwcZVB8h48SRPEmKZgKUz28dyCMJfMedSJ7"),
            tick_array_upper=Pubkey.from_string("ERpnkz7bTLYHPds67agacnAgR1RDRebcaT2v9QXWmEV"),
            
            # Pool authority - from transaction
            pool_authority=Pubkey.from_string("3rmHSu74h1ZcmAisVcWerTCiRDQbUrBKmcwptYGjHfet")
        )
        
        print("\n=== Meteora Trading Test ===")
        print(f"Token: {pool_config.token_mint_b}")
        print(f"Pool: {pool_config.pool_state}")
        
        # Check initial balances
        sol_balance = await trader.get_token_balance(pool_config.token_mint_a)
        token_balance = await trader.get_token_balance(pool_config.token_mint_b)
        
        print(f"\nInitial Balances:")
        print(f"SOL: {sol_balance / 1e9:.6f}")
        print(f"Token: {token_balance}")
        
        # Execute trade cycle with small amount
        print("\nStarting trade cycle...")
        success = await trader.execute_trade_cycle(
            pool_config=pool_config,
            amount_in_sol=0.01,    # Test with 0.01 SOL
            slippage_bps=1000,     # 10% slippage tolerance
            hold_time=5.0          # Hold for 5 seconds
        )
        
        if success:
            print("\n✅ Trade cycle completed!")
            # Check final balances
            final_sol = await trader.get_token_balance(pool_config.token_mint_a)
            final_token = await trader.get_token_balance(pool_config.token_mint_b)
            
            print(f"\nFinal Balances:")
            print(f"SOL: {final_sol / 1e9:.6f}")
            print(f"Token: {final_token}")
            
            # Calculate profit/loss
            sol_change = (final_sol - sol_balance) / 1e9
            print(f"\nSOL Change: {sol_change:+.6f}")
        else:
            print("\n❌ Trade cycle failed")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
