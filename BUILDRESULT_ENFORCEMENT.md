# BuildResult Enforcement

This document describes the BuildResult enforcement pattern and tools for maintaining it.

## Overview

All builder functions in this codebase should return a structured `BuildResult` instead of `None` to provide clear failure reasons and enable consistent error handling.

**Important:** The automated patcher only modifies functions that explicitly declare `BuildResult` as their return type. Functions returning `Optional[VersionedTransaction]` or other types require manual refactoring.

### BuildResult Structure

```python
@dataclass
class BuildResult:
    ok: bool                              # True if build succeeded
    tx: Optional[VersionedTransaction]    # The transaction if successful
    reason: Optional[str] = None          # Failure reason (REQUIRED when ok=False)
    dex: Optional[str] = None             # DEX name (jupiter, meteora, etc.)
    action: Optional[str] = None          # Action (buy, sell)
```

## Usage Pattern

### Builder Functions

Builder functions should return `BuildResult`:

```python
def build_and_sign(trade_info: dict, rpc: str, keypair: Keypair) -> BuildResult:
    """Build and sign a transaction."""
    try:
        # Build transaction
        tx = _build_transaction(...)
        return BuildResult(ok=True, tx=tx, dex="jupiter", action="buy")
    except Exception as e:
        return BuildResult(
            ok=False, 
            tx=None, 
            reason=f"Build failed: {str(e)}",
            dex="jupiter",
            action="buy"
        )
```

### Executor Functions

Executors should check the `.ok` property:

```python
async def execute_trade(trade_info: dict, keypair: Keypair):
    build_result = build_and_sign(trade_info, rpc_url, keypair)
    
    if not build_result.ok:
        logger.warning(f"Build failed: {build_result.reason}")
        if build_result.dex:
            logger.info(f"Failed DEX: {build_result.dex}, Action: {build_result.action}")
        return False
    
    # Use build_result.tx
    tx = build_result.tx
    sig = await submit_transaction(tx)
    return sig
```

## Tools

### 1. Patcher Tool (`tools/patch_buildresult.py`)

Automatically patches builder functions that have `BuildResult` return type but still have `return None` statements.

**Usage:**
```bash
# Preview changes
python tools/patch_buildresult.py --root . --dry-run --verbose

# Apply changes
python tools/patch_buildresult.py --root .

# Review changes
git diff
```

**What it does:**
- Scans Python files for builder functions with `BuildResult` return type
- Finds `return None` statements within these functions
- Replaces them with `return BuildResult(ok=False, tx=None, reason="builder failed (added by patch)")`
- Injects `from models.build_result import BuildResult` if missing

### 2. Verification Tool (`tools/verify_buildresult.py`)

Verifies that all builder functions follow the BuildResult pattern correctly.

**Usage:**
```bash
python tools/verify_buildresult.py
```

**What it checks:**
1. All builder functions with `BuildResult` return type don't have `return None` statements
2. Files using `BuildResult` properly check the `.ok` property
3. `BuildResult` is properly imported where used

**Output:**
```
✅ VERIFICATION PASSED!

All builder functions with BuildResult return type are compliant.
No 'return None' statements found in BuildResult functions.
```

## Current Status

As of the latest verification:

- ✅ **3 files** with builder functions: `mev_jupiter_executor.py`, `mev_meteora_executor.py`, `mev_raydium_executor.py`
- ✅ **All builder functions** return `BuildResult` properly
- ✅ **No `return None`** statements in builder functions
- ✅ **Executors check `.ok`** property correctly

Main builder functions:
- `mev_jupiter_executor.build_and_sign()` → Returns `BuildResult`
- `mev_jupiter_executor.build_buy_tx()` → Returns `BuildResult`
- `mev_jupiter_executor.build_sell_tx()` → Returns `BuildResult`
- `mev_meteora_executor.build_and_sign()` → Returns `BuildResult`
- `mev_raydium_executor.try_raydium_buy()` → Returns `BuildResult`
- `mev_raydium_executor.try_raydium_sell_all()` → Returns `BuildResult`

Executors that check `.ok`:
- `execution_coordinator.py` - Checks `build_result.ok` before using transaction
- `mev_meteora_executor.py` - Checks `result.ok` in transaction submission

## Development Workflow

When adding new builder functions:

1. **Declare the return type as `BuildResult`:**
   ```python
   def my_builder(...) -> BuildResult:
   ```

2. **Never return `None` - always return a structured result:**
   ```python
   # Bad
   if error:
       return None
   
   # Good
   if error:
       return BuildResult(ok=False, tx=None, reason="Error description")
   ```

3. **Provide clear failure reasons:**
   ```python
   return BuildResult(
       ok=False,
       tx=None,
       reason="Failed to get route from Jupiter API",
       dex="jupiter",
       action="buy"
   )
   ```

4. **Run verification before committing:**
   ```bash
   python tools/verify_buildresult.py
   ```

## Migration Guide

To migrate existing builders that return `Optional[VersionedTransaction]`:

1. **Update return type annotation:**
   ```python
   # Before
   def build_transaction(...) -> Optional[VersionedTransaction]:
   
   # After
   def build_transaction(...) -> BuildResult:
   ```

2. **Replace successful returns:**
   ```python
   # Before
   return transaction
   
   # After
   return BuildResult(ok=True, tx=transaction, dex="jupiter", action="buy")
   ```

3. **Replace error returns:**
   ```python
   # Before
   return None
   
   # After
   return BuildResult(ok=False, tx=None, reason="Build failed", dex="jupiter", action="buy")
   ```

4. **Update callers to check `.ok`:**
   ```python
   # Before
   tx = build_transaction(...)
   if tx is None:
       return
   
   # After
   result = build_transaction(...)
   if not result.ok:
       logger.warning(f"Build failed: {result.reason}")
       return
   tx = result.tx
   ```

5. **Run verification:**
   ```bash
   python tools/verify_buildresult.py
   ```

## Benefits

- **Clear error messages**: Every failure has a specific reason
- **Type safety**: No more `None` checks, use `.ok` instead
- **Debugging**: Easier to trace why builds fail
- **Monitoring**: Can track failure rates by DEX and action
- **Consistency**: All builders follow the same pattern
