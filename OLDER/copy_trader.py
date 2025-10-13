import asyncio
import json
import logging
from typing import List, Dict
import aiohttp
import websockets
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from env_keys import kz
from listener import fetch_transaction, identify_dex_and_instruction, extract_trade_data
from minimal_tx_builder import build_and_send_transaction
from log_utils import setup_logger

# Setup logging
logger = setup_logger('copy_trader', 'copy_trades.log')

class CopyTrader:
    def __init__(self, wallet_addresses: List[str], your_keypair: Keypair):
        self.wallet_addresses = wallet_addresses
        self.your_keypair = your_keypair
        self.ws_url = kz.HELIUS_Standard_Websocket_URL
        self.running = False
        
    async def start_listening(self):
        """Start listening to multiple wallet addresses"""
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    # Subscribe to all wallet addresses
                    for address in self.wallet_addresses:
                        await websocket.send(json.dumps({
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "accountSubscribe",
                            "params": [
                                address,
                                {"encoding": "jsonParsed", "commitment": "confirmed"}
                            ]
                        }))
                    
                    logger.info(f"Started monitoring wallets: {', '.join(self.wallet_addresses)}")
                    
                    while self.running:
                        try:
                            msg = await websocket.recv()
                            data = json.loads(msg)
                            
                            if "params" in data:
                                await self.handle_transaction(data["params"])
                                
                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
                            
            except Exception as e:
                logger.error(f"WebSocket connection error: {str(e)}")
                await asyncio.sleep(5)  # Wait before reconnecting
                
    async def handle_transaction(self, params: Dict):
        """Handle incoming transaction data"""
        try:
            if "result" in params and "signature" in params["result"]:
                signature = params["result"]["signature"]
                tx_data = await fetch_transaction(signature)
                
                if not tx_data:
                    return
                
                # Identify if this is a trade we want to copy
                dex_info = identify_dex_and_instruction(tx_data)
                if not dex_info:
                    return
                
                trade_data = extract_trade_data(tx_data, dex_info)
                if not trade_data:
                    return
                
                # Log the trade we're about to copy
                logger.info(f"Copying trade from {params['result']['accountId']}")
                logger.info(f"Trade details: {json.dumps(trade_data, indent=2)}")
                
                # Build and execute the copied trade
                await self.execute_copy_trade(trade_data, dex_info)
                
        except Exception as e:
            logger.error(f"Error handling transaction: {str(e)}")
            
    async def execute_copy_trade(self, trade_data: Dict, dex_info: Dict):
        """Execute a copy of the detected trade"""
        try:
            # Build and send the transaction
            result = await build_and_send_transaction(
                keypair=self.your_keypair,
                trade_data=trade_data,
                dex_info=dex_info
            )
            
            if result and result.get("success"):
                logger.info(f"Successfully copied trade: {result.get('signature')}")
            else:
                logger.error(f"Failed to copy trade: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error executing copy trade: {str(e)}")

async def main():
    # Load your keypair for executing trades
    keypair = Keypair.from_bytes(kz.PRIVATE_KEY_BYTES)
    
    # List of wallets to monitor
    wallets_to_monitor = [
        "WALLET_ADDRESS_1_HERE",  # Replace with actual wallet address
        "WALLET_ADDRESS_2_HERE"   # Replace with actual wallet address
    ]
    
    # Initialize and start the copy trader
    trader = CopyTrader(wallets_to_monitor, keypair)
    await trader.start_listening()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down copy trader...")
