"""A package containing the Account, Trade, and Position classes"""
import pickle
import os

class Account:
    """An Account is just a holder of a list of positions and trades"""
    def __init__(self, username, positions=[], trades=[]):
        self.username = username
        self.positions = positions
        self.trades = trades

    def __str__(self):
        return 'Account Holder: ' + self.username + '\nPositions: ' + str(self.positions) + '\nTrades: ' + str(self.trades)

    def get_username(self):
        return self.username
    def set_username(self, user):
        self.username = user
    def add_position(self, position):
        self.positions.append(position)
    def get_positions(self):
        return self.positions
    def get_trades(self):
        return self.trades
    def add_trade(self, trade):
        self.trades.append(trade)
    def remove_position(self, position):
        self.positions.remove(position)
    def remove_trade(self, trade):
        self.trades.remove(trade)   


    def save_self(self, directory):
        path = directory + '/' + self.username
        try:
            pickle.dump(self, open(path +'.act', 'wb'))
        except:
            os.mkdir(path.split('/')[0])
            pickle.dump(self, open(path +'.act', 'wb'))

    def view_feilds(self):
        return [self.username, self.positions, self.trades]

    @staticmethod
    def load_account(directory, username):
        path = directory + '/' + username + '.act'
        try:
            return 200, pickle.load(open(path, 'rb'))
        except Exception as e:
            return e, None

    @staticmethod
    def delete_account(directory, username):
        path = directory + '/' + username +'.act'
        os.remove(path)

    @staticmethod
    def get_accounts(directory):
        path = directory + '/'
        accounts = os.listdir(path)
        true_accounts = []
        for account in accounts:
            if '.act' in account:
                true_accounts.append(account)
        return true_accounts

class Trade():
    def __init__(self, opening_position, closing_position):
        self.opening_position = opening_position
        self.closing_position = closing_position

    def __str__(self):
        return str(self.opening_position) + '-' + str(self.closing_position)

    @staticmethod
    def load_position(directory, opening_position, closing_position):
        path = directory + '/'+ str(opening_position) + '-' + str(closing_position) + '.pos'
        try:
            return pickle.load(open(path, 'rb'))
        except:
            return '404: Error, Account not found.'

    def save_self(self, directory):
        path = directory + '/' + str(self)
        try:
            pickle.dump(self, open(path+'.pos', 'wb'))
        except:
            os.mkdir(path.split('/')[0])
            pickle.dump(self, open(path +'.pos', 'wb'))

class Position():
    def __init__(self, ticker, date, side, strike, price, symbol, closing_trade, short_trade, executed, trader, channel, time):
        self.ticker = ticker
        self.date = date
        self.side = side
        self.strike = strike
        self.price = price
        self.symbol = symbol
        self.closing_trade = closing_trade
        self.short_trade = short_trade
        self.executed = executed
        self.trader = trader
        self.channel = channel
        self.time = time

    def __str__(self):
        return str(self.ticker) + '_' + str(self.date) + '_' + str(self.trader) + '_' + self.time.strftime("%m/%d/%Y-%H:%M:%S")

    def human_string(self):
        return str(self.ticker) + ' ' + str(self.strike) + ' ' + str(self.side) + ' ' + str(self.date)

    @staticmethod
    def load_position(directory, ticker, date, trader):
        path = directory + '/'+ str(ticker) + '_' + str(date) + '_' + str(trader) + '.pos'
        try:
            return pickle.load(open(path, 'rb'))
        except:
            return '404: Error, Account not found.'

    def save_self(self, directory):
        path = directory + '/' + str(self)
        try:
            pickle.dump(self, open(path+'.pos', 'wb'))
        except:
            os.mkdir(path.split('/')[0])
            pickle.dump(self, open(path +'.pos', 'wb'))

    def get_symbol(self):
        return self.symbol

    def get_short(self):
        return self.short_trade

    def get_executed(self):
        return self.executed

    def get_ticker(self):
        return self.ticker

    def set_ticker(self, ticker):
        self.ticker = ticker

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time

    def get_side(self):
        return self.side

    def set_side(self, side):
        self.side = side

    def get_strike(self):
        return self.strike

    def set_strike(self, strike):
        self.strike = strike

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def copy(self, ticker=None, date=None, side=None, strike=None, price=None, symbol=None, closing_trade=None, short_trade=None, executed=None, trader=None, channel=None, time=None):
        if ticker == None:
            ticker = self.ticker
        if date == None:
            date = self.date
        if side == None:
            side = self.side
        if strike == None:
            strike = self.strike
        if price == None:
            price = self.price
        if symbol == None:
            symbol = self.symbol
        if closing_trade == None:
            closing_trade = self.closing_trade
        if short_trade == None:
            short_trade = self.short_trade
        if executed == None:
            executed = self.executed
        if trader == None:
            trader = self.trader
        if channel == None:
            channel = self.channel
        if time == None:
            time = self.time
        return Position(ticker, date, side, strike, price, symbol, closing_trade, short_trade, executed, trader, channel, time)
