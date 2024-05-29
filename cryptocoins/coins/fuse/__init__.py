from core.currency import CoinParams
from cryptocoins.coins.fuse.connection import get_w3_fuse_connection
from cryptocoins.coins.fuse.consts import FUSE , CODE
from cryptocoins.coins.fuse.wallet import fuse_wallet_creation_wrapper, is_valid_fuse_address
from cryptocoins.utils.register import register_coin

w3 = get_w3_fuse_connection()

FUSE_CURRENCY = register_coin(
    currency_id=FUSE,
    currency_code=CODE,
    address_validation_fn=is_valid_fuse_address,
    wallet_creation_fn=fuse_wallet_creation_wrapper,
    latest_block_fn=lambda currency: w3.eth.get_block_number(),
    blocks_diff_alert=100,
)
