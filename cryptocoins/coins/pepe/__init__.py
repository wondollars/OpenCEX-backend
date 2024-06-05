from core.currency import TokenParams
from cryptocoins.utils.register import register_token

PEPE = 39
CODE = 'PEPE'
DECIMALS = 18
BLOCKCHAINS = {
    # 'ETH': TokenParams(
    #     symbol=CODE,
    #     contract_address='0x6982508145454Ce325dDbE47a25d4ec3d2311933',
    #     decimal_places=18,
    # ),
    'BNB': TokenParams(
        symbol=CODE,
        contract_address='0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00',
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
PEPE_CURRENCY = register_token(PEPE, CODE, BLOCKCHAINS)
