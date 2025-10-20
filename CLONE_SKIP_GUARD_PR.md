# Clone Skip Guard for Slippage-Failed Transactions

## Overview
This PR implements a guard in the `_execute_direct_copy_buy` method to prevent cloning of slippage-failed source transactions when `retry_hint == "requote"`.

## Problem Statement
When a source transaction fails due to slippage (error 6004), cloning it would likely result in the same failure. Instead, the coordinator should try builders (Jupiter/Meteora) first, which can use fresh quotes and wider slippage tolerance.

## Solution

### Implementation
Added a guard at the beginning of `_execute_direct_copy_buy` in `execution_coordinator.py`:

```python
# Guard: Skip cloning slippage-failed source transactions
if trade_info and trade_info.get("retry_hint") == "requote":
    logger.info("ℹ️ [CLONE] Skipping clone of a slippage-failed source — using builders first")
    return None
```

### Key Features
- **Early Guard**: Checks `retry_hint` before attempting to clone
- **Returns None**: Allows coordinator to try next executor in plan (builders)
- **Emoji Logging**: Uses ℹ️ [CLONE] prefix for consistency
- **No New Dependencies**: Uses existing infrastructure only
- **Minimal Change**: 5 lines added to execution_coordinator.py

## Execution Flow

### When retry_hint == "requote"
1. `_execute_direct_copy_buy` is called
2. Guard detects `retry_hint == "requote"`
3. Logs: "ℹ️ [CLONE] Skipping clone of a slippage-failed source — using builders first"
4. Returns `None` immediately
5. Coordinator tries next executor (Jupiter or Meteora)
6. Builders use fresh quotes with wider slippage tolerance

### When retry_hint != "requote" (normal flow)
1. Guard check passes
2. Continues to signature extraction
3. Proceeds with normal clone logic
4. Clones transaction and submits via FastExecutor

## Testing

### New Test: `test_clone_skip_slippage.py`
Validates:
- ✅ Guard checks `retry_hint == "requote"` in `_execute_direct_copy_buy`
- ✅ Returns `None` when retry_hint is "requote"
- ✅ Uses emoji logging (ℹ️ [CLONE])
- ✅ No new dependencies added
- ✅ Correctly positioned before signature extraction

### Regression Tests
All existing tests pass:
- ✅ `test_direct_copy_cloner.py` - Direct copy integration
- ✅ `test_routing_logic.py` - Routing logic validation

## Files Changed
1. **execution_coordinator.py** (5 lines added)
   - Added guard in `_execute_direct_copy_buy`
   
2. **test_clone_skip_slippage.py** (new file)
   - Comprehensive test suite for the guard logic

## Benefits
1. **Prevents Duplicate Failures**: Doesn't waste time cloning transactions that will fail
2. **Better Success Rate**: Builders can use fresh quotes and wider slippage
3. **Efficient Routing**: Immediately tries alternative executors
4. **Clean Implementation**: Minimal change, no new dependencies
5. **Well Tested**: Comprehensive test coverage with regression testing
