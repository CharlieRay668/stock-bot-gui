import pandas as pd
import numpy as np
import datetime as dt
from io import StringIO
from TDRestAPI import Rest_Account
import uuid
from csv_manager import CSVHandler

look_up = {'01': 'January', '02': 'Febuary', '03': 'March', '04': 'April', '05': 'May',
            '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

look_up_short = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May',
            '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

reverse_look_up = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
            'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

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

def parse_ironcondor(order, author, channel, td_account,quantity_multiplier):
    pass
def parse_creditspread(order, author, channel, td_account,quantity_multiplier):
    pass
def parse_debitspread(order, author, channel, td_account,quantity_multiplier):
    pass

def handle_single_order(order, author, channel, td_account, quantity_multiplier):
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
            avg_price = item.replace('@', '')
            found.append(item)
    # Parsing strikes is different for individual options and complex orders
    options = []
    # Maybe hard code complex orders
    # If the order is complex continue
    # For each item that we have found (ticker, date, average price) remove it from the order string to make parsing strikes and order side easier.
    print(order, found)
    for item in found:
        print(item)
        order.remove(item.lower())
    quantity = None
    for item in order:
        if 'qty' in item:
            quantity_str = item
            quantity = item.replace('qty', '')
            quantity = quantity.replace('=','').replace(':','')
    if quantity is None:
        quantity = 1
        quantity_str = '1'
        order.append(quantity_str)
        #return 403, 'Quantity not Found'
    found = []
    found.append(quantity_str)
    for item in found:
        order.remove(item.lower())
    try:
        quantity = int(quantity)*quantity_multiplier
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
        description = quote['description'].replace('(Weekly)', '').strip()
        if description == 'Symbol not found':
            return 305, 'Symbol not found'
        asset_type = quote['assetType']
        positions.append([trade_id, ticker, asset_type, symbol, quantity, date, side, trade_price, strike, bid_price, ask_price, delta, theta, gamma, vega, description, author, channel, dt.datetime.now()])
    columns = ['id', 'ticker', 'asset', 'symbol', 'quantity', 'date', 'side','trade_price', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'vega', 'description', 'trader', 'channel', 'time']
    # Create a new position dataframe with each row as a full position.
    position_df = pd.DataFrame(data=positions, columns=columns)
    return 200, (position_df, 'single', avg_price)

def handle_temp_order(order, author, channel, td_account, desired_function, quantity_multiplier):
    position_status, data = desired_function(order, author, channel, td_account, quantity_multiplier)
    if position_status == 200:
        position_df = data[0]
        position_csv_handler = CSVHandler('new_positions.csv', 'id')
        position_csv_handler.add_rows(position_df)
        return 200, position_df
    return position_status, data

def get_open_positions(username):
    positions_db = pd.read_csv('new_positions.csv', index_col=0)
    user_positions = positions_db[positions_db['trader'] == username]
    descriptions = []
    for index, row in user_positions.iterrows():
        descriptions.append(row['description'])
    descriptions = list(set(descriptions))
    open_descriptions = []
    for description in descriptions:
        same_trades = user_positions[user_positions['description'] == description]
        qty = 0
        for index, pos in same_trades.iterrows():
            qty += pos['quantity']
        if qty > 0 or qty < 0:
            open_descriptions.append((qty, description))
    return open_descriptions

def order_to_description(order):
    splits = order.split(' ')
    date = None
    ticker = splits[0]
    strike = None
    side = None
    for item in splits:
        if '/' in item:
            date = item
    if 'call' or 'c' or 'calls' in order.lower():
        side = 'Call'
    elif 'put' or 'p' or 'puts' in order.lower():
        side = 'Put'
    for item in splits:
        if 's' in item and (check_int(item.replace('s','').replace(':','').replace('=',''))):
            strike = item
    if date is not None:
        print(date)   
        if len(date.split('/')) == 2:
            year = '2021'
        elif len(date.split('/')) == 3:
            year = date.split('/')[2]
        month = str(date.split('/')[0])
        if len(month) < 2:
            month = '0' + month
        day = str(date.split('/')[1])
        return_str = ticker.upper() + ' ' + look_up_short[month] + ' ' + day + ' ' + year + ' ' + str(strike) + ' ' + str(side)
        return date, ticker, strike, side, return_str
    return_str = ticker.upper() + ' None ' + str(strike) + ' ' + str(side)
    return date, ticker, strike, side, return_str


def close_position_given_symbol_qty(qty, symbol, author, channel, td_account):
    trade_id = uuid.uuid1().hex
    ticker = symbol.split('_')[0]
    other_info = symbol.split('_')[1]
    month = other_info[:2]
    day = other_info[2:4]
    year = other_info[4:6]
    side = other_info[6]
    if side == 'C':
        side == 'Calls'
    if side == 'P':
        side == 'Puts'
    strike = other_info[7:]
    date = month+'/'+day+'/'+year
    quantity = qty*-1
    quotes = td_account.get_quotes(symbol)
    positions = []
    # For each option extract relevant quote data and append all of the information into a list which will stand as a position.
    quote = quotes.iloc[0]
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
    description = quote['description'].replace('(Weekly)','').strip()
    if description == 'Symbol not found':
        return 305, 'Symbol not found'
    asset_type = quote['assetType']
    positions.append([trade_id, ticker, asset_type, symbol, quantity, date, side, trade_price, strike, bid_price, ask_price, delta, theta, gamma, vega, description, author, channel, dt.datetime.now()])
    columns = ['id', 'ticker', 'asset', 'symbol', 'quantity', 'date', 'side','trade_price', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'vega', 'description', 'trader', 'channel', 'time']
    position_df = pd.DataFrame(data=positions, columns=columns)
    position_csv_handler = CSVHandler('new_positions.csv', 'id')
    position_csv_handler.add_rows(position_df)
    return 200, position_df

def description_from_symbol(symbol):
    ticker = symbol.split('_')[0]
    other_info = symbol.split('_')[1]
    month = other_info[:2]
    day = other_info[2:4]
    if day[0] == '0':
        day = day[1:]
    year = other_info[4:6]
    year = '20' + year
    side = other_info[6]
    if side == 'C':
        side = 'Call'
    if side == 'P':
        side = 'Put'
    strike = other_info[7:]
    return ticker.upper() + ' ' + look_up_short[month] + ' ' + day + ' ' + year + ' ' + strike + ' ' + side

def symbol_from_description(description):
    splits = description.split(' ')
    ticker = splits[0]
    month = splits[1]
    month = reverse_look_up[month]
    day = splits[2]
    if len(day) < 2:
        day = '0' + day
    year = splits[3]
    year = year[2:]
    strike = splits[4]
    side = splits[5]
    if side == 'Call':
        side = 'C'
    if side == 'Put':
        side = 'P'
    symbol = ticker.upper() + '_' + month + day + year + side + strike
    return symbol

def close_position_given_symbol(symbol, author, channel, td_account):
    needed_desctiption = description_from_symbol(symbol)
    print(needed_desctiption)
    status, response = close_position_given_description(needed_desctiption, author, channel, td_account)
    if status != 200:
        return 300, 'Unable to find any open positions with the exact symbol ' + symbol
    return status, response

def close_position_given_description(description, author, channel, td_account):
    open_positions = get_open_positions(author)
    for qty, open_description in open_positions:
        if open_description == description:
            symbol = symbol_from_description(description)
            close_position_given_symbol_qty(qty, symbol, author, channel, td_account)
            if qty > 0:
                return 200, 'Closed position\n ' + description + '. Sold ' + str(qty) + ' shares/contracts.'
            elif qty < 0:
                return 200, 'Closed position\n ' + description + '. Bought ' + str(qty) + ' shares/contracts.'
    return 300, 'Unable to find any open position with the exact description ' + description

def handle_closing_order(order, author, channel, td_account):
    date, ticker, strike, side, attempted_description = order_to_description(order)
    ticker = ticker.upper()
    positions_db = pd.read_csv('new_positions.csv', index_col=0)
    open_positions = get_open_positions(author)
    descriptions = []
    for qty, description in open_positions:
        descriptions.append(description)
    targeted = [description for description in descriptions if ticker in description]
    if len(targeted) == 0:
        return 300, 'Unable to find any holdings with underlying ' + ticker
    if len(targeted) == 1:
        for qty, description in open_positions:
            if description == targeted[0]:
                symbol = symbol_from_description(description)
                close_position_given_symbol_qty(qty, symbol, author, channel, td_account)
                if qty > 0:
                    return 200, 'Closed position\n ' + description + '. Sold ' + str(qty) + ' shares/contracts.'
                elif qty < 0:
                    return 200, 'Closed position\n ' + description + '. Bought ' + str(qty) + ' shares/contracts.'
    if date is not None:
        date_str = attempted_description.split(' ')[1:4]
        targeted = [description for description in targeted if date_str in description]
        if len(targeted) == 0:
            return 300, 'Unable to find any holdings with both underlying ' + ticker + ' and expiry ' + date_str
        if len(targeted) == 1:
            for qty, description in open_positions:
                if description == targeted[0]:
                    symbol = symbol_from_description(description)
                    close_position_given_symbol_qty(qty, symbol, author, channel, td_account)
                    if qty > 0:
                        return 200, 'Closed position\n ' + description + '. Sold ' + str(qty) + ' shares/contracts.'
                    elif qty < 0:
                        return 200, 'Closed position\n ' + description + '. Bought ' + str(qty) + ' shares/contracts.'
    if strike is not None:
        targeted = [description for description in targeted if strike in description]
        if len(targeted) == 0:
            return 300, 'Unable to find any holdings with both underlying ' + ticker + ' and strike ' + strike
        if len(targeted) == 1:
            for qty, description in open_positions:
                if description == targeted[0]:
                    symbol = symbol_from_description(description)
                    close_position_given_symbol_qty(qty, symbol, author, channel, td_account)
                    if qty > 0:
                        return 200, 'Closed position\n ' + description + '. Sold ' + str(qty) + ' shares/contracts.'
                    elif qty < 0:
                        return 200, 'Closed position\n ' + description + '. Bought ' + str(qty) + ' shares/contracts.'
    if side is not None:
        targeted = [description for description in targeted if side in description]
        if len(targeted) == 0:
            return 300, 'Unable to find any holdings with both underlying ' + ticker + ' and side ' + side
        if len(targeted) == 1:
            for qty, description in open_positions:
                if description == targeted[0]:
                    symbol = symbol_from_description(description)
                    close_position_given_symbol_qty(qty, symbol, author, channel, td_account)
                    if qty > 0:
                        return 200, 'Closed position\n ' + description + '. Sold ' + str(qty) + ' shares/contracts.'
                    elif qty < 0:
                        return 200, 'Closed position\n ' + description + '. Bought ' + str(qty) + ' shares/contracts.'
    return 300, 'Unable to close position with given information. I thought you said\nTICKER: **'+str(ticker)+'** DATE: **'+str(date)+'** STRIKE: **'+str(strike)+'** SIDE: **' +str(side)+'**'
      
def handle_order(order, author, channel, td_account, quantity_multiplier):
    order_splits = order.split(' ')
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
    status_code, data = handle_temp_order(order, author, channel, td_account, desired_function, quantity_multiplier)
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
            if quantity_multiplier == 1:
                return 200, '**Success**\nBought **' + ticker.upper() + ' ' + str(strike) + ' ' + side + ' ' + date + '**\nFilled at ' + str(fill_price)
            elif quantity_multiplier == -1:
                return 200, '**Success**\nSold **' + ticker.upper() + ' ' + str(strike) + ' ' + side + ' ' + date + '**\nFilled at ' + str(fill_price)
            else:
                return 200, '**Success**\nThis should not be happening **' + ticker.upper() + ' ' + str(strike) + ' ' + side + ' ' + date + '**\nFilled at ' + str(fill_price)
        else:
            pass
    elif status_code == 300:
        return 300, '**Unable to parse average price**'
    elif status_code == 301:
        return 301, '**Unable to parse calls/puts**\nMake sure to specify.'
    elif status_code == 305:
        return 305, '**Option symbol not found**\nThis could be for a variety of reasons, the most common are invalid date or invalid strike.'
    elif status_code == 400:
        return 400, '**Unable to find any strikes**'
    elif status_code == 401:
        return 401, '**Invalid number of strikes**\nI was expecting at least one strike'
    elif status_code == 402:
        return 402, '**Expiration date not found**\nMake sure to indicate date with /'
    elif status_code == 403:
        return 402, '**Quantity not found**\nMake sure to specify with qty or turn off quantity via .account disable quantity'
    elif status_code == 399:
        return 399, '**Unable to find Stock Symbol ' + str(order_splits[0]) + '**'
    elif status_code == 405:
        return 405, '**Unable to determine side**\nMake sure to specify calls or puts'
    elif status_code == 406:
        return 406, '**Unable to find option data for specified option**\nThis could be for a variety of reasons but most likely is the date is incorrect'
    return 500, '**ERROR**\n Something went very wrong. @Charlie678'
