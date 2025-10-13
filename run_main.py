#!/usr/bin/env python3
"""
Simple wrapper to run the main trading script and catch any errors
"""
import sys
import os
import subprocess
import traceback

def run_main_script():
    """Run the main trading script"""
    script_path = "1_raydium_cpmm_trade_cycle_fixed_v2.py"
    python_path = "./hopeII/bin/python"
    
    print("=" * 60)
    print("RUNNING RAYDIUM CPMM TRADING BOT")
    print("=" * 60)
    print(f"Script: {script_path}")
    print(f"Python: {python_path}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60)
    
    try:
        # Run the script
        result = subprocess.run([python_path, script_path], 
                              capture_output=True, 
                              text=True,
                              timeout=60)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Script execution timed out (60 seconds)")
        return False
    except Exception as e:
        print(f"Error running script: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_main_script()
    sys.exit(0 if success else 1)
