import asyncio
import time
from solders.keypair import Keypair
from env_keys import EnvKeys

# Import all executor test entry points
from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
from raydium_copy_executor import RaydiumCopyExecutor, ExtractedRaydiumTradeInfo
from orca_copy_executor import OrcaCopyExecutor
from phoenix_copy_executor import PhoenixCopyExecutor

# USDC Mint (mainnet)
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"

async def test_jupiter(wallet_keypair, rpc_url):
    print("\n=== Testing Jupiter Executor ===")
    buy_result = await try_jupiter_buy(wallet_keypair, USDC_MINT, 0.001, rpc_url=rpc_url)
    print("Buy result:", buy_result)
    await asyncio.sleep(5)
    if buy_result.get('success'):
        sell_result = await try_jupiter_sell_all(wallet_keypair, USDC_MINT, rpc_url=rpc_url)
        print("Sell result:", sell_result)

async def test_raydium(wallet_keypair, rpc_url):
    print("\n=== Testing Raydium Executor ===")
    # You need to provide pool_info for Raydium. For test, use a known USDC/SOL pool (replace with real one if needed)
    pool_info = {
        "pool_id": "6UeJjQ2Qk4V5Qn2Qw2r8h1i6i1k1k1k1k1k1k1k1k1k1",  # Replace with real pool id
        "amm_authority": "...",
        "open_orders": "...",
        "target_orders": "...",
        "base_vault": "...",
        "quote_vault": "...",
        "serum_program": "...",
        "market_id": "...",
        "market_bids": "...",
        "market_asks": "...",
        "market_event_queue": "...",
        "market_base_vault": "...",
        "market_quote_vault": "...",
        "market_authority": "..."
    }
    trade_info = ExtractedRaydiumTradeInfo(
        token_mint=USDC_MINT,
        is_buy=True,
        amount_in=int(0.001 * 1_000_000_000),
        pool_info=pool_info,
        original_signature="test",
        wallet_address=str(wallet_keypair.pubkey())
    )
    executor = RaydiumCopyExecutor(wallet_keypair, rpc_url)
    buy_sig = await executor.execute_buy_copy(trade_info, 0.001)
    print("Buy signature:", buy_sig)
    await asyncio.sleep(5)
    # For sell, just reuse trade_info with is_buy=False
    trade_info.is_buy = False
    sell_sig = await executor.execute_sell_copy(trade_info)
    print("Sell signature:", sell_sig)

async def test_orca(wallet_keypair, rpc_url):
    print("\n=== Testing Orca Executor ===")
    executor = OrcaCopyExecutor(wallet_keypair, rpc_url)
    buy_result = await executor.try_orca_buy(USDC_MINT, 0.001)
    print("Buy result:", buy_result)
    await asyncio.sleep(5)
    sell_result = await executor.try_orca_sell_all(USDC_MINT)
    print("Sell result:", sell_result)
    await executor.close()

async def test_phoenix(wallet_keypair, rpc_url):
    print("\n=== Testing Phoenix Executor ===")
    executor = PhoenixCopyExecutor(wallet_keypair)
    buy_result = await executor.try_phoenix_buy(USDC_MINT, 0.001)
    print("Buy result:", buy_result)
    await asyncio.sleep(5)
    sell_result = await executor.try_phoenix_sell_all(USDC_MINT)
    print("Sell result:", sell_result)
    await executor.close()

async def main():
    env = EnvKeys()
    wallet_keypair = Keypair.from_base58_string(env.PRIVATE_KEY)
    rpc_url = env.HELIUS_RPC_URL
    await test_jupiter(wallet_keypair, rpc_url)
    await test_raydium(wallet_keypair, rpc_url)
    await test_orca(wallet_keypair, rpc_url)
    await test_phoenix(wallet_keypair, rpc_url)

if __name__ == "__main__":
    asyncio.run(main())
