import json
import logging
import time
from decimal import Decimal

import cachetools.func
from django.conf import settings
from django.core.cache import cache
from web3 import Web3
from web3.exceptions import BlockNotFound

from core.consts.currencies import BEP20_WON_CURRENCIES
from core.currency import Currency
from cryptocoins.coins.won import WON_CURRENCY
from cryptocoins.coins.won.connection import get_w3_connection, check_won_response_time
from cryptocoins.evm.manager import register_evm_handler
from cryptocoins.interfaces.common import GasPriceCache
from cryptocoins.interfaces.web3_commons import Web3Manager, Web3Token, Web3Transaction, Web3CommonHandler
from cryptocoins.utils.commons import store_last_processed_block_id
from exchange.settings import env
from lib.notifications import send_telegram_message

log = logging.getLogger(__name__)

BEP20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501
DEFAULT_TRANSFER_GAS_LIMIT = 100_000
DEFAULT_TRANSFER_GAS_MULTIPLIER = 2


class WonTransaction(Web3Transaction):
    pass


class WonGasPriceCache(GasPriceCache):
    GAS_PRICE_UPDATE_PERIOD = settings.WON_GAS_PRICE_UPDATE_PERIOD
    GAS_PRICE_COEFFICIENT = settings.WON_GAS_PRICE_COEFFICIENT
    MIN_GAS_PRICE = settings.WON_MIN_GAS_PRICE
    MAX_GAS_PRICE = settings.WON_MAX_GAS_PRICE

    @cachetools.func.ttl_cache(ttl=GAS_PRICE_UPDATE_PERIOD)
    def get_price(self):
        return self.web3.eth.gas_price


class BEP20Token(Web3Token):
    ABI = BEP20_ABI
    BLOCKCHAIN_CURRENCY: Currency = WON_CURRENCY
    CHAIN_ID = settings.WON_CHAIN_ID


class WonManager(Web3Manager):
    CURRENCY: Currency = WON_CURRENCY
    GAS_CURRENCY = settings.WON_TX_GAS
    TOKEN_CURRENCIES = BEP20_WON_CURRENCIES
    TOKEN_CLASS = BEP20Token
    GAS_PRICE_CACHE_CLASS = WonGasPriceCache
    CHAIN_ID = settings.WON_CHAIN_ID
    MIN_BALANCE_TO_ACCUMULATE_DUST = Decimal('0.0002')
    COLD_WALLET_ADDRESS = settings.WON_SAFE_ADDR

    def get_latest_block_num(self):
        try:
            current_block_id = self.client.eth.block_number
        except Exception as e:
            w3.change_provider()
            raise e
        return current_block_id

    def get_block(self, block_id):
        started_at = time.time()
        try:
            block = self.client.eth.get_block(block_id, full_transactions=True)
            response_time = time.time() - started_at
            check_won_response_time(w3, response_time)
        except Exception as e:
            store_last_processed_block_id(currency=WON_CURRENCY, block_id=block_id)
            self.client.change_provider()
            raise e
        return block


w3 = get_w3_connection()
won_manager = WonManager(client=w3)


@register_evm_handler
class WonHandler(Web3CommonHandler):
    CURRENCY = WON_CURRENCY
    COIN_MANAGER = won_manager
    TOKEN_CURRENCIES = won_manager.registered_token_currencies
    TOKEN_CONTRACT_ADDRESSES = won_manager.registered_token_addresses
    TRANSACTION_CLASS = WonTransaction
    IS_ENABLED = env('COMMON_TASKS_WON', default=True)

    if IS_ENABLED:
        SAFE_ADDR = w3.to_checksum_address(settings.WON_SAFE_ADDR)

    CHAIN_ID = settings.WON_CHAIN_ID
    BLOCK_GENERATION_TIME = settings.WON_BLOCK_GENERATION_TIME
    ACCUMULATION_PERIOD = settings.WON_BEP20_ACCUMULATION_PERIOD
    W3_CLIENT = w3
    DEFAULT_BLOCK_ID_DELTA = 100

    @classmethod
    def _filter_transactions(cls, transactions, **kwargs) -> list:
        current_provider = w3.provider.endpoint_uri
        block_id = kwargs.get('block_id')

        # check for incorrect block response
        valid_txs = [t for t in transactions if t['to'] != '0x0000000000000000000000000000000000001000']
        count_fail = cache.get('won_not_valid_block', 1)

        # if every tx have to_address == '0x0000000000000000000000000000000000001000' we try to change provider 10 times
        if not valid_txs and count_fail <= 10:
            msg = f'All txs in block {block_id} are zero.\nChange provider from:\n{current_provider}\nto {w3.provider.endpoint_uri}\nCount Fail: {count_fail}'
            send_telegram_message(msg)
            store_last_processed_block_id(currency=WON_CURRENCY, block_id=block_id)

            w3.change_provider()
            count_fail += 1
            cache.set('won_not_valid_block', count_fail)

            raise Exception(f'All txs in block {block_id} are zero.')
        return valid_txs
