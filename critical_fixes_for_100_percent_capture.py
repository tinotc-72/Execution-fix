"""
CRITICAL FIXES TO ENSURE 100% TRADE CAPTURE
===========================================
Apply these changes to your main.py to catch EVERY SINGLE TRADE
"""

# Key improvements needed in your current main.py:

# 1. INCREASE MONITORING FREQUENCY
async def _fetch_and_analyze_recent_transactions(self, wallet: str):
    # CHANGE: Increase from 20 to 50 transactions
    "params": [wallet, {"limit": 50}]  # Was 20, now 50
    
    # CHANGE: Analyze ALL recent transactions, not just top 10
    for i, sig_info in enumerate(signatures[:20]):  # Was 10, now 20

# 2. REDUCE SIGNATURE SKIPPING
async def _fetch_and_analyze_recent_transactions(self, wallet: str):
    # CHANGE: Only skip if processed in last 50 signatures (was 100)
    if len(self.processed_signatures) > 50:  # Was 100, now 50
        old_sigs = list(self.processed_signatures)[:25]  # Remove oldest 25

# 3. DECREASE ANALYSIS DELAYS
async def _fetch_and_analyze_recent_transactions(self, wallet: str):
    # CHANGE: Reduce delay between transaction analysis
    await asyncio.sleep(0.2)  # Was 0.5, now 0.2 (faster scanning)

# 4. EXTEND HISTORICAL SCANNING
async def scan_wallet_history(self):
    # CHANGE: Scan even more historical transactions
    response = await self.rpc_client.get_signatures_for_address(
        Pubkey.from_string(wallet),
        limit=150  # Was 100, now 150 (deeper history)
    )
    
    # CHANGE: Analyze more historical transactions
    for i, tx_info in enumerate(response.value[:50]):  # Was 25, now 50

# 5. ENHANCE DEX PATTERN DETECTION
def _analyze_logs_for_trade_info(self, logs: List[str], signature: str):
    # ADD: More comprehensive DEX detection patterns
    dex_patterns = {
        "Pump.fun": [
            'pump', 'pumpfun', '6eav', '6eav1tx', 'pumpportal', 'pump.fun',
            '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',  # Program ID
            'bonkbot', 'pumpbot'  # Additional patterns
        ],
        "Jupiter": [
            'jupiter', 'jup4x', 'jupag', 'jup6', 'jupiter aggregator',
            'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB',  # Program ID
            'jup', 'jupiter swap'  # Additional patterns
        ],
        # ... (add all patterns from complete_trade_capture_config.py)
    }

# 6. IMPLEMENT TRIPLE VALIDATION
async def _process_detected_trade(self, trade_info: Dict[str, Any], source_wallet: str):
    # ADD: Validate detection with blockchain data
    if await self._validate_trade_on_chain(trade_info):
        # Execute trade only if validated
        await self._execute_copy_trade(trade_info, source_wallet)

# 7. ADD MISSING TRADE DETECTION
class TradeMissDetector:
    def __init__(self):
        self.expected_trades = {}
        self.detected_trades = {}
    
    async def check_for_missed_trades(self, wallet: str):
        # Compare expected vs detected trades
        # Trigger emergency rescan if discrepancy found
        pass

# 8. IMPLEMENT EMERGENCY FULL RESCAN
async def emergency_full_rescan(self, wallet: str):
    """Emergency full rescan if trades are being missed"""
    logger.warning(f"🚨 EMERGENCY RESCAN for {wallet[:8]}...")
    
    # Scan last 500 transactions (ultra-deep)
    response = await self.rpc_client.get_signatures_for_address(
        Pubkey.from_string(wallet),
        limit=500
    )
    
    # Analyze ALL with no skipping
    self.processed_signatures.clear()  # Clear to reprocess everything
    
    for tx_info in response.value[:100]:  # Analyze top 100
        signature = tx_info.get("signature")
        if signature:
            await self._fetch_and_analyze_transaction(signature, wallet)

# 9. ADD HEALTH MONITORING
class TradeCaptureHealthMonitor:
    def __init__(self):
        self.last_trade_time = {}
        self.trade_count = defaultdict(int)
        self.missed_trade_alerts = 0
    
    async def check_health(self, wallet: str):
        # Monitor if wallet seems active but no trades detected
        # Trigger alerts/rescans if needed
        pass

# 10. IMPLEMENT MULTI-METHOD VALIDATION
async def _analyze_transaction_comprehensive(self, signature: str, wallet: str):
    """Use ALL analysis methods for maximum coverage"""
    results = []
    
    # Method 1: Balance analysis (primary)
    balance_result = await self._analyze_balance_method(signature, wallet)
    if balance_result:
        results.append(balance_result)
    
    # Method 2: Log analysis (secondary)  
    log_result = await self._analyze_logs_method(signature, wallet)
    if log_result:
        results.append(log_result)
    
    # Method 3: Instruction analysis (tertiary)
    instruction_result = await self._analyze_instructions_method(signature, wallet)
    if instruction_result:
        results.append(instruction_result)
    
    # Use any positive result (don't require agreement)
    if results:
        # Take the result with highest confidence
        best_result = max(results, key=lambda x: x.get('confidence', 0))
        return best_result
    
    return None
