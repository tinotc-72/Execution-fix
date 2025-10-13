# config.py

"""
Configuration file for Solana trading bot
Last updated: 2025-06-27
Author: tinotc-72
"""

import base58
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from env_keys import kz  # This loads your environment variables
import logging
from typing import Optional
import traceback

# === URLs and Endpoints ===
HELIUS_WS_URL = kz.HELIUS_Standard_Websocket_URL or f"wss://ws.helius-rpc.com/?api-key={kz.HELIUS_API_KEY}"
HELIUS_RPC_URL = kz.HELIUS_RPC_URL
WALLET_DEBUG = {
    "ENABLE_TX_LOGGING": True,
    "LOG_SIGNATURES": True,
    "VERIFY_BEFORE_SEND": True,
    "MAX_RETRIES": 3,
    "CONFIRMATION_TIMEOUT": 60
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_keypair_creation(private_key_bytes: bytes) -> None:
    """Debug utility to verify keypair creation parameters"""
    logger.debug(f"Private key length: {len(private_key_bytes)} bytes")
    logger.debug(f"First 32 bytes: {private_key_bytes[:32].hex()}")
    if len(private_key_bytes) >= 64:
        logger.debug(f"Last 32 bytes: {private_key_bytes[32:64].hex()}")

def validate_wallet(wallet: Optional[Keypair]) -> bool:
    """Validate that a wallet is properly configured and can sign transactions."""
    try:
        if wallet is None:
            logger.error("❌ Wallet is None")
            return False
            
        if not isinstance(wallet, Keypair):
            logger.error(f"❌ Wallet is not a Keypair: {type(wallet)}")
            return False
            
        # Verify public key
        try:
            pubkey = wallet.pubkey()
            if not pubkey:
                logger.error("❌ Could not get wallet public key")
                return False
            logger.info(f"✅ Valid public key: {pubkey}")
        except Exception as e:
            logger.error(f"❌ Error getting public key: {e}")
            return False
            
        # Test signing capability
        try:
            test_message = bytes([1, 2, 3, 4])
            signature = wallet.sign_message(test_message)
            # Check if signature exists (don't check length)
            if not signature:
                logger.error("❌ No signature produced")
                return False
            # Convert signature to bytes for verification
            sig_bytes = bytes(signature)
            if not sig_bytes:
                logger.error("❌ Could not convert signature to bytes")
                return False
            logger.info("✅ Signing capability verified")
        except Exception as e:
            logger.error(f"❌ Signing test failed: {e}")
            return False
            
        logger.info(f"✅ Wallet validated successfully:")
        logger.info(f"  Public Key: {pubkey}")
        logger.info(f"  Type: {type(wallet)}")
        logger.info(f"  Can Sign: True")
        return True
        
    except Exception as e:
        logger.error(f"❌ Wallet validation failed: {e}")
        return False

# === Load and decode Phantom private key ===
try:
    if not kz.PHANTOM_PRIVATE_KEY:
        raise ValueError("PHANTOM_PRIVATE_KEY is not set in your .env file")

    # Clean and decode the private key with detailed logging
    cleaned_key = kz.PHANTOM_PRIVATE_KEY.strip()
    logger.info("Attempting to decode private key...")
    
    try:
        DECODED_PRIVATE_KEY = base58.b58decode(cleaned_key)
        logger.info(f"✅ Successfully decoded private key (length: {len(DECODED_PRIVATE_KEY)} bytes)")
    except Exception as decode_error:
        logger.error(f"❌ Failed to decode private key: {decode_error}")
        raise ValueError("Invalid base58 private key format")

    # Verify decoded key length
    if len(DECODED_PRIVATE_KEY) != 64:
        logger.error(f"❌ Invalid decoded key length: {len(DECODED_PRIVATE_KEY)} bytes")
        raise ValueError(f"Decoded key must be 64 bytes, got {len(DECODED_PRIVATE_KEY)}")

    try:
        # Create keypair from bytes
        logger.info("Creating Keypair from decoded bytes...")
        
        # Create the keypair using from_bytes
        WALLET = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        
        # Get and verify public key
        BOT_PUBKEY = WALLET.pubkey()
        if not BOT_PUBKEY:
            raise ValueError("Could not derive public key from wallet")
            
        logger.info(f"✅ Created Keypair with public key: {BOT_PUBKEY}")
        
        # Test signing immediately after creation
        logger.info("Testing signing capability...")
        test_message = bytes([1, 2, 3, 4])
        test_signature = WALLET.sign_message(test_message)
        if not test_signature:
            raise ValueError("Initial signing test failed")
        logger.info("✅ Initial signing test successful")

        # Full wallet validation
        logger.info("Performing full wallet validation...")
        if not validate_wallet(WALLET):
            raise ValueError("Comprehensive wallet validation failed")

        # Success logging
        logger.info("🎉 Wallet initialization complete:")
        logger.info(f"  📱 Public Key: {BOT_PUBKEY}")
        logger.info(f"  🔐 Signing Enabled: Yes")

    except Exception as wallet_error:
        logger.error(f"❌ Wallet initialization failed: {wallet_error}")
        logger.error("Stack trace:", exc_info=True)
        raise ValueError(f"Failed to create wallet: {wallet_error}")

except Exception as e:
    logger.error("❌ Fatal error in wallet initialization:")
    logger.error(str(e))
    logger.error("Stack trace:", exc_info=True)
    raise ValueError(f"Failed to initialize wallet: {e}")

# Add transaction validation settings
TX_VALIDATION = {
    "VERIFY_SIGNATURES": True,
    "CHECK_BALANCE_BEFORE_SEND": True,
    "MIN_SOL_BALANCE": 0.01,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1.0
}

# === Pump.fun Program IDs ===
PUMP_FUN_PROGRAM_ID = Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj")
PUMP_TRADE_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

# === RPC Configuration ===
RPC_URL = HELIUS_RPC_URL  # Alias for backward compatibility

# === Jito Configuration ===
JITO_AUTH_TOKEN = kz.JITO_UUID

# Jito API Endpoints
JITO_BLOCK_ENGINE = "https://london.mainnet.block-engine.jito.wtf/api/v1/transactions"
JITO_RELAYER = "http://london.mainnet.relayer.jito.wtf:8100"
JITO_BUNDLE_URL = "https://london.mainnet.block-engine.jito.wtf/api/v1/bundle"
JITO_STATUS_URL = "https://london.mainnet.block-engine.jito.wtf/api/v1/getBundleStatuses"

# Jito Headers
JITO_HEADERS = {
    "Content-Type": "application/json",
    "x-jito-auth": JITO_AUTH_TOKEN
}

# === Transaction Configuration ===
COMPUTE_UNIT_LIMIT = 1_400_000
COMPUTE_UNIT_PRICE = 100
JITO_TIP_AMOUNT = 10_000
SLIPPAGE_BPS = 1000  # 10% slippage tolerance (1000 basis points)

# === Program IDs ===
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
JITO_TIP_PROGRAM_ID = Pubkey.from_string("4R3gSG8BpU4t19KYj8CfnbtRpnT8gtk4dvTHxVRwc2r7")

# === Jito tip accounts (from getTipAccounts endpoint) ===
VALID_JITO_TIP_ACCOUNTS = [
    Pubkey.from_string("96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"),
    Pubkey.from_string("HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"),
    Pubkey.from_string("Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY"),
    Pubkey.from_string("ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49"),
    Pubkey.from_string("DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh"),
    Pubkey.from_string("ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt"),
    Pubkey.from_string("DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL"),
    Pubkey.from_string("3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT")
]

# === Wallets to monitor ===
MONITORED_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Your original wallet 1
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Your original wallet 2
    # TEMPORARY TEST WALLETS - HIGHLY ACTIVE PUMP.FUN TRADERS
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Very active trader
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # High frequency trader  
    "7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN6X1oHXkuqvg",  # Volume trader
    "3D49QorJyNaL9HPe4VPTLqpezZZGP5TXKYaG1gJFJXFG",  # Active pump trader
    "CuieVDEDtLo7FypA9SbLM9saXFdb1dsshEkyErMqkRQq",  # Frequent trader
]
MONITORED_WALLET_PUBKEYS = [Pubkey.from_string(addr) for addr in MONITORED_WALLETS]

# Backward compatibility for legacy components
WALLET_A_ADDRESS = MONITORED_WALLETS[0]  # Primary wallet to monitor
RPC_URL = HELIUS_RPC_URL

# === Bundle Configuration ===
BUNDLE_CONFIG = {
    "tip_percentage": 90
}

# === Debug Flag ===
DEBUG = True

__all__ = [
    "WALLET",
    "BOT_PUBKEY",
    "PUMP_FUN_PROGRAM_ID",
    "PUMP_TRADE_PROGRAM",
    "RPC_URL",
    "JITO_AUTH_TOKEN",
    "JITO_BLOCK_ENGINE",
    "JITO_RELAYER",
    "JITO_BUNDLE_URL",
    "JITO_STATUS_URL",
    "JITO_HEADERS",
    "COMPUTE_UNIT_LIMIT",
    "COMPUTE_UNIT_PRICE",
    "JITO_TIP_AMOUNT",
    "WALLET_DEBUG",
    "validate_wallet",
    "SLIPPAGE_BPS",
    "COMPUTE_BUDGET_PROGRAM_ID",
    "SYS_PROGRAM_ID",
    "JITO_TIP_PROGRAM_ID",
    "VALID_JITO_TIP_ACCOUNTS",
    "MONITORED_WALLETS",
    "MONITORED_WALLET_PUBKEYS",
    "BUNDLE_CONFIG",
    "DEBUG"
]
