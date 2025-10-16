# Pipeline Exit Handoff - Flow Diagram

## Complete Flow After infer_missing_fields()

```
┌─────────────────────────────────────────────────────────────────┐
│                     WebSocket Trade Event                        │
│              (with rich postTokenBalances data)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: infer_missing_fields()                      │
│  ─────────────────────────────────────────────────────────      │
│  • Extract mint from postTokenBalances                           │
│  • Infer wallet_address from transaction                         │
│  • Detect DEX from program IDs                                   │
│  • Parse action from logs                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: _have_all_fields(trade_info)                │
│  ─────────────────────────────────────────────────────────      │
│  Helper function checks:                                         │
│  • dex not in (None, "", "unknown", "PENDING_ANALYSIS")          │
│  • action not in (None, "", "unknown", "PENDING_ANALYSIS")       │
│  • wallet_address not in (None, "", "unknown", "PENDING_...")    │
│  • token_mint OR mint is truthy                                  │
│                                                                   │
│  Returns: have_all = True/False                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           STEP 3: Normalize and Set Flags                        │
│  ─────────────────────────────────────────────────────────      │
│  trade_info["token_mint"] = token_mint or mint                   │
│  trade_info["use_universal_cloner"] = not have_all               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │   have_all?     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
         ┌────────┐                    ┌────────┐
         │  YES   │                    │   NO   │
         └────┬───┘                    └────┬───┘
              │                             │
              ▼                             ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│  Log Success            │    │  Log Warning                 │
│  ───────────            │    │  ───────────                 │
│  "🧭 [PIPELINE_EXIT]    │    │  "🛑 [PIPELINE_EXIT]         │
│   Final fields ready    │    │   Incomplete fields"         │
│   → coordinator"        │    │                              │
└───────────┬─────────────┘    └──────────────┬───────────────┘
            │                                  │
            ▼                                  │
┌─────────────────────────┐                   │
│  Extract RPC URL        │                   │
│  ───────────            │                   │
│  rpc_url = ...          │                   │
└───────────┬─────────────┘                   │
            │                                  │
            ▼                                  │
┌─────────────────────────┐                   │
│  Call Coordinator       │                   │
│  ───────────            │                   │
│  await maybe_execute(   │                   │
│    trade_info,          │                   │
│    rpc_url,             │                   │
│    wallet,              │                   │
│    jito_service         │                   │
│  )                      │                   │
└───────────┬─────────────┘                   │
            │                                  │
            │                                  │
            └──────────────┬───────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Continue Pipeline    │
              │   ─────────────────    │
              │   Validation & Process │
              └────────────────────────┘
```

## Key Decision Points

### 1. **have_all = True** (All Fields Present)
- `use_universal_cloner` = **False** ✅
- **Enables builder execution paths** (Meteora, Jupiter)
- Direct `maybe_execute` call to coordinator
- Logging: "🧭 [PIPELINE_EXIT] Final fields ready → coordinator"

### 2. **have_all = False** (Incomplete Fields)
- `use_universal_cloner` = **True** 🔄
- **Fallback to cloner mode**
- Continues to validation (may be rejected later)
- Logging: "🛑 [PIPELINE_EXIT] Incomplete fields"

## Coordinator Validation

After `maybe_execute` is called, the coordinator performs final validation:

```python
token_mint = trade_info.get("token_mint")
if not token_mint or token_mint in ("UNKNOWN", "PENDING_ANALYSIS", "unknown", ""):
    logger.error("❌ [COORDINATOR] Missing or invalid token_mint, cannot execute")
    return None
```

This two-stage validation ensures:
1. **Pipeline stage**: Fast check using `_have_all_fields` 
2. **Coordinator stage**: Strict validation before execution

## Example Scenarios

### Scenario 1: Complete Trade (Success Path)
```
Input:
  dex: "jupiter"
  action: "buy"
  wallet_address: "suqh5s..."
  token_mint: "EPjFWd..."

Flow:
  ✅ have_all = True
  ✅ use_universal_cloner = False
  ✅ Log: "🧭 [PIPELINE_EXIT] Final fields ready → coordinator"
  ✅ Call: await maybe_execute(...)
  ✅ Coordinator: Executes with builder (Jupiter)
```

### Scenario 2: Incomplete Trade (Fallback Path)
```
Input:
  dex: "unknown"
  action: "buy"
  wallet_address: "suqh5s..."
  token_mint: "EPjFWd..."

Flow:
  ❌ have_all = False (dex = "unknown")
  ✅ use_universal_cloner = True
  ⚠️  Log: "🛑 [PIPELINE_EXIT] Incomplete fields"
  ❌ Validation fails later in pipeline
```

### Scenario 3: Using 'mint' Field (Normalization)
```
Input:
  dex: "raydium"
  action: "sell"
  wallet_address: "suqh5s..."
  mint: "So1111..." (not token_mint)

Flow:
  ✅ have_all = True (finds mint)
  ✅ token_mint = "So1111..." (normalized)
  ✅ use_universal_cloner = False
  ✅ Log: "🧭 [PIPELINE_EXIT] Final fields ready → coordinator"
  ✅ Call: await maybe_execute(...)
```

## Benefits

### 🎯 Optimized Execution Path
- Builder execution (Meteora/Jupiter) when fields complete
- Cloner fallback only when necessary
- Clear decision flow with logging

### 🎯 Field Validation
- Two-stage validation (pipeline + coordinator)
- Accepts both `mint` and `token_mint`
- Proper normalization for consistency

### 🎯 Rich Data Utilization
- Leverages `postTokenBalances` for mint inference
- Transaction parsing for action/dex detection
- Maximizes execution success rate
