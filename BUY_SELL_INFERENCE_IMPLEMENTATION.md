# Buy/Sell Side Inference Implementation

## Overview

This document describes the implementation of buy/sell side inference for trades based on token balance changes, specifically comparing preTokenBalances vs postTokenBalances to determine trade direction.

## Problem Statement

The copy trading bot needed enhanced logic to:
1. Compare preTokenBalances vs postTokenBalances
2. Infer buy/sell direction based on WSOL balance changes
3. Save mint_in and mint_out for correct executor routing
4. Log detected actions with specific format

## Implementation

### Location
- **File**: `trade_processor.py`
- **Method**: `detect_buy_sell(meta, monitored_wallets)`

### Key Changes

#### 1. WSOL Balance Tracking
**Previous Behavior**: WSOL balance changes were skipped
```python
# Old code - WSOL was skipped
if mint == "So11111111111111111111111111111111111111112":
    logger.debug(f"⏭️ [DELTA_DETECTION] Skipping SOL balance change...")
    continue
```

**New Behavior**: WSOL balance changes are tracked and used for inference
```python
# New code - WSOL is tracked
WSOL = "So11111111111111111111111111111111111111112"
# ... track all changes including WSOL
owner_changes[owner][mint] = {
    'delta': delta,
    'pre_amount': pre_amount,
    'post_amount': post_amount
}
```

#### 2. Buy/Sell Inference Logic

**Buy Detection**:
```python
if delta > 0 and wsol_delta < 0:
    # Token increases, WSOL decreases → BUY
    action_type = 'buy'
    mint_in = WSOL      # User spent WSOL
    mint_out = mint     # User received token
elif delta > 0:
    # Token increases without WSOL context → assume BUY (WSOL→token)
    action_type = 'buy'
    mint_in = WSOL      # Default: assume WSOL input
    mint_out = mint
```

**Sell Detection**:
```python
elif delta < 0 and wsol_delta > 0:
    # Token decreases, WSOL increases → SELL
    action_type = 'sell'
    mint_in = mint      # User spent token
    mint_out = WSOL     # User received WSOL
elif delta < 0:
    # Token decreases without WSOL context → assume SELL (token→WSOL)
    action_type = 'sell'
    mint_in = mint
    mint_out = WSOL     # Default: assume WSOL output
```

**Unknown Action Fallback**:
When action cannot be determined from balance deltas, the system defaults to 'buy' (WSOL→token_mint):
```python
# In _extract_action_with_fallback
# PRIORITY 5: Default to 'buy' for permissive execution
# If action is still unknown, let builders default to buy (WSOL→token_mint)
logger.warning(f"   Defaulting to 'buy' (WSOL→token_mint) for improved route selection")
return 'buy'
```

#### 3. mint_in and mint_out Fields

These fields are now saved in the action_data dictionary:
```python
action_data = {
    'action': action_type,
    'owner': owner,
    'mint': mint,
    'amount': amount,
    'delta': delta,
    'pre_amount': pre_amount,
    'post_amount': post_amount,
    'method': 'token_balance_delta',
    'mint_in': mint_in,      # NEW: Input mint
    'mint_out': mint_out     # NEW: Output mint
}
```

#### 4. Enhanced Logging

Added the required logging format as specified:
```python
# Log detected action as per problem statement
logger.info(f"🎯 Detected action={action_type}")

# Also log mint routing
if mint_in:
    logger.info(f"   Mint In: {mint_in}")
if mint_out:
    logger.info(f"   Mint Out: {mint_out}")
```

### Owner Grouping Strategy

The implementation groups balance changes by owner to analyze WSOL and token changes together:

```python
# Group by owner to track WSOL and token changes together
owner_changes = {}  # owner -> {mint: delta}

for (owner, mint) in all_pairs:
    if owner not in owner_changes:
        owner_changes[owner] = {}
    owner_changes[owner][mint] = {
        'delta': delta,
        'pre_amount': pre_amount,
        'post_amount': post_amount
    }

# Analyze changes per owner
for owner, changes in owner_changes.items():
    wsol_delta = changes.get(WSOL, {}).get('delta', 0)
    # ... infer buy/sell based on WSOL + token changes
```

## Benefits

### 1. Accurate Trade Direction
- No longer relies on logs or instructions alone
- Uses actual balance changes to determine buy/sell
- More reliable for complex transactions

### 2. Correct Executor Routing
- `mint_in` and `mint_out` allow executors to construct correct swap paths
- Executors know exactly which tokens are involved in the trade
- Reduces execution errors from incorrect routing

### 3. Enhanced Debugging
- Clear logging shows WSOL deltas alongside token deltas
- mint_in/mint_out visible in logs for troubleshooting
- Better audit trail for trade analysis

### 4. Fallback Logic
- Still handles cases without WSOL context
- Gracefully degrades to simple increase/decrease logic
- Ensures trades are not skipped unnecessarily

## Example Output

### Buy Trade Example
```
🔍 [DELTA_DETECTION] Analyzing 4 pre + 4 post token balances
🎯 [DELTA_DETECTION] Monitoring 1 wallets: ['WalletAd...']
🟢 [DELTA_DETECTION] BUY detected: WalletAd.../TokenMin... +100.000000 (WSOL: -0.500000)
🎯 Detected action=buy
📝 [ACTION_LOG] Detected Action #1
   Action: BUY
   Token: TokenMint111...
   Wallet: WalletAddress111...
   Amount: 100.000000
   Delta: +100.000000
   Pre-Balance: 0.000000
   Post-Balance: 100.000000
   Mint In: So11111111111111111111111111111111111111112
   Mint Out: TokenMint111...
   Detection Method: token_balance_delta
```

### Sell Trade Example
```
🔍 [DELTA_DETECTION] Analyzing 4 pre + 4 post token balances
🎯 [DELTA_DETECTION] Monitoring 1 wallets: ['WalletAd...']
🔴 [DELTA_DETECTION] SELL detected: WalletAd.../TokenMin... -100.000000 (WSOL: +0.500000)
🎯 Detected action=sell
📝 [ACTION_LOG] Detected Action #1
   Action: SELL
   Token: TokenMint111...
   Wallet: WalletAddress111...
   Amount: 100.000000
   Delta: -100.000000
   Pre-Balance: 100.000000
   Post-Balance: 0.000000
   Mint In: TokenMint111...
   Mint Out: So11111111111111111111111111111111111111112
   Detection Method: token_balance_delta
```

## Testing

### Validation Tests
Created `validate_buy_sell_inference.py` to verify:
- ✅ WSOL constant is defined
- ✅ WSOL balance changes are tracked (not skipped)
- ✅ Balance changes are grouped by owner
- ✅ BUY inference logic (WSOL down + token up)
- ✅ SELL inference logic (token down + WSOL up)
- ✅ mint_in and mint_out fields are saved
- ✅ Required logging format present
- ✅ mint_in and mint_out are logged

All 8 validation tests pass ✅

### Usage in Executors

Executors can now access mint routing information:
```python
# Access detected balance actions
actions = trade_info.get('detected_balance_actions', [])
for action in actions:
    action_type = action['action']  # 'buy' or 'sell'
    mint_in = action.get('mint_in')  # Input token
    mint_out = action.get('mint_out')  # Output token
    
    # Use mint_in and mint_out to construct correct swap path
    if action_type == 'buy':
        # Buy: WSOL → Token
        # Execute swap from mint_in to mint_out
    elif action_type == 'sell':
        # Sell: Token → WSOL
        # Execute swap from mint_in to mint_out
```

## Conclusion

The buy/sell side inference implementation successfully:
1. ✅ Compares preTokenBalances vs postTokenBalances
2. ✅ Infers buy/sell based on WSOL balance changes
3. ✅ Saves mint_in and mint_out for executor routing
4. ✅ Logs detected actions with required format
5. ✅ **NEW**: Defaults to 'buy' (WSOL→token_mint) when action is unknown
6. ✅ **NEW**: Sets mint_in=WSOL default for buy cases without WSOL context
7. ✅ **NEW**: Sets mint_out=WSOL default for sell cases without WSOL context

This enhancement ensures trades are correctly labeled as BUY or SELL, allowing executors to use the correct execution path and improving trade execution reliability. The fallback to 'buy' ensures that even when action cannot be determined, the system makes a sensible default assumption that improves route selection and slippage settings.
