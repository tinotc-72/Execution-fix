import pytest

from trade_processor import TradeProcessor, is_valid_solana_address

class StubRPC:
    """Minimal async RPC stub to satisfy _get_account_info calls."""
    def __init__(self, table=None):
        self.table = table or {}

    async def call(self, method, params):
        if method != "getAccountInfo":
            return {"result": {"value": None}}
        pk = params[0]
        entry = self.table.get(pk)
        if not entry:
            return {"result": {"value": None}}
        owner = entry.get("owner", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        return {
            "result": {
                "value": {
                    "owner": owner,
                    "data": [entry.get("data_b64", ""), "base64"],
                }
            }
        }

def token_account_bytes_for_mint(mint_b58: str) -> bytes:
    import base58
    mint32 = base58.b58decode(mint_b58)
    pad = b"\x00" * (165 - 32)
    return mint32 + pad

def b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode()

def test_address_validator_ranges():
    assert is_valid_solana_address("11111111111111111111111111111112")
    assert is_valid_solana_address("So11111111111111111111111111111111111111112")
    assert is_valid_solana_address("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    assert not is_valid_solana_address("")
    assert not is_valid_solana_address("short")

@pytest.mark.asyncio
async def test_pumpfun_buy_meta_only_output_known():
    wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    tp = TradeProcessor(target_wallets=[wallet])
    out_mint = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"
    tx = {
        "meta": {
            "logMessages": ["Program log: pump.fun router"],
            "preTokenBalances": [],
            "postTokenBalances": [
                {"owner": wallet, "mint": out_mint, "uiTokenAmount": {"amount": "123456"}}
            ],
        },
        "transaction": {"message": {"instructions": []}},
    }
    res = await tp.extract_token_info_fast(tx, wallet)
    assert res and res["source"].startswith(("meta","dex"))
    assert res["output_mint"] == out_mint

# (rest of the tests… Jupiter, layout fallback, ALT handling, logs low_conf)
