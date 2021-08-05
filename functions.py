# Import needed libraries

import discord
from discord.ext import commands
import os
import pymongo
import sleeper_wrapper
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


# Define Bot and Bot Prefix

bot = commands.Bot(command_prefix=get_prefix)


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


# Get Matchups for Current Week

async def get_current_matchups():
    today = pendulum.today()
    starting_week = pendulum.datetime(constants.STARTING_YEAR, constants.STARTING_MONTH, constants.STARTING_DAY)
    week = today.diff(starting_week).in_weeks() + 1
    servers = MONGO.servers.find(
                {})
    if servers:
        for server in servers:
            league_id = server["league"]
            if league_id:
                users = sleeper_wrapper.League(int(league_id)).get_users()
                rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week)
                if matchups:
                    sorted_matchups = lambda i: i["matchup_id"]
                    matchups_string = ''
                    count = 0
                    matchup_count = 0
                    for matchup in sorted_matchups:
                        count = count + 1
                        roster = next((roster for roster in rosters if roster["roster_id"] == matchup["roster_id"]), None)
                        user = next((user for user in users if user["user_id"] == roster["owner_id"]), None)
                        if (count % 2) == 0:
                            matchup_count = matchup_count + 1
                            matchups_string += f'{user["display_name"]}\n'
                        else:
                            matchups_string += f'{str(matchup_count)}. {user["display_name"]} vs. '
                    embed = discord.Embed(title='Current Week Matchups', description=f'Matchups for Week {str(week)}', color=discord.Colour.blue())
                    embed.add_field(name='Matchups', value=matchups_string, inline=False)
                    channel = bot.get_channel(int(server["channel"]))
                    if channel:
                        await channel.send(f'Who is ready to rumble?! Here are the matchups for week {str(week)} in our league:')
                        await channel.send(embed=embed)
                    else:
                        pass
                else:
                    pass
            else:
                pass
    else:
        pass