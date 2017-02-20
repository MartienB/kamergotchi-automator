# Kamergotchi Automator
# https://github.com/MartienB/kamergotchi-automator
# Developed by: Martien Bonfrer
# Date: 20/2/17

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl
import time
import json
import urllib.request
from urllib.parse import urljoin
from urllib.error import URLError
from urllib.error import HTTPError
import codecs
from random import randint
import datetime

def getInfo(player_token):
    url = 'https://api.kamergotchi.nl/game'
    request = Request(url)
    request.add_header('x-player-token', player_token)
    context = ssl._create_unverified_context() # There is something wrong with the ssl certificate, so we just ignore it!
    json = urlopen(request, context=context).read().decode()

    return json

def giveMostNeededCare(player_token):
    returnJson = json.loads(getInfo(player_token))
    game = returnJson['game']
    careLeft = game['careLeft']
    current = game['current']

    foodValue = current['food']
    attentionValue = current['attention']
    knowledgeValue = current['knowledge']

    careReset = game['careReset']
    claimReset = game['claimReset']

    careResetDate = datetime.datetime.strptime(careReset, "%Y-%m-%dT%H:%M:%S.%fZ")
    claimResetDate = datetime.datetime.strptime(claimReset, "%Y-%m-%dT%H:%M:%S.%fZ")
    now = datetime.datetime.utcnow()

    # check if it is time to claim the bonus
    if (now > claimResetDate):
        claimBonus(player_token)

    # check if there are care's left, or if the careResetDate has elapsed (careLeft stays 0 even after reset date) .
    if (careLeft > 0 or now > careResetDate):

        if (foodValue < attentionValue):
            if (knowledgeValue < foodValue):
                giveCare(player_token, 'knowledge');
            else:
                giveCare(player_token, 'food')
            
        else:
            if (attentionValue < knowledgeValue):
                giveCare(player_token, 'attention')
            else:
                giveCare(player_token, 'knowledge')
        return 0
    else:
        remainingSeconds = (careResetDate-now).total_seconds()
        print ('{}{}'.format('Not yet! Remaining seconds:', remainingSeconds))
        return remainingSeconds
    
def claimBonus(player_token):
    context = ssl._create_unverified_context() 
    sessionUrl = 'https://api.kamergotchi.nl/game/claim'
    reqBody = {'bar' : 'foo'}

    data = json.dumps(reqBody).encode('utf-8')

    headers = {}
    # Input all the needed headers below
    headers['x-player-token'] = player_token
    headers['Content-type'] = "application/json;charset=utf-8"
    
    # headers['User-Agent'] = "kamergotchi/86 CFNetwork/808.0.2 Darwin/16.0.0"
    # headers['Host'] = "api.kamergotchi.nl"
    # headers['Accept-Language'] = "en-us"
    # headers['Accept'] = "application/json, text/plain, */*"
    # headers['Connection'] = "close"

    req = urllib.request.Request(sessionUrl, data, headers)

    try: 
        response = urllib.request.urlopen(req, context=context)
        jsonresp = response.read().decode()
        # print(jsonresp)
        print('Succesfully claimed bonus!')
    except HTTPError as httperror:
        print(httperror)
    except URLError as urlerror:
        print(urlerror)
    except:
        print('error')


def giveCare(player_token, careType):   
    context = ssl._create_unverified_context() 
    sessionUrl = 'https://api.kamergotchi.nl/game/care'
    reqBody = {'bar' : careType}

    data = json.dumps(reqBody).encode('utf-8')

    headers = {}
    # Input all the needed headers below
    headers['x-player-token'] = player_token
    headers['Content-type'] = "application/json;charset=utf-8"
    
    # headers['User-Agent'] = "kamergotchi/86 CFNetwork/808.0.2 Darwin/16.0.0"
    # headers['Host'] = "api.kamergotchi.nl"
    # headers['Accept-Language'] = "en-us"
    # headers['Accept'] = "application/json, text/plain, */*"
    # headers['Connection'] = "close"

    req = urllib.request.Request(sessionUrl, data, headers)

    try: 
        response = urllib.request.urlopen(req, context=context)
        jsonresp = response.read().decode()
        # print(jsonresp)
        returnJson = json.loads(jsonresp)
        game = returnJson['game']
        print ('{}{}{}{}{}'.format('Succesfully cared: ', careType, '(score: ', game['score'], ')'))
    except HTTPError as httperror:
        print(httperror)
    except URLError as urlerror:
        print(urlerror)
    except:
        print('error')


player_token = '' # Token can be found in the request header (x-player-token)

# print(giveMostNeededCare(player_token))

while True:
    sleep = giveMostNeededCare(player_token)
    if (sleep == 0):
        sleep += randint(1,3) # There are care's left, so just small timeout
    else:
        sleep += randint(2,120) # Waiting for careResetDate, bigger timout to keep things realistic

    time.sleep(sleep)

