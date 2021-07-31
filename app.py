import discord
from discord.ext import commands
import os
from flask_pymongo import PyMongo
import functions
if os.path.exists("env.py"):
    import env

TOKEN = os.environ.get("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='$')


@bot.event
async def on_guild_join(ctx):
    await ctx.send('Happy to be here! Please run the add-league command to set your Sleeper Fantasy Football league!')


bot.run(TOKEN)