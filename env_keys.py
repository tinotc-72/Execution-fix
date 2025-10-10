"""
Environment variables loader
Last updated: 2025-06-27
Author: tinotc-72
"""

from dotenv import load_dotenv, find_dotenv
import os
import logging
from solders.keypair import Keypair
import base58
from pathlib import Path
import re

# Configure logging first
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def find_env_file():
    """Find the .env file by looking in multiple possible locations"""
    # Try current directory first
    env_paths = [
        Path(".env"),  # Current directory
        Path(__file__).parent / ".env",  # Same directory as this script
        Path(__file__).parent.parent / ".env",  # Parent directory
    ]
    
    for path in env_paths:
        if path.exists():
            logger.info(f"Found .env file at: {path.absolute()}")
            return str(path.absolute())
    
    # If no .env found in explicit locations, try find_dotenv()
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        logger.info(f"Found .env file using find_dotenv: {dotenv_path}")
        return dotenv_path
    
    return None

# Find and load the .env file
env_path = find_env_file()
if not env_path:
    logger.error("No .env file found in any expected location!")
    raise RuntimeError("No .env file found!")

# Load environment variables from .env file
logger.info(f"Loading environment from: {env_path}")
if not load_dotenv(dotenv_path=env_path, override=True):
    logger.error(f"Failed to load .env file from {env_path}!")
    raise RuntimeError("Failed to load .env file!")

def validate_env_vars() -> dict:
    """Validate and return required environment variables"""
    required_vars = {
        "RPC_URL": "Solana RPC endpoint",
        "PHANTOM_PRIVATE_KEY": "Wallet private key"
    }
    
    missing = []
    env_vars = {}
    
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"{var} ({desc})")
        else:
            env_vars[var] = value
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Log RPC configuration (but not private key)
    logger.info("\nRPC Configuration:")
    logger.info(f"RPC_URL: {env_vars['RPC_URL']}")
    
    return env_vars

def load_wallet_from_private_key(private_key: str = None):
    """Load wallet from the base58 private key stored in environment variables"""
    if private_key is None:
        private_key = os.getenv("PHANTOM_PRIVATE_KEY")
        if not private_key:
            raise ValueError("PHANTOM_PRIVATE_KEY not found in environment variables")
    
    # Clean the key
    private_key = private_key.strip().replace('"', '').replace("'", '')
    logger.debug(f"Loading wallet from key starting with: {private_key[:4]}...")
    
    try:
        # Handle array format if needed
        if private_key.startswith('[') and private_key.endswith(']'):
            # Convert string array to bytes
            key_arr = [int(x) for x in private_key[1:-1].split(',')]
            keypair = Keypair.from_bytes(bytes(key_arr))
        else:
            # Convert base58 private key to bytes
            private_key_bytes = base58.b58decode(private_key)
            keypair = Keypair.from_bytes(private_key_bytes)
        
        logger.debug(f"Successfully loaded wallet with public key: {keypair.pubkey()}")
        return keypair
    except Exception as e:
        logger.error(f"Failed to create Keypair from private key: {str(e)}")
        raise ValueError(f"Failed to load wallet: {str(e)}")
        
# Clean up the path for RPC URLs to fix any double slashes
def clean_rpc_url(url: str) -> str:
    """Clean up RPC URL by fixing double slashes"""
    return re.sub(r'(?<!:)\/\/', '/', url)

def clean_rpc_url(url: str) -> str:
    """Clean up RPC URL by fixing double slashes"""
    return re.sub(r'(?<!:)\/\/', '/', url)

class EnvKeys:
    def __init__(self):
        # === Phantom Private Key ===
        self.PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY").strip()

        # === Helius API Configuration ===
        self.HELIUS_API_KEY = os.getenv("HELIUS_API_KEY").strip()

        # === Primary RPC Endpoints (Helius) ===
        # Start with base URL + API key
        self.HELIUS_RPC_URL = os.getenv("HELIUS_RPC_URL", "").strip()
        if not self.HELIUS_RPC_URL:
            self.HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={self.HELIUS_API_KEY}"
        
        # Add /v0 before the query string if not present
        if "/v0" not in self.HELIUS_RPC_URL and "?api-key=" in self.HELIUS_RPC_URL:
            self.HELIUS_RPC_URL = self.HELIUS_RPC_URL.replace("?api-key=", "/v0?api-key=")
        elif "/v0" not in self.HELIUS_RPC_URL:
            # Remove trailing slash before adding /v0
            self.HELIUS_RPC_URL = self.HELIUS_RPC_URL.rstrip("/")
            self.HELIUS_RPC_URL = self.HELIUS_RPC_URL + "/v0"
        
        # Clean up any double slashes (but preserve https://)
        self.HELIUS_RPC_URL = self.HELIUS_RPC_URL.replace("//", "/").replace("https:/", "https://")
        
        # OFFICIAL HELIUS FIX: Use explicit WebSocket URL from .env if available
        # Fallback to generated format if not explicitly set
        explicit_ws_url = os.getenv("HELIUS_Standard_Websocket_URL", "").strip()
        if explicit_ws_url:
            self.HELIUS_Standard_Websocket_URL = explicit_ws_url
            self.HELIUS_WS_URL = explicit_ws_url  # Add alias for main.py compatibility
            logger.info(f"Using explicit WebSocket URL from .env: {explicit_ws_url}")
        else:
            # Fallback: Generate websocket URL format (keep original logic as backup)
            ws_base = self.HELIUS_RPC_URL.split("://")[-1].replace("/v0", "")  # Remove /v0 from RPC URL
            self.HELIUS_Standard_Websocket_URL = f"wss://{ws_base}"
            self.HELIUS_WS_URL = self.HELIUS_Standard_Websocket_URL  # Add alias for main.py compatibility
            logger.info(f"Generated WebSocket URL: {self.HELIUS_Standard_Websocket_URL}")

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

        # === Jupiter API Settings ===
        self.JUPITER_API_KEY = os.getenv('JUPITER_API_KEY', '')
        self.JUPITER_QUOTE_URL = os.getenv('JUPITER_QUOTE_URL', 'https://quote-api.jup.ag/v6/quote')
        self.JUPITER_SWAP_URL = os.getenv('JUPITER_SWAP_URL', 'https://quote-api.jup.ag/v6/swap')

        # === Trading Settings ===
        self.INITIAL_INVESTMENT = float(os.getenv('INITIAL_INVESTMENT', '0.05'))

        # Debug logging only on first initialization
        if not hasattr(EnvKeys, '_initialized'):
            logger.info(f"🔗 RPC Configuration loaded successfully")
            logger.info(f"   HELIUS_RPC_URL: {self.HELIUS_RPC_URL[:50]}...") 
            logger.info(f"   WebSocket URL: {self.HELIUS_Standard_Websocket_URL[:50]}...")
            EnvKeys._initialized = True

# Singleton instance to import elsewhere
kz = EnvKeys()
