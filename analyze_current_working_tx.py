#!/usr/bin/env python3

import requests
import json
import base58
from datetime import datetime

def analyze_working_transactions():
    """Get actual working instruction data from recent successful transactions"""
    
    # Recent successful Pump.fun transaction signatures
    working_signatures = [
        '12cr5UibELxtm1L6QNAumD9u35Ai1CHLnPD2R7bLCQLTQv8cE5YCfKudqYEF12RmBBMwgihajGrmfz2Jd1AKhEP',
        '1HCGXK797SD6JM2eroyqz7ZdpZbAH3hA9sG3fQj1KP5YnxcREh8LDrCt8AiQuSmhBJqmfxMeR8Uo7dMa9vXYr8Q',
        '2QuLosLic46DFXKfgH8s9VzJwrU6oP3KjC3d1YKWEf9qHS2LzVNr8m4bZ7XgA6pPkE9TcL5DyRMvFnS8bQcXeV',
        '5Xp5nJC3rJHWWf1CF8ajMPiVGwuEFv9nqPNFh2jL8RpD6BwdU28VkJhFADsw54qTDt2koAHHMbq1sYWnMoouX6YT'
    ]
    
    print("🔍 ANALYZING WORKING PUMP.FUN TRANSACTIONS")
    print("=" * 60)
    
    instruction_patterns = {}
    
    for i, signature in enumerate(working_signatures):
        try:
            print(f"\n📋 Transaction {i+1}: {signature}")
            
            # Get transaction details
            url = f"https://api.helius.xyz/v0/transactions/{signature}?api-key=a9c41060-b6a2-466a-bfa9-7b16677f8da5"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"   ❌ API Error: {response.status_code}")
                continue
                
            tx_data = response.json()
            
            # Extract transaction details
            block_time = tx_data.get('blockTime', 0)
            if block_time:
                timestamp = datetime.fromtimestamp(block_time)
                print(f"   ⏰ Time: {timestamp}")
            
            instructions = tx_data.get('transaction', {}).get('message', {}).get('instructions', [])
            
            # Find all program instructions
            for j, instruction in enumerate(instructions):
                program_id = instruction.get('programId')
                instruction_data = instruction.get('data', '')
                
                if program_id == '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P':  # Direct Pump.fun
                    print(f"   🎯 PUMP.FUN INSTRUCTION {j}:")
                    print(f"      Base58: {instruction_data}")
                    
                    try:
                        hex_data = base58.b58decode(instruction_data).hex()
                        print(f"      Hex:    {hex_data}")
                        
                        if hex_data not in instruction_patterns:
                            instruction_patterns[hex_data] = []
                        instruction_patterns[hex_data].append(signature)
                        
                    except Exception as decode_error:
                        print(f"      ❌ Decode error: {decode_error}")
                
                elif program_id == 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4':  # Jupiter
                    print(f"   🚀 JUPITER INSTRUCTION {j}:")
                    print(f"      Base58: {instruction_data}")
                    
                    try:
                        hex_data = base58.b58decode(instruction_data).hex()
                        print(f"      Hex:    {hex_data}")
                    except:
                        print(f"      ❌ Could not decode Jupiter data")
                        
                elif program_id == 'ComputeBudget111111111111111111111111111111':
                    print(f"   💰 COMPUTE BUDGET {j}: {instruction_data}")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing transaction: {e}")
    
    print("\n" + "=" * 60)
    print("📊 INSTRUCTION PATTERN SUMMARY")
    print("=" * 60)
    
    for pattern, signatures in instruction_patterns.items():
        print(f"\n🔑 Pattern: {pattern}")
        print(f"   Used in {len(signatures)} transactions:")
        for sig in signatures:
            print(f"   - {sig}")
    
    # Compare with our current implementation
    print("\n" + "=" * 60)
    print("🔧 COMPARISON WITH OUR IMPLEMENTATION")
    print("=" * 60)
    
    our_current = "000b9a530600000000ef0e483a8f000000"
    our_old = "00bdda4598000000004586f554dc040000"
    
    print(f"Our OLD data:     {our_old}")
    print(f"Our CURRENT data: {our_current}")
    
    if our_current in instruction_patterns:
        print(f"✅ Our current data MATCHES working transactions!")
    else:
        print(f"❌ Our current data does NOT match any working patterns")
        print(f"🎯 RECOMMENDED patterns from analysis:")
        for pattern in instruction_patterns.keys():
            print(f"   - {pattern}")

if __name__ == "__main__":
    analyze_working_transactions()
