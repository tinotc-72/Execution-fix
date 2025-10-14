#!/usr/bin/env python3
"""
Demo script showing the new routing logic in action.

Demonstrates:
1. Meteora path with retry_hint support
2. Unknown DEX with mint routing
3. Source failed transaction handling
4. Force requote for slippage retry
"""

def demo_meteora_routing():
    """Demo 1: Meteora path routing with requote support"""
    print("=" * 80)
    print("DEMO 1: Meteora Path Routing")
    print("=" * 80)
    print()
    
    print("Scenario: Trade detected as Meteora DEX")
    print("-" * 80)
    
    # Example trade_info
    trade_info = {
        "dex": "meteora",
        "dex_type": "meteora_damm_v2",
        "token_mint": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "action": "buy",
        "signature": "abc123..."
    }
    
    print("\n1. Normal Meteora trade:")
    print(f"   Input: {trade_info}")
    print(f"   Route: ['meteora', 'jupiter', 'direct_copy']")
    print(f"   - Try Meteora executor first")
    print(f"   - If Meteora fails → Try Jupiter executor")
    print(f"   - If Jupiter fails → Try direct_copy")
    print()
    
    # With retry_hint
    trade_info["retry_hint"] = "requote"
    trade_info["source_tx_failed"] = True
    
    print("2. Meteora trade with slippage retry:")
    print(f"   Input: {trade_info}")
    print(f"   Route: ['meteora', 'jupiter', 'direct_copy']")
    print(f"   - ⚡ retry_hint='requote' detected!")
    print(f"   - Meteora executor called with force_requote=True")
    print(f"   - Uses min_tokens=0 for maximum slippage tolerance")
    print(f"   - If still fails → Try Jupiter executor")
    print(f"   - If Jupiter fails → Try direct_copy")
    print()


def demo_unknown_with_mint():
    """Demo 2: Unknown DEX with mint routing"""
    print("=" * 80)
    print("DEMO 2: Unknown DEX with Token Mint")
    print("=" * 80)
    print()
    
    print("Scenario: Unknown DEX but valid token mint present")
    print("-" * 80)
    
    trade_info = {
        "dex": "unknown",
        "dex_type": "unknown",
        "token_mint": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "action": "buy",
        "signature": "def456..."
    }
    
    print(f"\n   Input: {trade_info}")
    print(f"   Route: ['jupiter', 'meteora', 'direct_copy']")
    print(f"   - 🧭 Route=unknown; mint present → Jupiter → Meteora → Clone")
    print(f"   - Try Jupiter executor first (most likely to work)")
    print(f"   - If Jupiter fails → Try Meteora executor")
    print(f"   - If Meteora fails → Try direct_copy as last resort")
    print()
    
    print("   Rationale:")
    print("   - We have a valid mint, so we can build transactions")
    print("   - Try builders before cloning unknown transaction")
    print("   - Jupiter has widest DEX coverage, try it first")
    print()


def demo_source_failed():
    """Demo 3: Source failed transaction handling"""
    print("=" * 80)
    print("DEMO 3: Source Failed Transaction Handling")
    print("=" * 80)
    print()
    
    print("Scenario: Source transaction failed (e.g., error 6004)")
    print("-" * 80)
    
    trade_info = {
        "dex": "unknown",
        "dex_type": "unknown",
        "token_mint": None,  # No mint extracted
        "action": "buy",
        "signature": "ghi789...",
        "source_tx_failed": True,
        "retry_hint": "requote",
        "meta": {"err": {"InstructionError": [0, {"Custom": 6004}]}}
    }
    
    print(f"\n   Input: {trade_info}")
    print(f"   Route: ['jupiter', 'meteora', 'direct_copy']")
    print(f"   - 🧭 Source failed → avoid clone; try builders first")
    print(f"   - ⚠️ Source transaction failed with error 6004 (slippage)")
    print(f"   - Never clone a failed transaction first (would fail again)")
    print(f"   - Try Jupiter executor first")
    print(f"   - If Jupiter fails → Try Meteora executor")
    print(f"   - Only as last resort → Try direct_copy")
    print()
    
    print("   Rationale:")
    print("   - Source tx failed (e.g., exceeded slippage tolerance)")
    print("   - Cloning the same tx will likely fail with same error")
    print("   - Builders can use fresh quotes and wider slippage")
    print("   - Direct copy is last resort, not first attempt")
    print()


def demo_force_requote_implementation():
    """Demo 4: Force requote implementation details"""
    print("=" * 80)
    print("DEMO 4: Force Requote Implementation")
    print("=" * 80)
    print()
    
    print("Implementation Flow:")
    print("-" * 80)
    
    print("\n1. Execution Coordinator (_execute_copy_buy):")
    print("   ```python")
    print("   retry_hint = trade_info.get('retry_hint', '').strip()")
    print("   if dex_key == 'meteora':")
    print("       if retry_hint == 'requote':")
    print("           # Log the retry hint")
    print("           self.logger.info('⚡ retry_hint=requote - will force fresh quote/wider slippage')")
    print("   ```")
    print()
    
    print("2. Meteora Executor Call:")
    print("   ```python")
    print("   force_requote = retry_hint == 'requote'")
    print("   result = await self._execute_meteora_buy(")
    print("       token_mint, source_wallet,")
    print("       amount_sol=amount_sol,")
    print("       trade_info=trade_info,")
    print("       force_requote=force_requote,  # Pass the flag")
    print("       **kwargs")
    print("   )")
    print("   ```")
    print()
    
    print("3. Meteora Buy Method (_execute_meteora_buy):")
    print("   ```python")
    print("   force_requote = kwargs.get('force_requote', False)")
    print("   if force_requote:")
    print("       logger.info('⚡ force_requote=True - will request fresh quote with wider slippage')")
    print("   result = await mev_meteora_copy_trade(")
    print("       ...,")
    print("       force_requote=force_requote  # Pass to executor")
    print("   )")
    print("   ```")
    print()
    
    print("4. MEV Meteora Copy Trade (mev_meteora_executor.py):")
    print("   ```python")
    print("   async def mev_meteora_copy_trade(")
    print("       ...,")
    print("       force_requote: bool = False  # Accept the flag")
    print("   ):")
    print("       # Adjust min_tokens for wider slippage")
    print("       min_tokens = 1 if not force_requote else 0  # 0 = max slippage")
    print("       if force_requote:")
    print("           logger.info('⚡ force_requote=True - using min_tokens=0 for maximum slippage')")
    print("       tx = _build_meteora_buy_solders(rpc, owner, mint_pk, lamports, min_tokens=min_tokens, ...)")
    print("   ```")
    print()
    
    print("Result:")
    print("   - Normal trade: min_tokens=1 (tight slippage)")
    print("   - Retry with requote: min_tokens=0 (maximum slippage tolerance)")
    print("   - Allows trade to succeed even with high volatility")
    print()


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("ROUTING LOGIC ENHANCEMENT - DEMO")
    print("=" * 80)
    print()
    
    demo_meteora_routing()
    demo_unknown_with_mint()
    demo_source_failed()
    demo_force_requote_implementation()
    
    print("=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print()
    print("1. ✅ Meteora path: Meteora → Jupiter → direct_copy")
    print("2. ✅ Unknown + mint: Jupiter → Meteora → direct_copy")
    print("3. ✅ Source failed: Builders first, avoid cloning doomed tx")
    print("4. ✅ Force requote: Wider slippage (min_tokens=0) for retry")
    print("5. ✅ No new dependencies - uses existing infrastructure")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
