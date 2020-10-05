import time
import config as con 
import requests
import datetime as dt

epoch = dt.datetime.utcfromtimestamp(0)

def format_date(date):
    return str(date.year)+"-"+str(date.month)+"-"+str(date.day)

def format_datetime(date):
    return dt.datetime(int(date.split("-")[0]),int(date.split("-")[1]),int(date.split("-")[2].split(":")[0]),00,00,00)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def get_access_key(margin):
    url = r"https://api.tdameritrade.com/v1/oauth2/token"
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    payload = {'grant_type': 'refresh_token', 
            'refresh_token': con.get_refresh_token(margin), 
            'client_id':con.get_client_id()}
    authReply = requests.post(url, headers = headers, data=payload)
    return(authReply.json())

def get_accounts(access_token):
    headers = {'Authorization': "Bearer {}".format(access_token)}
    endpoint = r"https://api.tdameritrade.com/v1/accounts"
    content = requests.get(url = endpoint, headers = headers)
    return content.json()

def get_accounts_id(accounts):
    return accounts[0]['securitiesAccount']['accountId']

def get_account(access_token):
    headers = {'Authorization': "Bearer {}".format(access_token)}
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}".format(get_accounts_id(get_accounts(access_token)))
    content = requests.get(url = endpoint, headers = headers)
    return content.json()

def get_account_id(account):
    return account['securitiesAccount']['accountId']

def get_quote(ticker, access_token):
    headers = {'Authorization': "Bearer {}".format(access_token)}
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format(ticker.upper())
    payload = {'apikey':con.get_client_id()}
    content = requests.get(url = endpoint, params = payload, headers = headers)
    return content.json()

def get_hist_data(ticker, start, end):
    print(ticker, start, end)
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker.upper())
    payload = {'apikey': '9QAJTJSAZZIVFTUZYEEX1CRD4ECDM86B',
            'periodType':'day',
            'frequencyType':'minute',
            'frequency':'1',
            'startDate': int(unix_time_millis(start)),
            'endDate' : int(unix_time_millis(end)),
            'needExtendedHoursData':'True'}
    content = requests.get(url = endpoint, params = payload)
    return content.json()

def get_options_chain(access_token, ticker, side, startDate, endDate, strikes = 4, quotes = True, strategy = 'SINGLE'):
    headers = {'Authorization': "Bearer {}".format(access_token)}
    endpoint = r'https://api.tdameritrade.com/v1/marketdata/chains'
    payload = {'apikey': con.get_client_id(), 
        'symbol': ticker, 
        'contractType': side,
        'strikeCount': strikes,
        'includeQuotes': quotes,
        'strategy': strategy,
        'fromDate': startDate,
        'toDate': endDate}
    content = requests.get(url = endpoint, headers = headers, params=payload)
    return content.json()

def place_order_limit(ticker, amt, price, access_token, account_id):
    header = {'Authorization':"Bearer {}".format(access_token),
        "Content-Type":"application/json"}
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(account_id)
    if amt > 0: 
        payload = {'orderType':'LIMIT',
                'session':'NORMAL',
                'price': price,
                'duration':'DAY',
                'orderStrategyType':'SINGLE',
                'orderLegCollection':[{'instruction':'Buy','quantity':amt,'instrument':{'symbol':ticker,'assetType':'EQUITY'}}]}
    else:
        payload = {'orderType':'LIMIT',
                'session':'NORMAL',
                'price': price,
                'duration':'DAY',
                'orderStrategyType':'SINGLE',
                'orderLegCollection':[{'instruction':'Sell','quantity':amt*-1,'instrument':{'symbol':ticker,'assetType':'EQUITY'}}]}
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)
    print(str(content.status_code))

def place_order(ticker, amt, access_token, account_id):
    header = {'Authorization':"Bearer {}".format(access_token),
        "Content-Type":"application/json"}
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(account_id)
    if amt > 0: 
        payload = {'orderType':'MARKET',
                'session':'NORMAL',
                'duration':'DAY',
                'orderStrategyType':'SINGLE',
                'orderLegCollection':[{'instruction':'Buy','quantity':amt,'instrument':{'symbol':ticker,'assetType':'EQUITY'}}]}
    else:
        payload = {'orderType':'MARKET',
                'session':'NORMAL',
                'duration':'DAY',
                'orderStrategyType':'SINGLE',
                'orderLegCollection':[{'instruction':'Sell','quantity':amt*-1,'instrument':{'symbol':ticker,'assetType':'EQUITY'}}]}
    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    content = requests.post(url = endpoint, json = payload, headers = header)
    print(str(content.status_code))

def order_option_limit(buysell, symbol, amt, price, access_token, account_id):
    access_token = get_access_key(True)['access_token']
    header = {'Authorization':"Bearer {}".format(access_token),
        "Content-Type":"application/json"}
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(account_id)
    print(header, endpoint)
    if buysell == 'BUY':
        payload ={
            "complexOrderStrategyType": "NONE",
            "orderType": "LIMIT",
            "session": "NORMAL",
            "price": price,
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [{"instruction": "BUY_TO_OPEN", "quantity": str(amt), "instrument": {"symbol": symbol, "assetType": "OPTION"}}]
            }
    else:
        payload ={
            "complexOrderStrategyType": "NONE",
            "orderType": "LIMIT",
            "session": "NORMAL",
            "price": price,
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [{"instruction": "SELL_TO_CLOSE","quantity": str(amt),"instrument": {"symbol": symbol,"assetType": "OPTION"}}]
            }
    print('Requesting')
    content = requests.post(url = endpoint, json = payload, headers = header)
    print(content, 'initial')
    x = 1
    while(str(content.status_code) != '201' and x < 3):
        time.sleep(3)
        content = requests.post(url = endpoint, json = payload, headers = header)
        print(content, x+1)
        x += 1
    print(content, 'Final')

def order_option(buysell, symbol, amt, access_token, account_id):
    header = {'Authorization':"Bearer {}".format(access_token),
        "Content-Type":"application/json"}
    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(account_id)
    if buysell == 'BUY':
        payload ={
            "complexOrderStrategyType": "NONE",
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                "instruction": "BUY_TO_OPEN",
                "quantity": str(amt),
                "instrument": {
                    "symbol": symbol,
                    "assetType": "OPTION"
                    }
                }
            ]
            }
    else:
        payload ={
            "complexOrderStrategyType": "NONE",
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                "instruction": "SELL_TO_CLOSE",
                "quantity": str(amt),
                "instrument": {
                    "symbol": symbol,
                    "assetType": "OPTION"
                    }
                }
            ]
            }
    requests.post(url = endpoint, json = payload, headers = header)

def get_best_option(ticker, side, access_token=None):
    if access_token == None:
        access_token = get_access_key(True)['access_token']
    now = dt.datetime.now()
    then = now + dt.timedelta(days = 30)
    word_map = ''
    if side == 'LONG':
        word_map = 'callExpDateMap'
        data = get_options_chain(access_token, ticker, 'CALL', format_date(now), format_date(then))
    else:
        word_map = 'putExpDateMap'
        data = get_options_chain(access_token, ticker, 'PUT', format_date(now), format_date(then))
    dates = []
    timedelta = 14
    while len(dates) < 1:
        for dat in data[word_map]:
            if format_datetime(dat) > now + dt.timedelta(days = 7) and format_datetime(dat) < now + dt.timedelta(days=timedelta):
                dates.append(dat)
        timedelta += 1
    strikes = data[word_map][dates[0]]
    price = get_quote(ticker, access_token)[ticker]['mark']
    dist = 10000000
    strike = 0
    for item in strikes:
        if abs(price-float(item)) < dist:
            dist = abs(price-float(item))
            strike = item
    return strikes[strike][0]

def get_option_symbol(ticker, strike, year, month, day, side):
    if side == 'CALLS':
        return(ticker + "_" + str(month)+str(day)+str(year)+ "C"+str(strike))
    else:
        return(ticker + "_" + str(month)+str(day)+str(year)+ "P"+str(strike))

def specific_order(ticker, side, strike, year, month, day, amt):
    access_token = get_access_key(True)['access_token']
    account_id = get_account_id(get_account(access_token))
    print(access_token, account_id)
    option = get_option_symbol(ticker, strike, year, month, day, side)
    print(option)
    available_cash = get_account(access_token)['securitiesAccount']['currentBalances']['buyingPower']
    print(available_cash)
    if  available_cash > amt:
        mark = get_option_price(option, access_token)*100
        print(mark)
        ask = get_option_ask(option, access_token)*100
        print(ask)
        cost_per_option = int((mark+ask)/2)
        print(cost_per_option)
        option_amt = int(amt/cost_per_option)
        if option_amt >= 1:
            try:
                #order_option('BUY', option, option_amt, access_token, account_id)
                order_option_limit('BUY', option, option_amt, (cost_per_option/100), access_token, account_id)
                return (option, option_amt, ticker, 0, " Sucess, Option ordered")
            except:
                return(option, option_amt, ticker, 0, ' TotalFailure INVALID ORDER')
        else:
            return (option, 0, ticker, 0, " TotalFailure Option too expensive")
    else:
        return (option, 0, ticker, 0, " TotalFailure NOT ENOUGH CASH")

def bot_order(ticker, side, stockamt, optionamt):
    access_token = get_access_key(True)['access_token']
    account_id = get_account_id(get_account(access_token))
    option = get_best_option(access_token, ticker, side)
    available_cash = get_account(access_token)['securitiesAccount']['currentBalances']['buyingPower']
    buy_stock = True
    if side != "LONG":
        buy_stock = False
    if  available_cash > stockamt+optionamt:
        cost_per_option = int(((get_option_price(option['symbol'], access_token)*100) + (get_option_ask(option['symbol'], access_token)*100))/2)
        print(cost_per_option)
        #cost_per_option = 0.01*100
        cost_per_stock = get_quote(ticker, access_token)[ticker.upper()]['mark']
        print(cost_per_stock)
        option_amt = int(optionamt/cost_per_option)
        stock_amt = int(stockamt/cost_per_stock)
        if option_amt >= 1 and stock_amt >= 1 and buy_stock:
                #order_option('BUY', option['symbol'], option_amt, access_token, account_id)
                order_option_limit('BUY', option['symbol'], option_amt, (cost_per_option/100), access_token, account_id)
                place_order(ticker, stock_amt, access_token, account_id)
                return (option['symbol'], option_amt, ticker, stock_amt, " Ordered buy_stock=" +str(buy_stock))
        elif option_amt >= 1:
            #order_option('BUY', option['symbol'], option_amt, access_token, account_id)
            order_option_limit('BUY', option['symbol'], option_amt, (cost_per_option/100), access_token, account_id)
            return (option['symbol'], option_amt, ticker, stock_amt, " StockFailure Option Ordered buy_stock=" +str(buy_stock))
        elif stock_amt >= 1 and buy_stock:
            place_order(ticker, stock_amt, access_token, account_id)
            return (option['symbol'], option_amt, ticker, stock_amt, " OptionFailure Stock Ordered buy_stock=" +str(buy_stock))
        else:
            return (option['symbol'], 0, ticker, 0, " TotalFailure Option and Stock too expensive")
    else:
        return (option['symbol'], 0, ticker, 0, " TotalFailure NOT ENOUGH CASH")

def bot_sell_option(symbol, amt, margin):
    access_token = get_access_key(margin)['access_token']
    account_id = get_account_id(get_account(access_token))
    return order_option('SELL', symbol, amt, access_token, account_id)

def bot_sell_stock(ticker, amt):
    access_token = get_access_key(True)['access_token']
    account_id = get_account_id(get_account(access_token))
    return place_order(ticker, -amt, access_token, account_id)

def get_option_price(option, access_token):
    return get_quote(option, access_token)[option]['mark']

def get_option_ask(option, access_token):
    return get_quote(option, access_token)[option]['askPrice']

def get_auth_quote(ticker):
    access_token = get_access_key(True)['access_token']
    return get_quote(ticker, access_token)
