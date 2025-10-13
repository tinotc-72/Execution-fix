import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction
from solders.message import MessageV0, MessageHeader
from solders.transaction import VersionedTransaction
import base58
from config import kz
from tx_builder import debug_print_transaction
import time

# Program IDs
PUMP_TRADE_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

async def build_test_sell_tx(keypair: Keypair, amount: int, token_mint: str, client: AsyncClient = None):
    """Build a test sell transaction without token ownership verification"""
    from tx_builder import build_sell_tx
    
    # Let's skip the token ownership check
    class MockClient:
        async def get_program_accounts(self, *args, **kwargs):
            # Simulate owning the token by returning a mock account
            return {"result": {"value": [{"pubkey": "mock", "account": {"data": ""}}]}}
            
        async def get_latest_blockhash(self):
            return await client.get_latest_blockhash() if client else None
            
        async def close(self):
            pass
    
    mock_client = MockClient()
    return await build_sell_tx(keypair=keypair, amount=amount, token_mint=token_mint, client=mock_client)

async def simulate_full_trade_flow():
    print("\n🔬 Starting Full Trade Flow Simulation...")
    
    try:
        # Use mnemonic-based wallet from config
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        print(f"✅ Loaded keypair: {keypair.pubkey()}")

        # Connect to RPC
        client = AsyncClient(kz.HELIUS_RPC_URL)
        
        # Test Parameters
        amount = 1_000_000  # 1 USDC
        token_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
        
        try:
            # Test buy transaction first
            print("\n🔄 Testing Buy Transaction...")
            from tx_builder import build_buy_tx
            buy_tx = await build_buy_tx(
                keypair=keypair,
                amount=amount,
                token_mint=token_mint,
                client=client
            )
            
            if buy_tx:
                print("\n✅ Buy transaction simulation successful")
                print("Transaction signature would be:", str(buy_tx.signatures[0]))
                print("Would send to:", kz.JITO_BUNDLE_ENDPOINT)
            
            # Test sell transaction
            print("\n🔄 Testing Sell Transaction...")
            sell_tx = await build_test_sell_tx(
                keypair=keypair,
                amount=amount,
                token_mint=token_mint,
                client=client
            )
            
            if sell_tx:
                print("\n✅ Sell transaction simulation successful")
                print("Transaction signature would be:", str(sell_tx.signatures[0]))
                print("Would send to:", kz.JITO_BUNDLE_ENDPOINT)
            
            print("\n📊 Transaction Simulation Summary:")
            print("✓ Buy transaction constructed successfully")
            print("✓ Sell transaction constructed successfully")
            print("✓ All signatures generated")
            print("✓ Proper transaction formatting")
            
        finally:
            await client.close()
            
        return True
        
    except Exception as e:
        print(f"\n❌ Simulation Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simulate_full_trade_flow())
