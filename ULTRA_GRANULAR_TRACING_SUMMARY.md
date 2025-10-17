# Ultra-Granular Step Tracing Implementation Summary

## Overview

This implementation adds ultra-granular step tracing and timing to the inference pipeline, providing detailed observability into each sub-step of the trade processing flow.

## Components Implemented

### 1. DebugSpan Context Manager (`debug_utils/debug_span.py`)

A comprehensive tracing utility that supports:

- **START/OK/FAIL Logging**: Automatically logs the beginning and end of each step
- **Elapsed Time Tracking**: Records execution time in milliseconds
- **Input/Output Keys Logging**: Captures what data each step receives and produces
- **Correlation ID**: Propagates a unique identifier across all logs for event tracking
- **Stack Trace Capture**: Automatically captures and logs stack traces on errors
- **Dual Usage**: Works as both context manager and decorator

#### Example Usage:

```python
# As context manager
with DebugSpan("step_name", input_data={"key": "value"}):
    # do work
    pass

# As decorator
@DebugSpan("function_name")
def my_function():
    pass
```

### 2. Correlation ID Generation (`main.py`)

At the start of each event in `_process_detected_trade()`:

1. **Generate correlation ID** from:
   - Signature (preferred): `{sig[:12]}`
   - Event ID (fallback): `evt_{event_id[:8]}`
   - UUID (last resort): `uuid_{uuid[:8]}`

2. **Set correlation ID** for the thread:
   ```python
   set_span_id(correlation_id)
   ```

3. **Log correlation context**:
   ```python
   logger.info("🪪 [CTX] corr=%s, dex=%s, wallet=%s", 
               correlation_id, dex, wallet_address)
   ```

### 3. Pipeline Integration (`trade_processor.py`)

The `infer_missing_fields()` method now wraps each sub-step with DebugSpan:

1. **ensure_meta** - Ensures metadata is attached to trade_info
2. **annotate_source_failure** - Marks error context
3. **last_chance_fetch** - Fetches missing transaction data via RPC
4. **infer_signature** - Infers missing signature from transaction
5. **fetch_transaction** - Fetches full transaction data
6. **infer_wallet** - Infers wallet address from transaction
7. **infer_action** - Infers action (buy/sell/swap) from logs
8. **infer_dex** - Infers DEX type from logs/instructions
9. **infer_token_mint** - Infers token mint from logs/balances

Each step logs:
- Start with correlation ID and input keys
- Success/failure with elapsed time
- Errors with full stack trace

## Log Output Examples

### Successful Step Execution:
```
2025-10-17 16:11:56,572 - INFO - 🪪 [CTX] corr=5KqZ7Nx8mN.., dex=jupiter, wallet=ABC123xyz...
2025-10-17 16:11:56,572 - INFO - 🔍 [FIELD_INFERENCE] Starting comprehensive field inference... | corr=5KqZ7Nx8mN..
2025-10-17 16:11:56,572 - INFO - ⏱️  [START] ensure_meta | corr=5KqZ7Nx8mN.. | input_keys=['has_meta']
2025-10-17 16:11:56,593 - INFO - ✅ [OK] ensure_meta | corr=5KqZ7Nx8mN.. | elapsed=20.12ms
```

### Failed Step with Stack Trace:
```
2025-10-17 16:11:56,719 - INFO - ⏱️  [START] error_prone_step | corr=error-scenario-001 | input_keys=['test']
2025-10-17 16:11:56,732 - ERROR - ❌ [FAIL] error_prone_step | corr=error-scenario-001 | elapsed=10.12ms | error=Simulated error: RPC timeout
2025-10-17 16:11:56,732 - ERROR - Stack trace:
Traceback (most recent call last):
  File "...", line 121, in simulate_error_scenario
    raise ValueError("Simulated error: RPC timeout")
ValueError: Simulated error: RPC timeout
```

## Benefits

### 1. **Performance Analysis**
- Identify slow steps in the inference pipeline
- Track execution time for each sub-step
- Optimize bottlenecks based on timing data

### 2. **Error Debugging**
- Immediately see which step failed
- Full stack traces for all errors
- Correlation ID links all logs for a single event

### 3. **Data Flow Tracking**
- See what input data each step receives
- Understand the sequence of transformations
- Track data availability at each stage

### 4. **Event Correlation**
- Single correlation ID across all logs for an event
- Easy to grep/filter logs for specific transactions
- Trace complete flow from event to execution

## Testing

### Unit Tests (`test_debug_span.py`)
- Context manager success/failure scenarios
- Decorator functionality
- Correlation ID propagation
- Nested span support
- **Result: 5/5 tests pass ✅**

### Integration Tests (`test_debug_span_integration.py`)
- Correlation ID generation in main.py
- Context logging with dex/wallet info
- DebugSpan integration in trade_processor.py
- Input data logging in wrapped steps
- **Result: 5/5 tests pass ✅**

### Demo (`demo_ultra_granular_tracing.py`)
- Complete inference pipeline simulation
- Error handling demonstration
- Nested spans example
- Shows all features in action

## Files Modified

1. **`debug_utils/debug_span.py`** (NEW) - DebugSpan implementation
2. **`debug_utils/__init__.py`** (NEW) - Package initialization
3. **`main.py`** - Added correlation ID generation and context logging
4. **`trade_processor.py`** - Wrapped inference steps with DebugSpan
5. **`test_debug_span.py`** (NEW) - Unit tests
6. **`test_debug_span_integration.py`** (NEW) - Integration tests
7. **`demo_ultra_granular_tracing.py`** (NEW) - Demo script

## Usage in Production

To use the tracing in production:

1. **Set log level to INFO** to see trace messages
2. **Search logs by correlation ID** to track specific events:
   ```bash
   grep "corr=5KqZ7Nx8mN" bot.log
   ```
3. **Analyze performance** by reviewing elapsed times
4. **Debug failures** using stack traces and input data

## Future Enhancements

Potential improvements:
- Add metrics export (Prometheus/StatsD)
- Include output data in logs (with size limits)
- Support for distributed tracing (OpenTelemetry)
- Performance overhead measurement
- Configurable log verbosity levels

## Conclusion

The ultra-granular tracing implementation provides comprehensive observability into the inference pipeline, making it easy to:
- Debug issues with detailed context
- Optimize performance using timing data
- Track data flow through the system
- Correlate logs across the entire event lifecycle

All tests pass successfully, demonstrating the robustness and correctness of the implementation.
