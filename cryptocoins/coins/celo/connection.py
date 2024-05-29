from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers import (
    HTTPProvider,
)


def get_w3_celo_connection():
    from exchange.settings import env
    w3 = Web3(HTTPProvider(env('CELO_RPC_URL', default='https://rpc.celonetwork.org')))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


w3: Web3 = get_w3_celo_connection()
