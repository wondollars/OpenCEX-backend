import copy
from decimal import Decimal
from typing import Dict, List

from core.cache import external_exchanges_pairs_price_cache
from core.models import PairSettings, ExternalPricesHistory, Settings
from core.models.inouts.pair import Pair
from cryptocoins.default_settings import ALERT_ON_MISSING_EXTERNAL_PAIR_PRICE
from cryptocoins.interfaces.datasources import BaseDataSource
from lib.helpers import calc_relative_percent_difference
from lib.notifications import send_telegram_message

class DataSourcesManager:
    def __init__(self, main_source: BaseDataSource, reserve_sources: List[BaseDataSource]):
        self.main_source: BaseDataSource = main_source
        self.reserve_sources: List[BaseDataSource] = reserve_sources
        self._data: Dict[Pair, Decimal] = {}
        self._restore_old_prices()

    def _restore_old_prices(self):
        for pair in Pair.objects.all():
            self._data[pair] = external_exchanges_pairs_price_cache.get(pair.code)

    def _update_cached_prices(self, new_data=None):
        if not new_data:
            new_data = self._data
        for pair, price in new_data.items():
            external_exchanges_pairs_price_cache.set(pair.code, price)

    def _get_source_data(self, source):
        try:
            return source.get_latest_prices()
        except Exception as e:
            send_telegram_message(f'Datasource provider {source.NAME} error:\n{e}')
            return {}

    def update_prices(self):
        main_source_data = self._get_source_data(self.main_source)
        all_sources_data = main_source_data.copy()

        # Combine data from all reserve sources
        for source in self.reserve_sources:
            reserve_data = self._get_source_data(source)
            all_sources_data.update(reserve_data)

        new_data: Dict[Pair, Decimal] = copy.copy(self._data)

        for pair, old_price in self._data.items():
            # Skip pairs with custom price
            custom_price = PairSettings.get_custom_price(pair)
            if custom_price:
                new_data[pair] = custom_price
                continue

            new_price = all_sources_data.get(pair.code)
            if new_price:
                if not old_price:
                    new_data[pair] = new_price
                    continue

                if calc_relative_percent_difference(old_price, new_price) < self.main_source.MAX_DEVIATION:
                    new_data[pair] = new_price
                else:
                    send_telegram_message(f'{pair.code} price changes more than {self.main_source.MAX_DEVIATION}%.'
                                          f'\nCurrent price is {old_price}, new price: {new_price}')
            else:
                send_telegram_message(f'No price available for {pair.code} in all sources.')

        from core.tasks.orders import run_otc_orders_price_update
        history = []
        for pair in new_data:
            new_price = new_data[pair]
            custom_price = PairSettings.get_custom_price(pair.code)
            price = custom_price or new_price
            if price:
                new_data[pair] = price
                previous_price = self._data[pair]
                if previous_price:
                    percent_difference = calc_relative_percent_difference(price, previous_price)
                    if percent_difference > 0.3:
                        run_otc_orders_price_update.apply_async([pair.code], queue=f'orders.{pair.code}')

                if pair.code in ['BTC-USDT', 'ETH-USDT']:
                    history.append(ExternalPricesHistory(pair=pair, price=price))
        if history:
            ExternalPricesHistory.objects.bulk_create(history)

        self._update_cached_prices(new_data)
        return self._data
