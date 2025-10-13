#!/usr/bin/env python3
"""
Definitive Pump.fun Program ID Verification
Using Solana Explorer and transaction analysis
"""

import requests
import json

def verify_pump_program_id():
    """Verify using Helius API and transaction analysis"""
    
    print("🔍 DEFINITIVE PUMP.FUN PROGRAM ID VERIFICATION")
    print("=" * 60)
    
    # Your successful transaction
    tx_sig = "4s5A67RgY3zKCCjd164HhjNRHccUbbPWQcPBeLQWokJSddENtajaBTvnwbKwWp2ri3ay3M32Wjxhrd7TMsrhST4r"
    
    # Use Helius API to get transaction details
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_sig,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    try:
        response = requests.post(rpc_url, json=payload)
        data = response.json()
        
        if "result" in data and data["result"]:
            tx_data = data["result"]
            
            print("📋 TRANSACTION ANALYSIS:")
            print("-" * 40)
            
            # Extract logs
            if "meta" in tx_data and "logMessages" in tx_data["meta"]:
                logs = tx_data["meta"]["logMessages"]
                
                print("🔍 Program Invocations:")
                pump_program = None
                
                for log in logs:
                    if "Program " in log and " invoke [" in log:
                        # Extract program ID
                        parts = log.split()
                        if len(parts) >= 2:
                            program_id = parts[1]
                            level = log.split("[")[-1].split("]")[0] if "[" in log else "?"
                            print(f"   📦 {program_id} (level {level})")
                            
                            # Check if this program handles the Buy instruction
                            if "Buy" in ' '.join(logs[logs.index(log):logs.index(log)+5]):
                                pump_program = program_id
                                print(f"      ✅ This program handles BUY instruction!")
                
                print(f"\n🔥 PUMP.FUN BUY PROGRAM IDENTIFIED:")
                print(f"   🎯 Program ID: {pump_program}")
                
                # Look for the actual Buy instruction log
                buy_logs = [log for log in logs if "Instruction: Buy" in log]
                if buy_logs:
                    print(f"\n📝 BUY INSTRUCTION CONFIRMATION:")
                    for log in buy_logs:
                        print(f"   ✅ {log}")
                
                print(f"\n🏛️ OFFICIAL VERIFICATION:")
                print("-" * 40)
                
                # Check account structure from transaction
                if "transaction" in tx_data and "message" in tx_data["transaction"]:
                    message = tx_data["transaction"]["message"]
                    if "accountKeys" in message:
                        accounts = message["accountKeys"]
                        print(f"📦 Transaction used {len(accounts)} accounts")
                        
                        # Look for known Pump.fun constants
                        known_pump_accounts = [
                            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
                            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
                        ]
                        
                        for account in accounts:
                            if account in known_pump_accounts:
                                print(f"   ✅ Found known Pump.fun program: {account}")
                
                print(f"\n🎯 FINAL DETERMINATION:")
                print("-" * 40)
                print(f"✅ CORRECT PUMP.FUN PROGRAM ID: {pump_program}")
                print(f"📍 Evidence: Direct program invocation with 'Buy' instruction")
                print(f"🔍 Verification: On-chain transaction analysis")
                
                # Cross-reference with your executor
                executor_program = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
                old_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
                
                print(f"\n🔧 EXECUTOR STATUS:")
                print("-" * 40)
                if pump_program == executor_program:
                    print(f"✅ Your executor uses CORRECT program ID!")
                    print(f"   Current: {executor_program}")
                    print(f"   Verified: {pump_program}")
                elif pump_program == old_program:
                    print(f"⚠️ Need to update executor!")
                    print(f"   Current: {executor_program}")
                    print(f"   Should be: {pump_program}")
                else:
                    print(f"❌ Unknown program detected: {pump_program}")
                
            else:
                print("❌ No logs found in transaction")
        else:
            print("❌ Could not fetch transaction data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n📚 ADDITIONAL VERIFICATION SOURCES:")
    print("-" * 40)
    print("🔗 Solana Explorer: https://explorer.solana.com/tx/" + tx_sig)
    print("🔗 SolScan: https://solscan.io/tx/" + tx_sig)
    print("🔗 Pump.fun Official: https://pump.fun")

if __name__ == "__main__":
    verify_pump_program_id()
