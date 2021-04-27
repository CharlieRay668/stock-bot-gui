import discord
from discord.ext import commands
import requests
import json
import time

try:
    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot(command_prefix = '.', case_insensitive=True,  intents=intents)
except:
    client = commands.Bot(command_prefix = '.', case_insensitive=True)


UTOPIA = 679921845671035034
REQUEST = 679929147107180550

TEST_SERVER = 712778012302770944
PAPER = 736232441857048597
DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.cEmAhPCwe0y0vbqt-jpNF20GJ2E'
BOT_TOKEN = 'NzU0MDAyMzEwNTM5MTE2NTQ0.X1uZXw.lfvGKH-SJw54LEC0m-xUPxjsyIM'
CREDS = DEV_BOT_TOKEN

@client.event
async def on_ready():
    print("Website Bot is Ready")

async def check_activity():
    await client.wait_until_ready()
    server = client.get_guild(UTOPIA)
    channel = server.get_channel(REQUEST)
    print(channel)
    while client.is_closed:
        activity = requests.get(url='http://67.205.178.72/activity').json()['activity']
        print(activity)
        if len(activity) > 0:
            for action in activity:
                embedVar = discord.Embed(title="New Activity" , description='', color=0x00e6b8)
                embedVar.add_field(name='Ticker', value=action[0])
                embedVar.add_field(name='Quantity', value=action[1])
                embedVar.add_field(name='Fill Price', value=action[1])
                if action[3] == 1:
                    order_action = 'Buy'
                elif action[3] == 2:
                    order_action = 'Sell'
                else:
                    order_action = 'Unkown'
                embedVar.add_field(name='Action', value=order_action)
                await channel.send(embed = embedVar)
        time.sleep(5)


client.loop.create_task(check_activity())
client.run(CREDS)

# import pandas as pd
# from csv_manager import CSVHandler
# import datetime as dt
# from itertools import islice

# def get_history(individual_trades, name):
#     if name == 'SammySnipes' or name == 'MoneyMan' or name == 'Engine Trades' or name == 'Adam B':
#         return 300, 'No admins'
#     individual_trades = individual_trades[individual_trades['trader'] == name]
#     leaderboard = []
#     if len(individual_trades) > 1:
#         descriptions = []
#         for index, row in individual_trades.iterrows():
#             descriptions.append(row['description'])
#         descriptions = list(set(descriptions))
#         profit_descriptions = []
#         for description in descriptions:
#             curr_quantity = 0
#             exact_positions = individual_trades[individual_trades['description'] == description]
#             if len(exact_positions) > 1:
#                 prices = []
#                 all_prices = []
#                 qty = 0
#                 for index, row in exact_positions.iterrows():
#                     qty += row['quantity']
#                     # if abs(row['quantity']) == 100:
#                     #     row['quantity'] = row['quantity']/100
#                     if row['quantity'] > 0:
#                         prices.append(row['trade_price']*-1*abs(row['quantity']))
#                     elif row['quantity'] < 0:
#                         prices.append(row['trade_price']*abs(row['quantity']))
#                     if qty == 0:
#                         all_prices.append(prices)
#                         prices = []
#                 all_prices = [lst for lst in all_prices if lst != []]
#                 profits = []
#                 for prices in all_prices:
#                     received = 0
#                     spent = 0
#                     for price in prices:
#                         if price > 0:
#                             received += price
#                         elif price < 0:
#                             spent += price
#                     profit = ((abs(received)-abs(spent))/abs(spent))*100
#                     profit = round(profit, 2)
#                     profits.append(profit)
#                 profit_descriptions.append((profits, description))
#         if len(profit_descriptions) > 0:
#             return 200, profit_descriptions
#         else:
#             return 500, 'Description length < 1'
#     return 500, 'Length < 1'


# def in_depth(name, description):
#     positions_db = pd.read_csv('new_positions.csv', index_col=0)
#     positions_db['time'] = pd.to_datetime(positions_db['time'])
#     current_month = dt.datetime.now().replace(day=1)
#     mask = (positions_db['time'] > current_month) & (positions_db['time'] <= dt.datetime.now()) 
#     individual_trades = positions_db.loc[mask]
#     individual_trades = individual_trades[individual_trades['trader'] == name]
#     if len(individual_trades) < 1:
#         return 404, "Hmm, You dont seem to have any trades for this month."
#     individual_trades = individual_trades[individual_trades['description'] == description]
#     if len(individual_trades) < 1:
#         return 403, "Hmm, You dont seem to have any trades matching " + description + " for this month."
#     return 200, individual_trades

# def get_stats(name):
#     positions_db = pd.read_csv('new_positions.csv', index_col=0)
#     positions_db['time'] = pd.to_datetime(positions_db['time'])
#     current_month = dt.datetime.now().replace(day=1)
#     mask = (positions_db['time'] > current_month) & (positions_db['time'] <= dt.datetime.now()) 
#     individual_trades = positions_db.loc[mask]
#     individual_trades = individual_trades[individual_trades['trader'] == name]
#     if len(individual_trades) < 1:
#         return 500
#     else:
#         score = 0
#         wins = 0
#         losses = 0
#         status, profit_descriptions = get_history(individual_trades, name)
#         if status == 200:
#             for profits, description in profit_descriptions:
#                 for profit in profits:
#                     score += profit
#                     if profit > 0:
#                         wins += 1
#                     elif profit < 0:
#                         losses += 1
#         return score, wins, losses

# def calc_leaderboard(name):
#     member_names = [name]
#     leaderboard = []
#     positions_db = pd.read_csv('new_positions.csv', index_col=0)
#     positions_db['time'] = pd.to_datetime(positions_db['time'])
#     current_month = dt.datetime.now().replace(day=1)
#     mask = (positions_db['time'] > current_month) & (positions_db['time'] <= dt.datetime.now()) 
#     individual_trades = positions_db.loc[mask]
#     for name in member_names:
#         score = 0
#         status, profit_descriptions = get_history(individual_trades, name)
#         if status == 200:
#             for profits, description in profit_descriptions:
#                 for profit in profits:
#                     score += profit
#             leaderboard.append((score, name))
#     leaderboard.sort(reverse=True)
#     return leaderboard


# print(get_stats("Dick Branson"))
# print(calc_leaderboard("Dick Branson"))

# print(in_depth("Dick Branson", "SPCE Jan 8 2021 25 Call"))

# def get_history(individual_trades, name='Dick Branson'):
#     individual_trades = individual_trades[positions_db['trader'] == name]
#     leaderboard = []
#     if len(individual_trades) > 1:
#         descriptions = []
#         for index, row in individual_trades.iterrows():
#             descriptions.append(row['description'])
#         descriptions = list(set(descriptions))
#         profit_descriptions = []
#         for description in descriptions:
#             curr_quantity = 0
#             exact_positions = individual_trades[individual_trades['description'] == description]
#             if len(exact_positions) > 1:
#                 prices = []
#                 all_prices = []
#                 qty = 0
#                 for index, row in exact_positions.iterrows():
#                     qty += row['quantity']
#                     # if abs(row['quantity']) == 100:
#                     #     row['quantity'] = row['quantity']/100
#                     if row['quantity'] > 0:
#                         prices.append(row['trade_price']*-1*abs(row['quantity']))
#                     elif row['quantity'] < 0:
#                         prices.append(row['trade_price']*abs(row['quantity']))
#                     if qty == 0:
#                         all_prices.append(prices)
#                         prices = []
#                 all_prices = [lst for lst in all_prices if lst != []]
#                 profits = []
#                 for prices in all_prices:
#                     received = 0
#                     spent = 0
#                     for price in prices:
#                         if price > 0:
#                             received += price
#                         elif price < 0:
#                             spent += price
#                     profit = ((abs(received)-abs(spent))/abs(spent))*100
#                     profit = round(profit, 2)
#                     profits.append(profit)
#                 profit_descriptions.append((profits, description))
#     return profit_descriptions


# positions_db = pd.read_csv('new_positions.csv', index_col=0)
# positions_db['time'] = pd.to_datetime(positions_db['time'])
# current_month = dt.datetime.now().replace(day=1)
# mask = (positions_db['time'] > current_month) & (positions_db['time'] <= dt.datetime.now()) 
# individual_trades = positions_db.loc[mask]


# print(get_history(individual_trades))


# old = pd.read_csv('trades_db.csv')
# old_pos = pd.read_csv('positions_db.csv')
# positions = []
# for index, pos in old.iterrows():
#     oldies = old_pos[old_pos['id'] == pos['ID']]
#     if pos['COMMAND'] == 'standard':
#         # if len(oldies) < 2:
#         #     pass
#         if len(oldies) > 2:
#             print('error bot')
#             #print(oldies, pos['COMMAND'])
#         elif len(oldies) <= 2:
#             for index, pos in oldies.iterrows():
#                 trade_id = pos['id']
#                 ticker = pos['ticker']
#                 symbol = pos['symbol']
#                 if pos['closing']:
#                     quantity = -100
#                 else:
#                     quantity = 100
#                 asset_type = 'OPTION'
#                 date = pos['date']
#                 side = pos['side']
#                 if pos['closing']:
#                     trade_price = pos['bidPrice']
#                 else:
#                     trade_price = pos['askPrice']
#                 strike = pos['strike']
#                 bid_price = pos['bidPrice']
#                 ask_price = pos['askPrice']
#                 delta = pos['delta']
#                 theta = pos['theta']
#                 gamma = pos['gamma']
#                 vega = pos['volatility']
#                 description = pos['description'].replace('(Weekly)','').strip()
#                 author = pos['trader']
#                 channel = pos['channel']
#                 time = pos['time']
#                 if description == 'Expired' or description == 'Symbol not found':
#                     for index, item in enumerate(positions):
#                         if item[0] == trade_id:
#                             positions[index][4] = 0
#                 else:
#                     positions.append([trade_id, ticker, asset_type, symbol, quantity, date, side, trade_price, strike, bid_price, ask_price, delta, theta, gamma, vega, description, author, channel, time])
# columns = ['id', 'ticker', 'asset', 'symbol', 'quantity', 'date', 'side','trade_price', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'vega', 'description', 'trader', 'channel', 'time']
# # Create a new position dataframe with each row as a full position.
# position_df = pd.DataFrame(data=positions, columns=columns)
# # for index, pos in position_df.iterrows():
# #     news = position_df[position_df['id'] == pos['id']]
# #     if len(news) ==1:
# #         item = news.iloc[0]
# #         qty = item['quantity']
# #         if qty < 100:
# #             print(qty)
# #     elif len(news) > 2:
# #         print(news)
# position_csv_handler = CSVHandler('temp_positions.csv', 'id')
# position_csv_handler.add_rows(position_df)
    # #ID,TRADER,COMMAND,TICKER,POSITIONS,NET_PRICE,OPENING,DATE,AVG_PRICE,CLOSED,PROFIT
    # trade_id = pos['id']
    # if pos['COMMAND'] == 'standard':



# positions = []
# for index, pos in old.iterrows():
#     trade_id = pos['id']
#     ticker = pos['ticker']
#     symbol = pos['symbol']
#     if pos['closing']:
#         quantity = -100
#     else:
#         quantity = 100
#     asset_type = 'OPTION'
#     date = pos['date']
#     side = pos['side']
#     if pos['closing']:
#         trade_price = pos['bidPrice']
#     else:
#         trade_price = pos['askPrice']
#     strike = pos['strike']
#     bid_price = pos['bidPrice']
#     ask_price = pos['askPrice']
#     delta = pos['delta']
#     theta = pos['theta']
#     gamma = pos['gamma']
#     vega = pos['volatility']
#     description = pos['description'].replace('(Weekly)','').strip()
#     author = pos['trader']
#     channel = pos['channel']
#     time = pos['time']
#     if dt.datetime.strptime(pos['time'].split(' ')[0], '%Y-%m-%d').month == dt.datetime.now().month: 
#         if description == 'Expired' or description == 'Symbol not found':
#             for index, item in enumerate(positions):
#                 if item[0] == trade_id:
#                     positions[index][4] = 0
#         else:
#             positions.append([trade_id, ticker, asset_type, symbol, quantity, date, side, trade_price, strike, bid_price, ask_price, delta, theta, gamma, vega, description, author, channel, time])
# columns = ['id', 'ticker', 'asset', 'symbol', 'quantity', 'date', 'side','trade_price', 'strike', 'bidPrice', 'askPrice', 'delta', 'theta', 'gamma', 'vega', 'description', 'trader', 'channel', 'time']
# # Create a new position dataframe with each row as a full position.
# position_df = pd.DataFrame(data=positions, columns=columns)
# position_csv_handler = CSVHandler('temp_positions.csv', 'id')
# position_csv_handler.add_rows(position_df)
# print(old.columns, new.columns)
# from account_handler import AccountHandler

# data = ['Charlie678', ['Charlie678', 200200, 'CASH', 5000, 'octotoo']]
# index = data[0]
# row = data[1]
# ACCOUNT_HANDLER = AccountHandler()
# print(ACCOUNT_HANDLER.view_account(index))
# df = ACCOUNT_HANDLER.get_db()
# new_df = pd.DataFrame([[1,2,3,4]], columns = df.columns)
# df = df.append(new_df, ignore_index = True)
# df.to_csv('accounts_db.csv')


# import math
# from io import StringIO
# # df = pd.DataFrame(data=[[1,2,3,4,5,6,7]], columns=['ID', 'TRADER', 'COMMAND', 'TICKER', 'POSITIONS', 'NET_PRICE', 'OPENING'])
# # df.to_csv('trades_db.csv')
# data = pd.read_csv('trades_db.csv', index_col=0)
# #print(type(data['PROFIT'][-1 ]))
# for index, item in enumerate(data['PROFIT']):
#     if data['CLOSED'][index] and math.isnan(item):
#         print(index)
#         print(item)
# def position_df(positions):
#     return pd.read_csv(StringIO(positions), sep=';', index_col=0)
# def price_df(price):
#     return pd.read_csv(StringIO(price), sep='|', index_col=0)
# position = position_df(data.iloc[0]['POSITIONS'])
# price = price_df(position.iloc[0]['price'])
# print(position.head())
# print(price['askPrice'])




#from cStringIO import StringIO
# COLUMNS = ['SYMBOL', 'DIRECTION', 'THRESHOLD', 'PT', 'AUTHOR', 'UPLOADED']
# data = pd.DataFrame(data=[[1,2,3,4,5,6], [1,2,3,4,5,6]], columns=COLUMNS)
# #print(str(data.head()))
# fake_data = data.to_csv(index=False)
# cols = ['Fake1', 'csv', 'Fake2']
# data = pd.DataFrame(data=[[1,fake_data,3],[1,fake_data,3]], columns=cols)
# data.to_csv('fake_data.csv')
# data = pd.read_csv('fake_data.csv')
# print(type(data['csv'][0]))
# data = pd.read_csv(io.StringIO(data['csv'][0]))
# print(data.columns)

#.buy BIDU 137 calls 10/30 @1.25
# csv_path='command_db.csv'
# TRADE_COLUMNS = ['NAME', 'STRIKE_NUM', 'STRIKE_SEP', 'DIRECTIONAL', 'ORDER_STRUCT', 'DATE_SEP', 'AVERAGE_PRICE', 'AVERAGE_PRICE_SEP']
# POSITION_COLUMNS = ['Ticker', 'Date', 'Side', 'Strike', 'Price', 'Symbol', 'Closing_Trade', 'Short_Trade', 'Executed', 'Trader', 'Channel', 'Time', 'Active']
# new_df = pd.DataFrame(data=[['ironcondor',4,'-',False,['-1c', '+2c', '-1p', '+2p'],'/',False,None]], columns=TRADE_COLUMNS)

# #data = pd.read_csv(csv_path, index_col=0)
# #data = data.append(new_df, ignore_index = True)
# new_df.to_csv(csv_path)

# def parse_strikes(strike_str, order_struct, strike_split):
#     strikes = strike_str.split(strike_split)
#     calls = [(item[:-1], item[-1]) for item in strikes if 'C' in item]
#     puts = [(item[:-1], item[-1]) for item in strikes if 'P' in item]
#     call_struct = [(item[2:], item[0]) for item in order_struct if 'C' in item]
#     put_struct = [(item[2:], item[0]) for item in order_struct if 'P' in item]
#     call_struct.sort()
#     put_struct.sort()
#     calls.sort()
#     puts.sort()
#     call_struct = list(zip(calls, call_struct))
#     put_struct = list(zip(puts, put_struct))
#     buy_str = ''
#     sell_str = ''
#     for option, instruction in call_struct:
#         if instruction[1] == 'B':
#             buy_str += option[0] + ' Call strike'
#         else:
#             sell_str += option[0] + ' Call strike'
#     for option, instruction in put_struct:
#         if instruction[1] == 'B':
#             buy_str += option[0] + ' Put strike'
#         else:
#             sell_str += option[0] + ' Put strike'
#     return buy_str, sell_str

# parse_strikes('40C-45C-30P-25P', ['BC34', 'SC30', 'SP29', 'BP25'], '-')



# strike_str = new_df['STRIKE_SEP'].values[0].join([str(item) for item in list(range(40, 40+(5*new_df['STRIKE_NUM'].values[0]), 5))])
# directional_str = ''
# if new_df['DIRECTIONAL'].values[0]:
#     directional_str = ' calls'
# avg_price_str = ''
# if new_df['AVERAGE_PRICE'].values[0]:
#     avg_price_str = new_df['AVERAGE_PRICE_SEP']+'3.40'
# return_str = '.'+ new_df['NAME'] + ' TSLA' + directional_str + ' ' + strike_str + ' 10' + new_df['DATE_SEP'] + '29 ' + avg_price_str
# print(return_str.values[0])

# data = pd.read_csv('commands_db.csv')
# print(data)

# strike_str = data_base['STRIKE_SEP'].values[0].join([str(item) for item in list(range(40, 40+(5*data_base['STRIKE_NUM'].values[0]), 5))])
# print(data_base['STRIKE_SEP'].values[0])
# print(strike_str)
# data_base.to_csv('commands_db.csv')
# from TDAccount import Account
# from TDAccount import Position, Trade
# from DiscordListener import Listener
# import os
# from TDRestAPI import Rest_Account

# result, sammy = Account.load_account('accounts', 'SammySnipes')
# valid = 0
# print(result, sammy)
# x = 0
# remove_position = None
# for position in sammy.get_positions():
#     print(position.ticker)
#     if position.ticker =='APPL':
#         print(position)
#         remove_position = position
# sammy.positions.remove(remove_position)
# sammy.save_self('accounts')
# for trade in sammy.get_trades():
#     open_price = trade.opening_position.price[0]
#     close_price = trade.closing_position.price['mark'][0]
#     #print(open_price, close_price)
#     if not open_price == 0.0:
#         print((close_price/open_price)-1)
#         x += (close_price/open_price)-1
    #amt = 1000/(open_price*100)
    #print(amt)
    #print((amt*(close_price*100)) -1000)
    #x += amt*(close_price*100)
    #print(trade.opening_position.price[0] - trade.closing_position.price['mark'][0])

# from Watchlist import Watchlist, Watch
# import _thread as thread
# import time

# first_watch = Watch('TSLA', 'ABOVE', 500, 600)
# second_watch = Watch('AMD', 'ABOVE', 100, 120)
# watchlist = Watchlist('temporary')
# stream = watchlist.init_stream()
# #stream.run_forever()
# thread.start_new_thread(stream.run_forever, ())
# x = 0
# while True:
#     if x == 3:
#         watchlist.add_watch(first_watch)
#     if x == 4:
#         watchlist.add_watch(second_watch)
#     print('Whats up', x)
#     time.sleep(5)
#     x += 1
#     pass
# print("past watchlist")





# test_string ='1:50 PM AAPL Oct 23, 2020 $118.00 PUT $117.20 108 @ $1.92 $20.7 K SWEEP 22,744 12,606'
# splits = test_string.split()
# data = {   
#     'time': ' '.join(splits[0:2]),
#     "stock":(splits[2]),
#     "expiration":' '.join(splits[3:6]),
#     "strike":(splits[6]),
#     "contract":(splits[7]),
#     "referance":(splits[8]),
#     "details":' '.join(splits[9:12]),
#     "premium":' '.join(splits[12:14]),
#     "type":(splits[14]),
#     "volume":(splits[15]),
#     "OI":(splits[16])
# }
# print(data)
# from selenium import webdriver
# import time
# from selenium.webdriver.common.keys import Keys
# import random
# PASSWORD = 'r3I15XVm!C@b'
# USERNAME = 'charlieary'
# URL = 'https://quantdata.us/login'

# def login(password, username, url):
#     driver = webdriver.Chrome(executable_path=r'C:\Users\charl\Desktop\chromedriver\chromedriver.exe')
#     driver.get(url)
#     time.sleep(3)
#     driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div/div[2]/form/div[1]/div/input').send_keys(username)
#     time.sleep(2)
#     driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
#     time.sleep(2)
#     driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div/div[2]/form/div[4]/input').click()
#     time.sleep(4)
#     #option_table = driver.find_element_by_id('optionsTableBody')
#     return driver

# def get_option_table(driver):
#     return driver.find_element_by_id('optionsTableBody')


# driver = login(PASSWORD, USERNAME, URL)
# last_outputs = []
# while True:
#     outputs = get_option_table(driver).text.split('\n')
#     for output in outputs:
#         if output not in last_outputs:
#             print(output)
#     last_outputs = outputs
# from user_linsten import Listener as old_listen
# from DiscordListener import Listener as new_listen
# import os

# for fn in os.listdir('old_listeners'):
#     fn = fn.split('.')[0]
#     old = old_listen.load_listener('old_listeners', fn)
#     new = new_listen(old.username, old.listeners)
#     new.save_self('listeners')
#     print(new)

# from TDAccount import Trade, Position, Account
# from TDRestAPI import Rest_Account
# from TDExecutor import TDExecutor
# import datetime as dt
# #DIS_103020C133
# pos = Position(ticker='F', date='11/6', side='calls', strike=10.5, price=12, closing_trade = True, short_trade = False, executed = False, trader = 'Charlie678', channel='risky-trades', time=dt.datetime.now(), symbol='F_110620C10.5')
# rest_account = Rest_Account('keys.json')
# response = TDExecutor.close_position(pos, rest_account)
# print(response)
# TDExecutor.log_transaction(response)

# from multiprocessing import Pool

# async def f(x):
#     return x*x

# def callback():
#     print('calledback')

# if __name__ == '__main__':
#     print('nut')
#     pool = Pool(processes=1)              # Start a worker processes.
#     result = pool.apply_async(f, [10], callback)

# from TDAccount import Account
# from TDAccount import Position, Trade
# from DiscordListener import Listener
# import os
# from TDRestAPI import Rest_Account

# result, sammy = Account.load_account('accounts', 'SammySnipes')
# valid = 0
# print(result, sammy)
# for position in sammy.get_positions():
#     print(position, position.executed, position.symbol)
#     position.symbol = 'BAC_102320C25.5'
#     position.executed = True
#     if position.ticker == 'FSLY':
#         print(position, 'yes')
#         valid = position
# sammy.remove_position(valid)
# sammy.save_self('accounts')
# # # oldies = []
# for fn in os.listdir('old_accounts'):
#     fn = fn.split('.')[0]
#     oldies.append(old_account.load_account('old_accounts', fn)[1])

# print(oldies)
# newies = []
# for fn in os.listdir('accounts'):
#     fn = fn.split('.')[0]
#     if fn == 'MoneyMan':
#         money = new_account.load_account('accounts', fn)[1]
#         money.positions = []
#         money.save_self('accounts')
#     newies.append(new_account.load_account('accounts', fn)[1])

# print(newies)
# for act in newies:
#     for pos in act.positions:
#         print(pos)

# accounts = list(zip(oldies, newies))
# for old, new in accounts:
#     new_positions = []
#     new_trades = []
#     for pos in old.positions:
#         #print(pos)
#         new_positions.append(Position(pos.ticker, pos.date, pos.side, pos.strike, pos.price, 'OLD', pos.closing_trade, pos.short_trade, True, pos.trader, pos.channel, pos.time))
#     for trade in old.trades:
#         opening = trade.opening_position
#         closing = trade.closing_position
#         new_opening = Position(opening.ticker, opening.date, opening.side, opening.strike, opening.price, 'OLD', opening.closing_trade, opening.short_trade, True, opening.trader, opening.channel, opening.time)
#         new_closing = Position(closing.ticker, closing.date, closing.side, closing.strike, closing.price, 'OLD', closing.closing_trade, closing.short_trade, True, closing.trader, closing.channel, closing.time)
#         new_trade = Trade(new_opening, new_closing)
#         #print(new_trade)
#         new_trades.append(new_trade)
#     new.positions = new_positions
#     new.trades = new_trades
#     new.save_self('accounts')
#     #print(old, new)

# print(newies)