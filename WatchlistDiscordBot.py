import discord
from discord.ext import commands
from os import path
import os
import datetime as dt
import time
from TDRestAPI import Rest_Account
import pandas as pd
from TDAccount import Account, Trade, Position
import TDSteamingAPI as TD_Stream
from TDSteamingAPI import Request, ClientWebsocket
from Watchlist import Watch
import threading
try:
    import thread
except ImportError:
    import _thread as thread
import asyncio


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', case_insensitive=True,  intents=intents)

DIRECTORY = 'watchlists'

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
LOGS = 714310564062429275
DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.vKvoV8Gz9jBWDWvIaBGDC4xbLB4'
BOT_TOKEN = 'NzU0MDAyMzEwNTM5MTE2NTQ0.X1uZXw.urRh3pgMuS8IAfD4jAMbJVdO8D4'
CREDS = DEV_BOT_TOKEN

def clean_watch(args):
    args = args.lower()
    symbols = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '=', '+']
    banned_words = ['pt','pt:','profit', 'target', 'profittarget', 'target', 'tg', 'pr', 'pd', 'py', 'pg', 'pf', 'call', 'calls', 'put' , 'puts', 'p', 'c']
    banned_words = banned_words + symbols
    args = [arg for arg in args.split(' ') if arg not in banned_words]
    return args 

@client.command()
async def watchlist(ctx, *, args):
    args = clean_watch(args)
    print(args)
    if args[0] == 'add':
        print(args)
        new = Watch(args[1], args[2], args[3], args[4], ctx.author.name, False, False)
        await ctx.channel.send('Added ' + str(new))
    elif args[0] == 'view':
        today = dt.date.today().strftime("%Y_%m_%d")
        csv_path = DIRECTORY+'/'+today+'_watchlist.csv'
        if path.exists(csv_path):
            data = pd.read_csv(csv_path)
            embedVar = discord.Embed(title=ctx.author.name + "'s Watchlist for today", description='', color=0xb3b300)
            for row in data.iterrows():
                row = row[1].to_dict()
                first = 'PUTS'
                if row['DIRECTION'] == 'above':
                   first = 'CALLS'
                embedVar.add_field(name=row['SYMBOL'].upper(), value = first + ' ' + row['DIRECTION'].upper() + ' ' + str(row['THRESHOLD']) + ' Profit Target: ' + str(row['PT']), inline=False)
            await ctx.channel.send(embed = embedVar)
        else:
            await ctx.channel.send("Sorry, I can't seem to find any watchlists for today")
    elif args[0] == 'delete':
        pass

@client.event
async def on_ready():
    print("Watchlist Bot is Ready")

# async def output_logs():
#     await client.wait_until_ready()
#     server = client.get_guild(TEST_SERVER)
#     channel = server.get_channel(LOGS)
#     print(channel)
#     while client.is_closed:
#         logs = open('watchlists/watchlist_logs.txt', 'r').readlines()
#         print(logs,'yessir')
#         for log in logs:
#             await channel.send(log)

# client.loop.create_task(output_logs())
client.run(CREDS)
