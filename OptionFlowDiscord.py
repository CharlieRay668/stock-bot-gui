import discord
from discord.ext import commands
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import random
PASSWORD = 'r3I15XVm!C@b'
USERNAME = 'charlieary'
URL = 'https://quantdata.us/login'

def login(password, username, url):
    driver = webdriver.Chrome(executable_path=r'C:\Users\charl\Desktop\chromedriver\chromedriver.exe')
    driver.get(url)
    time.sleep(3)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div/div[2]/form/div[1]/div/input').send_keys(username)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div/div[2]/form/div[4]/input').click()
    time.sleep(4)
    #option_table = driver.find_element_by_id('optionsTableBody')
    return driver

def get_option_table(driver):
    return driver.find_element_by_id('optionsTableBody')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', case_insensitive=True, intents=intents)

TEST_SERVER = 767113239154393138
PAPER = 767113239594926120
BOT_TOKEN = 'NzY3MTEzNTA2NDU3MjU2MDA4.X4tMIA.aC_J8Q0maMWVeYM6QtdCMEXN-ko'
CREDS = BOT_TOKEN


    
def check_unstable(ctx):
    test_server = client.get_guild(TEST_SERVER)
    paper =  test_server.get_channel(PAPER)
    return ctx.channel == paper

async def send_message(channel, message):
    splits = message.split()
    data = {   
        'time': ' '.join(splits[0:2]),
        "stock":(splits[2]),
        "expiration":' '.join(splits[3:6]),
        "strike":(splits[6]),
        "contract":(splits[7]),
        "referance":(splits[8]),
        "details":' '.join(splits[9:12]),
        "premium":' '.join(splits[12:14]),
        "type":(splits[14]),
        "volume":(splits[15]),
        "OI":(splits[16])
    }
    embedVar = discord.Embed(title=data['stock'] + ' ' + data['contract'], description='', color=0x0EFF03)
    for key in data.keys():
        embedVar.add_field(name=key.upper(), value=data[key], inline=True)
    await channel.send(embed=embedVar)

async def option_flow():
    await client.wait_until_ready()
    test_server = client.get_guild(TEST_SERVER)
    print(test_server)
    channel =  test_server.get_channel(PAPER)
    print(channel)
    driver = login(PASSWORD, USERNAME, URL)
    last_outputs = []
    while True:
        outputs = get_option_table(driver).text.split('\n')
        for output in outputs:
            if output not in last_outputs:
                await send_message(channel, output)
        last_outputs = outputs

client.loop.create_task(option_flow())
client.run(CREDS)