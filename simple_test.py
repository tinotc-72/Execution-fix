#!/usr/bin/env python3
"""
Simple test to identify what's causing the hang
"""

import asyncio
import logging
from datetime import datetime

print("🔧 Starting simple test...")

# Test 1: Basic imports
print("📦 Testing basic imports...")
try:
    import time
    import traceback
    import signal
    print("✅ Basic imports OK")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")

# Test 2: Solana imports
print("📦 Testing Solana imports...")
try:
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
    print("✅ Solana imports OK")
except Exception as e:
    print(f"❌ Solana imports failed: {e}")

# Test 3: Local file imports
print("📦 Testing local imports...")

# Test config.py
try:
    print("   Testing config.py...")
    from config import WALLET
    print("   ✅ config.py imported successfully")
except Exception as e:
    print(f"   ❌ config.py failed: {e}")

# Test env_keys.py
try:
    print("   Testing env_keys.py...")
    from env_keys import EnvKeys
    print("   ✅ env_keys.py imported successfully")
except Exception as e:
    print(f"   ❌ env_keys.py failed: {e}")

# Test wallet_tx_parser.py
try:
    print("   Testing wallet_tx_parser.py...")
    from wallet_tx_parser import create_websocket_monitor
    print("   ✅ wallet_tx_parser.py imported successfully")
except Exception as e:
    print(f"   ❌ wallet_tx_parser.py failed: {e}")

# Test official_executor_wrappers.py
try:
    print("   Testing official_executor_wrappers.py...")
    from official_executor_wrappers import initialize_executors
    print("   ✅ official_executor_wrappers.py imported successfully")
except Exception as e:
    print(f"   ❌ official_executor_wrappers.py failed: {e}")

print("🎯 Test completed! Check which imports failed.")
