import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
import base58
from env_keys import kz

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def request_minimal_airdrop(client: AsyncClient, pubkey: Pubkey) -> bool:
    """Request a minimal airdrop (0.1 SOL) to avoid rate limiting"""
    try:
        amount_lamports = int(0.1 * 1e9)  # 0.1 SOL
        print(f"\nRequesting minimal airdrop of 0.1 SOL...")
        
        # Get latest blockhash
        recent_blockhash = await client.get_latest_blockhash()
        print(f"Got blockhash: {recent_blockhash.value.blockhash}")
        
        # Request airdrop
        result = await client.request_airdrop(pubkey, amount_lamports, recent_blockhash.value.blockhash)
        if not result.value:
            print("Airdrop request failed")
            return False
            
        print(f"Airdrop requested. Signature: {result.value}")
        
        # Wait for confirmation
        for _ in range(30):
            try:
                conf = await client.confirm_transaction(result.value)
                if conf.value:
                    balance = await get_balance(client, pubkey)
                    if balance > 0:
                        print(f"✅ Success! New balance: {balance} SOL")
                        return True
            except Exception as e:
                print(".", end="", flush=True)
            await asyncio.sleep(1)
        
        return False
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def main():
    print("🔥 Testing Minimal Airdrop")
    print("=========================")
    
    # Load wallet
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {str(e)}")
        return

    # Try endpoints
    endpoints = [
        kz.HELIUS_DEVNET_RPC_URL,
        "https://api.devnet.solana.com",
        "https://api.devnet.solana.com",  # Try public endpoint twice
    ]

    for endpoint in endpoints:
        print(f"\n🔄 Trying endpoint: {endpoint}")
        client = AsyncClient(endpoint)
        
        try:
            # Check initial balance
            balance = await get_balance(client, keypair.pubkey())
            print(f"Initial balance: {balance} SOL")

            if balance < 0.05:
                if await request_minimal_airdrop(client, keypair.pubkey()):
                    print("\n✅ Minimal airdrop successful!")
                    return True
            else:
                print(f"✅ Wallet already funded with {balance} SOL")
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
