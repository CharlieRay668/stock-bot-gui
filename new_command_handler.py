import pandas as pd
import numpy as np
import datetime as dt
from io import StringIO
from TDRestAPI import Rest_Account
import uuid
from csv_manager import CSVHandler

class Option():
    def __init__(self, ticker, side, strike, date, symbol):
        self.ticker = ticker
        self.side = side
        self.strike = strike
        self.date = date
        self.symbol = symbol

    def __str__(self):
        return str(self.ticker) + ' ' +str(self.strike) + ' ' + str(self.date) + ' ' + str(self.side) + ' ' + str(self.symbol)

def parse_strikes(strike_str, order_struct, strike_split):
    strike_str = strike_str.upper()
    strikes = strike_str.split(strike_split)
    calls = [(item[:-1], item[-1]) for item in strikes if 'C' in item]
    puts = [(item[:-1], item[-1]) for item in strikes if 'P' in item]
    if len(calls)+len(puts) == 0:
        return "Unable to parse calls/puts, make sure to specify"
    call_struct = [(item[2:], item[0]) for item in order_struct if 'C' in item]
    put_struct = [(item[2:], item[0]) for item in order_struct if 'P' in item]
    call_struct.sort()
    put_struct.sort()
    calls.sort()
    puts.sort()
    call_struct = list(zip(calls, call_struct))
    put_struct = list(zip(puts, put_struct))
    buy_str = ''
    sell_str = ''
    buys = []
    sells = []
    for option, instruction in call_struct:
        if instruction[1] == 'B':
            buy_str += option[0] + ' Call strike '
            buys.append(option)
        else:
            sells.append(option)
            sell_str += option[0] + ' Call strike '
    for option, instruction in put_struct:
        if instruction[1] == 'B':
            buy_str += option[0] + ' Put strike '
            buys.append(option)
        else:
            sell_str += option[0] + ' Put strike '
            sells.append(option)
    return buys, sells, buy_str, sell_str

def check_float(item):
    try:
        float(item)
        return True
    except:
        return False

def check_int(item):
    try:
        int(item)
        return True
    except:
        return False

def remove_chars(string, chars):
    for char in chars:
        string = string.replace(char, '')
    return string

def parse_single_strike(strike):
        # Get rid of any 's' characters, Cleans up calls-call puts-put ect.
        strike = strike.lower().replace('s','')
        side = None
        strike_num = None
        # Use c and call to identify if the order is calls, p or put to identify puts.
        if 'c' in strike or 'call' in strike:
            side = 'CALLS'
        elif 'p' in strike or 'put' in strike:
            side ='PUTS'
        # Remove side info. All that should be left now is the strikes, check if its a int or float and parse it out.
        strike = strike.replace('put', '').replace('p', '').replace('call', '').replace('c', '')
        if check_int(strike):
            strike_num = strike
        elif not check_int(strike):
            if check_float(strike):
                strike_num = strike
        return strike_num, side

def parse_ironcondor(order, author, channel, td_account):
    pass
def parse_creditspread(order, author, channel, td_account):
    pass
def parse_debitspread(order, author, channel, td_account):
    pass

def handle_single_order(order, author, channel, td_account):
    # Generate unique trade uuid
    trade_id = uuid.uuid1().hex
    order = order.split(' ')
    # Get ticker from order
    if True:
        name = 'standard'
        ticker = order[0].upper()
    else:
        name = order[0].lower()
        ticker = order[1].upper()
    # Get stock data from ticker
    quote = td_account.get_quotes(ticker)
    # Check to see if the ticker is valid
    if quote is None:
        return 399, 'Unable to find stock symbol'

    # Create a list called 'found'. This is where we store all the information we have parsed from the order. Initialize it with the ticker
    found = [ticker]
    # Parse the date out from the order using the identifier specified in the command info, throw error if not found, append it to found list.
    date = None
    for item in order:
        if '/' in item:
            date = item
    if date is None:
        return 402, 'Expiration Date not Found'
    found.append(date)

    # Try to predict the year from only MM/DD. If MM/DD is in the past we can assume that year is in the future. If not year is present year. If year is specified go with that.
    month = date.split('/')[0]
    day = date.split('/')[1]
    if len(date.split('/')) > 2:
        year = date.split('/')[2]
    else:
        if int(month) < dt.datetime.now().month or (int(month) == dt.datetime.now().month and int(day) < dt.datetime.now().day):
            new_year = dt.datetime.now() + dt.timedelta(year = 1)
            year = str(new_year.year)[2:]
        else:
            year = str(dt.datetime.now().year)[2:]

    # Parse out the average price from the order using the identifier specifed in the command info. If average price does not exist then continue else, try to clean it.
    avg_price = None
    for item in order:
        if '@' in item:
            avg_price = item
            found.append(avg_price.replace('@', ''))
    # Parsing strikes is different for individual options and complex orders
    options = []
    # Maybe hard code complex orders
    # If the order is complex continue
    # For each item that we have found (ticker, date, average price) remove it from the order string to make parsing strikes and order side easier.
    for item in found:
        order.remove(item.lower())
    quantity = None
    for item in order:
        if 'qty' in item:
            quantity_str = item
            quantity = item.replace('qty', '')
            quantity = quantity.replace('=','').replace(':','')
    if quantity is None:
        return 403, 'Quantity not Found'
    found = []
    found.append(quantity_str)
    for item in found:
        order.remove(item.lower())
    try:
        quantity = int(quantity)
    except:
        return 101, 'Quantity is not an integer'
    side = None
    # Make assign strike and side based of of the above code. If either are non return so.
    strike = None
    side = None
    for item in order:
        parsed = parse_single_strike(item)
        if parsed[0] is not None:
            strike = parsed[0]
        if parsed[1] is not None:
            side = parsed[1]
    if strike is None:
        return 400, 'Strike not found'
    if side is None:
        return 405, 'Unable to determine side'
    # Get a symbol for specified option and append it to the total options
    symbol = td_account.get_option_symbol(ticker, strike, year, month, day, side)
    option = Option(ticker, side, strike, date, symbol)
    options.append(option)
    symbols = []
    # Create a list of all option symbols to reduce API calls
    for option in options:
        print(option)
        symbols.append(option.symbol)
    # Get option quotes for each option
    quotes = td_account.get_quotes(symbols)
    positions = []
    # For each option extract relevant quote data and append all of the information into a list which will stand as a position.
    for index, option in enumerate(options):
        quote = quotes.iloc[index]
        bid_price = quote['bidPrice']
        ask_price = quote['askPrice']
        if quantity > 0:
            trade_price = quote['askPrice']
        elif quantity < 0:
            trade_price = quote['bidPrice']
        else:
            return 100, "Don't put 0 as quantity"
        delta = quote['delta']
        theta = quote['theta']
        gamma = quote['gamma']
        vega = quote['vega']
        volatility = quote['volatility']
        description = quote['description']
        if description == 'Symbol not found':
            return 305, 'Symbol not found'
        asset_type = quote['assetType']
        positions.append([trade_id, ticker, asset_type, symbol, quantity, date, side, trade_price, strike, bid_price, ask_price, delta, theta, gamma, vega, description, author, channel, dt.datetime.now()])
    columns = ['id', 'ticker', 'asset', 'symbol', 'quantity', 'date', 'side','trade_price', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'vega', 'description', 'trader', 'channel', 'time']
    # Create a new position dataframe with each row as a full position.
    position_df = pd.DataFrame(data=positions, columns=columns)
    return 200, (position_df, 'single', avg_price)

def handle_temp_order(order, author, channel, td_account, desired_function):
    position_status, data = desired_function(order, author, channel, td_account)
    if position_status == 200:
        position_df = data[0]
        position_csv_handler = CSVHandler('new_positions.csv', 'id')
        position_csv_handler.add_rows(position_df)
        return 200, position_df
    return position_status, data

def handle_closing_order(order, author, channel, td_account, specific_trade=(True, None)):
    commands = pd.read_csv('command_db.csv')['NAME'].values
    order_splits = order.split(' ')
    name = order_splits[0]
    trade_db = pd.read_csv('trades_db.csv', index_col=0)
    if specific_trade[1] is None:
        trade = trade_db[trade_db['CLOSED'] == False]
        if name in commands:
            single = False
            trade = trade[trade['COMMAND'] == name]
            ticker = order_splits[1].upper()
        else:
            single = True
            trade = trade[trade['COMMAND'] == 'standard'] 
            ticker = order_splits[0].upper()
        trade = trade[trade['TRADER'] == author]
        trade = trade[trade['TICKER'] == ticker]
    else:
        single = specific_trade[0]
        trade = specific_trade[1]
    if len(trade) == 1:
        trade_id = trade['ID'].values[0]
        positions = pd.read_csv('positions_db.csv', index_col=0)
        positions = positions[positions['id'] == trade_id]
        new_positions = []
        new_data ={'bidPrice':None,'askPrice':None,'delta':None,'theta':None,'gamma':None,'volatility':None,'description':None,'assetType':None}
        symbols = []
        for index, position_row in positions.iterrows():
            symbols.append(position_row['symbol'])
        quotes = td_account.get_quotes(symbols)
        quote_index = 0
        for index, position_row in positions.iterrows():
            new_position = []
            if not single:
                quote = quotes.iloc[quote_index]
            else:
                quote = quotes.iloc[0]
            quote_index +=1
            for key in new_data.keys():
                new_data[key] = quote[key]
            for index, data_point in enumerate(position_row):
                if index == len(position_row)-1:
                    new_position.append(True)
                else:
                    new_position.append(data_point)
            temp_columns = ['id', 'ticker', 'date', 'side', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'volatility', 'description', 'assetType', 'symbol', 'short_trade', 'executed', 'trader', 'channel', 'time','closing']
            position_dict = dict(zip(temp_columns, new_position))
            for key in new_data.keys():
                position_dict[key] = new_data[key]
            position_dict['time'] = dt.datetime.now()
            new_positions.append(position_dict.values())
        columns = ['id', 'ticker', 'date', 'side', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'volatility', 'description', 'assetType', 'symbol', 'short_trade', 'executed', 'trader', 'channel', 'time','closing']
        new_positions_df = pd.DataFrame(data=new_positions, columns=columns)
        position_db = pd.read_csv('positions_db.csv', index_col=0)
        position_db = position_db.append(new_positions_df, ignore_index = True)
        position_db.to_csv('positions_db.csv')
        credit = 0
        for index, row in new_positions_df.iterrows():
            if row['short_trade']:
                credit -= row['bidPrice']
            else:
                credit += row['askPrice']
        credit = round(float(credit), 2)
        trade['PROFIT'] =  round(float(((credit + trade['NET_PRICE'].values[0])/abs(trade['NET_PRICE']))*100),2)
        trade['CLOSED'] = True
        trade_db.iloc[trade.index] = trade
        trade_db.to_csv('trades_db.csv')
        profit_str = ' for recorded profit of ' + str(round(float(((credit + trade['NET_PRICE'].values[0])/abs(trade['NET_PRICE']))*100),2)) + '%'
        sell_str = ' Buying the'
        buy_str = ' Selling the' 
        x = 0
        s = 0
        for index, position in new_positions_df.iterrows():
            if position['short_trade']:
                sell_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and'
            else:
                buy_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and' 
        if single:
            for index, position in new_positions_df.iterrows():
                if not position['short_trade']:
                    buy_str = ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') 
            return 200, '**Success**\nClosed ' + trade['TICKER'].values[0] + buy_str + ' ' +  trade['DATE'].values[0] + profit_str
        return 200, '**Success**\nClosed ' + trade['TICKER'].values[0] + ' ' + trade['COMMAND'].values[0] + ' ' + trade['DATE'].values[0] + buy_str + sell_str + profit_str
    elif len(trade) == 0:
        return 100, 'Failed to find position in holdings. Type .check status to view your current holdings'
    elif len(trade) == 2:
        if len(order_splits) < 2:
            return 101, trade
        if single:
            date = None
            for item in order_splits:
                if '/' in item:
                    date = item
            strike = None
            if date is None:
                for item in order_splits:
                    if check_float(item):
                        strike = item
            positions = pd.read_csv('positions_db.csv')
            ids = []
            for index, tr in trade.iterrows():
                ids.append(tr['ID'])
            trade_id = None
            if date is not None:
                for index, tr in trade.iterrows():
                    if tr['DATE'] == date:
                        trade_id = tr['ID']
            if strike is not None:
                for pos_id in ids:
                    spec_positions = positions[positions['id'] == pos_id]
                    for index, row in spec_positions.iterrows():
                        if float(row['strike']) == float(strike):
                            for trade_index, trade_row in trade.iterrows():
                                if trade_row['ID'] == row['id']:
                                    trade_id = row['id']
            if trade_id is None:
                return 100, 'Failed to find position in holdings. Type .check status to view your current holdings'
            return handle_closing_order(order, author, channel, td_account, (True, trade[trade['ID'] == trade_id]))
      
def handle_order(order, author, channel, td_account):
    commands = pd.read_csv('command_db.csv')['NAME'].values
    name = 'Single'
    desired_function = handle_single_order
    if 'ironcondor' in order.lower():
        desired_function = parse_ironcondor
        name = 'Iron Condor'
    if 'creditspread' in order.lower():
        desired_function = parse_creditspread
        name = 'Credit Spread'
    if 'debitspread' in order.lower():
        desired_function = parse_debitspread
        name = 'Debit Spread'
    status_code, data = handle_temp_order(order, author, channel, td_account, desired_function)
    print(status_code, data)
    if status_code == 200:
        if name == 'Single':
            position_df = data
            positions = []
            for i in range(0, position_df.shape[0]):
                positions.append(position_df.iloc[i])
            position = positions[0]
            ticker = position['ticker']
            date = position['date']
            fill_price = position['trade_price']
            strike = position['strike']
            side = position['side']
            return 200, '**Success**\nOpened **' + ticker.upper() + ' ' + str(strike) + ' ' + side + ' ' + date + '**\nFilled at ' + str(fill_price)
        else:
            pass
        # position_df = data
        # positions = []
        # for i in range(0, position_df.shape[0]):
        #     positions.append(position_df.iloc[i])
        # sell_str = 'Selling the'
        # buy_str = 'Buying the' 
        # x = 0
        # s = 0
        # for position in positions:
        #     if position['short_trade']:
        #         sell_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and'
        #     else:
        #         buy_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and' 
        # sell_str = ' '.join(sell_str.split(' ')[:-1])
        # buy_str = ' '.join(buy_str.split(' ')[:-1])
        # credit = ''
        # if trade_sr['NET_PRICE'] > 0:
        #     credit = ' TOA '
        # else:
        #     credit = ' TOA '
        # price_str = ''
        # if trade_sr['AVG_PRICE'] == None:
        #     price_str = credit + str(trade_sr['NET_PRICE'])
        # else:
        #     price_str = credit + str(trade_sr['NET_PRICE']) + ' Avg Price ' + str(trade_sr['AVG_PRICE'])
        # if name == 'standard':
        #     position = positions[0]
        #     strike = position['strike']
        #     side = position['side']
        #     return 200, '**Success**\nOpened **' + trade_sr['TICKER'] + ' ' + strike + ' ' + side + ' ' + trade_sr['DATE'] + '** ' + price_str
        # return 200, '**Success**\nOpened ' + trade_sr['TICKER'] + ' ' + name[0].upper()+name[1:] + ' ' + buy_str + ', ' + sell_str + ' for ' + trade_sr['DATE'] + price_str
    elif status_code == 300:
        return 300, '**Unable to parse average price**'
    elif status_code == 301:
        return 301, '**Unable to parse calls/puts**\nMake sure to specify.'
    elif status_code == 305:
        return 305, '**Option symbol not found**\nThis could be for a variety of reasons, the most common are invalid date or invalid strike.'
    elif status_code == 400:
        return 400, '**Unable to find any strikes**'
    elif status_code == 401:
        return 401, '**Invalid number of strikes**\nI was expecting ' + command_info['STRIKE_NUM'] + ' strikes'
    elif status_code == 402:
        return 402, '**Expiration date not found**\nMake sure to indicate date with ' + command_info['DATE_SEP']
    elif status_code == 403:
        return 402, '**Quantity not found**\nMake sure to specify with qty or turn off quantity via .account disable quantity'
    elif status_code == 399:
        return 399, '**Unable to find Stock Symbol ' + str(order_splits[0]) + '**'
    elif status_code == 405:
        return 405, '**Unable to determine side**\nMake sure to specify calls or puts'
    elif status_code == 406:
        return 406, '**Unable to find option data for specified option**\nThis could be for a variety of reasons but most likely is the date is incorrect'
    return 500, '**ERROR**\n Something went very wrong. @Charlie678'
