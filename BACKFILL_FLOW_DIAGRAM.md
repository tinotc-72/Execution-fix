# Backfill Functionality - Flow Diagrams

## Flow 1: Account Notification with Backfill

```
┌─────────────────────────────────────────────────────────────────┐
│                    WebSocket Connection                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│        accountNotification Received (no signature)               │
│        ⚡ Account change detected                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│            Check: trade_info.get("signature")?                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (No signature)
┌─────────────────────────────────────────────────────────────────┐
│         🔍 [BACKFILL] Attempting backfill...                     │
│         Call: backfill_latest_tx(rpc_url, wallet)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         RPC Call 1: getSignaturesForAddress(wallet)              │
│         Returns: [{"signature": "abc123...", ...}]               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         RPC Call 2: getTransaction(signature)                    │
│         Encoding: jsonParsed                                     │
│         Returns: {transaction, meta, logs}                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Backfill Returns:                                        │
│         {                                                        │
│           "signature": "abc123...",                              │
│           "logs": [...],                                         │
│           "transaction": {...},                                  │
│           "meta": {...}                                          │
│         }                                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Attach to trade_info:                                    │
│         trade_info["signature"] = backfill["signature"]          │
│         trade_info["logs"] = backfill["logs"]                    │
│         trade_info["transaction"] = backfill["transaction"]      │
│         trade_info["meta"] = backfill["meta"]                    │
│         🔁 [BACKFILL] Attached signature/logs/tx                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Call trade_callback(trade_info)                          │
│         Trade info now COMPLETE! ✅                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flow 2: Logs Notification with Backfill + Optimization

```
┌─────────────────────────────────────────────────────────────────┐
│                    WebSocket Connection                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│        logsNotification Received                                 │
│        Has logs: YES                                             │
│        Has signature: NO                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         backfill_data = None  (Initialize tracker)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Check: if not signature and logs                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (True)
┌─────────────────────────────────────────────────────────────────┐
│         🔍 [BACKFILL] Logs event without signature               │
│         Call: backfill_latest_tx(rpc_url, wallet)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         RPC Call 1: getSignaturesForAddress(wallet)              │
│         RPC Call 2: getTransaction(signature)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Store result in backfill_data:                           │
│         {signature, logs, transaction, meta}                     │
│         🔁 [BACKFILL] Retrieved signature: abc123...             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Update from backfill:                                    │
│         signature = backfill_data["signature"]                   │
│         logs = backfill_data["logs"] (if better)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Check if looks_like_trade(logs)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Yes, it's a trade)
┌─────────────────────────────────────────────────────────────────┐
│         🎯 Trade detected: abc123...                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Check: if backfill_data exists?                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Yes! Optimization kicks in)
┌─────────────────────────────────────────────────────────────────┐
│         ⚡ OPTIMIZATION: Reuse backfill data                     │
│         meta = backfill_data["meta"]                             │
│         transaction = backfill_data["transaction"]               │
│         🔁 [BACKFILL] Reusing backfilled transaction/meta        │
│         ❌ SKIP redundant RPC call!                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Create trade_info with COMPLETE data:                    │
│         {                                                        │
│           signature: from backfill ✅                            │
│           logs: from backfill ✅                                 │
│           transaction: from backfill ✅                          │
│           meta: from backfill ✅                                 │
│         }                                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Call trade_callback(trade_info)                          │
│         ALL data available, NO extra RPC calls! 🚀               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│         Call: backfill_latest_tx(rpc_url, wallet)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Try: getSignaturesForAddress                             │
└─────────────────────────────────────────────────────────────────┘
                    │                         │
                    ▼ Success                ▼ No results
        ┌──────────────────┐    ┌──────────────────────────────┐
        │ sigs = [...]     │    │ 🧵 [BACKFILL] No signatures  │
        │ sig = sigs[0]    │    │ Return None                  │
        └──────────────────┘    └──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│         Try: getTransaction(signature)                           │
└─────────────────────────────────────────────────────────────────┘
                    │                         │
                    ▼ Success                ▼ No result
        ┌──────────────────┐    ┌──────────────────────────────┐
        │ tx = {...}       │    │ 🧵 [BACKFILL] No transaction │
        │ Return {data}    │    │ Return None                  │
        └──────────────────┘    └──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│         ✅ SUCCESS                                               │
│         Return: {signature, logs, transaction, meta}             │
└─────────────────────────────────────────────────────────────────┘

Exception at any point:
┌─────────────────────────────────────────────────────────────────┐
│         🧵 [BACKFILL] Failed to backfill latest tx: {error}      │
│         Return None                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Comparison: Before vs After

### BEFORE (No Backfill)
```
WebSocket Event (no signature)
        │
        ▼
   Return early ❌
        │
        ▼
   Lost trade event 😢
```

### AFTER (With Backfill)
```
WebSocket Event (no signature)
        │
        ▼
   🔍 Attempt backfill
        │
        ▼
   RPC: getSignaturesForAddress
        │
        ▼
   RPC: getTransaction
        │
        ▼
   🔁 Signature retrieved!
        │
        ▼
   Process trade event ✅
        │
        ▼
   Happy trading! 🎉
```

---

## Key Benefits Visualized

```
┌──────────────────────────────────────────────────────────────────┐
│                         BENEFITS                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Complete Trade Data                                          │
│     ❌ Before: signature missing                                 │
│     ✅ After:  signature + logs + transaction + meta             │
│                                                                  │
│  2. No Lost Events                                               │
│     ❌ Before: exit early if no signature                        │
│     ✅ After:  backfill and process                              │
│                                                                  │
│  3. Optimized RPC Calls                                          │
│     ❌ Before: separate RPC call for each data piece             │
│     ✅ After:  reuse backfill data (1 call instead of 2)         │
│                                                                  │
│  4. Clear Visibility                                             │
│     ❌ Before: no logging for missing signatures                 │
│     ✅ After:  emoji-rich logs (🔍, 🔁, ⚠️, 🧵)                  │
│                                                                  │
│  5. Zero New Dependencies                                        │
│     ✅ Uses existing aiohttp library                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Summary

The backfill implementation provides a robust, efficient, and well-tested solution for handling WebSocket events that arrive without signature information. The flow diagrams above show how the implementation:

1. **Detects** missing signatures in WebSocket events
2. **Backfills** data via RPC calls (getSignaturesForAddress + getTransaction)
3. **Optimizes** by reusing backfill data to avoid redundant calls
4. **Handles** errors gracefully with clear logging
5. **Delivers** complete trade data to downstream processors

All while staying within existing patterns and adding zero new dependencies! 🎉
