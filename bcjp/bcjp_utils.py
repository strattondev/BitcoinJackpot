import logging
import numpy as np
import redis
from django.conf import settings
from models import *
from log_utils import LogUtils

def create_round_log(message=None, rnd=None, payment=None, is_bet=False, is_start=False, is_end=False, is_winner=False, bet=None):
    if not message: 
        LogUtils().info('bcjp.file', 'bcjp_utils', 'create_round_log', "NO MESSAGE")
        return
    if not rnd: 
        LogUtils().info('bcjp.file', 'bcjp_utils', 'create_round_log', "NO rnd")
        return
    if not isinstance(rnd, Rounds):
        LogUtils().info('bcjp.file', 'bcjp_utils', 'create_round_log', "NO Rounds")
        return
    if bet and not isinstance(bet, BitcoinBet): 
        LogUtils().info('bcjp.file', 'bcjp_utils', 'create_round_log', "NO BitcoinBet")
        return
    if payment and not isinstance(payment, BitcoinPaymentCompleted): 
        LogUtils().info('bcjp.file', 'bcjp_utils', 'create_round_log', "NO BitcoinPaymentCompleted")
        return

    rl = RoundLog()

    rl.round = rnd
    rl.payment = payment
    rl.message = message
    rl.is_bet = is_bet
    rl.is_start = is_start
    rl.is_end = is_end
    rl.is_winner = is_winner
    rl.bet = bet

    rl.save()

    if bet:
        settings.REDIS_CLIENT.incrby(settings.REDIS_ROUND_CURRENT_AMOUNT, long(bet.amount))

    return rl

def create_round_log_payment(bet=None, bas=None, rnd=None):
    if not bet: 
        raise ValueError("") # Needs to change
    if not isinstance(bet, BitcoinBet):
        raise ValueError("") # Needs to change
    if not rnd: return
    if not isinstance(rnd, Rounds): return

    value = float(bet.amount) / settings.SATOSHI_RATIO

    try:
        bettor = bas.alias
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'bcjp_utils', 'create_round_log_payment', e)
        raise ValueError("") # Needs to change

    message = "{} bet {} BTC".format(bettor, value)

    return create_round_log(message=message, rnd=rnd, bet=bet, is_bet=True)

def create_round_log_secret(rnd=None):
    if not rnd: return
    if not isinstance(rnd, Rounds): return

    message = "Round Secret Hash: {}".format(rnd.secret_hash)

    return create_round_log(message=message, rnd=rnd, is_end=True)

def create_round_log_winning_percent(rnd=None):
    if not rnd: return
    if not isinstance(rnd, Rounds): return

    message = "Round Winning Percent: : {}".format(rnd.winning_percent)

    return create_round_log(message=message, rnd=rnd, is_end=True)

def create_round_log_winner(winner=None):
    if not winner: return
    if not isinstance(winner, RoundWinner): return

    value = float(winner.winnings) / settings.SATOSHI_RATIO

    message = "WE HAVE A WINNER! {} won {} BTC!".format(winner.bitcoin_address_session.alias, value)

    return create_round_log(message=message, rnd=winner.round, is_winner=True)

def create_round_log_new_round(rnd=None):
    if not rnd: return
    if not isinstance(rnd, Rounds): return

    message = "New Round"

    return create_round_log(message=message, rnd=rnd)

def create_round_log_hash(rnd=None):
    if not rnd: return
    if not isinstance(rnd, Rounds): return

    message = "Round Hash: {}".format(rnd.round_hash)

    return create_round_log(message=message, rnd=rnd, is_start=True)

def process_round_bet(bet=None, bas=None):
    if not bet or not bas:
        return

    while settings.REDIS_CLIENT.get(settings.REDIS_ROUND_LOCK):
        settings.REDIS_CLIENT.incrby(settings.REDIS_ROUND_LOCK_COUNT, 1)

    rnd = None

    try:
        rnd = Rounds.objects.get(pk=settings.REDIS_CLIENT.get(settings.REDIS_ROUND_CURRENT_ID))
    except Rounds.DoesNotExist, e:
        # THIS IS VERY SHITTY
        raise e

    try:
        bas.amount -= bet.amount
        bas.save()

        create_round_log_payment(bet, bas, rnd)
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'bcjp_utils', 'process_round_bet', e)
        return

    current_count = settings.REDIS_CLIENT.incrby(settings.REDIS_ROUND_BETS, 1)

    if current_count < 25:
        return

    # Set round lock
    settings.REDIS_CLIENT.set(settings.REDIS_ROUND_LOCK, 1)

    try:
        # Post secret and winning percentage logs
        create_round_log_winning_percent(rnd=rnd)
        create_round_log_secret(rnd=rnd)

        # Get Winner
        winner = get_round_winner(rnd)
        create_round_log_winner(winner=winner)

        # Make new round
        start_up_new_round(True)
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'bcjp_utils', 'process_round_bet', e)
        raise e
    finally:
        settings.REDIS_CLIENT.delete(settings.REDIS_ROUND_LOCK)

def get_round_winner(rnd=None):
    if not rnd: return
    if not isinstance(rnd, Rounds): return
    try:
        bets = RoundLog.objects.filter(round=rnd, is_bet=True)
        current_ticket_point = 0
        total_tickets = long(settings.REDIS_CLIENT.get(settings.REDIS_ROUND_CURRENT_AMOUNT))
        winning_ticket = np.floor(np.multiply((total_tickets - 0.0001), (rnd.winning_percent / 100)))
        winning_bet = None
        winner = None

        for bet in bets:
            current_ticket_point += long(bet.bet.amount) / 0.0001

            if current_ticket_point >= winning_ticket:
                winning_bet = bet
                break

        round_winner = RoundWinner()
        round_winner.round = rnd
        round_winner.bitcoin_address_session = winning_bet.bet.bitcoin_address_session
        round_winner.total = settings.REDIS_CLIENT.get(settings.REDIS_ROUND_CURRENT_AMOUNT)
        round_winner.save()

        winning_bet.bet.bitcoin_address_session.amount += round_winner.winnings
        winning_bet.bet.bitcoin_address_session.save()
    except Exception, e:
        print repr(e)
        raise e

    return round_winner

def start_up_new_round(make_round=False):
    new_round = None

    # If not forced we check to see if the round meets requirements
    if not make_round:
        if not settings.REDIS_CLIENT.get(settings.REDIS_ROUND_CURRENT_ID):
            make_round = True

    # If we should make a round
    if make_round:
        # Generate new round
        new_round = Rounds().save()

        # Post new round log
        create_round_log_new_round(rnd=new_round)
        create_round_log_hash(rnd=new_round)

        # Reset the round count
        settings.REDIS_CLIENT.set(settings.REDIS_ROUND_BETS, 0)
        # Reset round amount
        settings.REDIS_CLIENT.set(settings.REDIS_ROUND_CURRENT_AMOUNT, 0)
        # Set new round
        settings.REDIS_CLIENT.set(settings.REDIS_ROUND_CURRENT_ID, new_round.id)

    return new_round