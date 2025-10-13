"""
LIVE MEV EXECUTOR TEST - Real Blockchain Transactions
This will actually buy and sell tokens with real SOL to prove the executor works
"""

import asyncio
import logging
import time
from modern_mev_pumpfun_executor import ModernMEVPumpFunExecutor
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveMEVTest:
    def __init__(self):
        self.env = EnvKeys()
        self.executor = ModernMEVPumpFunExecutor(self.env)
        
        # Test parameters for REAL trading
        self.TEST_SOL_AMOUNT = 0.001  # 0.001 SOL as requested
        self.HOLD_DURATION = 5.0      # Hold for 5 seconds
        
    async def check_wallet_balance(self):
        """Check initial wallet balance"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [str(self.executor.wallet_address)]
                    }
                )
                
                data = response.json()
                if 'result' in data:
                    lamports = data['result']['value']
                    sol_balance = lamports / 1_000_000_000
                    logger.info(f"💰 Wallet balance: {sol_balance:.6f} SOL")
                    
                    if sol_balance < self.TEST_SOL_AMOUNT:
                        logger.error(f"❌ Insufficient balance! Need at least {self.TEST_SOL_AMOUNT} SOL")
                        return False
                    
                    return True
                
        except Exception as e:
            logger.error(f"❌ Error checking balance: {e}")
            return False
    
    async def wait_for_confirmation(self, signature: str, tx_type: str) -> bool:
        """Wait for transaction confirmation on blockchain"""
        import httpx
        
        logger.info(f"⏳ Waiting for {tx_type} confirmation: {signature}")
        
        for attempt in range(30):  # Wait up to 30 seconds
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
                            logger.info(f"✅ {tx_type} CONFIRMED on blockchain!")
                            logger.info(f"🔗 Explorer: https://solscan.io/tx/{signature}")
                            return True
                        else:
                            logger.error(f"❌ {tx_type} FAILED on blockchain: {error}")
                            return False
                    
            except Exception as e:
                logger.warning(f"⚠️  Error checking confirmation: {e}")
            
            await asyncio.sleep(1)
        
        logger.warning(f"⏰ {tx_type} confirmation timeout")
        return False
    
    async def get_token_balance_after_buy(self, mint_address: str) -> int:
        """Get token balance to confirm we received tokens"""
        try:
            accounts = self.executor.derive_pump_accounts(mint_address)
            balance = await self.executor.get_token_balance(accounts['user_token_account'])
            logger.info(f"🪙 Token balance: {balance:,} tokens")
            return balance
        except Exception as e:
            logger.error(f"❌ Error getting token balance: {e}")
            return 0
    
    async def execute_live_test(self, mint_address: str):
        """Execute REAL live trading test with blockchain confirmations"""
        
        logger.info("🎯 STARTING LIVE MEV EXECUTOR TEST")
        logger.info("=" * 60)
        logger.info(f"💎 Token: {mint_address}")
        logger.info(f"💰 Amount: {self.TEST_SOL_AMOUNT} SOL")
        logger.info(f"🔗 Wallet: {self.executor.wallet_address}")
        logger.info("🚨 THIS WILL USE REAL SOL FOR REAL TRADES!")
        logger.info("=" * 60)
        
        # Step 1: Check wallet balance
        if not await self.check_wallet_balance():
            return False
        
        # Step 2: Execute BUY
        logger.info("🚀 STEP 1: EXECUTING LIVE BUY...")
        buy_signature = await self.executor.execute_buy(mint_address, self.TEST_SOL_AMOUNT)
        
        if not buy_signature:
            logger.error("❌ BUY FAILED - No signature returned")
            return False
        
        logger.info(f"📤 BUY submitted: {buy_signature}")
        
        # Step 3: Wait for BUY confirmation
        buy_confirmed = await self.wait_for_confirmation(buy_signature, "BUY")
        
        if not buy_confirmed:
            logger.error("❌ BUY not confirmed on blockchain")
            return False
        
        # Step 4: Check we received tokens
        await asyncio.sleep(2)  # Brief pause
        token_balance = await self.get_token_balance_after_buy(mint_address)
        
        if token_balance == 0:
            logger.error("❌ No tokens received after buy")
            return False
        
        logger.info(f"✅ BUY SUCCESS: Received {token_balance:,} tokens!")
        
        # Step 5: Wait before selling
        logger.info(f"⏳ Holding tokens for {self.HOLD_DURATION} seconds...")
        await asyncio.sleep(self.HOLD_DURATION)
        
        # Step 6: Execute SELL
        logger.info("🚀 STEP 2: EXECUTING LIVE SELL...")
        sell_signature = await self.executor.execute_sell(mint_address, 100.0)  # Sell 100%
        
        if not sell_signature:
            logger.error("❌ SELL FAILED - No signature returned")
            return False
        
        logger.info(f"📤 SELL submitted: {sell_signature}")
        
        # Step 7: Wait for SELL confirmation
        sell_confirmed = await self.wait_for_confirmation(sell_signature, "SELL")
        
        if not sell_confirmed:
            logger.error("❌ SELL not confirmed on blockchain")
            return False
        
        logger.info("✅ SELL SUCCESS: Tokens sold!")
        
        # Step 8: Final verification
        await asyncio.sleep(2)
        final_token_balance = await self.get_token_balance_after_buy(mint_address)
        
        logger.info("=" * 60)
        logger.info("🎉 LIVE MEV EXECUTOR TEST COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"✅ BUY Transaction: {buy_signature}")
        logger.info(f"✅ SELL Transaction: {sell_signature}")
        logger.info(f"🔗 BUY Explorer: https://solscan.io/tx/{buy_signature}")
        logger.info(f"🔗 SELL Explorer: https://solscan.io/tx/{sell_signature}")
        logger.info(f"💰 Initial tokens: {token_balance:,}")
        logger.info(f"💰 Final tokens: {final_token_balance:,}")
        logger.info("🏆 MEV EXECUTOR PROVEN WORKING ON BLOCKCHAIN!")
        
        return True

async def main():
    """Run the live MEV executor test"""
    
    # Use an active meme coin for testing
    test_mint = "5rPVwsZ4KpPZ2Zt4FmYfMJuYe8PWRF2rXrBy2oG5pump"  # Active Pump.fun token
    
    test = LiveMEVTest()
    
    # Ask for confirmation before spending real SOL
    print("🚨 LIVE TRADING TEST CONFIRMATION")
    print("=" * 50)
    print(f"This will spend {test.TEST_SOL_AMOUNT} SOL for testing")
    print(f"Token: {test_mint}")
    print("This uses REAL money for REAL trades!")
    print("=" * 50)
    
    # Uncomment the line below if you want manual confirmation
    # confirmation = input("Type 'YES' to proceed with live test: ")
    # if confirmation != 'YES':
    #     print("❌ Test cancelled")
    #     return
    
    # Execute the live test
    success = await test.execute_live_test(test_mint)
    
    if success:
        print("\n🎊 SUCCESS: MEV EXECUTOR WORKS ON BLOCKCHAIN!")
        print("Your executor can now be used for profitable MEV trading!")
    else:
        print("\n❌ Test failed - needs investigation")

if __name__ == "__main__":
    asyncio.run(main())
