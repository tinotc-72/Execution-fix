# Quick Reference: Retry and Failover Utilities

## Basic Usage

### Check RPC Health
```python
from utils.health import rpc_healthy

# Check if an RPC endpoint is responding
if rpc_healthy("https://api.mainnet-beta.solana.com"):
    print("RPC is healthy")
```

### Wrap Functions with Retries (Sync)
```python
from utils.health import with_retries

# Wrap any risky function call
result = with_retries(
    lambda: risky_api_call(),
    attempts=3,        # Try up to 3 times
    base_sleep=0.5     # Start with 0.5s delay, doubles each retry
)
```

### Wrap Functions with Retries (Async)
```python
from utils.health import async_with_retries

# Wrap any risky async function call
result = await async_with_retries(
    lambda: async_risky_call(),
    attempts=3,
    base_sleep=0.5
)
```

### Automatic RPC Failover
```python
from config import HELIUS_RPC_URL, SECONDARY_RPC_URL
from utils.health import get_healthy_rpc

# Automatically select a healthy RPC
rpc_url = get_healthy_rpc(HELIUS_RPC_URL, SECONDARY_RPC_URL)
# Returns primary if healthy, secondary if primary unhealthy, or primary as fallback
```

## Common Patterns

### Pattern 1: Wrapping HTTP Requests
```python
from utils.health import with_retries
import requests

def fetch_data():
    def _request():
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    
    return with_retries(_request, attempts=3, base_sleep=0.5)
```

### Pattern 2: Wrapping Async RPC Calls
```python
from utils.health import async_with_retries
import httpx

async def submit_transaction(tx_data):
    async def _submit():
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(rpc_url, json=tx_data)
            r.raise_for_status()
            return r.json()
    
    return await async_with_retries(_submit, attempts=3, base_sleep=0.5)
```

### Pattern 3: Selective Retries
```python
from utils.health import with_retries

def operation_with_validation():
    def _inner():
        result = risky_operation()
        if not is_valid(result):
            raise ValueError("Invalid result")
        return result
    
    # Only retries on exceptions (ValueError, network errors, etc.)
    return with_retries(_inner, attempts=3)
```

## Integration Examples

### Jupiter Quote with Retries
```python
# From mev_jupiter_executor.py
def _quote_request():
    response = requests.get(endpoint_url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()

data = with_retries(_quote_request, attempts=3, base_sleep=0.5)
```

### Jito Transaction with Retries
```python
# From jito_service.py
async def send_transaction(self, signed_tx):
    async def _send_tx():
        tx = base64.b64encode(signed_tx).decode()
        payload = {"jsonrpc": "2.0", "id": 1, "method": "sendTransaction", "params": [tx]}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(self.tx_url, headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()
    
    return await async_with_retries(_send_tx, attempts=3, base_sleep=0.5)
```

## Configuration

### Default Values
- `attempts`: 3 (max number of tries)
- `base_sleep`: 0.5 seconds (initial delay)
- `timeout`: 3.0 seconds (for health checks)

### Retry Timing
- Attempt 1: Immediate (no delay)
- Attempt 2: 0.5s delay
- Attempt 3: 1.0s delay
- Attempt 4: 2.0s delay (if more attempts configured)
- Maximum delay capped at 2.0s

### Custom Configuration
```python
# More aggressive retries
result = with_retries(fn, attempts=5, base_sleep=0.2)

# More conservative retries
result = with_retries(fn, attempts=2, base_sleep=1.0)

# Longer health check timeout
healthy = rpc_healthy(url, timeout=10.0)
```

## Error Handling

### Exception Propagation
If all retry attempts fail, the last exception is raised:
```python
try:
    result = with_retries(always_fails, attempts=3)
except Exception as e:
    # This is the exception from the 3rd (last) attempt
    logger.error(f"All retries failed: {e}")
```

### No Retries on Success
If the function succeeds on the first try, no retries are performed:
```python
call_count = 0
def succeeds_immediately():
    call_count += 1
    return "success"

result = with_retries(succeeds_immediately, attempts=10)
# call_count == 1 (only called once)
```

## Testing

Run the test suite:
```bash
python3 test_health_utilities.py
```

Run the interactive demo:
```bash
python3 demo_retries_and_failover.py
```

## See Also

- `RETRIES_IMPLEMENTATION.md` - Full implementation documentation
- `IMPLEMENTATION_COMPLETE_RETRIES.md` - Completion summary
- `utils/health.py` - Source code with docstrings
