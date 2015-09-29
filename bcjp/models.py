import hashlib
import uuid
import numpy as np
import random
from blockchain import receive
from datetime import datetime
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from log_utils import LogUtils

class BitcoinAddressSession(models.Model):
    address = models.CharField(max_length=255, unique=True)
    session = models.CharField(max_length=255, default="")
    created_on = models.DateTimeField(auto_now_add=True)
    amount = models.BigIntegerField(default=0)
    alias = models.CharField(max_length=255, default=random.choice(settings.ALIAS_WORDS))
    withdraw_address = models.CharField(max_length=255, default=None, null=True)

    class Meta:
        db_table = "bitcoin_address_session"

    def save(self, *args, **kwargs):
        if not self.pk:
            first48 = "{}{}".format(uuid.uuid4(), uuid.uuid4()).replace("-", "")[:48]
            md5 = hashlib.md5()
            md5.update("{}{}".format(settings.SECRET_KEY, first48))
            reverse_track = reverse('betting_track', kwargs={'secret': md5.hexdigest(), 'first48': first48})
            try:
                recv = receive.receive(settings.BITCOIN_JACKPOT_ADDRESS, '{}{}'.format(settings.BASE_DOMAIN, reverse_track))
            except Exception, e:
                LogUtils().error('bcjp.file', 'models', 'BitcoinAddressSession', e)
                raise e
                
            LogUtils().info('bcjp.file', 'models', 'BitcoinAddressSession', "{}".format(recv.callback_url))
            self.address = recv.input_address
            self.alias = random.choice(settings.ALIAS_WORDS).title()

            super(BitcoinAddressSession, self).save(*args, **kwargs)

            self.session = "{}-{}".format(self.pk, first48)


        super(BitcoinAddressSession, self).save(*args, **kwargs)
        return self

class BitcoinBet(models.Model):
    bitcoin_address_session = models.ForeignKey(BitcoinAddressSession)
    amount = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitcoin_bet"

    def save(self, *args, **kwargs):
        LogUtils().info('bcjp.file', 'models', 'BitcoinBet', "Attempting to save BitcoinBet with bitcoin_address_session.id {} for amount {}".format(self.bitcoin_address_session.pk, self.amount))
        super(BitcoinBet, self).save(*args, **kwargs)

class Rounds(models.Model):
    secret_hash = models.CharField(max_length=48, unique=True)
    winning_percent = models.FloatField(default=(np.random.random_sample()*100)+1)
    round_hash = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rounds"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.secret_hash = "{}{}".format(uuid.uuid4(), uuid.uuid4()).replace("-", "")[:48]
            self.winning_percent = (np.random.random_sample()*100)+1
            md5 = hashlib.md5()
            md5.update("{}-{}".format(self.secret_hash, self.winning_percent))
            self.round_hash = md5.hexdigest()
            LogUtils().info('bcjp.file', 'models', 'Rounds', "Attempting to save Rounds with hash {}".format(self.round_hash))

        super(Rounds, self).save(*args, **kwargs)
        return self

class BitcoinPaymentPending(models.Model):
    """
    We will only accept bets that will have at least 6 confirmations

    This model will track each of the incoming confirmations < 6
    """
    value = models.BigIntegerField(default=0)
    input_address = models.CharField(max_length=255)
    confirmations = models.IntegerField(default=0)
    transaction_hash = models.CharField(max_length=255)
    input_transaction_hash = models.CharField(max_length=255)
    destination_address = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitcoin_payment_pending"

    def save(self, *args, **kwargs):
        LogUtils().info('bcjp.file', 'models', 'BitcoinPaymentPending', "Attempting to save payment with {} confirmations and hash {}".format(self.confirmations, self.transaction_hash))
        super(BitcoinPaymentPending, self).save(*args, **kwargs)

class BitcoinPaymentCompleted(models.Model):
    value = models.BigIntegerField(default=0)
    input_address = models.CharField(max_length=255)
    confirmations = models.IntegerField(default=6)
    transaction_hash = models.CharField(max_length=255)
    input_transaction_hash = models.CharField(max_length=255)
    destination_address = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitcoin_payment_completed"

    def save(self, *args, **kwargs):
        LogUtils().info('bcjp.file', 'models', 'BitcoinPaymentCompleted', "Attempting to save payment with {} confirmations and hash {}".format(self.confirmations, self.transaction_hash))
        super(BitcoinPaymentCompleted, self).save(*args, **kwargs)

class RoundLog(models.Model):
    round = models.ForeignKey(Rounds)
    payment = models.ForeignKey(BitcoinPaymentCompleted, default=None, null=True)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_bet = models.BooleanField(default=False)
    is_start = models.BooleanField(default=False) # Will be the round hash line
    is_end = models.BooleanField(default=False) # Will be the winning percent, and secret line
    is_winner = models.BooleanField(default=False) # Will be the winner line
    bet = models.ForeignKey(BitcoinBet, default=None, null=True)

    class Meta:
        db_table = "round_log"

class RoundWinner(models.Model):
    round = models.ForeignKey(Rounds)
    bitcoin_address_session = models.ForeignKey(BitcoinAddressSession)
    total = models.BigIntegerField(default=0)
    cut = models.BigIntegerField(default=0)
    winnings = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "round_winner"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.cut = float(self.total) * settings.ROUND_CUT_PERCENT
            self.winnings = float(self.total) * settings.ROUND_WINNING_PERCENT

        return super(RoundWinner, self).save(*args, **kwargs)

class BitcoinWithdrawRequest(models.Model):
    bitcoin_address_session = models.ForeignKey(BitcoinAddressSession)
    amount = models.BigIntegerField(default=0)
    to_address = models.CharField(max_length=255)
    from_address = models.CharField(max_length=255, default=settings.BITCOIN_JACKPOT_ADDRESS)
    created_on = models.DateTimeField(auto_now_add=True)
    transaction_hash = models.CharField(max_length=255)

    class Meta:
        db_table = "bitcoin_withdraw_request"

    def save(self, *args, **kwargs):
        LogUtils().info('bcjp.file', 'models', 'BitcoinWithdrawRequest', "Withdraw request made bitcoin_address_session.id {} amount {} to {}".format(self.bitcoin_address_session.id, self.amount, self.to_address))
        super(BitcoinWithdrawRequest, self).save(*args, **kwargs)

class AdminOverride(models.Model):
    uuid = models.CharField(max_length=36, default="{}".format(uuid.uuid4()), primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True)

    class Meta:
        db_table = "admin_override"

class AdminBitcoinAddressSession(models.Model):
    bitcoin_address_session = models.OneToOneField(BitcoinAddressSession,
                                                    on_delete=models.CASCADE,
                                                    primary_key=True)

    class Meta:
        db_table = "admin_bitcoin_address_session"

class AdminBitcoinBet(models.Model):
    bitcoin_bet = models.OneToOneField(BitcoinBet,
                                                    on_delete=models.CASCADE,
                                                    primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_bitcoin_bet"