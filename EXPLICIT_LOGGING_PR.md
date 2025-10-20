# Explicit Logging for Direct Copy and Meteora Routing

## Overview

This PR adds explicit logging when:
1. `route_hint` is set to `'direct_copy'` in `validate_trade_info()` due to unresolved mint but present signature
2. Meteora route is prioritized in `execution_coordinator` for `dex == 'meteora'`

## Problem Statement

> Stay within the existing rpc client used across the repo. Do not introduce new dependencies. Keep logging consistent with existing format (INFO/WARNING/ERROR emojis).
> 
> Task: Log explicitly when direct_copy fallback is chosen when mint remains unresolved but signature is present, and when Meteora route is prioritized for 'meteora' dex.

## Changes Made

### 1. trade_processor.py - validate_trade_info()

**Before:**
```python
logger.info("✅ [VALIDATION] Allowing execution via direct_copy (mint unresolved but signature present)")
```

**After:**
```python
logger.info("✅ [VALIDATION] route_hint='direct_copy' fallback - Allowing execution via direct_copy (mint unresolved but signature present)")
```

**What Changed:**
- Explicitly mentions `route_hint='direct_copy'` in the log message
- Makes it clear that route_hint is being set to 'direct_copy' as a fallback mechanism
- Maintains existing emoji format (✅ for approval/success)
- Maintains existing prefix ([VALIDATION])

### 2. execution_coordinator.py - Meteora Routing

**No changes needed** - Already has explicit logging:

```python
if dex_key == "meteora":
    self.logger.info(f"[ROUTING] ℹ️  Meteora detected - route prioritizes meteora executor first")
```

This log:
- Explicitly states that Meteora is detected
- Explicitly states that the route prioritizes meteora executor first
- Uses ℹ️ emoji for informational message (consistent with routing context)
- Uses [ROUTING] prefix

## Logging Format Consistency

The implementation follows the existing logging format:

### Emojis Used
- ✅ - Approval/Success messages (decisions, approvals)
- ℹ️ - Informational messages (context, detection)
- ❌ - Error messages
- 🛑 - Warning/Rejection messages

### Prefixes Used
- `[VALIDATION]` - Validation-related logs in trade_processor.py
- `[ROUTING]` - Routing-related logs in execution_coordinator.py

## Test Coverage

### New Test: test_explicit_logging.py
Validates:
- ✅ validate_trade_info() explicitly logs route_hint='direct_copy' setting
- ✅ execution_coordinator explicitly logs Meteora route prioritization
- ✅ Logging format consistency (emoji usage, prefixes)

### Existing Tests (All Pass)
- ✅ test_relaxed_validation.py - 3/3 tests passed
- ✅ test_route_hint_and_meteora.py - 4/4 tests passed
- ✅ test_direct_copy_cloner.py - All validations passed
- ✅ test_debugging_enhancements.py - 8/8 tests passed

## Benefits

1. **Explicit route_hint Logging**: Now clearly states when route_hint is being set to 'direct_copy', making debugging easier
2. **Meteora Routing Clarity**: Confirms that Meteora routing explicitly prioritizes meteora executor
3. **No New Dependencies**: Uses existing RPC client and logging infrastructure
4. **Format Consistency**: Maintains INFO/WARNING/ERROR emoji format throughout
5. **Backward Compatibility**: All existing tests pass without modification

## Example Logs

### Direct Copy Fallback
```
✅ [VALIDATION] route_hint='direct_copy' fallback - Allowing execution via direct_copy (mint unresolved but signature present)
```

### Meteora Route Prioritization
```
[ROUTING] Using ROUTE_MAP for dex='meteora': ['meteora', 'raydium', 'jupiter', 'direct_copy']
[ROUTING] ℹ️  Meteora detected - route prioritizes meteora executor first
[ROUTING] Execution plan: ['meteora', 'raydium', 'jupiter', 'direct_copy']
```

## Files Changed

1. **trade_processor.py** (1 line changed)
   - Updated log message to explicitly mention route_hint='direct_copy'

2. **test_explicit_logging.py** (new file)
   - Added comprehensive test for explicit logging validation

## No Breaking Changes

- All existing tests pass
- No changes to functionality, only logging clarity
- No new dependencies added
- Maintains existing emoji and prefix conventions
