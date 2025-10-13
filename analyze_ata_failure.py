#!/usr/bin/env python3
"""
Detailed analysis of the specific failed transaction
"""

import requests
import json

def analyze_ata_creation_failure():
    """Analyze why the ATA creation failed"""
    
    signature = "oZMfyPibSGA6nhwAmj6J91DixsVZYgLUbdRW8nSomJsCbJUjNf41TCZX6KjiStjaWY5QxtckbCW6oxGpyuBSo1F"
    
    print("🔍 DETAILED ANALYSIS OF ATA CREATION FAILURE")
    print("=" * 80)
    
    try:
        rpc_url = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
        
        # Get transaction with full details
        response = requests.post(rpc_url, json={
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
        })
        
        data = response.json()
        tx = data['result']
        meta = tx.get('meta', {})
        
        print("❌ FAILURE ANALYSIS:")
        print(f"   Error: {meta.get('err', 'Unknown error')}")
        print()
        
        # Get the specific error details
        if 'err' in meta:
            error = meta['err']
            if isinstance(error, dict):
                if 'InstructionError' in error:
                    inst_index, inst_error = error['InstructionError']
                    print(f"📋 INSTRUCTION ERROR DETAILS:")
                    print(f"   Failed Instruction: #{inst_index}")
                    print(f"   Error Type: {inst_error}")
                    print()
        
        # Show the specific instruction that failed
        instructions = tx['transaction']['message']['instructions']
        if len(instructions) > 0:
            failed_inst = instructions[0]  # First instruction failed
            
            print("📝 FAILED INSTRUCTION DETAILS:")
            print(f"   Program: {failed_inst.get('programId', 'Unknown')}")
            
            if 'parsed' in failed_inst:
                parsed = failed_inst['parsed']
                print(f"   Type: {parsed.get('type', 'Unknown')}")
                print(f"   Info: {json.dumps(parsed.get('info', {}), indent=6)}")
            print()
        
        # Analyze the specific error
        print("🔬 ERROR INTERPRETATION:")
        if "Provided owner is not allowed" in str(meta.get('logMessages', [])):
            print("   ❌ 'Provided owner is not allowed' means:")
            print("      • The wallet trying to create the ATA is not authorized")
            print("      • This could be because:")
            print("        - Wrong wallet public key used")
            print("        - Incorrect authority/owner specified")
            print("        - Token mint might have restrictions")
            print()
            
            print("🔧 POTENTIAL FIXES:")
            print("   1. Verify the wallet public key is correct")
            print("   2. Check if the token mint allows your wallet")
            print("   3. Ensure the ATA derivation uses the right owner")
            print("   4. Check if this is a restricted/frozen token")
        
        print()
        print("🎯 NEXT STEPS:")
        print("   • Check which wallet is being used in the transaction")
        print("   • Verify the ATA derivation logic")
        print("   • Confirm the token mint allows transfers")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_ata_creation_failure()
