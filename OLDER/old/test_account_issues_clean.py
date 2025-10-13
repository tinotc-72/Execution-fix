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
from solana.rpc.commitment import Confirmed
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.exceptions import SolanaRpcException
from base64 import b64encode
from config import kz
import base58
import time
import json
from typing import List, Optional

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PUMP_CORE = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_ROUTER = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")

# Test token (using Devnet USDC)
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC address

# RPC Configuration
RPC_ENDPOINTS = [
    "https://valry-c5zjvr-fast-devnet.helius-rpc.com",  # Helius Secure RPC (primary)
    "https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",  # Helius Standard RPC
    "https://eclipse.helius-rpc.com/",  # Helius Shared Eclipse
    "https://api.devnet.solana.com"  # Public devnet fallback
]

# Websocket endpoint for live updates if needed
WS_ENDPOINT = "wss://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"

# API endpoints for transaction parsing
HELIUS_TX_PARSE_URL = "https://api-devnet.helius-rpc.com/v0/transactions/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
HELIUS_TX_HISTORY_URL = "https://api-devnet.helius-rpc.com/v0/addresses/{address}/transactions/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"

async def get_best_rpc_client() -> AsyncClient:
    """Get the fastest responding RPC endpoint"""
    best_latency = float('inf')
    best_client = None
    best_endpoint = None
    
    for endpoint in RPC_ENDPOINTS:
        try:
            client = AsyncClient(endpoint, commitment=Confirmed)
            start = time.time()
            await client.get_latest_blockhash()
            latency = time.time() - start
            
            print(f"RPC {endpoint}: {latency:.2f}s")
            
            if latency < best_latency:
                if best_client:
                    await best_client.close()
                best_latency = latency
                best_endpoint = endpoint
                best_client = client
            else:
                await client.close()
                
        except Exception as e:
            print(f"Failed to connect to {endpoint}: {str(e)}")
            if client:
                await client.close()
                
    if best_endpoint:
        print(f"\n✅ Using fastest RPC ({best_endpoint}) with {best_latency:.2f}s latency")
        return AsyncClient(best_endpoint, commitment=Confirmed)
        
    print("\n⚠️ Falling back to default RPC")
    return AsyncClient(RPC_ENDPOINTS[0], commitment=Confirmed)

async def check_account_state(client: AsyncClient, pubkey: Pubkey, label: str = "Account", retries: int = 3) -> bool:
    """Check account state with retries"""
    for attempt in range(retries):
        try:
            print(f"\n🔍 Checking {label}...")
            info = await client.get_account_info(pubkey)
            if info.value:
                print(f"✅ {label} exists")
                print(f"Owner: {info.value.owner}")
                print(f"Lamports: {info.value.lamports}")
                print(f"Data length: {len(info.value.data)}")
                return True
            else:
                if attempt == retries - 1:
                    print(f"❌ {label} does not exist")
                return False
        except Exception as e:
            print(f"⚠️ Error checking {label} (attempt {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(1)
    return False

async def try_airdrop(wallet: Pubkey, amount: int = 100_000_000) -> bool:
    """Try to get an airdrop from any available devnet endpoint"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    # For airdrop, we'll try public devnet first as it's most reliable
    try_endpoints = [
        "https://api.devnet.solana.com",
        "https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    ]
    
    for endpoint in try_endpoints:
        client = None
        try:
            print(f"\nTrying airdrop from {endpoint}...")
            client = AsyncClient(endpoint, commitment=Confirmed, timeout=30)
            
            # Get initial balance
            initial_balance = await client.get_balance(wallet)
            print(f"Current balance: {initial_balance.value/1e9} SOL")
            
            # Request airdrop
            sig = await client.request_airdrop(wallet, amount)
            if not sig or not sig.value:
                print(f"❌ Airdrop request failed on {endpoint}")
                continue
                
            print(f"✅ Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            for _ in range(30):  # 30 second timeout
                try:
                    # Check balance first as it's most reliable
                    new_balance = await client.get_balance(wallet)
                    if new_balance.value > initial_balance.value:
                        print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                        return True
                        
                    # Check transaction status as backup
                    status = await client.get_signature_statuses([sig.value])
                    if status and status.value and status.value[0]:
                        if hasattr(status.value[0], 'err') and status.value[0].err:
                            print(f"❌ Airdrop failed with error: {status.value[0].err}")
                            break
                        if status.value[0].confirmation_status in ['confirmed', 'finalized']:
                            print(f"✅ Airdrop {status.value[0].confirmation_status}")
                            return True
                            
                except Exception as e:
                    print(f"⚠️ Error checking status: {str(e)}")
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
        finally:
            if client:
                await client.close()
    
    print("❌ All airdrop attempts failed")
    return False
    
    for endpoint in endpoints:
        client = None
        try:
            print(f"\nTrying airdrop from {endpoint}...")
            client = AsyncClient(
                endpoint,
                commitment=Confirmed,
                timeout=30
            )
            
            # Get initial balance
            initial_balance = await client.get_balance(wallet)
            print(f"Current balance: {initial_balance.value/1e9} SOL")
            
            # Request airdrop
            sig = await client.request_airdrop(wallet, amount)
            if not sig or not sig.value:
                print(f"❌ Airdrop request failed on {endpoint}")
                if client:
                    await client.close()
                continue
                
            print(f"✅ Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            for _ in range(30):  # 30 second timeout
                try:
                    # Check balance first as it's most reliable
                    new_balance = await client.get_balance(wallet)
                    if new_balance.value > initial_balance.value:
                        print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                        if client:
                            await client.close()
                        return True
                        
                    # Check transaction status
                    status = await client.get_signature_statuses([sig.value])
                    if status.value[0]:
                        if hasattr(status.value[0], 'err') and status.value[0].err:
                            print(f"❌ Airdrop failed with error: {status.value[0].err}")
                            break
                        if status.value[0].confirmation_status in ['confirmed', 'finalized']:
                            print(f"✅ Airdrop {status.value[0].confirmation_status}")
                            if client:
                                await client.close()
                            return True
                except Exception as e:
                    print(f"⚠️ Error checking status: {str(e)}")
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
            if client:
                await client.close()
            continue
            
    print("❌ All airdrop attempts failed")
    return False
                
            print(f"✅ Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            for _ in range(30):  # 30 second timeout
                try:
                    # First try get_signature_statuses
                    status = await client.get_signature_statuses([sig.value])
                    if status.value[0] is not None:
                        if hasattr(status.value[0], 'err') and status.value[0].err:
                            print(f"❌ Airdrop failed: {status.value[0].err}")
                            break
                        if status.value[0].confirmation_status in ["confirmed", "finalized"]:
                            print(f"✅ Airdrop confirmed!")
                            # Verify balance increase
                            new_balance = await client.get_balance(wallet)
                            if new_balance.value >= amount:
                                print(f"✅ New balance: {new_balance.value/1e9} SOL")
                                await client.close()
                                return True
                            
                    # Fallback to get_transaction
                    tx = await client.get_transaction(sig.value)
                    if tx.value is not None:
                        if hasattr(tx.value, 'meta') and tx.value.meta and hasattr(tx.value.meta, 'err') and tx.value.meta.err:
                            print(f"❌ Airdrop failed: {tx.value.meta.err}")
                            break
                        # If we got here and can verify the balance, consider it a success
                        new_balance = await client.get_balance(wallet)
                        if new_balance.value >= amount:
                            print(f"✅ Airdrop confirmed via transaction! New balance: {new_balance.value/1e9} SOL")
                            await client.close()
                            return True
                        
                except Exception as e:
                    print(f"⚠️ Error checking status: {str(e)}")
                    
                await asyncio.sleep(1)
                
            await client.close()
            
        except Exception as e:
            print(f"❌ Error with {endpoint}: {str(e)}")
            continue
            
    print("❌ All airdrop attempts failed")
    return False

async def get_minimum_balance_for_rent_exemption(client: AsyncClient, data_size: int) -> int:
    """Get the minimum balance required for rent exemption"""
    resp = await client.get_minimum_balance_for_rent_exemption(data_size)
    return resp.value

async def build_optimized_transaction(
    client: AsyncClient,
    wallet: Keypair,
    instructions: List[Instruction],
    priority_fee_microlamports: int = 10000  # Default priority fee (adjust based on network conditions)
) -> VersionedTransaction:
    """Build a transaction with optimized compute budget and priority fees"""
    
    try:
        # Add compute budget instructions at the start
        budget_instructions = [
            set_compute_unit_limit(150000),  # Conservative default, adjust based on instruction complexity
            set_compute_unit_price(priority_fee_microlamports)
        ]
        
        all_instructions = budget_instructions + instructions
        
        # Get recent blockhash
        blockhash_resp = await client.get_latest_blockhash(Confirmed)
        recent_blockhash = blockhash_resp.value.blockhash
        
        # Create versioned transaction with all instructions
        msg = MessageV0.try_compile(
            payer=wallet.pubkey(),
            instructions=all_instructions,
            recent_blockhash=recent_blockhash,
            address_lookup_table_accounts=[]
        )
        
        if not msg:
            raise Exception("Failed to compile transaction message")
            
        # Create and sign transaction
        tx = VersionedTransaction(msg, [])
        sig = wallet.sign_message(bytes(msg))
        tx.signatures.append(sig)
        
        return tx
        
    except Exception as e:
        print(f"Error building optimized transaction: {str(e)}")
        traceback.print_exc()
        raise

async def create_token_account(
    client: AsyncClient,
    payer: Keypair,
    mint: Pubkey,
    owner: Pubkey,
    is_native: bool = False
) -> tuple[Pubkey, List[Instruction]]:
    """Create an Associated Token Account with proper rent and initialization"""
    
    try:
        # Derive the ATA address
        ata_seeds = [
            bytes(owner),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        ata_address, bump = await find_program_address(ata_seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
        
        print(f"\n🏦 Creating token account for mint: {mint}")
        print(f"Owner: {owner}")
        print(f"ATA address: {ata_address}")
        
        # Check if account already exists
        account_info = await client.get_account_info(ata_address)
        if account_info.value is not None:
            print("✅ Token account already exists")
            return ata_address, []
            
        # Calculate minimum rent
        data_size = 165  # Standard token account size
        rent = await get_minimum_balance_for_rent_exemption(client, data_size)
        
        # Build create account instruction
        create_account_ix = Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=ata_address, is_signer=False, is_writable=True),
                AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
            ],
            data=b"" # Associated token program needs no additional data
        )
        
        return ata_address, [create_account_ix]
        
    except Exception as e:
        print(f"Error creating token account: {str(e)}")
        traceback.print_exc()
        raise

async def create_pda_account(
    client: AsyncClient,
    payer: Keypair,
    space: int,
    program_id: Pubkey,
    seeds: List[bytes]
) -> tuple[Pubkey, List[Instruction]]:
    """Create a PDA account with proper rent and initialization"""
    
    try:
        # Find PDA address with canonical bump
        pda_address, bump = await find_program_address(seeds, program_id)
        
        print(f"\n🏗️ Creating PDA account")
        print(f"Program ID: {program_id}")
        print(f"PDA address: {pda_address}")
        print(f"Canonical bump: {bump}")
        
        # Check if account already exists
        account_info = await client.get_account_info(pda_address)
        if account_info.value is not None:
            print("✅ PDA account already exists")
            return pda_address, []
            
        # Calculate rent
        rent = await get_minimum_balance_for_rent_exemption(client, space)
        
        # Create account instruction
        create_pda_ix = Instruction(
            program_id=SYS_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=pda_address, is_signer=False, is_writable=True),
            ],
            data=b"" # System program create account instruction data
        )
        
        return pda_address, [create_pda_ix]
        
    except Exception as e:
        print(f"Error creating PDA account: {str(e)}")
        traceback.print_exc()
        raise

async def find_program_address(seeds: List[bytes], program_id: Pubkey) -> tuple[Pubkey, int]:
    """Find a valid program address and bump seed"""
    bump = 255
    while bump >= 0:
        try:
            seeds_with_bump = seeds + [bytes([bump])]
            address = Pubkey.create_program_address(seeds_with_bump, program_id)
            return address, bump
        except Exception:
            bump -= 1
    raise Exception("Unable to find a valid program address")

async def send_and_confirm_transaction(client: AsyncClient, tx: VersionedTransaction, max_retries: int = 3) -> bool:
    """Send and confirm a transaction with improved reliability"""
    print("\n📡 Sending transaction...")
    
    for attempt in range(max_retries):
        try:
            # Send transaction
            result = await client.send_transaction(tx, opts=TxOpts(skip_preflight=True, preflight_commitment=Confirmed))
            
            if not result.value:
                print(f"❌ Failed to send transaction (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                continue
            
            signature = result.value
            print(f"✅ Transaction sent: {signature}")
            
            # Wait for confirmation with timeout
            for i in range(30):  # 30 second timeout
                try:
                    # Try get_transaction first
                    tx_resp = await client.get_transaction(signature, commitment=Confirmed)
                    if tx_resp and tx_resp.value:
                        if tx_resp.value.err:
                            error_msg = str(tx_resp.value.err)
                            print(f"❌ Transaction failed: {error_msg}")
                            if "AccountInUse" in error_msg and attempt < max_retries - 1:
                                print("⚠️ Account in use, retrying...")
                                break
                            return False
                        print("✅ Transaction confirmed!")
                        return True
                    
                    # Fallback to signature status
                    sig_resp = await client.get_signature_statuses([signature])
                    if sig_resp.value[0]:
                        if sig_resp.value[0].err:
                            print(f"❌ Transaction failed: {sig_resp.value[0].err}")
                            return False
                        if sig_resp.value[0].confirmation_status in ["confirmed", "finalized"]:
                            print(f"✅ Transaction {sig_resp.value[0].confirmation_status}!")
                            return True
                            
                except Exception as e:
                    print(f"⚠️ Error checking status: {str(e)}")
                    
                if i % 5 == 0:  # Status update every 5 seconds
                    print(f"⏳ Waiting for confirmation ({i}/30s)")
                await asyncio.sleep(1)
                
            print("⚠️ Transaction not confirmed, retrying...")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if attempt < max_retries - 1:
                print("🔄 Retrying...")
                await asyncio.sleep(2)
            
    print("❌ All attempts failed")
    return False

async def test_account_initialization():
    """Test account initialization with improved error handling"""
    client = None
    try:
        print("\n🔬 Testing Account Initialization")
        print("=" * 50)
        
        # Get the best RPC client
        client = await get_best_rpc_client()
        
        print("\n🔑 Setting up wallet...")
        wallet = Keypair()  # Generate new test wallet
        print(f"Wallet: {wallet.pubkey()}")
        
        # Test USDC mint for token accounts
        usdc_mint = Pubkey.from_string(TEST_TOKEN)
        
        # Check and fund wallet if needed
        print("\n💰 Checking wallet balance...")
        balance = await client.get_balance(wallet.pubkey())
        print(f"Initial balance: {balance.value/1e9} SOL")
        
        if balance.value < 1_000_000_000:  # Need at least 1 SOL
            print("Need airdrop...")
            if not await try_airdrop(wallet.pubkey(), 1_000_000_000):  # Request 1 SOL
                print("❌ Could not fund test wallet")
                return
                
            # Verify new balance
            await asyncio.sleep(2)  # Wait for confirmation
            balance = await client.get_balance(wallet.pubkey())
            print(f"✅ New wallet balance: {balance.value/1e9} SOL")
            
        # Create Associated Token Account
        print("\n📝 Creating Associated Token Account...")
        ata_address, ata_ix = await create_token_account(
            client,
            wallet,
            usdc_mint,
            wallet.pubkey()
        )
        
        if ata_ix:  # Only create if doesn't exist
            # Build and send ATA creation transaction
            tx = await build_optimized_transaction(
                client,
                wallet,
                ata_ix,
                priority_fee_microlamports=10000
            )
            
            if await send_and_confirm_transaction(client, tx):
                print("✅ ATA created successfully!")
            else:
                print("❌ Failed to create ATA")
                return
                
        # Create PDA for program state
        print("\n📝 Creating Program PDA...")
        seeds = [b"state", bytes(wallet.pubkey())]
        pda_address, pda_ix = await create_pda_account(
            client,
            wallet,
            space=1000,  # Adjust based on your data needs
            program_id=PUMP_CORE,
            seeds=seeds
        )
        
        if pda_ix:  # Only create if doesn't exist
            # Build and send PDA creation transaction  
            tx = await build_optimized_transaction(
                client,
                wallet,
                pda_ix,
                priority_fee_microlamports=15000  # Higher priority for PDAs
            )
            
            if await send_and_confirm_transaction(client, tx):
                print("✅ PDA created successfully!")
            else:
                print("❌ Failed to create PDA")
                return
                
        # Verify account states        
        print("\n🔍 Verifying created accounts...")
        await check_account_state(client, ata_address, "Associated Token Account")
        await check_account_state(client, pda_address, "Program PDA")
            
        print("\n✅ Account initialization tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()
    finally:
        if client:
            await client.close()

async def run_tests():
    """Run all account initialization tests"""
    try:
        await test_account_initialization()
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        traceback.print_exc()

def main():
    """Main entry point"""
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()
