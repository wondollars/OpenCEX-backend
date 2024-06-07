import json
import os
from datetime import datetime

from core.enums.profile import UserTypeEnum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchange.settings')
import django

django.setup()

from allauth.account.models import EmailAddress

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db.models import QuerySet
from django.db.transaction import atomic
from django_otp.plugins.otp_totp.models import TOTPDevice

from cryptocoins.coins.btc.service import BTCCoinService
from cryptocoins.models import Keeper, GasKeeper, LastProcessedBlock
from cryptocoins.utils.commons import create_keeper

from core.consts.currencies import CRYPTO_WALLET_CREATORS
from core.currency import Currency
from core.utils.wallet_history import create_or_update_wallet_history_item_from_transaction
from core.models import UserWallet, UserFee, Profile, DisabledCoin
from core.models import Transaction
from core.models import FeesAndLimits
from core.models import PairSettings
from core.models import WithdrawalFee
from core.models.facade import CoinInfo
from core.models.inouts.transaction import REASON_MANUAL_TOPUP
from core.models.inouts.pair import Pair, PAIRS_LIST
from cryptocoins.coins.btc import BTC, BTC_CURRENCY
from cryptocoins.coins.eth import ETH
from cryptocoins.coins.usdt import USDT
from cryptocoins.coins.bnb import BNB
from cryptocoins.coins.trx import TRX
from cryptocoins.coins.matic import MATIC
from cryptocoins.coins.won import WON
from cryptocoins.coins.celo import CELO
from cryptocoins.coins.fuse import FUSE
from cryptocoins.coins.core import CORE
from cryptocoins.coins.avax import AVAX
from cryptocoins.coins.etc import ETC
from cryptocoins.coins.ftm import FTM
from cryptocoins.coins.dai import DAI

from cryptocoins.coins.doge import DOGE
from cryptocoins.coins.ton import TON

# from cryptocoins.coins.pepe import PEPE
# from cryptocoins.coins.babydoge import BABYDOGE
# from cryptocoins.coins.shib import SHIB
# from cryptocoins.coins.floki import FLOKI
from cryptocoins.coins.meme import MEME
from cryptocoins.coins.cake import CAKE

from cryptocoins.utils.btc import generate_btc_multisig_keeper

from exchange.settings import env
from bots.models import BotConfig
from lib.cipher import AESCoderDecoder

User = get_user_model()

BACKUP_PATH = os.path.join(settings.BASE_DIR, 'backup')


def main():

    IS_TRON = env('COMMON_TASKS_TRON', default=True, cast=bool)
    IS_BSC = env('COMMON_TASKS_BNB', default=True, cast=bool)
    IS_MATIC = env('COMMON_TASKS_MATIC', default=True, cast=bool)
    IS_WON = env('COMMON_TASKS_WON', default=True, cast=bool)
    IS_CELO = env('COMMON_TASKS_CELO', default=True, cast=bool)
    IS_CORE = env('COMMON_TASKS_CORE', default=True, cast=bool)
    IS_FUSE = env('COMMON_TASKS_FUSE', default=True, cast=bool)
    IS_AVAX = env('COMMON_TASKS_AVAX', default=True, cast=bool)
    IS_ETC = env('COMMON_TASKS_ETC', default=True, cast=bool)
    IS_FTM = env('COMMON_TASKS_FTM', default=True, cast=bool)
    IS_DAI = env('COMMON_TASKS_DAI', default=True, cast=bool)

    coin_list = [
        ETH,
        BTC,
        USDT,
        BNB,
        TRX,
        MATIC,
        WON,
        CELO,
        CORE,
        FUSE,
        AVAX,
        ETC,
        FTM,
        DAI,
        DOGE,
        TON,
        # PEPE,
        # BABYDOGE,
        # SHIB,
        # FLOKI,
        MEME,
        CAKE,
    ]
    coin_info = {
        ETH: [
            {
                'model': CoinInfo,
                'find': {'currency': ETH},
                'attributes': {
                    'name': 'Ethereum',
                    'decimals': 8,
                    'index': 3,
                    'tx_explorer': 'https://etherscan.io/tx/',
                    'links': {
                        "bt": {
                            "href": "https://bitcointalk.org/index.php?topic=428589.0",
                            "title": "BitcoinTalk"
                        },
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/ethereum/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://etherscan.io/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "http://ethereum.org",
                            "title": "ethereum.org"
                        }
                    }
                }
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': ETH},
                    'attributes': {
                    'limits_deposit_min': 0.00500000,
                    'limits_deposit_max': 1000.00000000,
                    'limits_withdrawal_min': 0.00500000,
                    'limits_withdrawal_max': 15.00000000,
                    'limits_order_min': 0.00100000,
                    'limits_order_max': 15.00000000,
                    'limits_code_max': 100.00000000,
                    'limits_accumulation_min': 0.00500000,
                    'fee_deposit_address': 0.00000010,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,

                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': ETH},
                'attributes': {
                    'blockchain_currency': ETH,
                    'address_fee': 0.00000010
                }
            },
        ],
        BTC: [
            {
                'model': CoinInfo,
                'find': {'currency': BTC},
                'attributes': {
                    'name': 'Bitcoin',
                    'decimals': 8,
                    'index': 2,
                    'tx_explorer': 'https://www.blockchain.com/btc/tx/',
                    'links': {
                        "bt": {
                            "href": "https://bitcointalk.org/index.php",
                            "title": "BitcoinTalk"
                        },
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/bitcoin/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://www.blockchain.com/en/explorer",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://bitcoin.org",
                            "title": "bitcoin"
                        }
                    }
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': BTC},
                'attributes': {
                    'limits_deposit_min': 0.00020000,
                    'limits_deposit_max': 100,
                    'limits_withdrawal_min': 0.00020000,
                    'limits_withdrawal_max': 5,
                    'limits_order_min': 0.00030000,
                    'limits_order_max': 5.00000000,
                    'limits_code_max': 100.00000000,
                    'limits_accumulation_min': 0.00020000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,

                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': BTC},
                'attributes': {
                    'blockchain_currency': BTC,
                    'address_fee': 0.00000001
                },
            },
        ],
        USDT: [
            {
                'model': CoinInfo,
                'find': {'currency': USDT},
                'attributes': {
                    'name': 'Tether USDT',
                    'decimals': 6,
                    'index': 1,
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/tether/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://etherscan.io/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://tether.to/",
                            "title": "tether.to"
                        }
                    }
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': USDT},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 2.00000000,
                    'limits_withdrawal_max': 10000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 100000.00000000,
                    'limits_code_max': 100000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': USDT, 'blockchain_currency': ETH},
                'attributes': {
                    'blockchain_currency': ETH,
                    'address_fee': 5.00000000
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': USDT, 'blockchain_currency': BNB},
                'attributes': {
                    'blockchain_currency': BNB,
                    'address_fee': 0.00010000
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': USDT, 'blockchain_currency': TRX},
                'attributes': {
                    'blockchain_currency': TRX,
                    'address_fee': 1.00000000
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': USDT, 'blockchain_currency': WON},
                'attributes': {
                    'blockchain_currency': WON,
                    'address_fee': 1.00000000
                },
            },
        ],
        TON: [
            {
                'model': CoinInfo,
                'find': {'currency': TON},
                'attributes': {
                    'name': 'Toncoin ',
                    'decimals': 10,
                    'index': 33,
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/toncoin/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://bscscan.com/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://ton.org/",
                            "title": "Ton"
                        }
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/11419.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': TON},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 2.00000000,
                    'limits_withdrawal_max': 10000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 100000.00000000,
                    'limits_code_max': 100000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            # {
            #     'model': WithdrawalFee,
            #     'find': {'currency': USDT, 'blockchain_currency': ETH},
            #     'attributes': {
            #         'blockchain_currency': ETH,
            #         'address_fee': 5.00000000
            #     },
            # },
            {
                'model': WithdrawalFee,
                'find': {'currency': TON, 'blockchain_currency': BNB},
                'attributes': {
                    'blockchain_currency': BNB,
                    'address_fee': 0.00010000
                },
            },
             
        ],
        DOGE: [
            {
                'model': CoinInfo,
                'find': {'currency': DOGE},
                'attributes': {
                    'name': 'Dogecoin',
                    'decimals': 10,
                    'index': 33,
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/dogecoin/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://bscscan.com/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://dogecoin.com/",
                            "title": "Dogecoin"
                        }
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/74.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': DOGE},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 2.00000000,
                    'limits_withdrawal_max': 10000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 100000.00000000,
                    'limits_code_max': 100000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            # {
            #     'model': WithdrawalFee,
            #     'find': {'currency': USDT, 'blockchain_currency': ETH},
            #     'attributes': {
            #         'blockchain_currency': ETH,
            #         'address_fee': 5.00000000
            #     },
            # },
            {
                'model': WithdrawalFee,
                'find': {'currency': DOGE, 'blockchain_currency': BNB},
                'attributes': {
                    'blockchain_currency': BNB,
                    'address_fee': 0.00010000
                },
            },
             
        ],
        TRX: [
            {
                'model': CoinInfo,
                'find': {'currency': TRX},
                'attributes': {
                    'name': 'Tron',
                    'decimals': 8,
                    'index': 5,
                    'tx_explorer': 'https://tronscan.org/#/transaction/',
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/tron/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://tronscan.org/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://tron.network/",
                            "title": "tron.network"
                        }
                    }
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': TRX},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 100000000.00000000,
                    'limits_withdrawal_min': 1.00000000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 1000000.00000000,
                    'limits_code_max': 1000000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': TRX},
                'attributes': {
                    'blockchain_currency': TRX,
                    'address_fee': 1.00000000
                },
            },
        ],
        BNB: [
            {
                'model': CoinInfo,
                'find': {'currency': BNB},
                'attributes': {
                    'name': 'Binance Coin',
                    'decimals': 8,
                    'index': 6,
                    'tx_explorer': 'https://bscscan.com/tx/',
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/bnb/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://bscscan.com/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://www.binance.com/",
                            "title": "www.binance.com"
                        }
                    }
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': BNB},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 0.00100000,
                    'limits_withdrawal_max': 1000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 1000000.00000000,
                    'limits_code_max': 1000000.00000000,
                    'limits_accumulation_min': 0.00100000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': BNB},
                'attributes': {
                    'blockchain_currency': BNB,
                    'address_fee': 0.00010000
                },
            },
        ],
        MATIC: [
            {
                'model': CoinInfo,
                'find': {'currency': MATIC},
                'attributes': {
                    'name': 'MATIC',
                    'decimals': 8,
                    'index': 27,
                    'tx_explorer': 'https://polygonscan.com/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/3890.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': MATIC},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': MATIC},
                'attributes': {
                    'blockchain_currency': MATIC,
                    'address_fee': 0.00300000
                },
            },
        ],
        WON: [
            {
                'model': CoinInfo,
                'find': {'currency': WON},
                'attributes': {
                    'name': 'Won Coin',
                    'decimals': 8,
                    'index': 28,
                    'tx_explorer': 'https://scan.wonnetwork.org/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://www.wondollars.org/images/logo.svg',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': WON},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 1.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': WON},
                'attributes': {
                    'blockchain_currency': WON,
                    'address_fee': 0.00100000
                },
            },
        ],
        ETC: [
            {
                'model': CoinInfo,
                'find': {'currency': ETC},
                'attributes': {
                    'name': 'Ethereum Classic Coin',
                    'decimals': 8,
                    'index': 35,
                    'tx_explorer': 'https://etc.blockscout.com/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "https://coinmarketcap.com/currencies/ethereum-classic/", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/1321.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': ETC},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': ETC},
                'attributes': {
                    'blockchain_currency': ETC,
                    'address_fee': 0.00100000
                },
            },
        ],
        FTM: [
            {
                'model': CoinInfo,
                'find': {'currency': FTM},
                'attributes': {
                    'name': 'Fantom Coin',
                    'decimals': 8,
                    'index': 28,
                    'tx_explorer': 'https://ftmscan.com/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "https://coinmarketcap.com/currencies/fantom/", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/3513.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': FTM},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': FTM},
                'attributes': {
                    'blockchain_currency': FTM,
                    'address_fee': 0.00100000
                },
            },
        ],
        DAI: [
            {
                'model': CoinInfo,
                'find': {'currency': DAI},
                'attributes': {
                    'name': 'xDai Coin',
                    'decimals': 8,
                    'index': 28,
                    'tx_explorer': 'https://gnosis.blockscout.com/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/8635.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': DAI},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': DAI},
                'attributes': {
                    'blockchain_currency': DAI,
                    'address_fee': 0.00100000
                },
            },
        ],
        CELO: [
            {
                'model': CoinInfo,
                'find': {'currency': CELO},
                'attributes': {
                    'name': 'Celo Coin',
                    'decimals': 8,
                    'index': 28,
                    'tx_explorer': 'https://celoscan.io/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://wonnetwork.org/images/svg/celo.svg',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': CELO},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': CELO},
                'attributes': {
                    'blockchain_currency': CELO,
                    'address_fee': 0.00100000
                },
            },
        ],
        CORE: [
            {
                'model': CoinInfo,
                'find': {'currency': CORE},
                'attributes': {
                    'name': 'Core-Dao Coin',
                    'decimals': 8,
                    'index': 28,
                    'tx_explorer': 'https://scan.coredao.org/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://wonnetwork.org/images/svg/core.svg',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': CORE},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': CORE},
                'attributes': {
                    'blockchain_currency': CORE,
                    'address_fee': 0.00100000
                },
            },
        ],
        FUSE: [
            {
                'model': CoinInfo,
                'find': {'currency': FUSE},
                'attributes': {
                    'name': 'Fuse Coin',
                    'decimals': 8,
                    'index': 32,
                    'tx_explorer': 'https://explorer.fuse.io/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://wonnetwork.org/images/svg/fuse.svg',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': FUSE},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': FUSE},
                'attributes': {
                    'blockchain_currency': FUSE,
                    'address_fee': 0.00100000
                },
            },
        ],
        AVAX: [
            {
                'model': CoinInfo,
                'find': {'currency': AVAX},
                'attributes': {
                    'name': 'Avalanche Coin',
                    'decimals': 8,
                    'index': 30,
                    'tx_explorer': 'https://snowtrace.io/tx/',
                    'links': {
                        "bt": {"href": "", "title": "BitcoinTalk"},
                        "cmc": {"href": "", "title": "CoinMarketCap"},
                        "exp": {"href": "", "title": "Explorer"},
                        "official": {"href": "", "title": ""}
                    },
                    'logo': 'https://wonnetwork.org/images/svg/avax.svg',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': AVAX},
                'attributes': {
                    'limits_deposit_min': 0.00010000,
                    'limits_deposit_max': 10000000.00000000,
                    'limits_withdrawal_min': 0.00010000,
                    'limits_withdrawal_max': 10000000.00000000,
                    'limits_order_min': 0.01000000,
                    'limits_order_max': 100000000.00000000,
                    'limits_code_max': 10000000.00000000,
                    'limits_accumulation_min': 0.00010000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                    'limits_keeper_accumulation_balance': 100.00000000,
                    'limits_accumulation_max_gas_price': 500.00000000,
                },
            },
            {
                'model': WithdrawalFee,
                'find': {'currency': AVAX},
                'attributes': {
                    'blockchain_currency': AVAX,
                    'address_fee': 0.00100000
                },
            },
        ],
        # PEPE: [
        #     {
        #         'model': CoinInfo,
        #         'find': {'currency': PEPE},
        #         'attributes': {
        #             'name': 'PEPE',
        #             'decimals': 10,
        #             'index': 39,
        #             'links': {
        #                 "cmc": {
        #                     "href": "https://coinmarketcap.com/currencies/pepe/",
        #                     "title": "CoinMarketCap"
        #                 },
        #                 "exp": {
        #                     "href": "https://etherscan.io/",
        #                     "title": "Explorer"
        #                 },
        #                 "official": {
        #                     "href": "https://www.pepe.vip/",
        #                     "title": "PEPE"
        #                 }
        #             },
        #             'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/24478.png',
        #         },
        #     },
        #     {
        #         'model': FeesAndLimits,
        #         'find': {'currency': PEPE},
        #         'attributes': {
        #             'limits_deposit_min': 1.00000000,
        #             'limits_deposit_max': 1000000.00000000,
        #             'limits_withdrawal_min': 2.00000000,
        #             'limits_withdrawal_max': 10000.00000000,
        #             'limits_order_min': 1.00000000,
        #             'limits_order_max': 100000.00000000,
        #             'limits_code_max': 100000.00000000,
        #             'limits_accumulation_min': 1.00000000,
        #             'fee_deposit_address': 0,
        #             'fee_deposit_code': 0,
        #             'fee_withdrawal_code': 0,
        #             'fee_order_limits': 0.00100000,
        #             'fee_order_market': 0.00200000,
        #             'fee_exchange_value': 0.00200000,
        #         },
        #     },
        #     # {
        #     #     'model': WithdrawalFee,
        #     #     'find': {'currency': USDT, 'blockchain_currency': ETH},
        #     #     'attributes': {
        #     #         'blockchain_currency': ETH,
        #     #         'address_fee': 5.00000000
        #     #     },
        #     # },
        #     {
        #         'model': WithdrawalFee,
        #         'find': {'currency': PEPE, 'blockchain_currency': BNB},
        #         'attributes': {
        #             'blockchain_currency': BNB,
        #             'address_fee': 0.00010000
        #         },
        #     },
             
        # ],
        # SHIB: [
        #     {
        #         'model': CoinInfo,
        #         'find': {'currency': SHIB},
        #         'attributes': {
        #             'name': 'Shiba Inu',
        #             'decimals': 10,
        #             'index': 43,
        #             'links': {
        #                 "cmc": {
        #                     "href": "https://coinmarketcap.com/currencies/shiba-inu/",
        #                     "title": "CoinMarketCap"
        #                 },
        #                 "exp": {
        #                     "href": "https://etherscan.io/",
        #                     "title": "Explorer"
        #                 },
        #                 "official": {
        #                     "href": "https://shibatoken.com/",
        #                     "title": "Shiba Inu"
        #                 }
        #             },
        #             'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/74.png',
        #         },
        #     },
        #     {
        #         'model': FeesAndLimits,
        #         'find': {'currency': SHIB},
        #         'attributes': {
        #             'limits_deposit_min': 1.00000000,
        #             'limits_deposit_max': 1000000.00000000,
        #             'limits_withdrawal_min': 2.00000000,
        #             'limits_withdrawal_max': 10000.00000000,
        #             'limits_order_min': 1.00000000,
        #             'limits_order_max': 100000.00000000,
        #             'limits_code_max': 100000.00000000,
        #             'limits_accumulation_min': 1.00000000,
        #             'fee_deposit_address': 0,
        #             'fee_deposit_code': 0,
        #             'fee_withdrawal_code': 0,
        #             'fee_order_limits': 0.00100000,
        #             'fee_order_market': 0.00200000,
        #             'fee_exchange_value': 0.00200000,
        #         },
        #     },
        #     # {
        #     #     'model': WithdrawalFee,
        #     #     'find': {'currency': USDT, 'blockchain_currency': ETH},
        #     #     'attributes': {
        #     #         'blockchain_currency': ETH,
        #     #         'address_fee': 5.00000000
        #     #     },
        #     # },
        #     {
        #         'model': WithdrawalFee,
        #         'find': {'currency': SHIB, 'blockchain_currency': ETH},
        #         'attributes': {
        #             'blockchain_currency': ETH,
        #             'address_fee': 0.00010000
        #         },
        #     },
             
        # ],
        # FLOKI: [
        #     {
        #         'model': CoinInfo,
        #         'find': {'currency': FLOKI},
        #         'attributes': {
        #             'name': 'FLOKI',
        #             'decimals': 10,
        #             'index': 41,
        #             'links': {
        #                 "cmc": {
        #                     "href": "https://coinmarketcap.com/currencies/floki-inu/",
        #                     "title": "CoinMarketCap"
        #                 },
        #                 "exp": {
        #                     "href": "https://etherscan.io/",
        #                     "title": "Explorer"
        #                 },
        #                 "official": {
        #                     "href": "https://floki.com/",
        #                     "title": "FLOKI"
        #                 }
        #             },
        #             'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/10804.png',
        #         },
        #     },
        #     {
        #         'model': FeesAndLimits,
        #         'find': {'currency': FLOKI},
        #         'attributes': {
        #             'limits_deposit_min': 1.00000000,
        #             'limits_deposit_max': 1000000.00000000,
        #             'limits_withdrawal_min': 2.00000000,
        #             'limits_withdrawal_max': 10000.00000000,
        #             'limits_order_min': 1.00000000,
        #             'limits_order_max': 100000.00000000,
        #             'limits_code_max': 100000.00000000,
        #             'limits_accumulation_min': 1.00000000,
        #             'fee_deposit_address': 0,
        #             'fee_deposit_code': 0,
        #             'fee_withdrawal_code': 0,
        #             'fee_order_limits': 0.00100000,
        #             'fee_order_market': 0.00200000,
        #             'fee_exchange_value': 0.00200000,
        #         },
        #     },
        #     # {
        #     #     'model': WithdrawalFee,
        #     #     'find': {'currency': USDT, 'blockchain_currency': ETH},
        #     #     'attributes': {
        #     #         'blockchain_currency': ETH,
        #     #         'address_fee': 5.00000000
        #     #     },
        #     # },
        #     {
        #         'model': WithdrawalFee,
        #         'find': {'currency': FLOKI, 'blockchain_currency': ETH},
        #         'attributes': {
        #             'blockchain_currency': ETH,
        #             'address_fee': 0.00010000
        #         },
        #     },
             
        # ],
        MEME: [
            {
                'model': CoinInfo,
                'find': {'currency': MEME},
                'attributes': {
                    'name': 'MEME',
                    'decimals': 10,
                    'index': 42,
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/meme/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://etherscan.io/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://memecoin.org/",
                            "title": "MEME"
                        }
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/28301.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': MEME},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 2.00000000,
                    'limits_withdrawal_max': 10000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 100000.00000000,
                    'limits_code_max': 100000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            # {
            #     'model': WithdrawalFee,
            #     'find': {'currency': USDT, 'blockchain_currency': ETH},
            #     'attributes': {
            #         'blockchain_currency': ETH,
            #         'address_fee': 5.00000000
            #     },
            # },
            {
                'model': WithdrawalFee,
                'find': {'currency': MEME, 'blockchain_currency': ETH},
                'attributes': {
                    'blockchain_currency': ETH,
                    'address_fee': 0.00010000
                },
            },
             
        ],
        CAKE: [
            {
                'model': CoinInfo,
                'find': {'currency': CAKE},
                'attributes': {
                    'name': 'CAKE',
                    'decimals': 10,
                    'index': 45,
                    'links': {
                        "cmc": {
                            "href": "https://coinmarketcap.com/currencies/pancakeswap/",
                            "title": "CoinMarketCap"
                        },
                        "exp": {
                            "href": "https://bscscan.com/",
                            "title": "Explorer"
                        },
                        "official": {
                            "href": "https://pancakeswap.finance/",
                            "title": "CAKE"
                        }
                    },
                    'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/7186.png',
                },
            },
            {
                'model': FeesAndLimits,
                'find': {'currency': CAKE},
                'attributes': {
                    'limits_deposit_min': 1.00000000,
                    'limits_deposit_max': 1000000.00000000,
                    'limits_withdrawal_min': 2.00000000,
                    'limits_withdrawal_max': 10000.00000000,
                    'limits_order_min': 1.00000000,
                    'limits_order_max': 100000.00000000,
                    'limits_code_max': 100000.00000000,
                    'limits_accumulation_min': 1.00000000,
                    'fee_deposit_address': 0,
                    'fee_deposit_code': 0,
                    'fee_withdrawal_code': 0,
                    'fee_order_limits': 0.00100000,
                    'fee_order_market': 0.00200000,
                    'fee_exchange_value': 0.00200000,
                },
            },
            # {
            #     'model': WithdrawalFee,
            #     'find': {'currency': USDT, 'blockchain_currency': ETH},
            #     'attributes': {
            #         'blockchain_currency': ETH,
            #         'address_fee': 5.00000000
            #     },
            # },
            {
                'model': WithdrawalFee,
                'find': {'currency': CAKE, 'blockchain_currency': BNB},
                'attributes': {
                    'blockchain_currency': BNB,
                    'address_fee': 0.00010000
                },
            },
             
        ],
        # BABYDOGE: [
        #     {
        #         'model': CoinInfo,
        #         'find': {'currency': BABYDOGE},
        #         'attributes': {
        #             'name': 'Baby Doge Coin',
        #             'decimals': 10,
        #             'index': 33,
        #             'links': {
        #                 "cmc": {
        #                     "href": "https://coinmarketcap.com/currencies/baby-doge-coin/",
        #                     "title": "CoinMarketCap"
        #                 },
        #                 "exp": {
        #                     "href": "https://etherscan.io/",
        #                     "title": "Explorer"
        #                 },
        #                 "official": {
        #                     "href": "https://www.babydoge.com/",
        #                     "title": "Baby Doge Coin"
        #                 }
        #             },
        #             'logo': 'https://s2.coinmarketcap.com/static/img/coins/64x64/28301.png',
        #         },
        #     },
        #     {
        #         'model': FeesAndLimits,
        #         'find': {'currency': BABYDOGE},
        #         'attributes': {
        #             'limits_deposit_min': 1.00000000,
        #             'limits_deposit_max': 1000000.00000000,
        #             'limits_withdrawal_min': 2.00000000,
        #             'limits_withdrawal_max': 10000.00000000,
        #             'limits_order_min': 1.00000000,
        #             'limits_order_max': 100000.00000000,
        #             'limits_code_max': 100000.00000000,
        #             'limits_accumulation_min': 1.00000000,
        #             'fee_deposit_address': 0,
        #             'fee_deposit_code': 0,
        #             'fee_withdrawal_code': 0,
        #             'fee_order_limits': 0.00100000,
        #             'fee_order_market': 0.00200000,
        #             'fee_exchange_value': 0.00200000,
        #         },
        #     },
        #     # {
        #     #     'model': WithdrawalFee,
        #     #     'find': {'currency': USDT, 'blockchain_currency': ETH},
        #     #     'attributes': {
        #     #         'blockchain_currency': ETH,
        #     #         'address_fee': 5.00000000
        #     #     },
        #     # },
        #     {
        #         'model': WithdrawalFee,
        #         'find': {'currency': BABYDOGE, 'blockchain_currency': ETH},
        #         'attributes': {
        #             'blockchain_currency': ETH,
        #             'address_fee': 0.00010000
        #         },
        #     },
             
        # ],
         
    }

    if not IS_BSC:
        coin_info[BNB].append(
            {
                'model': DisabledCoin,
                'find': {'currency': BNB},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )

    if not IS_TRON:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': TRX},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )

    if not IS_MATIC:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': MATIC},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_WON:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': WON},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_CELO:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': CELO},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_CORE:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': CORE},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_FUSE:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': FUSE},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_AVAX:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': AVAX},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )

    if not IS_ETC:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': ETC},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )
    if not IS_FTM:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': FTM},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )

    if not IS_DAI:
        coin_info[TRX].append(
            {
                'model': DisabledCoin,
                'find': {'currency': DAI},
                'attributes': {
                    'disable_all': True,
                    'disable_stack': True,
                    'disable_pairs': True,
                    'disable_exchange': True,
                    'disable_withdrawals': True,
                    'disable_topups': True,
                },
            },
        )

    with atomic():
        to_write = []

        def get_or_create(model_inst, curr, get_attrs, set_attrs: dict):
            item, is_created = model_inst.objects.get_or_create(
                **get_attrs,
                defaults={
                    'currency': curr,
                    **set_attrs,
                }
            )

            if not is_created:
                for key, attr in set_attrs.items():
                    setattr(item, key, attr)
                item.save()

        for coin, to_create_list in coin_info.items():
            for data in to_create_list:
                model = data['model']
                find = data['find']
                attributes = data['attributes']
                get_or_create(model, coin, find,  attributes)

        # create user for bot
        name = 'bot1@bot.com'
        bot = User.objects.filter(username=name).first()
        to_write.append('Bot info:')
        if not bot:
            bot = User.objects.create_user(name, name, settings.BOT_PASSWORD)
            to_write.append('Bot created.')
            EmailAddress.objects.create(
                user=bot,
                email=bot.email,
                verified=True,
                primary=True,
            )

            UserFee.objects.create(
                user=bot,
                fee_rate=0,
            )

            # top up bot
            topup_list = {
                BTC: 1000,
                ETH: 1000_000,
                USDT: 10000_000,
                BNB: 1000_000,
                TRX: 100_000,
                MATIC: 1000_000,
                WON: 1000_000_000,
                CELO: 1000_000,
                CORE: 1000_000,
                FUSE: 1000_000,
                AVAX: 1000_000,
                ETC: 1000_000,
                FTM: 1000_000_000,
                DAI: 1000_000_000,
                DOGE: 1000_000_000,
                TON: 1000_000,
                # PEPE: 1000_000_000,
                # SHIB: 1000_000_000,
                # FLOKI: 1000_000_000,
                MEME: 1000_000_000,
                CAKE: 1000_000,
                # BABYDOGE: 1000_000_000,
            }

            for currency_id, amount in topup_list.items():
                currency = Currency.get(currency_id)
                tx = Transaction.topup(bot.id, currency, amount, {'1': 1}, reason=REASON_MANUAL_TOPUP)
                create_or_update_wallet_history_item_from_transaction(tx)
                to_write.append(f'Bot TopUp: {amount} {currency.code}')

        if bot.profile:
            bot.profile.user_type = UserTypeEnum.bot.value
            bot.profile.save()

        to_write.append(f'Email: {name}  Password: {settings.BOT_PASSWORD}')
        to_write.append('='*10)

        pairs = PAIRS_LIST + [
            (12, 'MATIC-USDT'),
            (13, 'WON-USDT'),
            (14, 'AVAX-USDT'),
            (15, 'FUSE-USDT'),
            (16, 'CORE-USDT'),
            (17, 'CELO-USDT'),
            (18, 'ETC-USDT'),
            (19, 'FTM-USDT'),
            (20, 'DAI-USDT'),
            (21, 'DOGE-USDT'),
            (22, 'TON-USDT'),
            # (23, 'PEPE-USDT'),
            # (24, 'SHIB-USDT'),
            # (25, 'FLOKI-USDT'),
            (26, 'MEME-USDT'),
            (28, 'CAKE-USDT'),
            # (27, 'BABYDOGE-USDT'),

        ]

        for pair_data in pairs:
            id_value, code = pair_data
            base, quote = code.split('-')
            Pair.objects.get_or_create(id=id_value, base=base, quote=quote)

        # create pairs
        pair_list = {
            # Pair.get('PEPE-USDT'): {
            #         PairSettings: {
            #             'is_enabled': True,
            #             'is_autoorders_enabled': True,
            #             'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
            #             'custom_price': 0.001,
            #             'deviation': 0,
            #             'precisions': ['0.001', '0.0001', '0.00001', '0.000001', '0.0000001', '0.00000001']
            #         },
            #         BotConfig: {
            #             'name': 'PEPE-USDT',
            #             'user': bot,
            #             'strategy': BotConfig.TRADE_STRATEGY_DRAW,
            #             'instant_match': True,
            #             'ohlc_period': 5,
            #             'loop_period_random': True,
            #             'min_period': 5,
            #             'max_period': 10,
            #             'ext_price_delta': 0.002,
            #             'min_order_quantity': 1,  # Số lượng đặt lệnh tối thiểu được điều chỉnh
            #             'max_order_quantity': 1000000,  # Số lượng đặt lệnh tối đa được điều chỉnh
            #             'low_orders_max_match_size': 10000,  # Kích thước khớp lệnh tối đa cho các lệnh nhỏ được điều chỉnh
            #             'low_orders_spread_size': 1,  # Kích thước spread tối thiểu giữa lệnh mua và lệnh bán
            #             'low_orders_min_order_size': 1,  # Kích thước đặt lệnh nhỏ nhất cho các lệnh nhỏ
            #             'enabled': True,
            #         }
            #     },
            Pair.get('CAKE-USDT'): {
                    PairSettings: {
                        'is_enabled': True,
                        'is_autoorders_enabled': True,
                        'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                        'custom_price': 0.001,
                        'deviation': 0,
                        'precisions': ['100', '10', '1', '0.1', '0.01', '0.001']
                    },
                    BotConfig: {
                        'name': 'CAKE-USDT',
                        'user': bot,
                        'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                        'instant_match': True,
                        'ohlc_period': 5,
                        'loop_period_random': True,
                        'min_period': 5,
                        'max_period': 10,
                        'ext_price_delta': 0.005,
                        'min_order_quantity': 1,  # Số lượng đặt lệnh tối thiểu được điều chỉnh
                        'max_order_quantity': 1000000,  # Số lượng đặt lệnh tối đa được điều chỉnh
                        'low_orders_max_match_size': 10000,  # Kích thước khớp lệnh tối đa cho các lệnh nhỏ được điều chỉnh
                        'low_orders_spread_size': 1,  # Kích thước spread tối thiểu giữa lệnh mua và lệnh bán
                        'low_orders_min_order_size': 1,  # Kích thước đặt lệnh nhỏ nhất cho các lệnh nhỏ
                        'enabled': True,
                    }
                },

            # Pair.get('SHIB-USDT'): {
            #         PairSettings: {
            #             'is_enabled': True,
            #             'is_autoorders_enabled': True,
            #             'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
            #             'custom_price': 0,
            #             'deviation': 0.98000000,
            #             'precisions': ['0.0001', '0.00001', '0.000001', '0.0000001', '0.00000001', '0.00000001']
            #         },
            #         BotConfig: {
            #             'name': 'SHIB-USDT',
            #             'user': bot,
            #             'strategy': BotConfig.TRADE_STRATEGY_DRAW,
            #             'instant_match': True,
            #             'ohlc_period': 5,
            #             'loop_period_random': True,
            #             'min_period': 5,
            #             'max_period': 10,
            #             'ext_price_delta': 0.002,
            #             'min_order_quantity': 1,  # Số lượng đặt lệnh tối thiểu được điều chỉnh
            #             'max_order_quantity': 1000000,  # Số lượng đặt lệnh tối đa được điều chỉnh
            #             'low_orders_max_match_size': 10000,  # Kích thước khớp lệnh tối đa cho các lệnh nhỏ được điều chỉnh
            #             'low_orders_spread_size': 1,  # Kích thước spread tối thiểu giữa lệnh mua và lệnh bán
            #             'low_orders_min_order_size': 1,  # Kích thước đặt lệnh nhỏ nhất cho các lệnh nhỏ
            #             'enabled': True,
            #         }
            #  },

             
            # Pair.get('FLOKI-USDT'): {
            #     PairSettings: {
            #         'is_enabled': True,
            #         'is_autoorders_enabled': True,
            #         'price_source': PairSettings.PRICE_SOURCE_EXTERNAL, 
            #         'custom_price': 0.001,
            #         'deviation': 0,
            #         'precisions': ['1', '0.1', '0.01', '0.001', '0.0001', '0.00001', '0.000001', '0.0000001']
 
            #     },
            #     BotConfig: {
            #         'name': 'FLOKI-USDT',
            #         'user': bot,
            #         'strategy': BotConfig.TRADE_STRATEGY_DRAW,
            #         'instant_match': True,
            #         'ohlc_period': 5,
            #         'loop_period_random': True,
            #         'min_period': 5,
            #         'max_period': 10,
            #         'ext_price_delta': 0.002,
            #         'min_order_quantity': 1,  # Số lượng đặt lệnh tối thiểu được điều chỉnh
            #         'max_order_quantity': 1000000,  # Số lượng đặt lệnh tối đa được điều chỉnh
            #         'low_orders_max_match_size': 10000,  # Kích thước khớp lệnh tối đa cho các lệnh nhỏ được điều chỉnh
            #         'low_orders_spread_size': 1,  # Kích thước spread tối thiểu giữa lệnh mua và lệnh bán
            #         'low_orders_min_order_size': 1,  # Kích thước đặt lệnh nhỏ nhất cho các lệnh nhỏ
            #         'enabled': True,
            #     }
            # },

            Pair.get('MEME-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.01,
                    'deviation': 0.98000000,
                    'precisions': ['0.1', '0.01', '0.0001', '0.00001', '0.000001', '0.0000001']
                },
                BotConfig: {
                    'name': 'MEME-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,  # Số lượng đặt lệnh tối thiểu được điều chỉnh
                    'max_order_quantity': 1000000,  # Số lượng đặt lệnh tối đa được điều chỉnh
                    'low_orders_max_match_size': 10000,  # Kích thước khớp lệnh tối đa cho các lệnh nhỏ được điều chỉnh
                    'low_orders_spread_size': 1,  # Kích thước spread tối thiểu giữa lệnh mua và lệnh bán
                    'low_orders_min_order_size': 1,  # Kích thước đặt lệnh nhỏ nhất cho các lệnh nhỏ
                    'enabled': True,
                }
            },

            # Pair.get('BABYDOGE-USDT'): {
            #     PairSettings: {
            #         'is_enabled': True,
            #         'is_autoorders_enabled': True,
            #         'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
            #         'custom_price': 0,
            #         'deviation':  0.01,
            #         'precisions': ['1', '0.1', '0.01', '0.001', '0.0001', '0.00001', '0.000001', '0.0000001', '0.00000001', '0.000000001', '0.0000000001', '0.00000000001']
            #     },
            #     BotConfig : {
            #         'name': 'BABYDOGE-USDT',
            #         'user': bot,
            #         'strategy': BotConfig.TRADE_STRATEGY_DRAW,
            #         'instant_match': True,
            #         'ohlc_period': 5,
            #         'loop_period_random': True,
            #         'min_period': 5,
            #         'max_period': 10,
            #         'ext_price_delta': 0,
            #         'min_order_quantity': 1,
            #         'max_order_quantity': 10000000,
            #         'low_orders_max_match_size': 0.0029,
            #         'low_orders_spread_size': 200,
            #         'low_orders_min_order_size': 0.000000001,  # Giảm giá trị này nếu cần
            #         'enabled': True
            #     }

            # },
            Pair.get('TON-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0.98000000,
                    'precisions': ['100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'TON-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,
                    'max_order_quantity': 10000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },
            Pair.get('DOGE-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0.98000000,
                    'precisions': ['100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'DOGE-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,
                    'max_order_quantity': 1000000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },

            Pair.get('ETC-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['1000','100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'ETC-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,
                    'max_order_quantity': 100000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },

            Pair.get('FTM-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'FTM-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,
                    'max_order_quantity': 100000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },

            Pair.get('DAI-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0,
                    'deviation': 0.98000000,
                    'precisions': ['100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'DAI-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 1,
                    'max_order_quantity': 100000,
                    'low_orders_max_match_size':1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },


            Pair.get('BTC-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0,
                    'deviation': 0.99000000,
                    'precisions': ['1000000','100000','10000','1000','100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'BTC-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 75,
                    'max_period': 280,
                    'ext_price_delta': 0.001,
                    'min_order_quantity': 0.001,
                    'max_order_quantity': 0.1,
                    'low_orders_max_match_size': 0.0029,
                    'low_orders_spread_size': 200,
                    'low_orders_min_order_size': 0.0003,
                    'enabled': True,
                }
            },
            Pair.get('ETH-USDT'): {
                PairSettings: {
                    'is_enabled': True,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0,
                    'deviation': 0.98000000,
                    'precisions': ['10000','1000','100', '10', '1', '0.1', '0.01']
                },
                BotConfig: {
                    'name': 'ETH-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 5,
                    'loop_period_random': True,
                    'min_period': 61,
                    'max_period': 208,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 0.03,
                    'max_order_quantity': 5.02,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': True,
                }
            },
            Pair.get('TRX-USDT'): {
                PairSettings: {
                    'is_enabled': IS_TRON,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0.0,
                    'precisions': ['100','10','1','0.1','0.01', '0.001', '0.0001', '0.00001', '0.000001']
                },
                BotConfig: {
                    'name': 'TRX-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': False,
                    'min_period': 60,
                    'max_period': 180,
                    'ext_price_delta': 0.001,
                    'min_order_quantity': 100,
                    'max_order_quantity': 10_000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_TRON,
                }
            },
            Pair.get('BNB-USDT'): {
                PairSettings: {
                    'is_enabled': IS_BSC,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0,
                    'deviation': 0,
                    'precisions': ['10000','1000','100', '10', '1', '0.1', '0.01'],
                },
                BotConfig: {
                    'name': 'BNB-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': False,
                    'min_period': 10,
                    'max_period': 180,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 0.01,
                    'max_order_quantity': 0.5, 
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_BSC,
                }
            },
            Pair.get('MATIC-USDT'): {
                PairSettings: {
                    'is_enabled': IS_MATIC,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['100','10', '1', '0.1', '0.01', '0.001'],
                },
                BotConfig: {
                    'name': 'MATIC-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 10,
                    'max_period': 60,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,  
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_MATIC,
                }
            },
            Pair.get('WON-USDT'): {
                PairSettings: {
                    'is_enabled': IS_WON,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_CUSTOM,
                    'custom_price': 0.05,
                    'deviation': 0,
                    'precisions': ['100','10', '1', '0.1', '0.01', '0.001','0.0001','0.00001'],
                },
                BotConfig: {
                    'name': 'WON-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.005,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_WON,
                }
            },
            Pair.get('CELO-USDT'): {
                PairSettings: {
                    'is_enabled': IS_CELO,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['100','10', '1', '0.1', '0.01', '0.001'],
                },
                BotConfig: {
                    'name': 'CELO-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_CELO,
                }
            },
            Pair.get('CORE-USDT'): {
                PairSettings: {
                    'is_enabled': IS_CORE,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['100','10', '1', '0.1', '0.01', '0.001'],
                },
                BotConfig: {
                    'name': 'CORE-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_CORE,
                }
            },
            Pair.get('FUSE-USDT'): {
                PairSettings: {
                    'is_enabled': IS_FUSE,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['100','10', '1', '0.1', '0.01', '0.001'],
                },
                BotConfig: {
                    'name': 'FUSE-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,  
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_FUSE,
                }
            },
            Pair.get('AVAX-USDT'): {
                PairSettings: {
                    'is_enabled': IS_AVAX,
                    'is_autoorders_enabled': True,
                    'price_source': PairSettings.PRICE_SOURCE_EXTERNAL,
                    'custom_price': 0.1,
                    'deviation': 0,
                    'precisions': ['1000','100','10', '1', '0.1', '0.01', '0.001'],
                },
                BotConfig: {
                    'name': 'AVAX-USDT',
                    'user': bot,
                    'strategy': BotConfig.TRADE_STRATEGY_DRAW,
                    'symbol_precision': 6,
                    'quote_precision': 6,
                    'instant_match': True,
                    'ohlc_period': 10,
                    'loop_period_random': True,
                    'min_period': 5,
                    'max_period': 10,
                    'ext_price_delta': 0.002,
                    'min_order_quantity': 10,
                    'max_order_quantity': 10000,
                    'low_orders_max_match_size': 1,
                    'low_orders_spread_size': 1,
                    'low_orders_min_order_size': 1,
                    'enabled': IS_AVAX,
                }
            },
        }

        for pair, model_list in pair_list.items():
            for model, kwargs in model_list.items():
                model.objects.get_or_create(
                    pair=pair,
                    defaults={
                        'pair': pair,
                        **kwargs,
                    }
                )

        # create user for super admin
        name = env('ADMIN_USER', default='admin@exchange.net')
        password = User.objects.make_random_password()
        user = User.objects.filter(username=name).first()
        if not user:
            user = User.objects.create_superuser(name, name, password)
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=True,
                primary=True,
            )
        else:
            user.set_password(password)
            user.save()

        Profile.objects.filter(user=user).update(is_auto_orders_enabled=True)

        to_write.append('Admin Info:')
        to_write.append(f'Email: {name}  Password: {password}')
        to_write.append(f'Master Pass: {settings.ADMIN_MASTERPASS}')
        print(f"password: {password}")

        totp, is_new_totp = TOTPDevice.objects.get_or_create(
            user=user,
            defaults={
                'name': user.email,
            }
        )
        to_write.append(f'2fa token: {totp.config_url}')
        to_write.append('='*10)

        site, site_is_new = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': settings.DOMAIN,
                'name': settings.PROJECT_NAME,
            }
        )
        if not site_is_new:
            site.domain = settings.DOMAIN
            site.name = settings.PROJECT_NAME
            site.save()

        service = BTCCoinService()
        last_processed_block_instance, _ = LastProcessedBlock.objects.get_or_create(
            currency=BTC_CURRENCY
        )
        last_processed_block_instance.block_id = service.get_last_network_block_id()
        last_processed_block_instance.save()

        # btc
        if not Keeper.objects.filter(currency=BTC_CURRENCY).exists():
            btc_info, btc_keeper = generate_btc_multisig_keeper()
            to_write.append('BTC Info')
            to_write.append(f'Keeper address: {btc_keeper.user_wallet.address}')
            to_write.append('private data:')
            to_write.append(json.dumps(btc_info, indent=4))
            to_write.append('='*10)
        else:
            to_write.append('BTC Info')
            to_write.append('Keeper exists, see previous file')
            to_write.append('='*10)

        for currency_id in coin_list:
            # if currency_id in [USDT, BTC, TON, DOGE,PEPE,SHIB,FLOKI,MEME,BABYDOGE]:
            if currency_id in [USDT, BTC, TON, DOGE,MEME,CAKE]:
                continue

            currency = Currency.get(currency_id)
            if not Keeper.objects.filter(currency=currency).exists():
                private_key_keep, k_password, keeper = keeper_create(currency)
                # gas_password, gas_keeper = keeper_create(currency, True)
                private_key_gas, gas_password, gas_keeper = keeper_create(currency, True)
                to_write.append(f'{currency.code} Info')
                to_write.append(f'Keeper address: {keeper.user_wallet.address}, Password: {k_password}')
                to_write.append(f'Keeper Private_key: {private_key_keep}')
                to_write.append(f'++++++++++++++++++++++++++++++++++++++++++++++++')
                to_write.append(f'GasKeeper address: {gas_keeper.user_wallet.address}, Password: {gas_password}')
                to_write.append(f'GasKeeper Private_key_gas: {private_key_gas}')
                to_write.append('='*10)
            else:
                to_write.append(f'{currency.code} Info')
                to_write.append('Keeper and GasKeeper exists, see previous file')
                to_write.append('=' * 10)

        filename = f'save_to_self_and_delete_{int(datetime.now().timestamp())}.txt'
        filename_path = os.path.join(settings.BASE_DIR, filename)
        with open(filename_path, 'a+') as file:
            for line in to_write:
                file.write(line + '\r\n')

        print(
            f'the file {filename} was created, it contains private information, '
            f'please save the file to yourself and delete it from the server'
        )


# def keeper_create(currency, is_gas_keeper=False):

#     wallet_create_fn = CRYPTO_WALLET_CREATORS[currency]
#     kwargs = {'user_id': None, 'is_new': True, 'currency': currency}

#     new_keeper_wallet: UserWallet = wallet_create_fn(**kwargs)
#     if isinstance(new_keeper_wallet, QuerySet):
#         new_keeper_wallet = new_keeper_wallet.first()

#     if not new_keeper_wallet:
#         raise Exception('New wallet was not created')

#     password = None
#     if not is_gas_keeper:
#         password = User.objects.make_random_password()
#         private_key = AESCoderDecoder(settings.CRYPTO_KEY).decrypt(new_keeper_wallet.private_key)
#         encrypted_key = AESCoderDecoder(password).encrypt(private_key)
#         dbl_encrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).encrypt(encrypted_key)
#         new_keeper_wallet.private_key = dbl_encrypted_key
#         new_keeper_wallet.save()

#     KeeperModel = Keeper
#     if is_gas_keeper:
#         # if currency not in [ETH_CURRENCY, TRX_CURRENCY]:
#         #     raise Exception('Only ETH and TRX GasKeeper can be created')
#         KeeperModel = GasKeeper

#     keeper = create_keeper(new_keeper_wallet, KeeperModel)
#     return password, keeper

def keeper_create(currency, is_gas_keeper=False):
    if currency not in CRYPTO_WALLET_CREATORS:
        raise ValueError(f"Unsupported currency: {currency}")

    wallet_create_fn = CRYPTO_WALLET_CREATORS[currency]
    if not callable(wallet_create_fn):
        raise TypeError(f"{wallet_create_fn} is not callable")

    kwargs = {'user_id': None, 'is_new': True, 'currency': currency}

    new_keeper_wallet: UserWallet = wallet_create_fn(**kwargs)
    if isinstance(new_keeper_wallet, QuerySet):
        new_keeper_wallet = new_keeper_wallet.first()

    if not new_keeper_wallet:
        raise Exception('New wallet was not created')

    private_key = None
    password = None
    if not is_gas_keeper:
        password = User.objects.make_random_password()
        private_key = AESCoderDecoder(settings.CRYPTO_KEY).decrypt(new_keeper_wallet.private_key)
        encrypted_key = AESCoderDecoder(password).encrypt(private_key)
        dbl_encrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).encrypt(encrypted_key)
        new_keeper_wallet.private_key = dbl_encrypted_key
        new_keeper_wallet.save()

    KeeperModel = Keeper
    if is_gas_keeper:
        KeeperModel = GasKeeper

    keeper = create_keeper(new_keeper_wallet, KeeperModel)
    return private_key, password, keeper



if __name__ == '__main__':
    print('Start')
    main()
    print('Stop')
