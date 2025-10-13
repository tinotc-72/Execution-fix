import asyncio
from wallet_tx_parser import WalletTransactionParser
from execution_coordinator import ExecutionCoordinator
from solders.keypair import Keypair

# Real Pump.fun transaction for testing
test_signature = "5cUKAb9cTwKxktLfP8FqM9bBjEwT7F6bbqESshhJ46jBtiDwwHBA9bhZau6Ci1G8uvsGZvQzut5Ux4rQ2BRR6Jdu"
test_source_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"  # Real wallet from the transaction
test_token_mint = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"  # Real token mint from the transaction

# Simulate a parsed transaction (mocked)
mock_tx_data = {
    "signature": test_signature,
    "source_wallet": test_source_wallet,
    "token_mint": test_token_mint,
    "amount": 1000000,
    "action": "buy",
    # For direct copy, only signature is required; instructions are fetched from chain
}

async def simulate_trade_detection_and_execution():
    print("[SIMULATION] Starting trade detection simulation...")
    # Step 1: Parse transaction (mocked)
    parser = WalletTransactionParser(rpc_client=None)
    parsed_tx = parser.parse_transaction(mock_tx_data)
    print(f"[SIMULATION] Parsed transaction: {parsed_tx}")

    # Manually set action and token_mint for simulation
    parsed_tx['action'] = 'buy'
    parsed_tx['token_mint'] = mock_tx_data['token_mint']
    parsed_tx['source_wallet'] = mock_tx_data['source_wallet']

    # Force detected_dex to 'pumpfun' for this test
    detected_dex = 'pumpfun'
    print(f"[SIMULATION] DEX detected: {detected_dex}")
    print(f"[SIMULATION] Action: {parsed_tx.get('action')}")

    # Step 3: Simulate execution coordinator logic
    mock_wallet = Keypair()
    coordinator = ExecutionCoordinator(wallet=mock_wallet)
    if parsed_tx.get('action') == 'buy':
        print("[SIMULATION] Simulating copy BUY execution...")
        # Ensure trade_info includes the signature
        trade_info = dict(parsed_tx)
        trade_info['signature'] = mock_tx_data['signature']
        result = await coordinator._execute_copy_buy(
            token_mint=trade_info['token_mint'],
            source_wallet=trade_info['source_wallet'],
            trade_info=trade_info,
            detected_dex=detected_dex,
            routing_instructions=None
        )
    elif parsed_tx.get('action') == 'sell':
        print("[SIMULATION] Simulating copy SELL execution...")
        result = await coordinator._execute_copy_sell(
            token_mint=parsed_tx['token_mint'],
            trade_info=parsed_tx,
            source_wallet=parsed_tx['source_wallet'],
            detected_dex=detected_dex
        )
    else:
        print("[SIMULATION] Unknown action, skipping execution.")
        result = None

    print(f"[SIMULATION] Execution result: {result}")
    print("[SIMULATION] Trade detection and execution simulation complete.")

if __name__ == "__main__":
    asyncio.run(simulate_trade_detection_and_execution())
