import os
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import tasks, commands
import urllib.request, urllib.parse, urllib.error
import json
import ssl
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
defaultCoin = 'NULL' 

# Load prefixes from json file
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefix = json.load(f)
    print (str(message.guild.id))
    print (prefix)
    return prefix[str(message.guild.id)]

# Set default prefix when joining 


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
                        activity = discord.Game(f'{symbol}: {"{:,}".format(value)} {fiat.upper()}' ))
                else:
                    value = checkIfSymbol(crypto)
                    symbol = str(value).upper()
                    await client.change_presence(status=discord.Status.idle, \
                        activity = discord.Game(f'{symbol}: {"{:,}".format(getPrice(value))} {fiat.upper()}' ))


# Function to return a single field embed
def getEmbed(name, value, inline):
    embed = discord.Embed(
            colour = discord.Colour.orange()
    )
    embed.add_field(name=name, value=value, inline=inline)
    return embed


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
client = commands.Bot(command_prefix = get_prefix) # Instancing a bot using the commands framework
client.remove_command('help')

@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefix = json.load(f)

    prefix[str(guild.id)] = '$'

    with open('prefixes.json', 'w') as f:
        json.dump(prefix,f)

@client.event   # Take note that the "client" variable is the actual bot
async def on_ready():
    print("bot has logged in")  # Print to the console when the bot is online


# Change Prefix function
@client.command(name='setprefix', aliases=['sp', 'setp'], description=\
    'Change the Bot prefix')
async def set_prefix_command(ctx, arg):
    with open('prefixes.json', 'r') as f:
        prefix = json.load(f)

    prefix[str(ctx.guild.id)] = arg

    with open('prefixes.json', 'w') as f:
        json.dump(prefix,f)
    
    await ctx.channel.send(embed=getEmbed(\
            name='PREFIX CHANGED',\
            value=f'Prefix is changed to {arg}', \
            inline=False))


# Function to check if the coin is in the default support list
@client.command(name='support', aliases=['s', 'supp'], description=\
    'Check if the coin is supported')
async def support_command(ctx, arg):
    if isCryptoSupported(arg):
        await ctx.channel.send(embed=getEmbed(\
            name='SUPPORTED',\
            value=f'> {arg} is supported', \
            inline=False))
    else:
        await ctx.channel.send(embed=getEmbed(\
            name='NOT SUPPORTED',\
            value=f'> {arg} is not supported. Get the API ID at [coingecko](https://www.coingecko.com/en)', \
            inline=False))


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
                    await ctx.channel.send(embed=getEmbed(\
                        name='DEFAULT FIAT CHANGED',\
                        value=f'> Default FIAT is now {str(fiat).upper()}', \
                        inline=False))
                    await getCryptoPrices()
                    if defaultCoin != 'NULL':
                        await setcoin_function() # Updates the status of the bot if it is active
                else:
                    hereLink = 'https://support.coingecko.com/help/which-currencies-are-supported'
                    await ctx.channel.send(embed=getEmbed(\
                        name='FIAT NOT FOUND',\
                        value=f'> Check the supported currencies [here]({hereLink})', \
                        inline=False))
    else:
        await ctx.channel.send(embed=getEmbed(\
            name='YOU\'RE NOT AN ADMIN',\
            value=f'> You must be an Administrator to change the default fiat.', \
            inline=False))
    

# Function to set the custom status tracked coin
@client.command(name='setcoin', aliases=['sc', 'setc'], description=\
    'Change the coin to be tracked and displayed as the Bot status')
async def setcoin_command(ctx, arg):
    if ctx.author.guild_permissions.administrator == True:   #Checks if the user is an Administrator
        crypto = arg
        async with aiohttp.ClientSession() as session:
            async with session.get(mainURL + crypto) as r:
                # Check if token is valid
                if isCryptoSupported(crypto) or r.status == 200:
                    global defaultCoin
                    defaultCoin = arg
                    await setcoin_function()
                    await ctx.channel.send(embed=getEmbed(\
                        name='TRACKED COIN CHANGED',\
                        value=f'> "{defaultCoin}" is now being tracked', \
                        inline=False))
                else:
                    await ctx.channel.send(embed=getEmbed(\
                        name='COIN NOT FOUND',\
                        value=f'> Get the API ID at [coingecko](https://www.coingecko.com/en)', \
                        inline=False))
    else:
        await ctx.channel.send(embed=getEmbed(\
            name='YOU\'RE NOT AN ADMIN',\
            value=f'> You must be an Administrator to change the tracked coin.', \
            inline=False))


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
                value = "{:,}".format(getPrice(coin))
                print(coin)
                print(fiat)
                await ctx.channel.send(embed=getEmbed(\
                    name=f'THE PRICE OF {crypto.upper()}:',\
                    value=f'> {value} {fiat.upper()}', \
                    inline=False))
            else:
                await ctx.channel.send(embed=getEmbed(\
                    name='COIN NOT FOUND',\
                    value=f'> get the API ID at [coingecko](https://www.coingecko.com/en)', \
                    inline=False))


@client.command(name='help', aliases=['h'])
async def help_command(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange()
    )
    embed.set_author(name='Crypto Bot Commands')
    embed.add_field(name='Instruction',value=f'> 1. Go to [coingecko](https://www.coingecko.com/en) \n \
        > 2. Select a coin\n \
        > 3. Copy the API id located below the Info \n \
        > Sample API id: `smooth-love-potion`, `bitcoin`, `binancecoin` \n \
        > Sample use case: `{get_prefix(client, ctx)}setcoin smooth-love-potion`')
    embed.add_field(name='setprefix <prefix>', value='> Set the new bot prefix \n \
        > aliases: `setprefix`, `sp`, `supp`', inline=False)
    embed.add_field(name='setcoin <API ID>', value='> Set the coin to be tracked. Needs Administrator role. \n \
        > aliases: `setcoin`, `sc`, `setc`', inline=False)
    embed.add_field(name='setfiat <API ID>', value='> Set the coin to fiat conversion currency. Needs Administrator role.\n \
        > aliases: `setfiat`, `sf`, `setf`', inline=False)
    embed.add_field(name='priceof <API ID>', value='> Check the price of a specific coin using the API ID \n \
        > aliases: `priceof`, `po`, `price`', inline=False)
    embed.add_field(name='support <API ID>', value='> Check if the coin is supported \n \
        > aliases: `support`, `s`, `supp`', inline=False)
    await ctx.channel.send(embed=embed)


getCryptoPrices.start()
client.run(os.getenv("BOT_TOKEN"))  # Running/Activating the Bot
