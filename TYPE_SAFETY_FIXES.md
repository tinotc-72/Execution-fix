# Type Safety Fixes: Meteora Signer and Jupiter Mints

## Summary

This PR implements critical type safety fixes to prevent builder crashes from type errors and missing keys:

1. **Never fabricate random keypairs** - only use configured wallet
2. **Never pass wrapper wallets to builders** - only raw `solders.Keypair`
3. **Assert Keypair types** in Meteora VersionedTransaction creation
4. **Normalize mints to strings** in Jupiter to prevent Pubkey type errors
5. **Guard against None** before accessing route.keys()

## Changes Made

### 1. execution_coordinator.py

#### Added `_require_keypair()` Helper
```python
def _require_keypair(self):
    """
    Fetch and validate the real Keypair from wallet configuration.
    
    Never fabricates a random keypair. If the configured wallet isn't loaded or 
    is not a valid Keypair, raises TypeError.
    """
    if hasattr(self.wallet, 'keypair'):
        keypair = self.wallet.keypair
        # Assert the extracted keypair is actually a Keypair instance
        if not isinstance(keypair, Keypair):
            error_msg = f"Wallet.keypair is not a Keypair instance: {type(keypair)}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
        return keypair
    elif isinstance(self.wallet, Keypair):
        return self.wallet
    else:
        error_msg = f"Configured wallet not loaded or invalid: {type(self.wallet)}"
        self.logger.error(error_msg)
        raise TypeError(error_msg)
```

#### Removed Random Keypair Fabrication
**Before:**
```python
if not wallet_keypair:
    logger.warning("[CONTEXT] Missing wallet keypair, using fallback Keypair()")
    from solders.keypair import Keypair
    wallet_keypair = Keypair()  # ❌ Random keypair!
```

**After:**
```python
# Use _require_keypair() to get validated keypair - raises if wallet not loaded
try:
    wallet_keypair = self._require_keypair()
except TypeError as e:
    logger.error(f"[CONTEXT] Cannot execute without valid wallet: {e}")
    return {'success': False, 'error': f'Wallet not loaded: {e}'}
```

### 2. mev_meteora_executor.py

#### Added Keypair Type Assertions
Three functions now assert `isinstance(owner/keypair, Keypair)` before creating VersionedTransaction:

1. **_build_meteora_buy_solders:**
```python
def _build_meteora_buy_solders(rpc: SimpleRPC, owner: Keypair, ...):
    # Assert owner is a valid Keypair before proceeding
    assert isinstance(owner, Keypair), f"owner must be a Keypair, got {type(owner)}"
    # ... rest of function
    return VersionedTransaction(msg, [owner])
```

2. **_build_meteora_sell_solders:**
```python
def _build_meteora_sell_solders(rpc: SimpleRPC, owner: Keypair, ...):
    # Assert owner is a valid Keypair before proceeding
    assert isinstance(owner, Keypair), f"owner must be a Keypair, got {type(owner)}"
    # ... rest of function
    return VersionedTransaction(msg, [owner])
```

3. **build_and_sign:**
```python
def build_and_sign(trade_info: dict, rpc: SimpleRPC, keypair: Keypair, ...):
    # ... build transaction
    # Assert keypair is a valid Keypair before creating VersionedTransaction
    assert isinstance(keypair, Keypair), f"keypair must be a Keypair, got {type(keypair)}"
    
    msg = MessageV0.try_compile(payer, ixs, address_lookup_tables, bh)
    vtx = VersionedTransaction(msg, [keypair])
```

### 3. mev_jupiter_executor.py

#### Already Had `_as_mint_str()` Helper
```python
def _as_mint_str(m) -> str:
    """Coerce any Pubkey or object to string for safe use in API calls."""
    return str(m) if not isinstance(m, Pubkey) else str(m)
```

#### Applied `_as_mint_str()` Throughout
1. **get_best_route** - Already had coercion for input_mint and output_mint
2. **build_buy_tx** - Added coercion:
```python
def build_buy_tx(token_mint: str, amount_sol: float, wallet: Keypair, ...):
    # Coerce token_mint to string in case it's a Pubkey
    token_mint_str = _as_mint_str(token_mint)
    route = get_best_route(_as_mint_str(SOL_MINT), token_mint_str, ...)
```

3. **build_sell_tx** - Added coercion:
```python
def build_sell_tx(token_mint: str, wallet: Keypair, ...):
    # Coerce token_mint to string in case it's a Pubkey
    token_mint_str = _as_mint_str(token_mint)
    route = get_best_route(token_mint_str, _as_mint_str(SOL_MINT), ...)
```

4. **execute_buy** - Added coercion:
```python
async def execute_buy(self, token_mint: str, amount_sol: float, **kwargs):
    # Coerce token_mint to string in case it's a Pubkey
    token_mint_str = _as_mint_str(token_mint)
    # ... use token_mint_str throughout
```

5. **execute_sell** - Added coercion:
```python
async def execute_sell(self, token_mint: str, **kwargs):
    # Coerce token_mint to string in case it's a Pubkey
    token_mint_str = _as_mint_str(token_mint)
    # ... use token_mint_str throughout
```

#### Added Route None Guard
**Before:**
```python
def get_swap_transaction(route: dict, user_pubkey: Pubkey):
    logger.debug(f"[JUPITER_SWAP] Route keys: {list(route.keys())}")  # ❌ Crashes if route is None
```

**After:**
```python
def get_swap_transaction(route: dict, user_pubkey: Pubkey):
    # Guard: Check if route is None before accessing .keys()
    if route is None:
        logger.error(f"[JUPITER_SWAP] ❌ Route is None, cannot get swap transaction")
        return None
    
    logger.debug(f"[JUPITER_SWAP] Route keys: {list(route.keys())}")  # ✅ Safe
```

#### Added Route Validation in Build Functions
```python
def build_buy_tx(...):
    route = get_best_route(...)
    if route is None:
        raise ValueError("Failed to get route from Jupiter")
    swap_tx_b64 = get_swap_transaction(route, ...)
    if swap_tx_b64 is None:
        raise ValueError("Failed to get swap transaction from Jupiter")
```

## Validation

All fixes validated with `validate_type_safety_fixes.py`:

```
✅ ALL CHECKS PASSED

Validated fixes:
  • _require_keypair() validates wallet and returns raw Keypair
  • No random keypair fabrication - raises if wallet not loaded
  • Meteora builders assert isinstance(owner/keypair, Keypair)
  • Jupiter _as_mint_str() coerces Pubkey to string for all mints
  • Jupiter guards route is None before .keys() access

Goal achieved: Fix Meteora signer and normalize Jupiter mints,
preventing builder crashes from type errors and missing keys.
```

## Impact

### Before
- ❌ Random keypairs could be fabricated, leading to failed transactions
- ❌ Wrapper wallets passed to builders causing type errors
- ❌ Pubkey objects passed where strings expected, causing API failures
- ❌ route.keys() crashes when route is None
- ❌ No type assertions before VersionedTransaction creation

### After
- ✅ Only configured wallet used, raises if not loaded
- ✅ Only raw `solders.Keypair` passed to builders
- ✅ All mints coerced to strings before API calls
- ✅ Route guarded before .keys() access
- ✅ Type assertions prevent crashes in Meteora builders

## Files Changed
- `execution_coordinator.py` - Added `_require_keypair()`, removed random keypair fabrication
- `mev_meteora_executor.py` - Added Keypair type assertions (3 locations)
- `mev_jupiter_executor.py` - Applied `_as_mint_str()` throughout, added route guards
- `validate_type_safety_fixes.py` - Validation script (new)
- `test_keypair_mint_validation.py` - Unit test script (new)
