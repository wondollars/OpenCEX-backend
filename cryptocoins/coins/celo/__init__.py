from core.currency import CoinParams
from cryptocoins.coins.celo.connection import get_w3_celo_connection
from cryptocoins.coins.celo.consts import CELO , CODE
from cryptocoins.coins.celo.wallet import celo_wallet_creation_wrapper, is_valid_celo_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_celo_connection()

CELO_CURRENCY = register_coin(
    currency_id=CELO,
    currency_code=CODE,
    address_validation_fn=is_valid_celo_address,
    wallet_creation_fn=celo_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
