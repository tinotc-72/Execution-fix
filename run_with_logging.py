#!/usr/bin/env python3
"""
Script to run the main copy trading bot with comprehensive logging to file
"""

import subprocess
import sys
from datetime import datetime
import os

def run_bot_with_logging():
    """Run the main bot and capture all output to a log file"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/bot_run_{timestamp}.log"
    
    print(f"🚀 Starting Copy Trading Bot...")
    print(f"📝 Logging output to: {log_file}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍 Use Ctrl+C to stop the bot")
    print("-" * 60)
    
    try:
        # Run the main bot and capture output
        with open(log_file, 'w') as f:
            # Write header to log file
            f.write(f"Copy Trading Bot Log\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Command: python3 main.py\n")
            f.write("=" * 80 + "\n\n")
            f.flush()
            
            # Run the bot with real-time output to both console and file
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print("📊 Bot output (also being saved to log file):")
            print("-" * 60)
            
            # Stream output in real-time
            for line in process.stdout:
                # Print to console
                print(line.rstrip())
                # Write to file
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                f.flush()
            
            # Wait for process to complete
            process.wait()
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Bot stopped by user at {datetime.now().strftime('%H:%M:%S')}")
        print(f"📝 Full log saved to: {log_file}")
        if 'process' in locals():
            process.terminate()
    
    except Exception as e:
        error_msg = f"\n❌ Error running bot: {e}"
        print(error_msg)
        with open(log_file, 'a') as f:
            f.write(f"\n\nERROR: {error_msg}\n")
    
    finally:
        print(f"\n📝 Complete log file available at: {log_file}")
        print(f"🔍 To view log: cat {log_file}")

if __name__ == "__main__":
    run_bot_with_logging()