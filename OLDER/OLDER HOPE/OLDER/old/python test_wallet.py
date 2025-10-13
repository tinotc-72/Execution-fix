# test_wallet.py
from dotenv import load_dotenv
import os

def test_wallet_setup():
    print("\n🔍 Testing Wallet Configuration")
    
    # Load the .env file
    load_dotenv()
    
    # Try to get the private key
    private_key = os.getenv('PRIVATE_KEY')
    
    if private_key:
        print("✅ Private key loaded successfully")
        print("✅ Environment setup is working")
        return True
    else:
        print("❌ Could not load private key")
        print("❌ Check that your .env file exists and contains PRIVATE_KEY=your_key")
        return False

if __name__ == "__main__":
    test_wallet_setup()