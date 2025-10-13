"""
Environment variables loader
Last updated: 2025-06-27
Author: tinotc-72
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

def validate_env_vars():
    """Validate critical environment variables are set"""
    required_vars = {
        "PHANTOM_PRIVATE_KEY": "Your Phantom wallet private key in base58 format",
        "HELIUS_API_KEY": "Your Helius API key"
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or len(value.strip()) == 0:
            missing.append(f"{var} ({description})")
    
    if missing:
        error_message = "\n❌ Missing required environment variables:\n\n"
        error_message += "\n".join(f"- {var}" for var in missing)
        error_message += "\n\nPlease create or update your .env file with these variables:"
        error_message += "\n\nExample .env format:"
        error_message += '\nPHANTOM_PRIVATE_KEY="your_base58_private_key_here"'
        error_message += '\nHELIUS_API_KEY="your-api-key-here"'
        raise ValueError(error_message)

# Validate environment variables on module import
validate_env_vars()

class EnvKeys:
    def __init__(self):
        # === Phantom Private Key ===
        self.PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY").strip()

        # === Helius API Configuration ===
        self.HELIUS_API_KEY = os.getenv("HELIUS_API_KEY").strip()

        # === Primary RPC Endpoints (Helius) ===
        self.HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={self.HELIUS_API_KEY}"
        self.HELIUS_Standard_Websocket_URL = f"wss://mainnet.helius-rpc.com/v0/?api-key={self.HELIUS_API_KEY}"

        # === Backup RPC Endpoints ===
        self.PUBLIC_RPC_URL = "https://api.mainnet-beta.solana.com"
        self.QUICKNODE_RPC_URL = os.getenv("QUICKNODE_RPC_URL", "")  # Optional QuickNode backup

        # === Headers ===
        self.HELIUS_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.HELIUS_API_KEY}"
        }

        self.WS_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.HELIUS_API_KEY}"
        }

        # === API Endpoints ===
        self.API_URL = "https://api.helius-rpc.com/v0"
        self.PARSE_TX_URL = f"{self.API_URL}/transactions"
        self.TX_HISTORY_URL = f"{self.API_URL}/addresses/{{address}}/transactions"

        # === Legacy Private Key (optional fallback) ===
        self.BULLX_NEO_PRIVATE_KEY_QM = os.getenv("BULLX_NEO_PRIVATE_KEY_QM", "")

        # === Jito Settings ===
        self.JITO_UUID = os.getenv('JITO_UUID')
        self.JITO_AUTH_TOKEN = os.getenv('JITO_AUTH_TOKEN')
        self.JITO_BUNDLE_ENDPOINT = os.getenv('JITO_BUNDLE_ENDPOINT')

        # === Trading Settings ===
        self.INITIAL_INVESTMENT = float(os.getenv('INITIAL_INVESTMENT', '0.05'))

        # === Debug Print ===
        print("\nRPC Configuration:")
        print(f"HELIUS_RPC_URL: {self.HELIUS_RPC_URL}")
        print(f"Websocket URL: {self.HELIUS_Standard_Websocket_URL}")

# Singleton instance to import elsewhere
kz = EnvKeys()
