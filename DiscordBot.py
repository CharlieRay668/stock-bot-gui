import discord
from discord.ext import commands
from DiscordListener import Listener
from TDAccount import Account, Trade, Position
from os import path
import os
import datetime as dt
import pandas as pd
from TDRestAPI import Rest_Account
from TDExecutor import TDExecutor
from multiprocessing import Pool
import chain_proccessor as cp
from PIL import Image


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', case_insensitive=True,  intents=intents)

DIRECTORY = 'listeners'

MONEY = 713081521925521469
ENGINE = 713081687516643389
SAMMY = 713082942527897650
ADAM = 738910845702242305
RISKY = 691803632999465011
SWING = 688817761002061848
UTOPIA = 679921845671035034
ADMIN_PRIVATE = 691803430200541244
ADMIN_TEST = 693616063174279270
REQUEST = 679929147107180550

TEST_SERVER = 712778012302770944
PAPER = 736232441857048597
DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.vKvoV8Gz9jBWDWvIaBGDC4xbLB4'
BOT_TOKEN = 'NzU0MDAyMzEwNTM5MTE2NTQ0.X1uZXw.urRh3pgMuS8IAfD4jAMbJVdO8D4'
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
    utopia = client.get_guild(UTOPIA)
    test_server = client.get_guild(TEST_SERVER)
    admin_test = utopia.get_channel(ADMIN_TEST)
    paper =  test_server.get_channel(PAPER)
    return ctx.channel == admin_test or ctx.channel == paper

def check_user_perms(ctx):
    utopia = client.get_guild(UTOPIA)
    request = utopia.get_channel(REQUEST)
    return ctx.channel == request or check_admin_perms(ctx)
    #return check_unstable(ctx)

def check_admin_perms(ctx):
    server_main = client.get_guild(UTOPIA)
    channel_money = server_main.get_channel(MONEY)
    channel_engine = server_main.get_channel(ENGINE)
    channel_sammy = server_main.get_channel(SAMMY)
    channel_admin_test = server_main.get_channel(ADMIN_TEST)
    channel_adam = server_main.get_channel(ADAM)
    channel_risky = server_main.get_channel(RISKY)
    channel_swing = server_main.get_channel(SWING)
    channel_test = server_main.get_channel(ADMIN_TEST)
    return ctx.channel == channel_test or ctx.channel == channel_money or ctx.channel == channel_engine or ctx.channel == channel_sammy or ctx.channel == channel_admin_test or ctx.channel == channel_adam or ctx.channel == channel_risky or ctx.channel == channel_swing
    #return check_unstable(ctx)

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
    print("Real Bot is Ready")


@client.event   
async def on_message_edit(before, ctx):
    if check_admin_perms(ctx):
        splits = ctx.content.split(' ')
        commands = {'creditspread':creditspread, 'debitspread':debitspread, 'buy':buy, 'sell':sell, 'in':buy, "bought":buy, "grabbed":buy, 'grabbing':buy, 'buying':buy, 'bto':buy, 'cut':sell, "sold":sell, "cutting":sell, 'selling':sell, 'stc':sell, 'closing':sell}
        if splits[0][0] == '.':
            for command in commands.keys():
                if splits[0][1:] == command:
                    await commands[command](ctx, order = ' '.join(splits[1:]))
                    #await ctx.invoke(get_command('buy'))


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
async def silentclose(ctx, *, order):
    order = order.replace('*', '').upper()
    ticker = order.split(' ')[0]
    print(order)
    server_main = client.get_guild(UTOPIA)
    if check_admin_perms(ctx):
        response, account = Account.load_account('accounts', ctx.author.name)
        if response == 200:
            positon = account.get_position(ticker)
            account.remove_position(positon)
            await ctx.channel.send('Silently Removed Position ' + str(positon))

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
        await ctx.channel.send('@here ** Success**\n' + open_close[0].upper() + open_close[1:] + ' debit spread' + base_string + legs)


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
                            TDExecutor.execute(account.get_username(), 'accounts', opening=False)
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
                    TDExecutor.execute(account.get_username(), 'accounts', opening=True)
                except Exception as e:
                    TDExecutor.log_transaction(str(e))
            else:
                await ctx.author.send("You sent out an alert without first inizializing an account, the alert was sent to all your followers however alert tracking is not available without an account.")
            
            await ctx.channel.send('**Success**\nBuying: Ticker **' + ticker +'** Strike **' + strike + '** Date **' + date + '** Side **' + side + '** Avg Price **' + str(ref_price) + '**')
            for member in broadcast(ctx, server_main):
                try:
                    await member.send(ctx.author.name + ' Is now BUYING ' + string)
                except:
                    print('Faile on ' + member.name)

def callback():
    print('calledback')

async def sendDM(member, message):
    await member.send(message)

@client.command()
async def speedtest(ctx):
    member = ctx.author
    start = dt.datetime.now()
    pool = Pool(processes=4)              # Start a worker processes.
    result = pool.apply_async(sendDM, args = (member, 'speedtest'), callback = callback)
    #await member.send("Speed Test " + str(x))
    end = dt.datetime.now()-start
    await ctx.channel.send('Time Elapsed to send 50 DMs ' + str(end))

@client.command(aliases=['cut', "sold", "cutting", 'selling', 'stc', 'closing', 'sto', 'close'])
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
                            TDExecutor.execute(account.get_username(), 'accounts', opening=False)
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
                    TDExecutor.execute(account.get_username(), 'accounts', opening=True)
                except Exception as e:
                    TDExecutor.log_transaction(str(e))
            else:
                await ctx.author.send("You sent out an alert without first inizializing an account, the alert was sent to all your followers however alert tracking is not available without an account.")
            
            await ctx.channel.send('**Success**\nSelling: Ticker **' + ticker +'** Strike **' + strike + '** Date **' + date + '** Side **' + side + '** Avg Price **' + str(ref_price))
            for member in broadcast(ctx, server_main):
                try:
                    await member.send(ctx.author.name + ' Is now SELLING ' + string)
                except:
                    print('Faile on ' + member.name)
    

async def handle_reactions(ctx):
    async def send_chain(data):
        img_io = cp.serve_pil_image(cp.create_pil_img(data))
        with open('temp.png' ,'wb') as out: ## Open temporary file as bytes
            out.write(img_io.read())                ## Read bytes into file
        message = await ctx.channel.send(file=discord.File('temp.png'))
        os.remove('temp.png')
        emojis = ['🔺', '🔻', '🇨', '🇵', '💲', '✅', '🔄']
        for emoji in emojis:
            await message.add_reaction(emoji)
        return message
    message = await send_chain(cp.defaultdata())
    def check(reaction, user):
        return user == ctx.author
    reaction_emoji = None
    edits = []
    current_pos = None
    while not reaction_emoji == '✅':
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        if reaction.emoji == '🇵':
            edits.append('BP27')
            current_pos = 'BP27'
        elif reaction.emoji == '🔺' and (not current_pos == None):
            loc = int(current_pos.replace('C', '').replace('P', '').replace('B', '').replace('S', '')) - 2
            current_pos = ''.join([i for i in current_pos if not i.isdigit()])
            current_pos = current_pos + str(loc)
            edits[-1] = current_pos
        elif reaction.emoji == '🔻' and (not current_pos == None):
            loc = int(current_pos.replace('C', '').replace('P', '').replace('B', '').replace('S', '')) + 2
            current_pos = ''.join([i for i in current_pos if not i.isdigit()])
            current_pos = current_pos + str(loc)
            edits[-1] = current_pos
        elif reaction.emoji =='🇨':
            edits.append('BC28')
            current_pos = 'BC28'
        elif reaction.emoji == '💲' and (not current_pos == None):
            if 'B' in current_pos:
                current_pos = current_pos.replace('B', 'S')
            else:
                current_pos = current_pos.replace('S', 'B')
            edits[-1] = current_pos
        elif reaction.emoji == '🔄':
            edits = []
            current_pos = None
        elif reaction.emoji == '✅':
            return edits
        reaction_emoji = reaction.emoji
        await message.delete()
        message = await send_chain(cp.get_edit_data(edits))
    return edits

@client.command()
async def commandcreate(ctx):
    def check(author):
        def inner_check(message): 
            if message.author != author:
                return False
            else:
                return True
        return inner_check
    new_entry = []
    TRADE_COLUMNS = dict.fromkeys(['NAME', 'STRIKE_NUM', 'STRIKE_SEP', 'DIRECTIONAL', 'ORDER_STRUCT', 'DATE_SEP', 'AVERAGE_PRICE', 'AVERAGE_PRICE_SEP'])
    await ctx.channel.send('You are now creating a new command.\nWhat do you want this command to be called, this will be what you type after the .open ex .open creditspread')
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    TRADE_COLUMNS['NAME'] = msg
    await ctx.channel.send('Great, you will now type .open '+msg+' to call your command.\nDoes this strategy contain more than one strike?')
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    msg = msg.lower()
    if msg == 'yes' or msg == 'y' or msg == 'true':
        strings = ['Press the 🇨 to add a call (left side)',
                    'Press the 🇵 to add a call (right side)',
                    'Press the 🔺 to move up a strike',
                    'Press the 🔻 to move down a strike',
                    'Press the 💲 to switch buy/sell, green->buy red->sell',
                    'Press the 🔄 to reset the chain',
                    'Press the ✅ to submit the chain']
        await ctx.channel.send('\nHere is a option chain, please adjust option positions to match your strategy.\n' + '\n'.join(strings))
        order_struct = await handle_reactions(ctx)
        print(order_struct)
        TRADE_COLUMNS['ORDER_STRUCT'] = [order_struct]
        strike_num = len(order_struct)
        TRADE_COLUMNS['STRIKE_NUM'] = strike_num
        calls = False
        puts = False
        for item in order_struct:
            if 'C' in item:
                calls = True
            elif 'P' in item:
                puts = True
        if calls and puts:
            TRADE_COLUMNS['DIRECTIONAL'] = False
            await ctx.channel.send('Great, looks like a non-directional ' + str(strike_num) + ' strike strategy.\n You will need to specify which strikes are calls and which are puts./nThis will look like 45C-50C-35P-40P')
        else:
            await ctx.channel.send('Great, looks like a directional ' + str(strike_num) + ' strike strategy. You will need to specify calls/puts')
            TRADE_COLUMNS['DIRECTIONAL'] = True
        await ctx.channel.send('What will mark your strikes (ex - or , -> 40-45 or 45,45)?')
        msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
        msg = msg.content
        TRADE_COLUMNS['STRIKE_SEP'] = msg
        msg = 'Got it, you will format your strikes like 40' +msg+ '45.'
        await ctx.channel.send(msg)
    else:
        TRADE_COLUMNS['ORDER_STRUCT'] = None
        TRADE_COLUMNS['DIRECTIONAL'] = True
        TRADE_COLUMNS['STRIKE_SEP'] = None
        TRADE_COLUMNS['STRIKE_NUM'] = 1
        await ctx.channel.send('Got it, directional single strike strategy, you will need to specify calls/puts')
    await ctx.channel.send('\nWhat will mark your date (ex / -> 10/29). Default is /, type None to leave as /')
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    if msg.lower() == 'none':
        msg = '/'
    TRADE_COLUMNS['DATE_SEP'] = msg
    await ctx.channel.send('Got it, you will format your dates like 10' +msg+ '29.\nDo you want to specify an average price? If no the bot will automatically gather price information')
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    msg = msg.lower()
    if msg == 'yes' or msg == 'y' or msg == 'true':
        TRADE_COLUMNS['AVERAGE_PRICE'] = True
        await ctx.channel.send('What will mark your average price? (ex @ -> @3.40)')
        msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
        msg = msg.content
        TRADE_COLUMNS['AVERAGE_PRICE_SEP'] = msg
    else:
        TRADE_COLUMNS['AVERAGE_PRICE'] = False
        TRADE_COLUMNS['AVERAGE_PRICE_SEP'] = False
    csv_path = 'command_db.csv'
    data = pd.read_csv(csv_path, index_col=0)
    new_df = pd.DataFrame(data=TRADE_COLUMNS)
    data = data.append(new_df, ignore_index = True)
    data.to_csv(csv_path)
    strike_str = '45'
    if new_df['STRIKE_NUM'].values[0] > 1:
        if new_df['DIRECTIONAL'].values[0]:
            strike_str = new_df['STRIKE_SEP'].values[0].join([str(item) for item in list(range(40, 40+(5*new_df['STRIKE_NUM'].values[0]), 5))])
        else:
            call_num =new_df['STRIKE_NUM'].values[0]//2
            put_num = new_df['STRIKE_NUM'].values[0]-call_num
            call_sep = 'C' + new_df['STRIKE_SEP'].values[0]
            put_sep =  'P' + new_df['STRIKE_SEP'].values[0]
            strike_str = call_sep.join([str(item) for item in list(range(40, 40+(5*call_num), 5))])
            strike_str += put_sep.join([str(item) for item in list(range(40, 40+(5*put_num), 5))])
    directional_str = ''
    if new_df['DIRECTIONAL'].values[0]:
        directional_str = 'calls'
    avg_price_str = ''
    if new_df['AVERAGE_PRICE'].values[0]:
        avg_price_str = new_df['AVERAGE_PRICE_SEP']+'3.40'
    return_str = '.open '+ new_df['NAME'] + ' AMD ' + directional_str + ' ' + strike_str + ' 10' + new_df['DATE_SEP'] + '29 ' + avg_price_str
    await ctx.channel.send("Great, looks like you're all done, here is an example of what your command will look like\n"+str(return_str.values[0]))
    alert_str = ''
    buys = ''
    calls = [item for item in new_df['ORDER_STRUCT'].values[0] if 'C' in item]
    puts = [item for item in new_df['ORDER_STRUCT'].values[0] if 'P' in item]
    def parse_strikes(strike_str, order_struct, strike_split):
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
        for option, instruction in call_struct:
            if instruction[1] == 'B':
                buy_str += option[0] + ' Call strike'
            else:
                sell_str += option[0] + ' Call strike'
        for option, instruction in put_struct:
            if instruction[1] == 'B':
                buy_str += option[0] + ' Put strike'
            else:
                sell_str += option[0] + ' Put strike'
        return buy_str, sell_str
    buy_str, sell_str = parse_strikes()
    await ctx.channel.send("Here is an example of what an alert will look like\n"+str(return_str.values[0]))

@client.command()
async def link(ctx, *, company):
    print('recievid linl')
    company = company.split(' ')
    ticker = company[0]
    name = company[1]
    data = pd.read_csv('company_names.csv', index_col=0)
    new_df = pd.DataFrame(data=[[ticker, name]], columns=['TICKER', 'NAME'])
    data = data.append(new_df, ignore_index = True)
    data.to_csv('company_names.csv')
    embedVar = discord.Embed(title="Got it, linked", description='', color=0xb3b300)
    embedVar.add_field(name='Stock Symbol', value=ticker, inline=False)
    embedVar.add_field(name='Company Name', value=name, inline=False)
    await ctx.channel.send(embed=embedVar)

@client.command()
async def createchannel(ctx):
    guild = ctx.message.guild
    await guild.create_text_channel('bot-created-channel')

@client.command()
async def forcepurge(ctx):
    guild = ctx.message.guild
    x = 0
    for fn in os.listdir('listeners'):
        target = fn.split('.')[0]
        listener = Listener.load_listener(DIRECTORY, target)
        target_members = listener.get_listeners()
        for member in guild.members:
            if member.name in target_members and member.name != 'MoneyMan':
                safe = False
                for role in member.roles:
                    if role.name == 'Gold Members' or role.name == 'Gold' or role.name == 'Admins':
                        safe = True
                if not safe:
                    x += 1
                    listener.remove_listener(member.name)
                    await member.send('You have been removed from alerts as you are no longer a gold member.\n Please resub to gain access again.\nIf you see this as an error please reach out and contact us.')
                    print(member.name)
    await ctx.channel.send('Purged ' + str(x) + ' non gold members from alerts.')

client.run(CREDS)