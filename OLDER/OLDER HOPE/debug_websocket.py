#!/usr/bin/env python3
"""
Debug WebSocket Activity - See what messages are actually being received
"""

import asyncio
import logging
import json
from datetime import datetime
from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup verbose logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_websocket_activity():
    """Debug what WebSocket messages are being received"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: WEBSOCKET ACTIVITY MONITOR")
    print("="*80)
    print("🎯 PURPOSE: See exactly what WebSocket messages are received")
    print("📊 This will show ALL activity from your monitored wallets")
    print("="*80)
    
    bot = PumpCopyTradingBot()
    
    # Override the message handler to show debug info
    original_handler = bot._handle_websocket_message
    message_count = 0
    
    async def debug_handler(message):
        nonlocal message_count
        message_count += 1
        
        try:
            print(f"\n🔥 MESSAGE #{message_count} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            
            # Try to parse the message
            if isinstance(message, str):
                try:
                    data = json.loads(message)
                    print(f"📊 Type: {type(data)} - {len(str(data))} chars")
                    
                    # Show key fields
                    if isinstance(data, dict):
                        if 'method' in data:
                            print(f"   Method: {data['method']}")
                        if 'params' in data:
                            params = data['params']
                            if 'result' in params:
                                result = params['result']
                                if 'value' in result:
                                    value = result['value']
                                    if 'logs' in value:
                                        logs = value['logs']
                                        print(f"   📋 Logs found: {len(logs)} entries")
                                        
                                        # Check for wallet activity
                                        signature = value.get('signature', 'Unknown')
                                        print(f"   🔗 Signature: {signature[:16]}...")
                                        
                                        # Show first few logs to see if pump activity
                                        for i, log in enumerate(logs[:5]):
                                            print(f"      {i+1}: {log}")
                                            if any(pattern in log for pattern in [
                                                'BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW',
                                                'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA',
                                                'PumpAmmSwap',
                                                'Instruction: Buy',
                                                'Instruction: Sell'
                                            ]):
                                                print(f"         🎯 PUMP ACTIVITY DETECTED!")
                                        
                                        if len(logs) > 5:
                                            print(f"      ... and {len(logs)-5} more logs")
                                    
                                    if 'accountIndex' in value:
                                        print(f"   👤 Account Index: {value['accountIndex']}")
                except json.JSONDecodeError:
                    print(f"📊 Raw message (not JSON): {str(message)[:200]}...")
            else:
                print(f"📊 Non-string message: {type(message)} - {str(message)[:200]}...")
            
            print("-" * 50)
            
            # Still call the original handler
            await original_handler(message)
            
        except Exception as e:
            print(f"❌ Debug handler error: {e}")
            # Still try to call original handler
            try:
                await original_handler(message)
            except:
                pass
    
    # Replace the handler
    bot._handle_websocket_message = debug_handler
    
    print(f"\n🔔 DEBUG MODE ENABLED!")
    print(f"📡 Monitoring {len(bot.target_wallets)} wallets:")
    for i, wallet in enumerate(bot.target_wallets, 1):
        print(f"   {i}. {wallet[:8]}...")
    
    print(f"\n🎯 What you'll see:")
    print(f"   📊 ALL WebSocket messages received")
    print(f"   🔍 Detailed log analysis for pump activity")  
    print(f"   🎯 Detection attempts and results")
    print(f"   ⚡ Real-time activity from your wallets")
    
    print(f"\n⚠️  This will be VERY verbose!")
    print(f"💡 Make a trade from one of your wallets to test")
    print(f"🛑 Press Ctrl+C to stop debugging")
    print("="*80)
    
    try:
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Debug session stopped")
        print(f"📊 Total messages received: {message_count}")
        await bot.close()
    except Exception as e:
        print(f"\n❌ Debug error: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(debug_websocket_activity())
