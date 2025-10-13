import httpx
import base64

class JitoClient:
    def __init__(self, auth_token, block_engine_url):
        self.headers = {
            "Content-Type": "application/json",
            "x-jito-auth": auth_token
        }
        self.block_engine_url = block_engine_url

    async def send_transaction(self, signed_tx: bytes):
        tx_b64 = base64.b64encode(signed_tx).decode()
        payload = {"transaction": tx_b64}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.block_engine_url, headers=self.headers, json=payload)
            return resp.json()

    async def send_bundle(self, signed_txs: list[bytes]):
        txs_b64 = [base64.b64encode(tx).decode() for tx in signed_txs]
        payload = {"transactions": txs_b64}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.block_engine_url.replace("/transactions", "/bundle"),
                headers=self.headers, json=payload
            )
            return resp.json()