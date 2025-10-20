# Reliable RPC Submitter - Visual Flow

## Transaction Submission Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Executor Calls send_and_confirm                  │
│                         (e.g., FastExecutor, Jupiter)                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Is Jito Enabled?     │
                    └─────────┬──────────────┘
                              │
                 ┌────────────┴────────────┐
                 │ YES                     │ NO
                 ▼                         ▼
    ┌────────────────────────┐   ┌────────────────────────┐
    │ Try Jito Submission    │   │ Use RPC Directly       │
    │ (send_transaction)     │   │ (send_and_confirm_v0)  │
    └─────────┬──────────────┘   └────────┬───────────────┘
              │                           │
              ▼                           │
    ┌────────────────────────┐           │
    │   Jito Success?        │           │
    └─────────┬──────────────┘           │
              │                           │
   ┌──────────┴──────────┐              │
   │ YES                 │ NO            │
   ▼                     ▼               │
┌──────────────┐  ┌─────────────────────┴───┐
│ Confirm TX   │  │ Fallback to RPC         │
│ Return {     │  │ send_and_confirm_v0_tx  │
│   success:   │  └──────────┬──────────────┘
│     True,    │             │
│   signature, │◄────────────┘
│   status,    │
│   path: jito │
│ }            │
└──────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           Return Structured Result            │
│  {                                           │
│    "success": true/false,                   │
│    "signature": "5j7s...",  // Real sig!   │
│    "status": {...},          // Real status!│
│    "error": "..."  // Only on failure       │
│  }                                          │
└──────────────────────────────────────────────┘
```

## send_and_confirm_v0_tx Internal Flow

```
┌─────────────────────────────────────────────────────────────┐
│         send_and_confirm_v0_tx(vtx, rpc_url)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  Step 1: Submit to RPC   │
        │  - POST sendTransaction  │
        │  - Encode as base64      │
        │  - Skip preflight        │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  Extract Signature       │
        │  from result field       │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  Step 2: Poll Confirm    │
        │  For attempt in retries: │
        │    - getSignatureStatuses│
        │    - Check status        │
        │    - Wait retry_delay    │
        └──────────┬───────────────┘
                   │
        ┌──────────┴──────────┐
        │ Confirmed?          │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │ YES                 │ NO (timeout)
        ▼                     ▼
┌────────────────┐   ┌────────────────┐
│ Return:        │   │ Return:        │
│ {              │   │ {              │
│   success:True,│   │   success:False│
│   signature,   │   │   signature,   │
│   status: {...}│   │   error: msg   │
│ }              │   │ }              │
└────────────────┘   └────────────────┘
```

## Executor Integration Patterns

### Pattern 1: Using FastExecutor (Recommended)
```python
# In executor code
result = await self.fast_executor.send_and_confirm(vtx)

if result and result.get("success"):
    signature = result["signature"]
    status = result["status"]
    path = result.get("path")  # "jito" or "rpc"
    logger.info(f"Success via {path}: {signature}")
    return exec_ok("executor_name", signature)
else:
    error = result.get("error") if result else "submission failed"
    logger.error(f"Failed: {error}")
    return exec_err("executor_name", error)
```

### Pattern 2: Direct Usage
```python
# Direct usage of send_and_confirm_v0_tx
from executors.submit import send_and_confirm_v0_tx

result = await send_and_confirm_v0_tx(vtx, RPC_URL)

if result.get("success"):
    signature = result["signature"]
    return signature
else:
    logger.error(f"Submission failed: {result.get('error')}")
    return None
```

### Pattern 3: With Jito Retry Logic
```python
# In Jupiter executor
for attempt in range(max_retries):
    # Try Jito first
    if jito_is_configured(self.jito_service):
        jito_result = await self.jito_service.send_transaction(bytes(tx))
        sig = jito_result.get("result")
        if sig:
            return sig
    
    # RPC fallback using shared submitter
    result = await send_and_confirm_v0_tx(tx, RPC_URL)
    if result.get("success"):
        return result["signature"]
    
    # Retry
    await asyncio.sleep(delay)

return None
```

## Error Handling Flow

```
┌────────────────────────────────────────────────┐
│           Transaction Submission               │
└─────────────────┬──────────────────────────────┘
                  │
                  ▼
     ┌────────────────────────┐
     │   Jito Available?      │
     └────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    │ YES               │ NO
    ▼                   │
┌───────────────┐       │
│ Try Jito      │       │
└───────┬───────┘       │
        │               │
        ▼               │
┌───────────────┐       │
│ Jito Error?   │       │
└───────┬───────┘       │
        │               │
    ┌───┴───┐          │
    │ YES   │ NO       │
    ▼       │          │
    │       ▼          │
    │   ┌──────────┐   │
    │   │ Success! │   │
    │   │ Return   │   │
    │   │ Result   │   │
    │   └──────────┘   │
    │                  │
    └──────────┬───────┘
               │
               ▼
    ┌──────────────────────┐
    │ RPC Fallback         │
    │ send_and_confirm_v0  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   RPC Error?         │
    └──────────┬───────────┘
               │
        ┌──────┴──────┐
        │ YES         │ NO
        ▼             ▼
┌───────────────┐ ┌──────────┐
│ Return Error  │ │ Success! │
│ {success:     │ │ Return   │
│  false,       │ │ Result   │
│  error:msg}   │ │          │
└───────────────┘ └──────────┘
```

## Logging Timeline Example

### Successful Jito Path
```
[10:30:45.123] [SUBMIT_JITO] region=https://london.mainnet.block-engine.jito.wtf sig=5j7s6K3...
[10:30:45.678] [CONFIRM] attempt=1/5 sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None}
[10:30:45.680] [CONFIRM][FINAL] sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None} path=jito
[10:30:45.681] [EXECUTOR] Transaction confirmed via Jito: 5j7s6K3...
```

### Jito Failure with RPC Fallback
```
[10:30:45.123] [SUBMIT_JITO] error: Connection timeout
[10:30:45.124] [EXECUTOR] Jito submission failed, falling back to RPC
[10:30:45.500] [SUBMIT_RPC] Transaction submitted successfully: 5j7s6K3...
[10:30:46.100] [CONFIRM] attempt=1/5 sig=5j7s6K3... status={'confirmationStatus': 'processed', 'err': None}
[10:30:46.900] [CONFIRM] attempt=2/5 sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None}
[10:30:46.902] [CONFIRM][FINAL] sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None}
[10:30:46.903] [EXECUTOR] RPC submission succeeded: 5j7s6K3...
```

### RPC Only (Jito Disabled)
```
[10:30:45.123] [SUBMIT_RPC] Transaction submitted successfully: 5j7s6K3...
[10:30:45.900] [CONFIRM] attempt=1/5 sig=5j7s6K3... status={'confirmationStatus': 'processed', 'err': None}
[10:30:46.700] [CONFIRM] attempt=2/5 sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None}
[10:30:46.702] [CONFIRM][FINAL] sig=5j7s6K3... status={'confirmationStatus': 'confirmed', 'err': None}
[10:30:46.703] [EXECUTOR] Transaction confirmed: 5j7s6K3...
```

## Benefits Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Before Implementation                         │
├─────────────────────────────────────────────────────────────────┤
│ ❌ Each executor had its own submission logic                   │
│ ❌ Inconsistent error handling                                  │
│ ❌ Some returned None, some returned signatures                 │
│ ❌ Placeholders in logs (simulation_signature)                  │
│ ❌ No guaranteed RPC fallback from Jito                         │
│ ❌ Inconsistent confirmation checking                           │
└─────────────────────────────────────────────────────────────────┘
                              ⬇️
┌─────────────────────────────────────────────────────────────────┐
│                    After Implementation                          │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Single reliable submitter (executors/submit.py)             │
│ ✅ Consistent error handling and logging                        │
│ ✅ Structured results with signature/status                     │
│ ✅ Real signatures in all logs                                  │
│ ✅ Guaranteed RPC fallback on any Jito error                    │
│ ✅ Robust confirmation polling (getSignatureStatuses)           │
│ ✅ Easy to maintain and update                                  │
└─────────────────────────────────────────────────────────────────┘
```
