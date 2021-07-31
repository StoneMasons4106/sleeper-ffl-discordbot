# Import needed libraries

import discord
from discord.ext import commands
import os
import pymongo
import sleeper_wrapper
if os.path.exists("env.py"):
    import env


# Define constant variables

TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Get Custom Prefixes

def get_prefix(message):
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(message.guild.id)})
    if existing_prefix:
        my_prefix = existing_prefix["prefix"]
    else:
        my_prefix = '$'
    return my_prefix


# Bot Prefix

bot = commands.Bot(command_prefix=get_prefix)


# Bot Events

## On Ready - Rich Presence

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="$help"))


## On Guild Join - Message

@bot.event
async def on_guild_join(ctx):
    await ctx.send('Happy to be here! Please run the add-league command to set your Sleeper Fantasy Football league!')


# Functions

## Get Existing Server League Object from Mongo

def get_existing_league(ctx):
    existing_league = MONGO.servers.find_one(
                {"server": str(ctx.message.guild.id)})
    return existing_league


# Bot Commands

## Set Custom Prefix

@bot.command(name='set-prefix', help='Set custom prefix per guild.')
async def set_prefix(ctx, prefix: str):
    if ctx.author.guild_permissions.administrator:
        existing_prefix = MONGO.prefixes.find_one(
                {"server": str(ctx.message.guild.id)})
        if existing_prefix:
            newvalue = {"$set": {"prefix": prefix}}
            MONGO.prefixes.update_one(existing_prefix, newvalue)
            await ctx.send('Successfully updated your prefix to '+prefix+'!')
        else:
            server_prefix_object = {
                "server": str(ctx.message.guild.id),
                "prefix": prefix
            }
            MONGO.prefixes.insert_one(server_prefix_object)
            await ctx.send('Successfully updated your prefix to '+prefix+'!')
    else:
        await ctx.send('You do not have access to this command.')


## Set League ID in MongoDB

@bot.command(name='add-league', help='Adds league associated to this guild ID.')
async def add_league(ctx, league: str):
    if ctx.author.guild_permissions.administrator:
        existing_league = get_existing_league(ctx)
        if existing_league:
            newvalue = {"$set": {"league": league}}
            MONGO.servers.update_one(existing_league, newvalue)
            await ctx.send('Successfully updated your Sleeper league to '+league+'!')
        else:
            server_league_object = {
                "server": str(ctx.message.guild.id),
                "league": league
            }
            MONGO.servers.insert_one(server_league_object)
            await ctx.send('Created your Sleeper league connection to '+league+'!')
    else:
        await ctx.send('You do not have access to this command.')


## Get League Name

@bot.command(name='my-league-name', help='Returns league name.')
async def my_league_name(ctx):
    existing_league = get_existing_league(ctx)
    if existing_league:
        league_id = existing_league["league"]
        league = sleeper_wrapper.League(int(league_id)).get_league()
        await ctx.send(league["name"])
    else:
        await ctx.send('No league ID found, run add-league command to complete setup.')


# Bot Run

bot.run(TOKEN)