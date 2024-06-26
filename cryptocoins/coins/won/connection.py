from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers import (
    HTTPProvider,
)


def get_w3_won_connection():
    from exchange.settings import env
    w3 = Web3(HTTPProvider(env('WON_RPC_URL', default='https://rpc.wonnetwork.org')))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


w3: Web3 = get_w3_won_connection()
