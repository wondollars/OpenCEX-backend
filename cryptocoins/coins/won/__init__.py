from cryptocoins.coins.won.connection import get_w3_connection
from cryptocoins.coins.won.wallet import won_wallet_creation_wrapper
from cryptocoins.coins.won.wallet import is_valid_won_address
from cryptocoins.utils.register import register_coin


WON = 27
CODE = 'WON'
DECIMALS = 8

WON_CURRENCY = register_coin(
    currency_id=WON,
    currency_code=CODE,
    address_validation_fn=is_valid_won_address,
    wallet_creation_fn=won_wallet_creation_wrapper,
    latest_block_fn=lambda currency: get_w3_connection().eth.get_block_number(),
    blocks_diff_alert=100,
)
