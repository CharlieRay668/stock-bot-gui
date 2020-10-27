import pandas as pd
COLUMNS = ['SYMBOL', 'DIRECTION', 'THRESHOLD', 'PT', 'AUTHOR', 'UPLOADED']
data = pd.DataFrame(data=[[1,2,3,4,5,6]], columns=COLUMNS)
print(type(str(data.head())))
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