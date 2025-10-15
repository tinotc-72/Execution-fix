# Pipeline Route and Execute Implementation

## Summary

This implementation adds the required pipeline flow enhancements as specified in the problem statement. The changes ensure that trade execution continues even when deep analysis is required, by making the analysis non-blocking.

## Changes Made

### 1. Helper Functions (Top of main.py)

#### `_have_all_fields(trade_info: dict) -> bool` (Line 226-247)
- ✅ **Already existed** - treats `mint` and `token_mint` as synonyms
- Normalizes to `token_mint` if only `mint` is present
- Validates all required fields: `dex`, `action`, `wallet_address`, and `token_mint`/`mint`
- Returns `False` for invalid values: `None`, `""`, `"unknown"`, `"PENDING_ANALYSIS"`

#### `schedule_deep_analysis(trade_info: dict)` (Line 283-297)
- ✅ **Added** - Non-blocking function to schedule deep analysis
- Currently a stub that can be extended to create background async tasks
- Used when `requires_full_analysis` is set but we want to continue to fast-path execution

#### `route_and_execute(trade_info: dict, rpc, keypair, jito=None)` (Line 300-335)
- ✅ **Already existed** - Async function that routes to execution coordinator
- Validates fields using `_have_all_fields()` before execution
- Logs handoff to coordinator with emoji markers
- Wraps `maybe_execute()` call in try/except for error handling

### 2. Pipeline Flow (Line 860-882)

The flow after `infer_missing_fields` now follows this pattern:

```python
# STEP 1: Infer missing fields
trade_info = self.trade_processor.infer_missing_fields(trade_info)
logger.debug(f"[DEBUG] After infer_missing_fields: ...")

# Do NOT return early on requires_full_analysis
if trade_info.get("requires_full_analysis"):
    try:
        schedule_deep_analysis(trade_info)  # non-blocking
        logger.info("ℹ️ scheduled deep analysis (non-blocking); continuing to fast-path")
    except Exception as e:
        logger.warning(f"⚠️ deep analysis scheduling failed: {e}")

# Compute per-trade mode and call the coordinator
have_all = _have_all_fields(trade_info)
trade_info["use_universal_cloner"] = not have_all
logger.info("✅ [MODE] Builders %s; Cloner as %s",
            "ENABLED (complete fields)" if have_all else "DISABLED",
            "fallback" if have_all else "PRIMARY")

logger.info("📤 [HANDOFF] Calling coordinator now…")
await route_and_execute(trade_info, rpc=self.rpc_client, keypair=self.wallet, jito=self.jito_service)
logger.info("📥 [HANDOFF] Coordinator call returned")
```

## Key Behaviors

### 1. No Early Return on requires_full_analysis
- ✅ When `requires_full_analysis` is set, the code does NOT return early
- ✅ Instead, it calls `schedule_deep_analysis()` non-blocking
- ✅ Then continues to check fields and call coordinator if ready

### 2. Field Synonym Handling
- ✅ `_have_all_fields()` accepts both `mint` and `token_mint`
- ✅ Normalizes by setting `token_mint` if only `mint` is present
- ✅ Prevents execution failures due to field name mismatches

### 3. Execution Handoff Logging
- ✅ Logs "📤 [HANDOFF] Calling coordinator now…" before execution
- ✅ Logs "📥 [HANDOFF] Coordinator call returned" after execution
- ✅ Logs field readiness status with mode selection

### 4. Mode Selection
- ✅ Computes `use_universal_cloner` based on field completeness
- ✅ `use_universal_cloner = False` when all fields present (Builders ENABLED)
- ✅ `use_universal_cloner = True` when fields missing (Cloner as PRIMARY)

## Test Coverage

### test_pipeline_route_and_execute.py
All 5 tests pass:
- ✅ `_have_all_fields` exists and treats mint/token_mint as synonyms
- ✅ `route_and_execute` exists and logs handoff
- ✅ `schedule_deep_analysis` exists and is non-blocking
- ✅ No early return in requires_full_analysis path
- ✅ `route_and_execute` called after "After infer_missing_fields" log

### demo_pipeline_flow.py
Demonstrates:
- ✅ Complete fields with `mint` → normalized to `token_mint`
- ✅ Incomplete fields → skips execution with warning
- ✅ `requires_full_analysis=True` → schedules analysis, continues to coordinator

## Why This Matters

As stated in the problem statement:
> "In this event you already have dex="meteora", action="swap", signer wallet_address, and token_mint (inferred via balances) before that early-return point. If you don't return early, execution will fire."

The implementation ensures:
1. Fields are inferred and validated
2. Deep analysis is scheduled non-blocking (doesn't halt execution)
3. If fields are ready, execution proceeds immediately
4. Clear logging shows the decision-making process

## Example Scenario

Given a trade with:
- `dex="meteora"`
- `action="swap"`
- `wallet_address="9ePNTG4j5eDG..."`
- `token_mint` (inferred via balances)
- `requires_full_analysis=True`

**Old behavior:** Would return early, never executing
**New behavior:** 
1. Schedules deep analysis (non-blocking)
2. Checks fields with `_have_all_fields()`
3. Sets mode: Builders ENABLED (complete fields)
4. Calls `route_and_execute()` → executes the trade
5. Logs handoff and return

This ensures trades fire when fields are ready, even if deep analysis is flagged.
