#!/usr/bin/env python3
"""
🧪 TEST ENHANCED DEX DETECTION
Test the improved program ID-based DEX detection system
"""

import asyncio
import logging
from typing import Dict, Any
from websocket_handler import WebSocketHandler, WebSocketConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDetection:
    """Test enhanced DEX detection logic"""
    
    def __init__(self):
        self.handler = None
    
    def setup_handler(self):
        """Setup a minimal websocket handler for testing"""
        config = WebSocketConfig(
            target_wallets=["test"],
            helius_ws_url="wss://test",
            helius_rpc_url="https://test"
        )
        self.handler = WebSocketHandler(config, self._dummy_callback)
    
    async def _dummy_callback(self, trade_info: Dict[str, Any]):
        """Dummy callback for testing"""
        pass
    
    def test_program_id_detection(self):
        """Test program ID based detection vs text pattern detection"""
        
        test_cases = [
            {
                'name': 'Raydium CPMM Transaction (Real)',
                'logs': [
                    'Program cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG invoke [1]',
                    'Program log: Instruction: Swap',
                    'Some other logs here'
                ],
                'expected_dex': 'raydium_cpmm',
                'expected_confidence': 'high',
                'expected_method': 'program_id'
            },
            {
                'name': 'Pump.fun Transaction (New Program ID)',
                'logs': [
                    'Program pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA invoke [1]',
                    'Program log: Instruction: Buy',
                    'Some other logs here'
                ],
                'expected_dex': 'pumpfun',
                'expected_confidence': 'high',
                'expected_method': 'program_id'
            },
            {
                'name': 'Jupiter Transaction',
                'logs': [
                    'Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]',
                    'Program log: Instruction: Route',
                    'Some other logs here'
                ],
                'expected_dex': 'jupiter',
                'expected_confidence': 'high',
                'expected_method': 'program_id'
            },
            {
                'name': 'Text Pattern Only (No Program ID)',
                'logs': [
                    'Program someRandomProgram invoke [1]',
                    'Program log: pump.fun buy instruction',
                    'Some other logs here'
                ],
                'expected_dex': 'pumpfun',
                'expected_confidence': 'medium',
                'expected_method': 'text_pattern'
            },
            {
                'name': 'Unknown Transaction',
                'logs': [
                    'Program unknownProgram invoke [1]',
                    'Program log: Unknown instruction',
                    'Some other logs here'
                ],
                'expected_dex': 'unknown',
                'expected_confidence': 'low',
                'expected_method': 'text_pattern'
            },
            {
                'name': 'Mixed Case - Program ID Wins',
                'logs': [
                    'Program cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG invoke [1]',
                    'Program log: jupiter swap instruction',  # Text suggests Jupiter
                    'Some other logs here'
                ],
                'expected_dex': 'raydium_cpmm',  # Program ID should win
                'expected_confidence': 'high',
                'expected_method': 'program_id'
            }
        ]
        
        self.setup_handler()
        
        print("🧪 Testing Enhanced DEX Detection System")
        print("=" * 60)
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print("-" * 50)
            
            # Run the analysis
            analysis = self.handler._basic_trade_analysis(test_case['logs'])
            
            # Check results
            detected_dex = analysis.get('detected_dex', 'unknown')
            detection_confidence = analysis.get('detection_confidence', 'low')
            detection_method = analysis.get('detection_method', 'text_pattern')
            
            print(f"📊 Results:")
            print(f"   • DEX: {detected_dex} (expected: {test_case['expected_dex']})")
            print(f"   • Confidence: {detection_confidence} (expected: {test_case['expected_confidence']})")
            print(f"   • Method: {detection_method} (expected: {test_case['expected_method']})")
            
            # Validate
            test_passed = (
                detected_dex == test_case['expected_dex'] and
                detection_confidence == test_case['expected_confidence'] and
                detection_method == test_case['expected_method']
            )
            
            if test_passed:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
                all_passed = False
            
            print(f"📝 Full Analysis: {analysis}")
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL TESTS PASSED! Enhanced DEX detection is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logic above.")
        
        return all_passed

def main():
    """Run the tests"""
    tester = TestDetection()
    success = tester.test_program_id_detection()
    
    print(f"\n🎯 Test Summary: {'SUCCESS' if success else 'FAILURE'}")
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
