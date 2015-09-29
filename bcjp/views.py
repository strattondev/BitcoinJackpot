import hashlib
import numpy as np
import re
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Sum
from urlparse import urlparse
from blockchain.wallet import Wallet
from blockchain.exceptions import *

from models import *
from bcjp_utils import create_round_log_payment, process_round_bet
from log_utils import LogUtils

def index(request):
    try:
        bas = BitcoinAddressSession.objects.get(pk=request.session["bas"])
    except:
        bas = BitcoinAddressSession().save()

    request.session['was_redirect'] = True
    return redirect('index_with_secret', secret_id=bas.session)

def index_with_secret(request, secret_id=None):
    if not secret_id:
        return redirect('index')

    was_redirect = request.session.get('was_redirect', False)
    hide_how_it_works = request.session.get('hide_how_it_works', False)

    if was_redirect:
        del request.session['was_redirect']

    if request.session.get('last_log_id', False):
        del request.session['last_log_id']

    try:
        bas = BitcoinAddressSession.objects.get(session=secret_id)
        request.session["bas"] = bas.id
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'views', 'index_with_secret', e)
        return redirect('index')

    return render(request, 'bcjp/index.html', {"bas": bas, "was_redirect": was_redirect, "hide_how_it_works": hide_how_it_works, "is_educational": settings.IS_EDUCATIONAL})

def about(request):
    return render(request, 'bcjp/about.html', {})

def provably(request):
    return render(request, 'bcjp/provably_fair.html', {})

def terms_and_conditions(request):
    return render(request, 'bcjp/terms_and_conditions.html', {})

def first_time(request):
    return render(request, 'bcjp/first_time.html', {})

def betting_log(request):
    return render(request, 'bcjp/index.html', {})

def betting_track(request, secret=None, first48=None):
    """The callback url that is utilized for Blockchain.info API

    """
    confirmations = request.GET.get("confirmations", -1)

    try:
        confirmations = int(confirmations)
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'views', 'betting_track', e)
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*not an integer*")
        return HttpResponse("*not an integer*")

    if confirmations < 0 or not secret or not first48:
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*invalid params*")
        return HttpResponse("*invalid params*")
    elif confirmations < 6:
        payment = BitcoinPaymentPending()
    else:
        payment = BitcoinPaymentCompleted()

    md5 = hashlib.md5()
    md5.update("{}{}".format(settings.SECRET_KEY, first48))

    if md5.hexdigest() != secret:
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*invalid secret*")
        return HttpResponse("*invalid secret*")

    payment.value = request.GET.get('value', 0)
    payment.input_address = request.GET.get('input_address', 0)
    payment.confirmations = confirmations
    payment.transaction_hash = request.GET.get('transaction_hash', 0)
    payment.input_transaction_hash = request.GET.get('input_transaction_hash', 0)
    payment.destination_address = request.GET.get('destination_address', 0)
    payment.save()

    try:
        bitcoin_address_session = BitcoinAddressSession.objects.get(address=payment.input_address, session__iendswith=first48)
        bitcoin_address_session.amount += long(payment.value)
        bitcoin_address_session.save()
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'views', 'betting_track', e)
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*there was an error*")
        return HttpResponse("*there was an error*")

    if payment.confirmations >= 6:
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*ok*")
        return HttpResponse("*ok*")
    else:
        LogUtils().info('bcjp.file', 'views', 'betting_track', "*not enough confirmations*")
        return HttpResponse("*not enough confirmations*")

def betting_withdraw(request):
    if request.method == "POST":
        jsonRtn = {"success": True}

        try:
            bitcoin_address_session = BitcoinAddressSession.objects.get(pk=request.session["bas"])
            withdraw_address = request.POST.get('ig-address-text', None)
            withdraw_amount = request.POST.get('ig-amount-text', None)
            withdraw_lock = None

            if not withdraw_address or not withdraw_amount:
                raise ValueError("Please enter address and amount")
            if bitcoin_address_session.amount == 0:
                raise ValueError("Could not withdraw. Your current balance is 0 BTC.")

            withdraw_amount = float(withdraw_amount) * settings.SATOSHI_RATIO

            if withdraw_amount > bitcoin_address_session.amount:
                raise ValueError("You cannot withdraw more than your current balance.")

            if withdraw_amount < (0.0001 * settings.SATOSHI_RATIO):
                raise ValueError("Minimum withdrawal amount is 0.0001 BTC.")

            withdraw_lock = "{}{}".format(settings.REDIS_WITHDRAW_LOCK_PREFIX, bitcoin_address_session.id)

            while settings.REDIS_CLIENT.get(withdraw_lock):
                settings.REDIS_CLIENT.incrby(settings.REDIS_WITHDRAW_LOCK_COUNT, 1)

            settings.REDIS_CLIENT.set(withdraw_lock, 1)

            wallet = Wallet(settings.BITCOIN_PRIVATE_ADDRESS, None)
            wallet_withdraw = wallet.send(withdraw_address, withdraw_amount)

            withdraw_request = BitcoinWithdrawRequest()
            withdraw_request.bitcoin_address_session = bitcoin_address_session
            withdraw_request.amount = withdraw_amount
            withdraw_request.to_address = withdraw_address
            withdraw_request.transaction_hash = wallet_withdraw.tx_hash
            withdraw_request.save()

            bitcoin_address_session.amount -= withdraw_amount
            bitcoin_address_session.save()

            jsonRtn["message"] = wallet_withdraw.message
        except APIException, apie:
            LogUtils().info('bcjp.file', 'views', 'betting_withdraw', "APIException")
            jsonRtn["success"] = False
            jsonRtn["message"] = str(apie)
        except ValueError, ve:
            LogUtils().info('bcjp.file', 'views', 'betting_withdraw', "ValueError")
            jsonRtn["success"] = False
            jsonRtn["message"] = str(ve)
        except Exception, e:
            LogUtils().error('bcjp.warning_file', 'views', 'betting_withdraw', e)
            jsonRtn["success"] = False
            jsonRtn["message"] = "Your withdraw could not be processed please try again."
        finally:
            if withdraw_lock:
                settings.REDIS_CLIENT.delete(withdraw_lock)
        
        return JsonResponse(jsonRtn)

    # request.method == GET portion
    if not request.session.get("bas", False):
        return render(request, 'bcjp/withdraw.html', {"valid": False, "message": "There was an issue with your request. Please try again!"})

    try:
        bitcoin_address_session = BitcoinAddressSession.objects.get(pk=request.session["bas"])

        if not bitcoin_address_session.withdraw_address:
            return render(request, 'bcjp/withdraw.html', {"valid": False, "message": "Your account does not have a withdraw account."})
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'views', 'betting_withdraw', e)
        return render(request, 'bcjp/withdraw.html', {"valid": False, "message": "Your session and input address did not align!"})

    return render(request, 'bcjp/withdraw.html', {"valid": not settings.IS_EDUCATIONAL, "amount": float(bitcoin_address_session.amount) / settings.SATOSHI_RATIO, "bas": bitcoin_address_session, "message": "Withdrawals have been disabled as this is the Educational Only version of BitcoinJackpot!"})

def betting_place(request):
    jsonRtn = {"success": True}

    try:
        bitcoin_address_session = BitcoinAddressSession.objects.get(pk=request.session["bas"])
        bet_amount = request.POST.get('ig-bet-text', None)

        try:
            bet_amount = float(bet_amount)
        except:
            raise ValueError("Please enter a valid numerical bet amount.")

        if not bet_amount:
            raise ValueError("Please enter an amount.")
        if bitcoin_address_session.amount == 0:
            raise ValueError("Could not bet. Your current balance is 0<span class='glyphicon glyphicon-btc' aria-hidden='true'></span>.")

        bet_amount = float(bet_amount) * settings.SATOSHI_RATIO

        if bet_amount > bitcoin_address_session.amount:
            raise ValueError("You cannot bet more than your current balance.")

        if bet_amount < (0.0001 * settings.SATOSHI_RATIO):
            raise ValueError("Minimum bet amount is 0.0001<span class='glyphicon glyphicon-btc' aria-hidden='true'></span>.")

        bet = BitcoinBet()
        bet.bitcoin_address_session = bitcoin_address_session
        bet.amount = bet_amount
        bet.save()

        process_round_bet(bet=bet, bas=bitcoin_address_session)

        jsonRtn["message"] = "Your bet of {}<span class='glyphicon glyphicon-btc' aria-hidden='true'></span> has been placed. Good Luck!".format(float(bet_amount) / settings.SATOSHI_RATIO)
    except ValueError, ve:
        jsonRtn["success"] = False
        jsonRtn["message"] = str(ve)
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'view', 'betting_place', e)
        jsonRtn["success"] = False
        jsonRtn["message"] = "Your bet could not be processed please try again."
    
    return JsonResponse(jsonRtn)

def round_log(request):
    """
    Will output a nicely formatted log of the rounds
    """

    try:
        last_id = int(request.session.get("last_log_id", -1))
    except Exception, e:
        last_id = -1

    if last_id != -1:
        round_logs = RoundLog.objects.filter(id__gt=last_id).order_by("-id")
    else:
        round_logs = RoundLog.objects.order_by("-id")[:10]

    changed_session = False

    for rnd in round_logs:
        rnd.message_with_btc = rnd.message.replace("BTC", '<span class="glyphicon glyphicon-btc" aria-hidden="true"></span>')

        if not changed_session:
            request.session["last_log_id"] = rnd.id
            changed_session = True

    return render(request, 'bcjp/round_log.html', {"round_logs": round_logs})

def round_progress(request):
    """
    Gets the round progress info
    """

    progress = settings.REDIS_CLIENT.get(settings.REDIS_ROUND_BETS)
    progress_sum = settings.REDIS_CLIENT.get(settings.REDIS_ROUND_CURRENT_AMOUNT)

    try:
        balance = BitcoinAddressSession.objects.get(pk=request.session["bas"]).amount
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'view', 'round_progress', e)
        balance = 0

    rtn = {
            "progress": progress, 
            "progress_sum": float(progress_sum) / settings.SATOSHI_RATIO,
            "balance": float(balance) / settings.SATOSHI_RATIO
        }

    return JsonResponse(rtn)

def betting_withdraw_address(request):
    if request.method != "POST":
        return redirect('index')
    if not request.POST.get('ig-withdraw_address-text', None):
        return redirect('index')
    if not request.session.get('bas', False):
        return redirect('index')

    withdraw_address = request.POST['ig-withdraw_address-text']

    if not re.search("^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", withdraw_address):
        return redirect('index')        

    try:
        bas = BitcoinAddressSession.objects.get(pk=request.session['bas'])
        bas.withdraw_address = withdraw_address

        if settings.IS_EDUCATIONAL:
            bas.amount = settings.IS_EDUCATIONAL_AMOUNT * settings.SATOSHI_RATIO

        bas.save()
    except Exception, e:
        LogUtils().error('bcjp.warning_file', 'view', 'betting_withdraw_address', e)

    return redirect('index')

def stats(request):
    total_bets = BitcoinBet.objects.count()
    total_bets_in_btc = float(BitcoinBet.objects.aggregate(Sum('amount'))['amount__sum']) / settings.SATOSHI_RATIO
    total_payout_in_btc = float(RoundWinner.objects.aggregate(Sum('winnings'))['winnings__sum']) / settings.SATOSHI_RATIO

    total_rounds = RoundWinner.objects.count()
    max_round_winnings = float(RoundWinner.objects.aggregate(Max('winnings'))['winnings__max']) / settings.SATOSHI_RATIO
    avg_round_winnings = float(RoundWinner.objects.aggregate(Avg('winnings'))['winnings__avg']) / settings.SATOSHI_RATIO


    return render(request, 'bcjp/stats.html', {"total_bets": total_bets, "total_bets_in_btc": total_bets_in_btc, "total_payout_in_btc": total_payout_in_btc, "total_rounds": total_rounds, "max_round_winnings": max_round_winnings, "avg_round_winnings": avg_round_winnings})

def hide_how_it_works(request):
    request.session['hide_how_it_works'] = True

    return HttpResponse(True)