#!/usr/bin/env python3
"""
WORKING Transaction History Scanner
Uses the EXACT same logic that successfully detected your real-time trades
"""

import asyncio
from main import CopyTradingBot, CopyTradeConfig
from env_keys import EnvKeys
from solders.pubkey import Pubkey
from datetime import datetime, timedelta
import json

class HistoricalTradeDetector:
    def __init__(self):
        self.detected_trades = []
        
    async def scan_wallet_history(self, wallet_address: str, limit: int = 100, days_back: int = 7):
        """Scan wallet history using the proven main.py detection logic"""
        print(f"🔍 SCANNING: {wallet_address}")
        
        # Initialize bot with the same config that works for real-time
        config = CopyTradeConfig(target_wallets=[wallet_address])
        bot = CopyTradingBot(config)
        
        # Override the copy trade execution to just collect trades instead
        original_execute_copy_trade = bot.execute_copy_trade
        detected_trades = []
        
        async def collect_trade_info(trade_info, source_wallet):
            """Collect trade info instead of executing trades"""
            detected_trades.append({
                'signature': trade_info.get('original_signature', 'unknown'),
                'wallet': source_wallet,
                'type': trade_info.get('type'),
                'token_mint': trade_info.get('token_mint'),
                'amount': trade_info.get('amount', 0),
                'dex': trade_info.get('dex'),
                'timestamp': trade_info.get('timestamp', datetime.now()),
                'detection_method': trade_info.get('detection_method', 'main.py_logic')
            })
            print(f"   ✅ TRADE DETECTED: {trade_info['type'].upper()} {trade_info['token_mint'][:8]}... on {trade_info.get('dex', 'Unknown')}")
        
        # Replace the execute method
        bot.execute_copy_trade = collect_trade_info
        
        try:
            # Get transaction signatures  
            wallet_pubkey = Pubkey.from_string(wallet_address)
            
            print(f"   📥 Fetching recent {limit} transactions...")
            response = await bot.rpc_client.get_signatures_for_address(
                wallet_pubkey, 
                limit=limit
            )
            
            if not response.value:
                print(f"   📭 No transactions found")
                return []
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(days=days_back)
            signatures_to_analyze = []
            
            for tx_info in response.value:
                if hasattr(tx_info, 'block_time') and tx_info.block_time:
                    tx_time = datetime.fromtimestamp(tx_info.block_time)
                    if tx_time >= cutoff_time:
                        signatures_to_analyze.append(str(tx_info.signature))
                    else:
                        break
            
            print(f"   📊 Found {len(signatures_to_analyze)} transactions within {days_back} days")
            print(f"   🔍 Analyzing with proven main.py logic...")
            
            # Process each signature using the EXACT same logic that works in real-time
            for i, signature in enumerate(signatures_to_analyze):
                try:
                    if i > 0 and i % 10 == 0:
                        print(f"      Progress: {i}/{len(signatures_to_analyze)} ({len(detected_trades)} trades found)")
                    
                    # Use the EXACT same analyze_transaction method that detected your real trades
                    await bot.analyze_transaction(signature, wallet_address)
                    
                    # Small delay
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    # Skip failed transactions
                    continue
            
            print(f"   ✅ Analysis complete: {len(detected_trades)} trades detected")
            return detected_trades
            
        except Exception as e:
            print(f"   ❌ Error scanning wallet: {e}")
            return []
        
        finally:
            try:
                await bot.stop()
            except:
                pass

async def main():
    """Run historical trade detection for both wallets"""
    print("🚀 HISTORICAL TRADE DETECTION")
    print("Using the SAME logic that successfully detected your real-time trades!")
    print("=" * 70)
    
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Wallet 2  
    ]
    
    detector = HistoricalTradeDetector()
    all_trades = {}
    
    for wallet in target_wallets:
        trades = await detector.scan_wallet_history(wallet, limit=100, days_back=3)
        all_trades[wallet] = {
            'trades': trades,
            'buys': [t for t in trades if t['type'] == 'buy'],
            'sells': [t for t in trades if t['type'] == 'sell'],
            'total_count': len(trades)
        }
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"proven_logic_historical_trades_{timestamp}.json"
    
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj
    
    serializable_results = convert_datetime(all_trades)
    
    with open(filename, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    # Print summary
    print(f"\n📊 HISTORICAL TRADE DETECTION RESULTS:")
    print(f"=" * 50)
    
    total_trades = 0
    total_buys = 0 
    total_sells = 0
    
    for wallet, data in all_trades.items():
        trades = data['trades']
        buys = data['buys']
        sells = data['sells']
        
        total_trades += len(trades)
        total_buys += len(buys)
        total_sells += len(sells)
        
        print(f"\n🎯 {wallet}")
        print(f"   💹 Total trades: {len(trades)}")
        print(f"   🟢 Buys: {len(buys)}")
        print(f"   🔴 Sells: {len(sells)}")
        
        # Show some recent trades
        if trades:
            print(f"   📈 Recent trades:")
            for trade in trades[-3:]:  # Show last 3
                print(f"      {trade['type'].upper()}: {trade['token_mint'][:8]}... ({trade['dex']}) - {trade['timestamp']}")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   📊 Total wallets: {len(target_wallets)}")
    print(f"   💹 Total trades found: {total_trades}")
    print(f"   🟢 Total buys: {total_buys}")
    print(f"   🔴 Total sells: {total_sells}")
    print(f"   💾 Results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
