from typing import List

from django.conf import settings

from cryptocoins.monitoring.base_monitor import BaseMonitor
from lib.helpers import to_decimal
from lib.services.daiscan_client import DaiscanClient


class DaiMonitor(BaseMonitor):
    CURRENCY = 'DAI'
    BLOCKCHAIN_CURRENCY = 'DAI'
    ACCUMULATION_TIMEOUT = 60 * 10
    DELTA_AMOUNT = to_decimal(0.01)
    SAFE_ADDRESS = settings.DAI_SAFE_ADDR
    OFFSET_SECONDS = 16

    def get_address_transactions(self, address, *args, **kwargs) -> List:
        """
        Get address transactions from third-party services like etherscan, blockstream etc
        """
        client = DaiscanClient()
        tx_list = client.get_address_tx_transfers(address)
        return tx_list
