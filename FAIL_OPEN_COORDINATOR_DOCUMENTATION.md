# Fail-Open Coordinator Implementation

## Overview

This document describes the implementation of fail-open coordinator logic in the execution system. The fail-open coordinator ensures that trade execution attempts are **never blocked** by missing or unparseable fields like DEX or amount. Instead, the coordinator normalizes inputs using sensible defaults and fallback values, then proceeds with execution.

## Problem Statement

Previously, the execution system would stall or fail when:
- The parser couldn't infer which DEX (jupiter, raydium, meteora, etc.) was used
- The parser couldn't determine the trade amount
- Action (buy/sell) wasn't clearly identified

This resulted in missed trading opportunities and reduced system reliability.

## Solution: Fail-Open Coordinator

The fail-open coordinator implements a "proceed with defaults" strategy:

### 1. Normalization Layer

When `maybe_execute()` receives `trade_info`, it normalizes all fields:

```python
# Amount normalization
if not amount_sol or not isinstance(amount_sol, (int, float)) or amount_sol <= 0:
    amount_sol = INVESTMENT_PER_TRADE_SOL  # from config.py
    trade_info["amount_sol"] = amount_sol

# Action normalization  
if not action or not isinstance(action, str):
    action = "buy"  # default to buy
    trade_info["action"] = action

# DEX normalization
if dex not in ["jupiter", "pumpfun", "raydium", "meteora"]:
    dex = "unknown"
    trade_info["dex"] = dex
```

### 2. Fallback Routing

The `ROUTE_MAP` defines execution paths for each DEX. When DEX is unknown:

```python
ROUTE_MAP = {
    "jupiter":   ["jupiter", "raydium", "direct_copy", "meteora"],
    "pumpfun":   ["pumpfun", "direct_copy", "jupiter", "raydium", "meteora"],
    "raydium":   ["raydium", "direct_copy", "jupiter", "meteora"],
    "meteora":   ["meteora", "raydium", "jupiter", "direct_copy"],
    "unknown":   ["direct_copy", "jupiter", "raydium", "meteora"],  # Fallback
}
```

For unknown DEX, the coordinator tries:
1. **direct_copy** - Clone the original transaction (if signature available)
2. **jupiter** - Build fresh transaction via Jupiter
3. **raydium** - Build via Raydium executor
4. **meteora** - Build via Meteora executor

### 3. Signature-Based Execution

Even without a token_mint, if a signature is available, the coordinator attempts `direct_copy`:

```python
if not token_mint or token_mint in ("UNKNOWN", "PENDING_ANALYSIS", "unknown", ""):
    signature = trade_info.get("signature")
    if signature:
        logger.info("✅ [FAIL-OPEN] Signature available, attempting direct_copy despite missing mint")
        return await execute_direct_copy(trade_info, rpc_url, keypair, jito_service)
```

## Configuration

### config.py

Added the `INVESTMENT_PER_TRADE_SOL` constant:

```python
# === Fail-Open Coordinator Configuration ===
INVESTMENT_PER_TRADE_SOL = 0.001  # Default investment amount when parser cannot infer amount
```

This value is used when:
- `amount_sol` is missing from trade_info
- `amount_sol` is invalid (negative, zero, non-numeric)
- Parser failed to extract amount from transaction

## Code Changes

### execution_coordinator.py

#### maybe_execute() Function

**Before:** Failed immediately if DEX or amount missing  
**After:** Normalizes all fields and proceeds with defaults

Key changes:
1. Import `INVESTMENT_PER_TRADE_SOL` from config
2. Normalize amount, action, and DEX at function start
3. Update `trade_info` dict with normalized values
4. Enhanced logging for all normalization decisions
5. Allow signature-based execution without mint

#### _execute_copy_buy() Method

**Before:** Used raw trade_info without validation  
**After:** Re-validates normalized values with fallbacks

Key changes:
1. Added fail-open normalization at executor level
2. Uses normalized amount from trade_info with fallback chain
3. Enhanced routing logic with fail-open logging
4. Added summary logging on failure showing normalized values

## Logging

The fail-open coordinator adds comprehensive logging:

### Normalization Logging
```
🔧 [FAIL-OPEN] Amount missing/invalid, using default: 0.001 SOL
🔧 [FAIL-OPEN] Action missing, defaulting to: buy
🔧 [FAIL-OPEN] DEX 'unknown_protocol' not recognized, treating as 'unknown'
```

### Routing Logging
```
[FAIL-OPEN ROUTING] DEX: unknown, Source failed: False, Mint available: True
[FAIL-OPEN] Using builder-first fallback route for unknown DEX with mint
[ROUTING] Using ROUTE_MAP for dex='unknown': ['direct_copy', 'jupiter', 'raydium', 'meteora']
```

### Execution Logging
```
[FAIL-OPEN] Despite all executor failures, attempt was made using fallback routes
[FAIL-OPEN] Trade detection triggered execution with normalized values:
   - Amount: 0.001 SOL (from config or trade_info)
   - DEX: unknown (normalized)
   - Route: ['direct_copy', 'jupiter', 'raydium', 'meteora']
```

## Testing

Created comprehensive test suite in `test_fail_open_coordinator.py`:

### Test Coverage

1. **Configuration Tests**
   - Verifies `INVESTMENT_PER_TRADE_SOL` is exposed and valid

2. **Normalization Tests**
   - Tests `normalize_dex()` function with various inputs
   - Verifies `ROUTE_MAP` has fallback for 'unknown'

3. **Fail-Open Behavior Tests**
   - Amount normalization (missing → config default)
   - Action normalization (missing → 'buy')
   - DEX normalization (invalid → 'unknown')
   - Signature-only execution capability

### Running Tests

```bash
python3 test_fail_open_coordinator.py
```

Expected output:
```
🎉 ALL TESTS PASSED! Fail-open coordinator is working correctly.
Total: 7/7 tests passed
```

## Examples

### Example 1: Missing Amount

**Input:**
```python
trade_info = {
    "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "dex": "jupiter",
    "signature": "abc123..."
    # amount_sol missing
}
```

**Behavior:**
- Normalizes amount to `0.001` (from `INVESTMENT_PER_TRADE_SOL`)
- Proceeds with Jupiter execution
- Logs: `🔧 [FAIL-OPEN] Amount missing/invalid, using default: 0.001 SOL`

### Example 2: Unknown DEX

**Input:**
```python
trade_info = {
    "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "dex": "some_new_protocol",
    "amount_sol": 0.005
}
```

**Behavior:**
- Normalizes DEX to `unknown`
- Uses fallback route: `[direct_copy, jupiter, raydium, meteora]`
- Tries each executor in order until one succeeds
- Logs: `[FAIL-OPEN] DEX unknown - using fallback route order from ROUTE_MAP`

### Example 3: Missing Action

**Input:**
```python
trade_info = {
    "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "dex": "raydium",
    "amount_sol": 0.01
    # action missing
}
```

**Behavior:**
- Normalizes action to `buy`
- Proceeds with Raydium buy execution
- Logs: `🔧 [FAIL-OPEN] Action missing, defaulting to: buy`

### Example 4: Signature-Only (No Mint)

**Input:**
```python
trade_info = {
    "signature": "xyz789...",
    "dex": "unknown"
    # token_mint missing
}
```

**Behavior:**
- Attempts `direct_copy` using signature
- Clones original transaction structure
- Logs: `✅ [FAIL-OPEN] Signature available, attempting direct_copy despite missing mint`

## Definition of Done

All requirements from the problem statement are met:

✅ **Config Exposure**
- `config.py` exposes `INVESTMENT_PER_TRADE_SOL`
- Value exported in `__all__` for clean imports

✅ **Fail-Open Logic**
- Coordinator normalizes missing/invalid DEX to 'unknown'
- Coordinator normalizes missing/invalid amount to config default
- Coordinator normalizes missing action to 'buy'
- Selection of route from `ROUTE_MAP` or fallback route

✅ **Execution Behavior**
- Always attempts trade execution when trade detected
- Never stalls on missing DEX or amount
- Iterates through route paths until success
- Uses unified submit helper (`send_and_confirm_v0_tx` via `try_submit`)

✅ **Logging**
- Standardized logging for all normalization decisions
- Clear routing logs showing fallback route selection
- Success/failure logs with route and executor information
- Summary logs on failure showing normalized values used

✅ **Testing**
- Comprehensive test suite covering all fail-open behaviors
- All 7 tests passing
- Tests validate config, normalization, and execution logic

## Performance Impact

The fail-open coordinator adds minimal overhead:

1. **Normalization**: O(1) field checks and assignments
2. **Logging**: Only when fields are missing (rare in normal operation)
3. **Routing**: Uses existing `ROUTE_MAP` logic
4. **Execution**: No change to executor performance

In exchange, the system gains:
- Higher execution rate (no stalls on missing fields)
- Better reliability (sensible defaults prevent failures)
- Improved observability (comprehensive logging)

## Future Enhancements

Potential improvements:

1. **Adaptive Defaults**: Learn optimal `INVESTMENT_PER_TRADE_SOL` per token
2. **Smart DEX Detection**: Use ML to infer DEX from transaction patterns
3. **Route Optimization**: Track success rates per route and reorder dynamically
4. **Amount Inference**: Estimate amount from similar transactions
5. **Partial Execution**: Execute with partial information and backfill later

## Conclusion

The fail-open coordinator transforms the execution system from a brittle, fail-fast model to a resilient, fail-open model. By normalizing inputs and using sensible defaults, the system maintains high availability while preserving execution quality through comprehensive logging and fallback routing.
