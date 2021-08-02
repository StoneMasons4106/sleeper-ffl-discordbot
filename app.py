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

def get_prefix(bot, message):
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


## Set Embed for Discord Bot Responses

def my_embed(title, description, color, name, value, inline, ctx):
    embed = discord.Embed(title=title, description=description, color = color)
    embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    return embed


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
            embed = my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
            await ctx.send(embed=embed)
        else:
            server_prefix_object = {
                "server": str(ctx.message.guild.id),
                "prefix": prefix
            }
            MONGO.prefixes.insert_one(server_prefix_object)
            embed = my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
            await ctx.send(embed=embed)
    else:
        embed = my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'You do not have access to this command, request failed.', False, ctx)
        await ctx.send(embed=embed)


## Set League ID in MongoDB

@bot.command(name='add-league', help='Adds league associated to this guild ID.')
async def add_league(ctx, league_id: str):
    if ctx.author.guild_permissions.administrator:
        existing_league = get_existing_league(ctx)
        if existing_league:
            newvalue = {"$set": {"league": league_id}}
            MONGO.servers.update_one(existing_league, newvalue)
            embed = my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league+'!', False, ctx)
            await ctx.send(embed=embed)
        else:
            server_league_object = {
                "server": str(ctx.message.guild.id),
                "league": league_id
            }
            MONGO.servers.insert_one(server_league_object)
            embed = my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league+'!', False, ctx)
            await ctx.send(embed=embed)
    else:
        embed = my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'You do not have access to this command, request failed.', False, ctx)
        await ctx.send(embed=embed)


## Get League Name

@bot.command(name='my-league-name', help='Returns league name.')
async def my_league_name(ctx):
    existing_league = get_existing_league(ctx)
    if existing_league:
        league_id = existing_league["league"]
        league = sleeper_wrapper.League(int(league_id)).get_league()
        embed = my_embed('Sleeper League Name', 'Name of your Sleeper League', discord.Colour.blue(), 'Name', league["name"], False, ctx)
        await ctx.send(embed=embed)
    else:
        embed = my_embed('Sleeper League Name', 'Name of your Sleeper League', discord.Colour.blue(), 'Name', 'No league specified, run add-league command to complete setup.', False, ctx)
        await ctx.send(embed=embed)


## Get League Users

@bot.command(name='my-league-members', help='Returns league member display names and quantity.')
async def my_league_members(ctx):
    existing_league = get_existing_league(ctx)
    if existing_league:
        league_id = existing_league["league"]
        users_object = sleeper_wrapper.League(int(league_id)).get_users()
        users = []
        for user in users_object:
            users.append(user["display_name"])
        embed = my_embed('Sleeper League Members', 'Display Names and Quantity of Sleeper League Members', discord.Colour.blue(), 'Members', ", ".join(users), False, ctx)
        embed.add_field(name='Quantity', value=len(users))
        await ctx.send(embed=embed)
    else:
        embed = my_embed('Sleeper League Members', 'Display Names and Quantity of Sleeper League Members', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, ctx)
        await ctx.send(embed=embed)


## Get League Standings Sorted by Most to Least Wins

@bot.command(name='my-league-standings', help='Returns the current standings of my league with win loss record and points for.')
async def my_league_standings(ctx):
    existing_league = get_existing_league(ctx)
    if existing_league:
        league_id = existing_league["league"]
        users_object = sleeper_wrapper.League(int(league_id)).get_users()
        rosters_object = sleeper_wrapper.League(int(league_id)).get_rosters()
        standings_object = sleeper_wrapper.League(int(league_id)).get_standings(rosters_object, users_object)
        standings_string = ''
        count = 0
        for i in standings_object:
            count = count + 1
            standings_string += str(count) + '.' + ' ' + i[0] + ' / Record: ' + i[1] + '-' + i[2] + ' / Points For: ' + i[3] + '\n'
        embed = my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', standings_string, False, ctx)
        await ctx.send(embed=embed)
    else:
        embed = my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', 'No league specified, run add-league command to complete setup.', False, ctx)
        await ctx.send(embed=embed)


## Get Trending Players

@bot.command(name='trending-players', help='Returns the current top 10 trending players over the last 24 hours based on add or drop rate.')
async def trending_players(ctx, add_drop: str):
    if add_drop == 'add' or add_drop == 'drop':
        trending_players = sleeper_wrapper.Players().get_trending_players('nfl', add_drop, 24, 10)
        trending_string = ''
        count = 0
        for player in trending_players:
            count = count + 1
            player_id = player["player_id"]
            change = player["count"]
            db_player = MONGO.players.find_one(
                {"id": str(player_id)})
            trending_string += str(count) + '.' + ' ' + db_player["name"] + ' ' + db_player["position"] + ' - ' + db_player["team"] + ' ' + str(change) + '\n'
        if add_drop == 'add':
            embed = my_embed('Trending Players', 'Display Current Trending Added Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
            await ctx.send(embed=embed)
        else:    
            embed = my_embed('Trending Players', 'Display Current Trending Dropped Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
            await ctx.send(embed=embed)
    else:
        await ctx.send('Invalid add_drop argument. Please use either add or drop to get trending players.')
        

# Bot Run

bot.run(TOKEN)