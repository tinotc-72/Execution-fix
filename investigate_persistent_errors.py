#!/usr/bin/env python3
"""
Deep investigation: Why are IllegalOwner errors still happening?
Let's trace exactly what code path is being used
"""

import requests
import json

def investigate_persistent_errors():
    print("🔬 DEEP INVESTIGATION: Persistent IllegalOwner Errors")
    print("=" * 80)
    
    # Get details of the most recent failed transaction
    signature = "pMdL9nKZNGfu3ydwkPL173hPG5jiLsRg7c7W1Wy5Np8xJZGj7kvwCTDF2gc1t37UPxsWeXTPNn3ApbTVZHCLSDa"
    rpc_url = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"🔍 Analyzing failed transaction: {signature[:20]}...")
    print()
    
    # Get transaction details
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0,
                "commitment": "confirmed"
            }
        ]
    }
    
    try:
        response = requests.post(rpc_url, json=payload)
        data = response.json()
        
        if "result" not in data or not data["result"]:
            print("❌ Could not fetch transaction details")
            return
        
        tx = data["result"]
        meta = tx.get("meta", {})
        instructions = tx["transaction"]["message"]["instructions"]
        
        print("📊 TRANSACTION ANALYSIS:")
        print(f"   Status: ❌ FAILED")
        print(f"   Error: {meta.get('err')}")
        print(f"   Instructions: {len(instructions)}")
        print()
        
        print("📝 INSTRUCTION BREAKDOWN:")
        for i, inst in enumerate(instructions):
            program_id = inst.get("programId", "Unknown")
            parsed = inst.get("parsed", {})
            
            print(f"   Instruction {i}: {program_id}")
            if parsed:
                inst_type = parsed.get("type", "Unknown")
                print(f"      Type: {inst_type}")
                if inst_type == "create":
                    print(f"      🚨 ATA CREATION DETECTED - This is the problem!")
                    info = parsed.get("info", {})
                    print(f"      Account: {info.get('account', 'Unknown')[:20]}...")
                    print(f"      Mint: {info.get('mint', 'Unknown')[:20]}...")
                    print(f"      Owner: {info.get('wallet', 'Unknown')[:20]}...")
            print()
        
        print("🔍 LOG ANALYSIS:")
        logs = meta.get("logMessages", [])
        for log in logs:
            if "IllegalOwner" in log or "Provided owner is not allowed" in log:
                print(f"   🚨 {log}")
        print()
        
        print("💡 CONCLUSION:")
        print("   The bot is STILL trying to create ATAs that already exist")
        print("   This means:")
        print("   • Our ATA existence checking is NOT being called")
        print("   • The bot is using a different code path")
        print("   • There might be multiple ATA creation locations")
        print()
        
        print("🎯 HYPOTHESIS:")
        print("   The bot might be using:")
        print("   • A cached version of the old code")
        print("   • A different import path we didn't fix")
        print("   • Direct ATA creation without going through our fixed methods")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_running_processes():
    print("\n" + "="*50)
    print("🔍 CHECKING WHAT'S ACTUALLY RUNNING")
    print("="*50)
    
    import subprocess
    
    # Check if there are multiple bot processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        python_processes = [line for line in lines if 'python' in line and 'main.py' in line]
        
        print(f"🤖 Found {len(python_processes)} bot processes:")
        for i, process in enumerate(python_processes, 1):
            print(f"   {i}. {process.strip()}")
        
        if len(python_processes) > 1:
            print("\n🚨 MULTIPLE BOT PROCESSES DETECTED!")
            print("   This could cause conflicts and use old code")
            print("   Recommendation: Kill all and start fresh")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

if __name__ == "__main__":
    investigate_persistent_errors()
    check_running_processes()
