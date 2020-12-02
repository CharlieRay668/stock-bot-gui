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
from Watchlist import Watch
import numpy as np
import command_handler as ch
# import WatchlistHandler as watchlist_handler
# import WatchlistDiscordHandler as watchlist_discord_handler


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', case_insensitive=True,  intents=intents)

look_up = {'01': 'January', '02': 'Febuary', '03': 'March', '04': 'April', '05': 'May',
            '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

DIRECTORY = 'listeners'
WATCHLIST_DIRECTORY = 'watchlists'

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


@client.event
async def on_ready():
    print("Real Bot is Ready")

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

async def sendDM(member, message):
    await member.send(message)

def check_member_id(params):
    members = client.get_guild(UTOPIA).members
    for param in params.split(' '):
        if '@' in param:
            name_id = param.replace('@', '').replace('@!', '').replace('<', '').replace('>', '')
            for member in members:
                if int(name_id) == member.id:
                    return member.name
    return None

def clean_watch(args):
    args = args.lower()
    symbols = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '=', '+']
    banned_words = ['pt','pt:','profit', 'target', 'profittarget', 'target', 'tg', 'pr', 'pd', 'py', 'pg', 'pf', 'call', 'calls', 'put' , 'puts', 'p', 'c']
    banned_words = banned_words + symbols
    args = [arg for arg in args.split(' ') if arg not in banned_words]
    return args 

def admin_channel_lookup(username):
    admin_channel = {'Charlie678':693616063174279270,
                    'SammySnipes':713082942527897650,
                    'Engine Trades':713081687516643389,
                    'MoneyMan':713081521925521469,
                    'Adam B':738910845702242305}
    if username in admin_channel.keys():
        return admin_channel[username]
    else:
        return None

@client.command()
async def watchlist(ctx, *, args):
    args = clean_watch(args)
    print(args)
    if args[0] == 'start':
        # watchlist_handler.handle_watches()
        # watchlist_discord_handler.start_discord_watchlist()
        await ctx.channel.send('Started watchlist')
    elif args[0] == 'add':
        channel = admin_channel_lookup(ctx.author.name)
        new = Watch(args[1], args[2], args[3], args[4], ctx.author.name, False, 0, channel)
        await ctx.channel.send('Added ' + str(new))
    elif args[0] == 'view':
        today = dt.date.today().strftime("%Y_%m_%d")
        csv_path = WATCHLIST_DIRECTORY+'/'+today+'_watchlist.csv'
        if path.exists(csv_path):
            params = ' '.join(args)
            if len(params.split(' ')) < 2:
                name = ctx.author.name
            else:
                name = ''
                if check_member_id(params) is None:
                    if '(' in params and ')' in params:
                        start = params.find('(')
                        end = params.find(')')
                        name = params[start+1:end]
                    else:
                        name = params.split(' ')[1]
                else:
                    name = check_member_id(params)
            data = pd.read_csv(csv_path)
            embedVar = discord.Embed(title=name + "'s Watchlist for today", description='', color=0xb3b300)
            signal_dict = {0:'Not Near or Crossed',
                            1:'Near but not Crossed',
                            2:'Crossed Threshold',
                            3:'Near Profit Target',
                            4:'Crossed Threshold and Profit Target'}
            for index, row in data.iterrows():
                print(row)
                if row['AUTHOR'] == name:
                    #row = row[1].to_dict()
                    first = 'PUTS'
                    if row['DIRECTION'] == 'above':
                        first = 'CALLS'
                    embedVar.add_field(name=row['SYMBOL'].upper(), value = first + ' ' + row['DIRECTION'].upper() + ' ' + str(row['THRESHOLD']) + ' Profit Target: ' + str(row['PT']) + ' ' + str(signal_dict[row['ALERTED']]), inline=False)
            await ctx.channel.send(embed = embedVar)
        else:
            await ctx.channel.send("Sorry, I can't seem to find any watchlists for today")
    elif args[0] == 'delete':
        pass

@client.command()
async def close_expirations(ctx):
    server_main = client.get_guild(UTOPIA)
    trades = pd.read_csv('trades_db.csv', index_col=0)
    positions = pd.read_csv('positions_db.csv', index_col=0)
    logs = open('expired_positions.txt', 'a+')
    trader_dict = {}
    for trader in trades['TRADER']:
        trader_dict[trader] = []
    for index, row in trades.iterrows():
        date = row['DATE'].split('/')
        if not row['CLOSED']:
            try:
                if len(date) == 3:
                    time =dt.datetime.strptime(row['DATE'],'%m/%d/%y')
                elif len(date) > 3:
                    date_str ='/'.join(date[:3])
                    time =dt.datetime.strptime(date_str,'%m/%d/%y')
                else:
                    date_str ='/'.join(date)+'/20'
                    time =dt.datetime.strptime(date_str,'%m/%d/%y')
                if time < dt.datetime.now():
                    trade_id = row['ID']
                    pos = positions[positions['id'] == trade_id]
                    num = 0
                    closed_positions = []
                    for i, p in pos.iterrows():
                        num += 1
                        closed_positions.append(p['ticker'] + ' ' + str(p['strike']) + ' ' + p['side'] + ' ' + p['date'] +  ' ' + str(p['askPrice']) + ' ' +str(time) + ' ' + str(p['id']))
                    trader_dict[row['TRADER']].append(closed_positions)
            except:
                print('failed on ' + row['DATE'])
    for key in trader_dict.keys():
        if len(trader_dict[key]) > 0:
            for member in server_main.members:
                if member.name == key:
                    send_str = 'This is a message updating you about unclosed expired positions that you held in the competition\n'
                    send_str += 'If your position expired ITM, the bot will recognize that and calculate profit accordingly\n'
                    send_str += 'If your position expired OTM, the bot will determine if there was an error closing the position or if the position was never closed\n'
                    send_str += 'If the bot determined there was an error when closing the position you will not receive any penalty to your leaderboard ranking\n'
                    send_str += 'If the bot determined that the position was simply forgotten about, there will be a -20% penalty to give grace and simulate proper risk management\n'
                    send_str += 'Going forward, ANY position that expired OTM will count as a -100% penalty, make sure to close out your positions in the future.\n'
                    for trade in trader_dict[key]:
                        if len(trade) > 1:
                            profit = 0
                            for pos in trade:
                                ticker = pos.split(' ')[0]
                                strike = pos.split(' ')[1]
                                side = pos.split(' ')[2]
                                date = pos.split(' ')[3]
                                price = pos.split(' ')[4]
                                time = pos.split(' ')[5]
                                trade_id = pos.split(' ')[7]
                                time = dt.datetime.strptime(time,'%Y-%m-%d')
                                num_days = (dt.datetime.now()-time).days
                                hist = TD_ACCOUNT.history(ticker, 1, 0, days_ago=num_days)
                                eod_price = hist.iloc[[-1]]['close'][0]
                                intrinsic_value = eod_price-float(strike)
                                if side == 'PUTS':
                                    intrinsic_value = intrinsic_value*-1
                                if float(price) == 0.0:
                                    profit += 0
                                    send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired ERROR reciving ' + '0' + '% ' + ' (No penalty)**\n'
                                elif intrinsic_value > 0:
                                    profit += round((float(intrinsic_value/abs(float(price)))-1)*100,2)
                                    send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired ITM reciving ' + str(round((float(intrinsic_value/abs(float(price)))-1)*100,2)) + '% ' + 'Calculated profit**\n'
                                else:
                                    profit += -20
                                    send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired OTM reciving ' + '-20' + '% ' + 'Penalty**\n'
                        else:
                            pos = trade[0]
                            ticker = pos.split(' ')[0]
                            strike = pos.split(' ')[1]
                            side = pos.split(' ')[2]
                            date = pos.split(' ')[3]
                            price = pos.split(' ')[4]
                            time = pos.split(' ')[5]
                            trade_id = pos.split(' ')[7]
                            
                            time = dt.datetime.strptime(time,'%Y-%m-%d')
                            num_days = (dt.datetime.now()-time).days
                            #print(ticker, strike, side, date, price)
                            hist = TD_ACCOUNT.history(ticker, 1, 0, days_ago=num_days)
                            eod_price = hist.iloc[[-1]]['close'][0]
                            intrinsic_value = eod_price-float(strike)
                            if side == 'PUTS':
                                intrinsic_value = intrinsic_value*-1
                            if float(price) == 0.0:
                                profit = 0
                                send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired ERROR reciving ' + str(profit) + '% ' + ' (No penalty)**\n'
                            elif intrinsic_value > 0:
                                profit = round((float(intrinsic_value/abs(float(price)))-1)*100,2)
                                send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired ITM reciving ' + str(profit) + '% ' + 'Calculated profit**\n'
                            else:
                                if member.name != 'Eddy_Trades💸⭕🖨' and member.name != 'Visvim':
                                    profit = -20
                                    send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired OTM reciving ' + str(profit) + '% ' + 'Penalty**\n'
                                else:
                                    profit = 0
                                    send_str += '**' + ticker + ' ' + str(strike) + ' ' + str(side) + ' ' + str(date) + ' expired ERROR reciving ' + str(profit) + '% ' + ' (No penalty)**\n' 
                        for index in trades.index:
                            if trades.loc[index,'ID']==trade_id:
                                trades.loc[index, 'CLOSED'] = True
                                trades.loc[index, 'PROFIT'] = float(profit)
                        trades.to_csv('trades_db.csv')
                        positions = pd.read_csv('positions_db.csv', index_col=0)
                        positions = positions[positions['id'] == trade_id]
                        new_positions = []
                        new_data ={'bidPrice':None,'askPrice':None,'delta':None,'theta':None,'gamma':None,'volatility':None,'description':None,'assetType':None}
                        for index, position_row in positions.iterrows():
                            new_position = []
                            for key in new_data.keys():
                                new_data[key] = 'Expired'
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
                    print(member.name)
                    await member.send(send_str)

@client.command()
async def record(ctx, *, params):
    print(ctx, params)
    members = client.get_guild(UTOPIA).members
    for param in params.split(' '):
        if '@!' in param:
            name_id = param.replace('@!', '').replace('<', '').replace('>', '')
            for member in members:
                if int(name_id) == member.id:
                    print(member.name)
        print(param)
        print(type(param))

def calc_leaderboard():
    trades_db = pd.read_csv('trades_db.csv')
    member_profits = {}
    for index, row in trades_db.iterrows():
        if not (row['TRADER'] == 'SammySnipes' or row['TRADER']  == 'MoneyMan' or row['TRADER']  == 'Engine Trades' or row['TRADER'] == 'TacoTradez🌮'):
            if not pd.isnull(row['PROFIT']):
                if row['TRADER'] in member_profits.keys():
                    if row['PROFIT'] > 0:
                        member_profits[row['TRADER']] = (member_profits[row['TRADER']][0] + row['PROFIT'], member_profits[row['TRADER']][1] + 1, member_profits[row['TRADER']][2])
                    else:
                        member_profits[row['TRADER']] = (member_profits[row['TRADER']][0] + row['PROFIT'], member_profits[row['TRADER']][1], member_profits[row['TRADER']][2] + 1)
                else:
                    if row['PROFIT'] >= -0.1:
                        member_profits[row['TRADER']] = (row['PROFIT'], 1, 0)
                    else:
                        member_profits[row['TRADER']] = (row['PROFIT'], 0, 1)
    leaderboard = []
    for key in member_profits.keys():
        profit = round(member_profits[key][0],2)
        win = member_profits[key][1]
        loss = member_profits[key][2]
        if loss == 0:
            score = (profit/100)
        else:
            score = (profit/100) * (win/(loss+win))
        score += (win*0.7)
        score -= (loss*0.7)
        leaderboard.append((round(score*10,2), key))
    leaderboard.sort(reverse=True)
    return leaderboard

@client.command(aliases=['check'])
async def view(ctx, *, params):
    if params.split(' ')[0] == 'commands':
        await ctx.channel.send("\n**OPENING COMMANDS**\n'in', 'bought', 'grabbed', 'grabbing', 'buying', 'bto', 'btc','swing', 'swinging', 'buy','open'\n**CLOSING COMMANDS**\n'cut', 'sold', 'cutting', 'selling', 'stc', 'closing', 'sto', 'sell'")
    elif params.split(' ')[0] == 'stats':
        trades_db = pd.read_csv('trades_db.csv')
        if len(params.split(' ')) < 2:
            name = ctx.author.name
        else:
            name = ''
            if check_member_id(params) is None:
                if '(' in params and ')' in params:
                    start = params.find('(')
                    end = params.find(')')
                    name = params[start+1:end]
                else:
                    name = params.split(' ')[1]
            else:
                name = check_member_id(params)
        individual_trades = trades_db[trades_db['TRADER'] == name]
        individual_trades = individual_trades[individual_trades['CLOSED'] == True]
        print(name)
        if len(individual_trades) < 1:
            await ctx.channel.send('User ' + name + ' has no stats to show')
        else:
            profit = 0
            wins = 0
            losses = 0
            for index, row in individual_trades.iterrows():
                profit += row['PROFIT']
                if row['PROFIT'] >= 0:
                    wins += 1
                else:
                    losses +=1
            leaderboard = calc_leaderboard()
            location = -1
            for index, person in enumerate(leaderboard):
                if person[1] == name:
                    location = index
            embedVar = discord.Embed(title="Stats for user " + name, description='', color=0x00e6b8)
            embedVar.add_field(name='% Profit', value=str(profit) + '%', inline=False)
            embedVar.add_field(name='# Wins', value=str(wins), inline=True)
            embedVar.add_field(name='# Losses', value=str(losses), inline=True)
            embedVar.add_field(name='Leaderboard Ranking', value=str(location+1), inline=False)
            await ctx.channel.send(embed=embedVar)
    elif params.split(' ')[0] == 'leaderboard':
        embedVar = discord.Embed(title="Leaderboard for month of " + look_up[dt.datetime.today().strftime('%m')], description='', color=0x00e6b8)
        leaderboard = calc_leaderboard()
        for index, person in enumerate(leaderboard[:10]):
            embedVar.add_field(name='#' + str(index+1), value=person[1] + ' Score ' + str(person[0]) + ' pts', inline=False)
        await ctx.channel.send(embed=embedVar)
    elif params.split(' ')[0] == 'status':
        if len(params.split(' ')) < 2:
            name = ctx.author.name
        else:
            name = ''
            if check_member_id(params) is None:
                if '(' in params and ')' in params:
                    start = params.find('(')
                    end = params.find(')')
                    name = params[start+1:end]
                else:
                    name = params.split(' ')[1]
            else:
                name = check_member_id(params)
        print(name)
        trades_db = pd.read_csv('trades_db.csv', index_col=0)
        positions_db = pd.read_csv('positions_db.csv', index_col=0)
        individual_trades = trades_db[trades_db['TRADER'] == name]
        print(individual_trades)
        individual_trades = individual_trades[individual_trades['CLOSED'] == False]
        if len(individual_trades) < 1:
            await ctx.channel.send('Either unable to find user ' + name + ' or user ' + name + ' has no open positions to show')
        else:
            embedVar = discord.Embed(title=name+"'s current public positions", description='These may not be fully accurate due to inconsitency in closing of positions.', color=0x00e6b8)
            for index, row in individual_trades.iterrows():
                positions = positions_db[positions_db['id'] == row['ID']]
                if row['COMMAND'] == 'standard':
                    title = row['TICKER']
                else:
                    title = row['TICKER'] + ' ' + row['COMMAND'][0].upper() + row['COMMAND'][1:]
                value = ''
                short_str = 'Short '
                long_str = 'Long '
                shorts = False
                longs = False
                for index, position in positions.iterrows():
                    if position['short_trade']:
                        short_str += str(position['strike']) + ' ' + position['side'] + ' '
                        shorts = True
                    else:
                        long_str += str(position['strike']) + ' ' + position['side'] + ' '
                        longs = True
                if longs:
                    value += long_str
                if shorts:
                    value += short_str
                value += ' ' + row['DATE']
                embedVar.add_field(name=title, value=value, inline=False)
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
        await ctx.channel.send('Unkown view command')

@client.command(aliases=['in', "bought", "grabbed", 'grabbing', 'buying', 'bto', 'btc','swing', 'swinging', 'buy','open'])
async def discordopen(ctx, *, order):
    server_main = client.get_guild(UTOPIA)
    order = order.lower().replace('$', '')
    response, message = ch.classic_open(order, ctx.author.name, ctx.channel.name, TD_ACCOUNT)
    await ctx.channel.send(message)
    if response == 200:
        for member in broadcast(ctx, server_main):
            try:
                await member.send(ctx.author.name + ' Is now ' + message.split('\n')[1])
            except:
                print('Faile on ' + member.name)

@client.command(aliases=['cut', "sold", "cutting", 'selling', 'stc', 'closing', 'sto', 'sell'])
async def close(ctx, *, order):
    server_main = client.get_guild(UTOPIA)
    order = order.lower().replace('$', '')
    response, message = ch.handle_closing_order(order, ctx.author.name, ctx.channel.name, TD_ACCOUNT)
    print(ctx.author.name)
    if (ctx.author.name == 'SammySnipes' or ctx.author.name == 'MoneyMan' or ctx.author.name == 'Engine Trades' or ctx.author.name =='Charlie678'):
        print('Located author name')
        print(message)
        message = message.split('for recorded')[0]
        print(message)
    if not response == 101:
        await ctx.channel.send(message)
    else:
        trades = message
        positions_db = pd.read_csv('positions_db.csv', index_col=0)
        embedVar = discord.Embed(title="You seem to have more than one position that fit " + str(order), description='Please add additional specification, ie a date or a strike', color=0x00e6b8)
        for index, row in trades.iterrows():
            positions = positions_db[positions_db['id'] == row['ID']]
            if row['COMMAND'] == 'standard':
                title = row['TICKER']
            else:
                title = row['TICKER'] + ' ' + row['COMMAND'][0].upper() + row['COMMAND'][1:]
            value = ''
            short_str = 'Short '
            long_str = 'Long '
            shorts = False
            longs = False
            for index, position in positions.iterrows():
                if position['short_trade']:
                    short_str += str(position['strike']) + ' ' + position['side'] + ' '
                    shorts = True
                else:
                    long_str += str(position['strike']) + ' ' + position['side'] + ' '
                    longs = True
            if longs:
                value += long_str
            if shorts:
                value += short_str
            value += ' ' + row['DATE']
            embedVar.add_field(name=title, value=value, inline=False)
        await ctx.channel.send(embed=embedVar)
    if response == 200:
        for member in broadcast(ctx, server_main):
            try:
                await member.send(ctx.author.name + ' Is now ' + message.split('\n')[1])
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
    name = msg.lower()
    data = pd.read_csv('command_db.csv')
    check_name = data[data['NAME'] == name]
    if len(check_name) > 0:
        await ctx.channel.send('Sorry, there is a command named ' + name + ' that already exists\nUnable to create duplicate command, exiting command creation process')
        return
    quote = TD_ACCOUNT.get_quotes(name.upper())
    if quote is not None:
        await ctx.channel.send('Sorry, your command is too similar to stock symbol ' + name.upper() +'\nUnable to create command, exiting command creation process')
        return
    TRADE_COLUMNS['NAME'] = msg.lower()
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
        await ctx.channel.send('What will mark your strikes (ex - -> 40-45)?')
        msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
        msg = msg.content
        if msg.lower() == ',':
            ctx.channel.send('Sorry, unable to set comma equal to strike seperator. This causes conflicts in data storage.\nExiting command creation process')
            return
        TRADE_COLUMNS['STRIKE_SEP'] = msg
        msg = 'Got it, you will format your strikes like 40' +msg+ '45.'
        await ctx.channel.send(msg)
    else:
        TRADE_COLUMNS['ORDER_STRUCT'] = None
        TRADE_COLUMNS['DIRECTIONAL'] = True
        TRADE_COLUMNS['STRIKE_SEP'] = None
        TRADE_COLUMNS['STRIKE_NUM'] = 1
        await ctx.channel.send('Got it, directional single strike strategy, you will need to specify calls/puts')
    await ctx.channel.send('\nDo you want to change the default date format of MM/DD? If so specify what seperates them, ex : -> MM:DD' )
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    if msg.lower() == 'no' or msg.lower() == 'n':
        msg = '/'
    if msg.lower() == ',':
        ctx.channel.send('Sorry, unable to set comma equal to date seperator. This causes conflicts in data storage.\nExiting command creation process')
        return
    TRADE_COLUMNS['DATE_SEP'] = msg
    await ctx.channel.send('Got it, you will format your dates like 10' +msg+ '29.\nDo you want to change the default avg price format of @3.00?')
    msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
    msg = msg.content
    msg = msg.lower()
    if msg == 'yes' or msg == 'y' or msg == 'true':
        TRADE_COLUMNS['AVERAGE_PRICE'] = True
        await ctx.channel.send('What will mark your average price? (ex @ -> @3.40)')
        msg = await client.wait_for('message', timeout=30.0, check=check(ctx.author))
        msg = msg.content
        if msg.lower() == ',':
            ctx.channel.send('Sorry, unable to set comma equal to avg price seperator. This causes conflicts in data storage.\nExiting command creation process')
            return
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
            call_num =new_df['STRIKE_NUM'].values[0]
            call_sep = 'C' + new_df['STRIKE_SEP'].values[0]
            strike_str = call_sep.join([str(item) for item in list(range(80, 80+(5*call_num), 5))])
            strike_str += 'C'
        else:
            call_num =new_df['STRIKE_NUM'].values[0]//2
            put_num = new_df['STRIKE_NUM'].values[0]-call_num
            call_sep = 'C' + new_df['STRIKE_SEP'].values[0]
            put_sep =  'P' + new_df['STRIKE_SEP'].values[0]
            strike_str = call_sep.join([str(item) for item in list(range(80, 80+(5*call_num), 5))])
            strike_str += put_sep.join([str(item) for item in list(range(80, 80+(5*put_num), 5))])
    avg_price_str = ''
    if new_df['AVERAGE_PRICE'].values[0]:
        avg_price_str = new_df['AVERAGE_PRICE_SEP']+'3.40'
    return_str = '.open '+ new_df['NAME'] + ' AMD ' + strike_str + ' MM' + new_df['DATE_SEP'] + 'DD ' + avg_price_str
    await ctx.channel.send("Great, looks like you're all done, here is an example of what your command will look like\n"+str(return_str.values[0]))

client.run(CREDS)