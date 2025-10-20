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

# === Secondary RPC for Failover ===
# Copilot TODO: If primary RPC is unhealthy, automatically switch to secondary
SECONDARY_RPC_URL = getattr(kz, 'SECONDARY_RPC_URL', 'https://api.mainnet-beta.solana.com')

WALLET_DEBUG = {
    "ENABLE_TX_LOGGING": True,
    "LOG_SIGNATURES": True,
    "VERIFY_BEFORE_SEND": True,
    "MAX_RETRIES": 3,
    "CONFIRMATION_TIMEOUT": 60
}

# Setup logging - DEEP DEBUG MODE
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for deeper logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level

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

    # Verify decoded key length (accept both 32 and 64 byte formats)
    if len(DECODED_PRIVATE_KEY) not in [32, 64]:
        logger.error(f"❌ Invalid decoded key length: {len(DECODED_PRIVATE_KEY)} bytes")
        raise ValueError(f"Decoded key must be 32 or 64 bytes, got {len(DECODED_PRIVATE_KEY)}")


    class WalletWithSign:
        def __init__(self, keypair, buy_amount_sol=0.001):
            self.keypair = keypair
            self.buy_amount_sol = buy_amount_sol
        def pubkey(self):
            return self.keypair.pubkey()
        def sign(self, message):
            return self.keypair.sign_message(message)
        def sign_message(self, message):
            return self.keypair.sign_message(message)
    try:
        # Create keypair from bytes (handle both 32 and 64-byte formats)
        logger.info("Creating Keypair from decoded bytes...")
        if len(DECODED_PRIVATE_KEY) == 64:
            # 64-byte format - use directly with solders
            base_keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        elif len(DECODED_PRIVATE_KEY) == 32:
            # 32-byte format - use from_seed with solders
            base_keypair = Keypair.from_seed(DECODED_PRIVATE_KEY)
        else:
            raise ValueError(f"Unsupported private key length: {len(DECODED_PRIVATE_KEY)} bytes")
        WALLET = WalletWithSign(base_keypair)
        # Get and verify public key
        BOT_PUBKEY = WALLET.pubkey()
        if not BOT_PUBKEY:
            raise ValueError("Could not derive public key from wallet")
        logger.info(f"✅ Created Keypair with public key: {BOT_PUBKEY}")
        # Test signing immediately after creation
        logger.info("Testing signing capability...")
        test_message = bytes([1, 2, 3, 4])
        test_signature = WALLET.sign(test_message)
        if not test_signature:
            raise ValueError("Initial signing test failed")
        logger.info("✅ Initial signing test successful")
        # Full wallet validation
        logger.info("Performing full wallet validation...")
        if not validate_wallet(base_keypair):
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
PUMP_FUN_PROGRAM_ID = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
PUMP_TRADE_PROGRAM = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")

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

# === Fail-Open Coordinator Configuration ===
INVESTMENT_PER_TRADE_SOL = 0.001  # Default investment amount when parser cannot infer amount

# === Program IDs ===
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
JITO_TIP_PROGRAM_ID = Pubkey.from_string("4R3gSG8BpU4t19KYj8CfnbtRpnT8gtk4dvTHxVRwc2r7")

# === Jito tip accounts (from getTipAccounts endpoint) ===
VALID_JITO_TIP_ACCOUNTS = [
    "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
    "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe", 
    "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
    "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
    "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
    "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
]

# === Wallets to monitor ===
MONITORED_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Your target wallet 1
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Your target wallet 2
    "Ez2jp3rwXUbaTx7XwiHGaWVgTPFdzJoSg8TopqbxfaJN",  # Your target wallet 3
    "9ePNTG4j5eDGTFtUr6axt7h747HHzJPfmFh6JHAwFZsd",  # Your target wallet 4 (added)
    "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB",  # Your target wallet 5 (new)
]
MONITORED_WALLET_PUBKEYS = [Pubkey.from_string(addr) for addr in MONITORED_WALLETS]

# Backward compatibility for legacy components
WALLET_A_ADDRESS = MONITORED_WALLETS[0]  # Primary wallet to monitor
RPC_URL = HELIUS_RPC_URL

# === Bundle Configuration ===
BUNDLE_CONFIG = {
    "tip_percentage": 90
}

# === Global Debug Configuration ===
DEBUG = True  # Global debug flag - set to False for production
DEEP_DEBUG = True  # Extra verbose debug logging - set to False for performance
EXECUTION_DEBUG = True  # Debug execution flow and parameters
TRANSACTION_DEBUG = True  # Debug transaction parsing and analysis
WEBSOCKET_DEBUG = True  # Debug WebSocket message processing

# === Program IDs ===
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

import os
# === Token to Trade (Replace with your token) ===
CPMM_TOKEN_MINT = Pubkey.from_string("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")  # Example token, replace with your target

class CopyTradeConfig:
    """Configuration class for copy trading bot with full executor compatibility"""
    
    def __init__(self, target_wallets=None, investment_amount_sol=None, max_positions=None, 
                 use_jito=None, slippage_tolerance=None, slippage_bps=None, enable_dexes=None):
        # Target wallets to monitor
        self.target_wallets = target_wallets if target_wallets is not None else MONITORED_WALLETS
        
        # Trading settings - MORE PERMISSIVE CONFIGURATION for aggressive copy trading
        self.investment_amount_sol = investment_amount_sol if investment_amount_sol is not None else 0.0001  # Lower minimum
        self.min_sol_amount = 0.0001  # Lower minimum SOL
        self.slippage_tolerance = slippage_tolerance if slippage_tolerance is not None else 0.99  # 99% slippage
        self.use_jito = use_jito if use_jito is not None else True  # Enable Jito for faster execution
        self.slippage_bps = slippage_bps if slippage_bps is not None else 9900  # 99% slippage in basis points
        self.max_positions = max_positions if max_positions is not None else 20  # Allow more positions
        
        # === EXECUTOR CONFIG COMPATIBILITY ===
        # More permissive retry parameters
        self.max_retries = 10  # More retries
        self.retry_delay = 0.5  # Shorter delay
        
        # Permissive transaction parameters
        self.skip_preflight = True  # Permissive: skip preflight checks for speed
        self.preflight_commitment = "processed"
        self.max_retries_rpc = 10  # More RPC retries
        
        # Faster confirmation parameters
        self.confirmation_timeout = 10.0  # Lower confirmation wait
        self.confirmation_commitment = "processed"  # Faster commitment level
        self.confirmation_check_interval = 0.5  # Faster checks
        
        # Higher compute budget parameters for better execution
        self.compute_unit_limit = 1_600_000  # Higher compute units
        self.compute_unit_price = 1  # Lower priority fee
        
        # Extended timeout parameters
        self.transaction_timeout = 300.0  # Longer blockhash timeout
        self.fresh_blockhash_timeout = 120.0
        
        # Permissive slippage and amounts
        self.default_slippage = 0.99  # 99% default slippage
        self.max_slippage = 0.99  # 99% max slippage
        self.gas_buffer_sol = 0.001  # Lower SOL buffer for gas fees
        
        # Additional executor fields - more permissive
        self.priority_fee = 1_000  # Lower priority fee in lamports
        self.jito_tip_amount = 10_000  # Lower Jito tip amount
        
        # DEX configuration - Enable all DEXes by default for maximum permissiveness
        default_dexes = {dex: True for dex in [
            "direct_pumpfun", "pumpfun", "jupiter", "raydium", "cpmm", "clmm", "orca", "phoenix", "meteora"
        ]}
        self.enable_dexes = enable_dexes if enable_dexes is not None else default_dexes
        
        # WebSocket and RPC settings
        # Always set rpc_url from env, fallback to os.getenv if needed
        self.rpc_url = HELIUS_RPC_URL if HELIUS_RPC_URL else os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
        self.ws_url = HELIUS_WS_URL if 'HELIUS_WS_URL' in globals() else os.getenv("WS_URL", "")

    @property
    def get_rpc_url(self):
        return self.rpc_url
        self.ws_url = HELIUS_WS_URL
        
        # Monitoring settings
        self.max_retries = 3
        self.analysis_timeout = 15.0
        
        # Position tracking
        self.enable_position_tracking = True
        self.auto_liquidate_on_stop = True
        
        # Debug configuration - inherit from global flags
        self.debug = DEBUG
        self.deep_debug = DEEP_DEBUG
        self.execution_debug = EXECUTION_DEBUG
        self.transaction_debug = TRANSACTION_DEBUG
        self.websocket_debug = WEBSOCKET_DEBUG
    
    def to_solana_executor_config(self):
        """Convert CopyTradeConfig to SolanaExecutorConfig for executor compatibility"""
        try:
            from base_solana_executor import SolanaExecutorConfig
            return SolanaExecutorConfig(
                max_retries=getattr(self, 'max_retries', 3),
                retry_delay=getattr(self, 'retry_delay', 1.0),
                skip_preflight=getattr(self, 'skip_preflight', True),
                preflight_commitment=getattr(self, 'preflight_commitment', "processed"),
                max_retries_rpc=getattr(self, 'max_retries_rpc', 3),
                confirmation_timeout=getattr(self, 'confirmation_timeout', 60.0),
                confirmation_commitment=getattr(self, 'confirmation_commitment', "confirmed"),
                confirmation_check_interval=getattr(self, 'confirmation_check_interval', 2.0),
                compute_unit_limit=getattr(self, 'compute_unit_limit', 300_000),
                compute_unit_price=getattr(self, 'compute_unit_price', 10_000),
                transaction_timeout=getattr(self, 'transaction_timeout', 150.0),
                fresh_blockhash_timeout=getattr(self, 'fresh_blockhash_timeout', 60.0),
                default_slippage=getattr(self, 'default_slippage', 0.05),
                max_slippage=getattr(self, 'max_slippage', 0.30),
                min_sol_amount=getattr(self, 'min_sol_amount', 0.001),
                gas_buffer_sol=getattr(self, 'gas_buffer_sol', 0.01)
            )
        except ImportError:
            # Fallback if SolanaExecutorConfig is not available
            logger.warning("SolanaExecutorConfig not available, using self as config")
            return self
    
    def validate_executor_config(self):
        """Validate that all required executor fields are present"""
        required_fields = [
            'gas_buffer_sol', 'default_slippage', 'max_slippage', 'min_sol_amount',
            'compute_unit_limit', 'compute_unit_price', 'max_retries', 'retry_delay',
            'confirmation_timeout', 'transaction_timeout'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not hasattr(self, field):
                missing_fields.append(field)
                logger.error(f"Config missing required field: {field}")
        
        if missing_fields:
            logger.error(f"Missing executor config fields: {missing_fields}")
            return False
        
        logger.info("✅ All executor config fields validated successfully")
        return True
    
    # Dict-like methods for executor compatibility (Jupiter executor needs these)
    def get(self, key, default=None):
        """Get config value with default fallback (dict-like behavior)"""
        return getattr(self, key, default)
    
    def __getitem__(self, key):
        """Allow dict-style access config['key']"""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Config key '{key}' not found")
    
    def __setitem__(self, key, value):
        """Allow dict-style assignment config['key'] = value"""
        setattr(self, key, value)
    
    def setdefault(self, key, default=None):
        """Set default value if key doesn't exist (dict-like behavior)"""
        if not hasattr(self, key):
            setattr(self, key, default)
        return getattr(self, key)

__all__ = [
    "WALLET",
    "BOT_PUBKEY",
    "PUMP_FUN_PROGRAM_ID",
    "PUMP_TRADE_PROGRAM",
    "RPC_URL",
    "SECONDARY_RPC_URL",
    "JITO_AUTH_TOKEN",
    "JITO_BLOCK_ENGINE",
    "JITO_RELAYER",
    "JITO_BUNDLE_URL",
    "JITO_STATUS_URL",
    "JITO_HEADERS",
    "COMPUTE_UNIT_LIMIT",
    "COMPUTE_UNIT_PRICE",
    "JITO_TIP_AMOUNT",
    "INVESTMENT_PER_TRADE_SOL",
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
    "DEBUG",
    "DEEP_DEBUG",
    "EXECUTION_DEBUG", 
    "TRANSACTION_DEBUG",
    "WEBSOCKET_DEBUG",
    "TOKEN_PROGRAM_ID",
    "SYSTEM_PROGRAM_ID",
    "ASSOCIATED_TOKEN_PROGRAM_ID",
    "SYSVAR_RENT_PUBKEY",
    "NATIVE_MINT",
    "CPMM_TOKEN_MINT",
    "CopyTradeConfig"
]
