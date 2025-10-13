# Debugging Strategy for Solana Copy Bot Execution Pipeline

## Overview

This document outlines the comprehensive debugging strategy implemented across the Solana Copy Bot execution pipeline. The strategy ensures that every critical operation is logged with sufficient detail to pinpoint exact failure locations and reasons.

## Debugging Principles

1. **Granular Logging**: Log at every critical decision point
2. **Context Preservation**: Include all relevant parameters and state
3. **Error Transparency**: Log full stack traces for all exceptions
4. **Performance Tracking**: Log execution times for performance-critical operations
5. **Progressive Detail**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

## Logging Levels

- **DEBUG**: Detailed diagnostic information for troubleshooting
- **INFO**: General informational messages about execution flow
- **WARNING**: Potentially problematic situations that don't halt execution
- **ERROR**: Error events that might still allow execution to continue
- **CRITICAL**: Serious errors that may cause application failure

## Pipeline Stage Logging

### 1. Pipeline Entry (main.py)

**Entry Points Logged:**
- `_handle_websocket_trade()`: Log incoming trade info, missing fields, validation results
- `_process_detected_trade()`: Log execution path selection (balance vs instruction)
- `_simple_trade_analysis()`: Log analysis start, results, and completion

**Key Debugging Points:**
- Trade info structure and completeness
- Field inference attempts and results
- Validation pass/fail with reasons
- Execution path selection logic

### 2. Field Inference (trade_processor.py)

**Functions Logged:**
- `infer_missing_fields()`: Log each field inference attempt
- `_infer_signature_from_transaction()`: Log signature extraction methods
- `_infer_wallet_from_transaction()`: Log wallet identification
- `_infer_action_from_logs()`: Log action detection from transaction logs
- `_infer_dex_from_logs()`: Log DEX identification

**Key Debugging Points:**
- Which fields were missing
- Which fields were successfully inferred
- Data sources used for inference
- Fallback logic activation

### 3. Trade Validation (trade_processor.py)

**Functions Logged:**
- `validate_trade_info()`: Log validation criteria, results, and skip reasons
- Aggressive mode activation (if implemented)
- Field acceptance (inferred vs explicit)

**Key Debugging Points:**
- Validation criteria used
- Which fields passed/failed validation
- Whether trade was approved or rejected
- Reason for rejection (if applicable)

### 4. Executor Setup

#### Direct Copy Executor (mev_direct_copy_executor.py)
**Logged Operations:**
- Constructor initialization with config type validation
- PHANTOM_PRIVATE_KEY access and decoding
- Keypair creation and validation
- Config object structure and attributes
- Jito service availability check

#### Raydium Executor (mev_raydium_executor.py)
**Logged Operations:**
- Pubkey imports and usage
- PoolResolver instantiation with rpc and trade_info
- Pool resolution attempts and results
- Account creation and validation
- Swap instruction building

#### Jupiter Executor (mev_jupiter_executor.py)
**Logged Operations:**
- Token mint validation and sanitization
- Quote API requests and responses
- Swap API requests and responses
- ATA creation attempts
- Transaction serialization
- Slippage adjustment and retry logic

#### Meteora Executor (mev_meteora_executor.py)
**Logged Operations:**
- Pool detection and validation
- Token account setup
- Swap instruction preparation
- Transaction submission

### 5. Trade Execution (execution_coordinator.py)

**Functions Logged:**
- `_execute_copy_buy()`: Log executor selection, attempts, results
- `_execute_copy_sell()`: Log sell percentage calculation, executor selection
- `_try_single_executor_buy()`: Log timeout, errors, retries
- All executor method calls with parameters

**Key Debugging Points:**
- DEX routing logic and plan selection
- Executor attempt sequence
- Success/failure for each executor
- Final execution result

### 6. Error Handling

**All Executors Include:**
- Try-catch blocks around critical operations
- Full exception stack traces using `traceback.format_exc()`
- Error context (what operation failed, with what parameters)
- Recovery attempts (if applicable)
- Final error state

### 7. Summary and Output

**Logged at Pipeline Completion:**
- Total execution time
- Executors attempted
- Success/failure status
- Transaction signature (if successful)
- Error summary (if failed)
- Recommendations for retry (if applicable)

## Implementation Examples

### Example 1: Direct Copy Executor Setup Logging

```python
def __init__(self, private_key: str, config=None, jito_service=None):
    logger.info(f"[DIRECT_COPY] Initializing executor...")
    logger.debug(f"[DIRECT_COPY] Config type: {type(config)}")
    logger.debug(f"[DIRECT_COPY] Jito service available: {jito_service is not None}")
    
    try:
        self.config = config or MEVDirectCopyConfig()
        logger.debug(f"[DIRECT_COPY] Config attributes: {vars(self.config)}")
        
        logger.info(f"[DIRECT_COPY] Creating keypair from private key...")
        self.keypair = Keypair.from_base58_string(private_key)
        logger.info(f"[DIRECT_COPY] Keypair created successfully: {self.keypair.pubkey()}")
        
        self.jito_service = jito_service
        logger.info(f"[DIRECT_COPY] Executor initialized successfully")
    except Exception as e:
        logger.error(f"[DIRECT_COPY] Failed to initialize executor: {e}")
        logger.error(traceback.format_exc())
        raise
```

### Example 2: Jupiter API Request Logging

```python
def get_jupiter_quote(input_mint: str, output_mint: str, amount: int, slippage_bps: int):
    logger.info(f"[JUPITER] Requesting quote...")
    logger.debug(f"[JUPITER] Input mint: {input_mint}")
    logger.debug(f"[JUPITER] Output mint: {output_mint}")
    logger.debug(f"[JUPITER] Amount: {amount}")
    logger.debug(f"[JUPITER] Slippage BPS: {slippage_bps}")
    
    try:
        response = requests.get(QUOTE_URL, params={...})
        logger.debug(f"[JUPITER] API response status: {response.status_code}")
        logger.debug(f"[JUPITER] API response: {response.text[:500]}")
        
        data = response.json()
        logger.info(f"[JUPITER] Quote received successfully")
        return data
    except Exception as e:
        logger.error(f"[JUPITER] Quote request failed: {e}")
        logger.error(traceback.format_exc())
        return None
```

### Example 3: Validation Logging

```python
def validate_trade_info(self, trade: dict) -> bool:
    logger.info(f"[VALIDATION] Starting trade validation...")
    logger.debug(f"[VALIDATION] Trade keys: {list(trade.keys())}")
    
    sig = trade.get("signature")
    if sig and sig != "unknown":
        logger.info(f"[VALIDATION] ✅ Signature present: {sig[:12]}...")
        return True
    
    dex = trade.get("dex") or trade.get("dex_type")
    action = trade.get("action")
    mint = trade.get("mint") or trade.get("token_mint")
    
    logger.debug(f"[VALIDATION] DEX: {dex}, Action: {action}, Mint: {mint}")
    
    if not dex:
        logger.warning(f"[VALIDATION] ❌ Rejected: Missing DEX")
        return False
    
    if action not in {"buy", "sell", "swap", "swap_in", "swap_out"}:
        logger.warning(f"[VALIDATION] ❌ Rejected: Invalid action '{action}'")
        return False
    
    if not mint or mint in {"UNKNOWN", "PENDING_ANALYSIS"}:
        logger.warning(f"[VALIDATION] ❌ Rejected: Invalid mint '{mint}'")
        return False
    
    logger.info(f"[VALIDATION] ✅ Trade approved")
    return True
```

## Error Categories and Logging

### Configuration Errors
- Missing environment variables
- Invalid configuration values
- Type mismatches in config objects

### Data Errors
- Missing required fields
- Invalid field values
- Type conversion failures

### Network Errors
- RPC connection failures
- API request timeouts
- WebSocket disconnections

### Execution Errors
- Transaction simulation failures
- Transaction submission failures
- Insufficient balance errors

### Logic Errors
- Invalid routing decisions
- Incorrect executor selection
- Pool resolution failures

## Monitoring and Analysis

### Log File Organization
- Main execution log: All INFO and above
- Debug log: All DEBUG and above (separate file)
- Error log: All ERROR and CRITICAL (separate file)
- Trade analysis log: Specific to failed trades

### Key Metrics to Track
- Total trades detected
- Trades validated vs rejected
- Executors attempted per trade
- Success rate per executor
- Average execution time
- Common failure reasons

### Debug Session Workflow
1. Identify failing trade signature
2. Search logs for signature
3. Trace execution path through logs
4. Identify failure point
5. Examine parameters and state at failure
6. Determine root cause
7. Implement fix with additional logging if needed

## Maintenance Guidelines

1. **Add Logging for New Features**: Every new function should include entry/exit logging
2. **Log Parameter Changes**: When parameters affect execution, log before and after
3. **Preserve Historical Context**: Include relevant historical data in logs
4. **Regular Log Review**: Review logs weekly to identify patterns
5. **Update Strategy Document**: Keep this document updated as pipeline evolves

## Future Enhancements

- Structured logging with JSON format
- Distributed tracing for async operations
- Real-time monitoring dashboard
- Automated log analysis and alerting
- Performance profiling integration
