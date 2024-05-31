from core.currency import TokenParams
from cryptocoins.utils.register import register_token

BABYDOGE = 44
CODE = 'BABYDOGE'
DECIMALS = 18
BLOCKCHAINS = {
    'ETH': TokenParams(
        symbol=CODE,
        contract_address='0xAC57De9C1A09FeC648E93EB98875B212DB0d460B',
        decimal_places=18,
    ),
    # 'BNB': TokenParams(
    #     symbol=CODE,
    #     contract_address='0xbA2aE424d960c26247Dd6c32edC70B295c744C43',
    #     decimal_places=18,
    # ),
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
BABYDOGE_CURRENCY = register_token(BABYDOGE, CODE, BLOCKCHAINS)
