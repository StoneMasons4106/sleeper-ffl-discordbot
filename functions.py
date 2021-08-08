# Import needed libraries

import discord
import os
import pymongo
import pendulum
import constants
if os.path.exists("env.py"):
    import env


# Define Environment Variables

MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Get Custom Prefixes

def get_prefix(bot, message):
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(message.guild.id)})
    if existing_prefix:
        my_prefix = existing_prefix["prefix"]
    else:
        my_prefix = '$'
    return my_prefix


# Get Existing Server League Object from Mongo

def get_existing_league(ctx):
    existing_league = MONGO.servers.find_one(
                {"server": str(ctx.message.guild.id)})
    return existing_league


# Set Embed for Discord Bot Responses

def my_embed(title, description, color, name, value, inline, ctx):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=ctx.me.display_name, icon_url=ctx.me.avatar_url)
    return embed


# Get Current Week

def get_current_week():
    today = pendulum.today()
    starting_week = pendulum.datetime(constants.STARTING_YEAR, constants.STARTING_MONTH, constants.STARTING_DAY)
    if starting_week.is_future():
        week = 1
    else:
        week = today.diff(starting_week).in_weeks() + 1
    return week