# Quick Reference: Executor Fixes

## For Developers Using These Executors

### 1. Jupiter Executor - Type-Safe Mint Handling

**Problem Solved**: Jupiter builder crashes when Pubkey objects are passed instead of strings.

**Solution**: Use `_as_mint_str()` helper or just pass any type - it auto-converts.

```python
from mev_jupiter_executor import get_best_route, _as_mint_str
from solders.pubkey import Pubkey

# ✅ All of these now work:
token_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
route1 = get_best_route(token_mint, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", amount)

route2 = get_best_route("So11111111111111111111111111111111111111112", 
                        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", amount)

# Manual conversion if needed
mint_str = _as_mint_str(my_pubkey_or_string)
```

### 2. Jupiter Executor - Null-Safe Route Handling

**Problem Solved**: Crashes when accessing route.keys() on None response.

**Solution**: Always check if route is None before using.

```python
from mev_jupiter_executor import get_best_route

route = get_best_route(input_mint, output_mint, amount)

# ✅ Safe pattern - route will be None if failed
if route is None:
    logger.error("No route available - trying different DEX")
    # Coordinator can fallback to Raydium, Meteora, etc.
else:
    # Safe to use route
    swap_tx = get_swap_transaction(route, wallet_pubkey)
```

### 3. Fast Executor - Optional Jito Import

**Problem Solved**: Import failure when jito_service not available breaks entire module.

**Solution**: Jito is now optional - pure RPC always works.

```python
from fast_executor import FastExecutor

# ✅ Works even if jito_service is not installed
executor = FastExecutor(keypair, rpc_url)

# Check Jito availability
if hasattr(executor, 'jito_client') and executor.jito_client:
    print("Jito available - MEV protection enabled")
else:
    print("Jito not available - using pure RPC")
```

### 4. Fast Executor - Unified Submit with Fallback

**Problem Solved**: Scattered submission logic with no clear fallback path.

**Solution**: Use `send_and_confirm()` for unified Jito → RPC fallback.

```python
from fast_executor import FastExecutor
from solders.transaction import VersionedTransaction

executor = FastExecutor(keypair, rpc_url)
await executor.initialize()

# Build your transaction
tx = VersionedTransaction(...)

# ✅ Unified submission with automatic fallback
signature = await executor.send_and_confirm(tx)

if signature:
    print(f"Success: {signature}")
    # Transaction confirmed
else:
    print("All paths failed (Jito + RPC)")
    # Handle failure - maybe retry with different settings
```

### 5. Fast Executor - EnvKeys Configuration

**Problem Solved**: Hardcoded config values don't allow runtime flexibility.

**Solution**: FastExecutor now uses EnvKeys for Jito configuration.

```python
# In your .env file:
# JITO_UUID=your_jito_auth_token
# JITO_BUNDLE_ENDPOINT=https://london.mainnet.block-engine.jito.wtf

from fast_executor import FastExecutor
from env_keys import EnvKeys

# ✅ Configuration loaded from EnvKeys
executor = FastExecutor(keypair, rpc_url)
# Jito credentials automatically loaded from env
```

### 6. Fast Executor - Get Tip Accounts Helper

**Problem Solved**: No easy way to get Jito tip accounts.

**Solution**: Use `get_tip_accounts()` helper.

```python
from fast_executor import FastExecutor

executor = FastExecutor(keypair, rpc_url)
await executor.initialize()

# ✅ Get tip accounts (from API or hardcoded fallback)
tip_accounts = await executor.get_tip_accounts()

print(f"Available tip accounts: {len(tip_accounts)}")
for account in tip_accounts:
    print(f"  - {account}")
```

## Common Patterns

### Pattern 1: Jupiter with Fallback to Different DEX

```python
from mev_jupiter_executor import get_best_route, get_swap_transaction
from mev_raydium_executor import RaydiumExecutor

# Try Jupiter first
route = get_best_route(input_mint, output_mint, amount)

if route:
    # Jupiter route available
    swap_tx = get_swap_transaction(route, wallet_pubkey)
    if swap_tx:
        signature = await executor.send_and_confirm(tx)
else:
    # ✅ Clean fallback to Raydium
    raydium = RaydiumExecutor(keypair, rpc_url)
    result = await raydium.execute_buy(token_mint, amount_sol)
```

### Pattern 2: Safe Transaction Submission with Retries

```python
from fast_executor import FastExecutor
import asyncio

executor = FastExecutor(keypair, rpc_url)
await executor.initialize()

max_retries = 3
for attempt in range(max_retries):
    signature = await executor.send_and_confirm(tx)
    
    if signature:
        print(f"✅ Success on attempt {attempt + 1}: {signature}")
        break
    else:
        if attempt < max_retries - 1:
            print(f"Retry {attempt + 1}/{max_retries}...")
            await asyncio.sleep(1)
        else:
            print("❌ All retries exhausted")
```

### Pattern 3: Multiple DEX Fallback Chain

```python
from mev_jupiter_executor import MEVJupiterExecutor
from mev_raydium_executor import MEVRaydiumExecutor
from mev_meteora_executor import MEVMeteoraExecutor

executors = [
    ("Jupiter", MEVJupiterExecutor(keypair, rpc_url)),
    ("Raydium", MEVRaydiumExecutor(keypair, rpc_url)),
    ("Meteora", MEVMeteoraExecutor(keypair, rpc_url))
]

for dex_name, executor in executors:
    print(f"Trying {dex_name}...")
    result = await executor.execute_buy(token_mint, amount_sol)
    
    if result.get('success'):
        print(f"✅ Success via {dex_name}: {result['signature']}")
        break
    else:
        print(f"❌ {dex_name} failed: {result.get('error')}")
        # ✅ Clean failure, try next DEX
```

## Error Handling Best Practices

### 1. Always Check Return Values

```python
# ❌ BAD - assumes success
route = get_best_route(input_mint, output_mint, amount)
swap_tx = get_swap_transaction(route, wallet)  # Crashes if route is None

# ✅ GOOD - checks for None
route = get_best_route(input_mint, output_mint, amount)
if route:
    swap_tx = get_swap_transaction(route, wallet)
    if swap_tx:
        # Proceed with transaction
```

### 2. Handle Type Flexibility

```python
# ✅ Works with any mint type
def my_trade_function(token_mint):
    # token_mint can be Pubkey, str, or any object with __str__
    route = get_best_route(token_mint, SOL_MINT, amount)
    # Automatically coerced to string
```

### 3. Graceful Degradation

```python
# Try Jito, fall back to RPC automatically
signature = await executor.send_and_confirm(tx)

if not signature:
    # All paths failed - handle gracefully
    logger.error("Transaction submission failed on all paths")
    # Maybe try different slippage, different DEX, or notify user
```

## Testing Your Integration

Run the validation test:

```bash
python3 test_executor_fixes.py
```

Expected output:
```
================================================================================
EXECUTOR FIXES VALIDATION TEST SUITE
================================================================================

✅ PASS: _as_mint_str() Helper
✅ PASS: Null-Safety Check
✅ PASS: Mint Coercion in get_best_route
✅ PASS: Jito Optional Import
✅ PASS: send_and_confirm() Method
✅ PASS: get_tip_accounts() Helper
✅ PASS: EnvKeys Usage

Total: 7/7 tests passed
🎉 All tests passed!
```

## Migration Checklist

If you're updating existing code:

- [ ] Replace direct `submit_transaction` calls with `send_and_confirm` for unified logic
- [ ] Remove manual Jito fallback code - now handled automatically
- [ ] Check for `route is None` instead of `not route` for clarity
- [ ] Update Jito configuration to use EnvKeys (JITO_UUID, JITO_BUNDLE_ENDPOINT)
- [ ] Remove any manual mint type conversion - now automatic
- [ ] Test without Jito installed to verify RPC fallback works

## Support

For issues or questions:
1. Check test_executor_fixes.py for examples
2. Review EXECUTOR_FIXES_BEFORE_AFTER.md for detailed comparisons
3. See EXECUTOR_FIXES_IMPLEMENTATION_SUMMARY.md for implementation details
