from core.currency import TokenParams
from cryptocoins.utils.register import register_token

TON = 35
CODE = 'TON'
DECIMALS = 2
BLOCKCHAINS = {
    # 'ETH': TokenParams(
    #     symbol=CODE,
    #     contract_address='0x582d872a1b094fc48f5de31d3b73f2d9be47def1',
    #     decimal_places=6,
    # ),
    'BNB': TokenParams(
        symbol=CODE,
        contract_address='0x76A797A59Ba2C17726896976B7B3747BfD1d220f',
        decimal_places=18,
    ),
    # 'TRX': TokenParams(
    #     symbol=CODE,
    #     contract_address='TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    #     decimal_places=6,
    #     origin_energy_limit=10000000,
    #     consume_user_resource_percent=30,
    # ),
    # 'WON': TokenParams(
    #     symbol=CODE,
    #     contract_address='0x30F9BcAf63A4A614afd250FE72ecd87d7856dec5',
    #     decimal_places=18,
    # ),
}
TON_CURRENCY = register_token(TON, CODE, BLOCKCHAINS)
