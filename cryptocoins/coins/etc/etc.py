import json
import logging

import cachetools.func
from django.conf import settings

from core.consts.currencies import ERC20_ETC_CURRENCIES
from core.currency import Currency
from cryptocoins.coins.etc import ETC_CURRENCY, w3
from cryptocoins.evm.manager import register_evm_handler
from cryptocoins.interfaces.common import GasPriceCache
from cryptocoins.interfaces.web3_commons import Web3Manager, Web3Token, Web3Transaction, Web3CommonHandler
from exchange.settings.env import env
from lib.helpers import to_decimal

log = logging.getLogger(__name__)

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501
DEFAULT_TRANSFER_GAS_LIMIT = 100_000
DEFAULT_TRANSFER_GAS_MULTIPLIER = 2


class EtcTransaction(Web3Transaction):
    pass


class EtcGasPriceCache(GasPriceCache):
    GAS_PRICE_UPDATE_PERIOD = settings.ETC_GAS_PRICE_UPDATE_PERIOD
    GAS_PRICE_COEFFICIENT = settings.ETC_GAS_PRICE_COEFFICIENT
    MIN_GAS_PRICE = settings.ETC_MIN_GAS_PRICE
    MAX_GAS_PRICE = settings.ETC_MAX_GAS_PRICE

    @cachetools.func.ttl_cache(ttl=GAS_PRICE_UPDATE_PERIOD)
    def get_price(self):
        return self.web3.eth.gas_price


class ERC20ETCToken(Web3Token):
    ABI = ERC20_ABI
    BLOCKCHAIN_CURRENCY: Currency = ETC_CURRENCY
    CHAIN_ID = settings.ETC_CHAIN_ID


class EtcManager(Web3Manager):
    GAS_CURRENCY = settings.ETC_TX_GAS
    CURRENCY: Currency = ETC_CURRENCY
    TOKEN_CURRENCIES = ERC20_ETC_CURRENCIES
    TOKEN_CLASS = ERC20ETCToken
    GAS_PRICE_CACHE_CLASS = EtcGasPriceCache
    CHAIN_ID = settings.ETC_CHAIN_ID
    MIN_BALANCE_TO_ACCUMULATE_DUST = to_decimal(env('ETC_MIN_BALANCE_TO_ACCUMULATE_DUST', default=0.01))
    DEFAULT_RECEIPT_WAIT_TIMEOUT = env('ETC_DEFAULT_RECEIPT_WAIT_TIMEOUT', default=5*60)
    COLD_WALLET_ADDRESS = settings.ETC_SAFE_ADDR


etc_manager: EtcManager = EtcManager(client=w3)


@register_evm_handler
class EtcHandler(Web3CommonHandler):
    CURRENCY = ETC_CURRENCY
    COIN_MANAGER = etc_manager
    TOKEN_CURRENCIES = etc_manager.registered_token_currencies
    TOKEN_CONTRACT_ADDRESSES = etc_manager.registered_token_addresses
    TRANSACTION_CLASS = EtcTransaction
    CHAIN_ID = settings.ETC_CHAIN_ID
    BLOCK_GENERATION_TIME = settings.ETC_BLOCK_GENERATION_TIME
    IS_ENABLED = env('COMMON_TASKS_ETC', default=True)
    W3_CLIENT = w3
    ACCUMULATION_PERIOD = settings.ETC_ACCUMULATION_PERIOD

    if IS_ENABLED:
        SAFE_ADDR = w3.to_checksum_address(settings.ETC_SAFE_ADDR)
