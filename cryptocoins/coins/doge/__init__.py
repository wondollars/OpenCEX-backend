from core.currency import TokenParams
from cryptocoins.utils.register import register_token

DOGE = 34
CODE = 'DOGE'
DECIMALS = 18
BLOCKCHAINS = {
    # 'ETH': TokenParams(
    #     symbol=CODE,
    #     contract_address='0xdAC17F958D2ee523a2206206994597C13D831ec7',
    #     decimal_places=6,
    # ),
    'BNB': TokenParams(
        symbol=CODE,
        contract_address='0xbA2aE424d960c26247Dd6c32edC70B295c744C43',
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
DOGE_CURRENCY = register_token(DOGE, CODE, BLOCKCHAINS)
