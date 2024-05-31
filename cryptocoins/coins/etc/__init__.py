from core.currency import CoinParams
from cryptocoins.coins.etc.connection import get_w3_etc_connection
from cryptocoins.coins.etc.consts import ETC , CODE
from cryptocoins.coins.etc.wallet import etc_wallet_creation_wrapper, is_valid_etc_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_etc_connection()

ETC_CURRENCY = register_coin(
    currency_id=ETC,
    currency_code=CODE,
    address_validation_fn=is_valid_etc_address,
    wallet_creation_fn=etc_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
