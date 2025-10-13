import asyncio
import traceback
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import AccountMeta, Instruction
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from config import kz
import base58
import time
from typing import List, Optional, Tuple

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PUMP_CORE = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

class AccountSetup:
    def __init__(self, rpc_url: str = kz.HELIUS_RPC_URL):
        self.client = AsyncClient(rpc_url)
        self.keypair = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    async def load_wallet(self, private_key: str) -> None:
        """Load wallet from private key"""
        try:
            decoded_key = base58.b58decode(private_key.strip())
            self.keypair = Keypair.from_bytes(decoded_key)
            print(f"✅ Loaded wallet: {self.keypair.pubkey()}")
        except Exception as e:
            print(f"❌ Failed to load wallet: {str(e)}")
            raise

    async def check_balance(self, required_sol: float = 0.1) -> bool:
        """Check if wallet has sufficient balance"""
        try:
            balance = await self.client.get_balance(self.keypair.pubkey())
            sol_balance = balance.value / 1e9
            print(f"💰 Current balance: {sol_balance} SOL")
            
            if sol_balance < required_sol:
                print(f"❌ Insufficient balance. Need {required_sol} SOL")
                return False
            return True
        except Exception as e:
            print(f"❌ Failed to check balance: {str(e)}")
            return False

    async def create_and_verify_ata(self, token_mint: str) -> Optional[Pubkey]:
        """Create and verify Associated Token Account"""
        try:
            mint_pubkey = Pubkey.from_string(token_mint)
            ata = await self._find_ata(mint_pubkey)
            
            # Check if ATA exists
            if await self._check_account(ata, "Token Account"):
                return ata
                
            print("\n📝 Creating Associated Token Account...")
            tx = await self._build_ata_transaction(mint_pubkey)
            
            if await self._send_and_confirm_tx(tx, "ATA Creation"):
                await asyncio.sleep(1)
                if await self._check_account(ata, "New Token Account"):
                    return ata
            
            return None
        except Exception as e:
            print(f"❌ ATA creation failed: {str(e)}")
            return None

    async def create_and_verify_pda(self) -> Optional[Pubkey]:
        """Create and verify Program Derived Account"""
        try:
            pda, bump = self._find_pda()
            
            # Check if PDA exists
            if await self._check_account(pda, "Program Account"):
                return pda
                
            print("\n📝 Creating Program Account...")
            tx = await self._build_pda_transaction(pda, bump)
            
            if await self._send_and_confirm_tx(tx, "PDA Creation"):
                await asyncio.sleep(2)
                if await self._check_account(pda, "New Program Account"):
                    return pda
            
            return None
        except Exception as e:
            print(f"❌ PDA creation failed: {str(e)}")
            return None

    async def _find_ata(self, mint: Pubkey) -> Pubkey:
        """Find Associated Token Account address"""
        return Pubkey.find_program_address(
            [bytes(self.keypair.pubkey()), bytes(TOKEN_PROGRAM_ID), bytes(mint)],
            ASSOCIATED_TOKEN_PROGRAM_ID
        )[0]

    def _find_pda(self) -> Tuple[Pubkey, int]:
        """Find Program Derived Account address"""
        return Pubkey.find_program_address(
            [b"user-state", bytes(self.keypair.pubkey())],
            PUMP_CORE
        )

    async def _check_account(self, pubkey: Pubkey, label: str) -> bool:
        """Check if account exists"""
        try:
            info = await self.client.get_account_info(pubkey)
            if info.value:
                print(f"✅ {label} exists")
                print(f"   Owner: {info.value.owner}")
                print(f"   Data length: {len(info.value.data)}")
                return True
            print(f"ℹ️ {label} does not exist")
            return False
        except Exception as e:
            print(f"❌ Error checking {label}: {str(e)}")
            return False

    async def _build_ata_transaction(self, mint: Pubkey) -> VersionedTransaction:
        """Build ATA creation transaction"""
        ata = await self._find_ata(mint)
        
        accounts = [
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False)
        ]
        
        create_ata_ix = Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=accounts,
            data=bytes([])
        )
        
        return await self._build_transaction([
            set_compute_unit_limit(400_000),
            set_compute_unit_price(1000),
            create_ata_ix
        ])

    async def _build_pda_transaction(self, pda: Pubkey, bump: int) -> VersionedTransaction:
        """Build PDA creation transaction"""
        accounts = [
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False)
        ]
        
        init_ix = Instruction(
            program_id=PUMP_CORE,
            accounts=accounts,
            data=bytes([0]) + (1024).to_bytes(4, 'little') + bytes([bump])
        )
        
        return await self._build_transaction([
            set_compute_unit_limit(400_000),
            set_compute_unit_price(1000),
            init_ix
        ])

    async def _build_transaction(self, instructions: List[Instruction]) -> VersionedTransaction:
        """Build and sign a transaction"""
        try:
            blockhash = await self._get_latest_blockhash()
            
            message = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=instructions,
                recent_blockhash=blockhash,
                address_lookup_table_accounts=[]
            )
            
            if not message:
                raise Exception("Failed to compile message")
                
            tx = VersionedTransaction.populate(message, [])
            sig = self.keypair.sign_message(bytes(tx.message))
            return VersionedTransaction.populate(message, [sig])
            
        except Exception as e:
            print(f"❌ Transaction build failed: {str(e)}")
            raise

    async def _get_latest_blockhash(self):
        """Get latest blockhash with retry"""
        for _ in range(3):
            try:
                return (await self.client.get_latest_blockhash()).value.blockhash
            except Exception as e:
                print(f"⚠️ Blockhash fetch failed: {str(e)}")
                await asyncio.sleep(1)
        raise Exception("Failed to get blockhash after retries")

    async def _send_and_confirm_tx(self, tx: VersionedTransaction, label: str) -> bool:
        """Send and confirm transaction with robust retry logic"""
        try:
            print(f"📡 Sending {label} transaction...")
            result = await self.client.send_raw_transaction(
                bytes(tx),
                skip_preflight=True,
                max_retries=3
            )
            
            if not result.value:
                print(f"❌ Failed to send transaction")
                return False
                
            print(f"✅ Transaction sent: {result.value}")
            
            # Monitor confirmation
            for i in range(30):  # 30 second timeout
                try:
                    status = await self.client.get_signature_statuses([result.value])
                    if status.value[0]:
                        if status.value[0].err:
                            print(f"❌ Transaction failed: {status.value[0].err}")
                            return False
                        if status.value[0].confirmation_status in ["confirmed", "finalized"]:
                            print(f"✅ Transaction confirmed!")
                            return True
                except Exception as e:
                    print(f"⚠️ Status check error: {str(e)}")
                
                if i % 5 == 0:
                    print(f"⏳ Waiting for confirmation... ({i}/30s)")
                await asyncio.sleep(1)
                
            print("❌ Transaction confirmation timeout")
            return False
            
        except Exception as e:
            print(f"❌ Transaction failed: {str(e)}")
            return False

async def setup_trading_accounts():
    """Main setup function"""
    print("\n🔧 Setting up Trading Accounts")
    print("=" * 50)
    
    try:
        async with AccountSetup() as setup:
            # Load wallet
            await setup.load_wallet(kz.BULLX_NEO_PRIVATE_KEY_QM)
            
            # Check balance
            if not await setup.check_balance(0.1):
                return
            
            # Create USDC ATA (common trading token)
            usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            ata = await setup.create_and_verify_ata(usdc_mint)
            if not ata:
                print("❌ Failed to setup token account")
                return
                
            # Create program PDA
            pda = await setup.create_and_verify_pda()
            if not pda:
                print("❌ Failed to setup program account")
                return
                
            print("\n✅ Account setup complete!")
            print(f"Token Account: {ata}")
            print(f"Program Account: {pda}")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_trading_accounts())
