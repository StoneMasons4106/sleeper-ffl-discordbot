import discord
from discord.ext import commands
from discord.utils import find
import os
import functions
import pymongo
if os.path.exists("env.py"):
    import env


MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


def help(ctx):
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(ctx.message.guild.id)})
    MONGO_CONN.close()
    embed = functions.my_embed('Help', 'Use help <command> for detailed information.', discord.Colour.blue(), 'IMPORTANT:', 'Please make sure that the bot has access to application commands under the permissions found in the Sleeper-FFL role.', False, ctx)
    embed.add_field(name='League', value='my-league, my-league-matchups, my-league-scoreboard, my-league-standings', inline=False)
    embed.add_field(name='Players', value='trending-players, roster, status, who-has', inline=False)
    embed.add_field(name='Weather', value='forecast, current-weather', inline=False)
    embed.add_field(name='Manage', value='kick, ban, unban', inline=False)
    embed.add_field(name='Patron Only', value='game-stats, waiver-order, transactions', inline=False)
    embed.add_field(name='Setup', value='set-channel, add-league, set-score-type, set-prefix', inline=False)
    if existing_prefix:
        embed.add_field(name='Prefix', value=existing_prefix["prefix"], inline=False)
    else:
        embed.add_field(name='Prefix', value="$", inline=False)
    embed.add_field(name='Helpful Links', value="[Github](https://github.com/StoneMasons4106/sleeper-ffl-discordbot), [Top.gg](https://top.gg/bot/871087848311382086), [Patreon](https://www.patreon.com/stonemasons)", inline=False)
    embed.add_field(name='Interested in Becoming a Patron for Increased Functionality?', value='Click the link to Patreon in the Helpful Links section to get started.', inline=False)
    return embed