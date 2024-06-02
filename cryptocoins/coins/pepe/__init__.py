from core.currency import TokenParams
from cryptocoins.utils.register import register_token

PEPE = 39
CODE = 'PEPE'
DECIMALS = 18
BLOCKCHAINS = {
    'BNB': TokenParams(
        symbol=CODE,
        contract_address='0x6982508145454Ce325dDbE47a25d4ec3d2311933',
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
PEPE_CURRENCY = register_token(PEPE, CODE, BLOCKCHAINS)
