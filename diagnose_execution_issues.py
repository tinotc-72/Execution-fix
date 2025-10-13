#!/usr/bin/env python3

import asyncio
import logging
import sys
import traceback
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('execution_diagnosis.log')
    ]
)
logger = logging.getLogger(__name__)

async def diagnose_execution_pipeline():
    """
    Comprehensive diagnosis of the execution pipeline
    """
    
    print("🔍 COPY BOT EXECUTION DIAGNOSIS")
    print("=" * 60)
    
    try:
        # Test 1: Import and Initialize Key Components
        print("\n🧪 TEST 1: Component Initialization")
        print("-" * 40)
        
        try:
            from execution_coordinator import ExecutionCoordinator
            print("✅ ExecutionCoordinator import: SUCCESS")
        except Exception as e:
            print(f"❌ ExecutionCoordinator import: FAILED - {e}")
            return False
        
        try:
            from trade_processor import TradeProcessor
            print("✅ TradeProcessor import: SUCCESS")
        except Exception as e:
            print(f"❌ TradeProcessor import: FAILED - {e}")
            return False
        
        try:
            from websocket_handler import WebSocketHandler
            print("✅ WebSocketHandler import: SUCCESS")
        except Exception as e:
            print(f"❌ WebSocketHandler import: FAILED - {e}")
            return False
        
        # Test 2: Configuration and Environment
        print("\n🧪 TEST 2: Configuration Check")
        print("-" * 40)
        
        try:
            from env_keys import EnvKeys
            env = EnvKeys()
            print("✅ Environment keys loaded")
            
            # Check critical keys
            if hasattr(env, 'PHANTOM_PRIVATE_KEY') and env.PHANTOM_PRIVATE_KEY:
                print("✅ PHANTOM_PRIVATE_KEY: Present")
            else:
                print("❌ PHANTOM_PRIVATE_KEY: Missing or empty")
                
            if hasattr(env, 'HELIUS_API_KEY') and env.HELIUS_API_KEY:
                print("✅ HELIUS_API_KEY: Present")
            else:
                print("❌ HELIUS_API_KEY: Missing or empty")
                
        except Exception as e:
            print(f"❌ Environment check: FAILED - {e}")
            return False
        
        # Test 3: Executor Availability
        print("\n🧪 TEST 3: Executor Availability")
        print("-" * 40)
        
        try:
            from mev_pumpfun_executor import try_pumpfun_buy
            print("✅ Pump.fun executor: Available")
        except Exception as e:
            print(f"⚠️ Pump.fun executor: {e}")
        
        try:
            from jupiter_copy_executor import execute_jupiter_buy_copy
            print("✅ Jupiter executor: Available")
        except Exception as e:
            print(f"⚠️ Jupiter executor: {e}")
        
        # Test 4: Live Bot Integration Test
        print("\n🧪 TEST 4: Live Bot Integration")
        print("-" * 40)
        
        try:
            # Import main components
            import main
            print("✅ Main module import: SUCCESS")
            
            # Check if main has required functions
            if hasattr(main, 'setup_copy_trading_bot'):
                print("✅ setup_copy_trading_bot: Available")
            else:
                print("⚠️ setup_copy_trading_bot: Not found")
                
            if hasattr(main, '_process_detected_trade'):
                print("✅ _process_detected_trade: Available")
            else:
                print("⚠️ _process_detected_trade: Not found")
                
        except Exception as e:
            print(f"❌ Main module check: FAILED - {e}")
        
        # Test 5: Wallet and RPC Connection
        print("\n🧪 TEST 5: Connection Tests")
        print("-" * 40)
        
        try:
            from solders.keypair import Keypair
            from solders.pubkey import Pubkey
            import httpx
            
            # Test wallet creation
            private_key = env.PHANTOM_PRIVATE_KEY
            if private_key:
                try:
                    wallet = Keypair.from_base58_string(private_key)
                    print(f"✅ Wallet creation: SUCCESS - {wallet.pubkey()}")
                except:
                    try:
                        wallet_bytes = bytes.fromhex(private_key)
                        wallet = Keypair.from_bytes(wallet_bytes)
                        print(f"✅ Wallet creation (hex): SUCCESS - {wallet.pubkey()}")
                    except Exception as wallet_error:
                        print(f"❌ Wallet creation: FAILED - {wallet_error}")
                        return False
            
            # Test RPC connection
            helius_url = f"https://mainnet.helius-rpc.com/?api-key={env.HELIUS_API_KEY}"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(helius_url, json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getHealth"
                    }, timeout=10)
                    
                    if response.status_code == 200:
                        print("✅ RPC Connection: SUCCESS")
                    else:
                        print(f"⚠️ RPC Connection: HTTP {response.status_code}")
                        
                except Exception as rpc_error:
                    print(f"❌ RPC Connection: FAILED - {rpc_error}")
                    
        except Exception as e:
            print(f"❌ Connection tests: FAILED - {e}")
        
        # Test 6: Token Analysis Pipeline
        print("\n🧪 TEST 6: Token Analysis Pipeline")
        print("-" * 40)
        
        try:
            import httpx
            processor = TradeProcessor(httpx.AsyncClient())
            
            # Test with a known transaction signature
            test_signature = "3AjZkK3tKdXr8ujjgPs9hAcP1LHjRNuyD6phme2M8EfQkHtZNoxaPJv47cZqArWwKX6mheXQcGgXywdXsQi1P1n4"
            test_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
            
            print(f"Testing token extraction with signature: {test_signature[:12]}...")
            
            result = await processor.extract_token_info_fast(test_signature, test_wallet)
            
            if result:
                print(f"✅ Token extraction: SUCCESS")
                print(f"   Token mint: {result.get('token_mint', 'Not found')}")
                print(f"   Action: {result.get('action', 'Not found')}")
                print(f"   Confidence: {result.get('confidence', 'Not found')}")
            else:
                print("⚠️ Token extraction: No result returned")
                
        except Exception as e:
            print(f"❌ Token analysis: FAILED - {e}")
            traceback.print_exc()
        
        # Test 7: Execution Path Simulation
        print("\n🧪 TEST 7: Execution Path Simulation")
        print("-" * 40)
        
        try:
            # Create mock trade info similar to what would come from websocket
            mock_trade_info = {
                'signature': test_signature,
                'wallet_address': test_wallet,
                'timestamp': datetime.now(),
                'detection_method': 'test',
                'requires_analysis': True,
                'basic_analysis': {
                    'likely_action': 'buy',
                    'confidence': 'medium',
                    'detected_dex': 'unknown'
                }
            }
            
            print("Simulating trade processing pipeline...")
            
            # Test trade processor analysis
            analysis_result = await processor.analyze_and_route_trade(mock_trade_info)
            
            if analysis_result:
                print(f"✅ Trade analysis: SUCCESS")
                print(f"   Requires execution: {analysis_result.get('requires_execution', False)}")
                print(f"   Token mint: {analysis_result.get('token_mint', 'Not found')}")
                print(f"   Action: {analysis_result.get('action', 'Not found')}")
                print(f"   Method: {analysis_result.get('method', 'Not found')}")
                
                # Check if execution would be triggered
                if analysis_result.get('requires_execution'):
                    print("✅ Trade would be sent for execution")
                else:
                    print("❌ Trade would NOT be executed")
                    print(f"   Reason: {analysis_result.get('error', 'Unknown')}")
            else:
                print("❌ Trade analysis: No result")
                
        except Exception as e:
            print(f"❌ Execution simulation: FAILED - {e}")
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("🏁 DIAGNOSIS COMPLETE")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Diagnosis failed with exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🚀 Starting execution diagnosis at {datetime.now()}")
    
    success = asyncio.run(diagnose_execution_pipeline())
    
    if success:
        print("\n✅ Diagnosis completed successfully")
        print("📋 Check execution_diagnosis.log for detailed logs")
    else:
        print("\n❌ Diagnosis encountered critical errors")
        print("📋 Check execution_diagnosis.log and traceback above")