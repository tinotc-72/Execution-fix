#!/usr/bin/env python3
"""
Essential files list - DO NOT MOVE TO OLDER FOLDER
These files are required for the copy trading bot to function
"""

ESSENTIAL_COPY_TRADING_FILES = [
    # Core bot files
    "advanced_copy_trading_bot.py",          # Main copy trading bot
    "generalized_pump_trading_bot.py",       # Trading engine
    "production_pump_trading_bot.py",        # Base trading bot
    
    # Configuration and keys
    "config.py",                             # Main configuration (monitored wallets)
    "env_keys.py",                          # API keys and environment
    
    # Supporting modules
    "listener.py",                          # Transaction analysis
    "wallet_tx_parser.py",                  # Transaction parsing
    "tx_builder.py",                        # Transaction building
    "models.py",                            # Data models (required by tx_builder)
    "jito_service.py",                      # Jito service (required by tx_builder)
    "fast_executor.py",                     # Fast execution
    "logger.py",                            # Logging utilities
    
    # Launcher scripts
    "launch_copy_trading.py",               # Alternative launcher
    "launch_production.py",                 # Production launcher
    "main.py",                              # Main entry point
    
    # Log files (for monitoring)
    "copy_trading.log",                     # Copy trading logs
    "generalized_pump_trading.log",         # Trading logs
    "pump_trading_bot.log",                 # Bot logs
    
    # Test files (for verification)
    "test_bot_functionality.py",            # Bot tests
    "test_copy_trading_system.py",          # System tests
    "test_trading_capability.py",           # Trading tests
    "find_active_wallets.py",               # Utility for finding wallets
]

OPTIONAL_BUT_USEFUL_FILES = [
    # Environment files
    ".env",
    ".env.example", 
    "env.example",
    
    # Documentation
    "README.md",
    "LICENSE",
    
    # Python environment
    "hopeII/",                              # Virtual environment
    "__pycache__/",                         # Python cache
    "logs/",                                # Log directory
]

print("🚨 IMPORTANT: Keep these files in the main directory!")
print("=" * 60)
print("Essential Copy Trading Bot Files:")
for i, file in enumerate(ESSENTIAL_COPY_TRADING_FILES, 1):
    print(f"  {i:2d}. {file}")

print(f"\nTotal essential files: {len(ESSENTIAL_COPY_TRADING_FILES)}")
print("\n⚠️  Never move these files to the OLDER folder!")
