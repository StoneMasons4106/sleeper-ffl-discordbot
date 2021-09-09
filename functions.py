# Import needed libraries

import discord
import os
import pymongo
import pendulum
import requests
import re
if os.path.exists("env.py"):
    import env


# Define Environment Variables

MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Get Custom Prefixes

def get_prefix(bot, message):
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(message.guild.id)})
    MONGO_CONN.close()
    if existing_prefix:
        my_prefix = existing_prefix["prefix"]
    else:
        my_prefix = '$'
    return my_prefix


# Get Existing Server League Object from Mongo

def get_existing_league(ctx):
    existing_league = MONGO.servers.find_one(
                {"server": str(ctx.message.guild.id)})
    MONGO_CONN.close()
    return existing_league


# Get Existing Player Object from Mongo

def get_existing_player(args):
    existing_player = MONGO.players.find_one(
                {"name": re.compile(f'{args[0]} {args[1]}', re.IGNORECASE), "team": re.compile(args[2], re.IGNORECASE)})
    MONGO_CONN.close()
    return existing_player


# Get All Server Objects from Mongo

def get_all_servers():
    servers = MONGO.servers.find(
                        {})
    MONGO_CONN.close()
    return servers


# Set Embed for Discord Bot Responses

def my_embed(title, description, color, name, value, inline, ctx):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=ctx.me.display_name, icon_url=ctx.me.avatar)
    return embed


# Get Current Week

def get_current_week():
    today = pendulum.today(tz='America/New_York')
    nfl_state = requests.get(
        'https://api.sleeper.app/v1/state/nfl'
    )
    nfl_date_list = nfl_state.json()["season_start_date"].split("-")
    starting_week = pendulum.datetime(int(nfl_date_list[0]), int(nfl_date_list[1]), int(nfl_date_list[2]), tz='America/New_York')
    if starting_week.is_future():
        future = True
        week = 1
    else:
        future = False
        week = today.diff(starting_week).in_weeks() + 1
    return week, future


# Check if a Server Has Patron Status

def is_patron(existing_league):
    if "patron" in existing_league:
        if existing_league["patron"] == "1":
            return True
        else:
            return False
    else:
        return False
