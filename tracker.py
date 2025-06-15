# tracker.py

import time
from config import WALLET


class MirrorStats:
    def __init__(self):
        self.total_wallet_a_trades = 0
        self.total_mirrored = 0
        self.total_success = 0
        self.total_latency_ms = 0

    def wallet_a_trade_seen(self):
        self.total_wallet_a_trades += 1

    def mirrored_trade(self, success, latency_ms):
        self.total_mirrored += 1
        if success:
            self.total_success += 1
        self.total_latency_ms += latency_ms

    def print_summary(self):
        avg_latency = (
            self.total_latency_ms / self.total_mirrored
            if self.total_mirrored else 0
        )
        print("\n📊 Performance Tracker")
        print(f"  Wallet A trades seen   : {self.total_wallet_a_trades}")
        print(f"  Trades mirrored        : {self.total_mirrored}")
        print(f"  Successful mirrors     : {self.total_success}")
        print(f"  Avg Mirror Latency (ms): {avg_latency:.2f}")
