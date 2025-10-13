#!/usr/bin/env python3
"""
PROFIT/LOSS TRACKING - How to determine if a trade was profitable

This shows how to enhance the official buy/sell detection with profit/loss analysis.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TradeRecord:
    """Track individual trades for profit/loss calculation"""
    token_mint: str
    trade_type: str  # "buy" or "sell"
    token_amount: float
    sol_amount: float  # SOL spent (buy) or received (sell)
    timestamp: datetime
    signature: str
    price_per_token: float  # SOL per token

class ProfitLossTracker:
    """Enhanced trade tracking with profit/loss analysis"""
    
    def __init__(self):
        self.trades: Dict[str, List[TradeRecord]] = {}  # token_mint -> [trades]
        self.positions: Dict[str, float] = {}  # token_mint -> current_token_balance
    
    def analyze_transaction_with_profit_loss(self, pre_token_balances: List, post_token_balances: List, 
                                           pre_sol_balance: float, post_sol_balance: float,
                                           signature: str, source_wallet: str) -> Optional[Dict]:
        """
        ENHANCED: Determine buy/sell AND calculate profit/loss
        """
        try:
            print(f"🎯 ENHANCED ANALYSIS: Buy/Sell + Profit/Loss for {signature[:8]}...")
            
            # Step 1: Official method - determine BUY vs SELL
            trade_info = self._official_buy_sell_detection(pre_token_balances, post_token_balances, source_wallet)
            
            if not trade_info:
                return None
            
            # Step 2: Calculate SOL amounts for profit/loss
            sol_change = post_sol_balance - pre_sol_balance
            token_mint = trade_info["token_mint"]
            token_change = trade_info["amount_change"]
            trade_type = trade_info["trade_type"]
            
            # Step 3: Calculate price and profit/loss
            if trade_type == "buy":
                sol_spent = abs(sol_change)  # SOL decreased (spent)
                price_per_token = sol_spent / token_change if token_change > 0 else 0
                
                print(f"💰 BUY ANALYSIS:")
                print(f"   Token gained: +{token_change:.6f}")
                print(f"   SOL spent: -{sol_spent:.6f}")
                print(f"   Price per token: {price_per_token:.9f} SOL")
                
                # Record the buy
                trade_record = TradeRecord(
                    token_mint=token_mint,
                    trade_type="buy",
                    token_amount=token_change,
                    sol_amount=sol_spent,
                    timestamp=datetime.now(),
                    signature=signature,
                    price_per_token=price_per_token
                )
                
                return {
                    **trade_info,
                    "sol_spent": sol_spent,
                    "price_per_token": price_per_token,
                    "profit_loss": 0,  # No profit/loss on buy
                    "trade_record": trade_record
                }
                
            elif trade_type == "sell":
                sol_received = abs(sol_change)  # SOL increased (received)  
                tokens_sold = abs(token_change)
                current_price = sol_received / tokens_sold if tokens_sold > 0 else 0
                
                print(f"💸 SELL ANALYSIS:")
                print(f"   Tokens sold: -{tokens_sold:.6f}")
                print(f"   SOL received: +{sol_received:.6f}")
                print(f"   Current price: {current_price:.9f} SOL")
                
                # Calculate profit/loss vs previous buys
                profit_loss = self._calculate_profit_loss(token_mint, tokens_sold, current_price)
                
                print(f"📊 PROFIT/LOSS: {profit_loss:+.6f} SOL")
                
                trade_record = TradeRecord(
                    token_mint=token_mint,
                    trade_type="sell",
                    token_amount=tokens_sold,
                    sol_amount=sol_received,
                    timestamp=datetime.now(),
                    signature=signature,
                    price_per_token=current_price
                )
                
                return {
                    **trade_info,
                    "sol_received": sol_received,
                    "current_price": current_price,
                    "profit_loss": profit_loss,
                    "trade_record": trade_record
                }
                
        except Exception as e:
            print(f"❌ Error in enhanced analysis: {e}")
            return None
    
    def _official_buy_sell_detection(self, pre_balances: List, post_balances: List, source_wallet: str) -> Optional[Dict]:
        """Official Solana method - just determines BUY vs SELL"""
        balance_changes = {}
        
        # Same logic as your current implementation
        for pre_bal in pre_balances:
            if pre_bal.get("owner") != source_wallet:
                continue
            mint = pre_bal.get("mint")
            if mint:
                pre_amount = float(pre_bal.get("uiTokenAmount", {}).get("uiAmount", 0))
                balance_changes[mint] = {"pre": pre_amount, "post": 0}
        
        for post_bal in post_balances:
            if post_bal.get("owner") != source_wallet:
                continue
            mint = post_bal.get("mint")
            if mint:
                post_amount = float(post_bal.get("uiTokenAmount", {}).get("uiAmount", 0))
                if mint in balance_changes:
                    balance_changes[mint]["post"] = post_amount
                else:
                    balance_changes[mint] = {"pre": 0, "post": post_amount}
        
        # Find significant changes
        for mint, changes in balance_changes.items():
            if mint == "So11111111111111111111111111111111111111112":  # Skip WSOL
                continue
                
            difference = changes["post"] - changes["pre"]
            if abs(difference) > 0.001:
                if difference > 0:
                    return {
                        "trade_type": "buy",
                        "token_mint": mint,
                        "amount_change": difference
                    }
                else:
                    return {
                        "trade_type": "sell", 
                        "token_mint": mint,
                        "amount_change": abs(difference)
                    }
        
        return None
    
    def _calculate_profit_loss(self, token_mint: str, tokens_sold: float, current_price: float) -> float:
        """Calculate profit/loss based on previous buy prices"""
        if token_mint not in self.trades:
            return 0  # No previous buys to compare
        
        # Get all previous buys for this token
        buys = [trade for trade in self.trades[token_mint] if trade.trade_type == "buy"]
        
        if not buys:
            return 0
        
        # Calculate average buy price (FIFO or weighted average)
        total_tokens_bought = sum(buy.token_amount for buy in buys)
        total_sol_spent = sum(buy.sol_amount for buy in buys)
        average_buy_price = total_sol_spent / total_tokens_bought if total_tokens_bought > 0 else 0
        
        # Profit/Loss = (Current Price - Average Buy Price) × Tokens Sold
        profit_loss = (current_price - average_buy_price) * tokens_sold
        
        print(f"   📈 Average buy price: {average_buy_price:.9f} SOL")
        print(f"   📊 Current sell price: {current_price:.9f} SOL")
        print(f"   {'📈' if profit_loss > 0 else '📉'} P&L: {profit_loss:+.6f} SOL")
        
        return profit_loss

def demonstrate_profit_loss_tracking():
    """Show examples of profit/loss calculation"""
    
    print("🎯 PROFIT/LOSS TRACKING EXAMPLES")
    print("=" * 50)
    
    tracker = ProfitLossTracker()
    
    # Example 1: PROFITABLE SELL
    print("\nEXAMPLE 1: PROFITABLE SELL")
    print("-" * 30)
    
    # Simulate BUY: 1 SOL → 1000 tokens (0.001 SOL per token)
    buy_pre_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 0}}]
    buy_post_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 1000}}]
    buy_pre_sol = 2.0
    buy_post_sol = 1.0  # Spent 1 SOL
    
    buy_result = tracker.analyze_transaction_with_profit_loss(
        buy_pre_token, buy_post_token, buy_pre_sol, buy_post_sol, "buy_sig123", "wallet123"
    )
    
    if buy_result:
        tracker.trades.setdefault(buy_result["token_mint"], []).append(buy_result["trade_record"])
    
    # Simulate SELL: 500 tokens → 0.75 SOL (0.0015 SOL per token) - PROFIT!
    sell_pre_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 1000}}]
    sell_post_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 500}}]
    sell_pre_sol = 1.0
    sell_post_sol = 1.75  # Received 0.75 SOL
    
    sell_result = tracker.analyze_transaction_with_profit_loss(
        sell_pre_token, sell_post_token, sell_pre_sol, sell_post_sol, "sell_sig123", "wallet123"
    )
    
    print(f"📊 RESULT: {sell_result['profit_loss']:+.6f} SOL profit!")
    
    # Example 2: LOSING SELL
    print("\nEXAMPLE 2: LOSING SELL")
    print("-" * 30)
    
    # Sell remaining 500 tokens for only 0.2 SOL (0.0004 SOL per token) - LOSS!
    sell2_pre_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 500}}]
    sell2_post_token = [{"owner": "wallet123", "mint": "TOKEN123", "uiTokenAmount": {"uiAmount": 0}}]
    sell2_pre_sol = 1.75
    sell2_post_sol = 1.95  # Received only 0.2 SOL
    
    sell2_result = tracker.analyze_transaction_with_profit_loss(
        sell2_pre_token, sell2_post_token, sell2_pre_sol, sell2_post_sol, "sell2_sig123", "wallet123"
    )
    
    print(f"📊 RESULT: {sell2_result['profit_loss']:+.6f} SOL loss!")

if __name__ == "__main__":
    demonstrate_profit_loss_tracking()
    
    print(f"\n🎉 SUMMARY")
    print("=" * 30)
    print("✅ Official method: Determines BUY vs SELL reliably")
    print("✅ Enhanced method: Adds profit/loss calculation")
    print("📊 Tracks: SOL spent, SOL received, price per token")
    print("💰 Calculates: Profit/loss vs average buy price")
