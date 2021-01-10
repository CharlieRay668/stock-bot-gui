import urllib
import json
import requests
import dateutil.parser
import datetime
from datetime import datetime
import time
import websocket
import threading
try:
    import thread
except ImportError:
    import _thread as thread
from TDRestAPI import Rest_Account   

def format_header(access_token):
    return {'Authorization': "Bearer {}".format(access_token)}

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def get_user_principals(key_file_name):
    account = Rest_Account(key_file_name)
    endpoint = "https://api.tdameritrade.com/v1/userprincipals"

    headers = format_header(account.update_access_token())

    params = {'fields':'streamerSubscriptionKeys,streamerConnectionInfo'}

    content = requests.get(url = endpoint, params = params, headers = headers)
    return content.json()

def get_login_request(userPrincipalsResponse):
    tokenTimeStamp = userPrincipalsResponse['streamerInfo']['tokenTimestamp']
    date = dateutil.parser.parse(tokenTimeStamp, ignoretz = True)
    tokenTimeStampAsMs = unix_time_millis(date)
    credentials = {"userid": userPrincipalsResponse['accounts'][0]['accountId'],
                "token": userPrincipalsResponse['streamerInfo']['token'],
                "company": userPrincipalsResponse['accounts'][0]['company'],
                "segment": userPrincipalsResponse['accounts'][0]['segment'],
                "cddomain": userPrincipalsResponse['accounts'][0]['accountCdDomainId'],
                "usergroup": userPrincipalsResponse['streamerInfo']['userGroup'],
                "accesslevel":userPrincipalsResponse['streamerInfo']['accessLevel'],
                "authorized": "Y",
                "timestamp": int(tokenTimeStampAsMs),
                "appid": userPrincipalsResponse['streamerInfo']['appId'],
                "acl": userPrincipalsResponse['streamerInfo']['acl'] }

    login_request = {"requests": [{"service": "ADMIN",
                                "requestid": "0",  
                                "command": "LOGIN",
                                "account": userPrincipalsResponse['accounts'][0]['accountId'],
                                "source": userPrincipalsResponse['streamerInfo']['appId'],
                                "parameters": {"credential": urllib.parse.urlencode(credentials),
                                                "token": userPrincipalsResponse['streamerInfo']['token'],
                                                "version": "1.0"}}]}
    return json.dumps(login_request)
    

def get_data_request(requests, request_id = 1):
    services = []
    for request in requests:
        services.append({'service': request.service,
                         'requestid': request_id,
                         'command': request.command,
                         'account': request.account,
                         'source': request.source,
                         'parameters': request.params})
        request_id += 1
    data_request = {'requests': services}
    return json.dumps(data_request), request_id


class Request():
    def __init__(self, service, command, user_principals, params):
        self.service = service
        self.command = command
        self.account = user_principals['accounts'][0]['accountId']
        self.source = user_principals['streamerInfo']['appId']
        self.params = params

class ClientWebsocket():
    def __init__(self, login, data, exit_condition, user_principals, enable_trace, data_handler):
        self.login = login
        self.data = data
        self.exit_condition = exit_condition
        self.user_principals = user_principals
        self.data_handler = data_handler
        uri = "wss://" + self.user_principals['streamerInfo']['streamerSocketUrl'] + "/ws"
        websocket.enableTrace(enable_trace)
        self.ws = websocket.WebSocketApp(uri,
                                on_message = lambda ws,msg: self.on_message(ws, msg),
                                on_error = lambda ws,msg: self.on_error(ws, msg),
                                on_close = lambda ws: self.on_close(ws),
                                on_open = lambda ws: self.on_open(ws))

    def send_message(self, message):
        try:
            self.ws.send(message)
            return 200
        except:
            self.ws.send(message)
            return 500

    def check_close(self):
        if self.exit_condition():
            self.ws.close()
            print("thread terminating...")

    def on_message(self, ws, message):
        print(message)
        message_decoded = json.loads(message)
        if 'data' in message_decoded.keys():
            data = message_decoded['data'][0]
            self.data_handler(data)
            self.check_close()
            return data
        self.check_close()
        return None

    def on_error(self, ws, error):
        print(error, ' errors')
        return error

    def on_close(self, ws):
        print("### closed ###")
        return True

    def on_open(self, ws):
        print('RUNNING')
        def run(*args):
            ws.send(self.login)
            time.sleep(1)
            ws.send(self.data)
            self.check_close()
        thread.start_new_thread(run, ())

    def get_websocket(self):
        return self.ws

if __name__ == "__main__":

    user_principals = get_user_principals('keys.json')
    requests = []
    #requests.append(Request('CHART_FUTURES', 'SUBS', user_principals, {"keys": "/ES","fields": "0,1,2,3,4,5,6,7"}))
    
    #requests.append(Request('OPTION', 'SUBS', user_principals, {"keys": 'AMZN_100220C3280',"fields": "0,1,2,3,4,5,6,7,8,32"}))
    #requests.append(Request('NEWS_HEADLINE', 'SUBS', user_principals, {'keys': 'GOOG,AMZN,TSLA,AAPL,MSFT,DDOG,SPY,WMT,CAT,MNRA,', 'fields':'0,1,2,3,4'}))
    requests.append(Request('QUOTE', 'SUBS', user_principals, {"keys": 'AMZN,TSLA,SPY,AMD',"fields": "0,1,2,3,4,5,6,7,8,48"}))
    login_encoded = get_login_request(user_principals)
    data_encoded, request_id = get_data_request(requests)

    def exit_con():
        return datetime.now().minute >= 57
    def data_handler(data):
        # x = 0
        # for item in data['content']:
        #     x += 1
        #     #print(item['key'])
        #     if item['key'] == 'AAPL':
        #         print(item)
        # print(x)
        open('td_ameritrade_data.txt', '+a').write(str(data) +'\n')

    client = ClientWebsocket(login_encoded, data_encoded, exit_con, user_principals, True, data_handler)

    ws = client.get_websocket()
    print(type(ws))
    thread.start_new_thread(ws.run_forever, ())
    # wst = threading.Thread(target=ws.run_forever())
    # wst.daemon = True
    # wst.start()
    x = 0
    while True:
        # if x == 3:
        #     requests.append(Request('QUOTE', 'SUBS', user_principals, {"keys": 'AMZN',"fields": "0,1,2,3,4,5,6,7,8,48"}))
        #     amnz_quote, request_id = get_data_request(requests, request_id)
        #     print(amnz_quote)
        #     print(client.send_message(amnz_quote), 'Result')
        # if x == 5:
        #     requests.append(Request('QUOTE', 'SUBS', user_principals, {"keys": 'TSLA',"fields": "0,1,2,3,4,5,6,7,8,48"}))
        #     amnz_quote, request_id = get_data_request(requests, request_id)
        #     print(amnz_quote)
        #     print(client.send_message(amnz_quote), 'Result')
        print('Whats up', x)
        time.sleep(5)
        x += 1
        pass
    #ws.run_forever()


    #print(mainstring)