from core.currency import CoinParams
from cryptocoins.coins.xdai.connection import get_w3_xdai_connection
from cryptocoins.coins.xdai.consts import XDAI , CODE
from cryptocoins.coins.xdai.wallet import xdai_wallet_creation_wrapper, is_valid_xdai_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_xdai_connection()

XDAI_CURRENCY = register_coin(
    currency_id=XDAI,
    currency_code=CODE,
    address_validation_fn=is_valid_xdai_address,
    wallet_creation_fn=xdai_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
