import os
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import tasks, commands
import urllib.request, urllib.parse, urllib.error
import json
import ssl
import threading
import aiohttp  # Kapalit ng "requests" na library

# HOY MGA HOTDOG!!
# || Note Use Double negative space when creating a new function for readability ||
# || Try to comment as much as possible || 

# Ignore SSL certificate errors
contx = ssl.create_default_context()
contx.check_hostname = False
contx.verify_mode = ssl.CERT_NONE


# Global variables
db = {}
dbSymbol = {}
mainURL = 'https://api.coingecko.com/api/v3/coins/'
fiat = 'usd'
prefix = '$'
defaultCoin = 'NULL' 


# Extracting API
# Function of getting crypto prices and saving it into the DB
@tasks.loop(seconds=120.0)
async def getCryptoPrices():
    url = mainURL + 'markets?vs_currency=' + fiat
    print(url)
    uh = urllib.request.urlopen(url, context=contx)
    data = uh.read().decode()
    js = json.loads(data)

    # Makng a list for their prices
    for i in range(len(js)):
        dbSymbol[js[i]['symbol']] = js[i]['current_price']
        db[js[i]['id']] = js[i]['symbol']
    if defaultCoin != 'NULL':
        await setcoin_function()


# Function to setcoin
async def setcoin_function():
    crypto = defaultCoin
    print (crypto)
    #if defaultCoin != 'NULL':
    #    getCryptoPrices()
    async with aiohttp.ClientSession() as session:
        async with session.get(mainURL + crypto) as r:
            if isCryptoSupported(crypto) or r.status == 200:
                if not isCryptoSupported(crypto):
                    js = await r.json()
                    symbol = str(js['symbol']).upper()
                    value = js['market_data']['current_price'][fiat]
                    await client.change_presence(status=discord.Status.idle, \
                        activity = discord.Game(f'{symbol}: {value} {fiat.upper()}' ))
                else:
                    value = checkIfSymbol(crypto)
                    symbol = str(value).upper()
                    await client.change_presence(status=discord.Status.idle, \
                        activity = discord.Game(f'{symbol}: {getPrice(value)} {fiat.upper()}' ))


# Function to get alsdfjlasdjf
def getPrice(crypto):
    if crypto in dbSymbol.keys():
        return dbSymbol[crypto]
    else:
        return getCustomCrypto(crypto)
   

# Function to aqwerdjflasjdfljwer
def getCustomCrypto(crypto):
    url = mainURL + crypto
    uh = urllib.request.urlopen(url, context=contx)
    data = uh.read().decode()
    js = json.loads(data)

    value = js['market_data']['current_price'][fiat]
    if value != None:
        return value
    else:
        return False


# Function to yeah ;alsdjfqwerasdf
def isCryptoSupported(crypto):
  if crypto in db.keys() or crypto in dbSymbol.keys():
    return True
  else:
    return False


# Function to check if Yeasdflasdjfljasdf
def checkIfSymbol(crypto):
    if crypto in db.keys():
        return db[crypto]
    else:
        return crypto


# || Start of the bot commands using the bots commands framework ||
client = commands.Bot(command_prefix = '>') # Instancing a bot using the commands framework

@client.event   # Take note that the "client" variable is the actual bot
async def on_ready():
    print("bot has logged in")
    # Print to the console when the bot is online
    await client.get_channel(894442046599860256).send('bot is now online!') 

    #await threading.Timer(60.0, setcoin).start()


# Change Prefix function
@client.command(name='changeprefix', aliases=['cp', 'changep'], description=\
    'Change the Bot prefix')
async def change_prefix_command(ctx, arg):
    client.command_prefix = arg
    await ctx.channel.send(f'Prefix is changed to {arg}')


# Function to check if the coin is in the default support list
@client.command(name='support', aliases=['sp', 'supp'], description=\
    'Check if the coin is supported')
async def support_command(ctx, arg):
    if isCryptoSupported(arg):
        await ctx.channel.send(f'{arg} is supported')
    else:
        await ctx.channel.send(f'{arg} is not supported, check and use the API id')


# Function to set the default fiat
@client.command(name='setfiat', aliases=['sf', 'setf'], description=\
    'Change the default currency conversion')
async def setfiat_command(ctx, arg):
    if ctx.author.top_role.permissions.administrator == True:   #Checks if the user is an Administrator
        global fiat
        fiat = arg
        async with aiohttp.ClientSession() as session:
            async with session.get(mainURL + 'markets?vs_currency=' + fiat) as r:
                if r.status == 200:
                    await ctx.channel.send(f'Default FIAT is now {fiat}')
                    await getCryptoPrices()
                    if defaultCoin != 'NULL':
                        await setcoin_function() # Updates the status of the bot if it is active
                else:
                    await ctx.channel.send(f'{fiat} mali lods aral muna')
    else:
        await ctx.channel.send(f'You must be an Administrator to change the tracked coin.')
    

# Function to set the custom status tracked coin
@client.command(name='setcoin', aliases=['sc', 'setc'], description=\
    'Change the coin to be tracked and displayed as the Bot status')
async def setcoin_command(ctx, arg):
    if ctx.author.top_role.permissions.administrator == True:   #Checks if the user is an Administrator
        global defaultCoin
        defaultCoin = arg
        await setcoin_function()
        await ctx.channel.send(f'"{defaultCoin}" is now being tracked')
    else:
        await ctx.channel.send(f'You must be an Administrator to change the tracked coin.')


# Function to check the current price of a coin using the API ID
@client.command(name='priceof', aliases=['po', 'price'], description=\
    'Check if the price of a specific coin using the coingecko API ID')
async def price_command(ctx, arg):
    crypto = arg
    async with aiohttp.ClientSession() as session:
        async with session.get(mainURL + crypto) as r:
            # Check if token is valid
            if isCryptoSupported(crypto) or r.status == 200:
                coin = checkIfSymbol(crypto)
                value = getPrice(coin)
                print(coin)
                print(fiat)
                await ctx.channel.send(f'The current price of "{crypto}" is: {value} {fiat.upper()}')
            else:
                await ctx.channel.send(f'The token is not not found, get the API ID  at coingecko')


# Function eme idk old function
@client.command(name='hello', aliases=['h', 'hl', 'he'])
async def hello_command(ctx):
    await ctx.channel.send("Hello Hotdog ")

#mark was here

#@getCryptoPrices.before_loop(client.wait_until_ready())
getCryptoPrices.start()
# Running/Activating the Bot
client.run(os.getenv("BOT_TOKEN"))