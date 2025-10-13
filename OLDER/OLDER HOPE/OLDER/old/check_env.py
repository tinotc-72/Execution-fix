"""
Environment File Checker
Created: 2025-06-19 00:46:00 UTC
Author: tinotc-72
"""

import os
from dotenv import load_dotenv

def check_env_file():
    # Get the absolute path to your .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    
    print("\n=== .env File Check ===")
    
    # Check if .env file exists
    if not os.path.exists(env_path):
        print(f"❌ ERROR: No .env file found at {env_path}")
        return
    
    print(f"✅ Found .env file at: {env_path}")
    
    # Read the raw contents of the .env file
    print("\nRaw contents of .env file:")
    print("-" * 50)
    with open(env_path, 'r') as f:
        for line in f:
            # If line contains 'PRIVATE' or 'KEY', mask the value
            if 'PRIVATE' in line.upper() or 'KEY' in line.upper():
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    masked_value = value[:4] + '*' * (len(value.strip()) - 8) + value.strip()[-4:]
                    print(f"{key}={masked_value}")
            else:
                print(line.rstrip())
    print("-" * 50)
    
    # Load and check environment variables
    load_dotenv()
    
    print("\nChecking BULLX_NEO_PRIVATE_KEY_QM:")
    key = os.getenv('BULLX_NEO_PRIVATE_KEY_QM')
    if key:
        print(f"Length: {len(key)} characters")
        print(f"First 4 chars: {key[:4]}")
        print(f"Last 4 chars: {key[-4:]}")
        print("Contains spaces: ", 'Yes' if ' ' in key else 'No')
        print("Contains quotes: ", 'Yes' if '"' in key or "'" in key else 'No')
        print("Contains hyphens: ", 'Yes' if '-' in key else 'No')
    else:
        print("❌ BULLX_NEO_PRIVATE_KEY_QM not found in environment")

if __name__ == "__main__":
    check_env_file()