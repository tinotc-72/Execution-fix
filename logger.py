# logger.py

import csv
import os
from datetime import datetime
import logging

def start_logging(logfile="bot.log"):
    logging.basicConfig(
        filename=logfile,
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logging.info("Logging started.")

# File to log mirrored trades
LOG_FILE = "mirrored_trades.csv"

# Initialize CSV if not exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Mint", "Curve", "Amount", "Status"])

# === Log each mirrored trade ===
def log_mirrored_trade(mint: str, curve: str, amount: float, status: str):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, mint, curve, amount, status])

# === Simple Performance Tracker ===
class PerformanceTracker:
    def __init__(self):
        self.trades_seen = 0
        self.trades_mirrored = 0
        self.successful_mirrors = 0
        self.latencies_ms = []

    def report_seen(self):
        self.trades_seen += 1

    def report_mirrored(self):
        self.trades_mirrored += 1

    def report_success(self, latency_ms):
        self.successful_mirrors += 1
        self.latencies_ms.append(latency_ms)

    def show_stats(self):
        avg_latency = sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0
        print("\n📊 Performance Tracker")
        print(f"  Wallet A trades seen   : {self.trades_seen}")
        print(f"  Trades mirrored        : {self.trades_mirrored}")
        print(f"  Successful mirrors     : {self.successful_mirrors}")
        print(f"  Avg Mirror Latency (ms): {avg_latency:.2f}")
