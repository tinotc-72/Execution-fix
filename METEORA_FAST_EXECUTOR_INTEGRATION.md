# Meteora FastExecutor Integration

## Problem
The original implementation used bundle-specific parsing that expected `{"success": ..., "signature": ...}` from Jito JSON-RPC. However, Jito JSON-RPC doesn't return this format, causing:
- False negatives (failing to detect successful submissions)
- No fallback to RPC when Jito fails

## Solution
Route all Meteora submissions through `FastExecutor.send_and_confirm()`, which already implements proper Jito→RPC fallback with correct JSON-RPC parsing.

## Changes Made

### 1. MEVMeteoraExecutor.__init__
**Before:**
```python
def __init__(self, wallet_keypair: Keypair, rpc_client: SimpleRPC, jito_service=None):
    self.jito_service = jito_service
```

**After:**
```python
def __init__(self, wallet_keypair: Keypair, rpc_client: SimpleRPC, fast_executor=None):
    self.fast_executor = fast_executor  # Use provided fast_executor for submissions
```

### 2. Removed Bundle Parsing Methods
**Removed:**
- `_execute_with_jito()` - used bundle parsing with `result.get("success")`
- `_execute_standard()` - used custom RPC submission

**Replaced with:**
```python
async def _execute_via_fast_executor(self, vtx: VersionedTransaction) -> MeteoraTradeResult:
    sig = await self.fast_executor.send_and_confirm(vtx)
    if not sig:
        return MeteoraTradeResult(success=False, error="submit failed (Jito+RPC)")
    return MeteoraTradeResult(success=True, signature=sig)
```

### 3. Updated execute_buy and execute_sell
**Before:**
```python
# Step 5: Execute with MEV protection
if params.use_jito:
    result = await self._execute_with_jito(transaction)
else:
    result = await self._execute_standard(transaction)
```

**After:**
```python
# Step 5: Convert to VersionedTransaction and sign
bh_resp = self.client.get_latest_blockhash()
msg = MessageV0.try_compile(self.wallet.pubkey(), transaction.instructions, [], bh)
vtx = VersionedTransaction(msg, [self.wallet])

# Step 6: Execute via FastExecutor
result = await self._execute_via_fast_executor(vtx)
```

### 4. Updated mev_meteora_copy_trade
**Before:**
```python
# Dual-path execution: Jito first, RPC fallback
if jito_is_configured(jito_service):
    result = await jito_service.send_transaction(signed_tx_bytes)
    signature = result.get("signature")  # ❌ Bundle parsing
    if signature:
        return exec_ok("meteora", signature, {"path": "jito"})
sig = _send_and_confirm(rpc, tx)
return exec_ok("meteora", str(sig), {"path": "rpc"})
```

**After:**
```python
# Use FastExecutor for unified Jito→RPC fallback
sig = await fast_executor.send_and_confirm(vtx)
if not sig:
    return None
return sig
```

### 5. Cleaned Up Helper Returns
Removed improper use of `exec_err()` in methods that should return `None` or proper types:
- `_get_pool_info()` now returns `None` instead of `exec_err()`
- `_get_tokens_received()` now returns `None` instead of `exec_err()`
- `SimpleRPC.get_transaction()` now returns `None` instead of `exec_err()`

## Expected Behavior

When a Meteora trade is triggered, you should see:

```
[METEORA_BUY] 🔄 Starting Meteora buy execution...
🚀 Executing via FastExecutor (Jito→RPC fallback)...
[SUBMIT_JITO] region=<url> sig=<signature>    # If Jito succeeds
  OR
[SUBMIT_RPC] sig=<signature>                   # If RPC is used
[CONFIRM] attempt=1/5 status=<status>
[CONFIRM][FINAL] sig=<signature> status=<status>
✅ Meteora buy successful!
```

## Testing

Run the test to verify the implementation:
```bash
python test_meteora_fast_executor.py
```

All tests should pass, confirming:
- ✅ MEVMeteoraExecutor accepts FastExecutor
- ✅ No bundle parsing (result.get)
- ✅ Uses FastExecutor.send_and_confirm(vtx)
- ✅ Returns proper MeteoraTradeResult
- ✅ mev_meteora_copy_trade updated to use FastExecutor

## Benefits

1. **Proper JSON-RPC Parsing**: FastExecutor correctly parses JSON-RPC responses
2. **Automatic Fallback**: Jito→RPC fallback is handled automatically
3. **Consistent Logging**: All submissions use standardized [SUBMIT_JITO]/[SUBMIT_RPC]/[CONFIRM] logs
4. **On-chain Confirmation**: FastExecutor waits for on-chain confirmation
5. **Reduced Code Duplication**: Centralized submission logic in FastExecutor
