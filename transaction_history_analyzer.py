#!/usr/bin/env python3
"""
Comprehensive Transaction History Analyzer for Target Wallets
Retrieves and analyzes all buy/sell transactions from both target wallets
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed, Processed
from solana.rpc.types import MemcmpOpts
import json
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionHistoryAnalyzer:
    """Comprehensive transaction history analyzer for target wallets"""
    
    def __init__(self, rpc_url: str, target_wallets: List[str]):
        self.rpc_client = AsyncClient(rpc_url, commitment=Confirmed)
        self.target_wallets = target_wallets
        self.analyzed_transactions = set()
        
        # DEX program IDs for filtering
        self.dex_programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv": "Raydium CPMM",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
            
            # Orca
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Whirlpool",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V1",
            "SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8": "Orca V2",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
            
            # Meteora
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
            
            # Other DEXes
            "srmqPiDkJXm6g7sjPhLKbf7zW9bP7iYKn3rJJsL6L5Q": "Serum V3",
            "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum V2",
        }
    
    async def get_all_transactions(self, wallet_address: str, limit: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """Retrieve all transactions for a wallet within the specified timeframe"""
        try:
            logger.info(f"🔍 Retrieving transaction history for wallet: {wallet_address}")
            logger.info(f"   📊 Limit: {limit} transactions, Days back: {days_back}")
            
            wallet_pubkey = Pubkey.from_string(wallet_address)
            all_transactions = []
            
            # Get signatures with pagination
            before_signature = None
            remaining_limit = limit
            
            while remaining_limit > 0:
                # Determine batch size (max 1000 per request)
                batch_size = min(1000, remaining_limit)
                
                logger.info(f"📥 Fetching batch of {batch_size} signatures...")
                
                # Get signatures for this batch
                if before_signature:
                    response = await self.rpc_client.get_signatures_for_address(
                        wallet_pubkey,
                        limit=batch_size,
                        before=before_signature
                    )
                else:
                    response = await self.rpc_client.get_signatures_for_address(
                        wallet_pubkey,
                        limit=batch_size
                    )
                
                if not response.value or len(response.value) == 0:
                    logger.info("📭 No more transactions found")
                    break
                
                logger.info(f"✅ Retrieved {len(response.value)} signatures")
                
                # Filter by time if specified
                cutoff_time = datetime.now() - timedelta(days=days_back)
                batch_transactions = []
                
                for tx_info in response.value:
                    # Check if transaction is within time window
                    if hasattr(tx_info, 'block_time') and tx_info.block_time:
                        tx_time = datetime.fromtimestamp(tx_info.block_time)
                        if tx_time < cutoff_time:
                            logger.info(f"⏰ Reached transactions older than {days_back} days, stopping")
                            remaining_limit = 0  # Stop fetching
                            break
                    
                    batch_transactions.append({
                        'signature': str(tx_info.signature),
                        'block_time': tx_info.block_time,
                        'confirmation_status': getattr(tx_info, 'confirmation_status', None),
                        'err': tx_info.err,
                        'memo': getattr(tx_info, 'memo', None),
                        'slot': tx_info.slot
                    })
                
                all_transactions.extend(batch_transactions)
                remaining_limit -= len(batch_transactions)
                
                # Set up for next batch
                if len(response.value) < batch_size:
                    break  # No more transactions available
                    
                before_signature = response.value[-1].signature
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            logger.info(f"📊 Total transactions retrieved: {len(all_transactions)}")
            return all_transactions
            
        except Exception as e:
            logger.error(f"❌ Error retrieving transactions for {wallet_address}: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return []
    
    async def analyze_transaction_for_trading(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Analyze a single transaction to determine if it's a buy/sell trade"""
        try:
            logger.debug(f"🔍 Analyzing transaction: {signature}")
            
            # Get transaction details
            sig_obj = Signature.from_string(signature)
            
            # Wait for transaction to be confirmed
            await asyncio.sleep(0.5)
            
            tx_response = await self.rpc_client.get_transaction(
                sig_obj,
                encoding="jsonParsed",
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            
            if not tx_response.value:
                logger.debug(f"⚠️ Could not retrieve transaction: {signature}")
                return None
                
            transaction = tx_response.value
            
            # Extract trade information
            trade_info = await self.extract_trade_info_from_transaction(transaction, wallet_address, signature)
            
            if trade_info:
                logger.info(f"✅ Trade detected: {trade_info['type']} {trade_info['token_mint'][:8]}... on {trade_info.get('dex', 'Unknown')}")
                logger.info(f"   💰 Amount: {trade_info['amount']:.6f} SOL")
                logger.info(f"   🕐 Time: {trade_info.get('timestamp', 'Unknown')}")
            
            return trade_info
            
        except Exception as e:
            logger.debug(f"⚠️ Error analyzing transaction {signature}: {e}")
            return None
    
    async def extract_trade_info_from_transaction(self, transaction: Any, wallet_address: str, signature: str) -> Optional[Dict[str, Any]]:
        """Extract trade information from a transaction (simplified version of main.py logic)"""
        try:
            # Get transaction metadata
            meta = None
            if hasattr(transaction, 'meta'):
                meta = transaction.meta
            elif hasattr(transaction, 'transaction') and hasattr(transaction.transaction, 'meta'):
                meta = transaction.transaction.meta
            
            if not meta:
                return None
            
            # Get instructions
            instructions = []
            if hasattr(transaction, 'transaction'):
                tx_data = transaction.transaction
                if hasattr(tx_data, 'message') and hasattr(tx_data.message, 'instructions'):
                    instructions = tx_data.message.instructions
            
            # Detect DEX from program IDs in instructions
            dex_detected = None
            programs_found = set()
            
            for instruction in instructions:
                if hasattr(instruction, 'program_id'):
                    program_id = str(instruction.program_id)
                    programs_found.add(program_id)
                    
                    if program_id in self.dex_programs:
                        dex_detected = self.dex_programs[program_id]
                        break
            
            if not dex_detected:
                logger.debug(f"No DEX programs detected. Programs found: {list(programs_found)[:5]}")
                return None
            
            # Calculate SOL balance change
            sol_balance_change = 0.0
            target_wallet_pubkey = Pubkey.from_string(wallet_address)
            
            if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                account_keys = []
                if hasattr(transaction, 'transaction') and hasattr(transaction.transaction, 'message'):
                    account_keys = getattr(transaction.transaction.message, 'account_keys', [])
                
                # Find target wallet in account keys
                target_index = -1
                for i, account_key in enumerate(account_keys):
                    if str(account_key) == wallet_address:
                        target_index = i
                        break
                
                if target_index >= 0 and target_index < len(meta.pre_balances) and target_index < len(meta.post_balances):
                    pre_balance = meta.pre_balances[target_index] / 1e9
                    post_balance = meta.post_balances[target_index] / 1e9
                    sol_balance_change = post_balance - pre_balance
            
            # Analyze token transfers
            token_transfers = []
            token_mint = None
            
            if hasattr(meta, 'post_token_balances') and hasattr(meta, 'pre_token_balances'):
                pre_token_balances = {
                    (tb.account_index, tb.mint): tb.ui_token_amount.ui_amount or 0
                    for tb in (meta.pre_token_balances or [])
                }
                
                post_token_balances = {
                    (tb.account_index, tb.mint): tb.ui_token_amount.ui_amount or 0
                    for tb in (meta.post_token_balances or [])
                }
                
                # Find token balance changes
                all_keys = set(pre_token_balances.keys()) | set(post_token_balances.keys())
                
                for (account_index, mint) in all_keys:
                    pre_amount = pre_token_balances.get((account_index, mint), 0)
                    post_amount = post_token_balances.get((account_index, mint), 0)
                    change = post_amount - pre_amount
                    
                    if abs(change) > 0.001:  # Significant change
                        token_transfers.append({
                            'mint': mint,
                            'change': change,
                            'account_index': account_index
                        })
                        
                        # Set token mint if not already set
                        if not token_mint and mint != "So11111111111111111111111111111112":  # Not SOL
                            token_mint = mint
            
            # Determine trade type
            trade_type = None
            if sol_balance_change < -0.001:  # SOL decreased (likely a buy)
                trade_type = 'buy'
            elif sol_balance_change > 0.001:  # SOL increased (likely a sell)
                trade_type = 'sell'
            
            # If we have a trade type and token, return the trade info
            if trade_type and token_mint:
                return {
                    'type': trade_type,
                    'token_mint': token_mint,
                    'amount': abs(sol_balance_change),
                    'timestamp': datetime.fromtimestamp(transaction.block_time) if hasattr(transaction, 'block_time') and transaction.block_time else datetime.now(),
                    'dex': dex_detected,
                    'signature': signature,
                    'sol_balance_change': sol_balance_change,
                    'token_transfers': len(token_transfers),
                    'programs_detected': list(programs_found)
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting trade info: {e}")
            return None
    
    async def get_all_trades_for_wallet(self, wallet_address: str, limit: int = 100, days_back: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """Get all buy and sell trades for a specific wallet"""
        logger.info(f"")
        logger.info(f"🎯 ANALYZING WALLET: {wallet_address}")
        logger.info(f"📊 Parameters: {limit} transactions, {days_back} days back")
        logger.info(f"")
        
        # Get all transactions
        all_transactions = await self.get_all_transactions(wallet_address, limit, days_back)
        
        if not all_transactions:
            logger.warning(f"⚠️ No transactions found for wallet: {wallet_address}")
            return {'buys': [], 'sells': [], 'other': []}
        
        # Analyze each transaction for trading activity
        buys = []
        sells = []
        other_trades = []
        
        logger.info(f"🔍 Analyzing {len(all_transactions)} transactions for trading activity...")
        
        # Process transactions in batches to avoid overwhelming the RPC
        batch_size = 10
        total_analyzed = 0
        
        for i in range(0, len(all_transactions), batch_size):
            batch = all_transactions[i:i + batch_size]
            logger.info(f"📊 Processing batch {i//batch_size + 1}/{(len(all_transactions) + batch_size - 1)//batch_size} ({len(batch)} transactions)")
            
            # Analyze transactions in parallel within batch
            tasks = [
                self.analyze_transaction_for_trading(tx['signature'], wallet_address)
                for tx in batch if not tx.get('err')  # Skip failed transactions
            ]
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict):  # Valid trade info
                        if result['type'] == 'buy':
                            buys.append(result)
                        elif result['type'] == 'sell':
                            sells.append(result)
                        else:
                            other_trades.append(result)
                        total_analyzed += 1
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        logger.info(f"")
        logger.info(f"📈 ANALYSIS COMPLETE FOR {wallet_address}")
        logger.info(f"   🟢 Buys found: {len(buys)}")
        logger.info(f"   🔴 Sells found: {len(sells)}")
        logger.info(f"   ⚪ Other trades: {len(other_trades)}")
        logger.info(f"   📊 Total analyzed: {total_analyzed}/{len(all_transactions)}")
        logger.info(f"")
        
        return {
            'buys': buys,
            'sells': sells,
            'other': other_trades,
            'wallet': wallet_address,
            'total_transactions': len(all_transactions),
            'analyzed_transactions': total_analyzed
        }
    
    async def get_all_trades_for_all_wallets(self, limit: int = 100, days_back: int = 7) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Get all trades for all target wallets"""
        logger.info(f"🚀 COMPREHENSIVE TRADE ANALYSIS")
        logger.info(f"🎯 Target wallets: {len(self.target_wallets)}")
        logger.info(f"📊 Parameters: {limit} transactions per wallet, {days_back} days back")
        logger.info(f"")
        
        all_wallet_trades = {}
        
        for wallet_address in self.target_wallets:
            try:
                wallet_trades = await self.get_all_trades_for_wallet(wallet_address, limit, days_back)
                all_wallet_trades[wallet_address] = wallet_trades
                
                # Summary for this wallet
                logger.info(f"✅ Wallet {wallet_address[:8]}... completed")
                logger.info(f"   📈 Total trades: {len(wallet_trades['buys']) + len(wallet_trades['sells'])}")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing wallet {wallet_address}: {e}")
                all_wallet_trades[wallet_address] = {'buys': [], 'sells': [], 'other': [], 'error': str(e)}
        
        # Overall summary
        total_buys = sum(len(trades['buys']) for trades in all_wallet_trades.values() if 'buys' in trades)
        total_sells = sum(len(trades['sells']) for trades in all_wallet_trades.values() if 'sells' in trades)
        
        logger.info(f"")
        logger.info(f"🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
        logger.info(f"   📊 Total wallets analyzed: {len(self.target_wallets)}")
        logger.info(f"   🟢 Total buys across all wallets: {total_buys}")
        logger.info(f"   🔴 Total sells across all wallets: {total_sells}")
        logger.info(f"   💹 Grand total trades: {total_buys + total_sells}")
        logger.info(f"")
        
        return all_wallet_trades
    
    async def save_analysis_to_file(self, analysis_results: Dict[str, Any], filename: str = None):
        """Save analysis results to a JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trade_analysis_{timestamp}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                else:
                    return obj
            
            serializable_results = convert_datetime(analysis_results)
            
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"💾 Analysis results saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis to file: {e}")
            return None
    
    async def close(self):
        """Close the RPC client"""
        await self.rpc_client.close()

async def main():
    """Example usage of the transaction history analyzer"""
    from env_keys import EnvKeys
    
    # Initialize environment keys
    env_keys = EnvKeys()
    
    # Target wallets (replace with your actual target wallets)
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Wallet 2
    ]
    
    # Initialize analyzer
    analyzer = TransactionHistoryAnalyzer(env_keys.HELIUS_RPC_URL, target_wallets)
    
    try:
        # Get all trades for all wallets (last 50 transactions, 3 days back)
        all_trades = await analyzer.get_all_trades_for_all_wallets(limit=50, days_back=3)
        
        # Save results to file
        filename = await analyzer.save_analysis_to_file(all_trades)
        
        # Print summary for each wallet
        for wallet, trades in all_trades.items():
            if 'error' in trades:
                print(f"\n❌ Wallet {wallet[:8]}... had an error: {trades['error']}")
                continue
                
            print(f"\n🎯 WALLET: {wallet}")
            print(f"📊 Total transactions analyzed: {trades.get('analyzed_transactions', 0)}")
            
            if trades['buys']:
                print(f"\n🟢 BUY TRANSACTIONS ({len(trades['buys'])}):")
                for buy in trades['buys'][-5:]:  # Show last 5 buys
                    print(f"  💰 {buy['amount']:.4f} SOL → {buy['token_mint'][:8]}... on {buy.get('dex', 'Unknown')}")
                    print(f"      🕐 {buy['timestamp']}")
                    print(f"      🔗 {buy['signature'][:16]}...")
            
            if trades['sells']:
                print(f"\n🔴 SELL TRANSACTIONS ({len(trades['sells'])}):")
                for sell in trades['sells'][-5:]:  # Show last 5 sells
                    print(f"  💸 {sell['token_mint'][:8]}... → {sell['amount']:.4f} SOL on {sell.get('dex', 'Unknown')}")
                    print(f"      🕐 {sell['timestamp']}")
                    print(f"      🔗 {sell['signature'][:16]}...")
        
        print(f"\n💾 Full analysis saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Error in main analysis: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    finally:
        await analyzer.close()

if __name__ == "__main__":
    asyncio.run(main())
