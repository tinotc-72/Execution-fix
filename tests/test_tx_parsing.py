"""
Unit test for transaction parsing/decoding (wallet_tx_parser)
"""
import unittest
from wallet_tx_parser import parse_transaction

class TestTxParsing(unittest.TestCase):
    def test_jupiter_swap_parsing(self):
        # Simulate Jupiter swap transaction
        tx = {'instructions': [{'program': 'Jupiter', 'data': 'swap'}]}
        result = parse_transaction(tx)
        self.assertIn('dex', result)
        self.assertEqual(result['dex'], 'Jupiter')

if __name__ == "__main__":
    unittest.main()
