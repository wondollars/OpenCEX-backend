from core.currency import CoinParams
from cryptocoins.coins.ftm.connection import get_w3_ftm_connection
from cryptocoins.coins.ftm.consts import FTM , CODE
from cryptocoins.coins.ftm.wallet import ftm_wallet_creation_wrapper, is_valid_ftm_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_ftm_connection()

FTM_CURRENCY = register_coin(
    currency_id=FTM,
    currency_code=CODE,
    address_validation_fn=is_valid_ftm_address,
    wallet_creation_fn=ftm_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
