# Import needed libraries

import discord
from discord.ext import commands
from discord.utils import find
import os
import pymongo
import sleeper_wrapper
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
import functions
import scheduled_jobs
import requests
from bs4 import BeautifulSoup as bs4
if os.path.exists("env.py"):
    import env


# Define Environment Variables

TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Define Bot and Bot Prefix/Remove Default Help

bot = commands.Bot(command_prefix=functions.get_prefix)
bot.remove_command("help")


# Bot Events

## On Ready - Rich Presence / Schedule Jobs

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="$help"))
    scheduler = AsyncIOScheduler(timezone='America/New_York')
    trigger_one = OrTrigger([
        CronTrigger(day_of_week='thu', hour=15)
    ])
    trigger_two = OrTrigger([
        CronTrigger(hour=4)
    ])
    trigger_three = OrTrigger([
        CronTrigger(day_of_week='tue', hour=12)
    ])
    scheduler.add_job(scheduled_jobs.get_current_matchups, trigger_one, [bot], misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.refresh_players, trigger_two, misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.get_current_scoreboard, trigger_three, [bot], misfire_grace_time=None)
    scheduler.start()


## On Guild Join - Message

@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Happy to be here! Please run the add-league, set-channel, and set-score-type commands to finish setting up!')


## On Guild Leave - Remove Prefix and Server Info from DB

@bot.event
async def on_guild_remove(guild):
    existing_league = MONGO.servers.find_one(
                {"server": str(guild.id)})
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(guild.id)})
    if existing_league:
        MONGO.servers.delete_one(
            {"server": str(guild.id)})
    else:
        pass
    if existing_prefix:
        MONGO.prefixes.delete_one(
            {"server": str(guild.id)})
    else:
        pass
    MONGO_CONN.close()


# Bot Commands

## Setup Cog

class Setup(commands.Cog, name='Setup'):

    def __init__(self, bot):
        self.bot = bot

    ### Set Custom Prefix

    @commands.command(name='set-prefix')
    async def set_prefix(self, ctx, prefix: str):
        if ctx.author.guild_permissions.administrator:
            existing_prefix = MONGO.prefixes.find_one(
                    {"server": str(ctx.message.guild.id)})
            if existing_prefix:
                newvalue = {"$set": {"prefix": prefix}}
                MONGO.prefixes.update_one(existing_prefix, newvalue)
                MONGO_CONN.close()
                embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
                await ctx.send(embed=embed)
            else:
                server_prefix_object = {
                    "server": str(ctx.message.guild.id),
                    "prefix": prefix
                }
                MONGO.prefixes.insert_one(server_prefix_object)
                MONGO_CONN.close()
                embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set Channel to Send Timed Messages in

    @commands.command(name='set-channel')
    async def set_channel(self, ctx, channel_id: str):
        if ctx.author.guild_permissions.administrator:
            if channel_id.isnumeric():
                count = 0
                found = 0
                for channel in ctx.message.guild.channels:
                    count = count + 1
                    if isinstance(channel, discord.channel.TextChannel):
                        if str(channel.id) == str(channel_id):
                            found = 1
                            existing_channel = MONGO.servers.find_one(
                                    {"server": str(ctx.message.guild.id)})
                            if existing_channel:
                                newvalue = {"$set": {"channel": str(channel_id)}}
                                MONGO.servers.update_one(existing_channel, newvalue)
                                MONGO_CONN.close()
                                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                                await ctx.send(embed=embed)
                                break
                            else:
                                server_channel_object = {
                                    "server": str(ctx.message.guild.id),
                                    "channel": channel_id
                                }
                                MONGO.servers.insert_one(server_channel_object)
                                MONGO_CONN.close()
                                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                                await ctx.send(embed=embed)
                                break
                        elif count == len(ctx.message.guild.channels):
                            if found == 0:
                                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
                                await ctx.send(embed=embed)
                            else:
                                pass
                        else:
                            continue
                    elif count == len(ctx.message.guild.channels):
                        embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
                        await ctx.send(embed=embed)
                    else:
                        continue
            else:
                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set League ID in MongoDB

    @commands.command(name='add-league')
    async def add_league(self, ctx, league_id: str):
        if ctx.author.guild_permissions.administrator:
            if league_id.isnumeric():
                league = sleeper_wrapper.League(int(league_id)).get_league()
                if hasattr(league, 'response'):
                    embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id', False, ctx)
                    await ctx.send(embed=embed)  
                else:
                    existing_league = functions.get_existing_league(ctx)
                    if existing_league:
                        newvalue = {"$set": {"league": league_id}}
                        MONGO.servers.update_one(existing_league, newvalue)
                        MONGO_CONN.close()
                        embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)
                        await ctx.send(embed=embed) 
                    else:
                        server_league_object = {
                            "server": str(ctx.message.guild.id),
                            "league": league_id
                        }
                        MONGO.servers.insert_one(server_league_object)
                        MONGO_CONN.close()
                        embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)
                        await ctx.send(embed=embed)
            else:
                embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id', False, ctx)
                await ctx.send(embed=embed)    
        else:
            embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set Score Type in MongoDB

    @commands.command(name='set-score-type')
    async def set_score_type(self, ctx, score_type: str):
        if ctx.author.guild_permissions.administrator:
            if score_type == 'pts_ppr' or score_type == 'pts_half_ppr' or score_type == 'pts_std': 
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    if score_type == 'pts_ppr':
                        score_type_output = 'PPR'
                    elif score_type == 'pts_half_ppr':
                        score_type_output = 'Half PPR'
                    else:
                       score_type_output = 'Standard' 
                    newvalue = {"$set": {"score_type": score_type}}
                    MONGO.servers.update_one(existing_league, newvalue)
                    MONGO_CONN.close()
                    embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type_output}!', False, ctx)
                    await ctx.send(embed=embed)
                else:
                    if score_type == 'pts_ppr':
                        score_type_output = 'PPR'
                    elif score_type == 'pts_half_ppr':
                        score_type_output = 'Half PPR'
                    else:
                       score_type_output = 'Standard' 
                    score_type_object = {
                        "server": str(ctx.message.guild.id),
                        "score_type": score_type
                    }
                    MONGO.servers.insert_one(score_type_object)
                    MONGO_CONN.close()
                    embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type_output}!', False, ctx)
                    await ctx.send(embed=embed)
            else:
                await ctx.send('Invalid score_type argument. Please use either pts_std, pts_ppr, or pts_half_ppr.')
        else:
            embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', 'You do not have access to this command.', False, ctx)
            await ctx.send(embed=embed)



## League Cog

class League(commands.Cog, name='League'):

    def __init__(self, bot):
        self.bot = bot


    ### Get League Name and Member Info

    @commands.command(name='my-league')
    async def my_league_members(self, ctx):
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if "league" in existing_league:
                league_id = existing_league["league"]
                league = sleeper_wrapper.League(int(league_id)).get_league()
                users_object = sleeper_wrapper.League(int(league_id)).get_users()
                users = []
                for user in users_object:
                    users.append(user["display_name"])
                embed = functions.my_embed('Sleeper League Info', 'Sleeper League General Information', discord.Colour.blue(), 'Name', f'[{league["name"]}](https://sleeper.app/leagues/{league_id})', False, ctx)
                embed.add_field(name='Members', value=", ".join(users), inline=False)
                embed.add_field(name='Quantity', value=len(users), inline=False)
                embed.add_field(name='Trade Deadline', value=f"Week {league['settings']['trade_deadline']}", inline=False)
                embed.add_field(name='Playoffs Start', value=f"Week {league['settings']['playoff_week_start']}", inline=False)
                if "score_type" in existing_league:
                    if existing_league["score_type"] == 'pts_ppr':
                        embed.add_field(name='Scoring Type', value='PPR', inline=False)
                    elif existing_league["score_type"] == 'pts_half_ppr':
                        embed.add_field(name='Scoring Type', value='Half PPR', inline=False)
                    elif existing_league["score_type"] == 'pts_std':
                        embed.add_field(name='Scoring Type', value='Standard', inline=False)
                else:
                    pass
                await ctx.send(embed=embed)
            else:
                embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, ctx)
            await ctx.send(embed=embed)


    ### Get League Standings Sorted by Most to Least Wins

    @commands.command(name='my-league-standings')
    async def my_league_standings(self, ctx):
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if "league" in existing_league:
                league_id = existing_league["league"]
                users_object = sleeper_wrapper.League(int(league_id)).get_users()
                rosters_object = sleeper_wrapper.League(int(league_id)).get_rosters()
                filtered_roster_object = []
                for roster in rosters_object:
                    if roster["owner_id"] != None:
                        filtered_roster_object.append(roster)
                    else:
                        pass
                standings_object = sleeper_wrapper.League(int(league_id)).get_standings(filtered_roster_object, users_object)
                standings_string = ''
                count = 0
                for i in standings_object:
                    count = count + 1
                    standings_string += f'{str(count)}. {i[0]} / Record: {i[1]}-{i[2]} / Points For: {i[3]}\n'
                embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', standings_string, False, ctx)
                await ctx.send(embed=embed)
            else:
                embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', 'No league specified, run add-league command to complete setup.', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', 'No league specified, run add-league command to complete setup.', False, ctx)
            await ctx.send(embed=embed)

    
    ### Get Current Week Matchups

    @commands.command(name='my-league-matchups')
    async def my_league_matchups(self, ctx, week: str):
        if week.isnumeric():
            if int(week) <= 18 and int(week) >= 1:
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(int(week))
                        if matchups:
                            sorted_matchups = sorted(matchups, key=lambda i: i["matchup_id"])
                            matchups_string = ''
                            count = 0
                            matchup_count = 1
                            for matchup in sorted_matchups:
                                count = count + 1
                                roster = next((roster for roster in rosters if roster["roster_id"] == matchup["roster_id"]), None)
                                user = next((user for user in users if user["user_id"] == roster["owner_id"]), None)
                                if (count % 2) == 0:
                                    matchup_count = matchup_count + 1
                                    matchups_string += f'{user["display_name"]}\n'
                                else:
                                    matchups_string += f'{str(matchup_count)}. {user["display_name"]} vs. '
                            embed = functions.my_embed('Current Week Matchups', f'Matchups for Week {week}', discord.Colour.blue(), 'Matchups', matchups_string, False, ctx)
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send('There are no matchups this week, try this command again during the season!')
                    else:
                        await ctx.send('Please run add-league command, no Sleeper League connected.')
                else:
                    await ctx.send('Please run add-league command, no Sleeper League connected.')
            else:
                await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')
        else:
            await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')

    
    ### Get Current Week Scoreboard

    @commands.command(name='my-league-scoreboard')
    async def my_league_scoreboard(self, ctx, week: str):
        if week.isnumeric():
            if int(week) <= 18 and int(week) >= 1:
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(int(week))
                        if matchups:
                            sorted_matchups = sorted(matchups, key=lambda i: i["matchup_id"])
                            scoreboard_string = ''
                            count = 0
                            matchup_count = 1
                            for matchup in sorted_matchups:
                                count = count + 1
                                roster = next((roster for roster in rosters if roster["roster_id"] == matchup["roster_id"]), None)
                                user = next((user for user in users if user["user_id"] == roster["owner_id"]), None)
                                if (count % 2) == 0:
                                    matchup_count = matchup_count + 1
                                    scoreboard_string += f'{user["display_name"]} - {matchup["points"]}\n'
                                else:
                                    scoreboard_string += f'{str(matchup_count)}. {user["display_name"]} - {matchup["points"]} / '
                            embed = functions.my_embed(f'Week {week} Scoreboard', f'Scoreboard for Week {str(week)}', discord.Colour.blue(), 'Scoreboard', scoreboard_string, False, ctx)
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send('There are no matchups this week, try this command again during the season!')
                    else:
                        await ctx.send('Please run add-league command, no Sleeper League connected.')
                else:
                    await ctx.send('Please run add-league command, no Sleeper League connected.')
            else:
                await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')
        else:
            await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')



## Players Cog

class Players(commands.Cog, name='Players'):

    def __init__(self, bot):
        self.bot = bot


    ### Get Trending Players

    @commands.command(name='trending-players')
    async def trending_players(self, ctx, add_drop: str):
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
                MONGO_CONN.close()
                if db_player["team"]:
                    team = db_player["team"]
                else:
                    team = 'None'
                if add_drop == 'add':
                    trending_string += f'{str(count)}. {db_player["name"]} {db_player["position"]} - {team} +{str(change)}\n'
                else:
                    trending_string += f'{str(count)}. {db_player["name"]} {db_player["position"]} - {team} -{str(change)}\n'
            if add_drop == 'add':
                embed = functions.my_embed('Trending Players', 'Display Current Trending Added Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
                await ctx.send(embed=embed)
            else:   
                embed = functions.my_embed('Trending Players', 'Display Current Trending Dropped Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
                await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid add_drop argument. Please use either add or drop to get trending players.')  

    
    ### Get Roster of Team in Your League

    @commands.command(name='roster')
    async def roster(self, ctx, username: str, roster_portion: str):
        if roster_portion == 'starters' or roster_portion == 'bench' or roster_portion == 'all':
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if "league" in existing_league:
                    league_id = existing_league["league"]
                    users = sleeper_wrapper.League(int(league_id)).get_users()
                    rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                    count = 0
                    for i in users:
                        count = count + 1
                        if i["display_name"] == username:
                            user = i
                            break
                        else:
                            if count == len(users):
                                user = False
                            else:
                                continue
                    if user:
                        for roster in rosters:
                            if roster["owner_id"] == user["user_id"]:
                                users_roster = roster
                                break
                            else:
                                continue
                        if roster_portion == 'starters':
                            starters_string = ''
                            res = all(i == '0' for i in users_roster["starters"])
                            if res == True:
                                starters_string += 'None\n'
                            else:
                                for i in users_roster["starters"]:
                                    if i == '0':
                                        starters_string += 'None\n'
                                    else:
                                        player = MONGO.players.find_one({'id': i})
                                        starters_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                            MONGO_CONN.close()
                            embed = functions.my_embed('Roster', f'Starting Roster for {user["display_name"]}', discord.Colour.blue(), 'Starting Roster', starters_string, False, ctx)
                            await ctx.send(embed=embed)
                        if roster_portion == 'all':
                            players_string = ''
                            try:
                                if len(users_roster["players"]) != 0:
                                    for i in users_roster["players"]:
                                        if i == '0':
                                            players_string += 'None\n'
                                        else:
                                            player = MONGO.players.find_one({'id': i})
                                            players_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed('Roster', f'Complete Roster for {user["display_name"]}', discord.Colour.blue(), 'Full Roster', players_string, False, ctx)
                                    await ctx.send(embed=embed)
                                else:
                                    players_string = 'None'
                                    embed = functions.my_embed('Roster', f'Complete Roster for {user["display_name"]}', discord.Colour.blue(), 'Full Roster', players_string, False, ctx)
                                    await ctx.send(embed=embed)
                            except:
                                if users_roster["players"] != None:
                                    for i in users_roster["players"]:
                                        if i == '0':
                                            players_string += 'None\n'
                                        else:
                                            player = MONGO.players.find_one({'id': i})
                                            players_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed('Roster', f'Complete Roster for {user["display_name"]}', discord.Colour.blue(), 'Full Roster', players_string, False, ctx)
                                    await ctx.send(embed=embed)
                                else:
                                    players_string = 'None'
                                    embed = functions.my_embed('Roster', f'Complete Roster for {user["display_name"]}', discord.Colour.blue(), 'Full Roster', players_string, False, ctx)
                                    await ctx.send(embed=embed)
                        if roster_portion == 'bench':
                            bench_string = ''
                            try:
                                if len(users_roster["players"]) != 0:
                                    bench_roster = list(set(users_roster["players"]).difference(users_roster["starters"]))
                                    for i in bench_roster:
                                        if i == '0':
                                            bench_string += 'None\n'
                                        else:
                                            player = MONGO.players.find_one({'id': i})
                                            bench_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed('Roster', f'Bench for {user["display_name"]}', discord.Colour.blue(), 'Bench', bench_string, False, ctx)
                                    await ctx.send(embed=embed)
                                else:
                                    bench_string = 'None'
                                    embed = functions.my_embed('Roster', f'Bench for {user["display_name"]}', discord.Colour.blue(), 'Bench', bench_string, False, ctx)
                                    await ctx.send(embed=embed)
                            except:
                                if users_roster["players"] != None:
                                    bench_roster = list(set(users_roster["players"]).difference(users_roster["starters"]))
                                    for i in bench_roster:
                                        if i == '0':
                                            bench_string += 'None\n'
                                        else:
                                            player = MONGO.players.find_one({'id': i})
                                            bench_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed('Roster', f'Bench for {user["display_name"]}', discord.Colour.blue(), 'Bench', bench_string, False, ctx)
                                    await ctx.send(embed=embed)
                                else:
                                    bench_string = 'None'
                                    embed = functions.my_embed('Roster', f'Bench for {user["display_name"]}', discord.Colour.blue(), 'Bench', bench_string, False, ctx)
                                    await ctx.send(embed=embed)
                    else:
                        await ctx.send('Invalid username. Double check for any typos and try again.')
                else:
                    await ctx.send('Please run add-league command, no Sleeper League connected.')
            else:
                await ctx.send('Please run add-league command, no Sleeper League connected.')
        else:
            await ctx.send('Invalid roster_portion argument. Please use starters, bench, or all.')


    ### Get the Roster, Injury, and Depth Chart Status of a Particular Player
            
    @commands.command(name='status')
    async def status(self, ctx, *args):
        if len(args) == 3:
            existing_player = functions.get_existing_player(args)
            if existing_player:
                embed = functions.my_embed('Status', f'Roster, Injury, and Depth Chart Status for {args[0]} {args[1]} - {args[2]}', discord.Colour.blue(), 'Roster Status', existing_player["status"], False, ctx)
                embed.add_field(name='Depth Chart Order', value=existing_player["depth_chart_order"], inline=False)
                embed.add_field(name='Injury Status', value=existing_player["injury_status"], inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send('No player found with those specifications, please try again!')
        else:
            await ctx.send('Invalid arguments provided. Please use the following format: status <first name> <last name> <team abbreviation in caps>')


    ### See Who Has a Particular Player

    @commands.command(name='who-has')
    async def who_has(self, ctx, *args):
        if len(args) == 3:
            existing_player = functions.get_existing_player(args)
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if "league" in existing_league:
                    if existing_player:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        count = 0
                        found = False
                        for roster in rosters:
                            count = count + 1
                            if roster["players"] != None:
                                for player in roster["players"]:
                                    if player == existing_player["id"]:
                                        for user in users:
                                            if user["user_id"] == roster["owner_id"]:
                                                embed = functions.my_embed('Who Has...', f'Command to find who currently has a particular player on their roster.', discord.Colour.blue(), f'Owner of {args[0]} {args[1]}', user["display_name"], False, ctx)
                                                await ctx.send(embed=embed)
                                                found = True
                                                break
                                            else:
                                                pass
                                    else:
                                        pass
                                if count == len(rosters):
                                    if found == True:
                                        pass
                                    else:
                                        embed = functions.my_embed('Who Has...', f'Command to find who currently has a particular player on their roster.', discord.Colour.blue(), f'Owner of {args[0]} {args[1]}', 'None', False, ctx)
                                        await ctx.send(embed=embed)
                                        break
                                else:
                                    continue
                            else:
                                if count == len(rosters):
                                    embed = functions.my_embed('Who Has...', f'Command to find who currently has a particular player on their roster.', discord.Colour.blue(), f'Owner of {args[0]} {args[1]}', 'None', False, ctx)
                                    await ctx.send(embed=embed)
                                    break
                                else:
                                    continue
                    else:
                        await ctx.send('No player found with those parameters, please try again!')
                else:
                    await ctx.send('Please run add-league command, no Sleeper League connected.')
            else:
                await ctx.send('Please run add-league command, no Sleeper League connected.')
        else:
            await ctx.send('Invalid arguments provided. Please use the following format: who-has <first name> <last name> <team abbreviation in caps>')



## Weather Cog

class Weather(commands.Cog, name='Weather'):

    def __init__(self, bot):
        self.bot = bot

    
    ### Get Local Forecast

    @commands.command(name='forecast')
    async def forecast(self, ctx, *city: str):
        weather_api_key = os.environ.get("WEATHER_API_KEY")
        forecast = requests.get(
            'http://api.weatherapi.com/v1/forecast.json',
            params= {
                'key': weather_api_key,
                'q': city,
                'days': 3
            }
        )
        if forecast.status_code == 200:
            forecast_string=''
            tuple_test = type(city) is tuple
            if tuple_test:
                city_string = ''
                for word in city:
                    city_string += f'{word} '
                city = city_string
            else:
                pass
            for day in forecast.json()["forecast"]["forecastday"]:
                forecast_string += f'{day["date"]}:\nHigh: {day["day"]["maxtemp_f"]} degrees F\nLow: {day["day"]["mintemp_f"]} degrees F\nWind: {day["day"]["maxwind_mph"]} mph\nPrecipitation Amount: {day["day"]["totalprecip_in"]} in.\nHumidity: {day["day"]["avghumidity"]}%\nChance of Rain: {day["day"]["daily_chance_of_rain"]}%\nChance of Snow: {day["day"]["daily_chance_of_snow"]}%\nGeneral Conditions: {day["day"]["condition"]["text"]}\n\n'
            embed = functions.my_embed('Weather Forecast', f'3 day forecast for {forecast.json()["location"]["name"]}, {forecast.json()["location"]["region"]}', discord.Colour.blue(), f'Forecast for {city}', forecast_string, False, ctx)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid city name or zip code, please try again!')


    ### Get Current Weather

    @commands.command(name='current-weather')
    async def current_weather(self, ctx, *city: str):
        weather_api_key = os.environ.get("WEATHER_API_KEY")
        current_weather = requests.get(
            'http://api.weatherapi.com/v1/current.json',
            params= {
                'key': weather_api_key,
                'q': city
            }
        )
        if current_weather.status_code == 200:
            tuple_test = type(city) is tuple
            if tuple_test:
                city_string = ''
                for word in city:
                    city_string += f'{word} '
                city = city_string
            else:
                pass
            current_weather_string = f'Local Time: {current_weather.json()["location"]["localtime"]}\nTemperature: {current_weather.json()["current"]["temp_f"]} degrees F\nFeels like: {current_weather.json()["current"]["feelslike_f"]} degrees F\nCurrent condition: {current_weather.json()["current"]["condition"]["text"]}\nWind: {current_weather.json()["current"]["wind_mph"]} mph\nWind Direction: {current_weather.json()["current"]["wind_dir"]}\nGust Speed: {current_weather.json()["current"]["gust_mph"]} mph\nHumidity: {current_weather.json()["current"]["humidity"]}%\n'
            embed = functions.my_embed('Current Weather', f'Current weather for {current_weather.json()["location"]["name"]}, {current_weather.json()["location"]["region"]}', discord.Colour.blue(), f'Current Weather for {city}', current_weather_string, False, ctx)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid city name or zip code, please try again!')



## Manage Cog

class Manage(commands.Cog, name='Manage'):

    def __init__(self, bot):
        self.bot = bot


    ### Kick Command

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if ctx.author.guild_permissions.administrator:
            await user.kick(reason=reason)
            await ctx.send(f"{user} has been ousted for being sassy!")
        else:
            await ctx.send('You do not have access to this command.')
    

    ### Ban Command

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        if ctx.author.guild_permissions.administrator:
            await user.ban(reason=reason)
            await ctx.send(f"{user} has been exiled for treason!")
        else:
            await ctx.send('You do not have access to this command.')


    ###Unban Command

    @commands.command(name='unban')
    async def unban(self, ctx, *, member):
        if ctx.author.guild_permissions.administrator:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f"{user} has been welcomed back! Shower them with gifts!")
        else:
            await ctx.send('You do not have access to this command.')



## Patron Cog

class Patron(commands.Cog, name='Patron'):

    def __init__(self, bot):
        self.bot = bot


    ### Starter Fantasy Points Command

    @commands.command(name='starter-fantasy-points')
    async def starter_fantasy_points(self, ctx, *args):
        if len(args) == 4:
            if args[3].isnumeric():
                if int(args[3]) <= 18 and int(args[3]) >= 1:
                    existing_league = functions.get_existing_league(ctx)
                    if existing_league:
                        if "patron" in existing_league:
                            if existing_league["patron"] == "1":
                                if "league" in existing_league:
                                    league_id = existing_league["league"]
                                    matchups = sleeper_wrapper.League(int(league_id)).get_matchups(int(args[3]))
                                    existing_player = functions.get_existing_player(args)
                                    if existing_player:
                                        if matchups:
                                            fantasy_points = ''
                                            count = 0
                                            found = 0
                                            for matchup in matchups:
                                                count = count + 1
                                                starters_points = zip(matchup["starters"], matchup["starters_points"])
                                                for point in starters_points:
                                                    if point[0] == existing_player["id"]:
                                                        fantasy_points += str(point[1])
                                                        found = 1
                                                        break
                                                    else:
                                                        pass
                                            if found == 1:
                                                embed = functions.my_embed('Starter Fantasy Points', f'Returns the points scored by a starting player for a specific week. Only available for players who started during said week.', discord.Colour.blue(), f'Fantasy Points for {args[0]} {args[1]} for Week {args[3]}', fantasy_points, False, ctx)
                                                await ctx.send(embed=embed)
                                            else:
                                                await ctx.send('No starters were found with this information. Please try again!')
                                        else:
                                            await ctx.send('There are no matchups this week, try this command again during the season!')
                                    else:
                                        await ctx.send('No players are found with these parameters, please try again!')
                                else:
                                    await ctx.send('Please run add-league command, no Sleeper League connected.')
                            else:
                                await ctx.send('You do not have access to this command, it is reserved for patrons only!')
                        else:
                            await ctx.send('You do not have access to this command, it is reserved for patrons only!')    
                    else:
                        await ctx.send('Please run add-league command, no Sleeper League connected.')
                else:
                    await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')
            else:
                await ctx.send('Invalid week number given. Choose a valid week between 1 and 18.')
        else:
            await ctx.send('Invalid arguments. Please use the format [prefix]starter-fantasy-points [first name] [last name] [team abbreviation] [week]')


    ### Game Stats Command

    @commands.command(name='game-stats')
    async def game_stats(self, ctx, *args):
        if len(args) == 5:
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if "patron" in existing_league:
                    if existing_league["patron"] == "1":
                        existing_player = functions.get_existing_player(args)
                        if existing_player:
                            if "espn_id" in existing_player:
                                res = requests.get(
                                    f'https://www.espn.com/nfl/player/gamelog/_/id/{existing_player["espn_id"]}/type/nfl/year/{args[3]}'
                                )
                                soup = bs4(res.text, 'html.parser')
                                search_data = soup.find_all('tr')
                                game_data = None
                                for tr in search_data:
                                    row_split = str(tr).split('<td class="Table__TD">')
                                    try:
                                        row_split_two = row_split[1].split(" ")
                                    except:
                                        continue
                                    try:
                                        row_split_three = row_split_two[1].split("</td>")
                                    except:
                                        continue
                                    if row_split_three[0] == args[4]:
                                        game_data = tr
                                    else:
                                        continue
                                if game_data == None:
                                    await ctx.send(f'Looks like {args[0]} {args[1]} did not play on the date specified, please try again!')
                                else:
                                    game_data_split = str(game_data).split('<td class="Table__TD">')
                                    if existing_player["position"] == "QB":
                                        cmp = game_data_split[4].split("</td>")[0]
                                        att = game_data_split[5].split("</td>")[0]
                                        pass_yds = game_data_split[6].split("</td>")[0]
                                        cmp_pct = game_data_split[7].split("</td>")[0]
                                        ypa = game_data_split[8].split("</td>")[0]
                                        pass_td = game_data_split[9].split("</td>")[0]
                                        int = game_data_split[10].split("</td>")[0]
                                        long = game_data_split[11].split("</td>")[0]
                                        sack = game_data_split[12].split("</td>")[0]
                                        rating = game_data_split[13].split("</td>")[0]
                                        qbr = game_data_split[14].split("</td>")[0]
                                        rush_att = game_data_split[15].split("</td>")[0]
                                        rush_yds = game_data_split[16].split("</td>")[0]
                                        rush_avg = game_data_split[17].split("</td>")[0]
                                        rush_td = game_data_split[18].split("</td>")[0]
                                        rush_long = game_data_split[19].split("</td>")[0]
                                        game_data_string = f'{cmp}/{att} ({cmp_pct}%), {pass_yds} yards, {ypa} yards per att, {pass_td} TD, {int} INT, {long} long, {sack} sacks, {rating} rating, {qbr} QBR\n\n{rush_att} rush att, {rush_yds} rush yards, {rush_avg} per carry, {rush_td} TD, {rush_long} long'
                                        embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and date.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for {args[4]}/{args[3]}', game_data_string, False, ctx)
                                        await ctx.send(embed=embed)
                                    elif existing_player["position"] == "RB":
                                        rush_att = game_data_split[4].split("</td>")[0]
                                        rush_yds = game_data_split[5].split("</td>")[0]
                                        rush_avg = game_data_split[6].split("</td>")[0]
                                        rush_td = game_data_split[7].split("</td>")[0]
                                        rush_long = game_data_split[8].split("</td>")[0]
                                        rec = game_data_split[9].split("</td>")[0]
                                        tgts = game_data_split[10].split("</td>")[0]
                                        rec_yds = game_data_split[11].split("</td>")[0]
                                        rec_avg = game_data_split[12].split("</td>")[0]
                                        rec_td = game_data_split[13].split("</td>")[0]
                                        rec_long = game_data_split[14].split("</td>")[0]
                                        fum = game_data_split[15].split("</td>")[0]
                                        lost_fum = game_data_split[16].split("</td>")[0]
                                        game_data_string = f'{rush_att} rush att, {rush_yds} rush yards, {rush_avg} per carry, {rush_td} TD, {rush_long} long\n\n{rec} rec, {tgts} targets, {rec_yds} yards, {rec_avg} per catch, {rec_td} TD, {rec_long} long\n\n{fum} fum, {lost_fum} lost'
                                        embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and date.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for {args[4]}/{args[3]}', game_data_string, False, ctx)
                                        await ctx.send(embed=embed)
                                    elif existing_player["position"] == "WR" or existing_player["position"] == "TE":
                                        rec = game_data_split[4].split("</td>")[0]
                                        tgts = game_data_split[5].split("</td>")[0]
                                        rec_yds = game_data_split[6].split("</td>")[0]
                                        rec_avg = game_data_split[7].split("</td>")[0]
                                        rec_td = game_data_split[8].split("</td>")[0]
                                        rec_long = game_data_split[9].split("</td>")[0]
                                        rush_att = game_data_split[10].split("</td>")[0]
                                        rush_yds = game_data_split[11].split("</td>")[0]
                                        rush_avg = game_data_split[12].split("</td>")[0]
                                        rush_long = game_data_split[13].split("</td>")[0]
                                        rush_td = game_data_split[14].split("</td>")[0]
                                        fum = game_data_split[15].split("</td>")[0]
                                        lost_fum = game_data_split[16].split("</td>")[0]
                                        game_data_string = f'{rec} rec, {tgts} targets, {rec_yds} yards, {rec_avg} per catch, {rec_td} TD, {rec_long} long\n\n{rush_att} rush att, {rush_yds} rush yards, {rush_avg} per carry, {rush_td} TD, {rush_long} long\n\n{fum} fum, {lost_fum} lost'
                                        embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and date.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for {args[4]}/{args[3]}', game_data_string, False, ctx)
                                        await ctx.send(embed=embed)
                                    elif existing_player["position"] == "K":
                                        long = game_data_split[9].split("</td>")[0]
                                        fg_pct = game_data_split[10].split("</td>")[0]
                                        fg = game_data_split[11].split("</td>")[0]
                                        avg = game_data_split[12].split("</td>")[0]
                                        xp = game_data_split[13].split("</td>")[0]
                                        pts = game_data_split[14].split("</td>")[0]
                                        game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                        embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and date.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for {args[4]}/{args[3]}', game_data_string, False, ctx)
                                        await ctx.send(embed=embed)
                                        pass
                                    else:
                                        await ctx.send('Game stats unavailable for this position, please try again!')
                            else:
                                await ctx.send('Game stats unavailable for this player, please try again!')
                        else:
                            await ctx.send('No players are found with these parameters, please try again!')
                    else:
                        await ctx.send('You do not have access to this command, it is reserved for patrons only!')  
                else:
                    await ctx.send('You do not have access to this command, it is reserved for patrons only!')    
            else:
                await ctx.send('Please run add-league command, no Sleeper League connected.')
        else:
            await ctx.send('Invalid arguments. Please use the format [prefix]game-stats [first name] [last name] [team abbreviation] [year] [date in mm/dd format]')



## Help Cog

class Help(commands.Cog, name='Help'):

    def __init__(self, bot):
        self.bot = bot


    ### Help Command

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        existing_prefix = MONGO.prefixes.find_one(
                    {"server": str(ctx.message.guild.id)})
        embed = functions.my_embed('Help', 'Use help <command> for detailed information.', discord.Colour.blue(), 'League', 'my-league, my-league-matchups, my-league-scoreboard, my-league-standings', False, ctx)
        embed.add_field(name='Players', value='trending-players, roster, status, who-has', inline=False)
        embed.add_field(name='Weather', value='forecast, current-weather', inline=False)
        embed.add_field(name='Manage', value='kick, ban, unban', inline=False)
        embed.add_field(name='Patron Only', value='starter-fantasy-points, game-stats', inline=False)
        embed.add_field(name='Setup', value='set-channel, add-league, set-score-type, set-prefix', inline=False)
        if existing_prefix:
            embed.add_field(name='Prefix', value=existing_prefix["prefix"], inline=False)
        else:
            embed.add_field(name='Prefix', value="$", inline=False)
        embed.add_field(name='Helpful Links', value="[Github](https://github.com/StoneMasons4106/sleeper-ffl-discordbot), [Top.gg](https://top.gg/bot/871087848311382086), [Patreon](https://www.patreon.com/stonemasons)", inline=False)
        MONGO_CONN.close()
        await ctx.send(embed=embed)

    
    ### My League Help

    @help.command(name="my-league")
    async def my_league(self, ctx):
        embed = functions.my_embed('My League', 'Returns information about the league such as league name, players, number of players, trade deadline, and the week that playoffs start. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>my-league', False, ctx)
        await ctx.send(embed=embed)


    ### My League Standings Help

    @help.command(name="my-league-standings")
    async def my_league_standings(self, ctx):
        embed = functions.my_embed('My League Standings', 'Returns current league standings. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>my-league-standings', False, ctx)
        await ctx.send(embed=embed)


    ### My League Matchups Help

    @help.command(name="my-league-matchups")
    async def my_league_matchups(self, ctx):
        embed = functions.my_embed('My League Matchups', 'Returns matchups for the specified week. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>my-league-matchups [week]', False, ctx)
        await ctx.send(embed=embed)


    ### My League Scoreboard Help

    @help.command(name="my-league-scoreboard")
    async def my_league_scoreboard(self, ctx):
        embed = functions.my_embed('My League Scoreboard', 'Returns scoreboard for the specified week. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>my-league-scoreboard [week]', False, ctx)
        await ctx.send(embed=embed)


    ### Trending Players Help

    @help.command(name="trending-players")
    async def trending_players(self, ctx):
        embed = functions.my_embed('Trending Players', 'Returns top 10 trending players based on add or drop rate for the past 24 hours.', discord.Colour.blue(), '**Syntax**', '<prefix>trending players [add or drop]', False, ctx)
        await ctx.send(embed=embed)


    ### Roster Help

    @help.command(name="roster")
    async def roster(self, ctx):
        embed = functions.my_embed('Roster', 'Returns the list of player on a given players roster based on parameters specified. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>roster [username] [starters, bench, or all]', False, ctx)
        await ctx.send(embed=embed)


    ### Status Help

    @help.command(name="status")
    async def status(self, ctx):
        embed = functions.my_embed('Status', 'Returns the roster, injury, and depth chart status of a specific player.', discord.Colour.blue(), '**Syntax**', '<prefix>status [first name] [last name] [team abbreviation]', False, ctx)
        await ctx.send(embed=embed)

    
    ### Who Has Help

    @help.command(name="who-has")
    async def who_has(self, ctx):
        embed = functions.my_embed('Who Has', 'Returns the owner in your league who has a specific player.', discord.Colour.blue(), '**Syntax**', '<prefix>who-has [first name] [last name] [team abbreviation]', False, ctx)
        await ctx.send(embed=embed)


    ### Forecast Help

    @help.command(name="forecast")
    async def forecast(self, ctx):
        embed = functions.my_embed('Forecast', 'Returns the 3 day forecast for a given city or zip code.', discord.Colour.blue(), '**Syntax**', '<prefix>forecast [city or zip code]', False, ctx)
        await ctx.send(embed=embed)


    ### Current Weather Help

    @help.command(name="current-weather")
    async def current_weather(self, ctx):
        embed = functions.my_embed('Current Weather', 'Returns the current weather for a given city or zip code.', discord.Colour.blue(), '**Syntax**', '<prefix>current-weather [city or zip code]', False, ctx)
        await ctx.send(embed=embed)


    ### Kick Help

    @help.command(name="kick")
    async def kick(self, ctx):
        embed = functions.my_embed('Kick', 'Kicks specified user from Discord server. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>kick @[username]', False, ctx)
        await ctx.send(embed=embed)

    
    ### Ban Help

    @help.command(name="ban")
    async def ban(self, ctx):
        embed = functions.my_embed('Ban', 'Bans specified user from Discord server. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>ban @[username]', False, ctx)
        await ctx.send(embed=embed)

    
    ### Unban Help

    @help.command(name="unban")
    async def unban(self, ctx):
        embed = functions.my_embed('Unban', 'Unbans specified user from Discord server. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>unban [username]#[number]', False, ctx)
        await ctx.send(embed=embed)


    ### Starter Fantasy Points Help

    @help.command(name="starter-fantasy-points")
    async def starter_fantasy_points(self, ctx):
        embed = functions.my_embed('Starter Fantasy Points', 'Returns fantasy points for the specified player for the specified week. Only available for starting players in a specific week due to structure of Sleeper API. Only available for Patrons. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>starter-fantasy-points [first name] [last name] [team abbreviation] [week]', False, ctx)
        await ctx.send(embed=embed)


    ### Game Stats Help

    @help.command(name="game-stats")
    async def game_stats(self, ctx):
        embed = functions.my_embed('Game Stats', 'Returns game stats for the specified player for the specified year and date. Only available for Patrons. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>game-stats [first name] [last name] [team abbreviation] [year] [date in mm/dd format]', False, ctx)
        await ctx.send(embed=embed)


    ### Add League Help

    @help.command(name="add-league")
    async def add_league(self, ctx):
        embed = functions.my_embed('Add League', 'Creates a connection in our database between your Sleeper League and your Discord Server. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>add-league [sleeper_league_id]', False, ctx)
        await ctx.send(embed=embed)


    ### Set Channel Help

    @help.command(name="set-channel")
    async def set_channel(self, ctx):
        embed = functions.my_embed('Set Channel', 'Designates a channel for your automated messages to funnel through. Restricted for administrators. See our Github for schedule of these messages.', discord.Colour.blue(), '**Syntax**', '<prefix>set-channel [discord_channel_id]', False, ctx)
        await ctx.send(embed=embed)


    ### Score Type Help

    @help.command(name="set-score-type")
    async def score_type(self, ctx):
        embed = functions.my_embed('Score Type', 'Designates the score type that your Sleeper League uses. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>score-type [pts_std, pts_half_ppr, or pts_ppr]', False, ctx)
        await ctx.send(embed=embed)


    ### Set Prefix Help

    @help.command(name="set-prefix")
    async def set_prefix(self, ctx):
        embed = functions.my_embed('Set Prefix', 'Designates the prefix you want this bot to use. Restricted for administrators.', discord.Colour.blue(), '**Syntax**', '<prefix>set-prefix [prefix]', False, ctx)
        await ctx.send(embed=embed)



# Bot Add Cogs

bot.add_cog(Setup(bot))
bot.add_cog(League(bot))
bot.add_cog(Players(bot))
bot.add_cog(Weather(bot))
bot.add_cog(Manage(bot))
bot.add_cog(Patron(bot))
bot.add_cog(Help(bot))


# Bot Run

bot.run(TOKEN)