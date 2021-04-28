import os, sys, time
import asyncio
import requests
import json
from bfxapi import Client


API_KEY = os.environ.get('API_KEY', None)
API_SECRET = os.environ.get('API_SECRET', None)
SLACK_URL = os.environ.get('SLACK_URL', None)
bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='WARNING',
)


# event type
FUNDING_ORDER_CANCEL = 'foc'
HEARTBEAT = 'hb'

if API_KEY == None or API_SECRET == None:
  print("API_KEY and API_SECRET should not be None")
  sys.exit()

if SLACK_URL == None:
  print("SLACK_URL should not be None")
  sys.exit()



@bfx.ws.on('wallet_update')
def wallet_update(wallet):
  print ("Balance updates: {}".format(wallet))
  now = time.time.now()
  msg = {
    'time': time.strftime('%b %d %Y %H:%M:%S', now),
    'event': 'wallet_update',
    'msg': str(wallet),
  }
  headers = {'Content-type': 'application/json'}
  res = requests.post(SLACK_URL, data=json.dumps({'text': json.dumps(msg)}), headers=headers)
  print(res)


@bfx.ws.on('new_funding_ticker')
def new_funding_ticker(req):
  print ("Fund Order New Request:::::{}".format(req))


@bfx.ws.on('funding_info_updates')
def funding_info_updates(req):
  print ("funding_info_updates::::: {}".format(req))


@bfx.ws.on('all')
def all(req):
  event_type = req[1]
  if event_type == FUNDING_ORDER_CANCEL:
    print("funding order canceled: {}".format(req))
    now = time.time.now()
    req_content = req[2]
    order_id = req_content[0]
    currency = req_content[1]
    amount = req_content[4]
    day_range = req_content[-6]
    rate = req_content[-7]
    msg = {
      'time': time.strftime('%b %d %Y %H:%M:%S', now),
      'event': 'funding order canceled',
      'currency': currency,
      'day_range': day_range,
      'amount': amount,
      'rate': rate,
    }
    headers = {'Content-type': 'application/json'}
    res = requests.post(SLACK_URL, data=json.dumps({'text': json.dumps(msg)}), headers=headers)
  elif event_type == HEARTBEAT:
   pass
  else:
    print('unknown event: ', req)

@bfx.ws.on('error')
def log_error(msg):
  print ("Error: {}".format(msg))

bfx.ws.run()
