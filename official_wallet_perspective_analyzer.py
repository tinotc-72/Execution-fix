"""
🎯 OFFICIAL WALLET-PERSPECTIVE ANALYZER
Using official Solana documentation to ensure EXACT copy trading

Based on official Solana RPC documentation:
- preTokenBalances: Token balances BEFORE transaction
- postTokenBalances: Token balances AFTER transaction  
- We analyze balance changes for the TARGET WALLET specifically

This ensures we copy exactly what the target wallet did, not what DEX programs did.
"""

import asyncio
import traceback
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from solders.signature import Signature as SoldersSignature
from solana.rpc.commitment import Confirmed
from solana.rpc.async_api import AsyncClient

class OfficialWalletPerspectiveAnalyzer:
    """
    OFFICIAL: Analyzes transactions from target wallet's perspective using Solana documentation
    
    According to Solana docs, transaction metadata contains:
    - preTokenBalances: List of token balances BEFORE transaction  
    - postTokenBalances: List of token balances AFTER transaction
    - Each balance has: accountIndex, mint, owner, uiTokenAmount
    
    This is the ONLY way to know what a specific wallet actually did.
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
    
    async def analyze_wallet_action(self, signature: str, target_wallet: str) -> Optional[Dict[str, Any]]:
        """
        🎯 OFFICIAL: Analyze what the target wallet actually did in this transaction
        Returns:
        - action: "buy" | "sell" | "none"
        - token_mint: The actual token that changed
        - amount_change: How much the balance changed
        - confidence: How confident we are in this analysis
        """
        try:
            print(f"🔍 OFFICIAL ANALYSIS: {signature[:8]}... for wallet {target_wallet[:8]}...")
            # STEP 1: Get transaction with official method
            tx_data = await self._fetch_transaction_official(signature)
            if not tx_data:
                print(f"❌ Could not fetch transaction data")
                return None
            # STEP 2: Extract token balance changes using official metadata
            balance_changes = await self._extract_official_balance_changes(tx_data, target_wallet)
            if not balance_changes:
                print(f"❌ No token balance changes found for target wallet")
                return None
            # STEP 3: Determine wallet action from balance changes
            return self._determine_wallet_action_from_balances(balance_changes)
        except Exception as e:
            print(f"❌ Error in official wallet analysis: {e}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    async def _fetch_transaction_official(self, signature: str) -> Optional[Any]:
        """OFFICIAL: Fetch transaction using official Solana getTransaction method"""
        try:
            # Convert string to Signature object (official method)
            sig_obj = SoldersSignature.from_string(signature)
            
            # OFFICIAL: Use jsonParsed encoding as recommended in docs
            print(f"📡 Fetching with official jsonParsed encoding...")
            tx_response = await self.rpc_client.get_transaction(
                sig_obj,
                encoding="jsonParsed",  # OFFICIAL: Best for token data
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            
            if not tx_response or not tx_response.value:
                print(f"⚠️ No transaction data returned")
                return None
            
            tx_data = tx_response.value
            print(f"🔍 Transaction data type: {type(tx_data)}")
            print(f"🔍 Has meta: {hasattr(tx_data, 'meta')}")
            
            # OFFICIAL: Check transaction success
            if hasattr(tx_data, 'meta') and tx_data.meta:
                print(f"🔍 Meta type: {type(tx_data.meta)}")
                print(f"🔍 Meta error: {tx_data.meta.err}")
                print(f"🔍 Has pre_token_balances: {hasattr(tx_data.meta, 'pre_token_balances')}")
                print(f"🔍 Has post_token_balances: {hasattr(tx_data.meta, 'post_token_balances')}")
                
                if tx_data.meta.err:
                    print(f"❌ Transaction failed with error: {tx_data.meta.err}")
                    return None
                print(f"✅ Transaction successful - ready for analysis")
                return tx_data
            else:
                print(f"⚠️ No metadata in transaction")
                # Try with different encoding
                print(f"📡 Retrying with json encoding...")
                tx_response = await self.rpc_client.get_transaction(
                    sig_obj,
                    encoding="json",
                    commitment=Confirmed,
                    max_supported_transaction_version=0
                )
                
                if tx_response and tx_response.value:
                    print(f"✅ Got transaction with json encoding")
                    return tx_response.value
                else:
                    print(f"❌ Failed with both encodings")
                    return None
                
        except Exception as e:
            print(f"❌ Error fetching transaction: {e}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    async def _extract_official_balance_changes(self, tx_data: Any, target_wallet: str) -> Optional[Dict[str, Dict[str, float]]]:
        """
        OFFICIAL: Extract token balance changes using official Solana metadata structure
        Enhanced: Robustly match both owner and associated token accounts for the target wallet.
        """
        try:
            print(f"🔍 Extracting balance changes from transaction data...")
            meta = None
            # Use official Solders .to_json() if available
            if hasattr(tx_data, 'to_json') and callable(tx_data.to_json):
                tx_json = json.loads(tx_data.to_json())
                meta = tx_json.get('meta')
            elif isinstance(tx_data, dict):
                meta = tx_data.get('meta')
            if not meta:
                print(f"❌ No meta found in transaction data (official JSON parse)")
                # Fallback: analyze logs and instruction accounts
                logs = None
                instructions = None
                # Try to extract logs and instructions from tx_data
                if isinstance(tx_data, dict):
                    logs = tx_data.get('logs') or tx_data.get('transaction', {}).get('logs')
                    # Try to get instruction accounts
                    message = tx_data.get('transaction', {}).get('message')
                    if message:
                        instructions = message.get('instructions')
                # If logs are present, look for buy/sell indicators
                action = None
                if logs:
                    logs_str = str(logs).lower()
                    if 'instruction: buy' in logs_str or 'pumpbuy' in logs_str:
                        action = 'buy'
                    elif 'instruction: sell' in logs_str or 'pumpsell' in logs_str:
                        action = 'sell'
                # If instructions are present, check if target_wallet is involved
                wallet_involved = False
                if instructions:
                    for ix in instructions:
                        accounts = ix.get('accounts', [])
                        if any(str(acc) == target_wallet for acc in accounts):
                            wallet_involved = True
                            break
                # If both action and wallet_involved, return synthetic balance change
                if action and wallet_involved:
                    print(f"⚡ Fallback: Detected {action} for wallet {target_wallet[:8]} via logs/instructions")
                    # Synthetic change: unknown mint, amount 0, low confidence
                    return {'unknown_mint': {'pre': 0, 'post': 0, 'change': 0, 'fallback': True, 'action': action}}
                print(f"❌ Fallback failed: Could not detect wallet action from logs/instructions")
                # Log full transaction for debugging
                print(f"🔎 Full transaction data: {json.dumps(tx_data)[:1000]}...")
                return None

            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            changes = {}

            # Helper: match by owner or by associated token accounts
            def is_wallet_related(balance):
                owner = balance.get('owner')
                if owner and str(owner) == target_wallet:
                    return True
                account = balance.get('account')
                if account and str(account) == target_wallet:
                    return True
                return False

            # Build dict of pre balances for quick lookup
            pre_dict = {}
            for bal in pre_balances:
                if is_wallet_related(bal):
                    mint = bal.get('mint')
                    amt = bal.get('uiTokenAmount', {}).get('uiAmount', 0)
                    pre_dict[mint] = amt

            # Compare with post balances
            for bal in post_balances:
                if is_wallet_related(bal):
                    mint = bal.get('mint')
                    post_amt = bal.get('uiTokenAmount', {}).get('uiAmount', 0)
                    pre_amt = pre_dict.get(mint, 0)
                    delta = post_amt - pre_amt
                    if abs(delta) > 0:
                        changes[mint] = {'pre': pre_amt, 'post': post_amt, 'change': delta}

            if changes:
                print(f"✅ Found token balance changes for target wallet: {changes}")
                return changes
            print(f"❌ No token balance changes found for target wallet (official JSON parse)")
            return None
        except Exception as e:
            print(f"❌ Error extracting balance changes: {e}")
            return None
    
    def _determine_wallet_action_from_balances(self, balance_changes: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        🎯 OFFICIAL: Determine wallet action from balance changes
        
        Logic:
        - If token balance INCREASED: Wallet BOUGHT the token
        - If token balance DECREASED: Wallet SOLD the token  
        - If multiple tokens changed: Find the primary trade
        """
        try:
            print(f"🎯 ANALYZING BALANCE CHANGES:")
            
            # Analyze each token's balance change
            actions = []
            for mint, changes in balance_changes.items():
                pre = changes["pre"]
                post = changes["post"]
                change = post - pre
                
                print(f"   {mint[:8]}...: {pre} → {post} (change: {change:+.6f})")
                
                if change > 0:
                    actions.append({
                        "action": "buy",
                        "token_mint": mint,
                        "amount_change": change,
                        "confidence": 10  # High confidence from balance data
                    })
                    print(f"   📈 BUY detected: +{change:.6f}")
                elif change < 0:
                    actions.append({
                        "action": "sell", 
                        "token_mint": mint,
                        "amount_change": abs(change),
                        "confidence": 10  # High confidence from balance data
                    })
                    print(f"   📉 SELL detected: -{abs(change):.6f}")
                else:
                    print(f"   ➡️ No change")
            
            if not actions:
                print(f"⚠️ No significant balance changes detected")
                return {
                    "action": "none",
                    "token_mint": None,
                    "amount_change": 0,
                    "confidence": 0,
                    "reason": "no_balance_changes"
                }
            
            # If multiple actions, find the primary one (largest change)
            primary_action = max(actions, key=lambda x: x["amount_change"])
            
            print(f"🎯 PRIMARY ACTION: {primary_action['action'].upper()} {primary_action['token_mint'][:8]}...")
            
            # Add metadata for debugging
            primary_action.update({
                "analysis_method": "official_balance_analysis",
                "all_actions": actions,
                "total_tokens_changed": len(actions)
            })
            
            return primary_action
            
        except Exception as e:
            print(f"❌ Error determining wallet action: {e}")
            return {
                "action": "error",
                "token_mint": None,
                "amount_change": 0,
                "confidence": 0,
                "error": str(e)
            }

async def test_official_analyzer():
    """Test the official analyzer with a known transaction"""
    try:
        from env_keys import EnvKeys
        
        # Initialize
        env_keys = EnvKeys()
        rpc_client = AsyncClient(env_keys.HELIUS_RPC_URL)
        analyzer = OfficialWalletPerspectiveAnalyzer(rpc_client)
        
        # Test with the problematic transaction
        test_signature = "4M82R9NUYKfDczxb2tCP1RcbxxVTREn6BAXCGvnPi35dAi8GxmyFEDLZdnRxJZAJ7iy8AeR747F7kCArR1jTQbkB"
        test_wallet = "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM"
        
        print(f"🧪 TESTING OFFICIAL ANALYZER")
        print(f"   Transaction: {test_signature[:12]}...")
        print(f"   Target Wallet: {test_wallet[:8]}...")
        
        result = await analyzer.analyze_wallet_action(test_signature, test_wallet)
        
        print(f"\n✅ OFFICIAL ANALYSIS RESULT:")
        if result:
            print(f"   Action: {result.get('action', 'Unknown')}")
            print(f"   Token: {result.get('token_mint', 'Unknown')[:8] if result.get('token_mint') else 'None'}...")
            print(f"   Amount Change: {result.get('amount_change', 0)}")
            print(f"   Confidence: {result.get('confidence', 0)}/10")
            print(f"   Method: {result.get('analysis_method', 'Unknown')}")
        else:
            print(f"   ❌ Analysis failed")
        
        await rpc_client.close()
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_official_analyzer())
