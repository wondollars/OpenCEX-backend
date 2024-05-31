import logging

from cryptocoins.monitoring.monitors.bep20_monitor import UsdtBnbMonitor
from cryptocoins.monitoring.monitors.bnb_monitor import BnbMonitor
from cryptocoins.monitoring.monitors.btc_monitor import BtcMonitor
from cryptocoins.monitoring.monitors.erc20_monitor import UsdtEthMonitor
from cryptocoins.monitoring.monitors.eth_monitor import EthMonitor
from cryptocoins.monitoring.monitors.trc20_monitor import UsdtTrxMonitor
from cryptocoins.monitoring.monitors.trx_monitor import TrxMonitor
# from cryptocoins.monitoring.monitors.won_monitor import WonMonitor
# from cryptocoins.monitoring.monitors.celo_monitor import CeloMonitor
# from cryptocoins.monitoring.monitors.core_monitor import CoreMonitor
# from cryptocoins.monitoring.monitors.polygon_monitor import PolygonMonitor
# from cryptocoins.monitoring.monitors.fuse_monitor import FuseMonitor
# from cryptocoins.monitoring.monitors.ftm_monitor import FtmMonitor
# from cryptocoins.monitoring.monitors.xdai_monitor import XdaiMonitor
# from cryptocoins.monitoring.monitors.etc_monitor import EtcMonitor

log = logging.getLogger(__name__)

MONITORS = {
    'BTC': BtcMonitor,
    'ETH': EthMonitor,
    'TRX': TrxMonitor,
    'BNB': BnbMonitor,
    # 'WON': WonMonitor,
    # 'ETC': EtcMonitor,
    # 'CELO': CeloMonitor,
    # 'CORE': CoreMonitor,
    # 'FUSE': FuseMonitor,
    # 'FTM': FtmMonitor,
    # 'XDAI': XdaiMonitor,
    # 'MATIC': PolygonMonitor,
    'USDTTRX': UsdtTrxMonitor,
    'USDTETH': UsdtEthMonitor,
    'USDTBNB': UsdtBnbMonitor,
}


class MonitoringProcessor:
    monitors: dict = MONITORS

    @classmethod
    def process(cls, currency):
        Monitor = MONITORS.get(currency)
        if not Monitor:
            raise Exception(f'Monitor not found for {currency}')

        monitor = Monitor()
        log.info(f'Monitoring: processing {monitor.CURRENCY} {monitor.BLOCKCHAIN_CURRENCY}')
        monitor.mark_wallet_transactions()
