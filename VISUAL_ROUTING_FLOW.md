# Routing Logic Enhancement - Visual Flow Diagram

## 🎯 Problem Statement Goals

Prevent execution of "doomed" transactions that are likely to fail by:
1. Trying builders (with fresh quotes) before cloning failed transactions
2. Supporting slippage retry with wider tolerance
3. Intelligent routing based on DEX type and transaction state

---

## 📊 Routing Flow Diagrams

### Flow 1: Meteora Path
```
┌─────────────────────────────────────────────────────┐
│ Trade Info: dex_key = "meteora"                     │
│             retry_hint = "requote" (optional)       │
└─────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  Route: ["meteora", "jupiter", │
         │          "direct_copy"]        │
         └────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  1️⃣  Try Meteora Builder       │
         │      force_requote = (retry    │
         │      hint == "requote")        │
         │                                │
         │      If requote:               │
         │      - min_tokens=0            │
         │      - Max slippage tolerance  │
         └────────────────────────────────┘
                          ↓
                   ┌─────────┐
                   │ Success?│
                   └─────────┘
                   ↙         ↘
              ✅ YES          ❌ NO
                ↓              ↓
            Return      ┌──────────────────┐
            signature   │ 2️⃣  Try Jupiter   │
                        │     Builder       │
                        └──────────────────┘
                                ↓
                          ┌─────────┐
                          │ Success?│
                          └─────────┘
                          ↙         ↘
                     ✅ YES          ❌ NO
                       ↓              ↓
                   Return      ┌──────────────────┐
                   signature   │ 3️⃣  Try direct_  │
                               │     copy (clone) │
                               └──────────────────┘
                                       ↓
                                  Return result
```

### Flow 2: Unknown DEX + Token Mint Present
```
┌─────────────────────────────────────────────────────┐
│ Trade Info: dex_key = "unknown"                     │
│             have_mint = True                        │
└─────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  Route: ["jupiter", "meteora", │
         │          "direct_copy"]        │
         └────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  1️⃣  Try Jupiter Builder       │
         │      (Widest DEX coverage)     │
         └────────────────────────────────┘
                          ↓
                   ┌─────────┐
                   │ Success?│
                   └─────────┘
                   ↙         ↘
              ✅ YES          ❌ NO
                ↓              ↓
            Return      ┌──────────────────┐
            signature   │ 2️⃣  Try Meteora   │
                        │     Builder       │
                        └──────────────────┘
                                ↓
                          ┌─────────┐
                          │ Success?│
                          └─────────┘
                          ↙         ↘
                     ✅ YES          ❌ NO
                       ↓              ↓
                   Return      ┌──────────────────┐
                   signature   │ 3️⃣  Try direct_  │
                               │     copy (clone) │
                               └──────────────────┘
                                       ↓
                                  Return result
```

### Flow 3: Source Transaction Failed
```
┌─────────────────────────────────────────────────────┐
│ Trade Info: source_tx_failed = True                 │
│             (e.g., error 6004 - slippage exceeded)  │
└─────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  ⚠️  WARNING: Source TX Failed │
         │                                │
         │  NEVER clone first!            │
         │  Cloning will fail again       │
         └────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  Route: ["jupiter", "meteora", │
         │          "direct_copy"]        │
         │                                │
         │  Builders use FRESH quotes     │
         └────────────────────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │  1️⃣  Try Jupiter Builder       │
         │      - Fresh quote             │
         │      - Current price           │
         │      - May succeed where       │
         │        clone would fail        │
         └────────────────────────────────┘
                          ↓
                   ┌─────────┐
                   │ Success?│
                   └─────────┘
                   ↙         ↘
              ✅ YES          ❌ NO
                ↓              ↓
            Return      ┌──────────────────┐
            signature   │ 2️⃣  Try Meteora   │
                        │     Builder       │
                        └──────────────────┘
                                ↓
                          ┌─────────┐
                          │ Success?│
                          └─────────┘
                          ↙         ↘
                     ✅ YES          ❌ NO
                       ↓              ↓
                   Return      ┌──────────────────────┐
                   signature   │ 3️⃣  Try direct_copy  │
                               │     (LAST RESORT)    │
                               │                      │
                               │  Still may fail with │
                               │  same error as source│
                               └──────────────────────┘
                                       ↓
                                  Return result
```

---

## 🔧 Force Requote Implementation

### Normal Trade (min_tokens=1)
```
┌─────────────────────────────────────────┐
│ Meteora Trade (Normal)                  │
│ retry_hint: None                        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Build Transaction:                      │
│   min_tokens = 1                        │
│   Tight slippage tolerance              │
└─────────────────────────────────────────┘
                  ↓
        Execute & Submit
```

### Requote Trade (min_tokens=0)
```
┌─────────────────────────────────────────┐
│ Meteora Trade (Retry)                   │
│ retry_hint: "requote"                   │
│ source_tx_failed: True                  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ ⚡ FORCE REQUOTE DETECTED               │
│                                         │
│ Build Transaction:                      │
│   min_tokens = 0                        │
│   MAXIMUM slippage tolerance            │
│   Allow trade even with high volatility │
└─────────────────────────────────────────┘
                  ↓
        Execute & Submit
```

---

## 📈 Comparison: Old vs New Behavior

### Scenario: Meteora Trade Fails

#### Old Behavior ❌
```
Meteora executor fails
        ↓
Immediate fallback to direct_copy
        ↓
Clone transaction
        ↓
Submit
```

**Problem**: Misses opportunity to try Jupiter builder

#### New Behavior ✅
```
Meteora executor fails
        ↓
Continue to next in routing plan
        ↓
Try Jupiter builder
        ↓
If Jupiter fails → Try direct_copy
```

**Benefit**: More chances to succeed with fresh quotes

---

## 🎯 Key Decision Points

### 1. Check DEX Type
```
if dex_key == "meteora":
    → Meteora path
elif dex_key == "unknown" and have_mint:
    → Unknown+mint path
elif source_tx_failed:
    → Source failed path
else:
    → Default ROUTE_MAP
```

### 2. Check Retry Hint
```
if retry_hint == "requote":
    force_requote = True
    → Use min_tokens=0 for max slippage
else:
    force_requote = False
    → Use min_tokens=1 for tight slippage
```

### 3. Execute Routing Plan
```
for executor in plan:
    result = try_executor()
    if success:
        return result
    else:
        continue to next
```

---

## 🚀 Benefits Summary

| Feature | Old | New | Benefit |
|---------|-----|-----|---------|
| Meteora routing | Immediate fallback | Try Jupiter first | More success chances |
| Unknown + mint | Clone first | Builders first | Fresh quotes |
| Source failed | May clone failed tx | Builders first | Avoid repeating failures |
| Slippage retry | No support | force_requote flag | Handle volatility |
| Dependencies | Existing | Existing | No new deps |

---

## ✅ Validation

All requirements met:
- ✅ Meteora: Meteora → Jupiter → direct_copy
- ✅ Unknown+mint: Jupiter → Meteora → direct_copy
- ✅ Source failed: Builders first, avoid doomed clone
- ✅ Force requote: Wider slippage (min_tokens=0)
- ✅ No new dependencies
- ✅ Tests: 5/5 passing
- ✅ Documentation: Complete
- ✅ Demo: Interactive examples
