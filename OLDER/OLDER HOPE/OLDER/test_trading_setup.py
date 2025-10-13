import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
import base58
from env_keys import kz
import time

WRAPPED_SOL = "So11111111111111111111111111111111111111112"

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def request_airdrop(client: AsyncClient, pubkey: Pubkey, amount_sol: float = 1.0) -> bool:
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            amount_lamports = int(amount_sol * 1e9)
            print(f"Attempt {attempt + 1}/{max_attempts}...")
            
            # Get recent blockhash for transaction
            recent_blockhash = await client.get_latest_blockhash()
            if not recent_blockhash.value:
                print("Failed to get recent blockhash")
                continue
                
            # Request airdrop
            result = await client.request_airdrop(pubkey, amount_lamports, recent_blockhash.value.blockhash)
            if not result.value:
                print("Airdrop request failed")
                continue
                
            print(f"Airdrop requested with signature: {result.value}")
            
            # Wait for confirmation with exponential backoff
            timeout = 10 * (2 ** attempt)  # 10s, 20s, 40s
            for _ in range(timeout):
                try:
                    conf = await client.confirm_transaction(result.value)
                    if conf.value:
                        # Verify balance increase
                        balance = await get_balance(client, pubkey)
                        if balance >= amount_sol:
                            return True
                except Exception as e:
                    print(".", end="", flush=True)
                await asyncio.sleep(1)
            print()  # New line after dots
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff between attempts
            continue
    
    return False

async def main():
    print("🔥 Testing Trading Setup")
    print("=======================")
    
    # Load wallet
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {str(e)}")
        return

    # Try different RPC endpoints
    endpoints = [
        kz.HELIUS_DEVNET_RPC_URL,  # Primary Helius devnet endpoint
        "https://api.devnet.solana.com",  # Public fallback
    ]

    for endpoint in endpoints:
        print(f"\n🔄 Trying endpoint: {endpoint}")
        client = AsyncClient(endpoint)
        
        try:
            # Check initial balance
            balance = await get_balance(client, keypair.pubkey())
            print(f"Initial balance: {balance} SOL")

            if balance < 0.5:
                print("💸 Requesting 1 SOL airdrop...")
                if await request_airdrop(client, keypair.pubkey(), 1.0):
                    print("✅ Airdrop successful!")
                    balance = await get_balance(client, keypair.pubkey())
                    print(f"New balance: {balance} SOL")
                else:
                    print("❌ Airdrop failed, trying next endpoint...")
                    continue
            
            print("\n✅ Wallet is ready for trading!")
            print(f"Final balance: {balance} SOL")
            return True

        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
            continue
        finally:
            await client.close()

    print("\n❌ All endpoints failed!")
    return False

if __name__ == "__main__":
    asyncio.run(main())
