import pandas as pd
import numpy as np
import datetime as dt
from io import StringIO
from TDRestAPI import Rest_Account
import uuid
from csv_manager import CSVHandler

class Option():
    def __init__(self, ticker, side, strike, date, buy, symbol):
        self.ticker = ticker
        self.side = side
        self.strike = strike
        self.date = date
        self.buy = buy
        self.symbol = symbol

    def __str__(self):
        return str(self.ticker) + ' ' +str(self.strike) + ' ' + str(self.date) + ' ' + str(self.side) + ' ' + str(self.buy)

def parse_strikes(strike_str, order_struct, strike_split):
    strike_str = strike_str.upper()
    strikes = strike_str.split(strike_split)
    calls = [(item[:-1], item[-1]) for item in strikes if 'C' in item]
    puts = [(item[:-1], item[-1]) for item in strikes if 'P' in item]
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

def handle_positions(order, author, channel, td_account, single=True):
    # Generate unique trade uuid
    trade_id = uuid.uuid1().hex
    order = order.split(' ')
    # Get ticker from order
    if single:
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
    # Get the command info from the database and read it into a dictionary
    data = pd.read_csv('command_db.csv', index_col=0)
    command_info = data[data['NAME'] == name]
    command_info = command_info.to_dict()
    # Structure the command info to behave like a normal dictionary, reading dicts from pandas can sometimes give strange results
    for key in command_info:
        index = None
        for i in command_info[key]:
            index = i
        command_info[key] = command_info[key][i]


    # Create a list called 'found'. This is where we store all the information we have parsed from the order. Initialize it with the ticker
    found = [ticker]
    # Parse the date out from the order using the identifier specified in the command info, throw error if not found, append it to found list.
    date = None
    for item in order:
        if command_info['DATE_SEP'] in item:
            date = item
    if date is None:
        return 402, 'Expiration Date not Found'
    found.append(date)

    # Try to predict the year from only MM/DD. If MM/DD is in the past we can assume that year is in the future. If not year is present year. If year is specified go with that.
    if int(date.split(command_info['DATE_SEP'])[0]) < dt.datetime.now().month or (int(date.split(command_info['DATE_SEP'])[0]) == dt.datetime.now().month and int(date.split(command_info['DATE_SEP'])[1]) < dt.datetime.now().day):
        year = '21'
    else:
        year = '20'
    for item in order:
        if 'year=' in item.lower():
            year = int(item.split('year=')[1])

    # Parse out the average price from the order using the identifier specifed in the command info. If average price does not exist then continue else, try to clean it.
    avg_price = None
    for item in order:
        if command_info['AVERAGE_PRICE_SEP'] in item:
            avg_price = item
            found.append(avg_price)
    if avg_price is not None:
        try:
            avg_price = float(item.replace(command_info['AVERAGE_PRICE_SEP'], ''))
        except:
            300, 'Unable to clean average price'

    # Parsing strikes is different for individual options and complex orders
    options = []
    # If the order is complex continue
    if not single:
        # Parse out each individual strike for the complex order. If there are no strikes or an invalid number of strikes return so.
        strikes = []
        for item in order:
            if command_info['STRIKE_SEP'] in item:
                strikes.append(item)
        if len(strikes) == 0:
            return 400, 'No Strikes Found'
        strikes = command_info['STRIKE_SEP'].join(strikes)
        if len(strikes.split(command_info['STRIKE_SEP'])) != command_info['STRIKE_NUM']:
            return 401, 'Invalid Number of Strikes'
        # Parse the order structer from the command info to determine which strikes are being bought and which are being sold
        order_struct = remove_chars(command_info['ORDER_STRUCT'], ['[', ']', "'", ',']).split()
        buys, sells, buy_str, sell_str = parse_strikes(strikes, order_struct, command_info['STRIKE_SEP'])
        # For each buy determine if it is a call or a put
        for strike, option in buys:
            option = option.upper()
            if option == "C" or option =='CALLS' or option == 'CALL' or option == 'c' or option =='calls' or option == 'call':
                side = 'CALLS'
            else:
                side = 'PUTS'
            # Get an option symbol and append it to the list of total options
            symbol = td_account.get_option_symbol(ticker, strike, year, date.split(command_info['DATE_SEP'])[0], date.split(command_info['DATE_SEP'])[1], side)
            options.append(Option(ticker, side, strike, date, True, symbol))
        # For each sell determine if it is a call or put
        for strike, option in sells:
            option = option.upper()
            if option == "C" or option =='CALLS' or option == 'CALL' or option == 'c' or option =='calls' or option == 'call':
                side = 'CALLS'
            else:
                side = 'PUTS'
            # Get an option symbol and append it to the list of total options
            symbol = td_account.get_option_symbol(ticker, strike, year, date.split(command_info['DATE_SEP'])[0], date.split(command_info['DATE_SEP'])[1], side)
            options.append(Option(ticker, side, strike, date, False, symbol))
    else:
         # For each item that we have found (ticker, date, average price) remove it from the order string to make parsing strikes and order side easier.
        for item in found:
            order.remove(item.lower())
        side = None
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
        # Determine year from given date. If the specified date is backwards in time we can assume that they are talking about a year ahead. if not its a year ahead.
        # Get a symbol for specified option and append it to the total options
        symbol = td_account.get_option_symbol(ticker, strike, year, date.split('/')[0], date.split('/')[1], side)
        option = Option(ticker, side, strike, date, True, symbol)
        options.append(option)

    # Now the complex and simple orders converge, the only difference is that the complex orders have multiple options and thus multiple positions.
    symbols = []
    # Create a list of all option symbols to reduce API calls
    for option in options:
        symbols.append(option.symbol)
    # Get option quotes for each option
    quotes = td_account.get_quotes(symbols)
    positions = []
    # For each option extract relevant quote data and append all of the information into a list which will stand as a position.
    for index, option in enumerate(options):
        quote = quotes.iloc[index]
        bid_price = quote['bidPrice']
        ask_price = quote['askPrice']
        delta = quote['delta']
        theta = quote['theta']
        gamma = quote['gamma']
        volatility = quote['volatility']
        description = quote['description']
        if description == 'Symbol not found':
            return 305, 'Symbol not found'
        asset_type = quote['assetType']
        short = not option.buy
        positions.append([trade_id, ticker, date, option.side, option.strike, bid_price, ask_price, delta, theta, gamma, volatility, description, asset_type, option.symbol, short, False, author, channel, dt.datetime.now(), False])
    columns = ['id', 'ticker', 'date', 'side', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'volatility', 'description', 'assetType', 'symbol', 'short_trade', 'executed', 'trader', 'channel', 'time','closing']
    # Create a new position dataframe with each row as a full position.
    position_df = pd.DataFrame(data=positions, columns=columns)
    return 200, (position_df, name, avg_price)

def trade_df_from_position_df(position_df, name, avg_price):
    credit = 0
    trade_id = None
    author = None
    ticker = None
    date = None
    for index, row in position_df.iterrows():
        if row['short_trade']:
            credit += row['bidPrice']
        else:
            credit -= row['askPrice']
        trade_id = row['id']
        author = row['trader']
        ticker = row['ticker']
        date = row['date']
    COLUMNS = ['ID', 'TRADER', 'COMMAND', 'TICKER', 'POSITIONS', 'NET_PRICE', 'OPENING', 'DATE', 'AVG_PRICE','CLOSED','PROFIT']
    if credit is not None:
        credit = round(float(credit), 2)
    if avg_price is not None:
        avg_price = round(float(avg_price), 2)
    trade_df = pd.DataFrame(data=[[trade_id, author, name, ticker, len(position_df.index), credit, True, date, avg_price, False, np.nan]], columns=COLUMNS)
    return 200, trade_df

def handle_temp_order(order, author, channel, td_account, single=True):
    position_status, data = handle_positions(order, author, channel, td_account, single)
    if position_status == 200:
        position_df = data[0]
        name = data[1]
        avg_price = data[2]
        trade_status, trade_df = trade_df_from_position_df(position_df, name, avg_price)
        if trade_status == 200:
            position_csv_handler = CSVHandler('temp_positions.csv', 'id')
            trade_csv_handler = CSVHandler('temp_trades.csv', 'ID')
            position_csv_handler.add_rows(position_df)
            trade_csv_handler.add_rows(trade_df)
            return 200, (position_df, trade_df)
        return trade_status, trade_df
    return position_status, data


def handle_single_order(order, author, channel, td_account):
    # Generate unique trade uuid
    trade_id = uuid.uuid1().hex
    order = order.split(' ')
    # Get ticker from order
    ticker = order[0].upper()
    # Get stock data from ticker
    quote = td_account.get_quotes(ticker)
    # Check to see if the ticker is valid
    if quote is None:
        return 399, 'Unable to find stock symbol'
    # Get the command info from the database and read it into a dictionary
    data = pd.read_csv('command_db.csv', index_col=0)
    command_info = data[data['NAME'] == 'standard']
    command_info = command_info.to_dict()
    # Structure the command info to behave like a normal dictionary, reading dicts from pandas can sometimes give strange results
    for key in command_info:
        index = None
        for i in command_info[key]:
            index = i
        command_info[key] = command_info[key][i]
    # Create a list called 'found'. This is where we store all the information we have parsed from the order. Initialize it with the ticker
    found = [ticker]
    # Parse the date out from the order using the identifier specified in the command info, throw error if not found, append it to found list.
    date = None
    for item in order:
        if command_info['DATE_SEP'] in item:
            date = item
    if date is None:
        return 402, 'Expiration Date not Found'
    found.append(date)
    # Parse out the average price from the order using the identifier specifed in the command info. If average price does not exist then continue else, try to clean it.
    avg_price = None
    for item in order:
        if command_info['AVERAGE_PRICE_SEP'] in item:
            avg_price = item
            found.append(avg_price)
    if avg_price is not None:
        try:
            avg_price = float(item.replace(command_info['AVERAGE_PRICE_SEP'], ''))
        except:
            300, 'Unable to clean average price'
    # For each item that we have found (ticker, date, average price) remove it from the order string to make parsing strikes and order side easier.
    for item in found:
        order.remove(item.lower())
    side = None
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
    # Determine year from given date. If the specified date is backwards in time we can assume that they are talking about a year ahead. if not its a year ahead.
    if int(date.split('/')[0]) < dt.datetime.now().month or (int(date.split('/')[0]) == dt.datetime.now().month and int(date.split('/')[1]) < dt.datetime.now().day):
        year = '21'
    else:
        year = '20'
    for item in order:
        if 'year=' in item.lower():
            year = int(item.split('year=')[1])
    # if not year == '20':
    #     date += '/' + year
    # Get option data from generated symbol.
    symbol = td_account.get_option_symbol(ticker, strike, year, date.split('/')[0], date.split('/')[1], side)
    option_quote = td_account.get_quotes(symbol)
    option = Option(ticker, side, strike, date, True, symbol)
    position = []
    # If we cant get option data for specifed symbol return so. 
    if option_quote is None:
        return 406, 'Unable to get option data for ' + str(symbol)
    # Extract all neccessary option information from the returned TD Ameritrade Option data.
    option_quote = option_quote.iloc[0]
    bid_price = option_quote['bidPrice']
    ask_price = option_quote['askPrice']
    delta = option_quote['delta']
    theta = option_quote['theta']
    gamma = option_quote['gamma']
    volatility = option_quote['volatility']
    description = option_quote['description']
    if description == 'Symbol not found':
        return 305, 'Symbol not found'
    asset_type = option_quote['assetType']
    short = not option.buy
    # Create our new position.
    position.append([trade_id, ticker, date, option.side, option.strike, bid_price, ask_price, delta, theta, gamma, volatility, description, asset_type, option.symbol, short, False, author, channel, dt.datetime.now(),False])
    columns = ['id', 'ticker', 'date', 'side', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'volatility', 'description', 'assetType', 'symbol', 'short_trade', 'executed', 'trader', 'channel', 'time','closing']
    # Add the new position to the positons db
    position_df = pd.DataFrame(data=position, columns=columns)
    # HERE TRANSFER TO CSV HANDELR
    position_db = pd.read_csv('positions_db.csv', index_col=0)
    position_db = position_db.append(position_df, ignore_index = True)
    position_db.to_csv('positions_db.csv')
    # Calculate how much money was spent on the option.
    credit = 0
    for index, row in position_df.iterrows():
        if row['short_trade']:
            credit += row['bidPrice']
        else:
            credit -= row['askPrice']
    COLUMNS = ['ID', 'TRADER', 'COMMAND', 'TICKER', 'POSITIONS', 'NET_PRICE', 'OPENING', 'DATE', 'AVG_PRICE','CLOSED','PROFIT']
    if credit is not None:
        credit = round(float(credit), 2)
    if avg_price is not None:
        avg_price = round(float(avg_price), 2)
    # Generate and save the trade from the initial option order.
    trade_df = pd.DataFrame(data=[[trade_id, author, 'standard', ticker, len(position_df.index), credit, True, date, avg_price, False, np.nan]], columns=COLUMNS)
    trade_db = pd.read_csv('trades_db.csv', index_col=0)
    trade_db = trade_db.append(trade_df, ignore_index = True)
    trade_db.to_csv('trades_db.csv')
    return trade_df, position_df

def handle_order(order, author, channel, td_account):
    trade_id = uuid.uuid1().hex
    order = order.split(' ')
    name = order[0].lower()
    ticker = order[1].upper()
    quote = td_account.get_quotes(ticker)
    if quote is None:
        return 399, 'Unable to find stock symbol'
    data = pd.read_csv('command_db.csv', index_col=0)
    command_info = data[data['NAME'] == name]
    command_info = command_info.to_dict()
    for key in command_info:
        index = None
        for i in command_info[key]:
            index = i
        command_info[key] = command_info[key][i]
    strikes = []
    for item in order:
        if command_info['STRIKE_SEP'] in item:
            strikes.append(item)
    if len(strikes) == 0:
        return 400, 'No Strikes Found'
    strikes = command_info['STRIKE_SEP'].join(strikes)
    if len(strikes.split(command_info['STRIKE_SEP'])) != command_info['STRIKE_NUM']:
        return 401, 'Invalid Number of Strikes'
    dates = []
    for item in order:
        if command_info['DATE_SEP'] in item:
            dates.append(item)
    if len(dates) == 0:
        return 402, 'Expiration Date not Found'
    date = dates[0]
    avg_price = None
    for item in order:
        if command_info['AVERAGE_PRICE_SEP'] in item:
            avg_price = item
    if avg_price is not None:
        avg_price = float(item.replace(command_info['AVERAGE_PRICE_SEP'], ''))
    order_struct = remove_chars(command_info['ORDER_STRUCT'], ['[', ']', "'", ',']).split()
    buys, sells, buy_str, sell_str = parse_strikes(strikes, order_struct, command_info['STRIKE_SEP'])
    options = []
    if int(date.split(command_info['DATE_SEP'])[0]) < dt.datetime.now().month or (int(date.split(command_info['DATE_SEP'])[0]) == dt.datetime.now().month and int(date.split(command_info['DATE_SEP'])[1]) < dt.datetime.now().day):
        year = '21'
    else:
        year = '20'
    for item in order:
        if 'year=' in item.lower():
            year = int(item.split('year=')[1])
    if not year == '20':
        date += command_info['DATE_SEP'] + year
    for strike, option in buys:
        option = option.upper()
        if option == "C" or option =='CALLS' or option == 'CALL' or option == 'c' or option =='calls' or option == 'call':
            side = 'CALLS'
        else:
            side = 'PUTS'
        symbol = td_account.get_option_symbol(ticker, strike, '20', date.split(command_info['DATE_SEP'])[0], date.split(command_info['DATE_SEP'])[1], side)
        options.append(Option(ticker, side, strike, date, True, symbol))
    for strike, option in sells:
        option = option.upper()
        if option == "C" or option =='CALLS' or option == 'CALL' or option == 'c' or option =='calls' or option == 'call':
            side = 'CALLS'
        else:
            side = 'PUTS'
        symbol = td_account.get_option_symbol(ticker, strike, '20', date.split(command_info['DATE_SEP'])[0], date.split(command_info['DATE_SEP'])[1], side)
        options.append(Option(ticker, side, strike, date, False, symbol))
    symbols = []
    for option in options:
        symbols.append(option.symbol)
    quotes = td_account.get_quotes(symbols)
    positions = []
    for index, option in enumerate(options):
        quote = quotes.iloc[index]
        bid_price = quote['bidPrice']
        ask_price = quote['askPrice']
        delta = quote['delta']
        theta = quote['theta']
        gamma = quote['gamma']
        volatility = quote['volatility']
        description = quote['description']
        if description == 'Symbol not found':
            return 305, 'Symbol not found'
        asset_type = quote['assetType']
        short = not option.buy
        positions.append([trade_id, ticker, date, option.side, option.strike, bid_price, ask_price, delta, theta, gamma, volatility, description, asset_type, option.symbol, short, False, author, channel, dt.datetime.now(), False])
    columns = ['id', 'ticker', 'date', 'side', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'volatility', 'description', 'assetType', 'symbol', 'short_trade', 'executed', 'trader', 'channel', 'time','closing']
    position_df = pd.DataFrame(data=positions, columns=columns)
    position_db = pd.read_csv('positions_db.csv', index_col=0)
    position_db = position_db.append(position_df, ignore_index = True)
    position_db.to_csv('positions_db.csv')
    credit = 0
    for index, row in position_df.iterrows():
        if row['short_trade']:
            credit += row['bidPrice']
        else:
            credit -= row['askPrice']
    COLUMNS = ['ID', 'TRADER', 'COMMAND', 'TICKER', 'POSITIONS', 'NET_PRICE', 'OPENING', 'DATE', 'AVG_PRICE','CLOSED','PROFIT']
    if credit is not None:
        credit = round(float(credit), 2)
    if avg_price is not None:
        avg_price = round(float(avg_price), 2)
    trade_df = pd.DataFrame(data=[[trade_id, author, name, ticker, len(position_df.index), credit, True, date, avg_price, False, np.nan]], columns=COLUMNS)
    trade_db = pd.read_csv('trades_db.csv', index_col=0)
    trade_db = trade_db.append(trade_df, ignore_index = True)
    trade_db.to_csv('trades_db.csv')
    return trade_df, position_df

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
      
def handle_open(order, author, channel, td_account):
    commands = pd.read_csv('command_db.csv')['NAME'].values
    order_splits = order.split(' ')
    name = order_splits[0]
    single = False
    if not name in commands:
        name = 'standard'
        single = True
    data = pd.read_csv('command_db.csv', index_col=0)
    command_info = data[data['NAME'] == name]
    command_info = command_info.to_dict()
    for key in command_info:
        index = None
        for i in command_info[key]:
            index = i
        command_info[key] = command_info[key][i]
    status_code, data = handle_temp_order(order, author, channel, td_account, single)
    if status_code == 200:
        position_df = data[0]
        trade_df = data[1]
        trade_sr = trade_df.iloc[0]
        positions = []
        for i in range(0, position_df.shape[0]):
            positions.append(position_df.iloc[i])
        sell_str = 'Selling the'
        buy_str = 'Buying the' 
        x = 0
        s = 0
        for position in positions:
            if position['short_trade']:
                sell_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and'
            else:
                buy_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and' 
        sell_str = ' '.join(sell_str.split(' ')[:-1])
        buy_str = ' '.join(buy_str.split(' ')[:-1])
        credit = ''
        if trade_sr['NET_PRICE'] > 0:
            credit = ' TOA Credit of '
        else:
            credit = ' TOA Debit of '
        price_str = ''
        if trade_sr['AVG_PRICE'] == None:
            price_str = credit + str(trade_sr['NET_PRICE'])
        else:
            price_str = credit + str(trade_sr['NET_PRICE']) + ' Avg Price ' + str(trade_sr['AVG_PRICE'])
        return 200, '**Success**\nOpened ' + trade_sr['TICKER'] + ' ' + name[0].upper()+name[1:] + ' ' + buy_str + ', ' + sell_str + ' for ' + trade_sr['DATE'] + price_str
    elif trade_df == 300:
        return 300, '**Unable to parse average price**'
    elif trade_df == 305:
        return 305, '**Option symbol not found**\nThis could be for a variety of reasons, the most common are invalid date or invalid strike.'
    elif trade_df == 400:
        return 400, '**Unable to find any strikes**'
    elif trade_df == 401:
        return 401, '**Invalid number of strikes**\nI was expecting ' + command_info['STRIKE_NUM'] + ' strikes'
    elif trade_df == 402:
        return 402, '**Expiration date not found**\nMake sure to indicate date with ' + command_info['DATE_SEP']
    elif trade_df == 399:
        return 399, '**Unable to find Stock Symbol ' + str(order_splits[0]) + '**'
    elif trade_df == 405:
        return 405, '**Unable to determine side**\nMake sure to specify calls or puts'
    elif trade_df == 406:
        return 406, '**Unable to find option data for specified option**\nThis could be for a variety of reasons but most likely is the date is incorrect'
    return 500, '**ERROR**\n Something went very wrong. @Charlie678'


def classic_open(order, author, channel, td_account):
    commands = pd.read_csv('command_db.csv')['NAME'].values
    order_splits = order.split(' ')
    name = order_splits[0]
    if name in commands:
        data = pd.read_csv('command_db.csv', index_col=0)
        command_info = data[data['NAME'] == name]
        command_info = command_info.to_dict()
        for key in command_info:
            index = None
            for i in command_info[key]:
                index = i
            command_info[key] = command_info[key][i]
        trade_df, position_df = handle_order(order, author, channel, td_account)
        if not type(trade_df) == pd.DataFrame:
            if trade_df == 400:
                return 400, '**Unable to find any strikes**\nMake sure to seperate strikes with ' + command_info['STRIKE_SEP']
            elif trade_df == 401:
                return 401, '**Invalid number of strikes**\nI was expecting ' + command_info['STRIKE_NUM'] + ' strikes'
            elif trade_df == 402:
                return 402, '**Expiration date not found**\nMake sure to indicate date with ' + command_info['DATE_SEP']
            elif trade_df == 399:
                return 399, '**Unable to find Stock Symbol ' + str(order_splits[1]) + '**'
        else:
            trade_sr = trade_df.iloc[0]
            positions = []
            for i in range(0, position_df.shape[0]):
                positions.append(position_df.iloc[i])
            sell_str = 'Selling the'
            buy_str = 'Buying the' 
            x = 0
            s = 0
            for position in positions:
                if position['short_trade']:
                    sell_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and'
                else:
                    buy_str += ' ' +str(position['strike']) + ' ' + str(position['side']).lower().replace('s', '') + ' and' 
            sell_str = ' '.join(sell_str.split(' ')[:-1])
            buy_str = ' '.join(buy_str.split(' ')[:-1])
            credit = ''
            if trade_sr['NET_PRICE'] > 0:
                credit = ' TOA Credit of '
            else:
                credit = ' TOA Debit of '
            price_str = ''
            if trade_sr['AVG_PRICE'] == None:
                price_str = credit + str(trade_sr['NET_PRICE'])
            else:
                price_str = credit + str(trade_sr['NET_PRICE']) + ' Avg Price ' + str(trade_sr['AVG_PRICE'])
            return 200, '**Success**\nOpened ' + trade_sr['TICKER'] + ' ' + name[0].upper()+name[1:] + ' ' + buy_str + ', ' + sell_str + ' for ' + trade_sr['DATE'] + price_str
    else:
        data = pd.read_csv('command_db.csv', index_col=0)
        command_info = data[data['NAME'] == 'standard']
        command_info = command_info.to_dict()
        for key in command_info:
            index = None
            for i in command_info[key]:
                index = i
            command_info[key] = command_info[key][i]
        trade_df, position_df = handle_single_order(order, author, channel, td_account)
        if not type(trade_df) == pd.DataFrame:
            if trade_df == 300:
                return 300, '**Unable to parse average price**'
            elif trade_df == 305:
                return 305, '**Option symbol not found**\nThis could be for a variety of reasons, the most common are invalid date or invalid strike.'
            elif trade_df == 400:
                return 400, '**Unable to find any strikes**'
            elif trade_df == 401:
                return 401, '**Invalid number of strikes**\nI was expecting ' + command_info['STRIKE_NUM'] + ' strikes'
            elif trade_df == 402:
                return 402, '**Expiration date not found**\nMake sure to indicate date with ' + command_info['DATE_SEP']
            elif trade_df == 399:
                return 399, '**Unable to find Stock Symbol ' + str(order_splits[0]) + '**'
            elif trade_df == 405:
                return 405, '**Unable to determine side**\nMake sure to specify calls or puts'
            elif trade_df == 406:
                return 406, '**Unable to find option data for specified option**\nThis could be for a variety of reasons but most likely is the date is incorrect'
        else:
            trade_sr = trade_df.iloc[0]
            position_sr = position_df.iloc[0]
            price_str = ''
            if trade_sr['AVG_PRICE'] == None:
                price_str = 'TOA ' + str(abs(trade_sr['NET_PRICE']))
            else:
                price_str = 'TOA ' + str(abs(trade_sr['NET_PRICE'])) + ' Avg Price ' + str(trade_sr['AVG_PRICE'])
            return 200, '**Success**\nOpened Ticker **' + trade_sr['TICKER'] + '** Strike **' + position_sr['strike'] + ' '  + position_sr['side'] + '** Date **' + position_sr['date'] + '** ' + price_str