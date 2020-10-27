import discord
from discord.ext import commands
from DiscordListener import Listener
from TDAccount import Account, Trade, Position
from os import path
import os
import datetime as dt
from TDRestAPI import Rest_Account
from TDExecutor import TDExecutor

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', case_insensitive=True, intents=intents)

DIRECTORY = 'listeners'

TEST_SERVER = 768531740527689779
UTOPIA = TEST_SERVER
PAPER = 768531889911889950
DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.vKvoV8Gz9jBWDWvIaBGDC4xbLB4'
BOT_TOKEN = 'NzY3MTEzNTA2NDU3MjU2MDA4.X4tMIA.aC_J8Q0maMWVeYM6QtdCMEXN-ko'
CREDS = BOT_TOKEN

TD_ACCOUNT = Rest_Account('keys.json')


def between(upper, lower, location):
    if upper == None or lower == None:
        return False
    return location < upper and location > lower

def check_float(string):
    try:
        float(string)
        return True
    except:
        return False
    
def check_unstable(ctx):
    test_server = client.get_guild(TEST_SERVER)
    paper =  test_server.get_channel(PAPER)
    return ctx.channel == paper

def check_user_perms(ctx):
    #return ctx.channel == request or check_admin_perms(ctx)
    return check_unstable(ctx)

def check_admin_perms(ctx):
    #return ctx.channel == channel_test or ctx.channel == channel_money or ctx.channel == channel_engine or ctx.channel == channel_sammy or ctx.channel == channel_admin_test or ctx.channel == channel_adam or ctx.channel == channel_risky or ctx.channel == channel_swing
    return check_unstable(ctx)

def broadcast(ctx, server_main):
    target_members = None
    for fn in os.listdir('listeners'):
        target = fn.split('.')[0]
        if target == ctx.author.name:
            listener = Listener.load_listener(DIRECTORY, target)
            target_members = listener.get_listeners()
    true_target = []
    if target_members is not None:
        for member in server_main.members:
            if member.name in target_members:
                true_target.append(member)
    return true_target

def parse_initial_order(order, spread = False):
    order = order.replace('$', '')
    order = order.replace('*', '')
    splits = order.split(' ')
    date = None
    strike = None
    ticker = splits[0]
    side = None
    ref_price = None
    extra_info = None
    start = None
    end = None
    if '(' in order and ')' in order:
        start = order.find('(')
        end = order.find(')')
        extra_info = order[start+1:end]
    for item in splits:
        if not between(start, end, order.find(item)):
            if not spread:
                if '/' in item and check_float(item.replace('/', '')):
                    date = item
                elif '@' in item and check_float(item.replace('@', '')):
                    ref_price = item
                elif check_float(item):
                    strike = item
                else:
                    if item.lower() =='call' or item.lower() == 'c' or item.lower() == 'calls':
                        side = 'CALLS'
                    elif item.lower() =='put' or item.lower() == 'p' or item.lower() == 'puts':
                        side = 'PUTS'
            else:
                if '/' in item and check_float(item.replace('/', '')):
                    date = item
                elif '@' in item and check_float(item.replace('@', '')):
                    ref_price = item
                elif '-' in item and check_float(item.replace('-', '')):
                    strike = item
                else:
                    if item.lower() =='call' or item.lower() == 'c' or item.lower() == 'calls':
                        side = 'CALLS'
                    elif item.lower() =='put' or item.lower() == 'p' or item.lower() == 'puts':
                        side = 'PUTS'
    return (date, strike, ticker, side, ref_price, extra_info)

def parse_error_order(order, date, strike, ticker, side, ref_price, spread = False):
    order = order.replace('$', '')
    splits = order.split(' ')
    for item in splits:
        if date is None:
            if '/' in item and check_float(item.replace('/', '')):
                date = item
        if strike is None:
            if not spread:
                if check_float(item):
                    strike = item
            else:
                if '-' in item and check_float(item.replace('-', '')):
                    strike = item
        if ref_price is None:
            if '@' in item and check_float(item.replace('@', '')):
                ref_price = item
        if side is None:
            if item.lower() =='call' or item.lower() == 'c' or item.lower() == 'calls':
                side = 'CALLS'
            elif item.lower() =='put' or item.lower() == 'p' or item.lower() == 'puts':
                side = 'PUTS'
        if ticker is None and date is not None and strike is not None and ref_price is not None and side is not None:
            ticker = item
    return (date, strike, ticker, side, ref_price)

@client.command()
async def init(ctx, *, params):
    if params.split(' ')[0] == 'account':
        if len(params.split(' ')) < 2:
            account = Account(ctx.author.name)
            account.save_self('accounts')
            await ctx.channel.send('Initialized account for user: ' + ctx.author.name)
        else:
            if '(' in params and ')' in params:
                start = params.find('(')
                end = params.find(')')
                acct_name = params[start+1:end]
            else:
                acct_name = params.split(' ')[1]
            account = Account(acct_name)
            account.save_self('accounts')
            await ctx.channel.send('Initialized account for user: ' + acct_name)
    # if params.split(' ')[0] == 'alert':
    #     alert_string = ' '.join(params.split[' '][1:])


@client.command()
async def adminhelp(ctx):
    if check_user_perms(ctx):
        embedVar = discord.Embed(title="Utopia Notification Admin", description='', color=0xb3b300)
        embedVar.add_field(name="Buy Alert ", value='.buy (Stock Symbol) (MM/DD) (Strike) (Avg Price @3.00) (Puts/Calls)', inline=False)
        embedVar.add_field(name="Sell Alert", value='.sell (Stock Symbol) (MM/DD) (Strike) (Avg Price @3.00) (Puts/Calls)', inline=False)
        embedVar.add_field(name="Open Spread Alert", value='.creditspread open/close (Stock Symbol) (MM/DD) (Strikes) (Avg Price @3.00) (Puts/Calls)')
        embedVar.add_field(name="Close Spread Alert", value='.debitspread open/close (Stock Symbol) (MM/DD) (Strikes) (Avg Price @3.00) (Puts/Calls)', inline=False)
        embedVar.add_field(name="Other Command Keywords", value='.commandaliases', inline=False)
        embedVar.add_field(name="Additional Info", value="The order of the alert information doesn't matter other than the stock symbol must come where indicated. Date must have a /, Average price must have an @.", inline=False)
        await ctx.channel.send(embed=embedVar)

@client.command()
async def commandaliases(ctx):
    if check_user_perms(ctx):
        embedVar = discord.Embed(title="Notification Command Aliases", description='', color=0xb3b300)
        embedVar.add_field(name="Buy Aliases ", value='in, bought, grabbed, grabbing, buying, bto', inline=False)
        embedVar.add_field(name="Sell Aliases", value='cut, sold, cutting, selling, stc, closing', inline=False)
        embedVar.add_field(name="Additional Info", value='Use any of these aliases in place of a .buy or .sell command, functunally the same', inline=False)
        await ctx.channel.send(embed=embedVar)

@client.event
async def on_ready():
    print("Dummy Bot is Ready")


# @client.event   
# async def on_message_edit(before, ctx):
#     if check_admin_perms(ctx):
#         splits = ctx.content.split(' ')
#         commands = {'creditspread':creditspread, 'debitspread':debitspread, 'buy':buy, 'sell':sell, 'in':buy, "bought":buy, "grabbed":buy, 'grabbing':buy, 'buying':buy, 'bto':buy, 'cut':sell, "sold":sell, "cutting":sell, 'selling':sell, 'stc':sell, 'closing':sell}
#         if splits[0][0] == '.':
#             for command in commands.keys():
#                 if splits[0][1:] == command:
#                     await commands[command](ctx, order = ' '.join(splits[1:]))
#                     #await ctx.invoke(get_command('buy'))


@client.command()
async def adjustment(ctx, *, adjustment):
    main_server = client.get_guild(UTOPIA)
    if check_admin_perms(ctx):
        for member in broadcast(ctx, main_server):
            try:
                await member.send('Adjustment alert From **' + ctx.author.name + '**: ' + adjustment)
            except:
                print('Faile on ' + member.name)

@client.command()
async def notifiactionhelp(ctx):
    if check_user_perms(ctx):
        embedVar = discord.Embed(title="Utopia Notification Commands", description='', color=0xb3b300)
        embedVar.add_field(name="Listen to Admin", value='.listen (admin name)', inline=False)
        embedVar.add_field(name="Opt out of notifications", value='.unlisten (admin name)', inline=False)
        embedVar.add_field(name="Available Admin Names", value='MoneyMan, SammySnipes, Engine Trades, Adam B', inline=False)
        embedVar.add_field(name="Additional Info", value='If you change your name you will need to re listen to the admins. The bot saves connections between users and when a name is changed it looses the connection', inline=False)
        await ctx.channel.send(embed=embedVar)

@client.command()
async def notificationhelp(ctx):
    if check_user_perms(ctx):
        embedVar = discord.Embed(title="Utopia Notification Commands", description='', color=0xb3b300)
        embedVar.add_field(name="Listen to Admin", value='.listen (admin name)', inline=False)
        embedVar.add_field(name="Opt out of notifications", value='.unlisten (admin name)', inline=False)
        embedVar.add_field(name="View who you are listening to", value='.checklisten', inline=False)
        embedVar.add_field(name="Available Admin Names", value='MoneyMan, SammySnipes, Engine Trades, Adam B', inline=False)
        embedVar.add_field(name="Additional Info", value='If you change your name you will need to re listen to the admins. The bot saves connections between users and when a name is changed it looses the connection', inline=False)
        await ctx.channel.send(embed=embedVar)

@client.command()
async def check(ctx, *, params):
    if params.split(' ')[0] == 'status':
        if len(params.split(' ')) < 2:
            await ctx.channel.send('Please enter a user to check position status')
        else:
            if '(' in params and ')' in params:
                start = params.find('(')
                end = params.find(')')
                acct_name = params[start+1:end]
            else:
                acct_name = params.split(' ')[1]
            status, account = Account.load_account('accounts', acct_name)
            if status == 200:
                embedVar = discord.Embed(title=acct_name+"'s current public positions", description='These may not be fully accurate due to inconsitency in closing of positions. If you dont see a open position you can take that as fact though.', color=0xb3b300)
                for pos in account.get_positions():
                    embedVar.add_field(name=pos.ticker, value=pos.strike + ' ' + pos.date + ' ' + pos.side, inline=False)
                await ctx.channel.send(embed=embedVar)
            else:
                embedVar = discord.Embed(title="Sorry", description='Unable to find user: ' + str(acct_name), color=0xD62121)
                await ctx.channel.send(embed=embedVar)
    elif params.split(' ')[0] == 'listen':
        if len(params.split(' ')) < 2:
            author_name = ctx.author.name
        else:
            if '(' in params and ')' in params:
                start = params.find('(')
                end = params.find(')')
                author_name = params[start+1:end]
            else:
                author_name = params.split(' ')[1]
        persons = []
        for fn in os.listdir('listeners'):
            file_name = fn.split('.')[0]
            if author_name in Listener.load_listener('listeners', file_name).get_listeners():
                persons.append(file_name)
        embedVar = discord.Embed(title="User " + author_name + ' Is following' , description= ', '.join(persons), color=0x00e6b8)
        await ctx.channel.send(embed=embedVar)
    else:
        await ctx.channel.send('Unkown check command')

@client.command()
async def checklisten(ctx):
    if check_user_perms(ctx):
        persons = []
        for fn in os.listdir('listeners'):
            file_name = fn.split('.')[0]
            if ctx.author.name in Listener.load_listener('listeners', file_name).get_listeners():
                persons.append(file_name)
        embedVar = discord.Embed(title="User " + ctx.author.name + ' Is following' , description= ', '.join(persons), color=0x00e6b8)
        await ctx.channel.send(embed=embedVar)

@client.command()
async def unlisten(ctx, * user):
    main_server = client.get_guild(UTOPIA)
    found_user = False
    if check_user_perms(ctx):
        for member in main_server.members:
            if member.name == user[0] or member.nick == user[0]:
                found_user = True
                if path.exists(DIRECTORY +'/' + member.name + '.lstn'):
                    listener = Listener.load_listener(DIRECTORY, member.name)
                    listener.remove_listener(ctx.author.name)
                    embedVar = discord.Embed(title="User " + ctx.author.name + " is no longer listening To: ", description=str(user[0]), color=0x00e6b8)
                    await ctx.channel.send(embed=embedVar)
                else:
                    embedVar = discord.Embed(title="User" + ctx.author.name + " is no longer listening To: ", description=str(user[0]) + '. You also were never listening to them in the first place', color=0x00e6b8)
                    await ctx.channel.send(embed=embedVar)
        if not found_user:
            embedVar = discord.Embed(title="Sorry", description='Unable to find user: ' + str(user), color=0xD62121)
            await ctx.channel.send(embed=embedVar)

@client.command()
async def checkperms(ctx):
    if check_user_perms(ctx):
        try:
            await ctx.author.send('You seem to have permissions turned on. Good Job!')
            embedVar = discord.Embed(title="All good", description="You have DM perms turned on", color=0x00e6b8)
            await ctx.channel.send(embed=embedVar)
        except:
            embedVar = discord.Embed(title="Sorry", description="You don't seem to have DM permissions turned on. I can't DM you without them.\nServer -> Privacy Settings -> Allow DM", color=0x00e6b8)
            await ctx.channel.send(embed=embedVar)

@client.command()
async def listen(ctx, *, user):
    main_server = ctx.guild
    found_user = False
    if check_user_perms(ctx):
        for member in main_server.members:
            print(main_server.members)
            if member.name == user or member.nick == user:
                found_user = True
                if path.exists(DIRECTORY +'/' + member.name + '.lstn'):
                    listener = Listener.load_listener(DIRECTORY, member.name)
                    listener.add_listener(ctx.author.name)
                    try:
                        await ctx.author.send('Got it, You are now listening to **' + str(user) +'** ')
                    except:
                        embedVar = discord.Embed(title="Sorry", description="You don't seem to have DM permissions turned on. I can't DM you without them.\nServer -> Privacy Settings -> Allow DM", color=0xD62121)
                        await ctx.channel.send(embed=embedVar)
                    embedVar = discord.Embed(title="User " + ctx.author.name + " is now listening To: ", description=str(user), color=0x00e6b8)
                    await ctx.channel.send(embed=embedVar)
                else:
                    listener = Listener(member.name, [ctx.author.name])
                    try:
                        await ctx.author.send('Got it, You are now listening to **' + str(user) +'** ')
                    except:
                        embedVar = discord.Embed(title="Sorry", description="You don't seem to have DM permissions turned on. I can't DM you without them.\nServer -> Privacy Settings -> Allow DM", color=0xD62121)
                        await ctx.channel.send(embed=embedVar)
                    embedVar = discord.Embed(title="User " + ctx.author.name + " is now listening To: ", description=str(user), color=0x00e6b8)
                    await ctx.channel.send(embed=embedVar)
        if not found_user:
            embedVar = discord.Embed(title="Sorry", description='Unable to find user: ' + str(user), color=0xD62121)
            await ctx.channel.send(embed=embedVar)

@client.command()
async def creditspread(ctx, *, order):
    server_main = client.get_guild(UTOPIA)
    open_close = order.split(' ')[0]
    order = ' '.join(order.split(' ')[1:])
    if check_admin_perms(ctx):
        date, strike, ticker, side, ref_price, extra_info = parse_initial_order(order, spread=True)
        while (date is None or strike is None or ticker is None or side is None or ref_price is None):
            await ctx.channel.send('Error: Missing Data.\nCurrent Data = **Ticker** ' + str(ticker) +' **Strikes** ' + str(strike) + ' **Date** ' + str(date) + ' **Side** ' + str(side) + ' **Avg Price** ' + str(ref_price))
            await ctx.channel.send('Please respond to this message with the missing data (indicated by None) within the next 30 secconds to update the message')
            def check(author):
                def inner_check(message): 
                    if message.author != author:
                        return False
                    else:
                        return True
                return inner_check
            msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
            date, strike, ticker, side, ref_price = parse_error_order(msg.content, date, strike, ticker, side, ref_price)
        
        base_string = ticker + ' ' + date + ' ' + side + ' ' + str(ref_price)
        legs = ''
        strike1 = strike.split('-')[0]
        strike2 = strike.split('-')[1]
        if not open_close.upper() == 'CLOSE':
            if side == 'CALLS':
                if strike1 > strike2:
                    legs = ' **Selling** the ' + strike2 + ' strike and **Buying** the ' + strike1 + ' strike'
                else:
                    legs = ' **Selling** the ' + strike1 + ' strike and **Buying** the ' + strike2 + ' strike'
            else:
                if strike1 < strike2:
                    legs = ' **Selling** the ' + strike2 + ' strike and **Buying** the ' + strike1 + ' strike'
                else:
                    legs = ' **Selling** the ' + strike1 + ' strike and **Buying** the ' + strike2 + ' strike'
        else:
            if side == 'CALLS':
                if strike1 > strike2:
                    legs = ' **Buying Back** the ' + strike2 + ' strike and **Selling** the ' + strike1 + ' strike'
                else:
                    legs = ' **Buying Back** the ' + strike1 + ' strike and **Selling** the ' + strike2 + ' strike'
            else:
                if strike1 < strike2:
                    legs = ' **Buying Back** the ' + strike2 + ' strike and **Selling** the ' + strike1 + ' strike'
                else:
                    legs = ' **Buying Back** the ' + strike1 + ' strike and **Selling** the ' + strike2 + ' strike'
        if extra_info is not None:
            legs += ' **Additional Message** ' + extra_info
        for member in broadcast(ctx, server_main):
            try:
                await member.send(ctx.author.name + ' Is '+ open_close +'ing a credit spread for  ' + base_string + legs)
            except:
                print('Faile on ' + member.name)
     
        embedVar = discord.Embed(title=open_close[0].upper() + open_close[1:] + ' credit spread', description=base_string + legs, color=0x0033cc)
        embedVar.add_field(name="Sender:", value=ctx.author.name, inline=False)
        await ctx.channel.send(embed=embedVar)

@client.command()
async def debitspread(ctx, *, order):
    server_main = client.get_guild(UTOPIA)
    open_close = order.split(' ')[0]
    order = ' '.join(order.split(' ')[1:])
    if check_admin_perms(ctx):
        date, strike, ticker, side, ref_price, extra_info = parse_initial_order(order, spread=True)
        while (date is None or strike is None or ticker is None or side is None or ref_price is None):
            await ctx.channel.send('Error: Missing Data.\nCurrent Data = **Ticker** ' + str(ticker) +' **Strikes** ' + str(strike) + ' **Date** ' + str(date) + ' **Side** ' + str(side) + ' **Avg Price** ' + str(ref_price))
            await ctx.channel.send('Please respond to this message with the missing data (indicated by None) within the next 30 secconds to update the message')
            def check(author):
                def inner_check(message): 
                    if message.author != author:
                        return False
                    else:
                        return True
                return inner_check
            msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
            date, strike, ticker, side, ref_price = parse_error_order(msg.content, date, strike, ticker, side, ref_price)
        
        base_string = ticker + ' ' + date + ' ' + side + ' ' + str(ref_price)
        legs = ''
        strike1 = strike.split('-')[0]
        strike2 = strike.split('-')[1]
        if not open_close.upper() == 'CLOSE':
            if side == 'CALLS':
                if strike1 < strike2:
                    legs = ' **Selling** the ' + strike2 + ' strike and **Buying** the ' + strike1 + ' strike'
                else:
                    legs = ' **Selling** the ' + strike1 + ' strike and **Buying** the ' + strike2 + ' strike'
            else:
                if strike1 > strike2:
                    legs = ' **Selling** the ' + strike2 + ' strike and **Buying** the ' + strike1 + ' strike'
                else:
                    legs = ' **Selling** the ' + strike1 + ' strike and **Buying** the ' + strike2 + ' strike'
        else:
            if side == 'CALLS':
                if strike1 < strike2:
                    legs = ' **Buying Back** the ' + strike2 + ' strike and **Selling** the ' + strike1 + ' strike'
                else:
                    legs = ' **Buying Back** the ' + strike1 + ' strike and **Selling** the ' + strike2 + ' strike'
            else:
                if strike1 > strike2:
                    legs = ' **Buying Back** the ' + strike2 + ' strike and **Selling** the ' + strike1 + ' strike'
                else:
                    legs = ' **Buying Back** the ' + strike1 + ' strike and **Selling** the ' + strike2 + ' strike'
        if extra_info is not None:
            legs += ' **Additional Message** ' + extra_info       
        for member in broadcast(ctx, server_main):
            try:
                await member.send(ctx.author.name + ' Is '+ open_close +'ing a debit spread for  ' + base_string + legs)
            except:
                print('Faile on ' + member.name)
        await ctx.channel.send('** Success**\n' + open_close[0].upper() + open_close[1:] + ' debit spread' + base_string + legs)


@client.command(aliases=['in', "bought", "grabbed", 'grabbing', 'buying', 'bto', 'btc','swing', 'swinging'])
async def buy(ctx, *, order):
    order = order.replace('*', '')
    print(order)
    server_main = client.get_guild(UTOPIA)
    if check_admin_perms(ctx):
        print('perms')
        if len(order.split(' ')) < 3:
            response, account = Account.load_account('accounts', ctx.author.name)
            if response == 200:
                removals = []
                for position in account.get_positions():
                    ticker = position.get_ticker().upper()
                    if ticker == order.split(' ')[0].upper():
                        strike = position.get_strike()
                        date = position.get_date()
                        side = position.get_side()
                        price = TD_ACCOUNT.get_quotes(TD_ACCOUNT.get_option_symbol(ticker, strike, '20', date.split('/')[0], date.split('/')[1], side))
                        position_2 = position.copy(closing_trade=True, time=dt.datetime.now(), ref_price=price, executed=False)
                        account.add_trade(Trade(position, position_2))
                        account.add_position(position_2)
                        account.save_self('accounts')
                        try:
                            pass
                            #TDExecutor.execute(account.get_username(), 'accounts', opening=False)
                        except Exception as e:
                            TDExecutor.log_transaction(str(e))
                        account.remove_position(position_2)
                        account.save_self('accounts')
                        await ctx.channel.send('**Success**\nClosed Position: **' + position_2.human_string() + '**')
                        for member in broadcast(ctx, server_main):
                            try:
                                await member.send(ctx.author.name + ' Is now Closing **' + position_2.human_string() + '**')
                            except:
                                print('Faile on ' + member.name)
                        removals.append(position)
                for pos in removals:
                    account.remove_position(pos)
                    account.save_self('accounts')
            else:
                await ctx.author.send("You tried to close a position without first inizializing an account, alert tracking is not available without an account.")
        else:
            date, strike, ticker, side, ref_price, extra_info = parse_initial_order(order)
            while (date is None or strike is None or ticker is None or side is None or ref_price is None):
                await ctx.channel.send('Error: Missing Data.\nCurrent Data = **Ticker** ' + str(ticker) +' **Strike** ' + str(strike) + ' **Date** ' + str(date) + ' **Side** ' + str(side) + ' **Avg Price** ' + str(ref_price))
                await ctx.channel.send('Please respond to this message with the missing data (indicated by None) within the next 30 secconds to update the message')
                def check(author):
                    def inner_check(message):
                        if message.author != author:
                            return False
                        else:
                            return True
                    return inner_check
                msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
                date, strike, ticker, side, ref_price = parse_error_order(msg.content, date, strike, ticker, side, ref_price)
            string = ticker + ' ' + strike + ' ' + date + ' ' + side + ' ' + str(ref_price) + ' Channel: ' + ctx.channel.name
            if extra_info is not None:
                string += ' Message: ' + extra_info

            response, account = Account.load_account('accounts', ctx.author.name)
            if response == 200:
                symbol = TD_ACCOUNT.get_option_symbol(ticker, strike, '20', date.split('/')[0], date.split('/')[1], side)
                price = TD_ACCOUNT.get_quotes(symbol)['mark']
                account.add_position(Position(ticker.upper(), date, side, strike, price, symbol, False, False, False, ctx.author.name, ctx.channel.name, dt.datetime.now()))
                print(type(account))
                account.save_self('accounts')
                try:
                    pass
                    #TDExecutor.execute(account.get_username(), 'accounts', opening=True)
                except Exception as e:
                    TDExecutor.log_transaction(str(e))
            else:
                await ctx.author.send("You sent out an alert without first inizializing an account, the alert was sent to all your followers however alert tracking is not available without an account.")

            for member in broadcast(ctx, server_main):
                try:
                    await member.send(ctx.author.name + ' Is now BUYING ' + string)
                except:
                    print('Faile on ' + member.name)
            await ctx.channel.send('**Success**\nBuying: Ticker **' + ticker +'** Strike **' + strike + '** Date **' + date + '** Side **' + side + '** Avg Price **' + str(ref_price) + '**')

@client.command(aliases=['cut', "sold", "cutting", 'selling', 'stc', 'closing', 'sto'])
async def sell(ctx, *, order):
    order = order.replace('*', '')
    server_main = client.get_guild(UTOPIA)
    if check_admin_perms(ctx):
        if len(order.split(' ')) < 3:
            response, account = Account.load_account('accounts', ctx.author.name)
            if response == 200:
                removals = []
                found = False
                for position in account.get_positions():
                    ticker = position.get_ticker().upper()
                    if ticker == order.split(' ')[0].upper():
                        found = True
                        strike = position.get_strike()
                        date = position.get_date()
                        side = position.get_side()
                        price = TD_ACCOUNT.get_quotes(TD_ACCOUNT.get_option_symbol(ticker, strike, '20', date.split('/')[0], date.split('/')[1], side))
                        position_2 = position.copy(closing_trade=True, time=dt.datetime.now(), price=price, executed=False)
                        account.add_trade(Trade(position, position_2))
                        account.add_position(position_2)
                        account.save_self('accounts')
                        try:
                            pass
                            #TDExecutor.execute(account.get_username(), 'accounts', opening=False)
                        except Exception as e:
                            TDExecutor.log_transaction(str(e))
                        account.remove_position(position_2)
                        account.save_self('accounts')
                        await ctx.channel.send('**Success**\nClosed Position: **' + position_2.human_string() + '**')
                        for member in broadcast(ctx, server_main):
                            try:
                                await member.send(ctx.author.name + ' Is now Closing **' + position_2.human_string() + '**')
                            except:
                                print('Faile on ' + member.name)
                        removals.append(position)
                for pos in removals:
                    account.remove_position(pos)
                    account.save_self('accounts')
            else:
                await ctx.author.send("You tried to close a position without first inizializing an account, alert tracking is not available without an account.")
        else:
            date, strike, ticker, side, ref_price, extra_info = parse_initial_order(order)
            while (date is None or strike is None or ticker is None or side is None or ref_price is None):
                await ctx.channel.send('Error: Missing Data.\nCurrent Data = **Ticker** ' + str(ticker) +' **Strike** ' + str(strike) + ' **Date** ' + str(date) + ' **Side** ' + str(side) + ' **Avg Price** ' + str(ref_price))
                await ctx.channel.send('Please respond to this message with the missing data (indicated by None) within the next 30 secconds to update the message')
                def check(author):
                    def inner_check(message): 
                        if message.author != author:
                            return False
                        else:
                            return True
                    return inner_check
                msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
                date, strike, ticker, side, ref_price = parse_error_order(msg.content, date, strike, ticker, side, ref_price)
            string = ticker + ' ' + strike + ' ' + date + ' ' + side + ' ' + str(ref_price) + ' Channel: ' + ctx.channel.name 
            if extra_info is not None:
                string += ' Message: ' + extra_info

            response, account = Account.load_account('accounts', ctx.author.name)
            if response == 200:
                symbol = TD_ACCOUNT.get_option_symbol(ticker, strike, '20', date.split('/')[0], date.split('/')[1], side)
                price = TD_ACCOUNT.get_quotes(symbol)['mark']
                account.add_position(Position(ticker.upper(), date, side, strike, price, symbol, False, True, False, ctx.author.name, ctx.channel.name, dt.datetime.now()))
                account.save_self('accounts')
                try:
                    pass
                    #TDExecutor.execute(account.get_username(), 'accounts', opening=True)
                except Exception as e:
                    TDExecutor.log_transaction(str(e))
            else:
                await ctx.author.send("You sent out an alert without first inizializing an account, the alert was sent to all your followers however alert tracking is not available without an account.")
            for member in broadcast(ctx, server_main):
                try:
                    await member.send(ctx.author.name + ' Is now SELLING ' + string)
                except:
                    print('Faile on ' + member.name)
            await ctx.channel.send('**Success**\nSelling: Ticker **' + ticker +'** Strike **' + strike + '** Date **' + date + '** Side **' + side + '** Avg Price **' + str(ref_price))

client.run(CREDS)