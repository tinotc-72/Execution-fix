#!/usr/bin/env python3
"""
Comprehensive diagnostic script to test the trading bot environment
"""
import sys
import os
import subprocess
import traceback
from pathlib import Path

def test_python_version():
    """Test Python version and executable"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[:3]}...")
    return True

def test_working_directory():
    """Test current working directory"""
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Check if the main script exists
    main_script = Path("1_raydium_cpmm_trade_cycle_fixed_v2.py")
    if main_script.exists():
        print(f"✓ Main script found: {main_script.absolute()}")
        return True
    else:
        print(f"✗ Main script not found: {main_script.absolute()}")
        return False

def test_environment_file():
    """Test .env file"""
    env_file = Path(".env")
    if env_file.exists():
        print(f"✓ .env file found: {env_file.absolute()}")
        return True
    else:
        print(f"✗ .env file not found: {env_file.absolute()}")
        return False

def test_basic_imports():
    """Test basic Python imports"""
    try:
        import asyncio
        import time
        import struct
        import logging
        print("✓ Basic imports successful")
        return True
    except ImportError as e:
        print(f"✗ Basic imports failed: {e}")
        return False

def test_env_keys_import():
    """Test env_keys module import"""
    try:
        from env_keys import load_wallet_from_private_key, validate_env_vars
        print("✓ env_keys import successful")
        return True
    except ImportError as e:
        print(f"✗ env_keys import failed: {e}")
        return False

def test_solana_imports():
    """Test Solana library imports"""
    try:
        from solders.pubkey import Pubkey
        from solders.keypair import Keypair
        from solana.rpc.async_api import AsyncClient
        from spl.token.instructions import get_associated_token_address
        print("✓ Solana imports successful")
        return True
    except ImportError as e:
        print(f"✗ Solana imports failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading"""
    try:
        from env_keys import validate_env_vars
        env_vars = validate_env_vars()
        print(f"✓ Environment variables loaded: {len(env_vars)} keys")
        return True
    except Exception as e:
        print(f"✗ Environment variables failed: {e}")
        return False

def test_script_syntax():
    """Test script syntax by compiling it"""
    try:
        script_path = "1_raydium_cpmm_trade_cycle_fixed_v2.py"
        with open(script_path, 'r') as f:
            content = f.read()
        compile(content, script_path, 'exec')
        print("✓ Script syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Script syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Script compilation failed: {e}")
        return False

def run_diagnosis():
    """Run comprehensive diagnosis"""
    print("=" * 60)
    print("RAYDIUM CPMM TRADING BOT DIAGNOSTIC")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Working Directory", test_working_directory),
        ("Environment File", test_environment_file),
        ("Basic Imports", test_basic_imports),
        ("env_keys Import", test_env_keys_import),
        ("Solana Imports", test_solana_imports),
        ("Environment Variables", test_environment_variables),
        ("Script Syntax", test_script_syntax),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    failed_tests = []
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            failed_tests.append(test_name)
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} tests failed:")
        for test in failed_tests:
            print(f"  - {test}")
        print("\nThe script may not run correctly until these issues are resolved.")
    else:
        print("\n✅ All tests passed! The script should be able to run.")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    try:
        success = run_diagnosis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Diagnostic failed: {e}")
        traceback.print_exc()
        sys.exit(1)
