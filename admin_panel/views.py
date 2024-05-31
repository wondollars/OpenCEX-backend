from functools import wraps

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.transaction import atomic
from django.shortcuts import render, redirect

from admin_panel.forms import BtcApproveAdminForm, EthApproveAdminForm, MakeTopUpForm, TrxApproveAdminForm, \
    BnbApproveAdminForm, MaticApproveAdminForm, WonApproveAdminForm, CeloApproveAdminForm, CoreApproveAdminForm, FuseApproveAdminForm, AvaxApproveAdminForm, EtcApproveAdminForm, FtmApproveAdminForm, DaiApproveAdminForm
from core.consts.currencies import BEP20_CURRENCIES, TRC20_CURRENCIES, ERC20_CURRENCIES, ERC20_MATIC_CURRENCIES, ERC20_WON_CURRENCIES, ERC20_CELO_CURRENCIES, ERC20_FUSE_CURRENCIES, ERC20_CORE_CURRENCIES, ERC20_AVAX_CURRENCIES, ERC20_ETC_CURRENCIES, ERC20_FTM_CURRENCIES,ERC20_DAI_CURRENCIES
from core.models import Transaction
from core.models.inouts.transaction import REASON_MANUAL_TOPUP
from core.utils.wallet_history import create_or_update_wallet_history_item_from_transaction
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
from cryptocoins.tasks.evm import process_payouts_task


@staff_member_required
def make_topup(request):
    if request.method == 'POST':
        form = MakeTopUpForm(request.POST)

        try:
            if form.is_valid():
                currency = form.cleaned_data.get('currency')
                amount = form.cleaned_data.get('amount')
                user = form.cleaned_data.get('user')
                with atomic():
                    tx = Transaction.topup(user.id, currency, amount, {'1': 1}, reason=REASON_MANUAL_TOPUP)
                    create_or_update_wallet_history_item_from_transaction(tx)
                messages.success(request, 'Top-Up completed')
                return redirect('admin_make_topup')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = MakeTopUpForm()

    return render(request, 'admin/form.html', context={
        'form': form,
    })


@staff_member_required
def admin_withdrawal_request_approve(request):
    service = BTCCoinService()
    withdrawal_requests = service.get_withdrawal_requests()

    if request.method == 'POST':
        form = BtcApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                private_key = form.cleaned_data.get('key')
                service.process_withdrawals(private_key=private_key)
                messages.success(request, 'Withdrawal completed')
                return redirect('admin_withdrawal_request_approve_btc')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = BtcApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })


@staff_member_required
def admin_eth_withdrawal_request_approve(request):
    currencies = [ETH_CURRENCY] + list(ERC20_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='ETH')

    if request.method == 'POST':
        form = EthApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['ETH', password,], queue='eth_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_eth')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = EthApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })


@staff_member_required
def admin_trx_withdrawal_request_approve(request):
    currencies = [TRX_CURRENCY] + list(TRC20_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='TRX')

    if request.method == 'POST':
        form = TrxApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['TRX', password, ], queue='trx_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_trx')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = TrxApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })


@staff_member_required
def admin_bnb_withdrawal_request_approve(request):
    currencies = [BNB_CURRENCY] + list(BEP20_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='BNB')

    if request.method == 'POST':
        form = BnbApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['BNB', password, ], queue='bnb_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_bnb')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = BnbApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })


@staff_member_required
def admin_matic_withdrawal_request_approve(request):
    currencies = [MATIC_CURRENCY] + list(ERC20_MATIC_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='MATIC')

    if request.method == 'POST':
        form = MaticApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['MATIC', password, ], queue='matic_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_matic')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = MaticApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_won_withdrawal_request_approve(request):
    currencies = [WON_CURRENCY] + list(ERC20_WON_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='WON')

    if request.method == 'POST':
        form = WonApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['WON', password, ], queue='won_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_won')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = WonApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_celo_withdrawal_request_approve(request):
    currencies = [CELO_CURRENCY] + list(ERC20_CELO_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='CELO')

    if request.method == 'POST':
        form = CeloApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['CELO', password, ], queue='celo_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_celo')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = CeloApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_core_withdrawal_request_approve(request):
    currencies = [CORE_CURRENCY] + list(ERC20_CORE_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='CORE')

    if request.method == 'POST':
        form = CoreApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['CORE', password, ], queue='core_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_core')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = CoreApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_fuse_withdrawal_request_approve(request):
    currencies = [FUSE_CURRENCY] + list(ERC20_FUSE_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='FUSE')

    if request.method == 'POST':
        form = FuseApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['FUSE', password, ], queue='fuse_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_fuse')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = FuseApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_avax_withdrawal_request_approve(request):
    currencies = [AVAX_CURRENCY] + list(ERC20_AVAX_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='AVAX')

    if request.method == 'POST':
        form = AvaxApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['AVAX', password, ], queue='avax_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_avax')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = AvaxApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_etc_withdrawal_request_approve(request):
    currencies = [ETC_CURRENCY] + list(ERC20_ETC_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='ETC')

    if request.method == 'POST':
        form = EtcApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['ETC', password, ], queue='etc_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_etc')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = EtcApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_ftm_withdrawal_request_approve(request):
    currencies = [FTM_CURRENCY] + list(ERC20_FTM_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='FTM')

    if request.method == 'POST':
        form = FtmApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['FTM', password, ], queue='ftm_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_ftm')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = FtmApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
def admin_dai_withdrawal_request_approve(request):
    currencies = [DAI_CURRENCY] + list(ERC20_DAI_CURRENCIES)
    withdrawal_requests = get_withdrawal_requests_to_process(currencies, blockchain_currency='DAI')

    if request.method == 'POST':
        form = DaiApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts_task.apply_async(['DAI', password, ], queue='dai_payouts')
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_dai')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = DaiApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })