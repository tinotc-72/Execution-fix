import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

async def try_airdrop(wallet: Pubkey) -> bool:
    """Try to get an airdrop from available devnet endpoints"""
    # Configure endpoints
    endpoints = [
        "https://api.devnet.solana.com",
        "https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    ]
    
    amount = 1_000_000_000  # 1 SOL
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    for endpoint in endpoints:
        client = None
        try:
            print(f"\nTrying airdrop from {endpoint}...")
            client = AsyncClient(endpoint, commitment=Confirmed)
            
            # Get initial balance
            initial_balance = await client.get_balance(wallet)
            print(f"Current balance: {initial_balance.value/1e9} SOL")
            
            # Request airdrop
            sig = await client.request_airdrop(wallet, amount)
            print(f"✅ Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            for _ in range(30):  # 30 second timeout
                try:
                    # Check balance first
                    new_balance = await client.get_balance(wallet)
                    if new_balance.value > initial_balance.value:
                        print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                        return True
                        
                    # Also check transaction status
                    status = await client.get_signature_statuses([sig.value])
                    if status and status.value and status.value[0]:
                        if hasattr(status.value[0], 'err') and status.value[0].err:
                            print(f"❌ Airdrop failed: {status.value[0].err}")
                            break
                        if status.value[0].confirmation_status in ['confirmed', 'finalized']:
                            print(f"✅ Airdrop {status.value[0].confirmation_status}")
                            return True
                except Exception as e:
                    print(f"⚠️ Error checking status: {str(e)}")
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
        finally:
            if client:
                await client.close()
    
    print("\n❌ All airdrop attempts failed")
    return False

async def main():
    # Create test wallet
    wallet = Keypair()
    print(f"🔑 Test wallet created: {wallet.pubkey()}")
    
    # Try to get airdrop
    success = await try_airdrop(wallet.pubkey())
    if success:
        print("\n✅ Airdrop test completed successfully!")
    else:
        print("\n❌ Airdrop test failed!")

if __name__ == "__main__":
    asyncio.run(main())
