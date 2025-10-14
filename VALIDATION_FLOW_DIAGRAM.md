# Validation Flow Diagram

## New Relaxed Validation Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                    validate_trade_info()                        │
│                                                                 │
│  Input: trade (dict)                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Extract Fields:                                                │
│  • token_mint = trade.get("token_mint") or trade.get("mint")   │
│  • has_sig = bool(trade.get("signature"))                      │
│  • has_any_data = has_sig or logs or transaction               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ has_any_data?   │
                    └─────────────────┘
                         NO │   │ YES
               ┌────────────┘   └────────────┐
               ▼                              ▼
    ┌─────────────────────┐      ┌─────────────────────────┐
    │ 🛑 REJECT           │      │ Continue Validation     │
    │ "Insufficient data" │      │                         │
    └─────────────────────┘      └─────────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │ token_mint in                │
                              │ (None, "", "PENDING_ANALYSIS"│
                              │  "UNKNOWN")?                 │
                              └───────────────────────────────┘
                                  YES │       │ NO
                         ┌────────────┘       └──────────────┐
                         ▼                                    ▼
            ┌─────────────────────┐              ┌─────────────────────┐
            │   has_sig?          │              │ Continue with       │
            └─────────────────────┘              │ existing validation │
               YES │      │ NO                   │ logic (lines 491+)  │
        ┌──────────┘      └──────────┐           └─────────────────────┘
        ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│ ✅ ALLOW             │    │ 🛑 REJECT            │
│ Set defaults:        │    │ "Mint unresolved and │
│ • route_hint =       │    │  no signature"       │
│   "direct_copy"      │    └──────────────────────┘
│ • dex = "unknown"    │
│ • action = "swap"    │
│ Log: "Allowing via   │
│  direct_copy"        │
└──────────────────────┘
```

## Decision Matrix

| Mint Status          | Signature | Logs/TX | Result                    | Reason                          |
|---------------------|-----------|---------|---------------------------|---------------------------------|
| PENDING_ANALYSIS    | ✅ Yes    | Any     | ✅ **ALLOW (direct_copy)** | Can copy tx directly           |
| PENDING_ANALYSIS    | ❌ No     | ✅ Yes  | 🛑 **REJECT**             | Can't resolve mint, no sig     |
| PENDING_ANALYSIS    | ❌ No     | ❌ No   | 🛑 **REJECT**             | No data available              |
| UNKNOWN             | ✅ Yes    | Any     | ✅ **ALLOW (direct_copy)** | Can copy tx directly           |
| UNKNOWN             | ❌ No     | ✅ Yes  | 🛑 **REJECT**             | Can't resolve mint, no sig     |
| UNKNOWN             | ❌ No     | ❌ No   | 🛑 **REJECT**             | No data available              |
| None/Empty          | ✅ Yes    | Any     | ✅ **ALLOW (direct_copy)** | Can copy tx directly           |
| None/Empty          | ❌ No     | Any     | 🛑 **REJECT**             | No mint, no sig                |
| Valid Mint          | ✅ Yes    | Any     | ✅ **ALLOW**              | Signature validation pass      |
| Valid Mint          | ❌ No     | ✅ Yes  | ✅ **ALLOW** (if valid)   | Existing validation logic      |
| Valid Mint          | ❌ No     | ❌ No   | 🛑 **REJECT**             | No data available              |

## Key Changes from Previous Implementation

### Before
```python
# Rejected all trades with PENDING_ANALYSIS mint
if mint and mint not in {"UNKNOWN", "PENDING_ANALYSIS"}:
    ✅ approved
else:
    ❌ rejected
```

### After
```python
# Allow direct_copy when signature exists, even with unknown mint
if token_mint in ("PENDING_ANALYSIS", "UNKNOWN", None, ""):
    if has_sig:
        ✅ ALLOW via direct_copy  # NEW!
    else:
        ❌ REJECT
else:
    # Continue with existing validation
```

## Log Output Examples

### Example 1: Success (Signature + Unknown Mint)
```
[VALIDATION] 🔍 Starting trade validation...
✅ [VALIDATION] Allowing execution via direct_copy (mint unresolved but signature present)
```

### Example 2: Rejection (No Signature + Unknown Mint)
```
[VALIDATION] 🔍 Starting trade validation...
🛑 [VALIDATION] Mint unresolved and no signature — skipping
```

### Example 3: Rejection (No Data)
```
[VALIDATION] 🔍 Starting trade validation...
🛑 [VALIDATION] Insufficient data (no signature/logs/tx) — skipping
```

## Trade Flow Impact

```
Before:
  Trade with PENDING_ANALYSIS mint → ❌ REJECTED (even with signature)
  Result: Missed execution opportunities

After:
  Trade with PENDING_ANALYSIS mint + signature → ✅ ALLOWED via direct_copy
  Result: More trades executed, better coverage
```
