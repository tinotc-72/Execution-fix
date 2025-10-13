import asyncio
import logging
import aiohttp
import json
from datetime import datetime
from wallet_tx_parser import WalletATxParser
from config import HELIUS_RPC_URL, WALLET_A_ADDRESS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_parser.log'),
        logging.StreamHandler()
    ]
)

async def fetch_recent_transactions():
    """Fetch recent transactions from Wallet A"""
    
    # Get confirmed signatures for Wallet A's transactions
    async with aiohttp.ClientSession() as session:
        async with session.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    WALLET_A_ADDRESS,
                    {
                        "limit": 50  # Increased to 50 for better testing
                    }
                ]
            }
        ) as response:
            signatures_data = await response.json()
            
        if "result" not in signatures_data:
            print("❌ Failed to fetch signatures")
            return []
            
        transactions = []
        print(f"\nFetching details for {len(signatures_data['result'])} transactions...")
        
        for signature_info in signatures_data["result"]:
            signature = signature_info["signature"]
            print(f"Processing signature: {signature}")
            
            # Get transaction details
            async with session.post(
                HELIUS_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": "jsonParsed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
            ) as tx_response:
                tx_data = await tx_response.json()
                if "result" in tx_data and tx_data["result"]:
                    transactions.append({
                        "value": {
                            "signature": signature,
                            "err": None,
                            "logs": tx_data["result"]["meta"]["logMessages"],
                            "raw": tx_data["result"]  # Store full transaction data
                        }
                    })
                    
        return transactions

async def test_token_extraction(parser, logs):
    """Test token extraction specifically"""
    print("\n🔍 Testing token extraction...")
    token = parser._extract_token_from_logs(logs)
    print(f"Token extracted: {token}")
    return token is not None

async def test_amount_extraction(parser, logs):
    """Test amount extraction specifically"""
    print("\n💰 Testing amount extraction...")
    amount = parser._extract_amount_from_logs(logs)
    print(f"Amount extracted: {amount}")
    return amount is not None

async def validate_trade_info(trade_info):
    """Validate trade information"""
    if not trade_info:
        return False
        
    required_fields = ['type', 'token', 'amount', 'program', 'signature']
    missing_fields = [field for field in required_fields if field not in trade_info]
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
        
    if not trade_info['token']:
        print("❌ Token address is None")
        return False
        
    if not trade_info['amount']:
        print("❌ Amount is None")
        return False
        
    if trade_info['type'] not in ['buy', 'sell']:
        print(f"❌ Invalid trade type: {trade_info['type']}")
        return False
        
    print("✅ Trade info validation passed")
    return True

async def test_parser():
    """Test parsing Pump.fun transactions"""
    parser = WalletATxParser()
    
    print("\n🧪 Testing Pump.fun Transaction Parser with Real Transactions")
    print("==========================================================")
    
    # Fetch recent transactions
    print("\nFetching recent transactions from Wallet A...")
    transactions = await fetch_recent_transactions()
    
    if not transactions:
        print("❌ No transactions found")
        return
        
    print(f"\nFound {len(transactions)} recent transactions")
    
    # Test statistics
    total_txs = len(transactions)
    pump_trades = 0
    successful_token_extractions = 0
    successful_amount_extractions = 0
    valid_trades = 0
    
    # Parse each transaction
    for tx in transactions:
        print(f"\n📝 Analyzing transaction: {tx['value']['signature']}")
        
        # Test token extraction
        if await test_token_extraction(parser, tx["value"]["logs"]):
            successful_token_extractions += 1
            
        # Test amount extraction
        if await test_amount_extraction(parser, tx["value"]["logs"]):
            successful_amount_extractions += 1
            
        # Test full transaction parsing
        trade_info = await parser.parse_transaction(tx)
        
        if trade_info:
            pump_trades += 1
            print(f"\n🎯 Found {trade_info['type'].upper()} trade:")
            print(f"Type: {trade_info['type']}")
            print(f"Token: {trade_info['token']}")
            print(f"Amount: {trade_info['amount']} SOL")
            print(f"Program: {trade_info['program']}")
            print(f"Signature: {trade_info['signature']}")
            
            if await validate_trade_info(trade_info):
                valid_trades += 1
            
            print("-" * 50)
    
    # Print test summary
    print("\n📊 Test Summary")
    print("==============")
    print(f"Total transactions analyzed: {total_txs}")
    print(f"Pump.fun trades detected: {pump_trades}")
    print(f"Successful token extractions: {successful_token_extractions}")
    print(f"Successful amount extractions: {successful_amount_extractions}")
    print(f"Valid trades (all fields present): {valid_trades}")
    print(f"Token extraction success rate: {successful_token_extractions/total_txs*100:.1f}%")
    print(f"Amount extraction success rate: {successful_amount_extractions/total_txs*100:.1f}%")
    print(f"Valid trade success rate: {valid_trades/total_txs*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_parser())
