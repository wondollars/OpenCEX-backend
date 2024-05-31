from core.currency import CoinParams
from cryptocoins.coins.dai.connection import get_w3_dai_connection
from cryptocoins.coins.dai.consts import DAI , CODE
from cryptocoins.coins.dai.wallet import dai_wallet_creation_wrapper, is_valid_dai_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_dai_connection()

DAI_CURRENCY = register_coin(
    currency_id=DAI,
    currency_code=CODE,
    address_validation_fn=is_valid_dai_address,
    wallet_creation_fn=dai_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
