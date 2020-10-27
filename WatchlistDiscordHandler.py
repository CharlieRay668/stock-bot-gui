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


@client.event
async def on_ready():
    print("Watchlist handler Bot is Ready")

async def output_logs():
    await client.wait_until_ready()
    server = client.get_guild(TEST_SERVER)
    channel = server.get_channel(LOGS)
    print(channel)
    while True:
        logs = [log for log in open('watchlists/watchlist_logs.txt', 'r').readlines() if log not in open('watchlists/watchlists_real_logs.txt', 'r')]
        for log in logs:
            open('watchlists/watchlists_real_logs.txt', '+a').write(log)
            await channel.send(log)

client.loop.create_task(output_logs())
client.run(CREDS)
