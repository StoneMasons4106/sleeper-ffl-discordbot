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
    embed = functions.my_embed('Bot Info', 'Important notifications, helpful links, bot server and member count.', discord.Colour.blue(), 'Helpful Links', '[Github](https://github.com/StoneMasons4106/sleeper-ffl-discordbot), [Discord](https://discord.gg/4MSEK8cpfp), [Top.gg](https://top.gg/bot/871087848311382086), [Patreon](https://www.patreon.com/stonemasons)', False, bot)
    embed.add_field(name='Server Count', value=str(len(bot.guilds)), inline=False)
    count = 0
    for guild in bot.guilds:
        count = count + int(len(guild.members))
    embed.add_field(name='Member Count', value=str(count), inline=False)
    embed.add_field(name='Patron Only Commands', value='waiver-order, transactions', inline=False)
    embed.add_field(name='Interested in Donating to the Project?', value='This has been a passion project for me, but continued scalability and improvements are not always free. If you have enjoyed the bot, please donate via the Patreon link. As a thank you, you will get access to some bonus commands not available to free users.', inline=False)
    embed.add_field(name='Still Have Questions?', value='Feel free to join the community Discord and subscribe to get access to exclusive channels and faster responses to questions.', inline=False)
    return embed