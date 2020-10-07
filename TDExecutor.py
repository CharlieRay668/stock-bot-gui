from TDAccount import Trade, Position, Account
from TDRestAPI import Rest_Account
import datetime
import matplotlib.pyplot as plt

class TDExecutor():

    @staticmethod
    def choose_best(td_account, position):
        surroundings = TDExecutor.get_surrounding(td_account, position)
        print(surroundings)
        min_symbol, min_spread = TDExecutor.find_min_spread(surroundings)
        new_position = position.copy(strike=TDExecutor.get_strike_from_symbol(min_symbol), symbol=min_symbol)
        print(new_position, 'NEW POSITION', position, new_position.symbol, position.symbol.upper())
        new_surroundings = TDExecutor.get_surrounding(td_account, new_position, above_below=1)
        print(new_surroundings, 'NEW SURROUNDINGS')
        if not (new_surroundings[0]['ask'] < new_surroundings[1]['ask'] and new_surroundings[2]['ask'] < new_surroundings[1]['ask']):
            return new_position, min_symbol, min_spread
        elif not (surroundings[0]['ask'] < surroundings[1]['ask'] and surroundings[2]['ask'] < surroundings[1]['ask']):
            return position, position.symbol, (surroundings[1]['ask']-surroundings[1]['bid'])/surroundings[1]['ask']
        else:
            return 404, 'Not able to find fairly priced symbol'

    @staticmethod
    def get_strike_from_symbol(symbol):
        data = symbol.split('_')[1]
        if 'C' in data:
            return float(data.split('C')[1])
        return float(data.split('P')[1])
    
    @staticmethod
    def get_symbol_from_position(td_account, position):
        strike = float(position.strike)
        date = position.date
        ticker = position.ticker
        side = position.side
        if strike.is_integer():
            strike = int(strike)
        return td_account.get_option_symbol(ticker, strike, '20', date.split('/')[0], date.split('/')[1], side)

    @staticmethod
    def find_min_spread(options):
        spreads = []
        for row in options:
            bid = row['bid']*100
            ask = row['ask']*100
            spread = (ask-bid)/ask
            spreads.append((row.name, spread))
        return min(spreads, key = lambda i : i[1])


    @staticmethod
    def get_surrounding(td_account, position, strike_count=10, above_below=4):
        date = position.date
        side = position.side
        date_string = '2020-'+date.split('/')[0]+'-'+date.split('/')[1]
        #print(position)
        symbol = TDExecutor.get_symbol_from_position(td_account, position)
        #print(symbol)
        delta = datetime.timedelta(weeks=2)
        date_time = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        from_date = datetime.datetime.strftime(date_time-delta, '%Y-%m-%d')
        to_date = datetime.datetime.strftime(date_time+delta, '%Y-%m-%d')
        chain = td_account.get_options_chain(position.ticker.upper(), strike_count=strike_count, from_date=from_date, to_date=to_date, contract_type=side.replace('S', ''))
        print(chain)
        for epoch_time in chain['expirationDate']:
            time = int(epoch_time)
            time = datetime.datetime.fromtimestamp(time/1000).strftime('%m/%d/%Y')
            if datetime.datetime.strftime(date_time, '%m/%d/%Y') == time:
                expiration_time = epoch_time
                break
        symbols = [index for (index, item) in chain['expirationDate'].iteritems() if item == expiration_time]
        print(symbols)
        for index, item in enumerate(symbols):
            print(item, symbol)
            if item == symbol:
                print(item, symbol)
                if index-(above_below+1) < 0 or index+(above_below+1) > len(symbols):
                    return TDExecutor.get_surrounding(td_account, position, strike_count+10, above_below=above_below)
                return [chain.loc[symbols[special_index]] for special_index in range(index-above_below, index+(above_below+1))]

    @staticmethod
    def order_proper(position, td_account, dollar_cost):
        available_cash = td_account.get_account_cash()
        ticker = position.ticker
        position, option, spread = TDExecutor.choose_best(td_account, position)
        print(available_cash)
        if  available_cash > dollar_cost:
            quote = td_account.get_quotes(option)
            mark = quote['mark']*100
            ask = quote['askPrice']*100
            cost_per_option = int((mark+ask)/2)
            print(cost_per_option, mark, ask, spread)
            option_amt = int(dollar_cost/cost_per_option)
            if option_amt >= 1:
                if spread < 0.15:
                    try:
                        response = td_account.place_order_limit(option, option_amt, (cost_per_option/100), 'BUY')
                        return (position, option, option_amt, ticker, dollar_cost, " Sucess, Option ordered", response)
                    except Exception as e:
                        print('Unexpected ordering error', e)
                        return(position, option, option_amt, ticker, 0, ' TotalFailure INVALID ORDER ' + str(e), None)
                else:
                    return(position, option, option_amt, ticker, 0, ' TotalFailure Spread too wide', None)
            else:
                return (position, option, 0, ticker, 0, " TotalFailure Option too expensive", None)
        else:
            return (position, option, 0, ticker, 0, " TotalFailure NOT ENOUGH CASH", None)


    @staticmethod
    def close_position(position, td_account):
        print(position)
        symbol = position.symbol
        positions = td_account.get_positions()
        if symbol in positions.keys():
            return (200, 'Success closed position', td_account.sell_to_close(symbol, positions[symbol]))
        else:
            return (404, 'Unable to find position in holdings', None)

    @staticmethod
    def log_transaction(message):
        with open('logs.txt', 'a+') as fw:
            fw.write(str(message) + '\n')

    @staticmethod
    def execute(account_name, directory, opening):
        response, account = Account.load_account(directory, account_name)
        if response == 200:
            for pos in account.get_positions():
                print(pos)
                if not pos.get_executed():
                        if not pos.short_trade:
                            pos.executed = True
                            rest_account = Rest_Account('keys.json')
                            response = None
                            if opening:
                                response = TDExecutor.order_proper(pos, rest_account, 1000)
                            else:
                                response = TDExecutor.close_position(pos, rest_account)
                            print(response)
                            TDExecutor.log_transaction(response)
            account.save_self('accounts')





#td_account = Rest_Account('keys.json')
#print(td_account.get_positions())
# result, money_man = Account.load_account('accounts', 'MoneyMan')
# for pos in money_man.get_positions():
#     strike = pos.strike
#     position = pos
# print(position)
# surroundings = TDExecutor.get_surrounding(td_account, position, above_below=10)
#print(find_min_spread(td_account, surroundings))

#print(TDExecutor.get_surrounding(td_account, position))