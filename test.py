# from user_linsten import Listener as old_listen
# from DiscordListener import Listener as new_listen
# import os

# for fn in os.listdir('old_listeners'):
#     fn = fn.split('.')[0]
#     old = old_listen.load_listener('old_listeners', fn)
#     new = new_listen(old.username, old.listeners)
#     new.save_self('listeners')
#     print(new)

# from account import Account as old_account
from TDAccount import Account
from TDAccount import Position, Trade
# import os


result, sammy = Account.load_account('accounts', 'SammySnipes')
valid = 0
for position in sammy.get_positions():
    print(position)
    if position.ticker == 'AMD':
        print(position, 'yes')
        valid = position
sammy.remove_position(valid)
sammy.save_self('accounts')
# oldies = []
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