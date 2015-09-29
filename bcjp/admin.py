import random
import numpy as np
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Sum
from django.views.decorators.csrf import csrf_exempt
from urlparse import urlparse
from bcjp_utils import process_round_bet

from models import *

@csrf_exempt
def create_bet(request):
    if not valid_uuid(request.POST.get("uuid", None)):
        return JsonResponse({"message": "Please try again!"}, status=404)

    jsonRtn = {}
    status = 200

    try:
        adminbas = random.choice(AdminBitcoinAddressSession.objects.all())
        top_up_bas(adminbas.bitcoin_address_session)

        bet = BitcoinBet()
        bet.bitcoin_address_session = adminbas.bitcoin_address_session
        bet.amount = np.random.randint(1, 20) * settings.SATOSHI_RATIO
        bet.save()

        abet = AdminBitcoinBet()
        abet.bitcoin_bet = bet
        abet.save()

        process_round_bet(bet=bet, bas=adminbas.bitcoin_address_session)
        jsonRtn["message"] = "Bet posted for {}".format(adminbas.bitcoin_address_session.id)
    except Exception, e:
        jsonRtn["message"] = str(e)
        status = 500
    
    return JsonResponse(jsonRtn, status=status)

@csrf_exempt
def top_up(request):
    if not valid_uuid(request.POST.get("uuid", None)):
        return JsonResponse({"message": "Please try again!"}, status=404)

    jsonRtn = {}
    status = 200

    try:
        adminbas = AdminBitcoinAddressSession.objects.all()

        for abas in adminbas:
            top_up_bas(abas.bitcoin_address_session)

        jsonRtn["message"] = "Topped up all Admin BAS"
    except Exception, e:
        jsonRtn["message"] = str(e)
        status = 500
    
    return JsonResponse(jsonRtn, status=status)

def valid_uuid(uuid=None):
    if not uuid:
        return False

    admin = True

    try:
        AdminOverride.objects.get(pk=uuid)
    except Exception, e:
        admin = False
    finally:
        return admin

def top_up_bas(bas=None):
    if not bas:
        return False

    if bas.amount <= (20 * settings.SATOSHI_RATIO):
        bas.amount = 25 * settings.SATOSHI_RATIO
        bas.save()
        return True

    return False