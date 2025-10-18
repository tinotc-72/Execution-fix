# meteora: use unified executor (Jito→RPC) instead of bundle parsing

## Why

Bundle parsing expected `{"success": ..., "signature": ...}` which our Jito JSON-RPC does not return. This caused:
- ❌ False negatives (successful submissions marked as failures)
- ❌ No fallback to RPC when Jito fails
- ❌ Inconsistent/missing logs

## What

All Meteora submits now use `FastExecutor.send_and_confirm(vtx)` which:
- ✅ Properly parses JSON-RPC responses (signature string, not bundle dict)
- ✅ Automatically tries Jito first, then falls back to RPC
- ✅ Confirms transactions on-chain before returning
- ✅ Provides standardized logging

## Test

Trigger a Meteora trade; expect:
```
[SUBMIT_JITO] region=<url> sig=<signature>  # or [SUBMIT_RPC] if fallback
[CONFIRM] attempt=1/5 status=<status>
[CONFIRM][FINAL] sig=<signature> status=<status>
✅ Meteora buy successful!
```

## Files Changed

### Core Implementation
- **mev_meteora_executor.py** (135 insertions, 155 deletions)
  - `__init__` accepts `fast_executor` instead of `jito_service`
  - Removed `_execute_with_jito` and `_execute_standard` (bundle parsing)
  - Added `_execute_via_fast_executor` using FastExecutor
  - Updated `execute_buy`, `execute_sell`, `mev_meteora_copy_trade`

### Testing & Documentation
- **test_meteora_fast_executor.py** - Comprehensive test suite (all pass ✅)
- **METEORA_FAST_EXECUTOR_INTEGRATION.md** - Technical documentation
- **BEFORE_AFTER_METEORA_FASTEXECUTOR.md** - Side-by-side comparison
- **METEORA_FLOW_DIAGRAM.md** - Visual flow diagrams
- **PR_SUMMARY_METEORA_FASTEXECUTOR.md** - Complete PR summary

## Key Code Change

### Before (Broken)
```python
result = await jito_service.send_bundle([transaction])
if result.get("success"):  # ❌ Never worked
    signature = result.get("signature")
    return MeteoraTradeResult(success=True, signature=signature)
```

### After (Fixed)
```python
sig = await fast_executor.send_and_confirm(vtx)
if not sig:
    return MeteoraTradeResult(success=False, error="submit failed (Jito+RPC)")
return MeteoraTradeResult(success=True, signature=sig)
```

## Validation

```bash
python test_meteora_fast_executor.py
```

Output:
```
Tests Passed: 5/5
🎉 ALL TESTS PASSED!
```

## Impact

All Meteora trade executions now use the unified FastExecutor path:
- `execute_buy()` - Meteora DBC buys
- `execute_sell()` - Meteora DBC sells  
- `mev_meteora_copy_trade()` - Copy trading wrapper
- `try_meteora_buy()` - Compatibility wrapper
- `try_meteora_sell_all()` - Compatibility wrapper
