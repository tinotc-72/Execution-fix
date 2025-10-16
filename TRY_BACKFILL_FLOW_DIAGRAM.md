# Try Backfill Flow Diagram

## Visual Flow for websocket_account_change Events

```
┌─────────────────────────────────────────────────────────────────┐
│              WebSocket Account Change Notification              │
│                                                                 │
│  • detection_method: "websocket_account_change"                │
│  • May or may not have signature                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline Entry (_handle_websocket_trade)      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         Check: detection_method == "websocket_account_change"   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                             YES
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Call: try_backfill(trade_info, rpc_client)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                ┌─────────────┴─────────────┐
                ↓                           ↓
         ┌─────────────┐            ┌─────────────┐
         │  Signature  │            │    No       │
         │  Already    │            │  Signature  │
         │  Exists?    │            │             │
         └─────────────┘            └─────────────┘
                ↓                           ↓
         ┌─────────────┐            ┌─────────────────────────────────┐
         │  Return     │            │  Get wallet_address             │
         │  True       │            │  Call backfill_latest_tx        │
         └─────────────┘            └─────────────────────────────────┘
                                                   ↓
                                    ┌──────────────┴──────────────┐
                                    ↓                             ↓
                            ┌─────────────┐              ┌─────────────────┐
                            │  Signature  │              │  No Signature   │
                            │  Found      │              │  Found          │
                            └─────────────┘              └─────────────────┘
                                    ↓                             ↓
                            ┌─────────────┐              ┌─────────────────┐
                            │  Get Tx     │              │  Log: "No recent│
                            │  via RPC    │              │  signature —    │
                            └─────────────┘              │  waiting for    │
                                    ↓                    │  logs event"    │
                            ┌──────────────┐             │  Return False   │
                            ↓              ↓             └─────────────────┘
                    ┌─────────────┐  ┌─────────────┐
                    │  Tx Data    │  │  Tx is None │
                    │  Available  │  │             │
                    └─────────────┘  └─────────────┘
                            ↓              ↓
                    ┌─────────────┐  ┌─────────────────┐
                    │  Attach:    │  │  Log: "getTx    │
                    │  - signature│  │  returned None  │
                    │  - tx       │  │  — waiting for  │
                    │  - meta     │  │  logs event"    │
                    │  - logs     │  │  Return False   │
                    │  Return True│  └─────────────────┘
                    └─────────────┘
                            ↓
                ┌───────────────────────────────┐
                │    Backfill Success?          │
                └───────────────────────────────┘
                            ↓
                ┌───────────┴───────────┐
                ↓                       ↓
         ┌─────────────┐         ┌─────────────────────────┐
         │  SUCCESS    │         │  FAILURE                │
         │             │         │                         │
         │  Log:       │         │  Log:                   │
         │  "✅ Backfill│         │  "⏳ Backfill failed —  │
         │  succeeded" │         │  waiting for logs event"│
         │             │         │                         │
         │  Proceed to:│         │  Log:                   │
         │  1. infer_  │         │  "ℹ️ Not marking as     │
         │     missing_│         │  skipped"               │
         │     fields  │         │                         │
         │  2. validate│         │  RETURN (early exit)    │
         │     _trade_ │         │                         │
         │     info    │         │  → Allow logs event     │
         └─────────────┘         │    to proceed           │
                ↓                └─────────────────────────┘
         ┌─────────────┐
         │  Execute    │
         │  Trade      │
         │  (if valid) │
         └─────────────┘
```

## Key Benefits

1. **Non-blocking**: Failed backfills don't mark events as skipped
2. **Complementary**: websocket_logs events can still proceed independently
3. **Efficient**: Only attempts backfill for account-change events
4. **Robust**: Handles all edge cases with appropriate logging

## Logging Markers

- 🔍 `[BACKFILL]` - Backfill attempt initiated
- ⏳ `[BACKFILL]` - Backfill waiting/failed (not critical, logs event will follow)
- ✅ `[BACKFILL]` - Backfill succeeded
- ℹ️ `[PIPELINE]` - Pipeline decision/status

## Edge Cases Handled

1. **Signature already exists**: Returns True immediately (no RPC call needed)
2. **No wallet address**: Returns False, logs warning
3. **RPC returns no signatures**: Logs and returns False (waits for logs event)
4. **getTransaction returns None**: Logs specific message and returns False
5. **Exception during backfill**: Catches and logs, returns False
6. **Successful backfill**: Attaches all data and returns True
