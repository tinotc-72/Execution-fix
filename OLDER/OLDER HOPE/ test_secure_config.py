# test_secure_config.py
from config import *

def test_config():
    print("\n🔒 Testing Secure Configuration")
    print("=" * 50)
    
    # Test wallet configuration
    print("\n👛 Wallet Configuration:")
    print(f"BOT_PUBKEY: {BOT_PUBKEY}")
    print(f"Private key loaded: {'✅' if DECODED_PRIVATE_KEY else '❌'}")
    
    # Test RPC configuration
    print("\n🌐 RPC Configuration:")
    print(f"HELIUS_RPC_URL: {'✅' if HELIUS_RPC_URL else '❌'}")
    print(f"HELIUS_WS_URL: {'✅' if HELIUS_WS_URL else '❌'}")
    
    # Test Jito configuration
    print("\n🚀 Jito Configuration:")
    print(f"JITO_AUTH_TOKEN: {'✅' if JITO_AUTH_TOKEN else '❌'}")
    
    # Verify program IDs
    print("\n📝 Program IDs:")
    print(f"PUMP_FUN_PROGRAM_ID: {PUMP_FUN_PROGRAM_ID}")
    print(f"COMPUTE_BUDGET_PROGRAM_ID: {COMPUTE_BUDGET_PROGRAM_ID}")

if __name__ == "__main__":
    test_config()