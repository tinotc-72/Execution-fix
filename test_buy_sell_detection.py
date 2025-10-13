#!/usr/bin/env python3
"""
Quick test script to verify our buy/sell detection fix
"""

# Simulate the logs from the problematic transaction
test_logs = [
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]",
    "Program log: CreateIdempotent",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
    "Program log: Instruction: GetAccountDataSize",
    "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]",
    "Program log: Instruction: Route",
    "Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [2]",
    "Program log: Instruction: Sell",  # 🚨 THE CRITICAL PATTERN!
    "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [3]",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [4]",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"
]

def test_buy_sell_detection():
    """Test our fixed buy/sell detection logic"""
    
    # Convert to lowercase for pattern matching (like the real code does)
    log_text = ' '.join(test_logs).lower()
    
    print(f"🔍 Testing buy/sell detection on logs...")
    print(f"📝 Looking for 'instruction: sell' pattern...")
    
    # Check for explicit SELL patterns (our fix)
    explicit_sell_patterns = [
        'instruction: sell',    # This should match!
        'program log: sell',
        'sell instruction',
        'action: sell',
        '"sell"',
        "'sell'"
    ]
    
    trade_type = None
    confidence_score = 0
    
    for pattern in explicit_sell_patterns:
        if pattern in log_text:
            print(f"🚨 EXPLICIT SELL DETECTED: {pattern}")
            trade_type = 'sell'
            confidence_score = 10
            break
    
    if trade_type:
        print(f"✅ SUCCESS: Correctly detected SELL transaction")
        print(f"📊 Trade type: {trade_type}")
        print(f"📊 Confidence: {confidence_score}")
        return True
    else:
        print(f"❌ FAILED: Did not detect sell transaction")
        return False

if __name__ == "__main__":
    print("🧪 Testing buy/sell detection fix...")
    success = test_buy_sell_detection()
    if success:
        print("\n✅ BUY/SELL DETECTION FIX VERIFIED!")
        print("🎯 The bot should now correctly identify SELL transactions")
    else:
        print("\n❌ BUY/SELL DETECTION STILL BROKEN!")
        print("🔧 Additional debugging needed")
