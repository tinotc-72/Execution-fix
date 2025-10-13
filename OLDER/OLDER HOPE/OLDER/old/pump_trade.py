"""
PUMP router trading module using exact mainnet accounts and instruction data.
"""

import base64
import logging
from typing import Optional
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

# PUMP Router Constants from mainnet tx: 48Yp8uU4Gj2CtsWXQ1ZvgYxocANqtGuXWUkFJvUfAussrjxHk5AiULgVW19Hx1RPv2yLnGRdxzNHFxjeyWDCFwfs
PUMP_TRADE_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_ROUTER_STATE = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_ACCOUNT = Pubkey.from_string("62qc2CNXwrYqQScmEdiZFFAnJR262PxWEuNQtxfafNgV")
PUMP_VAULT_AUTHORITY = Pubkey.from_string("893s38tuZ4gFF8yYvLRKiyPVsw7ZpwN8H6wBPeHvgHLP")
PUMP_TOKEN_VAULT = Pubkey.from_string("GM8KAofy5rJ5FJooNQUNPZRUkpeEkpfVXxgQa9AC4H3i")

# Target token from mainnet transaction
TARGET_TOKEN_MINT = "BngZsgk4R9TNuLJsHnyEKCTUcBCc4ThcD1zfwfqvpump"

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

def check_ata_exists(owner: Pubkey, mint: Pubkey) -> bool:
    """Check if an Associated Token Account exists"""
    if isinstance(mint, str):
        mint = Pubkey.from_string(mint)
    if isinstance(owner, str):
        owner = Pubkey.from_string(owner)

    # TODO: Implement actual check, for now assume we need to create it
    return False

def build_buy_tx(
    payer: Pubkey,
    amount: int,  # in lamports
    slippage: float = 0.30,  # 30% default slippage
) -> Optional[VersionedTransaction]:
    """Build a buy transaction using exact account ordering from mainnet"""
    try:
        # Convert string pubkeys if needed
        if isinstance(payer, str):
            payer = Pubkey.from_string(payer)

        # Derive user's token ATA
        token_ata = get_associated_token_address(payer, Pubkey.from_string(TARGET_TOKEN_MINT))
        
        # Build accounts in exact order from mainnet transaction
        accounts = [
            AccountMeta(pubkey=PUMP_ROUTER_STATE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=PUMP_FEE_ACCOUNT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=Pubkey.from_string(TARGET_TOKEN_MINT), is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_VAULT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_TOKEN_VAULT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),
        ]

        # Build minimal instruction with exact data
        # From the mainnet transaction we have:
        # Program log: Instruction: PumpBuy
        # Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke [2]
        # Program log: Instruction: Buy
        instruction = Instruction(
            program_id=PUMP_TRADE_PROGRAM,
            accounts=accounts,
            data=bytes.fromhex("00")  # Buy instruction discriminator
        )

        # Create transaction
        instructions = [
            # Add ATA creation if needed
            *([] if check_ata_exists(payer, Pubkey.from_string(TARGET_TOKEN_MINT)) else [
                create_associated_token_account(
                    payer=payer,
                    owner=payer,
                    mint=Pubkey.from_string(TARGET_TOKEN_MINT)
                )
            ]),
            # Add compute budget for good measure
            set_compute_unit_limit(400_000),  # 400k compute units
            set_compute_unit_price(500),      # 500 micro-lamports per unit
            instruction
        ]

        # Build message first
        legacy_message = MessageV0.try_compile(
            payer=payer,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=Hash.default()  # Will be updated by executor
        )

        # Create versioned transaction (no signers yet, they'll be added by executor)
        tx = VersionedTransaction(legacy_message, [])

        # Create versioned transaction (no signers yet, they'll be added by executor)
        tx = VersionedTransaction(message, [])

        # Print debug info
        logging.info(f"Built transaction with {len(instructions)} instructions:")
        for i, ix in enumerate(instructions):
            logging.info(f"  {i}: {ix.program_id} with {len(ix.accounts)} accounts")
            logging.info(f"     Data (hex): {ix.data.hex()}")

        return tx

    except Exception as e:
        logging.error(f"Error building buy transaction: {e}")
        return None
