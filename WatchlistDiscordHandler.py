import discord
from discord.ext import commands
from os import path
import os
from DiscordListener import Listener
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

DIRECTORY = 'listeners'

UTOPIA = 679921845671035034

LOGS = 714310564062429275
DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.vKvoV8Gz9jBWDWvIaBGDC4xbLB4'
BOT_TOKEN = 'NzU0MDAyMzEwNTM5MTE2NTQ0.X1uZXw.urRh3pgMuS8IAfD4jAMbJVdO8D4'
CREDS = DEV_BOT_TOKEN


@client.event
async def on_ready():
    print("Watchlist handler Bot is Ready")

def broadcast(author_name, server_main):
    target_members = None
    for fn in os.listdir('listeners'):
        target = fn.split('.')[0]
        if target == author_name:
            listener = Listener.load_listener(DIRECTORY, target)
            target_members = listener.get_listeners()
    true_target = []
    if target_members is not None:
        for member in server_main.members:
            if member.name in target_members:
                true_target.append(member)
    return true_target

async def output_logs():
    await client.wait_until_ready()
    server = client.get_guild(UTOPIA)
    while True:
        try:
            logs = [log for log in open('watchlists/watchlist_logs.txt', 'r').readlines() if log not in open('watchlists/watchlists_real_logs.txt', 'r')]
            for log in logs:
                message = log.split('//:')[0]
                print(message)
                print(log)
                channel = log.split('//:')[1].split(' ')[0]
                print(channel)
                author = log.split('//:')[1].split(' ')[1]
                print(author)
                for member in server.members:
                    if member.name == author or member.nick == author:
                        await member.send(message)
                for user in broadcast(author, server):
                    try:
                        await user.send(message + ' from ' + str(author) + "'s Watchlist" )
                    except:
                        print('Failed on ' + str(user.name))
                open('watchlists/watchlists_real_logs.txt', '+a').write(log)
                await server.get_channel(int(channel)).send(message + ' from ' + str(author) + "'s Watchlist" )
        except:
            pass

def start_discord_watchlist():
    client.loop.create_task(output_logs())
    client.run(CREDS)

start_discord_watchlist()