# Logging Improvements in maybe_execute

## Summary

Enhanced error logging in the `maybe_execute` function in `execution_coordinator.py` to ensure better debugging capabilities with full stack traces.

## Changes Made

### 1. Added `exc_info=True` to All Error Logging

All `logger.error()` calls in exception handlers now include `exc_info=True` to capture full stack traces:

- **try_submit helper** (line 127): `logger.error(f"❌ [EXECUTION] submission failed: {e}", exc_info=True)`
- **execute_direct_copy_fallback** (line 146): `logger.error(f"❌ [DIRECT_COPY] Clone failed: {e}", exc_info=True)`
- **Meteora build error** (line 162): `logger.error(f"❌ [METEORA] build error: {e}", exc_info=True)`
- **Jupiter build error** (line 179): `logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)`
- **Jupiter build error in unknown path** (line 217): `logger.error(f"❌ [JUPITER] build error: {e}", exc_info=True)`

### 2. Enhanced Meteora Route Logging

Updated the meteora route log to show the `prefer_clone` flag:

```python
logger.info("🧭 [COORDINATOR] Route=meteora (prefer_clone=%s)", prefer_clone)
```

This makes it clear whether the clone path is preferred or builder logic is used.

### 3. Added Fallback Warnings

Added clear warning messages before falling back to `direct_copy`:

- **Meteora → Jupiter → direct_copy path** (line 185): `logger.warning("⚠️ Builders failed — falling back to direct_copy")`
- **Unknown with mint → direct_copy path** (line 220): `logger.warning("⚠️ Builders failed — falling back to direct_copy")`
- **Unknown without mint → direct_copy** (line 224): `logger.warning("⚠️ No builder available — falling back to direct_copy")`

### 4. Removed Duplicate Logging

Removed the duplicate warning message from inside `execute_direct_copy_fallback()` since the warning is now logged at the call site.

## Benefits

1. **Better Debugging**: Full stack traces with `exc_info=True` help identify the root cause of errors
2. **Clear Execution Path**: Visible fallback warnings show the exact execution flow
3. **Consistent Logging**: All error paths follow the same logging pattern with emoji indicators
4. **No Code Duplication**: Removed duplicate warning messages

## Testing

All tests pass:

1. ✅ `test_maybe_execute.py` - Validates meteora routing logic (6/6 tests passed)
2. ✅ `test_exc_info_logging.py` - Validates exc_info usage (2/2 tests passed)
3. ✅ `test_problem_statement_requirements.py` - Validates requirements (7/7 passed)

## Code Example

```python
# Before: No stack trace
logger.error(f"❌ [EXECUTION] submission failed: {e}")

# After: Full stack trace for debugging
logger.error(f"❌ [EXECUTION] submission failed: {e}", exc_info=True)
```

## Files Changed

- `execution_coordinator.py` - Updated error logging in `maybe_execute` function
- `test_exc_info_logging.py` - New test to validate logging improvements
