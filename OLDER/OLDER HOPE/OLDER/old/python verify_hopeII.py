# verify_hopeII.py
import os
import sys
from datetime import datetime, timezone

def verify_hopeII():
    print("\n🔍 HopeII Environment Verification")
    print("=" * 50)
    
    # Check timestamp
    utc_now = datetime.now(timezone.utc)
    print(f"\nVerification Time (UTC): {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: tinotc-72")
    
    # Environment paths
    print("\nEnvironment Paths:")
    print(f"Python: {sys.executable}")
    print(f"Virtual env: {os.environ.get('VIRTUAL_ENV')}")
    
    # Verify it's named hopeII
    venv_name = os.path.basename(os.environ.get('VIRTUAL_ENV', ''))
    if venv_name == 'hopeII':
        print("\n✅ Correctly using hopeII environment")
    else:
        print(f"\n❌ Wrong environment: {venv_name}")
    
    # Check critical packages
    packages = {
        'dotenv': 'python-dotenv for configuration',
        'base58': 'base58 for key encoding',
        'solders': 'solders for Solana operations'
    }
    
    print("\nPackage Verification:")
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package} installed - {description}")
        except ImportError:
            print(f"❌ {package} missing - {description}")
    
    # Check .env file
    print("\nConfiguration:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'BULLX_NEO_PRIVATE_KEY_QM',
            'HELIUS_RPC_URL',
            'HELIUS_Standard_Websocket_URL',
            'JITO_UUID'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if not missing:
            print("✅ All required environment variables found")
        else:
            print("⚠️  Missing environment variables:")
            for var in missing:
                print(f"  - {var}")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")

if __name__ == "__main__":
    verify_hopeII()