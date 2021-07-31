import discord
from discord.ext import commands
import os
import pymongo
import sleeper_wrapper
if os.path.exists("env.py"):
    import env


TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="$help"))


@bot.event
async def on_guild_join(ctx):
    await ctx.send('Happy to be here! Please run the add-league command to set your Sleeper Fantasy Football league!')


@bot.command(name='add-league', help='Adds league associated to this guild ID.')
async def add_league(ctx, league: str):
    if ctx.author.guild_permissions.administrator:
        existing_league = MONGO.servers.find_one(
                {"server": ctx.message.guild.id})
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


bot.run(TOKEN)