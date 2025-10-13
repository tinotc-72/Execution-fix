import asyncio
import traceback
from typing import Optional, Dict, List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import AccountMeta, Instruction
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
import base58
from config import kz

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PUMP_CORE = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

# Common tokens we'll trade
COMMON_TOKENS = [
    "So11111111111111111111111111111111111111112",  # Wrapped SOL
]

class AccountSetup:
    def __init__(self, keypair: Keypair):
        self.keypair = keypair
        self.client = AsyncClient(kz.HELIUS_RPC_URL)
        
    async def check_and_create_ata(self, token_mint: Pubkey) -> bool:
        """Check if ATA exists and create if needed"""
        try:
            # Find ATA address
            ata = Pubkey.find_program_address(
                [
                    bytes(self.keypair.pubkey()),
                    bytes(TOKEN_PROGRAM_ID),
                    bytes(token_mint)
                ],
                ASSOCIATED_TOKEN_PROGRAM_ID
            )[0]
            
            # Check if account exists
            info = await self.client.get_account_info(ata)
            if info.value:
                print(f"✅ ATA exists for {token_mint}")
                return True
                
            print(f"🔄 Creating ATA for {token_mint}...")
            
            # Create ATA instruction
            create_ata_ix = Instruction(
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
                    AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=self.keypair.pubkey(), is_signer=False, is_writable=False),
                    AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                ],
                data=bytes([])
            )
            
            # Add compute budget instructions
            compute_ix = set_compute_unit_limit(200_000)
            priority_ix = set_compute_unit_price(1000)
            
            # Build and send transaction
            success = await self.send_and_confirm_transaction(
                [compute_ix, priority_ix, create_ata_ix],
                f"Create ATA for {token_mint}"
            )
            
            if success:
                print(f"✅ Successfully created ATA for {token_mint}")
                return True
            else:
                print(f"❌ Failed to create ATA for {token_mint}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating ATA: {str(e)}")
            traceback.print_exc()
            return False
            
    async def check_and_create_user_account(self) -> bool:
        """Check if user account exists and create if needed"""
        try:
            # Get PDA for user account
            user_pda = Pubkey.find_program_address(
                [b"user-state", bytes(self.keypair.pubkey())],
                PUMP_CORE
            )[0]
            
            # Check if account exists
            info = await self.client.get_account_info(user_pda)
            if info.value:
                print("✅ User account exists")
                return True
                
            print("🔄 Creating user account...")
            
            # Create initialization instruction
            init_ix = Instruction(
                program_id=PUMP_CORE,
                accounts=[
                    AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
                    AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False)
                ],
                data=bytes([0])  # initialization instruction
            )
            
            # Add compute budget instructions
            compute_ix = set_compute_unit_limit(200_000)
            priority_ix = set_compute_unit_price(1000)
            
            # Build and send transaction
            success = await self.send_and_confirm_transaction(
                [compute_ix, priority_ix, init_ix],
                "Create user account"
            )
            
            if success:
                print("✅ Successfully created user account")
                return True
            else:
                print("❌ Failed to create user account")
                return False
                
        except Exception as e:
            print(f"❌ Error creating user account: {str(e)}")
            traceback.print_exc()
            return False
            
    async def send_and_confirm_transaction(
        self,
        instructions: List[Instruction],
        description: str
    ) -> bool:
        """Send and confirm a transaction with retries"""
        try:
            # Get recent blockhash
            blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create message
            msg = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=instructions,
                recent_blockhash=blockhash,
                address_lookup_table_accounts=[]
            )
            
            if not msg:
                raise Exception("Failed to compile message")
                
            # Create and sign transaction
            tx = VersionedTransaction.populate(msg, [])
            sig = self.keypair.sign_message(bytes(tx.message))
            tx = VersionedTransaction.populate(msg, [sig])
            
            print(f"📝 Sending {description} transaction...")
            result = await self.client.send_transaction(tx)
            
            if not result.value:
                return False
                
            print(f"Signature: {result.value}")
            
            # Wait for confirmation with retries
            retry_count = 0
            while retry_count < 30:
                try:
                    conf = await self.client.confirm_transaction(result.value)
                    if conf.value.err is None:
                        return True
                    else:
                        print(f"❌ Transaction error: {conf.value.err}")
                        return False
                except Exception as e:
                    print(f"⚠️ Confirmation attempt {retry_count + 1}: {str(e)}")
                    
                retry_count += 1
                await asyncio.sleep(1)
                
            return False
            
        except Exception as e:
            print(f"❌ Transaction error: {str(e)}")
            traceback.print_exc()
            return False
            
    async def initialize_all(self) -> bool:
        """Initialize all required accounts"""
        try:
            print("\n🚀 Initializing Trading Accounts")
            print("=" * 50)
            
            # Check wallet balance
            balance = await self.client.get_balance(self.keypair.pubkey())
            print(f"\n💰 Wallet balance: {balance.value / 1e9} SOL")
            
            if balance.value < 0.1 * 1e9:  # Less than 0.1 SOL
                print("⚠️ Warning: Low wallet balance")
            
            # Create ATAs for common tokens
            print("\n📝 Creating Associated Token Accounts...")
            for token in COMMON_TOKENS:
                token_mint = Pubkey.from_string(token)
                if not await self.check_and_create_ata(token_mint):
                    print(f"⚠️ Failed to setup ATA for {token}")
                    
            # Create user account
            print("\n📝 Setting up user account...")
            if not await self.check_and_create_user_account():
                print("⚠️ Failed to setup user account")
                return False
                
            print("\n✅ Account initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {str(e)}")
            traceback.print_exc()
            return False
        finally:
            await self.client.close()
            
async def main():
    """Initialize trading accounts"""
    try:
        # Load wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        keypair = Keypair.from_bytes(base58.b58decode(key))
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
        
        # Initialize accounts
        setup = AccountSetup(keypair)
        await setup.initialize_all()
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
