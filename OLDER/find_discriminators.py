#!/usr/bin/env python3
"""
Find the correct sell discriminator by examining known pump.fun transactions directly
"""

import asyncio
import base64
import logging
import json
import hashlib

# Common instruction names and their potential discriminators
ANCHOR_DISCRIMINATORS = {
    # Standard Anchor discriminators for common instruction names
    "buy": hashlib.sha256(b"global:buy").digest()[:8].hex(),
    "sell": hashlib.sha256(b"global:sell").digest()[:8].hex(),
    "swap": hashlib.sha256(b"global:swap").digest()[:8].hex(),
    "create": hashlib.sha256(b"global:create").digest()[:8].hex(),
    "initialize": hashlib.sha256(b"global:initialize").digest()[:8].hex(),
}

# Pump.fun might use different patterns
PUMP_DISCRIMINATORS = {
    # Try variations
    "pump_buy": hashlib.sha256(b"global:pump_buy").digest()[:8].hex(),
    "pump_sell": hashlib.sha256(b"global:pump_sell").digest()[:8].hex(),
    "trade_buy": hashlib.sha256(b"global:trade_buy").digest()[:8].hex(),
    "trade_sell": hashlib.sha256(b"global:trade_sell").digest()[:8].hex(),
    # Try without global prefix
    "buy_no_global": hashlib.sha256(b"buy").digest()[:8].hex(),
    "sell_no_global": hashlib.sha256(b"sell").digest()[:8].hex(),
}

# Known working buy discriminator
KNOWN_BUY = "66063d1201daebea"

def main():
    """Print potential discriminators"""
    print("🔍 POTENTIAL PUMP.FUN DISCRIMINATORS")
    print("=" * 50)
    
    print(f"Known BUY discriminator: {KNOWN_BUY}")
    print()
    
    print("Standard Anchor patterns:")
    for name, disc in ANCHOR_DISCRIMINATORS.items():
        print(f"  {name:12}: {disc}")
    
    print()
    print("Pump.fun specific patterns:")
    for name, disc in PUMP_DISCRIMINATORS.items():
        print(f"  {name:12}: {disc}")
    
    print()
    print("Manual calculations:")
    # Try some manual patterns that might be used by pump.fun
    manual_patterns = [
        "instruction:sell",
        "market:sell", 
        "token:sell",
        "pump:sell",
        "sell_tokens",
        "trade_sell",
        "sell_trade",
    ]
    
    for pattern in manual_patterns:
        disc = hashlib.sha256(pattern.encode()).digest()[:8].hex()
        print(f"  {pattern:15}: {disc}")
    
    # Special case: the current sell discriminator we're using might be wrong
    print(f"\nCurrent (wrong?) SELL: 33e685a4017f83ad")
    print(f"Current (wrong?) SELL: b712469c946da122")
    
    # Let's also try the discriminator that would be at offset +1 from buy
    try:
        buy_bytes = bytes.fromhex(KNOWN_BUY)
        buy_int = int.from_bytes(buy_bytes, 'little')
        sell_int = buy_int + 1
        sell_bytes = sell_int.to_bytes(8, 'little')
        sell_hex = sell_bytes.hex()
        print(f"\nBUY + 1 pattern:     {sell_hex}")
    except:
        pass
        
    # Also try reversing the buy discriminator
    try:
        buy_bytes = bytes.fromhex(KNOWN_BUY)
        reversed_bytes = buy_bytes[::-1]
        print(f"Reversed BUY:        {reversed_bytes.hex()}")
    except:
        pass

if __name__ == "__main__":
    main()
