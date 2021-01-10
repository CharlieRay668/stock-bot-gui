
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
    # def exit_con():
    #     if (dt.datetime.now().hour >= 16 and dt.datetime.now().minute >= 30):
    #         log_data('Closing down stream\n')
    #         return True
    # def data_handler(data):
    #     keys = data.keys()
    #     if 'content' in keys:
    #         fields = data['content']
    #         for field in fields:
    #             field_keys = field.keys()
    #             #log_data(str(field)+'\n')
    #             try:
    #                 if 'key' in field_keys and '49' in field_keys:
    #                     key = field['key']
    #                     mark = field['49']
    #                     today = dt.date.today().strftime("%Y_%m_%d")
    #                     csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
    #                     data = pd.read_csv(csv_path)
    #                     for index, row in data.iterrows():
    #                         row = row.to_dict()
    #                         if row['SYMBOL'].upper() == key.upper():
    #                             if row['ALERTED'] == 0:
    #                                 margin = row['THRESHOLD']*0.002
    #                                 if row['DIRECTION'] == 'above':
    #                                     if float(mark) > (float(row['THRESHOLD'])-margin):
    #                                         data.loc[index, 'ALERTED'] = 1
    #                                         log_data(str(key) + ' is **near above** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 else:
    #                                     if float(mark) < (float(row['THRESHOLD'])+margin):
    #                                         data.loc[index, 'ALERTED'] = 1
    #                                         log_data(str(key) + ' is **near below** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 data.to_csv(csv_path, index=False)
    #                             elif row['ALERTED'] == 1:
    #                                 if row['DIRECTION'] == 'above':
    #                                     if float(mark) > (float(row['THRESHOLD'])):
    #                                         data.loc[index, 'ALERTED'] = 2
    #                                         log_data(str(key) + ' is **crossing above** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 else:
    #                                     if float(mark) < (float(row['THRESHOLD'])):
    #                                         data.loc[index, 'ALERTED'] = 2
    #                                         log_data(str(key) + ' is **crossing below** ' + str(row['THRESHOLD']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 data.to_csv(csv_path, index=False)
    #                             elif row['ALERTED'] == 2:
    #                                 margin = row['PT']*0.002
    #                                 if row['DIRECTION'] == 'above':
    #                                     if float(mark) > (float(row['PT'])-margin):
    #                                         data.loc[index, 'ALERTED'] = 3
    #                                         log_data(str(key) + ' is **near profit target** ' + str(row['PT']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 else:
    #                                     if float(mark) < (float(row['PT'])+margin):
    #                                         data.loc[index, 'ALERTED'] = 3
    #                                         log_data(str(key) + ' is **near profit target** ' + str(row['PT']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 data.to_csv(csv_path, index=False)
    #                             elif row['ALERTED'] == 3:
    #                                 if row['DIRECTION'] == 'above':
    #                                     if float(mark) > (float(row['PT'])):
    #                                         data.loc[index, 'ALERTED'] = 4
    #                                         log_data(str(key) + ' is **crossing above profit target** ' + str(row['PT']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 else:
    #                                     if float(mark) < (float(row['PT'])):
    #                                         data.loc[index, 'ALERTED'] = 4
    #                                         log_data(str(key) + ' is **crossing below profit target** ' + str(row['PT']) + ' current price ' + str(mark) + ' @here//:' + str(row['CHANNEL']) + ' ' + str(row['AUTHOR'] + '\n'))
    #                                 data.to_csv(csv_path, index=False)
    #             except:
    #                 pass
    def exit_con():
        return False

    def data_handler(data):
        print(data)

    client = ClientWebsocket(login_encoded, data_encoded, exit_con, user_principals, True, data_handler)
    ws = client.get_websocket()
    thread.start_new_thread(ws.run_forever, ())

    # symbol_keys.append('AMD')
    # quote, REQUEST_ID = TD_Stream.get_data_request([Request('QUOTE', 'SUBS', user_principals, {"keys": ','.join(symbol_keys),"fields": "0,1,2,3,4,5,6,7,8,49"})], REQUEST_ID)
    # client.send_message(quote)
    today = dt.date.today().strftime("%Y_%m_%d")
    csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
    time.sleep(5)
    while (dt.datetime.now().hour <= 16):
        if path.exists(csv_path):
            try:
                data = pd.read_csv(csv_path)
                print(data)
                for index, row in data.iterrows():
                    row = row.to_dict()
                    print(row['UPLOADED'])
                    if row['UPLOADED'] == False:
                        print('SENT ' + row['SYMBOL'] + '<-----------------------')
                        symbol_keys.append(row['SYMBOL'].upper())
                        print('\n\n\n'+ str(symbol_keys) + '\n\n\n')
                        print(','.join(symbol_keys))
                        quote, REQUEST_ID = TD_Stream.get_data_request([Request('QUOTE', 'SUBS', user_principals, {"keys": ','.join(symbol_keys),"fields": "0,1,2,3,4,5,6,7,8,49"})], REQUEST_ID)
                        client.send_message(quote)
                        data.loc[index, 'UPLOADED'] = True
                        data.to_csv(csv_path, index=False)
                        break
                time.sleep(2.5)
            except:
                time.sleep(2.5)
        else:
            time.sleep(5)

handle_watches()