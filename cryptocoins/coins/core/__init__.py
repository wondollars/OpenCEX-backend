from core.currency import CoinParams
from cryptocoins.coins.core.connection import get_w3_core_connection
from cryptocoins.coins.core.consts import CORE , CODE
from cryptocoins.coins.core.wallet import core_wallet_creation_wrapper, is_valid_core_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_core_connection()

CORE_CURRENCY = register_coin(
    currency_id=CORE,
    currency_code=CODE,
    address_validation_fn=is_valid_core_address,
    wallet_creation_fn=core_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
