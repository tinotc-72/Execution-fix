#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_processor import TradeProcessor
from execution_coordinator import ExecutionCoordinator
from solana.rpc.async_api import AsyncClient

async def test_full_routing():
    """Test the full routing pipeline"""
    
    signature = "3fmwcJWcVoE7qtdFJSz9UQhpXjJohbGa3H79aqLzXhPHJhArxU2rBHZewmEKhdVD7ekSTcheABJzpov1iVgivAzi"
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    rpc_client = AsyncClient("https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
    
    try:
        # Test trade processor
        trade_processor = TradeProcessor(target_wallets=[wallet_address], rpc_client=rpc_client)
        trade_info = await trade_processor.analyze_trade_simple(signature, wallet_address)
        
        print("🔍 Trade Processor Result:")
        print(f"  - Token: {trade_info.get('token_mint', 'N/A')}")
        print(f"  - Action: {trade_info.get('action', 'N/A')}")
        print(f"  - DEX Type: {trade_info.get('dex_type', 'N/A')}")
        print(f"  - Analysis Method: {trade_info.get('analysis_method', 'N/A')}")
        
        # Test execution coordinator platform detection
        # Mock the required config and wallet for testing
        class MockConfig:
            def __init__(self):
                self.sol_per_trade = 0.001
                
        class MockWallet:
            def __init__(self):
                pass
                
        execution_coordinator = ExecutionCoordinator(MockConfig(), MockWallet())
        detected_platform = await execution_coordinator._detect_token_platform(
            trade_info.get('token_mint'), trade_info
        )
        
        print(f"\\n🎯 Execution Coordinator Platform Detection:")
        print(f"  - Detected Platform: {detected_platform}")
        
        if detected_platform == 'meteora_damm_v2':
            print("✅ SUCCESS: Will route to Meteora DAMM v2 (Raydium CPMM) executor!")
        else:
            print(f"❌ ISSUE: Expected 'meteora_damm_v2', got '{detected_platform}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await rpc_client.close()

if __name__ == "__main__":
    asyncio.run(test_full_routing())
