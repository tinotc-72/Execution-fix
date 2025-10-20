# Try Backfill Implementation for websocket_account_change

## Overview

This implementation adds a `try_backfill` function to handle websocket_account_change events that arrive without a signature. The function attempts to fetch the latest transaction signature and full transaction data via RPC before proceeding with validation.

## Problem Statement

The pipeline was skipping account-change events that didn't have a signature, blocking the pipeline. This caused legitimate trades to be missed when they arrived via websocket_account_change notifications.

## Solution

### 1. try_backfill Function

Created an async function `try_backfill(trade_info: dict, rpc_client) -> bool` that:

- **Returns True immediately** if trade_info already has a signature
- **Fetches wallet address** from trade_info
- **Uses RPC to get latest signature** via `backfill_latest_tx` helper
- **Logs appropriate messages** for different scenarios:
  - "⏳ [BACKFILL] No recent signature — waiting for logs event" when no signature found
  - "⏳ [BACKFILL] getTransaction returned None — waiting for logs event" when transaction fetch fails
  - "✅ [BACKFILL] Successfully backfilled..." on success
- **Attaches data to trade_info** on success:
  - signature
  - transaction
  - meta
  - logs
- **Returns False on failure**, True on success

### 2. Pipeline Integration

Modified `_handle_websocket_trade` in main.py to:

1. **Check detection_method** for "websocket_account_change"
2. **Call try_backfill** before infer_missing_fields and validate_trade_info
3. **Handle backfill failure** by:
   - Logging "⏳ [BACKFILL] Backfill failed — waiting for subsequent websocket_logs event"
   - Logging "ℹ️ [PIPELINE] Not marking as skipped to allow logs event to proceed"
   - Returning early without marking as skipped
4. **Proceed to validation** only when backfill succeeds

## Key Implementation Details

### Flow for websocket_account_change Events

```
1. WebSocket receives account_change notification
2. Pipeline checks: detection_method == "websocket_account_change"
3. Call try_backfill(trade_info, rpc_client):
   a. If signature exists → return True
   b. If no wallet_address → return False
   c. Call backfill_latest_tx to fetch signature
   d. If no signature found → log and return False
   e. If getTransaction returns None → log and return False
   f. If successful → attach all data and return True
4. If backfill failed:
   - Log waiting for logs event
   - Return without marking as skipped
5. If backfill succeeded:
   - Proceed to infer_missing_fields
   - Proceed to validate_trade_info
   - Execute trade if valid
```

### Why This Works

1. **Non-blocking**: Account-change events that fail backfill don't block the pipeline
2. **Complementary**: Allows subsequent websocket_logs events to proceed normally
3. **Efficient**: Attempts backfill only for account-change events
4. **Robust**: Handles all edge cases with appropriate logging

## Testing

Created comprehensive test suite in `test_try_backfill.py` that validates:

1. ✅ try_backfill function signature and return type
2. ✅ Early return when signature already exists
3. ✅ Backfill logic with RPC calls
4. ✅ Logging messages for all scenarios
5. ✅ Data attachment on success
6. ✅ Pipeline detection method check
7. ✅ Backfill failure handling
8. ✅ Pipeline proceeds on success
9. ✅ Correct ordering (backfill before validation)

All tests pass: **9/9 checks passed**

## Files Modified

1. **main.py**:
   - Added `try_backfill` function (lines 300-364)
   - Modified `_handle_websocket_trade` to check detection_method and call try_backfill (lines 929-941)

2. **test_try_backfill.py** (new):
   - Comprehensive test suite for try_backfill implementation

## Backward Compatibility

- ✅ Existing websocket_logs events work unchanged
- ✅ Existing enhanced_transaction_stream events work unchanged
- ✅ Only adds special handling for websocket_account_change events
- ✅ No changes to RPC client or other core components
- ✅ Uses existing `backfill_latest_tx` helper from websocket_handler.py

## Benefits

1. **More trades captured**: Account-change events can now proceed if backfill succeeds
2. **No false skips**: Failed backfills don't mark events as skipped
3. **Better logging**: Clear messages for debugging backfill attempts
4. **Complementary events**: websocket_logs events can still proceed independently
5. **Robust error handling**: All edge cases are handled gracefully
