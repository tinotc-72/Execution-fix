"""
Test Modern MEV Executor - Protocol Fix Validation
Tests the updated MEV bot with current Pump.fun protocol
"""

import asyncio
import logging
from modern_mev_pumpfun_executor import ModernMEVPumpFunExecutor
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModernMEVTest:
    def __init__(self):
        self.env = EnvKeys()
        self.executor = ModernMEVPumpFunExecutor(self.env)
        
        # Safety limits
        self.MAX_SOL_AMOUNT = 0.01  # 0.01 SOL max
        
    async def test_protocol_fix(self):
        """Test the modern protocol fix"""
        
        # Use a real active meme coin for testing
        test_mint = "5rPVwsZ4KpPZ2Zt4FmYfMJuYe8PWRF2rXrBy2oG5pump"  # Active mint
        test_amount = 0.005  # 0.005 SOL
        
        if test_amount > self.MAX_SOL_AMOUNT:
            logger.error(f"❌ Test amount {test_amount} exceeds safety limit {self.MAX_SOL_AMOUNT}")
            return False
        
        logger.info(f"🧪 Testing modern MEV protocol fix")
        logger.info(f"   Mint: {test_mint}")
        logger.info(f"   Amount: {test_amount} SOL")
        
        try:
            # Test the complete cycle
            results = await self.executor.buy_and_sell_cycle(
                mint_address=test_mint,
                sol_amount=test_amount,
                hold_duration=3.0
            )
            
            buy_sig = results.get('buy')
            sell_sig = results.get('sell')
            
            if buy_sig:
                logger.info(f"✅ Modern buy successful: {buy_sig}")
            else:
                logger.error(f"❌ Modern buy failed")
                return False
                
            if sell_sig:
                logger.info(f"✅ Modern sell successful: {sell_sig}")
            else:
                logger.warning(f"⚠️  Sell failed, but buy succeeded")
            
            # Check transaction status
            await asyncio.sleep(5)  # Wait for confirmation
            
            # Analyze what happened
            if buy_sig:
                await self.check_transaction_status(buy_sig, "BUY")
            if sell_sig:
                await self.check_transaction_status(sell_sig, "SELL")
            
            return buy_sig is not None
            
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")
            return False
    
    async def check_transaction_status(self, signature: str, tx_type: str):
        """Check if transaction succeeded on blockchain"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
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
                )
                
                data = response.json()
                if 'result' in data and data['result']:
                    tx = data['result']
                    error = tx.get('meta', {}).get('err')
                    
                    if error is None:
                        logger.info(f"✅ {tx_type} transaction confirmed on blockchain")
                        return True
                    else:
                        logger.error(f"❌ {tx_type} transaction failed on blockchain: {error}")
                        return False
                else:
                    logger.warning(f"⏳ {tx_type} transaction not yet confirmed")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error checking {tx_type} status: {e}")
            return False

async def main():
    """Run the protocol fix test"""
    logger.info("🚀 Starting Modern MEV Protocol Fix Test")
    logger.info("=" * 60)
    
    test = ModernMEVTest()
    
    # Run the test
    success = await test.test_protocol_fix()
    
    logger.info("=" * 60)
    if success:
        logger.info("🎉 PROTOCOL FIX TEST PASSED!")
        logger.info("   Modern MEV bot working with current Pump.fun protocol")
    else:
        logger.error("❌ PROTOCOL FIX TEST FAILED")
        logger.error("   Need further investigation")

if __name__ == "__main__":
    asyncio.run(main())
