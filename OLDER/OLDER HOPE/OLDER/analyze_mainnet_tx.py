"""Monitor and analyze live Pump.fun transactions."""

import asyncio
import json
import aiohttp
import logging
from datetime import datetime, timezone
from env_keys import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pump.fun program ID
PUMP_PROGRAM_ID = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"

async def monitor_pump_transactions():
    """Monitor live Pump.fun transactions."""
    print("\n🔄 Starting live transaction monitor...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": "1",
                    "method": "getSignaturesForAddress",
                    "params": [
                        PUMP_PROGRAM_ID,
                        {
                            "limit": 1,
                            "commitment": "confirmed"
                        }
                    ]
                }
                
                async with session.post(kz.HELIUS_RPC_URL, json=payload) as response:
                    if response.status != 200:
                        print(f"❌ HTTP {response.status} from RPC")
                        continue
                        
                    data = await response.json()
                    if "error" in data:
                        print(f"❌ RPC error: {json.dumps(data['error'], indent=2)}")
                        continue
                        
                    signatures = data.get("result", [])
                    if not signatures:
                        print("No transactions found, retrying...")
                        await asyncio.sleep(1)
                        continue
                        
                    # Found a transaction, analyze it
                    sig = signatures[0]["signature"]
                    print(f"\n✨ Found new transaction: {sig}")
                    
                    # Get transaction details
                    tx_data = await fetch_transaction(session, sig)
                    if tx_data:
                        await analyze_transaction(tx_data, sig)
                        break  # Exit after analyzing one transaction
                    
            except Exception as e:
                print(f"❌ Error monitoring transactions: {e}")
                await asyncio.sleep(1)

async def fetch_transaction(session: aiohttp.ClientSession, signature: str) -> dict:
    """Fetch transaction details."""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "jsonParsed",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed"
                }
            ]
        }
        
        print(f"📥 Fetching transaction data...")
        async with session.post(kz.HELIUS_RPC_URL, json=payload) as response:
            if response.status != 200:
                print(f"❌ HTTP {response.status}")
                return None
                
            data = await response.json()
            if "error" in data:
                print(f"❌ RPC error: {json.dumps(data['error'], indent=2)}")
                return None
                
            result = data.get("result")
            if not result:
                print("❌ No transaction data")
                return None
                
            print("✅ Transaction data fetched successfully")
            return result
            
    except Exception as e:
        print(f"❌ Error fetching transaction: {e}")
        return None

async def analyze_transaction(tx_data: dict, signature: str):
    """Analyze transaction data."""
    try:
        print(f"\n📊 Analysis of transaction {signature}:")
        
        # Transaction metadata
        meta = tx_data.get("meta", {})
        fee = meta.get("fee", 0)
        status = "✅ Success" if not meta.get("err") else f"❌ Failed: {meta.get('err')}"
        
        print(f"\n🔹 Status: {status}")
        print(f"🔹 Fee: {fee/1e9:.6f} SOL")
        print(f"🔹 Slot: {tx_data.get('slot', 'unknown')}")
        
        # Balance changes
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        accounts = tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])
        
        if pre_balances and post_balances:
            print("\n💰 Balance Changes:")
            for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                if pre != post:
                    change = (post - pre) / 1e9
                    account = accounts[i] if i < len(accounts) else "Unknown"
                    print(f"  {account}: {change:+.6f} SOL")
        
        # Instructions analysis
        instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])
        print(f"\n📋 Instructions ({len(instructions)}):")
        
        for i, ix in enumerate(instructions):
            print(f"\n📎 Instruction {i}:")
            program_id = ix.get('programId', 'unknown')
            print(f"  Program: {program_id}")
            
            # Parse instruction data
            data = ix.get('data', '')
            if data and program_id == PUMP_PROGRAM_ID:
                try:
                    # Remove '0x' prefix if present
                    data = data.replace('0x', '')
                    
                    # First 8 bytes are the discriminator
                    discriminator = data[:16]
                    print(f"  Discriminator: {discriminator}")
                    
                    # Try to parse amounts if present
                    if len(data) >= 48:  # Has two u64 values
                        amount1 = int(data[16:32], 16)
                        amount2 = int(data[32:48], 16)
                        print(f"  Amount 1: {amount1/1e9:.6f} SOL")
                        print(f"  Amount 2: {amount2/1e9:.6f} SOL")
                except Exception as e:
                    print(f"  ❌ Error parsing data: {e}")
            
            # Account analysis
            accounts = ix.get("accounts", [])
            print(f"\n  🔑 Accounts ({len(accounts)}):")
            for j, acc in enumerate(accounts):
                print(f"    {j}: {acc}")
        
        # Save transaction data
        output_file = f"pump_tx_{signature[:8]}.json"
        with open(output_file, "w") as f:
            json.dump(tx_data, f, indent=2)
        print(f"\n✅ Transaction data saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")

async def main():
    """Main execution function."""
    print(f"\n🕒 Started at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("👀 Monitoring for Pump.fun transactions...")
    
    try:
        await monitor_pump_transactions()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        logger.exception("Fatal error during monitoring")

if __name__ == "__main__":
    print(f"Current Date and Time (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())
    