from admin_rest import restful_admin as api_admin
from admin_rest.mixins import ReadOnlyMixin
from admin_rest.restful_admin import DefaultApiAdmin
from core.consts.currencies import BEP20_CURRENCIES, ERC20_MATIC_CURRENCIES, ERC20_WON_CURRENCIES, ERC20_CELO_CURRENCIES, ERC20_CORE_CURRENCIES, ERC20_FUSE_CURRENCIES, ERC20_AVAX_CURRENCIES,ERC20_ETC_CURRENCIES, ERC20_FTM_CURRENCIES,ERC20_DAI_CURRENCIES
from core.consts.currencies import ERC20_CURRENCIES
from core.consts.currencies import TRC20_CURRENCIES
from core.models import UserWallet
from core.utils.withdrawal import get_withdrawal_requests_to_process
from cryptocoins.coins.bnb import BNB_CURRENCY
from cryptocoins.coins.btc.service import BTCCoinService
from cryptocoins.coins.eth import ETH_CURRENCY
from cryptocoins.coins.matic import MATIC_CURRENCY
from cryptocoins.coins.won import WON_CURRENCY
from cryptocoins.coins.celo import CELO_CURRENCY
from cryptocoins.coins.core import CORE_CURRENCY
from cryptocoins.coins.fuse import FUSE_CURRENCY
from cryptocoins.coins.avax import AVAX_CURRENCY
from cryptocoins.coins.trx import TRX_CURRENCY
from cryptocoins.coins.etc import ETC_CURRENCY
from cryptocoins.coins.ftm import FTM_CURRENCY
from cryptocoins.coins.dai import DAI_CURRENCY
from cryptocoins.models import ScoringSettings
from cryptocoins.models import TransactionInputScore
from cryptocoins.models.proxy import BNBWithdrawalApprove, MaticWithdrawalApprove
from cryptocoins.models.proxy import BTCWithdrawalApprove
from cryptocoins.models.proxy import ETHWithdrawalApprove
from cryptocoins.models.proxy import TRXWithdrawalApprove
from cryptocoins.models.proxy import WonWithdrawalApprove
from cryptocoins.models.proxy import CeloWithdrawalApprove
from cryptocoins.models.proxy import CoreWithdrawalApprove
from cryptocoins.models.proxy import FuseWithdrawalApprove
from cryptocoins.models.proxy import AvaxWithdrawalApprove
from cryptocoins.models.proxy import EtcWithdrawalApprove
from cryptocoins.models.proxy import FtmWithdrawalApprove
from cryptocoins.models.proxy import DaiWithdrawalApprove
 
from cryptocoins.serializers import BNBKeySerializer
from cryptocoins.serializers import BTCKeySerializer
from cryptocoins.serializers import ETHKeySerializer
from cryptocoins.serializers import TRXKeySerializer
from cryptocoins.serializers import MaticKeySerializer
from cryptocoins.serializers import WonKeySerializer
from cryptocoins.serializers import CeloKeySerializer
from cryptocoins.serializers import CoreKeySerializer
from cryptocoins.serializers import FuseKeySerializer
from cryptocoins.serializers import AvaxKeySerializer
from cryptocoins.serializers import EtcKeySerializer
from cryptocoins.serializers import FtmKeySerializer
from cryptocoins.serializers import DaiKeySerializer
 
from cryptocoins.tasks.evm import process_payouts_task


class BaseWithdrawalApprove(ReadOnlyMixin, DefaultApiAdmin):
    list_display = ['user', 'confirmed', 'currency', 'state', 'details', 'amount']
    search_fields = ['user__email', 'data__destination']
    filterset_fields = ['currency']
    global_actions = {
        'process': [{
            'label': 'Password',
            'name': 'key'
        }]
    }

    def details(self, obj):
        return obj.data.get('destination')


@api_admin.register(BTCWithdrawalApprove)
class BTCWithdrawalApproveApiAdmin(BaseWithdrawalApprove):

    def get_queryset(self):
        service = BTCCoinService()
        return service.get_withdrawal_requests()

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        service = BTCCoinService()
        # form = MySerializer(request)
        serializer = BTCKeySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            private_key = request.data.get('key')
            service.process_withdrawals(private_key=private_key)

    process.short_description = 'Process withdrawals'


@api_admin.register(ETHWithdrawalApprove)
class ETHWithdrawalApproveApiAdmin(BaseWithdrawalApprove):

    def get_queryset(self):
        return get_withdrawal_requests_to_process([ETH_CURRENCY, *ERC20_CURRENCIES], blockchain_currency='ETH')

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = ETHKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['ETH', password, ], queue='eth_payouts')

    process.short_description = 'Process withdrawals'


@api_admin.register(TRXWithdrawalApprove)
class TRXWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process([TRX_CURRENCY, *TRC20_CURRENCIES], blockchain_currency='TRX')

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = TRXKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['TRX', password, ], queue='trx_payouts')

    process.short_description = 'Process withdrawals'


@api_admin.register(BNBWithdrawalApprove)
class BNBWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process([BNB_CURRENCY, *BEP20_CURRENCIES], blockchain_currency='BNB')

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = BNBKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['BNB', password, ], queue='bnb_payouts')

    process.short_description = 'Process withdrawals'


@api_admin.register(MaticWithdrawalApprove)
class MaticWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [MATIC_CURRENCY, *ERC20_MATIC_CURRENCIES],
            blockchain_currency='MATIC'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = MaticKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['MATIC', password, ], queue='matic_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(WonWithdrawalApprove)
class WonWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [WON_CURRENCY, *ERC20_WON_CURRENCIES],
            blockchain_currency='WON'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = WonKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['WON', password, ], queue='won_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(CeloWithdrawalApprove)
class CeloWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [CELO_CURRENCY, *ERC20_CELO_CURRENCIES],
            blockchain_currency='CELO'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = CeloKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['CELO', password, ], queue='celo_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(CoreWithdrawalApprove)
class CoreWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [CORE_CURRENCY, *ERC20_CORE_CURRENCIES],
            blockchain_currency='CORE'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = CoreKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['CORE', password, ], queue='core_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(FuseWithdrawalApprove)
class FuseWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [FUSE_CURRENCY, *ERC20_FUSE_CURRENCIES],
            blockchain_currency='FUSE'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = FuseKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['FUSE', password, ], queue='fuse_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(AvaxWithdrawalApprove)
class AvaxWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [AVAX_CURRENCY, *ERC20_AVAX_CURRENCIES],
            blockchain_currency='AVAX'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = AvaxKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['AVAX', password, ], queue='avax_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(EtcWithdrawalApprove)
class EtcWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [ETC_CURRENCY, *ERC20_ETC_CURRENCIES],
            blockchain_currency='ETC'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = EtcKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['ETC', password, ], queue='etc_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(FtmWithdrawalApprove)
class FtmWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [FTM_CURRENCY, *ERC20_FTM_CURRENCIES],
            blockchain_currency='FTM'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = FtmKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['FTM', password, ], queue='ftm_payouts')

    process.short_description = 'Process withdrawals'

@api_admin.register(DaiWithdrawalApprove)
class DaiWithdrawalApproveApiAdmin(BaseWithdrawalApprove):
    def get_queryset(self):
        return get_withdrawal_requests_to_process(
            [DAI_CURRENCY, *ERC20_DAI_CURRENCIES],
            blockchain_currency='DAI'
        )

    @api_admin.action(permissions=True)
    def process(self, request, queryset):
        serializer = DaiKeySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data.get('key')
            process_payouts_task.apply_async(['DAI', password, ], queue='dai_payouts')

    process.short_description = 'Process withdrawals'


@api_admin.register(TransactionInputScore)
class TransactionInputScoreAdmin(ReadOnlyMixin, DefaultApiAdmin):
    vue_resource_extras = {'title': 'Transaction Input Score'}
    list_filter = ('deposit_made', 'accumulation_made', 'currency', 'token_currency')
    list_display = ('created', 'hash', 'address', 'user', 'score', 'currency',
                    'token_currency', 'deposit_made', 'accumulation_made', 'scoring_state')
    search_fields = ('address', 'hash')
    filterset_fields = ['created', 'currency', 'token_currency', 'deposit_made']
    ordering = ('-created',)

    def user(self, obj):
        wallet = UserWallet.objects.filter(address=obj.address).first()
        if wallet:
            return wallet.user.email
        return None


@api_admin.register(ScoringSettings)
class ScoringSettingsAdmin(DefaultApiAdmin):
    vue_resource_extras = {'title': 'Scoring Settings'}
    list_display = ('currency', 'min_score', 'deffered_scoring_time', 'min_tx_amount')
    readonly_fields = ('id',)
