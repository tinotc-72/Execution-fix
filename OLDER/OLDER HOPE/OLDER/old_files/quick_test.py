# quick_test.py
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv installed successfully")
    
    import os
    load_dotenv()
    print("✅ .env loading capability verified")
    
    # Test if .env is readable
    if os.getenv('BULLX_NEO_PRIVATE_KEY_QM'):
        print("✅ .env file found and readable")
    else:
        print("❌ .env file not found or BULLX_NEO_PRIVATE_KEY_QM not set")
        
except ImportError:
    print("❌ python-dotenv not installed. Run: pip install python-dotenv")