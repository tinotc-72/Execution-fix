"""
Unit test for trade execution (execution_coordinator)
"""
import unittest
from execution_coordinator import ExecutionCoordinator
from solders.keypair import Keypair

class TestExecution(unittest.TestCase):
    def test_execute_copy_buy(self):
        wallet = Keypair.from_bytes(bytes([0]*64))  # Dummy wallet
        coordinator = ExecutionCoordinator(wallet)
        result = coordinator._execute_copy_buy('dummy_mint', 'dummy_wallet', trade_info={'parsed_tx': {'dex': 'Jupiter'}})
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)

if __name__ == "__main__":
    unittest.main()
