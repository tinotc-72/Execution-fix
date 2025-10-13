# main.py - Copy Trading Bot
"""
Copy Trading Bot for Solana
Watches Wallet A and copies their trades using Helius RPC
"""

import json
import asyncio
import logging
import time
import traceback
from datetime import datetime
import base58
import base64
import websockets
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from spl.token.instructions import get_associated_token_address, create_associated_token_account

# Import core components
from config import MONITORED_WALLETS
from advanced_copy_trading_bot import PumpCopyTradingBot

# Configure logging
logger = setup_logging()
trade_logger = logging.getLogger('trade_logger')

# Constants
from config import MONITORED_WALLETS, MONITORED_WALLET_PUBKEYS
HELIUS_WS_URL = kz.HELIUS_Standard_Websocket_URL
RPC_URL = kz.HELIUS_RPC_URL
RPC_HEADERS = kz.HELIUS_HEADERS
WS_HEADERS = kz.WS_HEADERS

# Trading parameters
FIXED_BUY_AMOUNT = 0.05  # Fixed buy amount in SOL
SLIPPAGE_BPS = 3000     # 30% slippage tolerance
MIN_SOL_BALANCE = 0.06  # Minimum SOL needed (trade amount + fees)

class CopyTradingBot:
    def __init__(self):
        """Initialize the copy trading bot with essential components"""
        try:
            # Use mnemonic-based wallet from config
            from config import WALLET
            self.keypair = WALLET  # Already properly derived from mnemonic
            logger.info(f"✅ Successfully loaded wallet: {self.keypair.pubkey()}")
            
            # Initialize core components with validated settings (FastExecutor will use mnemonic wallet by default)
            self.executor = FastExecutor()
            self.parser = WalletATxParser()
            self.target_wallets = MONITORED_WALLETS
            self.running = False
            
            # Trading parameters
            self.buy_amount = FIXED_BUY_AMOUNT
            self.slippage_bps = SLIPPAGE_BPS
            self.min_sol_balance = MIN_SOL_BALANCE
            
            # WebSocket configuration
            self.ws_url = kz.HELIUS_Standard_Websocket_URL
            self.ws_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kz.HELIUS_API_KEY}"
            }
            
            # Connection management
            self.last_heartbeat = datetime.now()
            self.heartbeat_interval = 30  # seconds
            self.reconnect_delay = 5  # seconds
            self.max_reconnect_attempts = 3
            
            logger.info("✅ Core components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def initialize(self):
        """Initialize core components"""
        try:
            # Initialize FastExecutor
            await self.executor.initialize()
            logger.info("✅ FastExecutor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {str(e)}")
            return False

    async def start(self):
        """Start the copy trading bot"""
        logger.info("\n🤖 Starting Copy Trading Bot")
        logger.info("==========================")
        logger.info(f"Your wallet: {self.keypair.pubkey()}")
        logger.info(f"Copying: {self.target_wallet}")
        
        # Initialize components
        if not await self.initialize():
            logger.error("Failed to initialize bot components")
            return
        
        self.running = True
        await self.monitor_wallet()

    async def _send_heartbeat(self, ws):
        """Send periodic websocket ping to keep connection alive"""
        while self.running:
            try:
                await ws.ping()
                self.last_heartbeat = datetime.now()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                break

    async def connect_websocket(self):
        """Establish WebSocket connection with proper authentication"""
        try:
            # Create connection with headers
            ws = await websockets.connect(
                self.ws_url,
                extra_headers=self.ws_headers,
                ping_interval=None,  # We'll handle our own heartbeat
                ping_timeout=None
            )
            
            # Subscribe to logs
            subscribe_msg = {
                "jsonrpc": "2.0",
                "id": str(int(time.time() * 1000)),
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [str(self.target_wallet)]},
                    {"commitment": "confirmed"}
                ]
            }
            
            await ws.send(json.dumps(subscribe_msg))
            response = await ws.recv()
            
            # Verify subscription success
            response_data = json.loads(response)
            if "result" not in response_data:
                raise Exception(f"Failed to subscribe: {response}")
                
            logger.info(f"✅ Successfully subscribed to {self.target_wallet}")
            return ws
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            return None

    async def monitor_wallet(self):
        """Monitor wallet A's transactions via WebSocket with robust error handling"""
        reconnect_attempts = 0
        
        while self.running:
            try:
                logger.info("Connecting to WebSocket...")
                async with websockets.connect(
                    self.ws_url,
                    extra_headers=self.ws_headers,
                    ping_interval=None,
                    ping_timeout=None
                ) as ws:
                    logger.info("✅ WebSocket connected")
                    
                    # Subscribe to multiple types of events
                    subscriptions = [
                        # Subscribe to logs from relevant programs and addresses
                        {
                            "jsonrpc": "2.0",
                            "id": str(int(time.time() * 1000)),
                            "method": "logsSubscribe",
                            "params": [
                                {"filter": {
                                    "mentions": [str(self.target_wallet)],
                                    "programIds": [
                                        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Pump.fun router
                                        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"    # Pump.fun core
                                    ]
                                }},
                                {"commitment": "confirmed", "encoding": "jsonParsed"}
                            ]
                        },
                        # Subscribe to account updates
                        {
                            "jsonrpc": "2.0",
                            "id": str(int(time.time() * 1000) + 1),
                            "method": "accountSubscribe",
                            "params": [
                                str(self.target_wallet),
                                {"encoding": "jsonParsed", "commitment": "confirmed"}
                            ]
                        }
                    ]
                    
                    # Initialize subscriptions with proper error handling
                    subscription_ids = {}
                    active_signatures = set()  # Track active signature subscriptions
                    
                    for sub_msg in subscriptions:
                        method = sub_msg["method"]
                        try:
                            logger.debug(f"Setting up {method}...")
                            logger.debug(f"Request: {json.dumps(sub_msg, indent=2)}")
                            
                            await ws.send(json.dumps(sub_msg))
                            response = await ws.recv()
                            response_data = json.loads(response)
                            
                            if "result" in response_data:
                                subscription_ids[method] = response_data["result"]
                                logger.info(f"✅ {method} subscription active (ID: {response_data['result']})")
                            else:
                                logger.error(f"❌ {method} subscription failed: {response}")
                                
                        except Exception as e:
                            logger.error(f"Error setting up {method}: {str(e)}")
                            continue
                    
                    if not subscription_ids:
                        raise Exception("Failed to establish any subscriptions")
                        
                    async def subscribe_to_signature(signature):
                        """Subscribe to a specific transaction signature"""
                        if signature in active_signatures:
                            return
                            
                        try:
                            sub_msg = {
                                "jsonrpc": "2.0",
                                "id": str(int(time.time() * 1000)),
                                "method": "signatureSubscribe",
                                "params": [
                                    signature,
                                    {"commitment": "confirmed"}
                                ]
                            }
                            
                            await ws.send(json.dumps(sub_msg))
                            response = await ws.recv()
                            response_data = json.loads(response)
                            
                            if "result" in response_data:
                                subscription_id = response_data["result"]
                                subscription_ids[f"signature_{signature}"] = subscription_id
                                active_signatures.add(signature)
                                logger.info(f"✅ Subscribed to signature: {signature}")
                            else:
                                logger.error(f"Failed to subscribe to signature: {response_data}")
                                
                        except Exception as e:
                            logger.error(f"Error subscribing to signature: {str(e)}")
                    
                    # Log active subscriptions
                    logger.info("\n📡 Active Subscriptions:")
                    for method, sub_id in subscription_ids.items():
                        logger.info(f"- {method}: {sub_id}")
                        
                    logger.info(f"✅ Successfully subscribed to {self.target_wallet}")
                    logger.info("📡 Monitoring for trades (debug mode enabled)")
                    
                    # Start heartbeat
                    heartbeat_task = asyncio.create_task(self._send_heartbeat(ws))
                    
                    try:
                        async for message in ws:
                            try:
                                if not message:
                                    continue
                                    
                                data = json.loads(message)
                                logger.debug(f"\n📥 Received message: {json.dumps(data, indent=2)}")
                                
                                # Handle subscription notifications
                                if "method" in data and data["method"] == "subscription":
                                    params = data.get("params", {})
                                    subscription = params.get("subscription")
                                    result = params.get("result")
                                    
                                    if not (subscription and result):
                                        logger.debug("Invalid subscription message format")
                                        continue
                                        
                                    # Handle based on subscription type
                                    if subscription == subscription_ids.get("logsSubscribe"):
                                        # Process program logs
                                        logs = result.get("logs", [])
                                        signature = result.get("signature")
                                        
                                        if signature:
                                            logger.info(f"🔍 New transaction in logs: {signature}")
                                            await subscribe_to_signature(signature)
                                            
                                        # Check for pump.fun logs
                                        pump_logs = [log for log in logs if any(id in log for id in 
                                                    ["BSfD6SHZ", "6EF8rrec"])]
                                        if pump_logs:
                                            logger.info("Found Pump.fun program logs")
                                            await self.handle_transaction(result)
                                            
                                    elif subscription == subscription_ids.get("accountSubscribe"):
                                        # Process account updates
                                        logger.debug(f"Account update for {self.target_wallet}")
                                        if "lamports" in result:
                                            logger.debug(f"New balance: {result['lamports']} lamports")
                                            
                                    elif any(subscription == sub_id for method, sub_id in subscription_ids.items() 
                                           if method.startswith("signature_")):
                                        # Process signature confirmation
                                        logger.info(f"🔍 Transaction confirmed")
                                        logger.debug(f"Confirmation data: {result}")
                                        
                                        # Remove from active signatures once confirmed
                                        signature = next((sig for sig in active_signatures 
                                                        if subscription_ids.get(f"signature_{sig}") == subscription),
                                                       None)
                                        if signature:
                                            active_signatures.remove(signature)
                                            
                                        # Process the confirmed transaction
                                        await self.handle_transaction(result)
                                        
                                    else:
                                        logger.warning(f"Unknown subscription: {subscription}")
                                        
                            except json.JSONDecodeError as e:
                                logger.warning(f"Invalid JSON message: {str(e)}")
                            except Exception as e:
                                logger.error(f"Error processing message: {str(e)}")
                                logger.error(traceback.format_exc())
                                
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                    finally:
                        heartbeat_task.cancel()
                        self.running = False
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                logger.error(traceback.format_exc())
                reconnect_attempts += 1
                
                if reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error("Max reconnection attempts reached. Stopping bot.")
                    self.running = False
                    break
                    
                # Wait before reconnecting
                await asyncio.sleep(self.reconnect_delay)
                logger.info(f"Attempting to reconnect... (attempt {reconnect_attempts})")
                
    async def execute_buy(self, token_mint: str, amount_sol: float = FIXED_BUY_AMOUNT) -> bool:
        """Execute a buy trade for a token using validated settings"""
        try:
            # Convert token mint string to Pubkey
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Convert SOL amount to lamports
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            # Build the buy transaction with validated settings
            tx = await build_buy_tx(
                executor=self.executor,
                token=token_pubkey,
                amount=amount_lamports,
                keypair=self.keypair,
                slippage_bps=self.slippage_bps  # Use 30% slippage
            )
            
            if not tx:
                logger.error("❌ Failed to build buy transaction")
                return False
                
            # Execute the transaction
            result = await self.executor.execute_transaction(tx)
            if result:
                logger.info(f"✅ Buy trade executed successfully! Amount: {amount_sol} SOL")
                return True
            else:
                logger.error("❌ Buy trade execution failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing buy trade: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    async def execute_sell(self, token_mint: str, token_balance: int) -> bool:
        """Execute a sell trade for a token using validated settings"""
        try:
            # Convert token mint string to Pubkey
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Build the sell transaction with validated settings
            tx = await build_sell_tx(
                executor=self.executor,
                token=token_pubkey,
                amount=token_balance,
                keypair=self.keypair,
                slippage_bps=self.slippage_bps  # Use 30% slippage
            )
            
            if not tx:
                logger.error("❌ Failed to build sell transaction")
                return False
                
            # Execute the transaction
            result = await self.executor.execute_transaction(tx)
            if result:
                logger.info(f"✅ Sell trade executed successfully! Amount: {token_balance} tokens")
                return True
            else:
                logger.error("❌ Sell trade execution failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing sell trade: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    async def handle_transaction(self, tx_context: dict) -> bool:
        """Handle a detected transaction from Wallet A"""
        try:
            # Parse the transaction
            trade_info = self.parser.parse_transaction(tx_context)
            if not trade_info:
                logger.info("No trade detected")
                return False
                
            # Extract trade details
            token_mint = trade_info.get("token_mint")
            is_buy = trade_info.get("is_buy")
            
            if not token_mint:
                logger.error("No token mint found in transaction")
                return False
                
            # Check if we have enough SOL for the trade
            balance = await self.executor.get_balance(self.keypair.pubkey())
            if balance is None or balance < 0.06:  # 0.05 + fees
                logger.error(f"Insufficient balance: {balance} SOL")
                return False
                
            if is_buy:
                # Execute buy trade with fixed amount
                return await self.execute_buy(token_mint, amount_sol=0.05)
            else:
                # For sells, get current token balance
                token_pubkey = Pubkey.from_string(token_mint)
                token_balance = await self.executor.get_token_balance(
                    self.keypair.pubkey(),
                    token_pubkey
                )
                
                if not token_balance:
                    logger.error("Failed to get token balance")
                    return False
                    
                # Execute sell trade with full balance
                return await self.execute_sell(token_mint, token_balance)
                
        except Exception as e:
            logger.error(f"Error handling transaction: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping Copy Trading Bot...")
        self.running = False
        await self.executor.cleanup()
        logger.info("Bot stopped")

async def main():
    """Main entry point for the copy trading bot"""
    bot = None
    try:
        # Create the advanced copy trading bot with our configuration
        copy_config = {
            'fixed_buy_amount': 0.05,     # Always invest exactly 0.05 SOL on buys
            'delay_seconds': 2,           # Delay after detecting trade
            'enable_sells': True,         # Whether to copy sell trades
            'enable_buys': True,          # Whether to copy buy trades
            'proportional_selling': True  # Sell proportionally to target wallet
        }
        
        bot = PumpCopyTradingBot(copy_config)
        
        # Check wallet balance
        balance = await bot.trading_bot.get_sol_balance()
        if balance is None:
            logger.error("❌ Could not fetch wallet balance")
            return
        if balance < 0.1:  # Minimum required balance
            logger.error(f"❌ Insufficient starting balance: {balance} SOL")
            logger.error("Please ensure wallet has at least 0.1 SOL before starting")
            return
            
        # Print startup banner
        print("\n🤖 Advanced Copy Trading Bot Starting")
        print("=====================================")
        print(f"🏦 Your wallet: {bot.trading_bot.wallet_pubkey}")
        print(f"💰 Current balance: {balance:.4f} SOL")
        print(f"👀 Watching wallets: {', '.join(MONITORED_WALLETS)}")
        print(f"💰 Buy amount: {copy_config['fixed_buy_amount']} SOL (fixed)")
        print(f"📈 Sell type: {'Proportional' if copy_config['proportional_selling'] else 'Full'}")
        print("=====================================\n")
        
        # Start monitoring the wallets
        print("✅ Bot initialized successfully - starting wallet monitoring")
        
        # Start the WebSocket listener for target wallets
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if bot:
            await bot.close()

if __name__ == "__main__":
    # Set up asyncio for debug mode
    if logging.getLogger().level == logging.DEBUG:
        asyncio.get_event_loop().set_debug(True)
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
