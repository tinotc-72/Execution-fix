"""
🎯 COMPREHENSIVE COPY TRADING VERIFICATION
Ensures your wallet does EXACTLY what your chosen wallets do using official Solana documentation

This test verifies:
1. Official wallet perspective analysis using Solana RPC documentation
2. Accurate buy/sell detection from target wallet's balance changes
3. Proper copy trading execution that mirrors target wallet actions
"""

import asyncio
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from env_keys import EnvKeys
from solana.rpc.async_api import AsyncClient
from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer

class CopyTradingVerificationSuite:
    """Comprehensive verification that your bot copies target wallets exactly"""
    
    def __init__(self):
        self.env_keys = EnvKeys()
        self.rpc_client = AsyncClient(self.env_keys.HELIUS_RPC_URL)
        self.analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
        
        # Test target wallets (replace with your actual target wallets)
        self.target_wallets = [
            "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM",  # Your primary target
            # Add more target wallets here
        ]
        
        # Your wallet for comparison
        self.your_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    
    async def verify_exact_copy_trading(self, signature: str):
        """
        🎯 MAIN VERIFICATION: Ensure bot copies target wallet actions exactly
        
        Steps:
        1. Analyze what each target wallet did in this transaction
        2. Verify what your wallet did in response
        3. Confirm actions match exactly
        """
        try:
            print(f"🎯 COPY TRADING VERIFICATION")
            print(f"   Transaction: {signature[:12]}...")
            print(f"   Your Wallet: {self.your_wallet[:8]}...")
            print(f"   Target Wallets: {len(self.target_wallets)}")
            
            # Step 1: Analyze target wallet actions
            target_actions = {}
            for wallet in self.target_wallets:
                print(f"\n🔍 Analyzing target wallet: {wallet[:8]}...")
                action = await self.analyzer.analyze_wallet_action(signature, wallet)
                if action and action.get('action') not in ['none', 'error']:
                    target_actions[wallet] = action
                    print(f"   ✅ Target Action: {action['action'].upper()}")
                    print(f"   📦 Token: {action.get('token_mint', 'Unknown')[:8]}...")
                    print(f"   📊 Amount: {action.get('amount_change', 0)}")
                else:
                    print(f"   ➡️ No action (wallet not involved)")
            
            # Step 2: Analyze your wallet's action
            print(f"\n🔍 Analyzing YOUR wallet: {self.your_wallet[:8]}...")
            your_action = await self.analyzer.analyze_wallet_action(signature, self.your_wallet)
            if your_action and your_action.get('action') not in ['none', 'error']:
                print(f"   ✅ Your Action: {your_action['action'].upper()}")
                print(f"   📦 Token: {your_action.get('token_mint', 'Unknown')[:8]}...")
                print(f"   📊 Amount: {your_action.get('amount_change', 0)}")
            else:
                print(f"   ➡️ No action (you didn't trade)")
            
            # Step 3: Verify copy trading accuracy
            verification_results = self._verify_copy_accuracy(target_actions, your_action)
            
            # Step 4: Display verification results
            print(f"\n🎯 COPY TRADING VERIFICATION RESULTS:")
            print(f"   Target Wallets with Actions: {len(target_actions)}")
            print(f"   Your Wallet Action: {your_action.get('action', 'none') if your_action else 'none'}")
            print(f"   Copy Accuracy: {verification_results['accuracy']}")
            print(f"   Status: {verification_results['status']}")
            
            if verification_results['issues']:
                print(f"   ⚠️ Issues Found:")
                for issue in verification_results['issues']:
                    print(f"      - {issue}")
            
            return verification_results
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    def _verify_copy_accuracy(self, target_actions: Dict, your_action: Optional[Dict]) -> Dict[str, Any]:
        """Verify that your wallet's action matches target wallet actions exactly"""
        try:
            issues = []
            
            # Case 1: No target wallets acted
            if not target_actions:
                if your_action and your_action.get('action') not in ['none', 'error']:
                    issues.append("You traded when target wallets didn't - should not have traded")
                    return {
                        'accuracy': 'FAILED',
                        'status': 'INCORRECT_ACTION',
                        'issues': issues,
                        'expected': 'No action',
                        'actual': f"{your_action['action']} {your_action.get('token_mint', '')[:8]}..."
                    }
                else:
                    return {
                        'accuracy': 'PERFECT',
                        'status': 'CORRECT_NO_ACTION',
                        'issues': [],
                        'expected': 'No action',
                        'actual': 'No action'
                    }
            
            # Case 2: Target wallets acted, verify your response
            if len(target_actions) == 1:
                # Single target wallet action
                target_wallet, target_action = list(target_actions.items())[0]
                expected_action = target_action['action']
                expected_token = target_action['token_mint']
                
                if not your_action or your_action.get('action') in ['none', 'error']:
                    issues.append(f"Target wallet {target_wallet[:8]}... {expected_action.upper()}ed {expected_token[:8]}... but you didn't copy")
                    return {
                        'accuracy': 'FAILED',
                        'status': 'MISSED_COPY',
                        'issues': issues,
                        'expected': f"{expected_action} {expected_token[:8]}...",
                        'actual': 'No action'
                    }
                
                # Verify action matches
                if your_action['action'] != expected_action:
                    issues.append(f"Action mismatch: expected {expected_action}, got {your_action['action']}")
                
                # Verify token matches
                if your_action.get('token_mint') != expected_token:
                    issues.append(f"Token mismatch: expected {expected_token[:8]}..., got {your_action.get('token_mint', 'None')[:8]}...")
                
                if issues:
                    return {
                        'accuracy': 'FAILED',
                        'status': 'INCORRECT_COPY',
                        'issues': issues,
                        'expected': f"{expected_action} {expected_token[:8]}...",
                        'actual': f"{your_action['action']} {your_action.get('token_mint', 'None')[:8]}..."
                    }
                else:
                    return {
                        'accuracy': 'PERFECT',
                        'status': 'CORRECT_COPY',
                        'issues': [],
                        'expected': f"{expected_action} {expected_token[:8]}...",
                        'actual': f"{your_action['action']} {your_action.get('token_mint', '')[:8]}..."
                    }
            
            # Case 3: Multiple target wallets acted
            else:
                # For multiple target actions, you should copy the primary/largest one
                # This is more complex and depends on your copy trading strategy
                issues.append(f"Multiple target wallets acted - verification needs strategy-specific logic")
                return {
                    'accuracy': 'COMPLEX',
                    'status': 'MULTIPLE_TARGETS',
                    'issues': issues,
                    'expected': 'Strategy-dependent',
                    'actual': f"{your_action['action'] if your_action else 'none'}"
                }
                
        except Exception as e:
            return {
                'accuracy': 'ERROR',
                'status': 'VERIFICATION_ERROR',
                'issues': [f"Verification error: {e}"],
                'expected': 'Unknown',
                'actual': 'Unknown'
            }
    
    async def test_recent_transactions(self, wallet: str, limit: int = 10):
        """Test copy trading accuracy on recent transactions from a target wallet"""
        try:
            print(f"🧪 TESTING RECENT TRANSACTIONS from {wallet[:8]}...")
            
            from solana.rpc.api import Client
            from solders.pubkey import Pubkey
            
            # Get recent transactions
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet),
                limit=limit
            )
            
            if not response.value:
                print(f"❌ No transactions found for {wallet[:8]}...")
                return
            
            print(f"📊 Found {len(response.value)} recent transactions")
            
            results = []
            for i, tx_info in enumerate(response.value):
                signature = str(tx_info.signature)
                print(f"\n📋 [{i+1}/{limit}] Testing: {signature[:12]}...")
                
                result = await self.verify_exact_copy_trading(signature)
                if result:
                    results.append({
                        'signature': signature,
                        'result': result
                    })
                
                # Don't overwhelm the RPC
                await asyncio.sleep(1)
            
            # Summary
            print(f"\n📊 COPY TRADING ACCURACY SUMMARY:")
            perfect_count = sum(1 for r in results if r['result']['accuracy'] == 'PERFECT')
            failed_count = sum(1 for r in results if r['result']['accuracy'] == 'FAILED')
            
            print(f"   Total Tested: {len(results)}")
            print(f"   Perfect Copies: {perfect_count}")
            print(f"   Failed Copies: {failed_count}")
            print(f"   Accuracy Rate: {(perfect_count / len(results) * 100) if results else 0:.1f}%")
            
            return results
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            return None
    
    async def close(self):
        """Clean up resources"""
        await self.rpc_client.close()

async def main():
    """Run copy trading verification"""
    verifier = CopyTradingVerificationSuite()
    
    try:
        # Test specific transaction
        test_signature = "4M82R9NUYKfDczxb2tCP1RcbxxVTREn6BAXCGvnPi35dAi8GxmyFEDLZdnRxJZAJ7iy8AeR747F7kCArR1jTQbkB"
        print(f"🧪 TESTING SPECIFIC TRANSACTION: {test_signature[:12]}...")
        
        result = await verifier.verify_exact_copy_trading(test_signature)
        
        # Test recent transactions from target wallet
        # print(f"\n🧪 TESTING RECENT TRANSACTIONS...")
        # await verifier.test_recent_transactions(verifier.target_wallets[0], limit=5)
        
    finally:
        await verifier.close()

if __name__ == "__main__":
    asyncio.run(main())
