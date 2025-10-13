"""
Unit test for event detection (websocket_handler)
"""
import unittest
from websocket_handler import WebSocketHandler

class TestEventDetection(unittest.TestCase):
    def test_trade_event_detection(self):
        # Simulate a trade event payload
        payload = {
            'type': 'trade',
            'signature': 'dummy_signature',
            'wallet': 'dummy_wallet'
        }
        handler = WebSocketHandler()
        result = handler._detect_trade_event(payload)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
