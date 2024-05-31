import logging
from functools import partial
from typing import Dict, Optional, Callable

from core.consts.currencies import (
    ALL_CURRENCIES,
    CRYPTO_COINS_PARAMS,
    CRYPTO_WALLET_ACCOUNT_CREATORS,
    ERC20_MATIC_CURRENCIES,
    ERC20_WON_CURRENCIES,
    ERC20_CELO_CURRENCIES,
    ERC20_CORE_CURRENCIES,
    ERC20_FUSE_CURRENCIES,
    ERC20_AVAX_CURRENCIES,
    ERC20_ETC_CURRENCIES,
    ERC20_FTM_CURRENCIES,
    ERC20_XDAI_CURRENCIES,
)
from core.consts.currencies import ALL_TOKEN_CURRENCIES
from core.consts.currencies import BEP20_CURRENCIES
from core.consts.currencies import CRYPTO_ADDRESS_VALIDATORS
from core.consts.currencies import CRYPTO_WALLET_CREATORS
from core.consts.currencies import CURRENCIES_LIST
from core.consts.currencies import ERC20_CURRENCIES
from core.consts.currencies import TRC20_CURRENCIES
from core.currency import Currency, TokenParams, CoinParams

log = logging.getLogger(__name__)


def register_coin(currency_id: int, currency_code: str, *,
                  address_validation_fn: Optional[Callable] = None,
                  wallet_creation_fn: Optional[Callable] = None,
                  latest_block_fn: Optional[Callable] = None,
                  blocks_diff_alert: Optional[int] = None):

    currency = Currency(currency_id, currency_code)
    if currency not in ALL_CURRENCIES:
        if not address_validation_fn:
            log.warning(f'Address validation FN not specified for {currency}')
        if not wallet_creation_fn:
            log.warning(f'Wallet creation FN not specified for {currency}')
        if not latest_block_fn:
            log.warning(f'Latest block FN not specified for {currency}')

        from cryptocoins.utils.wallet import generate_new_wallet_account

        ALL_CURRENCIES.append(currency)
        CURRENCIES_LIST.append((currency_id, currency_code,))
        CRYPTO_ADDRESS_VALIDATORS.update({currency: address_validation_fn})
        CRYPTO_WALLET_CREATORS.update({currency: wallet_creation_fn})
        CRYPTO_WALLET_ACCOUNT_CREATORS.update({currency:  partial(generate_new_wallet_account, currency)})
        CRYPTO_COINS_PARAMS.update({
            currency: CoinParams(
                latest_block_fn=latest_block_fn,
                blocks_monitoring_diff=blocks_diff_alert,
            )
        })

        log.debug(f'Coin {currency_code} registered')
    return currency


def register_token(currency_id, currency_code, blockchains: Optional[Dict[str, TokenParams]] = None):
    # if not isinstance(blockchains, list) or not blockchains:
    #     raise Exception('blockchains must be type of "list" and cannot be empty')

    currency = Currency(currency_id, currency_code, is_token=True)

    if currency not in ALL_CURRENCIES:
        ALL_CURRENCIES.append(currency)
        CURRENCIES_LIST.append((currency_id, currency_code,))

    if blockchains:
        wallet_creators = {}
        address_validators = {}

        if 'ETH' in blockchains:
            from cryptocoins.coins.eth.wallet import erc20_wallet_creation_wrapper, is_valid_eth_address

            ERC20_CURRENCIES.update({
                currency: blockchains['ETH']
            })
            wallet_creators['ETH'] = erc20_wallet_creation_wrapper
            address_validators['ETH'] = is_valid_eth_address

            log.debug(f'Token {currency} registered as ERC20')

        if 'BNB' in blockchains:
            from cryptocoins.coins.bnb.wallet import bep20_wallet_creation_wrapper, is_valid_bnb_address

            BEP20_CURRENCIES.update({
                currency: blockchains['BNB']
            })
            wallet_creators['BNB'] = bep20_wallet_creation_wrapper
            address_validators['BNB'] = is_valid_bnb_address

            log.debug(f'Token {currency} registered as BEP20')

        if 'TRX' in blockchains:
            from cryptocoins.coins.trx.utils import is_valid_tron_address
            from cryptocoins.coins.trx.wallet import trx20_wallet_creation_wrapper

            TRC20_CURRENCIES.update({
                currency: blockchains['TRX']
            })
            wallet_creators['TRX'] = trx20_wallet_creation_wrapper
            address_validators['TRX'] = is_valid_tron_address

            log.debug(f'Token {currency} registered as TRC20')

        if 'MATIC' in blockchains:
            from cryptocoins.coins.matic.wallet import erc20_polygon_wallet_creation_wrapper, is_valid_matic_address

            ERC20_MATIC_CURRENCIES.update({
                currency: blockchains['MATIC']
            })
            wallet_creators['MATIC'] = erc20_polygon_wallet_creation_wrapper
            address_validators['MATIC'] = is_valid_matic_address

            log.debug(f'Token {currency} registered as ERC20 Polygon')
        if 'WON' in blockchains:
            from cryptocoins.coins.won.wallet import erc20_won_wallet_creation_wrapper, is_valid_won_address

            ERC20_WON_CURRENCIES.update({
                currency: blockchains['WON']
            })
            wallet_creators['WON'] = erc20_won_wallet_creation_wrapper
            address_validators['WON'] = is_valid_won_address

            log.debug(f'Token {currency} registered as ERC20 Won')
        if 'CELO' in blockchains:
            from cryptocoins.coins.celo.wallet import erc20_celo_wallet_creation_wrapper, is_valid_celo_address

            ERC20_CELO_CURRENCIES.update({
                currency: blockchains['CELO']
            })
            wallet_creators['CELO'] = erc20_celo_wallet_creation_wrapper
            address_validators['CELO'] = is_valid_celo_address

            log.debug(f'Token {currency} registered as ERC20 Celo')
        if 'CORE' in blockchains:
            from cryptocoins.coins.core.wallet import erc20_core_wallet_creation_wrapper, is_valid_core_address

            ERC20_CORE_CURRENCIES.update({
                currency: blockchains['CORE']
            })
            wallet_creators['CORE'] = erc20_core_wallet_creation_wrapper
            address_validators['CORE'] = is_valid_core_address

            log.debug(f'Token {currency} registered as ERC20 Core')
        if 'FUSE' in blockchains:
            from cryptocoins.coins.fuse.wallet import erc20_fuse_wallet_creation_wrapper, is_valid_fuse_address

            ERC20_FUSE_CURRENCIES.update({
                currency: blockchains['FUSE']
            })
            wallet_creators['FUSE'] = erc20_fuse_wallet_creation_wrapper
            address_validators['FUSE'] = is_valid_fuse_address

            log.debug(f'Token {currency} registered as ERC20 FUSE')
        if 'AVAX' in blockchains:
            from cryptocoins.coins.avax.wallet import erc20_avax_wallet_creation_wrapper, is_valid_avax_address

            ERC20_AVAX_CURRENCIES.update({
                currency: blockchains['AVAX']
            })
            wallet_creators['AVAX'] = erc20_avax_wallet_creation_wrapper
            address_validators['AVAX'] = is_valid_avax_address

            log.debug(f'Token {currency} registered as ERC20 AVAX')
        
        if 'ETC' in blockchains:
            from cryptocoins.coins.etc.wallet import erc20_etc_wallet_creation_wrapper, is_valid_etc_address

            ERC20_ETC_CURRENCIES.update({
                currency: blockchains['ETC']
            })
            wallet_creators['ETC'] = erc20_etc_wallet_creation_wrapper
            address_validators['ETC'] = is_valid_etc_address

            log.debug(f'Token {currency} registered as ERC20 ETC')

        if 'FTM' in blockchains:
            from cryptocoins.coins.ftm.wallet import erc20_ftm_wallet_creation_wrapper, is_valid_ftm_address

            ERC20_FTM_CURRENCIES.update({
                currency: blockchains['FTM']
            })
            wallet_creators['FTM'] = erc20_ftm_wallet_creation_wrapper
            address_validators['FTM'] = is_valid_ftm_address

            log.debug(f'Token {currency} registered as ERC20 FTM')

        if 'XDAI' in blockchains:
            from cryptocoins.coins.xdai.wallet import erc20_xdai_wallet_creation_wrapper, is_valid_xdai_address

            ERC20_XDAI_CURRENCIES.update({
                currency: blockchains['XDAI']
            })
            wallet_creators['XDAI'] = erc20_xdai_wallet_creation_wrapper
            address_validators['XDAI'] = is_valid_xdai_address

            log.debug(f'Token {currency} registered as ERC20 XDAI')

        CRYPTO_WALLET_CREATORS[currency] = wallet_creators
        CRYPTO_ADDRESS_VALIDATORS[currency] = address_validators
        currency.set_blockchain_list(list(blockchains))

    if currency not in ALL_TOKEN_CURRENCIES:
        ALL_TOKEN_CURRENCIES.append(currency)

    return currency
