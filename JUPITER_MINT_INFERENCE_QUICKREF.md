# Jupiter Token Mint Inference - Quick Reference

## When Does It Run?
The Jupiter-specific token mint inference logic triggers when:
- `dex_type == 'jupiter'` 
- `token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', None, '']`
- `postTokenBalances` are present in transaction meta

## What Does It Do?

### Step 1: Extract Token Balances
```python
pre_token_balances = meta.get('preTokenBalances', [])
post_token_balances = meta.get('postTokenBalances', [])
```

### Step 2: Build Pre-Balance Map
```python
pre_map = {}  # {(owner, mint): amount}
for balance in pre_token_balances:
    pre_map[(owner, mint)] = float(uiAmount)
```

### Step 3: Calculate Deltas and Find Best
```python
WSOL = "So11111111111111111111111111111111111111112"
best_mint = None
best_delta = 0.0

for balance in post_token_balances:
    if mint != WSOL:  # Exclude WSOL
        delta = post_amount - pre_map.get((owner, mint), 0)
        if delta > best_delta:  # Only positive deltas
            best_delta = delta
            best_mint = mint
```

### Step 4: Set Result
```python
if best_mint:
    token_mint = best_mint
    trade_info['token_mint'] = best_mint
else:
    token_mint = None  # Input-only swap
    trade_info['token_mint'] = None
```

## Examples

### Example 1: BUY (Positive Delta)
```python
# Pre-balances: WSOL=1.0, TokenA=0
# Post-balances: WSOL=0.5, TokenA=1000.0

# Deltas:
#   WSOL: 0.5 - 1.0 = -0.5 (excluded anyway)
#   TokenA: 1000.0 - 0 = +1000.0 ✅

# Result: token_mint = 'TokenA'
```

### Example 2: SELL (Negative Delta)
```python
# Pre-balances: TokenA=1000.0
# Post-balances: TokenA=500.0

# Deltas:
#   TokenA: 500.0 - 1000.0 = -500.0 (negative, not selected)

# Result: token_mint = None (input-only swap)
```

### Example 3: WSOL Exclusion
```python
# Pre-balances: WSOL=10.0, TokenA=0
# Post-balances: WSOL=1000.0, TokenA=100.0

# Deltas:
#   WSOL: +990 (excluded - is WSOL)
#   TokenA: +100.0 ✅

# Result: token_mint = 'TokenA'
```

## Code Location
- **File:** `trade_processor.py`
- **Lines:** 743-806
- **Method:** `analyze_and_route_trade()`
- **Position:** After DEX detection, before uncertainty debugging

## Logging
The implementation includes comprehensive logging:
- `🎯 [JUPITER_MINT_INFERENCE] Attempting...` - Start of inference
- `✅ [JUPITER_MINT_INFERENCE] Set token_mint to...` - Success with positive delta
- `⚠️ [JUPITER_MINT_INFERENCE] No positive deltas found...` - None case
- `❌ [JUPITER_MINT_INFERENCE] Exception...` - Error handling

## Testing
Run standalone tests:
```bash
python test_jupiter_mint_logic.py
```

Expected output:
```
RESULTS: 4 passed, 0 failed
```

## Edge Cases Handled
✅ Missing `preTokenBalances` → Assumes 0 for all mints  
✅ Missing `postTokenBalances` → Skips inference  
✅ No meta information → Skips inference  
✅ All negative deltas → Sets `token_mint = None`  
✅ WSOL has largest delta → Excludes WSOL, picks next best  
✅ Non-Jupiter DEX → Skips logic entirely  

## Integration with Pipeline
1. **Before:** DEX detection sets `dex_type = 'jupiter'`
2. **This logic:** Sets `token_mint` based on deltas
3. **After:** Uncertainty debugging logs if still unknown
4. **Finally:** Execution validation checks requirements

## Notes
- Only considers **positive** deltas (tokens acquired, not spent)
- Always excludes WSOL (`So111...112`)
- Sets `None` for input-only swaps (no positive deltas)
- Updates both `token_mint` variable and `trade_info['token_mint']`
