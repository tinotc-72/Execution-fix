# Sanity Check Logs - Visual Flow Diagram

## Overview
This diagram shows the complete log flow after "After infer_missing_fields", 
ensuring all sanity check logs always appear.

## Flow Diagram

### Entry Point: _handle_websocket_trade
```
┌─────────────────────────────────────────────────────────────┐
│  _handle_websocket_trade()                                  │
│  • Receives trade event from WebSocket                      │
│  • Parses and validates transaction                         │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  📝 Step 1: Infer Missing Fields                            │
│  trade_info = trade_processor.infer_missing_fields(...)     │
│  logger.debug("[DEBUG] After infer_missing_fields: {...}")  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  📝 Step 2: Compute Mode                                    │
│  have_all = _have_all_fields(trade_info)                    │
│  trade_info["use_universal_cloner"] = not have_all          │
│  logger.info("✅ [MODE] Builders %s; Cloner as %s")         │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  📝 Step 3: HANDOFF LOG (ALWAYS APPEARS)                    │
│  logger.info("📤 [HANDOFF] Calling coordinator now…")       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
                  route_and_execute()
                       ↓
          ┌────────────┴────────────┐
          │                         │
    Fields Complete            Fields Incomplete
          │                         │
          ↓                         ↓
┌──────────────────┐       ┌──────────────────────────┐
│ SUCCESS PATH     │       │ ERROR PATH               │
│                  │       │                          │
│ logger.info(     │       │ logger.warning(          │
│   "🧭 [PIPELINE_ │       │   "🛑 [PIPELINE_EXIT]    │
│   EXIT] Final    │       │   Fields incomplete,     │
│   fields ready → │       │   but attempting         │
│   handoff to     │       │   coordinator handoff    │
│   coordinator")  │       │   for logging")          │
└────────┬─────────┘       └────────┬─────────────────┘
         │                          │
         └────────────┬─────────────┘
                      ↓
              await maybe_execute()
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  📝 Step 4: COORDINATOR LOG (ALWAYS APPEARS)                │
│  logger.info("🧭 [COORDINATOR] route start: dex=%s, ...")   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
          ┌────────────┴────────────┐
          │                         │
    Token Mint Valid          Token Mint Invalid
          │                         │
          ↓                         ↓
┌──────────────────┐       ┌──────────────────────────┐
│ SUCCESS PATH     │       │ ERROR PATH               │
│                  │       │                          │
│ (Route based on  │       │ logger.error(            │
│  DEX type)       │       │   "❌ [COORDINATOR]       │
│                  │       │   Missing or invalid     │
│ if meteora:      │       │   token_mint...")        │
│   logger.info(   │       │                          │
│     "🧭 [ROUTE]  │       │ logger.info(             │
│     Meteora →    │       │   "🧭 [ROUTE] Skipped →  │
│     build_and_   │       │   missing token_mint")   │
│     sign")       │       │                          │
│                  │       │ logger.error(            │
│ Build & submit   │       │   "❌ [EXECUTION]        │
│   transaction    │       │   Failed: missing        │
│                  │       │   required fields")      │
│ logger.info(     │       │                          │
│   "✅ [EXECUTION]│       │ return None              │
│   submitted:     │       │                          │
│   {sig}")        │       │                          │
└──────────────────┘       └──────────────────────────┘
```

## Key Changes

### Before (Old Behavior)
```python
# route_and_execute()
if not _have_all_fields(trade_info):
    logger.warning("🛑 [PIPELINE_EXIT] Fields incomplete, skipping execution")
    return  # ❌ EARLY RETURN - Coordinator never called
    
logger.info("🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator")
await maybe_execute(...)
```

**Problem:** If fields incomplete, coordinator logs never appear!

### After (New Behavior)
```python
# route_and_execute()
if not _have_all_fields(trade_info):
    logger.warning("🛑 [PIPELINE_EXIT] Fields incomplete, but attempting coordinator handoff for logging")
else:
    logger.info("🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator")

# ✅ NO EARLY RETURN - Always call coordinator
await maybe_execute(...)
```

**Solution:** Coordinator always called, all logs always appear!

### Coordinator Error Handling
```python
# maybe_execute()
logger.info("🧭 [COORDINATOR] route start: dex=%s, prefer_clone=%s", dex, prefer_clone)

# ✅ Check fields and log errors if incomplete
token_mint = trade_info.get("token_mint")
if not token_mint or token_mint in ("UNKNOWN", "PENDING_ANALYSIS", "unknown", ""):
    logger.error("❌ [COORDINATOR] Missing or invalid token_mint, cannot execute")
    logger.info("🧭 [ROUTE] Skipped → missing token_mint")
    logger.error("❌ [EXECUTION] Failed: missing required fields")
    return None
```

## Guaranteed Log Sequence

### Success Path
```
1. [DEBUG] After infer_missing_fields: {...}
2. [INFO]  ✅ [MODE] Builders ENABLED (complete fields); Cloner as fallback
3. [INFO]  📤 [HANDOFF] Calling coordinator now…
4. [INFO]  🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator
5. [INFO]  🧭 [COORDINATOR] route start: dex=meteora, prefer_clone=False
6. [INFO]  🧭 [ROUTE] Meteora → build_and_sign
7. [INFO]  ✅ [EXECUTION] submitted: 5abc123def456...
8. [INFO]  📥 [HANDOFF] Coordinator call returned
```

### Error Path
```
1. [DEBUG] After infer_missing_fields: {...}
2. [INFO]  ✅ [MODE] Builders DISABLED; Cloner as PRIMARY
3. [INFO]  📤 [HANDOFF] Calling coordinator now…
4. [WARN]  🛑 [PIPELINE_EXIT] Fields incomplete, but attempting coordinator handoff for logging
5. [INFO]  🧭 [COORDINATOR] route start: dex=meteora, prefer_clone=True
6. [ERROR] ❌ [COORDINATOR] Missing or invalid token_mint, cannot execute
7. [INFO]  🧭 [ROUTE] Skipped → missing token_mint
8. [ERROR] ❌ [EXECUTION] Failed: missing required fields
9. [INFO]  📥 [HANDOFF] Coordinator call returned
```

## Benefits

✅ **All logs always appear** - No early returns prevent logging  
✅ **Clear error messages** - Error variants explain what went wrong  
✅ **Complete audit trail** - Easy to trace execution flow  
✅ **Better debugging** - Can see exactly where and why execution failed

## Validation

Run these tests to verify:
```bash
python test_sanity_check_logs.py           # Unit tests
python test_sanity_check_integration.py    # Integration tests  
python demo_sanity_check_logs.py           # Interactive demo
```

All tests should pass with confirmation that log sequence appears correctly!
