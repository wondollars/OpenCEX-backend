import logging
import secrets

from django.conf import settings
from django.db import transaction
from eth_account import Account
from web3 import Web3

from cryptocoins.coins.core.consts import CORE
from lib.cipher import AESCoderDecoder

log = logging.getLogger(__name__)


def create_core_address():
    while 1:
        private_key = Web3.to_hex(secrets.token_bytes(32))
        account = Account.from_key(private_key)

        encrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).encrypt(
            private_key
        )
        decrypted_key = AESCoderDecoder(settings.CRYPTO_KEY).decrypt(encrypted_key)

        if decrypted_key.startswith('0x') and len(decrypted_key) == 66:
            break

    return account.address, encrypted_key


@transaction.atomic
def get_or_create_core_wallet(user_id, is_new=False):
    """
    Make new user wallet and related objects if not exists
    """
    # implicit logic instead of get_or_create
    from core.models.cryptocoins import UserWallet

    user_wallet = UserWallet.objects.filter(
        user_id=user_id,
        currency=CORE,
        blockchain_currency=CORE,
    ).order_by('-id').first()

    if not is_new and user_wallet is not None:
        return user_wallet

    address, encrypted_key = create_core_address()

    user_wallet = UserWallet.objects.create(
        user_id=user_id,
        currency=CORE,
        address=address,
        private_key=encrypted_key,
        blockchain_currency=CORE,
    )

    return user_wallet


@transaction.atomic
def get_or_create_erc20_core_wallet(user_id, token_currency, is_new=False):
    from core.models.cryptocoins import UserWallet

    erc20_core_wallet = UserWallet.objects.filter(
        user_id=user_id,
        currency=token_currency,
        blockchain_currency=CORE,
    ).order_by('-id').first()

    if not is_new and erc20_core_wallet is not None:
        return erc20_core_wallet

    address, encrypted_key = create_core_address()

    erc20_core_wallet = UserWallet.objects.create(
        user_id=user_id,
        address=address,
        private_key=encrypted_key,
        currency=token_currency,
        blockchain_currency=CORE,
    )

    return erc20_core_wallet


def is_valid_core_address(address):
    return Web3.is_address(address)


def core_wallet_creation_wrapper(user_id, is_new=False, **kwargs):
    from core.models.cryptocoins import UserWallet

    wallet = get_or_create_core_wallet(
        user_id,
        is_new=is_new,
    )
    return UserWallet.objects.filter(id=wallet.id)


def erc20_core_wallet_creation_wrapper(user_id, currency, is_new=False, **kwargs):
    from core.models.cryptocoins import UserWallet

    wallet = get_or_create_erc20_core_wallet(
        user_id,
        token_currency=currency,
        is_new=is_new,
    )
    return UserWallet.objects.filter(id=wallet.id)
