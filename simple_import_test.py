#!/usr/bin/env python3
"""
Simple test to check what's happening
"""

print("=== SIMPLE TEST START ===")

try:
    print("Testing imports...")
    import sys
    print(f"Python version: {sys.version}")
    
    import os
    print(f"Current directory: {os.getcwd()}")
    
    print("Trying to import config...")
    from config import WALLET
    print("✅ Config imported successfully")
    
    print("Trying to import env_keys...")
    from env_keys import EnvKeys
    print("✅ EnvKeys imported successfully")
    
    print("Trying to import jupiter_copy_executor...")
    from jupiter_copy_executor import JupiterCopyExecutor
    print("✅ JupiterCopyExecutor imported successfully")
    
    print("=== ALL IMPORTS SUCCESSFUL ===")
    
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    print(f"❌ Traceback: {traceback.format_exc()}")

print("=== SIMPLE TEST END ===")
