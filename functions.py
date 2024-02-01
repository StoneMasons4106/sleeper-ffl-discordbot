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


# Get Existing Server League Object from Mongo

def get_existing_league(message):
    existing_league = MONGO.servers.find_one(
                {"server": str(message.guild.id)})
    MONGO_CONN.close()
    return existing_league


# Get Existing Player Object from Mongo

def get_existing_player(first_name, last_name, team_abbreviation):
    existing_player = MONGO.players.find_one(
                {"name": re.compile(f'{first_name} {last_name}', re.IGNORECASE), "team": re.compile(team_abbreviation, re.IGNORECASE)})
    MONGO_CONN.close()
    return existing_player


# Get All Server Objects from Mongo

def get_all_servers():
    servers = MONGO.servers.find(
                        {})
    MONGO_CONN.close()
    return servers


# Set Embed for Discord Bot Responses

def my_embed(title, description, color, name, value, inline, bot):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name='Sleeper-FFL', icon_url=bot.user.display_avatar)
    return embed


# Get Current Week

def get_current_week():
    today = pendulum.today(tz='America/New_York')
    nfl_state = requests.get(
        'https://api.sleeper.app/v1/state/nfl'
    )
    nfl_date_list = nfl_state.json()
    starting_date = nfl_date_list["season_start_date"].split("-")
    starting_week = pendulum.datetime(int(starting_date[0]), int(starting_date[1]), int(starting_date[2]), tz='America/New_York')
    if starting_week.is_future() or nfl_date_list['season_type'] == 'pre' or nfl_date_list['season_type'] == 'post':
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
