#!/usr/bin/env python3
"""
Quick test to verify DEX executors are importable and working
"""

def test_executor_imports():
    """Test if all executor functions can be imported"""
    try:
        print("🔍 Testing DEX executor imports...")
        
        # Test Jupiter executor
        try:
            from jupiter_copy_executor import try_jupiter_buy, try_jupiter_sell_all
            print("✅ Jupiter executor imported successfully")
        except Exception as e:
            print(f"❌ Jupiter executor import failed: {e}")
        
        # Test Pump.fun executor
        try:
            from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all
            print("✅ Pump.fun executor imported successfully")
        except Exception as e:
            print(f"❌ Pump.fun executor import failed: {e}")
        
        # Test Raydium executor
        try:
            from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
            print("✅ Raydium executor imported successfully")
        except Exception as e:
            print(f"❌ Raydium executor import failed: {e}")
        
        # Test CPMM executor
        try:
            from cpmm_copy_executor import try_cpmm_buy, try_cpmm_sell_all
            print("✅ CPMM executor imported successfully")
        except Exception as e:
            print(f"❌ CPMM executor import failed: {e}")
        
        # Test CLMM executor
        try:
            from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
            print("✅ CLMM executor imported successfully")
        except Exception as e:
            print(f"❌ CLMM executor import failed: {e}")
        
        # Test Orca executor
        try:
            from orca_copy_executor import try_orca_buy, try_orca_sell_all
            print("✅ Orca executor imported successfully")
        except Exception as e:
            print(f"❌ Orca executor import failed: {e}")
        
        # Test Phoenix executor  
        try:
            from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all
            print("✅ Phoenix executor imported successfully")
        except Exception as e:
            print(f"❌ Phoenix executor import failed: {e}")
        
        print("🎯 Import test completed!")
        
    except Exception as e:
        print(f"❌ Overall test failed: {e}")

if __name__ == "__main__":
    test_executor_imports()
