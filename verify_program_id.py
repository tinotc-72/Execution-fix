#!/usr/bin/env python3
"""
Quick program ID verification from your logs
"""

def verify_program_id():
    print("🔍 PROGRAM ID VERIFICATION")
    print("=" * 50)
    
    print("From your bot logs (successful transaction 4s5A67Rg...):")
    print("Program: pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
    print()
    
    print("From your executor:")
    print("Program: 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    print()
    
    print("🎯 LOG EVIDENCE:")
    print("Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]")
    print("Program log: Instruction: Buy")
    print()
    
    print("✅ CORRECT PROGRAM ID: pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
    print("❌ WRONG PROGRAM ID: 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    print()
    print("🔧 Need to update PUMP_FUN_PROGRAM_ID in executor!")

if __name__ == "__main__":
    verify_program_id()
