# config.py

import base58
import keyZ as kz
from solders.pubkey import Pubkey

# Decode the private key that we verified is working
DECODED_PRIVATE_KEY = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM)
WALLET_PRIVATE_KEY = DECODED_PRIVATE_KEY
BOT_PUBKEY = Pubkey.from_bytes(DECODED_PRIVATE_KEY[32:])

# The main Pump.fun program ID for production environment
PUMP_FUN_PROGRAM_ID = Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj")

# RPC Configuration
HELIUS_RPC_URL = kz.HELIUS_RPC_URL
RPC_URL = kz.HELIUS_RPC_URL
HELIUS_WS_URL = kz.HELIUS_Standard_Websocket_URL

# Jito Configuration
JITO_AUTH_TOKEN = kz.JITO_AUTH_TOKEN

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

# Transaction Configuration
COMPUTE_UNIT_LIMIT = 1_400_000  # Jito recommended value
COMPUTE_UNIT_PRICE = 100        # Micro-lamports per compute unit
JITO_TIP_AMOUNT = 10_000       # Minimum tip amount required by Jito

# Program IDs
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
JITO_TIP_PROGRAM_ID = Pubkey.from_string("4R3gSG8BpU4t19KYj8CfnbtRpnT8gtk4dvTHxVRwc2r7")

# Jito tip accounts (from getTipAccounts endpoint)
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

# Wallet Configuration
WALLET_A_ADDRESS = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
WALLET_A = Pubkey.from_string(WALLET_A_ADDRESS)

# Bundle Configuration
BUNDLE_CONFIG = {
    "tip_percentage": 90  # Percentage of profit to tip searchers
}