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


def help(bot):
    embed = functions.my_embed('Bot Info', 'Important notifications, helpful links, bot server and member count.', discord.Colour.blue(), 'IMPORTANT:', 'Please make sure that the bot has access to application commands under the permissions found in the Sleeper-FFL role. If you continue to experience issues, invite the bot to the server again without kicking it using the invite on Top.gg.', False, bot)
    embed.add_field(name='Server Count', value=str(len(bot.guilds)), inline=False)
    count = 0
    for guild in bot.guilds:
        count = count + int(len(guild.members))
    embed.add_field(name='Member Count', value=str(count), inline=False)
    embed.add_field(name='Patron Only Commands', value='game-stats, waiver-order, transactions', inline=False)
    embed.add_field(name='Helpful Links', value="[Github](https://github.com/StoneMasons4106/sleeper-ffl-discordbot), [Top.gg](https://top.gg/bot/871087848311382086), [Patreon](https://www.patreon.com/stonemasons)", inline=False)
    embed.add_field(name='Interested in Becoming a Patron for Increased Functionality?', value='Click the link to Patreon in the Helpful Links section to get started.', inline=False)
    embed.add_field(name='Still Have Questions?', value='Feel free to add and DM me, StoneMasons#5854.', inline=False)
    return embed