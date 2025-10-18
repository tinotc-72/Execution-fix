# Retries, Health Checks, and Endpoint Failover Implementation

## Overview

This implementation adds automatic retry logic and RPC endpoint failover to handle transient RPC/Jito issues without blocking execution.

## Components Added

### 1. `utils/health.py`

Core utilities for health checking and retry logic:

- **`rpc_healthy(rpc_url, timeout=3.0)`**: Checks if an RPC endpoint is responding by calling `getHealth`
- **`with_retries(fn, attempts=3, base_sleep=0.5)`**: Wraps synchronous functions with exponential backoff retries
- **`async_with_retries(fn, attempts=3, base_sleep=0.5)`**: Wraps async functions with exponential backoff retries
- **`get_healthy_rpc(primary_rpc, secondary_rpc=None)`**: Implements automatic failover from primary to secondary RPC

### 2. Configuration Updates (`config.py`)

- Added `SECONDARY_RPC_URL` configuration for automatic failover
- Default fallback: `https://api.mainnet-beta.solana.com`

### 3. Integration Points

#### Jupiter Executor (`mev_jupiter_executor.py`)

Quote requests wrapped with retries:
```python
def _quote_request():
    response = requests.get(endpoint_url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()

data = with_retries(_quote_request, attempts=3, base_sleep=0.5)
```

Swap requests wrapped with retries:
```python
def _swap_request():
    response = requests.post(endpoint_url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()

data = with_retries(_swap_request, attempts=3, base_sleep=0.5)
```

#### Jito Service (`jito_service.py`)

All Jito RPC calls wrapped with async retries:
- `send_transaction()` - wrapped with 3 retry attempts
- `send_bundle()` - wrapped with 3 retry attempts
- `get_tip_accounts()` - wrapped with 3 retry attempts

#### Fast Executor (`fast_executor.py`)

RPC submission and confirmation wrapped with async retries:
- `_submit_via_rpc()` - wrapped with 3 retry attempts
- `_confirm_once()` - wrapped with 3 retry attempts

## Retry Behavior

### Exponential Backoff

The retry mechanism uses exponential backoff to reduce load on failing endpoints:
- Attempt 1: Immediate
- Attempt 2: 0.5s delay
- Attempt 3: 1.0s delay
- Maximum delay capped at 2.0s

### Bounded Attempts

All retries are bounded to prevent infinite loops:
- Default: 3 attempts
- Configurable per call site
- Last exception is raised if all attempts fail

## Failover Logic

The `get_healthy_rpc()` function implements simple failover:

1. Check if primary RPC is healthy
2. If primary is healthy, use it
3. If primary is unhealthy, check secondary
4. If secondary is healthy, use it
5. If both are unhealthy, use primary as fallback (let caller handle error)

## Copilot TODO Comments

All integration points include clear TODO comments for future reference:

```python
# Copilot TODO: Wrap outbound RPC calls in `with_retries()` with bounded attempts.
# Copilot TODO: Add a simple failover: if `rpc_healthy(primary)` is False, switch to `secondary` from config.
```

## Testing

### Unit Tests (`test_health_utilities.py`)

Comprehensive tests for all utility functions:
- `test_rpc_healthy()` - Tests health checking
- `test_with_retries()` - Tests sync retry wrapper
- `test_async_with_retries()` - Tests async retry wrapper
- `test_get_healthy_rpc()` - Tests failover logic

### Demo (`demo_retries_and_failover.py`)

Interactive demo showing:
- RPC health checks in action
- Automatic failover scenarios
- Retry mechanism with different failure patterns
- Integration examples from the codebase

## Usage Examples

### Using Health Check and Failover

```python
from config import HELIUS_RPC_URL, SECONDARY_RPC_URL
from utils.health import get_healthy_rpc

# Automatically select healthy RPC
rpc_url = get_healthy_rpc(HELIUS_RPC_URL, SECONDARY_RPC_URL)
```

### Using Retry Wrapper (Sync)

```python
from utils.health import with_retries

# Wrap any function that might fail transiently
result = with_retries(
    lambda: risky_api_call(),
    attempts=3,
    base_sleep=0.5
)
```

### Using Retry Wrapper (Async)

```python
from utils.health import async_with_retries

# Wrap async functions
result = await async_with_retries(
    lambda: async_risky_call(),
    attempts=3,
    base_sleep=0.5
)
```

## Benefits

✅ **Resilience**: Execution continues through temporary endpoint problems
✅ **Automatic Recovery**: Transient failures are handled automatically
✅ **Bounded Behavior**: No infinite loops or excessive retries
✅ **Exponential Backoff**: Reduces load on failing services
✅ **Simple Failover**: Automatic switch to secondary RPC when primary fails
✅ **Minimal Changes**: Small, surgical modifications to existing code
✅ **Well Documented**: Copilot TODO comments explain the logic

## Dependencies

- `requests>=2.31.0` - For synchronous HTTP requests and health checks
- `httpx>=0.25.0` - Already in use for async HTTP requests
- `asyncio` - Standard library for async retry logic

## Files Modified

1. `utils/health.py` (created)
2. `config.py` (added SECONDARY_RPC_URL)
3. `requirements.txt` (added requests)
4. `mev_jupiter_executor.py` (wrapped quote/swap with retries)
5. `jito_service.py` (wrapped all methods with async retries)
6. `fast_executor.py` (wrapped RPC calls with async retries)

## Files Added

1. `test_health_utilities.py` - Comprehensive unit tests
2. `demo_retries_and_failover.py` - Interactive demonstration

## Acceptance Criteria ✅

- [x] Add `utils/health.py` with `rpc_healthy()` and `with_retries()` 
- [x] Wrap quote/build/submit with retries
- [x] Implement automatic failover to secondary RPC
- [x] Document Copilot TODOs in code comments
- [x] Create tests for health check and retry utilities
- [x] Execution continues through temporary endpoint problems
