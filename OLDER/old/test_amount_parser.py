#!/usr/bin/env python3

import asyncio
import logging
import json
import base64
import struct
from wallet_tx_parser import WalletATxParser
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_pump_instruction_data(amount_sol):
    """Create encoded Pump.fun instruction data"""
    # Convert SOL amount to lamports
    lamports = int(amount_sol * 1e9)
    logging.debug(f"Converting {amount_sol} SOL to {lamports} lamports")
    
    # Create instruction data:
    # - 8 bytes discriminator "PUMPBUY\x00"
    # - 32 bytes token mint (all FF for test)
    # - 8 bytes amount in lamports
    discriminator = b"PUMPBUY\x00"
    token_mint = b"\xFF" * 32
    amount_bytes = struct.pack("<Q", lamports)  # Little-endian uint64
    
    instruction_data = discriminator + token_mint + amount_bytes
    encoded = base64.b64encode(instruction_data).decode('utf-8')
    logging.debug(f"Created instruction data: {len(instruction_data)} bytes")
    logging.debug(f"- Discriminator: {discriminator!r}")
    logging.debug(f"- Token mint: {token_mint.hex()}")
    logging.debug(f"- Amount bytes: {amount_bytes.hex()}")
    logging.debug(f"Base64 encoded: {encoded}")
    return encoded

async def test_with_sample_tx():
    """Test amount extraction with a sample Pump.fun transaction"""
    parser = WalletATxParser()
    
    # Sample amount in SOL
    test_amount = 0.123456789
    print(f"\n🔍 Testing with amount: {test_amount} SOL")
    
    # Create encoded instruction data
    instruction_data = create_pump_instruction_data(test_amount)
    
    # Sample Pump.fun buy transaction logs
    sample_tx = {
        "value": {
            "signature": "test_signature",
            "logs": [
                "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]",
                "Program log: Instruction: PumpBuy",
                f"Program data: {instruction_data}",
                "Program 11111111111111111111111111111111 invoke [2]",
                f"Program log: Transfer {int(test_amount * 1e9)} lamports to Pump.fun",
                "Program 11111111111111111111111111111111 success",
                "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW success",
            ]
        }
    }
    
    print("\n📋 Testing transaction logs:")
    for i, log in enumerate(sample_tx["value"]["logs"]):
        print(f"[{i}] {log}")
    
    print("\n🧪 Testing instruction data first:")
    # Enable debug printing of instruction data
    raw_data = base64.b64decode(instruction_data)
    print(f"Total length: {len(raw_data)} bytes")
    print(f"Discriminator: {raw_data[:8]!r}")
    print(f"Token mint: {raw_data[8:40].hex()}")
    print(f"Amount bytes: {raw_data[40:48].hex()}")
    expected_amount = int.from_bytes(raw_data[40:48], 'little') / 1e9
    print(f"Expected decoded amount: {expected_amount} SOL")
    
    print("\n🔍 Testing amount extraction:")
    test_logs = sample_tx["value"]["logs"]
    print("\nTrying system transfer first...")
    for log in test_logs:
        if "Program log: Transfer" in log:
            print(f"Found transfer log: {log}")
            try:
                # Extract number between "Transfer" and "lamports"
                words = log.split()
                transfer_index = words.index("Transfer")
                if transfer_index + 1 < len(words):
                    amount_str = words[transfer_index + 1]
                    print(f"Found amount string: {amount_str}")
                    if amount_str.isdigit():
                        test_amount_raw = int(amount_str)
                        test_sol = test_amount_raw / 1e9
                        print(f"Parsed test amount: {test_amount_raw} lamports = {test_sol} SOL")
            except Exception as e:
                print(f"Test parsing failed: {e}")

    print("\nNow running parser:")
    amount = parser._extract_amount_from_logs(sample_tx["value"]["logs"])
    print(f"Parser returned: {amount}")
    
    assert amount == test_amount, f"Expected {test_amount} SOL, got {amount}"
    print("✅ Test passed! Amount correctly extracted")
    
    # Now test with alternative format (system transfer)
    print("\n🔍 Testing system transfer fallback...")
    sample_tx["value"]["logs"] = [
        "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]",
        "Program log: Instruction: PumpBuy",
        "Program 11111111111111111111111111111111 invoke [2]",
        f"Program log: Transfer {int(test_amount * 1e9)} lamports",
        "Program 11111111111111111111111111111111 success",
        "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW success",
    ]
    
    amount = parser._extract_amount_from_logs(sample_tx["value"]["logs"])
    assert amount == test_amount, f"Expected {test_amount} SOL, got {amount}"
    print("✅ Test passed! Amount correctly extracted from system transfer")
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    logging.debug("Starting amount extraction tests...")
    asyncio.run(test_with_sample_tx())
