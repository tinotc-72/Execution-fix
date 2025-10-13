#!/usr/bin/env python3
"""
Test the fixed ATA creation logic - NEW VERSION
"""

print("Starting ATA fix test...")

import asyncio
import logging
print("Imported asyncio and logging...")

try:
    from jupiter_copy_executor import JupiterCopyExecutor
    print("Successfully imported JupiterCopyExecutor")
except Exception as e:
    print(f"Failed to import JupiterCopyExecutor: {e}")
    raise

try:
    from config import WALLET
    print("Successfully imported WALLET")
except Exception as e:
    print(f"Failed to import WALLET: {e}")
    raise

try:
    from env_keys import EnvKeys
    print("Successfully imported EnvKeys")
except Exception as e:
    print(f"Failed to import EnvKeys: {e}")
    raise

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_new_ata_fix():
    """Test the fixed ATA creation logic"""
    
    print(f"🧪 TESTING NEW ATA FIX")
    print("=" * 80)
    
    try:
        env_keys = EnvKeys()
        
        # Create Jupiter executor
        executor = JupiterCopyExecutor(
            wallet_keypair=WALLET,
            rpc_url=env_keys.HELIUS_RPC_URL
        )
        
        # Test with the token from successful trades
        test_token = "DAjnBrfGGYtC2QFypWMZivxTETKF9Abu8ZK17VZ5pump"
        
        print(f"🪙 Testing ATA creation for: {test_token[:8]}...")
        
        # Test ATA creation
        from solders.pubkey import Pubkey
        mint_pubkey = Pubkey.from_string(test_token)
        ata_address = await executor.ensure_token_account_exists(mint_pubkey)
        
        print(f"✅ ATA creation test successful!")
        print(f"🎯 ATA Address: {ata_address}")
        
        # Verify ATA exists
        account_info = await executor.client.get_account_info(ata_address)
        if account_info.value:
            print(f"✅ ATA verified to exist on chain")
        else:
            print(f"❌ ATA not found on chain")
        
        return True
        
    except Exception as e:
        print(f"❌ ATA creation test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_new_ata_fix())
    if success:
        print(f"\n✅ NEW ATA FIX IS WORKING!")
        print(f"🎯 This should resolve the IllegalOwner errors")
    else:
        print(f"\n❌ ATA creation still has issues")
