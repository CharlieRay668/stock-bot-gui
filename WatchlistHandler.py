
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

def log_data(data):
    logger = open(DIRECTORY+'/'+'watchlist_logs.txt', '+a')
    logger.write(data)

def handle_watches():
    #49 = market price
    symbol_keys = []
    user_principals = TD_Stream.get_user_principals('keys.json')
    requests = []
    requests.append(Request('QUOTE', 'SUBS', user_principals, {"keys": 'SPY',"fields": "0,1,2,3,4,5,6,7,8,49"}))

    login_encoded = TD_Stream.get_login_request(user_principals)
    data_encoded, REQUEST_ID = TD_Stream.get_data_request(requests)
    def exit_con():
        if (dt.datetime.now().hour >= 14 and dt.datetime.now().minute >= 30):
            log_data('Closing down stream\n')
            return True

    def data_handler(data):
        keys = data.keys()
        if 'content' in keys:
            fields = data['content']
            for field in fields:
                field_keys = field.keys()
                #log_data(str(field)+'\n')
                if 'key' in field_keys and '49' in field_keys:
                    key = field['key']
                    mark = field['49']
                    today = dt.date.today().strftime("%Y_%m_%d")
                    csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
                    data = pd.read_csv(csv_path)
                    for index, row in data.iterrows():
                        row = row.to_dict()
                        if row['SYMBOL'].upper() == key.upper() and not row['ALERTED']:
                            if row['DIRECTION'] == 'above':
                                if float(mark) > row['THRESHOLD']:
                                    data.loc[index, 'ALERTED'] = True
                                    log_data(str(key) + ' is crossing **above** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here\n')
                            else:
                                if float(mark) < row['THRESHOLD']:
                                    data.loc[index, 'ALERTED'] = True
                                    log_data(str(key) + ' is crossing **below** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here\n')
                            data.to_csv(csv_path, index=False)

    client = ClientWebsocket(login_encoded, data_encoded, exit_con, user_principals, True, data_handler)
    ws = client.get_websocket()
    thread.start_new_thread(ws.run_forever, ())
    today = dt.date.today().strftime("%Y_%m_%d")
    csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
    time.sleep(5)
    while not (dt.datetime.now().hour >= 14 and dt.datetime.now().minute >= 31):
        if path.exists(csv_path):
            data = pd.read_csv(csv_path)
            for index, row in data.iterrows():
                row = row.to_dict()
                if row['UPLOADED'] == False:
                    print('SENT ' + row['SYMBOL'] + '<-----------------------')
                    symbol_keys.append(row['SYMBOL'].upper())
                    print(','.join(symbol_keys))
                    quote, REQUEST_ID = TD_Stream.get_data_request([Request('QUOTE', 'SUBS', user_principals, {"keys": ','.join(symbol_keys),"fields": "0,1,2,3,4,5,6,7,8,49"})], REQUEST_ID)
                    client.send_message(quote)
                    data.loc[index, 'UPLOADED'] = True
                    data.to_csv(csv_path, index=False)
                    break
            time.sleep(2.5)
        else:
            time.sleep(5)

handle_watches()