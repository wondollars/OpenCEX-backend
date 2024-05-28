import logging

import requests
from django.conf import settings

from core.consts.currencies import BEP20_WON_CURRENCIES
from core.currency import Currency
from lib.services.etherscan_client import EtherscanClient

log = logging.getLogger(__name__)


class WONscanClient(EtherscanClient):
    def __init__(self):
        self.url = 'https://scan.wonnetwork.org/api?'

    def _make_request(self, uri=''):
        res = {}
        try:
            res = requests.get(
                f'{self.url}{uri}&apikey={settings.WONSCAN_KEY}')
            res = res.json()
        except Exception as e:
            log.exception('Can\'t fetch data from blockchain.info')
        return res

    def get_token_params(self, currency_code):
        return BEP20_WON_CURRENCIES.get(Currency.get(currency_code))
