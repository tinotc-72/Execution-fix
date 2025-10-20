#!/usr/bin/env python3
"""
Demonstration of the dynamic cloner mode implementation.

This script shows how the use_universal_cloner flag is dynamically set
based on field completeness after parsing and inference.
"""

def simulate_trade_processing(trade_info):
    """Simulate the dynamic mode logic from main.py"""
    print(f"\n{'='*80}")
    print(f"Processing Trade:")
    print(f"  dex: {trade_info.get('dex')}")
    print(f"  action: {trade_info.get('action')}")
    print(f"  token_mint: {trade_info.get('token_mint', 'None')[:50] if trade_info.get('token_mint') else 'None'}...")
    
    # This is the exact logic from main.py after inference
    have_all = all(trade_info.get(k) not in (None, "", "unknown", "PENDING_ANALYSIS")
                   for k in ("dex", "action", "token_mint"))
    
    if have_all:
        use_universal_cloner = False
        mode_msg = "✅ [MODE] Builders enabled (complete fields). Cloner kept as fallback."
    else:
        use_universal_cloner = True
        mode_msg = "ℹ️ [MODE] Universal Cloner mode active (incomplete fields)."
    
    trade_info["use_universal_cloner"] = use_universal_cloner
    
    print(f"\n{mode_msg}")
    print(f"  use_universal_cloner = {use_universal_cloner}")
    print(f"{'='*80}")
    
    return trade_info

def main():
    print("\n" + "🎯"*40)
    print("DYNAMIC CLONER MODE DEMONSTRATION")
    print("🎯"*40)
    
    # Scenario 1: Complete Meteora swap (after parsing + inference)
    print("\n📋 SCENARIO 1: Complete Meteora Swap")
    print("After parsing detects Meteora program ID and inference extracts all fields:")
    trade1 = {
        "dex": "meteora",
        "action": "swap",
        "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "signature": "5xyz..."
    }
    result1 = simulate_trade_processing(trade1)
    print(f"\n➡️ Result: Builder path will be used (Meteora executor)")
    print(f"   The Meteora build_and_sign will construct the swap transaction")
    
    # Scenario 2: Unknown DEX with token mint
    print("\n\n📋 SCENARIO 2: Unknown DEX but with Token Mint")
    print("Parser couldn't identify DEX, but token mint was extracted:")
    trade2 = {
        "dex": "unknown",
        "action": "swap",
        "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "signature": "5abc..."
    }
    result2 = simulate_trade_processing(trade2)
    print(f"\n➡️ Result: Universal cloner will be used")
    print(f"   Transaction will be cloned directly since DEX is unknown")
    
    # Scenario 3: Missing action
    print("\n\n📋 SCENARIO 3: Missing Action")
    print("DEX and token detected but action couldn't be inferred:")
    trade3 = {
        "dex": "raydium",
        "action": "unknown",
        "token_mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "signature": "5def..."
    }
    result3 = simulate_trade_processing(trade3)
    print(f"\n➡️ Result: Universal cloner will be used")
    print(f"   Since action is unknown, we can't build a transaction properly")
    
    # Scenario 4: PENDING_ANALYSIS token mint
    print("\n\n📋 SCENARIO 4: Token Mint Still Pending Analysis")
    print("DEX and action known but token mint extraction pending:")
    trade4 = {
        "dex": "jupiter",
        "action": "buy",
        "token_mint": "PENDING_ANALYSIS",
        "signature": "5ghi..."
    }
    result4 = simulate_trade_processing(trade4)
    print(f"\n➡️ Result: Universal cloner will be used")
    print(f"   Without token mint, we can't build a buy transaction")
    
    # Scenario 5: Complete Raydium buy
    print("\n\n📋 SCENARIO 5: Complete Raydium Buy")
    print("All fields successfully parsed and inferred:")
    trade5 = {
        "dex": "raydium",
        "action": "buy",
        "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "signature": "5jkl..."
    }
    result5 = simulate_trade_processing(trade5)
    print(f"\n➡️ Result: Builder path will be used (Raydium executor)")
    print(f"   The Raydium executor will construct an optimized buy transaction")
    
    print("\n\n" + "✨"*40)
    print("KEY INSIGHT:")
    print("The mode is now DYNAMIC - it adapts based on what information")
    print("could be successfully extracted from the transaction.")
    print("This prevents starving the builder path when we have complete data,")
    print("while still falling back to cloning when data is incomplete.")
    print("✨"*40 + "\n")

if __name__ == "__main__":
    main()
