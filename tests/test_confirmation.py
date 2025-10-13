"""
Unit test for confirmation and retry logic (execution_coordinator)
"""
import unittest
from execution_coordinator import ExecutionCoordinator
from solders.keypair import Keypair

class TestConfirmation(unittest.TestCase):
    def test_confirm_transaction(self):
        wallet = Keypair.from_bytes(bytes([0]*64))
        coordinator = ExecutionCoordinator(wallet)
        # Simulate confirmation (should handle gracefully)
        result = coordinator._confirm_transaction('dummy_signature')
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
