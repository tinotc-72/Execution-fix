import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
import base58
from config import kz
from solders.instruction import Instruction, AccountMeta
from time import sleep

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PUMP_USER_STORAGE = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

# Add instruction helpers for Pump.fun program
def create_initialize_user_instruction(
    wallet: Pubkey,
    user_storage: Pubkey
) -> Instruction:
    """Create instruction to initialize user account"""
    return Instruction(
        program_id=PUMP_USER_STORAGE,
        accounts=[
            AccountMeta(pubkey=wallet, is_signer=True, is_writable=True),
            AccountMeta(pubkey=user_storage, is_signer=False, is_writable=True),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        ],
        data=bytes([1])  # Initialize instruction discriminator
    )

def create_test_instruction(wallet: Pubkey) -> Instruction:
    """Create a test instruction to diagnose program panic"""
    # Get the PDA for user storage
    user_storage, _ = Pubkey.find_program_address(
        [bytes(wallet), b"user"],
        PUMP_USER_STORAGE
    )
    
    return Instruction(
        program_id=PUMP_USER_STORAGE,
        accounts=[
            AccountMeta(pubkey=wallet, is_signer=True, is_writable=True),
            AccountMeta(pubkey=user_storage, is_signer=False, is_writable=True),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        ],
        data=bytes([2])  # Test instruction discriminator
    )

async def test_user_account_initialization():
    """Test and fix user account initialization"""
    try:
        # Initialize client
        client = AsyncClient(kz.HELIUS_RPC_URL)
        
        # Load wallet
        wallet_key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        keypair = Keypair.from_bytes(base58.b58decode(wallet_key))
        print(f"\n🔑 Using wallet: {keypair.pubkey()}")
        
        # Check balances
        balance = await client.get_balance(keypair.pubkey())
        print(f"💰 SOL Balance: {balance.value / 1e9} SOL")
        
        # Get the PDAs
        print("\n🔍 Checking Program Derived Accounts...")
        
        # User Storage Account (PDA)
        user_storage_seeds = [
            bytes(keypair.pubkey()),
            b"user"
        ]
        user_storage, bump = Pubkey.find_program_address(
            user_storage_seeds,
            PUMP_USER_STORAGE
        )
        print(f"📝 User Storage PDA: {user_storage}")
        
        # Check if account exists
        account = await client.get_account_info(user_storage)
        if not account.value:
            print("⚠️ User storage account does not exist. Creating...")
            
            # Create account instruction
            space = 1024  # Adjust size as needed
            rent = await client.get_minimum_balance_for_rent_exemption(space)
            
            create_storage_ix = create_account(
                CreateAccountParams(
                    from_pubkey=keypair.pubkey(),
                    to_pubkey=user_storage,
                    space=space,
                    lamports=rent.value,
                    owner=PUMP_USER_STORAGE
                )
            )
            
            # Add compute budget instructions
            compute_limit_ix = set_compute_unit_limit(200_000)
            compute_price_ix = set_compute_unit_price(1)
            
            # Build and send transaction
            recent_blockhash = await client.get_latest_blockhash()
            if not recent_blockhash.value:
                raise Exception("Failed to get recent blockhash")
                
            instructions = [
                compute_limit_ix,
                compute_price_ix,
                create_storage_ix
            ]
            
            tx = VersionedTransaction.populate(
                recent_blockhash.value.blockhash,
                instructions,
                keypair.pubkey()
            )
            tx.sign([keypair])
            
            print("🔄 Sending initialization transaction...")
            result = await client.send_transaction(tx)
            
            if result.value:
                print(f"✅ Account initialized! Signature: {result.value}")
            else:
                print("❌ Failed to initialize account")
        else:
            print("✅ User storage account already exists")
            
        # Now test the account
        print("\n🔍 Testing account accessibility...")
        account_data = await client.get_account_info(user_storage)
        print(f"Account size: {len(account_data.value.data) if account_data.value else 'Not found'}")
        print(f"Account owner: {account_data.value.owner if account_data.value else 'Not found'}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
async def test_program_panic():
    """Test and diagnose program panic"""
    try:
        client = AsyncClient(kz.HELIUS_RPC_URL)
        
        # Load wallet
        wallet_key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        keypair = Keypair.from_bytes(base58.b58decode(wallet_key))
        
        print("\n🔍 Testing program interaction to diagnose panic...")
        
        # Add proper compute budget
        compute_limit_ix = set_compute_unit_limit(400_000)  # Increased limit
        compute_price_ix = set_compute_unit_price(1)
        
        # Test basic interaction
        test_ix = create_test_instruction(keypair.pubkey())
        
        recent_blockhash = await client.get_latest_blockhash()
        if not recent_blockhash.value:
            raise Exception("Failed to get recent blockhash")
            
        instructions = [
            compute_limit_ix,
            compute_price_ix,
            test_ix
        ]
        
        tx = VersionedTransaction.populate(
            recent_blockhash.value.blockhash,
            instructions,
            keypair.pubkey()
        )
        tx.sign([keypair])
        
        print("🔄 Sending test transaction...")
        
        # Simulate first
        print("\n🔬 Simulating transaction...")
        sim_result = await client.simulate_transaction(tx)
        
        if sim_result.value.err:
            print(f"❌ Simulation failed: {sim_result.value.err}")
            print("\nLogs:")
            for log in sim_result.value.logs:
                print(log)
        else:
            print("✅ Simulation successful")
            
            # Send transaction
            result = await client.send_transaction(tx)
            if result.value:
                print(f"✅ Transaction successful! Signature: {result.value}")
            else:
                print("❌ Transaction failed")
                
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n🔧 Testing Account Initialization and Program Panic")
    print("=" * 50)
    
    print("\n1️⃣ Testing Account Initialization...")
    await test_user_account_initialization()
    
    print("\n2️⃣ Testing Program Panic...")
    await test_program_panic()

if __name__ == "__main__":
    asyncio.run(main())
