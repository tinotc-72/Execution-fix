# keyZ.py

import base58
from solders.keypair import Keypair

# Helius Configuration
HELIUS_API_KEY = "7277139c-ff2c-4257-ad06-2db6aa16c315"
HELIUS_RPC_URL = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
HELIUS_Standard_Websocket_URL = "wss://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"


JITO_UUID = "4d08ea10-2b60-11f0-858a-6bee29fce9c1" 

# Jito Configuration
JITO_AUTH_TOKEN = "4d08ea10-2b60-11f0-858a-6bee29fce9c1" 
JITO_BUNDLE_ENDPOINT = "https://mainnet.block-engine.jito.wtf/api/v1/bundles/sendBundle"

# Wallet Configuration
BULLX_NEO_PRIVATE_KEY_QM = "q371JiV7NjNxbznxP63JYyFknJvtrEUA78mg2EwJbQ9UNhz5cJo8W7DTH3EbD9LAkV2FJgGGkF4tNrWRsXAJnUk"

BOT_PRIVATE_KEY_B58 = "3Td2VwL2vhb9mvCoHBA6WMWhbUWrmuVYGPhH9AXqzGo3LJafm4xzot1kBspHM2vLMxNboW9FhqeHBasq2iursG6o"

DECODED_PRIVATE_KEY = base58.b58decode(BULLX_NEO_PRIVATE_KEY_QM)