#!/usr/bin/env python3
"""
🧪 TEST ENHANCED STOP FUNCTIONALITY
This script tests whether the enhanced stop methods work properly
"""

import asyncio
import signal
import sys
import time

# Simple test bot that mimics the main bot behavior
class TestBot:
    def __init__(self):
        self.is_running = False
        self.tasks = []
        
    async def start_monitoring(self):
        """Simulate the main bot monitoring loop"""
        self.is_running = True
        print("🚀 Test bot started - monitoring...")
        
        # Create some background tasks (simulating WebSocket monitoring)
        self.tasks.append(asyncio.create_task(self._fake_websocket_monitor()))
        self.tasks.append(asyncio.create_task(self._fake_status_monitor()))
        
        # Main monitoring loop
        try:
            while self.is_running:
                print("💓 Test bot heartbeat...")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
        finally:
            print("🛑 Test bot monitoring loop ended")
    
    async def _fake_websocket_monitor(self):
        """Simulate WebSocket monitoring"""
        try:
            while self.is_running:
                print("📡 WebSocket ping...")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("🔥 WebSocket monitor cancelled")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def _fake_status_monitor(self):
        """Simulate status monitoring"""
        try:
            while self.is_running:
                print("📊 Status check...")
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            print("🔥 Status monitor cancelled")
        except Exception as e:
            print(f"❌ Status error: {e}")
    
    async def stop(self):
        """Enhanced stop method (mimics the real one)"""
        print("🚨 ENHANCED STOP: Forcefully stopping test bot...")
        self.is_running = False
        
        try:
            # Cancel all tasks
            print(f"🔥 CANCELLING {len(self.tasks)} tasks...")
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for cancellation
            if self.tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self.tasks, return_exceptions=True),
                        timeout=3.0
                    )
                except asyncio.TimeoutError:
                    print("⚠️ Some tasks did not cancel in time")
            
            print("✅ ENHANCED STOP COMPLETED")
            
        except Exception as e:
            print(f"❌ Error in enhanced stop: {e}")

# Global bot instance
test_bot = None

def setup_signal_handlers():
    """Setup enhanced signal handlers (mimics the real ones)"""
    signal_count = 0
    
    def signal_handler(signum, frame):
        nonlocal signal_count
        signal_count += 1
        
        print(f"\n🚨 RECEIVED SIGNAL {signum} (attempt {signal_count}) - FORCE STOPPING...")
        
        if signal_count == 1:
            print("🔄 First signal - attempting graceful shutdown...")
            if test_bot and asyncio.get_event_loop().is_running():
                asyncio.create_task(graceful_shutdown())
            else:
                print("⚠️ No bot instance running or event loop not active")
                sys.exit(1)
        elif signal_count == 2:
            print("🚨 Second signal - FORCE KILL...")
            sys.exit(1)
        else:
            print("🔥 Third signal - NUCLEAR OPTION...")
            import os
            os._exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

async def graceful_shutdown():
    """Enhanced graceful shutdown (mimics the real one)"""
    global test_bot
    
    if test_bot:
        print("🚨 ENHANCED SHUTDOWN: Force stopping test bot...")
        try:
            test_bot.is_running = False
            await asyncio.wait_for(test_bot.stop(), timeout=10.0)
            print("✅ Enhanced shutdown completed")
        except asyncio.TimeoutError:
            print("⚠️ Graceful shutdown timed out")
        except Exception as e:
            print(f"❌ Error during graceful shutdown: {e}")
    else:
        print("⚠️ No bot instance found")

async def main():
    """Test main function"""
    global test_bot
    
    print("🧪 TESTING ENHANCED STOP FUNCTIONALITY")
    print("=" * 50)
    print("🎯 Press Ctrl+C once for graceful shutdown")
    print("🎯 Press Ctrl+C twice for force kill")
    print("=" * 50)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Create and start test bot
    test_bot = TestBot()
    
    try:
        await test_bot.start_monitoring()
    except KeyboardInterrupt:
        print("🚨 KeyboardInterrupt detected - forcing shutdown...")
        await graceful_shutdown()
    except Exception as e:
        print(f"❌ Error in test: {e}")
        if test_bot:
            await graceful_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test terminated by keyboard interrupt")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    print("\n✅ Test completed!")
