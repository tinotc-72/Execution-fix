import asyncio
import time
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from spl.token.instructions import get_associated_token_address

from config import WALLET
from env_keys import EnvKeys

JUPITER_SWAP_PROGRAM = Pubkey.from_string("JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB")
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradeConfig:
    sol_amount: float = 0.005
    slippage: float = 0.5  # in %

class JupiterTradingBot:
    def __init__(self, config: TradeConfig):
        self.wallet = WALLET
        self.wallet_pubkey = self.wallet.pubkey()
        self.config = config
        self.client = AsyncClient(EnvKeys().HELIUS_RPC_URL)

    async def get_sol_balance(self) -> float:
        balance = await self.client.get_balance(self.wallet_pubkey)
        return balance.value / 1_000_000_000

    async def get_token_balance(self, token_mint: str) -> int:
        ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(token_mint))
        try:
            res = await self.client.get_token_account_balance(ata)
            return int(res.value.amount)
        except:
            return 0

    def get_best_swap_route(self, input_mint: str, output_mint: str, amount: int) -> Dict[str, Any]:
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": int(self.config.slippage * 100),
            "onlyDirectRoutes": False,
        }
        res = requests.get(JUPITER_QUOTE_URL, params=params)
        return res.json()['data'][0]

    def get_swap_tx(self, route: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "route": route,
            "userPublicKey": str(self.wallet_pubkey),
            "wrapUnwrapSOL": True,
            "feeAccount": None
        }
        res = requests.post(JUPITER_SWAP_URL, json=body)
        return res.json()

    async def send_swap_tx(self, swap_tx_b64: str) -> Optional[str]:
        tx = Transaction.from_bytes(bytes.fromhex(swap_tx_b64))
        sig = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=True, max_retries=1))
        return str(sig.value) if sig.value else None

    async def execute_jupiter_trade_cycle(self, token_mint: str) -> bool:
        logger.info("Starting Jupiter trade cycle")
        token = token_mint
        sol_amount = int(self.config.sol_amount * 1_000_000_000)

        pre_sol = await self.get_sol_balance()
        pre_tokens = await self.get_token_balance(token)

        # BUY
        route = self.get_best_swap_route("So11111111111111111111111111111111111111112", token, sol_amount)
        swap = self.get_swap_tx(route)
        buy_tx = swap['swapTransaction']
        buy_sig = await self.send_swap_tx(buy_tx)
        logger.info(f"Buy signature: {buy_sig}")

        await asyncio.sleep(5)  # HOLD

        # SELL
        token_amount = await self.get_token_balance(token)
        if token_amount == 0:
            logger.warning("No tokens to sell")
            return False

        route = self.get_best_swap_route(token, "So11111111111111111111111111111111111111112", token_amount)
        swap = self.get_swap_tx(route)
        sell_tx = swap['swapTransaction']
        sell_sig = await self.send_swap_tx(sell_tx)
        logger.info(f"Sell signature: {sell_sig}")

        # Final balances
        post_sol = await self.get_sol_balance()
        post_tokens = await self.get_token_balance(token)

        net_sol = post_sol - pre_sol
        logger.info(f"💰 SOL net change: {net_sol:.6f}")
        logger.info(f"🪙 Token net change: {post_tokens - pre_tokens}")
        return True

    async def close(self):
        await self.client.close()

if __name__ == "__main__":
    async def main():
        config = TradeConfig(sol_amount=0.005, slippage=0.5)
        bot = JupiterTradingBot(config)
        target_token = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
        await bot.execute_jupiter_trade_cycle(target_token)
        await bot.close()

    asyncio.run(main())
