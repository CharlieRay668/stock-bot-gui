
from os import path
import os
import datetime as dt
import time
import pandas as pd
from TDAccount import Account, Trade, Position
import TDSteamingAPI as TD_Stream
from TDSteamingAPI import Request, ClientWebsocket
import _thread as thread

REQUEST_ID = 0
DIRECTORY = 'watchlists'
symbol_keys = []
user_principals = TD_Stream.get_user_principals('keys.json')
requests = []
requests.append(Request('QUOTE', 'SUBS', user_principals, {"keys": 'SPY',"fields": "0,1,2,3,4,5,6,7,8,49"}))

login_encoded = TD_Stream.get_login_request(user_principals)
data_encoded, REQUEST_ID = TD_Stream.get_data_request(requests)
def exit_con():
    return False

def data_handler(data):
    print(data)

client = ClientWebsocket(login_encoded, data_encoded, exit_con, user_principals, True, data_handler)
ws = client.get_websocket()
thread.start_new_thread(ws.run_forever, ())
time.sleep(5)
quote, REQUEST_ID = TD_Stream.get_data_request([Request('QUOTE', 'SUBS', user_principals, {"keys": ','.join(symbol_keys),"fields": "0,1,2,3,4,5,6,7,8,49"})], REQUEST_ID)
client.send_message(quote)

