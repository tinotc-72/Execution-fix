import asyncio
from solders.keypair import Keypair
from env_keys import EnvKeys
from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

async def main():
    env = EnvKeys()
    wallet_keypair = Keypair.from_base58_string(env.PHANTOM_PRIVATE_KEY)
    rpc_url = env.HELIUS_RPC_URL
    print("\n=== Testing Jupiter Executor ===")
    buy_result = await try_jupiter_buy(wallet_keypair, USDC_MINT, 0.001, rpc_url=rpc_url)
    print("Buy result:", buy_result)
    await asyncio.sleep(5)
    if buy_result.get('success'):
        sell_result = await try_jupiter_sell_all(wallet_keypair, USDC_MINT, rpc_url=rpc_url)
        print("Sell result:", sell_result)

if __name__ == "__main__":
    asyncio.run(main())
