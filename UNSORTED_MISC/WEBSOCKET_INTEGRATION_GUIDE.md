# WebSocket Wallet Monitoring Integration Guide

## Overview
The `wallet_tx_parser.py` has been enhanced with real-time WebSocket monitoring capabilities to detect when target wallets buy or sell meme coins. This integration uses the official Solana WebSocket API through Helius to provide instant trade detection.

## Key Features

### 🚀 Real-time WebSocket Monitoring
- Uses Solana's official `logsSubscribe` WebSocket method
- Monitors multiple target wallets simultaneously
- Provides instant notifications when transactions occur
- Automatically connects to your Helius WebSocket endpoint

### 🔍 Advanced Trade Detection
- Detects buy/sell actions across multiple DEXs (Pump.fun, Jupiter, Raydium, Orca, etc.)
- Extracts token mint addresses from transaction logs
- Identifies the specific DEX used for each trade
- Provides detailed trade information including signatures and timestamps

### 🎯 Meme Coin Focus
- Specifically designed for meme coin trading detection
- Filters out system transactions and focuses on relevant trades
- Extracts token mint addresses for immediate copy trading

## How It Works

### 1. WebSocket Connection
```python
# Connects to Helius WebSocket endpoint
wss://rpc.helius.xyz/?api-key=YOUR_API_KEY
```

### 2. Wallet Subscription
For each target wallet, it subscribes using:
```json
{
  "jsonrpc": "2.0",
  "method": "logsSubscribe",
  "params": [
    {"mentions": ["WALLET_ADDRESS"]},
    {"commitment": "processed"}
  ]
}
```

### 3. Real-time Analysis
When a transaction occurs:
1. Receives `logsNotification` with transaction logs
2. Parses logs to detect DEX and trade type (buy/sell)
3. Extracts token mint address
4. Calls your callback function with trade details

### 4. Trade Detection Logic
- **DEX Detection**: Identifies program IDs for Pump.fun, Jupiter, Raydium, etc.
- **Buy/Sell Detection**: Analyzes instruction types and token flow patterns
- **Token Extraction**: Finds token mint addresses in transaction logs

## Usage Examples

### Basic Usage
```python
from wallet_tx_parser import start_realtime_monitoring

# Define your target wallets
target_wallets = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
    "DfMxre4cKmvogbLrPigxmibULPkPpA557prMG47xCHQfK"
]

# Define callback for detected trades
async def handle_trade(trade_info):
    print(f"🚨 {trade_info['action'].upper()} detected!")
    print(f"Token: {trade_info.get('token_mint')}")
    print(f"DEX: {trade_info.get('dex')}")
    
    # Your copy trading logic here
    if trade_info['action'] == 'buy':
        await execute_copy_buy(trade_info['token_mint'])

# Start monitoring
await start_realtime_monitoring(target_wallets, handle_trade)
```

### Integration with Your main.py
```python
# In your CopyTradingBot class:
from wallet_tx_parser import WebSocketWalletMonitor

class CopyTradingBot:
    def __init__(self, config: CopyTradeConfig):
        # ... existing initialization ...
        
        # Add WebSocket monitor
        self.ws_monitor = WebSocketWalletMonitor(config.target_wallets)
        self.ws_monitor.set_trade_callback(self._handle_websocket_trade)
    
    async def _handle_websocket_trade(self, trade_info):
        """Handle trades detected via WebSocket"""
        if trade_info['action'] == 'buy':
            await self._execute_copy_buy(
                trade_info.get('token_mint'),
                trade_info['wallet_address'],
                trade_info.get('dex')
            )
    
    async def start_monitoring(self):
        # Start WebSocket monitoring alongside your existing logic
        websocket_task = asyncio.create_task(self.ws_monitor.start_monitoring())
        # ... your existing monitoring logic ...
```

## Trade Information Structure

Each detected trade provides:
```python
{
    'signature': 'transaction_signature',
    'wallet_address': 'source_wallet_address',
    'action': 'buy' or 'sell',
    'dex': 'Pump.fun' | 'Jupiter' | 'Raydium' | etc.,
    'token_mint': 'token_mint_address',
    'timestamp': datetime_object,
    'instruction_type': 'BuyExactIn' | 'SellExactIn' | etc.
}
```

## Supported DEXs

The system recognizes these platforms:
- **Pump.fun**: Primary meme coin platform
- **Jupiter**: Aggregator
- **Raydium**: CPMM and CLMM
- **Orca**: Whirlpools
- **Meteora**: DLMM
- **Phoenix**: Order book
- **Mango**: Derivatives

## Configuration

### Environment Variables
The system automatically uses your existing configuration:
- `HELIUS_Standard_Websocket_URL`: WebSocket endpoint
- `HELIUS_API_KEY`: API key for authentication

### Debug Mode
Enable debug logging:
```python
DEBUG = True
TRACE_LOGS = True
```

## Testing

Run the integration example:
```bash
python3 websocket_integration_example.py
```

Or test the setup:
```bash
python3 -c "
from wallet_tx_parser import WebSocketWalletMonitor
import asyncio

async def test():
    monitor = WebSocketWalletMonitor(['test_wallet'])
    print('✅ Setup successful')

asyncio.run(test())
"
```

## Performance Benefits

1. **Instant Detection**: WebSocket provides real-time notifications
2. **Efficient**: Only processes relevant transactions
3. **Reliable**: Uses official Solana WebSocket API
4. **Scalable**: Can monitor multiple wallets simultaneously

## Integration Steps

1. **Import the WebSocket monitor** in your main.py
2. **Add target wallets** to your configuration
3. **Create a trade callback function** that integrates with your copy trading logic
4. **Start WebSocket monitoring** alongside your existing monitoring

The WebSocket monitoring will now provide instant trade detection to complement your existing copy trading bot!

## Error Handling

The system includes robust error handling for:
- WebSocket connection issues
- Malformed messages
- Network timeouts
- Invalid wallet addresses

All errors are logged with detailed information for debugging.
