from core.currency import CoinParams
from cryptocoins.coins.won.connection import get_w3_won_connection
from cryptocoins.coins.won.consts import WON , CODE
from cryptocoins.coins.won.wallet import won_wallet_creation_wrapper, is_valid_won_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_won_connection()

WON_CURRENCY = register_coin(
    currency_id=WON,
    currency_code=CODE,
    address_validation_fn=is_valid_won_address,
    wallet_creation_fn=won_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
