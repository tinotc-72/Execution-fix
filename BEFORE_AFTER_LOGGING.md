# Before and After: maybe_execute Logging Improvements

## Changes Summary

Enhanced the `maybe_execute` function in `execution_coordinator.py` to ensure better debugging with full stack traces and clear fallback logging.

## Key Changes

### 1. Exception Logging - Added exc_info=True

**Before:**
```python
except Exception as e:
    logger.error(f"❌ [EXECUTION] submission failed: {e}")
    return False
```

**After:**
```python
except Exception as e:
    logger.error(f"❌ [EXECUTION] submission failed: {e}", exc_info=True)
    return False
```

This applies to **all 5 exception handlers** in the function:
- try_submit helper
- execute_direct_copy_fallback
- Meteora build error
- Jupiter build error (meteora path)
- Jupiter build error (unknown path)

### 2. Meteora Route Logging - Show prefer_clone Flag

**Before:**
```python
logger.info("🧭 [COORDINATOR] Route=meteora")
```

**After:**
```python
logger.info("🧭 [COORDINATOR] Route=meteora (prefer_clone=%s)", prefer_clone)
```

### 3. Fallback Warnings - Added Clear Messages

**Before:**
```python
# No warning before calling execute_direct_copy_fallback()
return await execute_direct_copy_fallback()
```

**After:**
```python
logger.warning("⚠️ Builders failed — falling back to direct_copy")
return await execute_direct_copy_fallback()
```

Applied to 3 fallback paths:
- Meteora → direct_copy
- Unknown with mint → direct_copy  
- Unknown without mint → direct_copy

### 4. Removed Duplicate Warning

**Before (inside execute_direct_copy_fallback):**
```python
async def execute_direct_copy_fallback():
    """Fall back to transaction cloning"""
    logger.warning("⚠️ Builders failed — falling back to direct_copy")  # DUPLICATE
    signature = trade_info.get("signature")
    ...
```

**After (removed from function):**
```python
async def execute_direct_copy_fallback():
    """Fall back to transaction cloning"""
    signature = trade_info.get("signature")
    ...
```

## Example Log Output

### Before (No Stack Traces):
```
🧭 [COORDINATOR] Route=meteora
❌ [METEORA] build error: Connection timeout
❌ [JUPITER] build error: Invalid token address
⚠️ Builders failed — falling back to direct_copy  # Only showed once at end
```

### After (With Full Stack Traces):
```
🧭 [COORDINATOR] Route=meteora (prefer_clone=False)
❌ [METEORA] build error: Connection timeout
Traceback (most recent call last):
  File "execution_coordinator.py", line 160, in maybe_execute
    vtx = meteora_build_and_sign(trade_info, rpc, keypair)
  ...full stack trace...
⚠️ Meteora build failed — trying Jupiter
❌ [JUPITER] build error: Invalid token address
Traceback (most recent call last):
  File "execution_coordinator.py", line 174, in maybe_execute
    vtx = jupiter_build_buy_tx(token_mint_str, amount_sol, keypair)
  ...full stack trace...
⚠️ Builders failed — falling back to direct_copy
```

## Benefits

1. **🔍 Better Debugging**: Full stack traces help identify root causes immediately
2. **📊 Clear Execution Flow**: Visible warnings show exactly which fallback path was taken
3. **🎯 Consistent Logging**: All error paths follow the same pattern with emoji indicators
4. **🚀 No Duplication**: Removed duplicate warning messages

## Tests Pass

All existing tests continue to pass:
- ✅ test_maybe_execute.py (6/6 tests)
- ✅ test_exc_info_logging.py (2/2 tests)
- ✅ test_problem_statement_requirements.py (7/7 tests)
