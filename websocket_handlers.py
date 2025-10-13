    async def handle_logs_notification(self, result: Dict[str, Any]):
        """Handle transaction logs notifications with AGGRESSIVE instant detection"""
        try:
            value = result.get("value", {})
            signature = value.get("signature", "")
            logs = value.get("logs", [])
            error = value.get("err")
            
            if error:
                return
            
            # 🚀 CRITICAL FIX: Don't check logs for wallet addresses - they're NEVER there!
            # Instead, analyze EVERY transaction that involves DEX activity
            if not logs:
                return
            
            log_text = ' '.join(logs).lower()
            
            # 🚀 ULTRA-AGGRESSIVE: Detect ANY DEX activity and analyze it
            dex_activity = False
            dex_detected = None
            
            # Enhanced DEX detection patterns
            if any(pattern in log_text for pattern in ['jupiter', 'jup aggregator', 'route plan']):
                dex_detected = "Jupiter"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['raydium', 'cpmm', 'clmm', 'amm']):
                dex_detected = "Raydium"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['pump.fun', 'pumpfun', 'bonding curve']):
                dex_detected = "Pump.fun"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['orca', 'whirlpool']):
                dex_detected = "Orca"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['phoenix', 'meteora', 'lifinity']):
                dex_detected = dex_detected or "DEX"
                dex_activity = True
            elif any(pattern in log_text for pattern in ['swap', 'exchange', 'trade']):
                dex_detected = "Unknown DEX"
                dex_activity = True
            
            # 🚀 CRITICAL FIX: If ANY DEX activity detected, analyze the transaction
            if dex_activity:
                logger.info(f"⚡ INSTANT DEX DETECTION: {signature[:8]}... on {dex_detected}")
                logger.info(f"🔥 AGGRESSIVE MODE: Analyzing transaction for target wallet involvement...")
                
                # Immediately analyze the transaction to see if it involves our target wallets
                asyncio.create_task(self.analyze_transaction_aggressive(signature, dex_detected))
            
        except Exception as e:
            logger.error(f"❌ Error in aggressive logs handling: {e}")
    
    async def analyze_transaction_aggressive(self, signature: str, detected_dex: str):
        """AGGRESSIVE transaction analysis - analyzes EVERY DEX transaction for target wallet involvement"""
        try:
            logger.info(f"🔥 AGGRESSIVE ANALYSIS: {signature[:8]}... on {detected_dex}")
            
            # Get transaction details immediately
            tx_response = await self.rpc_client.get_transaction(
                signature=signature,
                max_supported_transaction_version=0,
                encoding="json"
            )
            
            if not tx_response or not tx_response.value:
                logger.debug(f"❌ Transaction not found: {signature[:8]}...")
                return
            
            tx = tx_response.value
            meta = tx.meta
            
            if meta.err:
                return  # Skip failed transactions
            
            # 🚀 CRITICAL: Check if ANY of our target wallets are involved
            account_keys = tx.transaction.message.account_keys
            involved_wallets = []
            
            for wallet in self.config.target_wallets:
                if wallet in [str(key) for key in account_keys]:
                    involved_wallets.append(wallet)
            
            if not involved_wallets:
                return  # None of our target wallets involved
            
            # 🚀 SUCCESS: Target wallet found in transaction!
            for target_wallet in involved_wallets:
                logger.info(f"🎯 TARGET WALLET FOUND: {target_wallet[:8]}... in {signature[:8]}...")
                
                # Immediately analyze the trade
                trade_info = await self.extract_trade_info_quick(signature, target_wallet)
                
                if trade_info:
                    logger.info(f"✅ TRADE EXTRACTED: {trade_info['type'].upper()} {trade_info['token_mint'][:8]}...")
                    
                    # 🚀 EXECUTE IMMEDIATELY
                    await self.execute_copy_trade(trade_info, target_wallet)
                else:
                    # Fallback to full analysis
                    logger.info(f"🔄 Quick analysis failed, using full analysis...")
                    await self.analyze_transaction(signature, target_wallet)
            
        except Exception as e:
            logger.error(f"❌ Error in aggressive transaction analysis: {e}")
    
    async def handle_account_notification(self, result: Dict[str, Any]):
        """Handle account balance change notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            lamports = value.get("lamports", 0)
            sol_balance = lamports / 1e9
            
            logger.info(f"💰 ACCOUNT: Balance change detected at slot {slot}")
            logger.info(f"   💎 New SOL balance: {sol_balance:.6f} SOL")
            
            # Balance changes are strong indicators of trading activity
            logger.info(f"🔥 STRONG SIGNAL: Account balance changed - likely trade!")
            
            # Get recent transaction to analyze
            # Immediately check for the transaction that caused this balance change
            for wallet in self.config.target_wallets:
                await self.check_recent_transactions_for_wallet(wallet)
            
        except Exception as e:
            logger.error(f"❌ Error handling account notification: {e}")
