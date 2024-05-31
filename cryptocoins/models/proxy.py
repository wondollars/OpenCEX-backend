from core.models.inouts.withdrawal import WithdrawalRequest as BaseWithdrawalRequest


class BTCWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True


class ETHWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True


class TRXWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True


class BNBWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True


class MaticWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class WonWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class CeloWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class CoreWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class FuseWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class AvaxWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class EtcWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class FtmWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True

class XdaiWithdrawalApprove(BaseWithdrawalRequest):
    class Meta:
        proxy = True
 
