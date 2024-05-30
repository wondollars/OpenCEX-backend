from decimal import Decimal
import json
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
        response = requests.get('https://www.bitstamp.net/api/v2/ticker/')
        data = response.json()
        
        logging.debug(f'Bitstamp API response: {data}')

        pairs_prices = {}
        for ticker in data:
            symbol = ticker['pair'].replace('/', '-')
            pair = Pair.get(symbol)
            if pair:
                pairs_prices[pair] = to_decimal(ticker['last'])
            else:
                logging.warning(f'Pair not found for symbol: {symbol}')
        
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.bitstamp.net/api/v2/ticker/')
        
        if data:
            short_response = data[:3]  # Get the first 3 elements of the data list
            message = f'Datasource provider response bitstapm: {json.dumps(short_response)}'
            send_telegram_message(message)
        else:
            send_telegram_message(f'Datasource provider error bitstapm')
        data = response.json()
        pairs = [ticker['pair'].replace('/', '-') for ticker in data]
        exists = pair_symbol in pairs
        if not exists:
            logging.warning(f'Pair symbol {pair_symbol} not found in Bitstamp data')
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
        response = requests.get('https://www.mexc.com/open/api/v2/market/ticker')
        
        data = {bc['symbol']: bc['last'] for bc in response}
        
        logging.debug(f'MEXC API response: {data}')
        
        pairs_prices = {}

        for pair in Pair.objects.all():
            pair_exchange_key = f'{pair.base.code}-{pair.quote.code}'
            pair_exchange_key = pair_exchange_key.replace('-', '_')
            if pair_exchange_key in data:
                pairs_prices[pair] = to_decimal(data[pair_exchange_key]) 
        
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.mexc.com/open/api/v2/market/ticker')
        
        if data:
            short_response = data[:3]  # Get the first 3 elements of the data list
            message = f'Datasource provider response Mexc: {json.dumps(short_response)}'
            send_telegram_message(message)
        else:
            send_telegram_message(f'Datasource provider error mexc')

        pair_symbol_new = pair_symbol.replace('-', '_')
        data = response.json().get('data', [])
        pairs = [ticker['symbol'] for ticker in data]
        exists = pair_symbol_new in pairs
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
        response = requests.get('https://www.okx.com/api/v5/public/mark-price?instType=SWAP')
        data = response.json().get('data', [])
        
        pairs_prices = {}
        for ticker in data:
            symbol = ticker['instId'].replace('_SWAP', '')
            pair = Pair.get(symbol)
            if pair:
                pairs_prices[pair] = to_decimal(ticker['markPx'])
        
        self._data = pairs_prices
        return pairs_prices

    def is_pair_exists(self, pair_symbol) -> bool:
        response = requests.get('https://www.okx.com/api/v5/public/mark-price?instType=SWAP')
        if data:
            short_response = data[:3]  # Get the first 3 elements of the data list
            message = f'Datasource provider response OK: {json.dumps(short_response)}'
            send_telegram_message(message)
        else:
            send_telegram_message(f'Datasource provider error OK')

        data = response.json().get('data', [])
        pairs = [ticker['instId']   .replace('_SWAP', '') for ticker in data]
        return pair_symbol in pairs

binance_data_source = BinanceDataSource()
kucoin_data_source = KuCoinDataSource()
bitstamp_data_source = BitstampDataSource()
mexc_data_source = MexcDataSource()
okx_data_source = OkxDataSource()

