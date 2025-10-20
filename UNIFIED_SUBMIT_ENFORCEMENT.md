# Unified Submit Helper Enforcement

## Overview

This PR enforces repo-wide use of the unified transaction submission helper (`send_and_confirm_v0_tx_sync`) for all RPC transaction submission code paths. This ensures consistent logging, confirmation, and error handling across all executors.

## Goals

- Remove direct JSON-RPC submissions (raw `sendTransaction` or `sendRawTransaction` calls)
- Guarantee confirmation & logging via `send_and_confirm_v0_tx_sync` for every executor
- Jito-first submit is optional, but RPC fallback with unified confirmation is mandatory
- Every code path logs: `DEX, action, mint, signature, confirmationStatus, ok`

## Implementation

### 1. Enhanced `executors/submit.py`

Added:
- `SubmitResult` dataclass for structured results with fields:
  - `ok` (bool): Success status
  - `signature` (str): Transaction signature
  - `status` (str): Human-readable status
  - `confirmationStatus` (str): RPC confirmation status
  - `error` (str): Error message on failure

- `send_and_confirm_v0_tx_sync()`: Synchronous wrapper for the async helper
  - Takes `rpc_url`, `versioned_tx` as parameters
  - Returns `SubmitResult` with all fields populated
  - Automatically handles event loop management

### 2. Automated Patcher Tool

`tools/patch_unified_submit.py`:
- Scans Python files for raw submission patterns
- Replaces them with imports and calls to unified helper
- Preserves original code as comments for review
- Skips test files, demos, and Jito service (as per requirements)

Usage:
```bash
python tools/patch_unified_submit.py --root . --rpc-env RPC_URL [--dry-run]
```

### 3. Verification Tool

`tools/verify_readiness.py`:
- Checks for remaining raw submission patterns
- Verifies helper imports are present
- Reports on logging compliance
- Identifies files needing attention

Usage:
```bash
python tools/verify_readiness.py
```

## Excluded Files

The following files are intentionally excluded from enforcement:

1. **`jito_service.py`**: Jito Block Engine client for MEV protection
   - Reason: Jito-first submission is optional per requirements
   - Uses Jito's `/api/v1/transactions` endpoint, not standard RPC
   - RPC fallback (when used) should still use unified helper

2. **Test files** (`test_*.py`): Testing infrastructure
   - Reason: Tests may need to test raw submission patterns
   - Tests verify the unified helper itself

3. **Demo files** (`demo_*.py`): Example and demonstration code
   - Reason: Demos may show both old and new patterns

4. **Validation files** (`validate_*.py`, `verify_*.py`): Verification scripts
   - Reason: These scripts check for patterns, don't submit transactions

## Files Requiring Manual Review

The following files have raw submission patterns that need to be replaced with the unified helper:

### 1. `transaction_cloner.py` (Line 326)

**Current code:**
```python
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": [tx_b64, params]
}
async with aiohttp.ClientSession() as session:
    async with session.post(self.rpc_url, json=payload) as response:
        data = await response.json()
        if "result" in data:
            logger.info(f"Transaction sent successfully. Signature: {data['result']}")
            return data["result"]
```

**Recommended fix:**
```python
from executors.submit import send_and_confirm_v0_tx

# Instead of raw submission, use the unified helper
result = await send_and_confirm_v0_tx(new_tx, self.rpc_url)
if result["success"]:
    sig = result["signature"]
    logger.info(f"[SUBMIT] DEX=cloner action=clone mint=unknown sig={sig} status={result['status']['confirmationStatus']} ok=True")
    return sig
else:
    logger.error(f"Transaction submission failed: {result.get('error')}")
    return None
```

### 2. `complete_mev_bot.py` (Line 169)

**Current code:**
```python
async with httpx.AsyncClient(timeout=self.config.timeout) as client:
    serialized = b58encode(bytes(transaction)).decode()
    
    response = await client.post(
        self.env.HELIUS_RPC_URL,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [serialized, {...}]
        }
    )
    
    result = response.json()
    if 'result' in result:
        signature = result['result']
        logger.info(f"✅ CompleteMEVBot buy success: {signature}")
```

**Recommended fix:**
```python
from executors.submit import send_and_confirm_v0_tx

# Use unified helper
result = await send_and_confirm_v0_tx(transaction, self.env.HELIUS_RPC_URL)
if result["success"]:
    signature = result["signature"]
    logger.info(f"[SUBMIT] DEX=mev action=buy mint={token_mint} sig={signature} status={result['status']['confirmationStatus']} ok=True")
else:
    logger.error(f"Transaction failed: {result.get('error')}")
```

### 3. `mev_meteora_executor.py` (Line 129)

**Current code in SimpleRPC class:**
```python
def send_transaction(self, txn: VersionedTransaction, skip_preflight: bool = False) -> Signature:
    raw = base64.b64encode(bytes(txn)).decode()
    params = [
        raw,
        {"encoding": "base64", "skipPreflight": skip_preflight, "maxRetries": 3},
    ]
    sig_str = self._post("sendTransaction", params)
    return Signature.from_string(sig_str)
```

**Recommended fix:**
Replace the synchronous SimpleRPC.send_transaction with async version using unified helper:
```python
async def send_transaction(self, txn: VersionedTransaction, skip_preflight: bool = False) -> Signature:
    """Send transaction using unified helper for consistent confirmation and logging"""
    from executors.submit import send_and_confirm_v0_tx
    
    result = await send_and_confirm_v0_tx(txn, self.url)
    if result["success"]:
        return Signature.from_string(result["signature"])
    else:
        raise RuntimeError(f"Transaction submission failed: {result.get('error')}")
```

### 4. `fast_executor.py` (Line 170)

**Current code:**
```python
async def _submit_via_rpc(self, vtx) -> str | None:
    """Submit transaction via RPC"""
    try:
        raw = bytes(vtx)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [base64.b64encode(raw).decode(), {"encoding": "base64"}]
        }
        async def _send_rpc():
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(self._rpc_url, json=payload)
                r.raise_for_status()
                return r.json()
        
        data = await async_with_retries(_send_rpc, attempts=3, base_sleep=0.5)
        sig = (data or {}).get("result")
        return sig
```

**Recommended fix:**
```python
async def _submit_via_rpc(self, vtx) -> str | None:
    """Submit transaction via RPC using unified helper"""
    try:
        from executors.submit import send_and_confirm_v0_tx
        
        result = await send_and_confirm_v0_tx(vtx, self._rpc_url)
        if result["success"]:
            sig = result["signature"]
            self.logger.info(f"[SUBMIT_RPC] sig={sig} status={result['status']['confirmationStatus']} ok=True")
            return sig
        else:
            self.logger.error(f"[SUBMIT_RPC] error: {result.get('error')}")
            return None
    except Exception as e:
        self.logger.error(f"[SUBMIT_RPC] exception: {e}")
        return None
```

### 5. `mev_direct_sell_executor.py` (Line 644)

**Current code:**
```python
async def _submit_via_rpc(self, serialized_tx: bytes) -> Optional[str]:
    """Submit transaction via RPC (legacy method)"""
    try:
        import base64
        tx_base64 = base64.b64encode(serialized_tx).decode('utf-8')
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [tx_base64, {...}]
        }
        
        import requests
        response = requests.post(self.rpc_url, json=payload, timeout=30)
        ...
```

**Recommended fix:**
```python
async def _submit_via_rpc(self, serialized_tx: bytes) -> Optional[str]:
    """Submit transaction via RPC using unified helper"""
    try:
        from executors.submit import send_and_confirm_v0_tx
        from solders.transaction import VersionedTransaction
        
        # Deserialize back to VersionedTransaction for unified helper
        # Note: This assumes serialized_tx is from bytes(vtx)
        # If not, this method needs adjustment
        vtx = VersionedTransaction.from_bytes(serialized_tx)
        
        result = await send_and_confirm_v0_tx(vtx, self.rpc_url)
        if result["success"]:
            signature = result["signature"]
            logger.info(f"[SUBMIT] DEX=direct_sell action=sell mint=unknown sig={signature} status={result['status']['confirmationStatus']} ok=True")
            return signature
        else:
            logger.error(f"RPC submission error: {result.get('error')}")
            return None
    except Exception as e:
        logger.error(f"RPC submission exception: {e}")
        return None
```

### 6. `utils.py` (Lines 214, 516)

These utility functions need to be reviewed and updated to use the unified helper. The specific context depends on how they're used.

**Line 214 context:** Check if this is a standalone submission function
**Line 516 context:** Check if this is part of a larger utility

Both should be replaced with calls to `send_and_confirm_v0_tx` or `send_and_confirm_v0_tx_sync` depending on whether the context is async or sync.

## Implementation Notes

1. **Async vs Sync**: 
   - Use `send_and_confirm_v0_tx()` in async functions
   - Use `send_and_confirm_v0_tx_sync()` in synchronous functions

2. **Result Format**:
   - Async version returns `Dict[str, Any]` with keys: `success`, `signature`, `status`, `error`
   - Sync version returns `SubmitResult` dataclass with attributes: `ok`, `signature`, `status`, `confirmationStatus`, `error`

3. **Logging**:
   - Always log after submission with the standard format
   - Include DEX, action, mint, signature, status, and ok fields
   - Use appropriate values based on context

4. **Error Handling**:
   - Check `result["success"]` (async) or `res.ok` (sync)
   - Log errors from `result.get("error")` or `res.error`
   - Return appropriate error values (None, False, etc.)

## Verification Checklist

After patching, verify the following:

- [ ] Run patcher: `python tools/patch_unified_submit.py --root . --rpc-env RPC_URL`
- [ ] Review changes: `git diff`
- [ ] Run verification: `python tools/verify_readiness.py`
- [ ] Search for bypasses: `grep -r 'sendTransaction\|sendRawTransaction' --include='*.py' . | grep -v test_ | grep -v demo_ | grep -v jito_service`
- [ ] Confirm all submit paths log: `grep -r 'DEX.*action.*mint.*sig.*status.*ok' --include='*.py' .`
- [ ] Test executors still work correctly

## Logging Format

All transaction submissions must log in this format:

```python
logger.info(f"[SUBMIT] DEX={dex} action={action} mint={mint} sig={res.signature} status={res.confirmationStatus} ok={res.ok}")
```

Where:
- `dex`: DEX name (e.g., "raydium", "meteora", "jupiter")
- `action`: Action type (e.g., "buy", "sell", "swap")
- `mint`: Token mint address
- `sig`: Transaction signature (from `res.signature`)
- `status`: Confirmation status (from `res.confirmationStatus`)
- `ok`: Success boolean (from `res.ok`)

## Example Usage

### Before (Raw Submission)
```python
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": [base64.b64encode(bytes(vtx)).decode(), {"encoding": "base64"}]
}
response = requests.post(rpc_url, json=payload)
sig = response.json()["result"]
```

### After (Unified Helper)
```python
from executors.submit import send_and_confirm_v0_tx_sync, SubmitResult
import os

# For synchronous code
res = send_and_confirm_v0_tx_sync(os.getenv("RPC_URL"), versioned_tx)
logger.info(f"[SUBMIT] DEX={dex} action={action} mint={mint} sig={res.signature} status={res.confirmationStatus} ok={res.ok}")

# For async code
from executors.submit import send_and_confirm_v0_tx

res = await send_and_confirm_v0_tx(versioned_tx, os.getenv("RPC_URL"))
logger.info(f"[SUBMIT] DEX={dex} action={action} mint={mint} sig={res['signature']} status={res['status']['confirmationStatus']} ok={res['success']}")
```

## Benefits

1. **Consistency**: All submissions use the same code path
2. **Reliability**: Unified confirmation polling with retries
3. **Observability**: Standardized logging format for all transactions
4. **Maintainability**: Single source of truth for submission logic
5. **Debugging**: Easier to track down submission issues

## Definition of Done

- ✅ Synchronous wrapper added to `executors/submit.py`
- ✅ Patcher tool created (`tools/patch_unified_submit.py`)
- ✅ Verification tool created (`tools/verify_readiness.py`)
- ⏳ All non-Jito RPC submissions use unified helper
- ⏳ All submit paths include proper logging
- ⏳ Verification script passes with zero violations
- ⏳ Documentation complete

## Notes

- The patcher is conservative and comments out original code for review
- Manual adjustments may be needed for complex async patterns
- Jito service intentionally excluded as Jito-first is optional
- Test and demo files intentionally excluded for flexibility
