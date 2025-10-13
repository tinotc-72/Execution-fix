#!/usr/bin/env python3
"""
Threshold Impact Analysis: Check if 71% threshold affects buy detection
"""

async def check_buy_impact():
    """Check if 71% threshold would still correctly detect buys"""
    
    print("🔍 THRESHOLD IMPACT ANALYSIS")
    print("=" * 50)
    
    # Your confirmed buy transfer positions from previous analysis
    buy_positions = [
        66.67,  # 4TMgVbpTY83d... (3 identical buys)
        66.67,  # 2CDKCDhzUjKK...
        66.67,  # UDUp8Z5FA8HP...
        73.21   # 3zpcyXDudoSh...
    ]
    
    # Current sell data (all positions)
    original_sell_positions = [62.96] * 7  # Original 7 sells
    new_sell_positions = [62.96, 70.00, 70.00, 70.00, 70.00, 62.96, 62.96, 70.00, 70.00, 68.75]  # New sells
    
    all_sell_positions = original_sell_positions + new_sell_positions
    
    current_threshold = 65.63
    proposed_threshold = 71.00
    
    print(f"📈 BUY ANALYSIS:")
    print(f"   Positions: {buy_positions}")
    print(f"   Range: {min(buy_positions):.2f}% - {max(buy_positions):.2f}%")
    print(f"   Average: {sum(buy_positions)/len(buy_positions):.2f}%")
    
    print(f"\n📉 SELL ANALYSIS:")
    print(f"   Total sells: {len(all_sell_positions)}")
    print(f"   Range: {min(all_sell_positions):.2f}% - {max(all_sell_positions):.2f}%")
    print(f"   Average: {sum(all_sell_positions)/len(all_sell_positions):.2f}%")
    
    # Check current threshold performance
    print(f"\n🎯 CURRENT THRESHOLD (65.63%):")
    buys_correct_current = sum(1 for pos in buy_positions if pos > current_threshold)
    sells_correct_current = sum(1 for pos in all_sell_positions if pos <= current_threshold)
    
    total_correct_current = buys_correct_current + sells_correct_current
    total_transactions = len(buy_positions) + len(all_sell_positions)
    accuracy_current = (total_correct_current / total_transactions) * 100
    
    print(f"   Buys correct: {buys_correct_current}/{len(buy_positions)} ({buys_correct_current/len(buy_positions)*100:.1f}%)")
    print(f"   Sells correct: {sells_correct_current}/{len(all_sell_positions)} ({sells_correct_current/len(all_sell_positions)*100:.1f}%)")
    print(f"   Overall accuracy: {accuracy_current:.1f}%")
    
    # Check proposed threshold performance
    print(f"\n🎯 PROPOSED THRESHOLD (71.00%):")
    buys_correct_proposed = sum(1 for pos in buy_positions if pos > proposed_threshold)
    sells_correct_proposed = sum(1 for pos in all_sell_positions if pos <= proposed_threshold)
    
    total_correct_proposed = buys_correct_proposed + sells_correct_proposed
    accuracy_proposed = (total_correct_proposed / total_transactions) * 100
    
    print(f"   Buys correct: {buys_correct_proposed}/{len(buy_positions)} ({buys_correct_proposed/len(buy_positions)*100:.1f}%)")
    print(f"   Sells correct: {sells_correct_proposed}/{len(all_sell_positions)} ({sells_correct_proposed/len(all_sell_positions)*100:.1f}%)")
    print(f"   Overall accuracy: {accuracy_proposed:.1f}%")
    
    # Analysis
    print(f"\n📊 ANALYSIS:")
    if buys_correct_proposed == len(buy_positions):
        print(f"   ✅ All buys still detected correctly with 71% threshold")
    else:
        missed_buys = [pos for pos in buy_positions if pos <= proposed_threshold]
        print(f"   ❌ Would miss {len(missed_buys)} buys: {missed_buys}")
    
    if sells_correct_proposed == len(all_sell_positions):
        print(f"   ✅ All sells correctly detected with 71% threshold")
    else:
        missed_sells = [pos for pos in all_sell_positions if pos > proposed_threshold]
        print(f"   ❌ Would still miss {len(missed_sells)} sells: {missed_sells}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if accuracy_proposed > accuracy_current:
        improvement = accuracy_proposed - accuracy_current
        print(f"   🟢 71% threshold improves accuracy by {improvement:.1f}%")
        print(f"   🔧 RECOMMENDED: Update threshold to 71.00%")
    else:
        print(f"   🔴 71% threshold doesn't solve the problem completely")
        print(f"   🔧 RECOMMENDED: Use multi-criteria detection logic")
    
    # Show distribution
    print(f"\n📈 POSITION DISTRIBUTION:")
    all_positions = buy_positions + all_sell_positions
    all_types = ['BUY'] * len(buy_positions) + ['SELL'] * len(all_sell_positions)
    
    # Sort by position
    sorted_data = sorted(zip(all_positions, all_types))
    
    print(f"   {'Position':<10} {'Type':<6} {'Threshold':<12}")
    print(f"   {'-'*10} {'-'*6} {'-'*12}")
    
    for pos, typ in sorted_data:
        current_result = ">" if pos > current_threshold else "≤"
        proposed_result = ">" if pos > proposed_threshold else "≤"
        print(f"   {pos:7.2f}%   {typ:<6} Current:{current_result}65.63 Proposed:{proposed_result}71.00")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_buy_impact())
