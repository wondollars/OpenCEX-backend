from decimal import Decimal
from typing import Dict
import logging

import requests
from binance.client import Client as BinanceClient
from django.conf import settings

from core.cache import cryptocompare_pairs_price_cache
from core.models.inouts.pair import Pair
from cryptocoins.interfaces.datasources import BaseDataSource
from lib.helpers import to_decimal
from lib.notifications import send_telegram_message


class BinanceDataSource(BaseDataSource):
    NAME = 'Binance'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        binance_client = BinanceClient()
        binance_pairs_data = {bc['symbol']: bc['price'] for bc in binance_client.get_all_tickers()}
        pairs_prices = {}
        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}{pair.quote.code}'
            if pair_exchange_key in binance_pairs_data:
                pairs_prices[pair] = to_decimal(binance_pairs_data[pair_exchange_key])
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        binance_client = BinanceClient()
        binance_pairs = [bc['symbol'] for bc in binance_client.get_all_tickers()]
        base, quote = pair_symbol.split('-')
        return f'{base}{quote}' in binance_pairs



class CryptocompareDataSource(BaseDataSource):
    """
    Uses cached values
    """
    NAME = 'Cryptocompare'
    MAX_DEVIATION = settings.CRYPTOCOMPARE_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        pairs_prices = {}
        for pair in Pair.objects.all():
            pairs_prices[pair] = cryptocompare_pairs_price_cache.get(pair)
        self._data = pairs_prices
        return pairs_prices


class KuCoinDataSource(BaseDataSource):
    NAME = 'KuCoin'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        data = requests.get('https://api.kucoin.com/api/v1/market/allTickers').json()['data']['ticker']
        kucoin_prices_data = {bc['symbol']: bc['last'] for bc in data}

        pairs_prices = {}
        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}-{pair.quote.code}'
            if pair_exchange_key in kucoin_prices_data:
                pairs_prices[pair] = to_decimal(kucoin_prices_data[pair_exchange_key])
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        data = requests.get('https://api.kucoin.com/api/v1/market/allTickers').json()['data']['ticker']
        kucoin_pairs = [bc['symbol'] for bc in data]
        return pair_symbol in kucoin_pairs

class BitstampDataSource(BaseDataSource):
    NAME = 'Bitstamp'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        response = requests.get('https://www.bitstamp.net/api/v2/ticker/').json()
        bitstamp_prices_data = {bc['pair']: bc['last'] for bc in response}             
        pairs_prices = {}
        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}/{pair.quote.code}'
            if pair_exchange_key in bitstamp_prices_data:
                pairs_prices[pair] = to_decimal(bitstamp_prices_data[pair_exchange_key])
        self._data = pairs_prices
        return pairs_prices
        

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.bitstamp.net/api/v2/ticker/').json()
        bitstamp_pairs = [bc['pair'].replace('/', '-') for bc in response]       
    
        exists = pair_symbol in bitstamp_pairs
        if not exists:
            logging.warning(f'Pair symbol {pair_symbol} not found in MEXC data')
        return exists
      
class MexcDataSource(BaseDataSource):
    NAME = 'MEXC'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        response = requests.get('https://www.mexc.com/open/api/v2/market/ticker').json()['data']
        mexc_prices_data = {bc['symbol']: bc['last'] for bc in response}    
        
        pairs_prices = {}
        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}_{pair.quote.code}'
            if pair_exchange_key in mexc_prices_data:
                pairs_prices[pair] = to_decimal(mexc_prices_data[pair_exchange_key])
        self._data = pairs_prices
        send_telegram_message(f'mexc_prices_data {pairs_prices}')
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.mexc.com/open/api/v2/market/ticker').json()['data']
        mexc_pairs = [bc['symbol'].replace('_', '-') for bc in response]       
    
        exists = pair_symbol in mexc_pairs
        if not exists:
            logging.warning(f'Pair symbol {pair_symbol} not found in MEXC data')
        return exists

class OkxDataSource(BaseDataSource):
    NAME = 'OKX'
    MAX_DEVIATION = settings.EXTERNAL_PRICES_DEVIATION_PERCENTS

    def __init__(self):
        self._data: Dict[Pair, Decimal] = {}

    @property
    def data(self) -> Dict[Pair, Decimal]:
        return self._data

    def get_latest_prices(self) -> Dict[Pair, Decimal]:
        response = requests.get('https://www.okx.com/api/v5/public/mark-price?instType=SWAP').json()['data']
        okx_prices_data = {bc['instId'].replace('-SWAP', ''): bc['markPx'] for bc in response}            
        pairs_prices = {}
        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}-{pair.quote.code}'
            if pair_exchange_key in okx_prices_data:
                pairs_prices[pair] = to_decimal(okx_prices_data[pair_exchange_key])
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.okx.com/api/v5/public/mark-price?instType=SWAP').json()['data']
        okx_pairs = [bc['instId'].replace('-SWAP', '') for bc in response]         
        exists = pair_symbol in okx_pairs
        if not exists:
            logging.warning(f'Pair symbol {pair_symbol} not found in MEXC data')
        return exists

binance_data_source = BinanceDataSource()
kucoin_data_source = KuCoinDataSource()
bitstamp_data_source = BitstampDataSource()
mexc_data_source = MexcDataSource()
okx_data_source = OkxDataSource()

