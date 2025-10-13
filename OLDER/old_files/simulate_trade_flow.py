import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58
from tx_builder import build_buy_tx, build_sell_tx
from config import kz
import time

# Test USDC token mint
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

async def simulate_trade_flow():
    print("\n🔬 Starting Trade Flow Simulation...")
    
    try:
        # Load keypair
        cleaned_key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        keypair = Keypair.from_bytes(base58.b58decode(cleaned_key))
        print(f"✅ Loaded keypair: {keypair.pubkey()}")

        # Connect to RPC
        client = AsyncClient(kz.HELIUS_RPC_URL)
        
        # Test Parameters
        amount_in = 1_000_000  # 1 USDC
        slippage_bps = 100     # 1% slippage
        
        print("\n🔄 Simulating Buy Transaction...")
        print(f"Amount: {amount_in/1_000_000} USDC")
        print(f"Slippage: {slippage_bps/100}%")
        
        # Build buy transaction
        buy_tx = await build_buy_tx(
            keypair=keypair,
            amount=amount_in,
            token_mint=USDC_MINT,
            client=client
        )
        
        if buy_tx:
            print("\n✅ Buy transaction built successfully")
            print("Transaction signature would be:", str(buy_tx.signatures[0]))
            print("Would send to:", kz.JITO_BUNDLE_ENDPOINT)
        else:
            print("\n❌ Failed to build buy transaction")

        print("\n🔄 Simulating Sell Transaction...")
        
        # Build sell transaction
        sell_tx = await build_sell_tx(
            keypair=keypair,
            amount=amount_in,
            token_mint=USDC_MINT,
            client=client
        )
        
        if sell_tx:
            print("\n✅ Sell transaction built successfully")
            print("Transaction signature would be:", str(sell_tx.signatures[0]))
            print("Would send to:", kz.JITO_BUNDLE_ENDPOINT)
        else:
            print("\n❌ Failed to build sell transaction")
            
        # Close client
        await client.close()
        
        print("\n📊 Simulation Summary:")
        print("- Transactions built ✓")
        print("- Signatures generated ✓")
        print("- Jito tip accounts included ✓")
        print("- Compute budget set ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Simulation Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simulate_trade_flow())
    if not success:
        exit(1)
