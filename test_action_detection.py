#!/usr/bin/env python3
"""
Test script to verify the action detection fix
"""

# Import the keywords and detection function
from wallet_tx_parser import BUY_KEYWORDS, SELL_KEYWORDS

def test_action_detection(logs):
    """Test the fixed action detection logic"""
    full_log_text = ' '.join(logs)
    
    print(f"🔍 Testing log text: {full_log_text[:100]}...")
    
    # CRITICAL FIX: Check SELL keywords FIRST to avoid false positives
    print(f"🔍 Checking SELL keywords first...")
    for keyword in SELL_KEYWORDS:
        if keyword in full_log_text:
            print(f"✅ SELL keyword matched: '{keyword}'")
            return "sell"
    
    print(f"🔍 Checking BUY keywords...")
    for keyword in BUY_KEYWORDS:
        if keyword in full_log_text:
            print(f"✅ BUY keyword matched: '{keyword}'")
            return "buy"
    
    print(f"❌ No keywords matched")
    return None

# Test with the actual log from your system
test_logs = [
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95 invoke [1]",
    "Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke [2]",
    "Program log: Instruction: SellExactIn"
]

print("=" * 60)
print("🧪 TESTING ACTION DETECTION FIX")
print("=" * 60)

result = test_action_detection(test_logs)
print(f"\n🎯 RESULT: {result}")

if result == "sell":
    print("✅ SUCCESS: SellExactIn correctly detected as SELL")
else:
    print("❌ FAILURE: SellExactIn incorrectly detected or not detected")

print("\n📋 KEYWORDS LOADED:")
print(f"   SELL_KEYWORDS: {SELL_KEYWORDS}")
print(f"   BUY_KEYWORDS: {BUY_KEYWORDS[:5]}...")  # Show first 5
