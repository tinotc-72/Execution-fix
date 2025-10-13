"""
Minimal transaction builder using only solders for PUMP trades.
Uses exact instruction data and account order from mainnet.
"""

import base64
import logging
import traceback
from typing import Optional, List
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import AccountMeta, Instruction
from solders.hash import Hash
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Token Program Constants
TOKEN_PROGRAM_KEY = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM_KEY = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

# PUMP Router Constants from mainnet
PUMP_TRADE_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_ROUTER_STATE = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_ACCOUNT = Pubkey.from_string("62qc2CNXwrYqQScmEdiZFFAnJR262PxWEuNQtxfafNgV")
PUMP_VAULT_AUTHORITY = Pubkey.from_string("893s38tuZ4gFF8yYvLRKiyPVsw7ZpwN8H6wBPeHvgHLP")
PUMP_TOKEN_VAULT = Pubkey.from_string("GM8KAofy5rJ5FJooNQUNPZRUkpeEkpfVXxgQa9AC4H3i")

# Test token (BONK)
BONK_MINT = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

# Instruction data from successful mainnet transaction
PUMP_BUY_IX_DATA = base64.b64decode("57rQahYVzDKpAxTmJ5dZtsfoPzp1AVfuxRq6b2wUaxxGACKqxoXxeNI=")
import struct
import hashlib
import traceback
import json
from typing import List, Tuple, Optional, Dict, Any
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID, transfer, TransferParams
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.transaction import VersionedTransaction
from solders.message import MessageV0

# Program IDs
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ATA_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
NATIVE_MINT = "So11111111111111111111111111111111111111112"
METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"

# PUMP router and program IDs
PUMP_ROUTER = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"  # Production PUMP router
PUMP_TRADE_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"   # PUMP trade program

# Convert all program IDs to Pubkey objects
NATIVE_MINT_KEY = Pubkey.from_string(NATIVE_MINT)
TOKEN_PROGRAM_KEY = Pubkey.from_string(TOKEN_PROGRAM_ID)
ATA_PROGRAM_KEY = Pubkey.from_string(ATA_PROGRAM_ID)
METADATA_PROGRAM_KEY = Pubkey.from_string(METADATA_PROGRAM_ID)
PUMP_ROUTER_KEY = PUMP_ROUTER  # Production PUMP router (entry point)
PUMP_TRADE_KEY = Pubkey.from_string(PUMP_TRADE_PROGRAM)

def find_program_address(seeds: List[bytes], program_id: Pubkey) -> Tuple[Pubkey, int]:
    """Find a program derived address"""
    # Start with bump seed 255 and work down
    for bump in range(255, -1, -1):
        try:
            # Pass list of seeds directly to create_program_address
            all_seeds = seeds + [bytes([bump])]
            address = Pubkey.create_program_address(all_seeds, program_id)
            return address, bump
        except Exception as e:
            continue
    raise ValueError("Unable to find viable program address")

def get_associated_token_address(wallet_address: Pubkey, token_mint_address: Pubkey) -> Pubkey:
    """Find the associated token account address using the official derivation"""
    if isinstance(token_mint_address, str):
        token_mint_address = Pubkey.from_string(token_mint_address)
    if isinstance(wallet_address, str):
        wallet_address = Pubkey.from_string(wallet_address)

    seeds = [
        bytes(wallet_address),
        bytes(TOKEN_PROGRAM_KEY),
        bytes(token_mint_address)
    ]

    # Official SPL Token ATA derivation
    program_address = Pubkey.find_program_address(
        seeds,
        ATA_PROGRAM_KEY
    )
    return program_address[0]

def create_associated_token_account(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey
) -> Instruction:
    """Create an instruction to create an Associated Token Account"""
    if isinstance(mint, str):
        mint = Pubkey.from_string(mint)
    if isinstance(payer, str):
        payer = Pubkey.from_string(payer)
    if isinstance(owner, str):
        owner = Pubkey.from_string(owner)

    ata = get_associated_token_address(owner, mint)
    
    accounts = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ATA_PROGRAM_KEY, is_signer=False, is_writable=False),
    ]
    
    return Instruction(
        program_id=ATA_PROGRAM_KEY,
        accounts=accounts,
        data=bytes([])  # Empty data for create instruction
    )

async def check_ata_exists(owner: Pubkey, mint: Pubkey) -> bool:
    """Check if an Associated Token Account exists"""
    if isinstance(mint, str):
        mint = Pubkey.from_string(mint)
    if isinstance(owner, str):
        owner = Pubkey.from_string(owner)

    # TODO: Implement actual check, for now assume we need to create it
    return False

def create_compute_budget_instructions(
    unit_limit: int = 1_400_000,
    unit_price: int = 100
) -> List[Instruction]:
    """Create compute budget instructions."""
    return [
        set_compute_unit_limit(unit_limit),
        set_compute_unit_price(unit_price)
    ]

def get_user_pda(owner: Pubkey) -> Pubkey:
    """Get the PDA for a user's state account"""
    pda, bump = find_program_address([b"user-state", bytes(owner)], PUMP_TRADE_KEY)
    print(f"\n👤 User PDA:")
    print(f"Owner: {owner}")
    print(f"PDA: {pda}")
    print(f"Bump seed: {bump}")
    print(f"Seeds: user-state + {owner}")
    return pda

def create_user_init_instruction(owner: Pubkey) -> Instruction:
    """Create an instruction to initialize a user's account in the PUMP trade program"""
    user_pda = get_user_pda(owner)
    
    accounts = [
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),
        AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    return Instruction(
        program_id=PUMP_TRADE_KEY,  # Always create user account in trade program
        accounts=accounts,
        data=bytes([0])  # Initialize instruction
    )

def create_associated_token_account_idempotent(payer: Pubkey, wallet: Pubkey, mint: Pubkey) -> Instruction:
    """Create an idempotent instruction to create the ATA if it doesn't exist"""
    ata = get_associated_token_address(wallet, mint)
    
    accounts = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),  # Payer
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),   # ATA to create
        AccountMeta(pubkey=wallet, is_signer=False, is_writable=False), # Wallet to own ATA
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # System program
        AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),  # Token program
        AccountMeta(pubkey=ATA_PROGRAM_KEY, is_signer=False, is_writable=False),  # ATA program
    ]
    
    return Instruction(
        program_id=ATA_PROGRAM_KEY,  # ATA program
        accounts=accounts,
        data=bytes([1])  # CreateIdempotent instruction
    )

def create_sync_native_instruction(wsol_account: Pubkey) -> Instruction:
    """Create sync native instruction for WSOL account"""
    accounts = [
        AccountMeta(pubkey=wsol_account, is_signer=False, is_writable=True),   # WSOL account
    ]
    
    # SyncNative instruction = 17
    return Instruction(
        program_id=TOKEN_PROGRAM_KEY,  # Token program
        accounts=accounts,
        data=bytes([17])
    )

def create_buy_instruction(
        owner: Pubkey, 
        token: Pubkey,
        amount: int, 
        slippage_bps: int,
        wsol_ata: Pubkey,
        token_ata: Pubkey,
        pump_wsol_vault: Pubkey,
        pump_token_vault: Pubkey,
        user_pda: Pubkey,
        metadata_key: Pubkey = None
    ) -> Instruction:
    """Create a buy instruction for the PUMP router"""
    print("\n🛠️ Building buy instruction:")

    # Create instruction data with correct Anchor discriminator
    # - 8 bytes discriminator for initialize_curve_and_buy
    # - 32 bytes token mint
    # - 8 bytes amount in lamports
    discriminator = bytes.fromhex("adf0bdc6df9c34d1")  # initialize_curve_and_buy
    instruction_data = (
        discriminator +                     # 8 bytes: Anchor discriminator
        bytes(token) +                      # 32 bytes: Token mint
        struct.pack("<Q", amount)           # 8 bytes: Amount (u64 little-endian)
    )
    
    print(f"\n📝 Instruction data:")
    print(f"Full hex: {instruction_data.hex()}")
    print(f"Discriminator: {discriminator.hex()}")
    print(f"Token mint: {bytes(token).hex()}")
    print(f"Amount: {struct.pack('<Q', amount).hex()}")
    
    # Account metas in exact order from successful trade
    print(f"\n📋 Building swap accounts:")
    accounts = [
        # Essential accounts only, in exact order
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),           # Wallet (signer)
        AccountMeta(pubkey=wsol_ata, is_writable=True, is_signer=False),      # WSOL ATA
        AccountMeta(pubkey=token_ata, is_writable=True, is_signer=False),     # Token ATA
        AccountMeta(pubkey=pump_wsol_vault, is_writable=True, is_signer=False), # WSOL vault
        AccountMeta(pubkey=pump_token_vault, is_writable=True, is_signer=False), # Token vault
        AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),      # User PDA
        AccountMeta(pubkey=token, is_writable=False, is_signer=False),         # Token mint
        AccountMeta(pubkey=NATIVE_MINT_KEY, is_writable=False, is_signer=False), # WSOL mint
        AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_writable=False, is_signer=False) # Token program
    ]
    
    return Instruction(
        program_id=PUMP_ROUTER_KEY,  # Production PUMP router
        accounts=accounts,
        data=instruction_data
    )

async def build_buy_tx(executor, token: Pubkey, amount: int, keypair: Keypair, slippage_bps: int = 3000):
    """Build a buy transaction for PUMP router using only solders"""
    try:
        print("\n🔍 Starting account derivation...")
        owner = keypair.pubkey()
        print(f"Owner: {owner}")
        
        # Get ATAs and check if they exist
        token_ata = get_associated_token_address(owner, token)
        wsol_ata = get_associated_token_address(owner, NATIVE_MINT_KEY)
        print(f"\n💳 Token ATAs:")
        print(f"Token ATA: {token_ata}")
        print(f"WSOL ATA: {wsol_ata}")
        
        # Get router's vaults
        pump_wsol_vault = get_associated_token_address(PUMP_ROUTER_KEY, NATIVE_MINT_KEY)  # Production router
        pump_token_vault = get_associated_token_address(PUMP_ROUTER_KEY, token)  # Production router
        print(f"\n🏦 PUMP Vaults:")
        print(f"WSOL Vault: {pump_wsol_vault}")
        print(f"Token Vault: {pump_token_vault}")
        print(f"Vault Owner: {PUMP_ROUTER_KEY} (Production router)")
        
        # Get token metadata and user PDA (these functions print debug info)
        metadata_key = get_metadata_address(token)
        user_pda = get_user_pda(owner)
        
        # Check if accounts exist
        token_ata_exists = await check_ata_exists(executor, token_ata)
        wsol_ata_exists = await check_ata_exists(executor, wsol_ata)
        user_account_exists = await executor.get_account_info(user_pda) is not None
        
        print(f"\n✅ Account existence:")
        print(f"Token ATA exists: {token_ata_exists}")
        print(f"WSOL ATA exists: {wsol_ata_exists}")
        print(f"User PDA exists: {user_account_exists}")
        
        # Start with compute budget instructions
        instructions = create_compute_budget_instructions()
        print(f"\n💰 Transaction budget:")
        print(f"Compute unit limit: 1,400,000")
        print(f"Compute unit price: 100")
        
        # Initialize user account if needed (always in PUMP_TRADE program)
        if not user_account_exists:
            print("\n🔧 Creating PUMP user account")
            init_ix = create_user_init_instruction(owner)
            instructions.append(init_ix)
        
        # Add ATA creation instructions if needed
        if not token_ata_exists or not wsol_ata_exists:
            print("\n🔧 Creating ATAs:")
            if not token_ata_exists:
                print(f"Token ATA: {token_ata}")
                create_token_ata_ix = create_associated_token_account_idempotent(
                    payer=owner,
                    wallet=owner,
                    mint=token
                )
                instructions.append(create_token_ata_ix)
            
            if not wsol_ata_exists:
                print(f"WSOL ATA: {wsol_ata}")
                create_wsol_ata_ix = create_associated_token_account_idempotent(
                    payer=owner,
                    wallet=owner,
                    mint=NATIVE_MINT_KEY
                )
                instructions.append(create_wsol_ata_ix)
            
        # Transfer SOL to user's WSOL ATA
        transfer_ix = transfer(TransferParams(
            from_pubkey=owner,
            to_pubkey=wsol_ata,  # Transfer to user's WSOL ATA
            lamports=amount
        ))
        print(f"\n💸 SOL Transfer:")
        print(f"From: {owner}")
        print(f"To: {wsol_ata}")
        print(f"Amount: {amount} lamports")
        
        # Create PUMP router buy instruction
        print("\n🔄 Creating PUMP router buy instruction")
        buy_ix = create_buy_instruction(
            owner=owner,
            token=token,
            amount=amount,
            slippage_bps=slippage_bps,
            wsol_ata=wsol_ata,
            token_ata=token_ata,
            pump_wsol_vault=pump_wsol_vault,
            pump_token_vault=pump_token_vault,
            user_pda=user_pda,
            metadata_key=metadata_key
        )
        
        # Add sync native instruction after transfer
        sync_native_ix = create_sync_native_instruction(wsol_ata)
        
        # Add transfer, sync, and swap instructions in order
        instructions.extend([transfer_ix, sync_native_ix, buy_ix])
        
        # Get blockhash
        blockhash = await executor.get_latest_blockhash()
        if not blockhash:
            print("Failed to get blockhash")
            return None
            
        print(f"\n🔐 Building transaction:")
        print(f"Recent blockhash: {blockhash}")
        print(f"Total instructions: {len(instructions)}")
        
        # Build and return transaction
        message = MessageV0.try_compile(
            payer=owner,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )
        
        print("\n✅ Transaction built successfully!")
        return VersionedTransaction(message, [keypair])
        
    except Exception as e:
        print(f"\n❌ Error building buy transaction: {e}")
        traceback.print_exc()
        return None

async def build_sell_tx(executor, token: Pubkey, token_amount: int, keypair: Keypair, slippage_bps: int = 3000):
    """Build a sell transaction for PUMP router using only solders"""
    try:
        print("\n🔍 Starting account derivation...")
        owner = keypair.pubkey()
        print(f"Owner: {owner}")
        
        # Get ATAs
        token_ata = get_associated_token_address(owner, token)
        wsol_ata = get_associated_token_address(owner, NATIVE_MINT_KEY)
        print(f"\n💳 Token ATAs:")
        print(f"Token ATA: {token_ata}")
        print(f"WSOL ATA: {wsol_ata}")
        
        # Get router's vaults
        pump_token_vault = get_associated_token_address(PUMP_ROUTER_KEY, token)
        pump_wsol_vault = get_associated_token_address(PUMP_ROUTER_KEY, NATIVE_MINT_KEY)
        print(f"\n🏦 PUMP Vaults:")
        print(f"Token Vault: {pump_token_vault}")
        print(f"WSOL Vault: {pump_wsol_vault}")
        print(f"Vault Owner: {PUMP_ROUTER_KEY} (Production router)")
        
        # Get token metadata and user PDA
        metadata_key = get_metadata_address(token)
        user_pda = get_user_pda(owner)
        
        # Check if accounts exist
        wsol_ata_exists = await check_ata_exists(executor, wsol_ata)
        user_account_exists = await executor.get_account_info(user_pda) is not None
        
        # Start with compute budget instructions
        instructions = create_compute_budget_instructions()
        print(f"\n💰 Transaction budget:")
        print(f"Compute unit limit: 1,400,000")
        print(f"Compute unit price: 100")
        
        # Create WSOL ATA if needed
        if not wsol_ata_exists:
            print(f"\n🔧 Creating WSOL ATA: {wsol_ata}")
            create_wsol_ata_ix = create_associated_token_account_idempotent(
                payer=owner,
                wallet=owner,
                mint=NATIVE_MINT_KEY
            )
            instructions.append(create_wsol_ata_ix)
        
        # Initialize user account if needed
        if not user_account_exists:
            print("\n🔧 Creating PUMP user account")
            init_ix = create_user_init_instruction(owner)
            instructions.append(init_ix)
        
        # Create instruction data with correct Anchor discriminator
        # - 8 bytes discriminator
        # - 32 bytes token mint
        # - 8 bytes token amount
        # - 4 bytes slippage
        discriminator = bytes.fromhex("2c1dcd5a8b6c3c54")  # initialize_curve_and_sell
        instruction_data = (
            discriminator +                      # 8 bytes: Anchor discriminator
            bytes(token) +                       # 32 bytes: Token mint
            struct.pack("<Q", token_amount) +    # 8 bytes: Token amount (u64)
            struct.pack("<I", slippage_bps)      # 4 bytes: Slippage (u32)
        )
        
        print(f"\n📝 Instruction data:")
        print(f"Total length: {len(instruction_data)} bytes")
        print(f"Full hex: {instruction_data.hex()}")
        print(f"Discriminator: {discriminator.hex()}")
        print(f"Token mint: {bytes(token).hex()}")
        print(f"Amount: {struct.pack('<Q', token_amount).hex()}")
        print(f"Slippage: {struct.pack('<I', slippage_bps).hex()}")
        
        # Account metas in same order as buy, just swapped ATAs
        print(f"\n📋 Building swap accounts:")
        accounts = [
            # Essential accounts only, in exact order
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),           # Wallet (signer)
            AccountMeta(pubkey=token_ata, is_writable=True, is_signer=False),     # Token ATA
            AccountMeta(pubkey=wsol_ata, is_writable=True, is_signer=False),      # WSOL ATA
            AccountMeta(pubkey=pump_token_vault, is_writable=True, is_signer=False), # Token vault
            AccountMeta(pubkey=pump_wsol_vault, is_writable=True, is_signer=False), # WSOL vault  
            AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),      # User PDA
            AccountMeta(pubkey=token, is_writable=False, is_signer=False),         # Token mint
            AccountMeta(pubkey=NATIVE_MINT_KEY, is_writable=False, is_signer=False), # WSOL mint
            AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_writable=False, is_signer=False) # Token program
        ]
        
        print(f"\n📄 Account list:")
        for i, acct in enumerate(accounts):
            writable = "✏️" if acct.is_writable else "📖"
            signer = "🔑" if acct.is_signer else "  "
            print(f"{i:2d}. {writable} {signer} {acct.pubkey}")
        
        sell_ix = Instruction(
            program_id=PUMP_ROUTER_KEY,  # Production PUMP router
            data=instruction_data,
            accounts=accounts
        )
        
        # Add transaction components
        instructions.append(sell_ix)
        
        # Get blockhash
        blockhash = await executor.get_latest_blockhash()
        if not blockhash:
            print("Failed to get blockhash")
            return None
            
        print(f"\n🔐 Building transaction:")
        print(f"Recent blockhash: {blockhash}")
        print(f"Total instructions: {len(instructions)}")
        
        # Build and return transaction
        message = MessageV0.try_compile(
            payer=owner,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )
        
        print("\n✅ Transaction built successfully!")
        return VersionedTransaction(message, [keypair])
        
    except Exception as e:
        print(f"\n❌ Error building sell transaction: {e}")
        traceback.print_exc()
        return None
