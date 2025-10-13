import asyncio
import logging
from wallet_tx_parser import parse_transaction
from execution_coordinator import ExecutionCoordinator

# Step 1: Simulate WebSocket event detection (mock event)
def mock_websocket_event():
    print("[TEST] Simulating WebSocket event detection...")
    # This would be a real event in production
    return {
        "signature": "5N1QwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1v",
        "source_wallet": "7GkQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1v"
    }

# Step 2: Simulate fetching full transaction (mock RPC)
def mock_fetch_full_transaction(signature):
    print(f"[TEST] Simulating full transaction fetch for signature: {signature}")
    # This would be a real RPC call in production
    return {
        "signature": signature,
        "source_wallet": "7GkQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1v",
        "token_mint": "So11111111111111111111111111111111111111112",
        "amount": 1000000,
        "dex": "Jupiter",
        "action": "buy",
        "alt_lookup": None,
        "accounts": ["7GkQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1vQwQJv1v", "So11111111111111111111111111111111111111112"],
    }

async def full_pipeline_test():
    print("\n[TEST] Starting full pipeline simulation...")
    # 1. Simulate WebSocket event detection
    event = mock_websocket_event()
    print(f"[TEST] WebSocket event: {event}")

    # 2. Simulate fetching full transaction
    tx_data = mock_fetch_full_transaction(event["signature"])
    print(f"[TEST] Full transaction data: {tx_data}")

    # 3. Parse and decode transaction
    parsed_tx = parse_transaction(tx_data)
    print(f"[TEST] Parsed transaction: {parsed_tx}")
    print(f"[TEST] DEX detected: {parsed_tx.get('dex')}")
    print(f"[TEST] Action: {parsed_tx.get('action')}")

    # 4. Rebuild and execute copier transaction
    coordinator = ExecutionCoordinator()
    if parsed_tx.get('action') == 'buy':
        print("[TEST] Simulating copy BUY execution...")
        result = await coordinator._execute_copy_buy(
            token_mint=parsed_tx['token_mint'],
            source_wallet=parsed_tx['source_wallet'],
            trade_info=parsed_tx,
            detected_dex=parsed_tx.get('dex'),
            routing_instructions=None
        )
    elif parsed_tx.get('action') == 'sell':
        print("[TEST] Simulating copy SELL execution...")
        result = await coordinator._execute_copy_sell(
            token_mint=parsed_tx['token_mint'],
            trade_info=parsed_tx,
            source_wallet=parsed_tx['source_wallet'],
            detected_dex=parsed_tx.get('dex')
        )
    else:
        print("[TEST] Unknown action, skipping execution.")
        result = None

    print(f"[TEST] Execution result: {result}")
    print("[TEST] Full pipeline simulation complete.\n")

if __name__ == "__main__":
    asyncio.run(full_pipeline_test())
