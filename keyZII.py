# keyZ.py

import base58
from solders.keypair import Keypair

# Helius Configuration
HELIUS_API_KEY = "=your-private-key-here"
HELIUS_RPC_URL = "=your-private-key-here"
HELIUS_Standard_Websocket_URL = "=your-private-key-here"


JITO_UUID = "=your-private-key-here"

# Jito Configuration
JITO_AUTH_TOKEN = "=your-private-key-here"
JITO_BUNDLE_ENDPOINT = "=your-private-key-here"

# Wallet Configuration
BULLX_NEO_PRIVATE_KEY_QM = "=your-private-key-here"

BOT_PRIVATE_KEY_B58 = "=your-private-key-here"

DECODED_PRIVATE_KEY = base58.b58decode(BULLX_NEO_PRIVATE_KEY_QM)