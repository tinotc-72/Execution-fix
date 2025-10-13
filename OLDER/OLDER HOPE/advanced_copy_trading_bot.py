#!/usr/bin/env python3
"""
Advanced Copy Trading Bot using Generalized Pump.Fun Trading System
Monitors target wallets and executes trades using the proven direct trading bot
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import websockets
import aiohttp

from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig, TradeAction, TradeExecutionResult, TradeResult
from listener import fetch_transaction, identify_dex_and_instruction, extract_trade_data
from config import MONITORED_WALLETS
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copy_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from other loggers
logging.getLogger('websockets').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)

class PumpCopyTradingBot:
    """
    Advanced copy trading bot that monitors target wallets and replicates their pump.fun trades
    """
    
    def __init__(self, copy_config: Dict = None):
        self.copy_config = copy_config or {
            'fixed_buy_amount': 0.01,   # Testing with 0.01 SOL per buy
            'delay_seconds': 0,         # No delay - execute immediately
            'enable_sells': True,       # Whether to copy sell trades
            'enable_buys': True,        # Whether to copy buy trades
            'proportional_selling': True  # Sell proportionally to target wallet
        }
        
        # Track our positions for proportional selling
        self.position_tracker = {}  # {token_mint: {'our_balance': int, 'target_initial_balance': int}}
        
        # Initialize trading bot with proven system
        trade_config = TradeConfig(
            sol_amount=0.005,  # Default amount, will be overridden per trade
            max_retries=3,
            slippage_tolerance=0.1,  # 10% slippage for fast execution
            retry_delay=1.0
        )
        self.trading_bot = GeneralizedPumpTradingBot(trade_config)
        
        # Initialize Multi-DEX Trader for all other DEXes
        try:
            from multi_dex_trader import MultiDexTrader
            from config import WALLET
            self.multi_dex_trader = MultiDexTrader(WALLET)
            logger.info("🌐 Multi-DEX Trader initialized (Jupiter, Raydium, Orca, etc.)")
        except Exception as e:
            logger.warning(f"⚠️ Multi-DEX Trader initialization failed: {e}")
            self.multi_dex_trader = None
        
        # WebSocket configuration
        self.helius_ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        
        # Track recent trades to avoid duplicates
        self.processed_signatures = set()
        self.target_wallets = MONITORED_WALLETS
        
        # Performance tracking
        self.stats = {
            'trades_detected': 0,
            'trades_copied': 0,
            'successful_copies': 0,
            'failed_copies': 0,
            'total_volume_sol': 0.0,
            'start_time': datetime.now()
        }
        
        logger.info("🤖 Advanced Copy Trading Bot initialized")
        logger.info(f"📡 Monitoring wallets: {self.target_wallets}")
        logger.info(f"⚙️ Copy config: {self.copy_config}")
    
    async def analyze_target_trade(self, tx_data: Dict, target_wallet: str) -> Optional[Dict]:
        """
        Analyze a target wallet's transaction to extract trade information
        """
        try:
            # Use existing DEX identification from listener.py (which is proven to work)
            dex_info = identify_dex_and_instruction(tx_data)
            if not dex_info:
                return None
            
            dex_name, instruction_data = dex_info
            
            logger.info(f"🎯 Found {dex_name} transaction - analyzing for trades...")
            
            # Enhanced trade detection with proven discriminator analysis
            trade_result = self._analyze_instruction_data(tx_data, target_wallet, dex_name)
            if not trade_result:
                logger.info("❌ No trade detected through instruction or balance analysis")
                return None
            
            # Handle enhanced trade result format
            if 'trade_type' in trade_result:
                # This came from discriminator analysis - more reliable
                trade_type = trade_result['trade_type']
                logger.info(f"✅ DISCRIMINATOR-BASED DETECTION: {trade_type}")
                
                if trade_type == "BUY":
                    trade_action = TradeAction.BUY
                    # Extract from discriminator data
                    sol_amount = trade_result.get('amount', 0) / 1_000_000_000  # Convert to SOL
                    token_amount = 0  # Will be calculated from balance changes if available
                    
                    # Always get token mint from balance changes for BUY
                    balance_data = self._analyze_balance_changes(tx_data, target_wallet, dex_name)
                    if balance_data and 'token_mint' in balance_data:
                        token_mint = balance_data['token_mint']
                        token_amount = balance_data.get('token_change', 0)
                        # Use discriminator SOL amount if available, otherwise balance change
                        if sol_amount > 0:
                            logger.info(f"✅ BUY detected via discriminator: {sol_amount:.6f} SOL → {token_amount:,} tokens of {token_mint[:8]}...")
                        else:
                            sol_amount = abs(balance_data.get('sol_change', 0))
                            logger.info(f"✅ BUY detected via discriminator + balance: {sol_amount:.6f} SOL → {token_amount:,} tokens of {token_mint[:8]}...")
                    else:
                        logger.warning("⚠️ BUY detected but no balance changes found")
                        return None
                        
                elif trade_type in ["SELL", "SELL_ALT"]:
                    trade_action = TradeAction.SELL
                    # Extract from discriminator data
                    token_amount = trade_result.get('amount', 0)
                    sol_amount = 0  # Will be calculated from balance changes
                    
                    # Always get token mint and accurate amounts from balance changes for SELL
                    balance_data = self._analyze_balance_changes(tx_data, target_wallet, dex_name)
                    if balance_data and 'token_mint' in balance_data:
                        token_mint = balance_data['token_mint']
                        sol_amount = abs(balance_data.get('sol_change', 0))
                        token_amount = abs(balance_data.get('token_change', 0))  # Use actual balance change
                        logger.info(f"✅ SELL detected via discriminator + balance: {token_amount:,} tokens → {sol_amount:.6f} SOL of {token_mint[:8]}...")
                    else:
                        logger.warning("⚠️ SELL detected but no balance changes found")
                        return None
                else:
                    logger.warning(f"⚠️ Unknown trade type from discriminator: {trade_type}")
                    return None
                    
            else:
                # This came from balance analysis - traditional approach
                token_mint = trade_result['token_mint']
                sol_change = trade_result['sol_change']
                token_change = trade_result['token_change']
                detected_trade_type = trade_result.get('trade_type')
                
                if detected_trade_type == "BUY":
                    trade_action = TradeAction.BUY
                    sol_amount = abs(sol_change)
                    token_amount = token_change
                    logger.info(f"✅ BUY detected via balance: {sol_amount:.6f} SOL → {token_amount:,} tokens of {token_mint[:8]}...")
                elif detected_trade_type == "SELL":
                    trade_action = TradeAction.SELL
                    sol_amount = sol_change
                    token_amount = abs(token_change)
                    logger.info(f"✅ SELL detected via balance: {token_amount:,} tokens → {sol_amount:.6f} SOL of {token_mint[:8]}...")
                else:
                    logger.debug(f"Balance changes don't indicate a clear trade type: {detected_trade_type}")
                    return None
            
            return {
                'action': trade_action,
                'token_mint': token_mint,
                'sol_amount': sol_amount,
                'token_amount': token_amount,
                'target_wallet': target_wallet,
                'signature': tx_data.get('signature', ''),
                'timestamp': datetime.now(),
                'dex': dex_name,
                'instruction': 'BUY' if trade_action == TradeAction.BUY else 'SELL'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing target trade: {e}")
            return None
    
    def _extract_sol_amount_from_tx(self, tx_data: Dict, wallet: str) -> float:
        """Extract SOL amount spent/received from transaction"""
        try:
            # Get pre and post balances
            pre_balances = tx_data.get('meta', {}).get('preBalances', [])
            post_balances = tx_data.get('meta', {}).get('postBalances', [])
            account_keys = tx_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            # Find wallet index
            wallet_index = -1
            for i, account in enumerate(account_keys):
                if account == wallet:
                    wallet_index = i
                    break
            
            if wallet_index >= 0 and wallet_index < len(pre_balances) and wallet_index < len(post_balances):
                # Calculate difference (negative means spent, positive means received)
                balance_change = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1_000_000_000
                return abs(balance_change)  # Return absolute value
            
        except Exception as e:
            logger.error(f"Error extracting SOL amount: {e}")
        
        return 0.0
    
    def _extract_token_amount_from_tx(self, tx_data: Dict, token_mint: str, wallet: str) -> int:
        """Extract token amount from transaction"""
        try:
            # Look for token transfer instructions
            instructions = tx_data.get('transaction', {}).get('message', {}).get('instructions', [])
            
            for instruction in instructions:
                if instruction.get('programId') == 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA':
                    # This is a token instruction
                    if 'parsed' in instruction and instruction['parsed'].get('type') == 'transfer':
                        info = instruction['parsed']['info']
                        if info.get('mint') == token_mint:
                            return int(info.get('amount', 0))
            
        except Exception as e:
            logger.error(f"Error extracting token amount: {e}")
        
        return 0
    
    async def get_target_wallet_token_balance(self, wallet: str, token_mint: str) -> int:
        """Get target wallet's current token balance"""
        try:
            # This would require additional RPC calls to get target wallet's token balance
            # For now, we'll use transaction analysis to estimate
            return 0
        except Exception as e:
            logger.error(f"Error getting target wallet balance: {e}")
            return 0
    
    def calculate_copy_amount(self, target_trade: Dict) -> float:
        """Calculate how much to copy trade - always 0.01 SOL for buys (testing)"""
        try:
            if target_trade['action'] == TradeAction.BUY:
                # Always invest exactly 0.01 SOL regardless of target trade size
                return self.copy_config['fixed_buy_amount']
            
            elif target_trade['action'] == TradeAction.SELL:
                # For sells, calculate proportional amount based on target's sell percentage
                return self._calculate_proportional_sell_amount(target_trade)
                
        except Exception as e:
            logger.error(f"Error calculating copy amount: {e}")
            return self.copy_config['fixed_buy_amount']
    
    def _calculate_proportional_sell_amount(self, target_trade: Dict) -> int:
        """Calculate how many tokens to sell proportionally"""
        try:
            token_mint = target_trade['token_mint']
            target_sell_amount = target_trade['token_amount']
            
            # Check if we have position tracking for this token
            if token_mint not in self.position_tracker:
                logger.warning(f"No position tracking for {token_mint[:8]}... - selling all")
                return 0  # Will be handled as "sell all" in execute_copy_trade
            
            position = self.position_tracker[token_mint]
            our_current_balance = position.get('our_balance', 0)
            
            # If we don't have any tokens, nothing to sell
            if our_current_balance == 0:
                return 0
            
            # Estimate target's sell percentage
            # This is a simplified approach - you might want to implement more sophisticated tracking
            target_initial_balance = position.get('target_initial_balance', target_sell_amount)
            
            if target_initial_balance > 0:
                sell_percentage = min(target_sell_amount / target_initial_balance, 1.0)
            else:
                sell_percentage = 1.0  # Sell all if we can't determine percentage
            
            # Calculate our proportional sell amount
            our_sell_amount = int(our_current_balance * sell_percentage)
            
            logger.info(f"📊 Proportional sell calculation:")
            logger.info(f"   Target selling: {target_sell_amount:,} tokens ({sell_percentage:.1%})")
            logger.info(f"   Our balance: {our_current_balance:,} tokens")
            logger.info(f"   Our sell amount: {our_sell_amount:,} tokens")
            
            return our_sell_amount
            
        except Exception as e:
            logger.error(f"Error calculating proportional sell: {e}")
            return 0
    
    async def execute_copy_trade(self, target_trade: Dict) -> Dict:
        """Execute a copy trade based on target wallet's trade"""
        
        copy_result = {
            'success': False,
            'signature': None,
            'error': None,
            'amount': 0,
            'timestamp': datetime.now()
        }
        
        try:
            token_mint = target_trade['token_mint']
            action = target_trade['action']
            
            logger.info(f"🔄 Executing copy trade: {action.value} {token_mint[:8]}...")
            
            if action == TradeAction.BUY and self.copy_config['enable_buys']:
                copy_amount = self.copy_config['fixed_buy_amount']
                token_mint = target_trade['token_mint']
                dex = target_trade.get('dex', 'UNKNOWN')
                
                logger.info(f"💰 Copy buying {copy_amount:.3f} SOL worth of {token_mint[:8]}... on {dex}")
                
                # Handle different DEXes
                if dex in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"]:
                    logger.info(f"🎯 Attempting to copy {dex} trade for token: {token_mint}")
                    
                    # Try different approaches based on the DEX type
                    if dex in ["PUMP_ROUTER", "PUMP_TRADING"]:
                        # For router-based trades, try with a more flexible approach
                        logger.info(f"🔄 Router-based trade detected - using flexible trading approach")
                        result = await self._execute_router_trade(token_mint, copy_amount, target_trade)
                    else:
                        # For standard pump trades, use the regular generalized bot
                        result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                    
                    # Process the result
                    if result.result.value == 'success':
                        copy_result['success'] = True
                        copy_result['signature'] = result.signature
                        copy_result['amount'] = result.tokens_amount
                        self.stats['successful_copies'] += 1
                        self.stats['total_volume_sol'] += copy_amount
                        
                        # Track our position for proportional selling
                        self.position_tracker[token_mint] = {
                            'our_balance': result.tokens_amount,
                            'target_initial_balance': target_trade.get('token_amount', 0),
                            'buy_timestamp': datetime.now(),
                            'dex': dex
                        }
                        
                        logger.info(f"✅ Copy buy successful: {result.tokens_amount:,} tokens")
                        logger.info(f"📊 TX: https://solscan.io/tx/{result.signature}")
                        logger.info(f"📍 Position tracked for proportional selling")
                    else:
                        copy_result['error'] = result.error_message
                        self.stats['failed_copies'] += 1
                        
                        # Provide better error categorization
                        if "Router-only token" in str(result.error_message):
                            logger.info(f"📋 Router-only token detected - trade logged for future implementation")
                        elif "Invalid token" in str(result.error_message):
                            logger.error(f"❌ Token validation failed - possibly not a pump.fun token")
                        else:
                            logger.error(f"❌ Copy buy failed: {result.error_message}")
                        
                elif dex in ["RAYDIUM", "ORCA", "JUPITER", "PHOENIX", "OPENBOOK", "JUPITER_V6", "JUPITER_V4"]:
                    # NOW SUPPORTS ALL DEX TRADES via Multi-DEX Trader!
                    logger.info(f"🔄 {dex} trade detected - Token: {token_mint[:8]}...")
                    logger.info(f"� COPYING {dex} TRADE via Multi-DEX Trader!")
                    logger.info(f"📝 Target invested {target_trade.get('sol_amount', 0):.6f} SOL")
                    logger.info(f"� Our copy amount: {copy_amount:.6f} SOL")
                    logger.info(f"�📊 Original TX: https://solscan.io/tx/{target_trade.get('signature', 'unknown')}")
                    
                    # Import and use Multi-DEX Trader
                    try:
                        from multi_dex_trader import multi_dex_trader
                        
                        # Execute multi-DEX trade
                        result = await multi_dex_trader.buy_token(
                            token_mint=token_mint,
                            sol_amount=copy_amount,
                            preferred_dex=dex
                        )
                        
                        if result.success:
                            copy_result['success'] = True
                            copy_result['signature'] = result.signature
                            copy_result['amount'] = copy_amount
                            copy_result['dex_used'] = result.dex_used
                            copy_result['tokens_received'] = result.output_amount
                            
                            self.stats['successful_copies'] += 1
                            logger.info(f"✅ {dex} COPY SUCCESS via {result.dex_used}: {result.signature[:8]}...")
                            logger.info(f"🎯 Received: {result.output_amount:,} tokens")
                            logger.info(f"🔗 Our TX: https://solscan.io/tx/{result.signature}")
                            
                            # Track position for future sells
                            self.position_tracker[token_mint] = {
                                'our_balance': result.output_amount,
                                'target_initial_balance': target_trade.get('token_amount', result.output_amount),
                                'dex': result.dex_used,
                                'buy_signature': result.signature
                            }
                        else:
                            copy_result['error'] = f'{dex} copy failed: {result.error}'
                            self.stats['failed_copies'] += 1
                            logger.error(f"❌ {dex} copy failed: {result.error}")
                            
                    except Exception as multi_dex_error:
                        copy_result['error'] = f'Multi-DEX trader error: {multi_dex_error}'
                        self.stats['failed_copies'] += 1
                        logger.error(f"❌ Multi-DEX trader failed: {multi_dex_error}")
                    
                    # Track the trade
                    self.stats['trades_detected'] += 1
                    
                else:
                    logger.warning(f"⚠️ Unknown DEX: {dex} - cannot copy trade")
                    copy_result['error'] = f'Unknown DEX: {dex}'
            
            elif action == TradeAction.SELL and self.copy_config['enable_sells']:
                token_mint = target_trade['token_mint']
                dex = target_trade.get('dex', 'UNKNOWN')
                
                # Check if we even have this token before trying to sell
                if token_mint not in self.position_tracker:
                    logger.info(f"💡 SELL detected for {token_mint[:8]}... but we don't own this token")
                    logger.info(f"📊 Target trade: {target_trade['token_amount']:,} tokens → {target_trade['sol_amount']:.6f} SOL")
                    logger.info(f"🎯 Instead, let's BUY this token since target is actively trading it!")
                    
                    # Convert this to a BUY opportunity since the target is actively trading this token
                    copy_amount = self.copy_config['fixed_buy_amount']
                    logger.info(f"💰 Buying {copy_amount:.3f} SOL worth of {token_mint[:8]}... (target is trading it)")
                    
                    if dex in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"]:
                        result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                        
                        if result.result.value == 'success':
                            copy_result['success'] = True
                            copy_result['signature'] = result.signature
                            copy_result['amount'] = result.tokens_amount
                            self.stats['successful_copies'] += 1
                            self.stats['total_volume_sol'] += copy_amount
                            
                            # Track our position for future selling
                            self.position_tracker[token_mint] = {
                                'our_balance': result.tokens_amount,
                                'target_initial_balance': target_trade.get('token_amount', 0),
                                'buy_timestamp': datetime.now(),
                                'dex': dex
                            }
                            
                            logger.info(f"✅ Opportunistic buy successful: {result.tokens_amount:,} tokens")
                            logger.info(f"📊 TX: https://solscan.io/tx/{result.signature}")
                            logger.info(f"📍 Position tracked for future proportional selling")
                        else:
                            copy_result['error'] = result.error_message
                            self.stats['failed_copies'] += 1
                            logger.error(f"❌ Opportunistic buy failed: {result.error_message}")
                    else:
                        copy_result['error'] = f'{dex} trading not yet supported'
                    
                    return copy_result
                
                # Execute proportional copy sell if we have a position
                if self.copy_config['proportional_selling']:
                    # Calculate proportional sell amount
                    proportional_sell_amount = self._calculate_proportional_sell_amount(target_trade)
                    
                    if proportional_sell_amount > 0:
                        # Check if we have this position and what DEX it was bought on
                        position_dex = self.position_tracker.get(token_mint, {}).get('dex', 'UNKNOWN')
                        
                        if position_dex in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"]:
                            logger.info(f"💸 Copy selling {proportional_sell_amount:,} tokens of {token_mint[:8]} (proportional) on PUMP...")
                            
                            result = await self.trading_bot.sell_token(token_mint, proportional_sell_amount)
                            
                            if result.result.value == 'success':
                                copy_result['success'] = True
                                copy_result['signature'] = result.signature
                                copy_result['amount'] = result.tokens_amount
                                self.stats['successful_copies'] += 1
                                self.stats['total_volume_sol'] += result.sol_amount
                                
                                # Update our position tracking
                                if token_mint in self.position_tracker:
                                    self.position_tracker[token_mint]['our_balance'] -= result.tokens_amount
                                    if self.position_tracker[token_mint]['our_balance'] <= 0:
                                        del self.position_tracker[token_mint]  # Position closed
                                
                                logger.info(f"✅ Proportional sell successful: {result.tokens_amount:,} tokens → {result.sol_amount:.6f} SOL")
                                logger.info(f"📊 TX: https://solscan.io/tx/{result.signature}")
                            else:
                                copy_result['error'] = result.error_message
                                self.stats['failed_copies'] += 1
                                logger.error(f"❌ Proportional sell failed: {result.error_message}")
                        else:
                            logger.info(f"🔄 {dex} sell detected - Token: {token_mint[:8]}...")
                            logger.info(f"💡 No position to sell (only PUMP.FUN positions can be sold)")
                            logger.info(f"📊 Target sell TX: https://solscan.io/tx/{target_trade.get('signature', 'unknown')}")
                            copy_result['error'] = f'No {dex} position to sell - only PUMP.FUN positions supported'
                    else:
                        logger.info(f"⏭️ No proportional sell needed for {token_mint[:8]}...")
                        copy_result['error'] = 'No proportional sell amount calculated'
                else:
                    # Fallback: sell all our tokens
                    current_balance = await self.trading_bot.get_token_balance_by_mint(token_mint)
                    
                    if current_balance > 0:
                        logger.info(f"💸 Copy selling ALL {current_balance:,} tokens of {token_mint[:8]}...")
                        
                        result = await self.trading_bot.sell_token(token_mint, current_balance)
                        
                        if result.result.value == 'success':
                            copy_result['success'] = True
                            copy_result['signature'] = result.signature
                            copy_result['amount'] = result.tokens_amount
                            self.stats['successful_copies'] += 1
                            self.stats['total_volume_sol'] += result.sol_amount
                            
                            # Clear position tracking
                            if token_mint in self.position_tracker:
                                del self.position_tracker[token_mint]
                            
                            logger.info(f"✅ Full sell successful: {result.tokens_amount:,} tokens → {result.sol_amount:.6f} SOL")
                            logger.info(f"📊 TX: https://solscan.io/tx/{result.signature}")
                        else:
                            copy_result['error'] = result.error_message
                            self.stats['failed_copies'] += 1
                            logger.error(f"❌ Full sell failed: {result.error_message}")
                    else:
                        logger.warning(f"⚠️ No tokens to sell for {token_mint[:8]}...")
                        copy_result['error'] = 'No tokens to sell'
            
            else:
                logger.info(f"⏭️ Skipping {action.value} (disabled in config)")
                copy_result['error'] = f'{action.value} disabled in config'
            
        except Exception as e:
            logger.error(f"❌ Copy trade execution error: {e}")
            copy_result['error'] = str(e)
            self.stats['failed_copies'] += 1
        
        return copy_result
    
    async def handle_target_transaction(self, signature: str, target_wallet: str, logs: List[str] = None, tx_data: Dict = None):
        """Handle a detected transaction from target wallet - ULTRA FAST VERSION based on OLDER scripts"""
        
        # Avoid processing duplicates
        if signature in self.processed_signatures:
            return
        
        self.processed_signatures.add(signature)
        
        # Keep only recent signatures (last 500 for speed)
        if len(self.processed_signatures) > 500:
            self.processed_signatures = set(list(self.processed_signatures)[-250:])
        
        try:
            logger.info(f"⚡ ULTRA-FAST analyzing: {signature[:8]}... from {target_wallet[:8]}...")
            
            # ULTRA FAST PATH 1: Use logs for instant detection if available
            if logs:
                fast_result = self._ultra_fast_log_detection(logs, target_wallet, signature)
                if fast_result:
                    logger.info(f"🚀 INSTANT detection via logs: {fast_result['action']} {fast_result['token_mint'][:8]}...")
                    copy_result = await self._instant_execute_trade(fast_result)
                    self._track_result(copy_result)
                    return
            
            # ULTRA FAST PATH 2: Minimal transaction fetch only if needed
            if not tx_data:
                tx_data = await fetch_transaction(signature)
                if not tx_data:
                    logger.debug("Could not fetch transaction data")
                    return
            
            # ULTRA FAST PATH 3: Quick DEX + discriminator check
            trade_info = self._ultra_fast_discriminator_detection(tx_data, target_wallet)
            if not trade_info:
                logger.debug("No pump trade detected in ultra-fast analysis")
                return
            
            self.stats['trades_detected'] += 1
            
            logger.info(f"⚡ ULTRA-FAST trade: {trade_info['action']} {trade_info['token_mint'][:8]}... on {trade_info['dex']}")
            
            # ULTRA FAST PATH 4: Immediate execution without validation delays
            copy_result = await self._instant_execute_trade(trade_info)
            self._track_result(copy_result)
            
        except Exception as e:
            logger.error(f"Error in ultra-fast handler: {e}")
            self.stats['failed_copies'] += 1
    
    async def start_monitoring(self):
        """Start monitoring target wallets - ULTRA FAST VERSION"""
        logger.info("🚀 Starting ULTRA-FAST copy trading bot...")
        logger.info(f"📡 Monitoring {len(self.target_wallets)} wallets")
        
        while True:
            try:
                async with websockets.connect(self.helius_ws_url) as ws:
                    # Subscribe to all target wallets
                    for wallet in self.target_wallets:
                        subscription = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "logsSubscribe",
                            "params": [
                                {"mentions": [wallet]},
                                {"commitment": "confirmed"}  # Changed from "finalized" for faster detection
                            ]
                        }
                        await ws.send(json.dumps(subscription))
                        logger.info(f"✅ Subscribed to wallet: {wallet[:8]}...")
                    
                    logger.info("⚡ ULTRA-FAST copy trading bot active - waiting for trades...")
                    
                    # Listen for messages with maximum speed priority
                    while True:
                        try:
                            msg = await ws.recv()
                            data = json.loads(msg)
                            
                            result = data.get("params", {}).get("result", {})
                            logs = result.get("value", {}).get("logs", [])
                            signature = result.get("value", {}).get("signature")
                            
                            if not logs or not signature:
                                continue  # Skip irrelevant messages
                            
                            # ULTRA FAST PATH 1: Instant log detection (NO RPC CALL!)
                            for wallet in self.target_wallets:
                                # Quick check if wallet is in logs
                                wallet_in_logs = any(wallet in log for log in logs)
                                if not wallet_in_logs:
                                    continue
                                
                                logger.info(f"⚡ INSTANT detection: {signature[:8]}... from {wallet[:8]}...")
                                
                                # Try ultra-fast log detection immediately
                                fast_result = self._ultra_fast_log_detection(logs, wallet, signature)
                                if fast_result:
                                    logger.info(f"🚀 INSTANT LOG TRADE: {fast_result['action'].value} {fast_result['token_mint'][:8]}...")
                                    
                                    # Execute immediately in background for maximum speed
                                    asyncio.create_task(self._execute_instant_trade(fast_result))
                                    break  # Found trade, move to next message
                            
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("WebSocket connection closed, reconnecting...")
                            break
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            continue
            
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                logger.info("Reconnecting in 2 seconds...")
                await asyncio.sleep(2)  # Reduced from 5 to 2 for faster reconnection
    
    def print_stats(self):
        """Print current performance statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        print(f"\n📊 COPY TRADING BOT STATISTICS")
        print("=" * 50)
        print(f"⏱️  Uptime: {uptime}")
        print(f"🎯 Trades Detected: {self.stats['trades_detected']}")
        print(f"📋 Trades Copied: {self.stats['trades_copied']}")
        print(f"✅ Successful Copies: {self.stats['successful_copies']}")
        print(f"❌ Failed Copies: {self.stats['failed_copies']}")
        print(f"💰 Total Volume: {self.stats['total_volume_sol']:.6f} SOL")
        
        if self.stats['trades_copied'] > 0:
            success_rate = (self.stats['successful_copies'] / self.stats['trades_copied']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("=" * 50)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("🛑 Shutting down copy trading bot...")
        if self.trading_bot:
            await self.trading_bot.close()
        self.print_stats()

    def _ultra_fast_log_detection(self, logs: List[str], target_wallet: str, signature: str) -> Optional[Dict]:
        """
        ULTRA FAST: Detect trades directly from WebSocket logs without RPC calls
        Based on proven patterns from OLDER scripts - PumpBuy/PumpSell detection
        """
        try:
            # ULTRA FAST: Look for proven pump.fun instruction patterns in logs
            pump_instruction = None
            token_mint = None
            
            for log in logs:
                # FASTEST PATH: Check for pump trade instructions in logs (UPDATED PATTERNS)
                if any(pattern in log for pattern in [
                    "Program log: Instruction: PumpBuy",
                    "Program log: Instruction: Buy",
                    "Program log: Instruction: PumpAmmSwap"
                ]):
                    pump_instruction = "BUY"
                    logger.info(f"🚀 INSTANT BUY detection from log: {log}")
                elif any(pattern in log for pattern in [
                    "Program log: Instruction: PumpSell", 
                    "Program log: Instruction: Sell",
                    "Program log: Instruction: PumpAmmSell"
                ]):
                    pump_instruction = "SELL"
                    logger.info(f"🚀 INSTANT SELL detection from log: {log}")
                elif "Program log: Token:" in log:
                    # Extract token mint from log: "Program log: Token: ERGKydJayFVtBogci46Ht4U3otjJgchiYWo83mT1Kgw5"
                    try:
                        token_mint = log.split("Program log: Token: ")[1].strip()
                        logger.info(f"🎯 Token extracted from log: {token_mint[:8]}...")
                    except:
                        continue
            
            # If we found both instruction and token from logs, we can execute immediately!
            if pump_instruction and token_mint:
                logger.info(f"⚡ INSTANT DETECTION: {pump_instruction} {token_mint[:8]}... (NO RPC CALL NEEDED!)")
                
                return {
                    'action': TradeAction.BUY if pump_instruction == "BUY" else TradeAction.SELL,
                    'token_mint': token_mint,
                    'sol_amount': 0.01,  # Fixed for speed
                    'token_amount': 0,
                    'target_wallet': target_wallet,
                    'signature': signature,
                    'timestamp': datetime.now(),
                    'dex': 'PUMP',
                    'detection_method': 'ultra_fast_log_instant'
                }
            
            # FAST FALLBACK: Check for other pump patterns in logs (UPDATED program IDs)
            pump_programs = [
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # Original Trading program
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Router program (SEEN in real transaction)
                "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # AMM program (SEEN in real transaction)
                "GDDMwNyyx8uB6zrqwBFHjLLG3TBYk2F8Az4yrQC5RzMp",  # PUMP
                "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95"   # PUMP_NEW
            ]
            
            # Quick scan for pump.fun program invocation
            is_pump_trade = False
            trade_type = None
            dex_name = "PUMP"
            
            for log in logs:
                # Check for program invocation first (UPDATED with real transaction programs)
                for prog in pump_programs:
                    if f"Program {prog} invoke" in log:
                        is_pump_trade = True
                        if prog == "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW":
                            dex_name = "PUMP_ROUTER"
                        elif prog == "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA":
                            dex_name = "PUMP_AMM"
                        elif prog == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                            dex_name = "PUMP_TRADING"
                        logger.info(f"🎯 Pump program detected: {dex_name} ({prog[:8]}...)")
                        break
                
                # Instant trade type detection from logs (UPDATED patterns based on real transactions)
                if any(pattern in log for pattern in [
                    "Program log: Instruction: Buy",
                    "Program log: Instruction: PumpBuy", 
                    "Program log: Instruction: PumpAmmSwap",
                    "Instruction: Buy",
                    "Instruction: PumpBuy"
                ]):
                    trade_type = "BUY"
                    logger.info(f"🎯 BUY detected from log: {log[:100]}...")
                elif any(pattern in log for pattern in [
                    "Program log: Instruction: Sell",
                    "Program log: Instruction: PumpSell",
                    "Program log: Instruction: PumpAmmSell", 
                    "Instruction: Sell",
                    "Instruction: PumpSell"
                ]):
                    trade_type = "SELL"
                    logger.info(f"🎯 SELL detected from log: {log[:100]}...")
                elif "Buy" in log and "Instruction:" in log:
                    trade_type = "BUY"
                elif "Sell" in log and "Instruction:" in log:
                    trade_type = "SELL"
            
            if not is_pump_trade or not trade_type:
                return None
            
            # Try to extract token from logs (ultra-fast method)
            token_mint = self._extract_token_from_logs_fast(logs)
            if not token_mint:
                return None  # Skip if we can't get token quickly
            
            logger.info(f"⚡ INSTANT LOG DETECTION: {trade_type} of {token_mint[:8]}... on {dex_name}")
            
            return {
                'action': TradeAction.BUY if trade_type == "BUY" else TradeAction.SELL,
                'token_mint': token_mint,
                'sol_amount': 0.01,  # Use fixed amount for speed
                'token_amount': 0,   # Will be calculated in execution if needed
                'target_wallet': target_wallet,
                'signature': signature,
                'timestamp': datetime.now(),
                'dex': dex_name,
                'detection_method': 'ultra_fast_logs'
            }
            
        except Exception as e:
            logger.debug(f"Ultra-fast log detection failed: {e}")
            return None
    
    def _extract_token_from_logs_fast(self, logs: List[str]) -> Optional[str]:
        """Extract token address from logs using fastest possible method"""
        try:
            # Look for direct token mentions in logs (fastest)
            for log in logs:
                if "Token:" in log or "Mint:" in log:
                    parts = log.split(":")
                    if len(parts) > 1:
                        potential_token = parts[-1].strip()
                        if len(potential_token) == 44:  # Valid Solana address length
                            try:
                                from solders.pubkey import Pubkey
                                Pubkey.from_string(potential_token)  # Validate
                                return potential_token
                            except:
                                continue
            
            # Look in ATA initialization (reliable and fast)
            for i, log in enumerate(logs):
                if "Initialize the associated token account" in log:
                    # Look in surrounding logs for token
                    start = max(0, i - 3)
                    end = min(len(logs), i + 3)
                    for j in range(start, end):
                        if "Account:" in logs[j] or "Mint:" in logs[j]:
                            parts = logs[j].split(":")
                            if len(parts) > 1:
                                potential_token = parts[-1].strip().split()[0]
                                if len(potential_token) == 44:
                                    try:
                                        from solders.pubkey import Pubkey
                                        Pubkey.from_string(potential_token)
                                        return potential_token
                                    except:
                                        continue
            
            return None
        except:
            return None
    
    def _ultra_fast_discriminator_detection(self, tx_data: Dict, target_wallet: str) -> Optional[Dict]:
        """
        ULTRA FAST: Detect trades using proven discriminator patterns from OLDER scripts
        """
        try:
            # Known discriminators from proven working OLDER scripts
            ULTRA_FAST_DISCRIMINATORS = {
                "66063d1201daebea": ("BUY", "PUMP"),
                "33e685a4017f83ad": ("SELL", "PUMP"), 
                "b712469c946da122": ("SELL", "PUMP")
            }
            
            instructions = tx_data.get('transaction', {}).get('message', {}).get('instructions', [])
            account_keys = tx_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            # Quick wallet check first for speed
            if target_wallet not in account_keys:
                return None
            
            # Ultra-fast discriminator scan - only check PUMP programs
            pump_program_indices = []
            for i, account in enumerate(account_keys):
                if account in [
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # PUMP_TRADING
                    "GDDMwNyyx8uB6zrqwBFHjLLG3TBYk2F8Az4yrQC5RzMp",   # PUMP
                    "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",   # PUMP_NEW
                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"    # PUMP_ROUTER
                ]:
                    pump_program_indices.append(i)
            
            if not pump_program_indices:
                return None
            
            # Scan only pump instructions for maximum speed
            for instruction in instructions:
                program_id_index = instruction.get('programIdIndex')
                if program_id_index not in pump_program_indices:
                    continue
                    
                program_id = account_keys[program_id_index]
                data = instruction.get('data', '')
                
                if len(data) >= 16:
                    try:
                        import base64
                        decoded = base64.b64decode(data)
                        discriminator_hex = decoded[:8].hex()
                        
                        if discriminator_hex in ULTRA_FAST_DISCRIMINATORS:
                            trade_type, dex = ULTRA_FAST_DISCRIMINATORS[discriminator_hex]
                            
                            # Ultra-fast token extraction from balance changes
                            token_mint = self._ultra_fast_token_from_balances(tx_data, target_wallet)
                            if not token_mint:
                                continue
                            
                            logger.info(f"⚡ ULTRA-FAST discriminator: {trade_type} of {token_mint[:8]}...")
                            
                            return {
                                'action': TradeAction.BUY if trade_type == "BUY" else TradeAction.SELL,
                                'token_mint': token_mint,
                                'sol_amount': 0.01,  # Fixed for speed
                                'token_amount': 0,
                                'target_wallet': target_wallet,
                                'signature': tx_data.get('signature', ''),
                                'timestamp': datetime.now(),
                                'dex': dex,
                                'detection_method': 'ultra_fast_discriminator'
                            }
                    except:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Ultra-fast discriminator detection failed: {e}")
            return None

    def _ultra_fast_token_from_balances(self, tx_data: Dict, target_wallet: str) -> Optional[str]:
        """Ultra-fast token extraction from balance changes"""
        try:
            # Get token balance changes quickly
            pre_tokens = tx_data.get('meta', {}).get('preTokenBalances', [])
            post_tokens = tx_data.get('meta', {}).get('postTokenBalances', [])
            
            # Quick scan for target wallet's token changes
            target_tokens = set()
            
            for balance in post_tokens:
                if balance.get('owner') == target_wallet:
                    mint = balance.get('mint')
                    if mint and mint != "So11111111111111111111111111111111111111112":  # Skip WSOL
                        target_tokens.add(mint)
            
            for balance in pre_tokens:
                if balance.get('owner') == target_wallet:
                    mint = balance.get('mint')
                    if mint and mint != "So11111111111111111111111111111111111111112":  # Skip WSOL
                        target_tokens.add(mint)
            
            # Return first non-WSOL token (good enough for speed)
            if target_tokens:
                return next(iter(target_tokens))
            
            return None
        except:
            return None

    async def _execute_instant_trade(self, trade_info: Dict) -> Dict:
        """
        ULTRA FAST: Execute trade immediately with fire-and-forget pattern
        Based on proven patterns from OLDER scripts for maximum speed
        """
        copy_result = {
            'success': False,
            'signature': None,
            'error': None,
            'trade_info': trade_info,
            'execution_time_ms': 0
        }
        
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 INSTANT EXECUTE: {trade_info['action'].value} {trade_info['token_mint'][:8]}...")
            
            # ULTRA FAST: Fire-and-forget execution (no waiting for confirmation)
            if trade_info['action'] == TradeAction.BUY:
                logger.info(f"💰 INSTANT BUY: {trade_info['sol_amount']} SOL")
                
                # Try generalized bot first (fastest path)
                result = await self.trading_bot.buy_token(
                    token_mint=trade_info['token_mint'],
                    sol_amount=trade_info['sol_amount']
                )
                
                if result and result.get('success'):
                    copy_result.update(result)
                    self.stats['successful_copies'] += 1
                    logger.info(f"✅ INSTANT BUY SUCCESS: {result.get('signature', '')[:8]}...")
                else:
                    # Ultra-fast fallback to production bot
                    logger.info("🔄 Instant fallback to production bot...")
                    result = await self.production_bot.buy_token(
                        token_mint=trade_info['token_mint'],
                        sol_amount=trade_info['sol_amount']
                    )
                    
                    if result and result.get('success'):
                        copy_result.update(result)
                        self.stats['successful_copies'] += 1
                        logger.info(f"✅ INSTANT FALLBACK BUY SUCCESS: {result.get('signature', '')[:8]}...")
                    else:
                        copy_result['error'] = f"Both bots failed: {result.get('error', 'Unknown error')}"
                        self.stats['failed_copies'] += 1
            
            elif trade_info['action'] == TradeAction.SELL:
                logger.info(f"💸 INSTANT SELL: {trade_info['token_mint'][:8]}...")
                
                # Check if we own the token first (ultra-fast check)
                try:
                    # Skip complex balance checks for maximum speed
                    # Just attempt the sell, if it fails we'll do opportunistic buy
                    logger.info(f"� Attempting instant sell...")
                    
                    result = await self.trading_bot.sell_token(
                        token_mint=trade_info['token_mint'],
                        percentage=100  # Sell all for speed
                    )
                    
                    if result and result.get('success'):
                        copy_result.update(result)
                        self.stats['successful_copies'] += 1
                        logger.info(f"✅ INSTANT SELL SUCCESS: {result.get('signature', '')[:8]}...")
                    else:
                        # If sell fails, try opportunistic buy instead
                        logger.info(f"💡 Sell failed - trying opportunistic buy...")
                        
                        result = await self.trading_bot.buy_token(
                            token_mint=trade_info['token_mint'],
                            sol_amount=0.01
                        )
                        
                        if result and result.get('success'):
                            copy_result.update(result)
                            self.stats['successful_copies'] += 1
                            logger.info(f"✅ OPPORTUNISTIC BUY SUCCESS: {result.get('signature', '')[:8]}...")
                        else:
                            copy_result['error'] = f"Both sell and opportunistic buy failed: {result.get('error', 'Unknown error')}"
                            self.stats['failed_copies'] += 1
                
                except Exception as sell_error:
                    # Handle any errors in the sell attempt
                    logger.warning(f"⚠️ Sell attempt failed, trying opportunistic buy: {sell_error}")
                    
                    try:
                        result = await self.trading_bot.buy_token(
                            token_mint=trade_info['token_mint'],
                            sol_amount=0.01
                        )
                        
                        if result and result.get('success'):
                            copy_result.update(result)
                            self.stats['successful_copies'] += 1
                            logger.info(f"✅ OPPORTUNISTIC BUY SUCCESS: {result.get('signature', '')[:8]}...")
                        else:
                            copy_result['error'] = f"Both sell and opportunistic buy failed: {result.get('error', 'Unknown error')}"
                            self.stats['failed_copies'] += 1
                    except Exception as buy_error:
                        copy_result['error'] = f"All trading attempts failed: {buy_error}"
                        self.stats['failed_copies'] += 1
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            copy_result['execution_time_ms'] = execution_time
            
            self.stats['trades_copied'] += 1
            self.stats['total_volume_sol'] += trade_info['sol_amount']
            
            logger.info(f"⚡ INSTANT EXECUTION COMPLETE: {execution_time:.1f}ms")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            copy_result['execution_time_ms'] = execution_time
            copy_result['error'] = str(e)
            self.stats['failed_copies'] += 1
            logger.error(f"❌ INSTANT EXECUTION ERROR: {e}")
        
        return copy_result
    
    def _detect_enhanced_trade_data(self, tx_data: Dict, target_wallet: str, dex_name: str) -> Optional[Dict]:
        """
        Enhanced trade detection using proven discriminator analysis from OLDER files
        """
        try:
            # Known discriminators from proven working trades
            KNOWN_DISCRIMINATORS = {
                "66063d1201daebea": "BUY",    # Proven buy discriminator from OLDER files
                "33e685a4017f83ad": "SELL",   # Proven sell discriminator from OLDER files
                "b712469c946da122": "SELL_ALT"  # Alternative sell discriminator
            }
            
            instructions = tx_data.get('transaction', {}).get('message', {}).get('instructions', [])
            account_keys = tx_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            # Check if target wallet is involved
            if target_wallet not in account_keys:
                return None
            
            # Analyze each instruction for trade patterns
            for instruction in instructions:
                program_id_index = instruction.get('programIdIndex')
                if program_id_index is None:
                    continue
                    
                program_id = account_keys[program_id_index]
                
                # Check if this is a PUMP program instruction
                if dex_name in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"] and program_id in [
                    "GDDMwNyyx8uB6zrqwBFHjLLG3TBYk2F8Az4yrQC5RzMp",  # PUMP
                    "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",  # PUMP_NEW
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # Trading program
                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"    # Router program
                ]:
                    data = instruction.get('data', '')
                    if len(data) >= 16:  # At least 8 bytes for discriminator + some data
                        try:
                            # Decode instruction data
                            import base64
                            decoded = base64.b64decode(data)
                            discriminator_hex = decoded[:8].hex()
                            
                            logger.info(f"🔍 Instruction data analysis:")
                            logger.info(f"   Program: {program_id}")
                            logger.info(f"   Discriminator: {discriminator_hex}")
                            logger.info(f"   Data length: {len(decoded)} bytes")
                            
                            # Check against known discriminators
                            if discriminator_hex in KNOWN_DISCRIMINATORS:
                                trade_type = KNOWN_DISCRIMINATORS[discriminator_hex]
                                logger.info(f"✅ MATCHED KNOWN TRADE TYPE: {trade_type}")
                                
                                # Extract amounts from instruction data (proven structure)
                                if len(decoded) >= 24:  # 8 bytes discriminator + 8 bytes amount + 8 bytes min_out
                                    amount = int.from_bytes(decoded[8:16], 'little')
                                    min_out = int.from_bytes(decoded[16:24], 'little')
                                    
                                    logger.info(f"📊 Trade details:")
                                    logger.info(f"   Type: {trade_type}")
                                    logger.info(f"   Amount: {amount}")
                                    logger.info(f"   Min out: {min_out}")
                                    
                                    # Return enhanced trade data with discriminator info
                                    return {
                                        'trade_type': trade_type,
                                        'discriminator': discriminator_hex,
                                        'amount': amount,
                                        'min_out': min_out,
                                        'program_id': program_id,
                                        'instruction_data': data
                                    }
                        except Exception as e:
                            logger.debug(f"Could not decode instruction data: {e}")
                            continue
            
            # Fall back to balance analysis if discriminator detection fails
            return self._analyze_balance_changes(tx_data, target_wallet, dex_name)
            
        except Exception as e:
            logger.error(f"Error in instruction analysis: {e}")
            return self._analyze_balance_changes(tx_data, target_wallet, dex_name)

    def _analyze_balance_changes(self, tx_data: Dict, target_wallet: str, dex_name: str) -> Optional[Dict]:
        """
        Enhanced balance analysis with improved thresholds and detection
        """
        try:
            meta = tx_data.get('meta', {})
            if not meta or meta.get('err'):
                return None
                
            # Get balance data
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            account_keys = tx_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            # Find target wallet index in accounts
            wallet_index = -1
            try:
                wallet_index = account_keys.index(target_wallet)
            except ValueError:
                logger.debug(f"Target wallet {target_wallet[:8]}... not found in account keys")
                return None
            
            # Calculate SOL balance change
            sol_change = 0.0
            if wallet_index < len(pre_balances) and wallet_index < len(post_balances):
                sol_change = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1_000_000_000
                logger.info(f"💰 SOL balance change for {target_wallet[:8]}...: {sol_change:.9f}")
            else:
                logger.info(f"⚠️ Could not calculate SOL balance change - wallet_index: {wallet_index}, pre_len: {len(pre_balances)}, post_len: {len(post_balances)}")
            
            # Find token balance changes for the target wallet
            token_changes = {}
            
            # Process pre-transaction token balances
            wallet_pre_tokens = {}
            for balance in pre_token_balances:
                if balance.get('owner') == target_wallet:
                    mint = balance.get('mint')
                    amount = int(balance.get('uiTokenAmount', {}).get('amount', 0))
                    wallet_pre_tokens[mint] = amount
            
            # Process post-transaction token balances
            wallet_post_tokens = {}
            for balance in post_token_balances:
                if balance.get('owner') == target_wallet:
                    mint = balance.get('mint')
                    amount = int(balance.get('uiTokenAmount', {}).get('amount', 0))
                    wallet_post_tokens[mint] = amount
            
            # Calculate changes for each token
            all_mints = set(wallet_pre_tokens.keys()) | set(wallet_post_tokens.keys())
            for mint in all_mints:
                pre_amount = wallet_pre_tokens.get(mint, 0)
                post_amount = wallet_post_tokens.get(mint, 0)
                change = post_amount - pre_amount
                if change != 0:
                    token_changes[mint] = change
            
            # Filter out wrapped SOL and find the most significant token change
            wsol_mint = "So11111111111111111111111111111111111111112"
            significant_token_change = None
            max_change_magnitude = 0
            
            for mint, change in token_changes.items():
                if mint != wsol_mint and abs(change) > max_change_magnitude:
                    max_change_magnitude = abs(change)
                    significant_token_change = (mint, change)
            
            # Enhanced trade detection with lower thresholds
            min_sol_change = 0.00001  # Very low threshold to catch micro trades
            min_token_change = 1      # Any token movement
            
            # Determine trade type from balance changes
            trade_type = None
            if significant_token_change:
                token_mint, token_change = significant_token_change
                
                if token_change > 0 and sol_change < -min_sol_change:
                    trade_type = "BUY"
                elif token_change < 0 and sol_change > min_sol_change:
                    trade_type = "SELL"
                
                logger.info(f"📊 Enhanced balance analysis for {target_wallet[:8]}...:")
                logger.info(f"   SOL change: {sol_change:.9f}")
                logger.info(f"   Token {token_mint[:8]}... change: {token_change:,}")
                logger.info(f"   DEX: {dex_name}")
                logger.info(f"   Detected trade type: {trade_type}")
                
                if trade_type:
                    return {
                        'token_mint': token_mint,
                        'sol_change': sol_change,
                        'token_change': token_change,
                        'trade_type': trade_type
                    }
            
            # Log if no trade detected
            if abs(sol_change) > 0 or len(token_changes) > 0:
                logger.info(f"❓ Potential trade but unclear type:")
                logger.info(f"   SOL change: {sol_change:.9f} (min: ±{min_sol_change})")
                logger.info(f"   Token changes: {len(token_changes)}")
                for mint, change in token_changes.items():
                    logger.info(f"     {mint[:8]}...: {change:,}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing balance changes: {e}")
            return None

    async def _execute_router_trade(self, token_mint: str, copy_amount: float, target_trade: Dict) -> TradeExecutionResult:
        """
        Execute router-based trades with fallback mechanisms
        """
        logger.info(f"🔄 Executing router trade for {token_mint[:8]}... with {copy_amount:.3f} SOL")
        
        # First, try the generalized bot normally
        try:
            result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
            if result.result.value == 'success':
                logger.info(f"✅ Router trade successful via generalized bot")
                return result
        except Exception as e:
            logger.warning(f"⚠️ Generalized bot failed: {e}")
        
        # If that fails, try with forced account creation and relaxed validation
        try:
            logger.info(f"🔄 Attempting router trade with bypass validation...")
            result = await self._bypass_validation_buy(token_mint, copy_amount)
            
            if result.result.value == 'success':
                logger.info(f"✅ Router trade successful via bypass validation")
                return result
                
        except Exception as e:
            logger.warning(f"⚠️ Bypass validation failed: {e}")
        
        # If all else fails, log the opportunity and return failure
        logger.info(f"💡 Router-based trade opportunity detected but couldn't execute")
        logger.info(f"📊 Target: {target_trade['sol_amount']:.6f} SOL → {target_trade['token_amount']:,} tokens")
        logger.info(f"🎯 Token: {token_mint}")
        logger.info(f"📋 Original TX: https://solscan.io/tx/{target_trade.get('signature', 'unknown')}")
        logger.info(f"🔍 Error details: Bonding curve account not initialized - likely router-only token")
        logger.info(f"💭 This token might use a different trading mechanism than standard pump.fun")
        
        # Check if this is a real Solscan transaction
        if target_trade.get('signature') != 'test_signature':
            logger.info(f"🏆 PROFITABLE OPPORTUNITY MISSED:")
            logger.info(f"   📈 Target made: {target_trade['sol_amount']:.6f} SOL profit")
            logger.info(f"   🎯 We would have invested: {copy_amount:.6f} SOL")
            logger.info(f"   💡 Consider implementing router-specific trading logic")
        
        return TradeExecutionResult(
            action=TradeAction.BUY,
            result=TradeResult.FAILED,
            signature=None,
            tokens_amount=0,
            sol_amount=copy_amount,
            timestamp=datetime.now(),
            error_message='Router-only token detected - standard pump.fun trading not applicable'
        )

    async def _create_router_token_info(self, token_mint: str, target_trade: Dict):
        """
        Create token info for router-based trades with manual account derivation
        """
        try:
            from solders.pubkey import Pubkey
            from spl.token.instructions import get_associated_token_address
            
            logger.info(f"🔧 Deriving accounts for router token: {token_mint}")
            
            mint_pubkey = Pubkey.from_string(token_mint)
            
            # Try different derivation patterns for router-based tokens
            pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
            
            # Standard bonding curve derivation
            seeds = [b"bonding-curve", bytes(mint_pubkey)]
            bonding_curve, bump = Pubkey.find_program_address(seeds, pump_program)
            
            # Get the associated token account
            bonding_curve_ata = get_associated_token_address(bonding_curve, mint_pubkey)
            
            # Create a simple token info object without strict validation
            class SimpleTokenInfo:
                def __init__(self):
                    self.mint = mint_pubkey
                    self.bonding_curve = bonding_curve
                    self.bonding_curve_ata = bonding_curve_ata
                    self.is_valid = True  # Force valid for router trades
            
            token_info = SimpleTokenInfo()
            
            logger.info(f"🔧 Derived accounts:")
            logger.info(f"   Mint: {mint_pubkey}")
            logger.info(f"   Bonding Curve: {bonding_curve}")
            logger.info(f"   BC ATA: {bonding_curve_ata}")
            
            return token_info
            
        except Exception as e:
            logger.error(f"❌ Failed to derive router accounts: {e}")
            return None

    async def _bypass_validation_buy(self, token_mint: str, sol_amount: float) -> TradeExecutionResult:
        """
        Bypass strict validation for router-based trades
        """
        try:
            from solders.pubkey import Pubkey
            from spl.token.instructions import get_associated_token_address
            
            logger.info(f"🔄 Bypassing validation for router token: {token_mint}")
            
            mint_pubkey = Pubkey.from_string(token_mint)
            pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
            
            # Derive accounts manually
            seeds = [b"bonding-curve", bytes(mint_pubkey)]
            bonding_curve, bump = Pubkey.find_program_address(seeds, pump_program)
            bonding_curve_ata = get_associated_token_address(bonding_curve, mint_pubkey)
            
            logger.info(f"🔧 Using derived accounts:")
            logger.info(f"   Bonding Curve: {bonding_curve}")
            logger.info(f"   BC ATA: {bonding_curve_ata}")
            
            # Execute trade directly with these accounts
            result = await self.trading_bot.execute_buy_trade(
                mint_pubkey,
                bonding_curve, 
                bonding_curve_ata,
                sol_amount
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Bypass validation failed: {e}")
            return TradeExecutionResult(
                action=TradeAction.BUY,
                result=TradeResult.FAILED,
                signature=None,
                tokens_amount=0,
                sol_amount=sol_amount,
                timestamp=datetime.now(),
                error_message=f'Bypass validation failed: {str(e)}'
            )
    
    async def _execute_instant_trade(self, trade_info: Dict):
        """
        INSTANT TRADE EXECUTION - Fire and forget for maximum speed
        Based on the fastest patterns from OLDER scripts
        """
        try:
            action = trade_info['action']
            token_mint = trade_info['token_mint']
            dex = trade_info.get('dex', 'PUMP')
            
            logger.info(f"🚀 FIRE-AND-FORGET: {action.value} {token_mint[:8]}... on {dex}")
            
            # Update stats immediately
            self.stats['trades_detected'] += 1
            
            # INSTANT BUY execution
            if action == TradeAction.BUY and self.copy_config['enable_buys']:
                copy_amount = self.copy_config['fixed_buy_amount']
                
                result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                
                if result.result.value == 'success':
                    self.stats['trades_copied'] += 1
                    self.stats['successful_copies'] += 1
                    self.stats['total_volume_sol'] += copy_amount
                    
                    # Ultra-fast position tracking
                    self.position_tracker[token_mint] = {
                        'our_balance': result.tokens_amount,
                        'target_initial_balance': 0,
                        'buy_timestamp': datetime.now(),
                        'dex': dex
                    }
                    
                    logger.info(f"✅ FIRE-AND-FORGET BUY: {result.tokens_amount:,} tokens | TX: {result.signature}")
                else:
                    self.stats['failed_copies'] += 1
                    logger.error(f"❌ FIRE-AND-FORGET BUY FAILED: {result.error_message}")
            
            # INSTANT SELL execution or OPPORTUNITY BUY
            elif action == TradeAction.SELL and self.copy_config['enable_sells']:
                if token_mint not in self.position_tracker:
                    # OPPORTUNITY BUY
                    copy_amount = self.copy_config['fixed_buy_amount']
                    result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                    
                    if result.result.value == 'success':
                        self.stats['trades_copied'] += 1
                        self.stats['successful_copies'] += 1
                        self.stats['total_volume_sol'] += copy_amount
                        
                        self.position_tracker[token_mint] = {
                            'our_balance': result.tokens_amount,
                            'target_initial_balance': 0,
                            'buy_timestamp': datetime.now(),
                            'dex': dex
                        }
                        
                        logger.info(f"✅ FIRE-AND-FORGET OPPORTUNITY BUY: {result.tokens_amount:,} tokens")
                    else:
                        self.stats['failed_copies'] += 1
                        logger.error(f"❌ OPPORTUNITY BUY FAILED: {result.error_message}")
                else:
                    # INSTANT SELL
                    our_balance = self.position_tracker[token_mint]['our_balance']
                    sell_amount = our_balance // 2  # Quick 50% sell
                    
                    if sell_amount > 0:
                        result = await self.trading_bot.sell_token(token_mint, sell_amount)
                        
                        if result.result.value == 'success':
                            self.stats['trades_copied'] += 1
                            self.stats['successful_copies'] += 1
                            
                            # Quick position update
                            self.position_tracker[token_mint]['our_balance'] -= result.tokens_amount
                            if self.position_tracker[token_mint]['our_balance'] <= 0:
                                del self.position_tracker[token_mint]
                            
                            logger.info(f"✅ FIRE-AND-FORGET SELL: {result.tokens_amount:,} tokens → {result.sol_amount:.6f} SOL")
                        else:
                            self.stats['failed_copies'] += 1
                            logger.error(f"❌ FIRE-AND-FORGET SELL FAILED: {result.error_message}")
                    else:
                        logger.warning(f"⚠️ No tokens to sell for {token_mint[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ Fire-and-forget execution error: {e}")
            self.stats['failed_copies'] += 1

    async def _instant_execute_trade(self, trade_info: Dict) -> Dict:
        """
        INSTANT EXECUTION: Execute trade with minimal validation for maximum speed
        Based on patterns from OLDER/replicator.py
        """
        copy_result = {
            'success': False,
            'signature': None,
            'error': None,
            'amount': 0,
            'timestamp': datetime.now()
        }
        
        try:
            action = trade_info['action']
            token_mint = trade_info['token_mint']
            dex = trade_info.get('dex', 'PUMP')
            
            logger.info(f"⚡ INSTANT executing: {action.value} {token_mint[:8]}... on {dex}")
            
            # INSTANT BUY execution
            if action == TradeAction.BUY and self.copy_config['enable_buys']:
                copy_amount = self.copy_config['fixed_buy_amount']
                
                logger.info(f"🚀 INSTANT BUY: {copy_amount:.3f} SOL of {token_mint[:8]}...")
                
                # Execute with minimal validation for speed
                result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                
                if result.result.value == 'success':
                    copy_result['success'] = True
                    copy_result['signature'] = result.signature
                    copy_result['amount'] = result.tokens_amount
                    
                    # Quick position tracking
                    self.position_tracker[token_mint] = {
                        'our_balance': result.tokens_amount,
                        'target_initial_balance': 0,  # Skip complex tracking for speed
                        'buy_timestamp': datetime.now(),
                        'dex': dex
                    }
                    
                    logger.info(f"✅ INSTANT BUY SUCCESS: {result.tokens_amount:,} tokens")
                    logger.info(f"📊 TX: https://solscan.io/tx/{result.signature}")
                else:
                    copy_result['error'] = result.error_message
                    logger.error(f"❌ INSTANT BUY FAILED: {result.error_message}")
            
            # INSTANT SELL execution
            elif action == TradeAction.SELL and self.copy_config['enable_sells']:
                # Check if we have this token quickly
                if token_mint not in self.position_tracker:
                    # OPPORTUNITY BUY: If target is selling, we should buy!
                    logger.info(f"💡 SELL detected but we don't own it - OPPORTUNITY BUY!")
                    copy_amount = self.copy_config['fixed_buy_amount']
                    
                    result = await self.trading_bot.buy_token(token_mint, sol_amount=copy_amount)
                    
                    if result.result.value == 'success':
                        copy_result['success'] = True
                        copy_result['signature'] = result.signature
                        copy_result['amount'] = result.tokens_amount
                        
                        self.position_tracker[token_mint] = {
                            'our_balance': result.tokens_amount,
                            'target_initial_balance': 0,
                            'buy_timestamp': datetime.now(),
                            'dex': dex
                        }
                        
                        logger.info(f"✅ OPPORTUNITY BUY SUCCESS: {result.tokens_amount:,} tokens")
                    else:
                        copy_result['error'] = result.error_message
                        logger.error(f"❌ OPPORTUNITY BUY FAILED: {result.error_message}")
                else:
                    # INSTANT SELL: Use 50% for speed (avoid complex calculations)
                    our_balance = self.position_tracker[token_mint]['our_balance']
                    sell_amount = our_balance // 2  # Sell half for speed
                    
                    if sell_amount > 0:
                        logger.info(f"🚀 INSTANT SELL: {sell_amount:,} tokens of {token_mint[:8]}...")
                        
                        result = await self.trading_bot.sell_token(token_mint, sell_amount)
                        
                        if result.result.value == 'success':
                            copy_result['success'] = True
                            copy_result['signature'] = result.signature
                            copy_result['amount'] = result.tokens_amount
                            
                            # Quick position update
                            self.position_tracker[token_mint]['our_balance'] -= result.tokens_amount
                            if self.position_tracker[token_mint]['our_balance'] <= 0:
                                del self.position_tracker[token_mint]
                            
                            logger.info(f"✅ INSTANT SELL SUCCESS: {result.tokens_amount:,} tokens → {result.sol_amount:.6f} SOL")
                        else:
                            copy_result['error'] = result.error_message
                            logger.error(f"❌ INSTANT SELL FAILED: {result.error_message}")
                    else:
                        copy_result['error'] = 'No tokens to sell'
                        logger.warning(f"⚠️ No tokens to sell for {token_mint[:8]}...")
            else:
                copy_result['error'] = f'{action.value} disabled in config'
                logger.info(f"⏭️ Skipping {action.value} (disabled)")
            
        except Exception as e:
            logger.error(f"❌ INSTANT execution error: {e}")
            copy_result['error'] = str(e)
        
        return copy_result
    
    def _track_result(self, copy_result: Dict):
        """Quick result tracking for stats"""
        if copy_result['success']:
            self.stats['trades_copied'] += 1
            self.stats['successful_copies'] += 1
            self.stats['total_volume_sol'] += self.copy_config['fixed_buy_amount']
            logger.info(f"🎉 ULTRA-FAST copy completed!")
        else:
            self.stats['failed_copies'] += 1
            logger.warning(f"⚠️ ULTRA-FAST copy failed: {copy_result['error']}")

async def main():
    """Main entry point"""
    
    print("🚀 ADVANCED MULTI-DEX COPY TRADING BOT")
    print("="*60)
    
    # Configuration
    copy_config = {
        'fixed_buy_amount': 0.01,     # Testing with 0.01 SOL per buy
        'delay_seconds': 0,           # No delay - execute immediately
        'enable_sells': True,         # Copy sell trades
        'enable_buys': True,          # Copy buy trades
        'proportional_selling': True  # Sell proportionally to target wallet
    }
    
    bot = PumpCopyTradingBot(copy_config)
    
    try:
        # Print initial status
        print(f"🎯 Target Wallets: {len(MONITORED_WALLETS)}")
        for i, wallet in enumerate(MONITORED_WALLETS):
            print(f"   {i+1}. {wallet}")
        
        print(f"\n⚙️ Copy Configuration:")
        for key, value in copy_config.items():
            print(f"   {key}: {value}")
        
        print(f"\n🔥 Starting copy trading bot...")
        print(f"Press Ctrl+C to stop")
        
        # Start monitoring
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
