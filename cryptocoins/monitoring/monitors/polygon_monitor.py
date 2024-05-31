from typing import List

from django.conf import settings

from cryptocoins.monitoring.base_monitor import BaseMonitor
from lib.helpers import to_decimal
from lib.services.polygonscan_client import PolygonscanClient


class PolygonMonitor(BaseMonitor):
    CURRENCY = 'MATIC'
    BLOCKCHAIN_CURRENCY = 'MATIC'
    ACCUMULATION_TIMEOUT = 60 * 10
    DELTA_AMOUNT = to_decimal(0.01)
    SAFE_ADDRESS = settings.MATIC_SAFE_ADDR
    OFFSET_SECONDS = 16

    def get_address_transactions(self, address, *args, **kwargs) -> List:
        """
        Get address transactions from third-party services like etherscan, blockstream etc
        """
        client = PolygonscanClient()
        tx_list = client.get_address_tx_transfers(address)
        return tx_list
