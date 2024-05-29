from core.currency import CoinParams
from cryptocoins.coins.avax.connection import get_w3_avax_connection
from cryptocoins.coins.avax.consts import AVAX , CODE
from cryptocoins.coins.avax.wallet import avax_wallet_creation_wrapper, is_valid_avax_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_avax_connection()

AVAX_CURRENCY = register_coin(
    currency_id=AVAX,
    currency_code=CODE,
    address_validation_fn=is_valid_avax_address,
    wallet_creation_fn=avax_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
