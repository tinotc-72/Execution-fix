    async def _detect_trading_platform(self, meta: Dict[str, Any], account_keys: List[str]) -> str:
        """Detect which trading platform was used"""
        
        # Check logs for platform signatures
        logs = meta.get('logMessages', [])
        
        # Pump.fun detection
        pump_fun_programs = [
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
        ]
        for log in logs:
            for pump_program in pump_fun_programs:
                if pump_program in log:
                    return "pumpfun"
        
        # Check account keys for DEX programs
        dex_programs = {
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "raydium_cpmm",
            "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "raydium_cpmm",  # Active Raydium CPMM program
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "orca",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "jupiter",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "raydium_v4"
        }
        
        for account in account_keys:
            if account in dex_programs:
                return dex_programs[account]
        
        return "unknown"
    
    async def _extract_token_from_tx_data(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract token mint from transaction data without needing wallet balance analysis"""
        try:
            # Try to get token from account keys - first key is often the token mint
            transaction = result.get('transaction', {})
            message = transaction.get('message', {})
            account_keys = message.get('accountKeys', [])
            
            # Token mint is often the first account key in Raydium/DEX transactions
            if account_keys:
                potential_token = account_keys[0]
                # Basic validation that it's not a program or system account
                if (len(potential_token) == 44 and  # Valid base58 length
                    not potential_token.startswith('11111') and  # Not system program
                    not potential_token.startswith('Token') and  # Not token program
                    not potential_token.startswith('Compute') and  # Not compute budget
                    not potential_token.startswith('So1111')):  # Not WSOL
                    return potential_token
            
            return None
        except Exception as e:
            logger.debug(f"Error extracting token from tx data: {e}")
            return None
    
    async def _pump_fun_log_based_fallback(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Extract real token from transaction logs as fallback"""
        try:
            logger.info(f"   🎯 EXTRACTING REAL TOKEN from transaction: {signature[:8]}...")
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            # Handle both string URLs and AsyncClient objects
            if self.env_keys and self.env_keys.HELIUS_RPC_URL:
                rpc_url = self.env_keys.HELIUS_RPC_URL
            elif isinstance(self.rpc_client, str):
                rpc_url = self.rpc_client
            else:
                rpc_url = self.rpc_client._provider.endpoint_uri
            
            async with aiohttp.ClientSession() as session:
                async with session.post(rpc_url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('result') and data['result'].get('transaction'):
                            tx = data['result']['transaction']
                            
                            # Extract token mint from transaction instructions
                            real_token_mint = self._extract_real_token_mint(tx)
                            
                            if real_token_mint and len(real_token_mint) == 44:
                                logger.info(f"   ✅ REAL TOKEN EXTRACTED: {real_token_mint[:8]}...")
                                
                                return {
                                    'action': 'buy',
                                    'confidence': "HIGH",
                                    'reasoning': f"Real token extracted from transaction",
                                    'signature': signature,
                                    'wallet': wallet_address,
                                    'token_mint': real_token_mint,
                                    'timestamp': time.time(),
                                    'method': 'real_token_extraction',
                                    'dex': 'extracted_from_tx'
                                }
            
            logger.warning(f"   ⚠️ Could not extract real token mint")
            return None
                    
        except Exception as e:
            logger.error(f"   ❌ Error in real token extraction: {e}")
            return None
    
    def _extract_real_token_mint(self, transaction: dict) -> Optional[str]:
        """Extract the actual token mint from transaction data"""
        try:
            system_programs = {
                "11111111111111111111111111111111",
                "ComputeBudget111111111111111111111111111111",
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
            }
            candidates = set()
            # 1. Scan all accountKeys for 44-char keys not in system programs
            accounts = []
            if 'message' in transaction and 'accountKeys' in transaction['message']:
                accounts = transaction['message']['accountKeys']
            for account in accounts:
                account_key = account if isinstance(account, str) else account.get('pubkey', '')
                if (
                    len(account_key) == 44 and
                    account_key not in system_programs and
                    not account_key.startswith('So1111')
                ):
                    logger.info(f"   🎯 Candidate token mint from accountKeys: {account_key}")
                    candidates.add(account_key)

            # 2. Scan meta.postTokenBalances for mint
            meta = transaction.get('meta', {})
            if 'postTokenBalances' in meta:
                for bal in meta['postTokenBalances']:
                    mint = bal.get('mint')
                    if mint and len(mint) == 44 and not mint.startswith('So1111'):
                        logger.info(f"   🎯 Candidate token mint from postTokenBalances: {mint}")
                        candidates.add(mint)

            # 3. Scan all instruction accounts for 44-char keys
            if 'meta' in transaction and 'innerInstructions' in transaction['meta']:
                for ix in transaction['meta']['innerInstructions']:
                    for inst in ix.get('instructions', []):
                        for acct in inst.get('accounts', []):
                            if len(acct) == 44 and not acct.startswith('So1111'):
                                logger.info(f"   🎯 Candidate token mint from inner instruction: {acct}")
                                candidates.add(acct)

            # 4. Parse all log messages for any 44-char base58 string
            import re
            if 'meta' in transaction and 'logMessages' in transaction['meta']:
                logs = transaction['meta']['logMessages']
                for log in logs:
                    for candidate in re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{44}\b', log):
                        if candidate not in system_programs and not candidate.startswith('So1111'):
                            logger.info(f"   🎯 Candidate token mint from log: {candidate}")
                            candidates.add(candidate)

            # 5. Fallback: scan all 44-char strings in transaction for possible mints
            tx_str = str(transaction)
            for candidate in re.findall(r'\b[1-9A-HJ-NP-Za-km-z]{44}\b', tx_str):
                if candidate not in system_programs and not candidate.startswith('So1111'):
                    logger.info(f"   🎯 Candidate token mint from transaction string: {candidate}")
                    candidates.add(candidate)

            if candidates:
                logger.info(f"✅ Meme coin mint candidates found: {list(candidates)}")
                # Prefer candidates found in postTokenBalances, then accountKeys, then logs
                for bal in meta.get('postTokenBalances', []):
                    mint = bal.get('mint')
                    if mint in candidates:
                        return mint
                # Otherwise, just return the first candidate
                return next(iter(candidates))

            logger.error("   ❌ Could not extract token mint from transaction after all methods.")
            return None
        except Exception as e:
            logger.error(f"   ❌ Error extracting token mint: {e}")
            return None
    
    async def _create_emergency_trade_result(self, signature: str, wallet_address: str) -> Dict[str, Any]:
        """Create emergency trade result when analysis fails"""
        logger.error(f"   ❌ EMERGENCY FAILURE: Cannot analyze transaction {signature[:8]}... - SKIPPING!")
        logger.error(f"   ❌ This prevents false buy/sell assumptions that lead to failed trades")
        
        # DON'T make emergency assumptions - return None to skip the trade
        return None
    
    async def reanalyze_transaction_with_balance_data(self, signature: str, wallet_address: str, 
                                                    detected_action: str) -> Optional[Dict[str, Any]]:
        """Re-analyze transaction using balance data with retry logic"""
        
        max_retries = 5
        retry_delays = [0.5, 1.0, 2.0, 3.0, 5.0]
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 RETRY {attempt+1}/{max_retries}: Waiting {retry_delays[attempt]:.1f}s...")
                    await asyncio.sleep(retry_delays[attempt])
                
                logger.info(f"🔧 BALANCE RE-ANALYSIS (attempt {attempt+1}): {signature[:8]}...")
                
                # Use the official analyzer if available
                try:
                    from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
                    analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
                    result = await analyzer.analyze_wallet_action(signature, wallet_address)
                    
                    if result and result.get('action') not in ['none', 'error']:
                        logger.info(f"✅ OFFICIAL RE-ANALYSIS SUCCESS! (attempt {attempt+1})")
                        logger.info(f"   🎯 Action: {result['action'].upper()}")
                        logger.info(f"   💎 Token: {result.get('token_mint', 'Unknown')[:8]}...")
                        
                        return {
                            'signature': signature,
                            'wallet_address': wallet_address,
                            'action': result['action'],
                            'dex': 'Official_Balance_Re_Analysis',
                            'token_mint': result['token_mint'],
                            'timestamp': datetime.now(timezone.utc),
                            'extraction_method': 'official_solana_balance_re_analysis',
                            'balance_change': result.get('amount_change', 0),
                            'confidence': result.get('confidence', 10)
                        }
                    else:
                        if result:
                            logger.warning(f"❌ RE-ANALYSIS (attempt {attempt+1}): {result.get('action', 'unknown')}")
                        continue
                        
                except ImportError:
                    # Fallback to our own analysis
                    result = await self.analyze_transaction_with_balance_detection(signature, wallet_address)
                    if result:
                        return result
                    continue
                        
            except Exception as e:
                logger.error(f"❌ Error in balance re-analysis (attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    continue
        
        logger.error(f"🚨 ALL RETRIES EXHAUSTED: Could not re-analyze {signature[:8]}...")
        return None


# Factory function for easy creation
def create_transaction_analyzer(rpc_client: AsyncClient, env_keys=None) -> TransactionAnalyzer:
    """Create a transaction analyzer instance"""
    return TransactionAnalyzer(rpc_client=rpc_client, env_keys=env_keys)
