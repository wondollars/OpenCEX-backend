from cryptos import Bitcoin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cryptocoins.coins.bnb.bnb import bnb_manager
from cryptocoins.coins.eth.ethereum import ethereum_manager
from cryptocoins.coins.matic.polygon import matic_manager
from cryptocoins.coins.won.won import won_manager
from cryptocoins.coins.celo.celo import celo_manager
from cryptocoins.coins.core.core import core_manager
from cryptocoins.coins.fuse.fuse import fuse_manager
from cryptocoins.coins.avax.avax import avax_manager
from cryptocoins.coins.etc.etc import etc_manager
from cryptocoins.coins.ftm.ftm import ftm_manager
from cryptocoins.coins.dai.dai import dai_manager
from cryptocoins.coins.trx.tron import tron_manager
from lib.cipher import AESCoderDecoder

CryptoBitcoin = Bitcoin()


class BaseKeySerializer(serializers.Serializer):
    key = serializers.CharField(max_length=255)

    def get_encrypted_string(self):
        raise NotImplementedError

    def validate_key(self, key):
        if not key:
            raise ValidationError("Bad password!")

        try:
            to_check_string = self.get_encrypted_string()
            res = AESCoderDecoder(key).decrypt(to_check_string)
            if not res:
                raise ValidationError("Bad private key")
        except Exception as e:
            raise ValidationError("Bad password!")

        return key


class BTCKeySerializer(BaseKeySerializer):
    def validate_key(self, key):
        if len(key) != 52:
            raise ValidationError("Bad format private key!")

        if key[0] not in ['K', 'L']:
            raise ValidationError("Bad format private key.")

        try:
            CryptoBitcoin.privtopub(key)
        except AssertionError as e:
            raise ValidationError("Bad format private key")

        return key


class ETHKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return ethereum_manager.get_keeper_wallet().private_key


class TRXKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return tron_manager.get_keeper_wallet().private_key


class BNBKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return bnb_manager.get_keeper_wallet().private_key


class MaticKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return matic_manager.get_keeper_wallet().private_key
    
class WonKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return won_manager.get_keeper_wallet().private_key

class CeloKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return celo_manager.get_keeper_wallet().private_key
    
class CoreKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return core_manager.get_keeper_wallet().private_key
    
class FuseKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return fuse_manager.get_keeper_wallet().private_key
    
class AvaxKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return avax_manager.get_keeper_wallet().private_key
    
class EtcKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return etc_manager.get_keeper_wallet().private_key
    
class FtmKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return ftm_manager.get_keeper_wallet().private_key
    
class DaiKeySerializer(BaseKeySerializer):
    def get_encrypted_string(self):
        return dai_manager.get_keeper_wallet().private_key
    
 

