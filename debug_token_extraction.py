#!/usr/bin/env python3
"""
Debug script to analyze the differences between BUY and SELL transaction logs
"""

# Mock data from your terminal logs to understand the pattern
buy_transaction_logs_sample = [
    "Program 11111111111111111111111111111111 invoke [1]",
    "Program 11111111111111111111111111111111 success", 
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    # ... more logs that we don't see in terminal
]

sell_transaction_logs_sample = [
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95 invoke [1]",  # TOKEN MINT!
    "Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]",
    "Program log: Instruction: SellExactIn"
]

def analyze_logs(logs, transaction_type):
    print(f"\n🔍 ANALYZING {transaction_type} TRANSACTION:")
    print(f"   📊 Log count: {len(logs)}")
    
    # Extract potential token addresses
    import re
    full_log_text = ' '.join(logs)
    token_matches = re.findall(r'\b[A-Za-z0-9]{32,44}\b', full_log_text)
    
    print(f"   🔍 Found {len(token_matches)} potential token addresses:")
    for i, token in enumerate(token_matches):
        print(f"      {i+1}: {token[:8]}...{token[-8:]}")
    
    # System addresses to skip (same as in your code)
    system_addresses = {
        "So11111111111111111111111111111111111111112",
        "11111111111111111111111111111111", 
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "ComputeBudget111111111111111111111111111111",
        "SysvarRent111111111111111111111111111111111",
        "SysvarC1ock11111111111111111111111111111111",
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
        "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
        "Sysvar1nstructions1111111111111111111111111",
        "SysvarEpochSchedu1e111111111111111111111111",
        "SysvarRecentB1ockHashes11111111111111111111",
        "TokenkegQfeZNn4nqN6bD5Z2PBZKUeEXweCg4n2XcCxKa",
    }
    
    # Find valid tokens
    valid_tokens = []
    for token in token_matches:
        if (len(token) >= 32 and 
            token not in system_addresses and
            not any(sys_part in token for sys_part in ['111111111111', 'SysvarRent', 'ComputeBudget', 'TokenkegQ'])):
            
            is_likely_meme_coin = (
                len(token) in [43, 44] and
                not token.endswith('111111111111') and
                not token.startswith('Sysvar') and
                token != "So11111111111111111111111111111111111111112"
            )
            
            if is_likely_meme_coin:
                valid_tokens.append(token)
                print(f"      ✅ Valid token candidate: {token[:8]}...{token[-8:]}")
    
    if valid_tokens:
        print(f"   🎯 Selected token mint: {valid_tokens[0][:8]}...{valid_tokens[0][-8:]}")
        return valid_tokens[0]
    else:
        print(f"   ❌ No valid meme coin token mints found")
        return None

print("🧪 DEBUGGING TOKEN MINT EXTRACTION")
print("=" * 60)

# Analyze SELL transaction (working)
sell_result = analyze_logs(sell_transaction_logs_sample, "SELL")

# Analyze BUY transaction (failing)  
buy_result = analyze_logs(buy_transaction_logs_sample, "BUY")

print(f"\n🎯 ANALYSIS RESULTS:")
print(f"   SELL extraction: {'✅ SUCCESS' if sell_result else '❌ FAILED'}")
print(f"   BUY extraction: {'✅ SUCCESS' if buy_result else '❌ FAILED'}")

print(f"\n💡 DIAGNOSIS:")
print(f"   The key difference is that SELL transactions have:")
print(f"   🔑 Program BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95 invoke [1]")
print(f"   This IS the token mint address!")
print(f"   ")
print(f"   BUY transactions might have similar patterns but in different logs")
print(f"   that we're not seeing in the terminal output (truncated logs)")
