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
if os.path.exists("env.py"):
    import env


# Define Environment Variables

TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Define Bot and Bot Prefix

bot = commands.Bot(command_prefix=functions.get_prefix)


# Bot Events

## On Ready - Rich Presence

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="$help"))
    scheduler = AsyncIOScheduler()
    trigger_one = OrTrigger([
        CronTrigger(day_of_week='thu', hour=15)
    ])
    trigger_two = OrTrigger([
        CronTrigger(day_of_week='tue', hour=9)
    ])
    scheduler.add_job(get_current_matchups, trigger_one, misfire_grace_time=None)
    scheduler.add_job(get_current_scoreboards, trigger_two, misfire_grace_time=None)
    scheduler.start()


## On Guild Join - Message

@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Happy to be here! Please run the add-league, set-channel, and set-score-type commands to finish setting up!')


# Bot Commands

## Setup Cog

class Setup(commands.Cog, name='Setup'):

    def __init__(self, bot):
        self.bot = bot

    ### Set Custom Prefix

    @commands.command(name='set-prefix', help='Set custom prefix per guild.')
    async def set_prefix(self, ctx, prefix: str):
        if ctx.author.guild_permissions.administrator:
            existing_prefix = MONGO.prefixes.find_one(
                    {"server": str(ctx.message.guild.id)})
            if existing_prefix:
                newvalue = {"$set": {"prefix": prefix}}
                MONGO.prefixes.update_one(existing_prefix, newvalue)
                embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
                await ctx.send(embed=embed)
            else:
                server_prefix_object = {
                    "server": str(ctx.message.guild.id),
                    "prefix": prefix
                }
                MONGO.prefixes.insert_one(server_prefix_object)
                embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set Channel to Send Timed Messages in

    @commands.command(name='set-channel', help='Set channel to send timed messages in.')
    async def set_channel(self, ctx, channel_id: str):
        if ctx.author.guild_permissions.administrator:
            existing_channel = MONGO.servers.find_one(
                    {"server": str(ctx.message.guild.id)})
            if existing_channel:
                newvalue = {"$set": {"channel": str(channel_id)}}
                MONGO.servers.update_one(existing_channel, newvalue)
                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                await ctx.send(embed=embed)
            else:
                server_channel_object = {
                    "server": str(ctx.message.guild.id),
                    "channel": channel_id
                }
                MONGO.servers.insert_one(server_channel_object)
                embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set League ID in MongoDB

    @commands.command(name='add-league', help='Adds league associated to this guild ID.')
    async def add_league(self, ctx, league_id: str):
        if ctx.author.guild_permissions.administrator:
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                newvalue = {"$set": {"league": league_id}}
                MONGO.servers.update_one(existing_league, newvalue)
                embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)
                await ctx.send(embed=embed)
            else:
                server_league_object = {
                    "server": str(ctx.message.guild.id),
                    "league": league_id
                }
                MONGO.servers.insert_one(server_league_object)
                embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)
                await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'You do not have access to this command, request failed.', False, ctx)
            await ctx.send(embed=embed)


    ### Set Score Type in MongoDB

    @commands.command(name='set-score-type', help='Adds score type used in scheduled scoreboard message associated to your league.')
    async def set_score_type(self, ctx, score_type: str):
        if ctx.author.guild_permissions.administrator:
            if score_type == 'pts_ppr' or score_type == 'pts_half_ppr' or score_type == 'pts_std': 
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    newvalue = {"$set": {"score_type": score_type}}
                    MONGO.servers.update_one(existing_league, newvalue)
                    embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type}!', False, ctx)
                    await ctx.send(embed=embed)
                else:
                    score_type_object = {
                        "server": str(ctx.message.guild.id),
                        "score_type": score_type
                    }
                    MONGO.servers.insert_one(score_type_object)
                    embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type}!', False, ctx)
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

    @commands.command(name='my-league', help='Returns league name, member display names, and quantity of players.')
    async def my_league_members(self, ctx):
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            league_id = existing_league["league"]
            league = sleeper_wrapper.League(int(league_id)).get_league()
            users_object = sleeper_wrapper.League(int(league_id)).get_users()
            users = []
            for user in users_object:
                users.append(user["display_name"])
            embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Name', league["name"], False, ctx)
            embed.add_field(name='Members', value=", ".join(users), inline=False)
            embed.add_field(name='Quantity', value=len(users), inline=False)
            await ctx.send(embed=embed)
        else:
            embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, ctx)
            await ctx.send(embed=embed)


    ### Get League Standings Sorted by Most to Least Wins

    @commands.command(name='my-league-standings', help='Returns the current standings of my league with win loss record and points for.')
    async def my_league_standings(self, ctx):
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
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

    
    ### Get Current Week Matchups

    @commands.command(name='my-league-matchups', help='Returns the matchups for the current week.')
    async def my_league_matchups(self, ctx):
        week = functions.get_current_week()
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            league_id = existing_league["league"]
            if league_id:
                users = sleeper_wrapper.League(int(league_id)).get_users()
                rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
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
                    embed = functions.my_embed('Current Week Matchups', f'Matchups for Week {str(week[0])}', discord.Colour.blue(), 'Matchups', matchups_string, False, ctx)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('There are no matchups this week, try this command again during the season!')
            else:
                await ctx.send('Please run add-league command, no Sleeper League connected.')
        else:
            await ctx.send('Please run add-league command, no Sleeper League connected.')
    

    ### Get Current Week Scoreboard

    @commands.command(name='my-league-scoreboard', help='Returns the scoreboard for the current week based on score type.')
    async def my_league_scoreboard(self, ctx):
        week = functions.get_current_week()
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            league_id = existing_league["league"]
            if league_id:
                if existing_league["score_type"]:
                    users = sleeper_wrapper.League(int(league_id)).get_users()
                    rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                    matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                    scoreboard = sleeper_wrapper.League(int(league_id)).get_scoreboards(rosters, matchups, users, existing_league["score_type"], week[0])
                    if scoreboard:
                        scoreboard_string = ''
                        count = 0
                        for score in scoreboard:
                            count = count + 1
                            scoreboard_string += f'{str(count)}. {scoreboard[score][0][0]} - {str(scoreboard[score][0][1])} / {scoreboard[score][1][0]} - {str(scoreboard[score][1][1])}\n'
                        embed = functions.my_embed('Current Week Scoreboard', f'Scoreboard for Week {str(week[0])}', discord.Colour.blue(), 'Scoreboard', scoreboard_string, False, ctx)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send('There is no scoreboard this week, try this command again during the season!')
                else:
                    await ctx.send('Please run set-score-type command, no score type specified.')
            else:
                await ctx.send('Please run add-league command, no Sleeper League connected.')
        else:
            await ctx.send('Please run add-league command, no Sleeper League connected.')


## Players Cog

class Players(commands.Cog, name='Players'):

    def __init__(self, bot):
        self.bot = bot


    ### Get Trending Players

    @commands.command(name='trending-players', help='Returns the current top 10 trending players over the last 24 hours based on add or drop rate.')
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
                if db_player["team"]:
                    team = db_player["team"]
                else:
                    team = 'None'
                trending_string += f'{str(count)}. {db_player["name"]} {db_player["position"]} - {team} {str(change)}\n'
            if add_drop == 'add':
                embed = functions.my_embed('Trending Players', 'Display Current Trending Added Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
                await ctx.send(embed=embed)
            else:    
                embed = functions.my_embed('Trending Players', 'Display Current Trending Dropped Players', discord.Colour.blue(), 'Players', trending_string, False, ctx)
                await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid add_drop argument. Please use either add or drop to get trending players.')

    
    ### Get Roster of Team in Your League

    @commands.command(name='roster', help='Returns the roster, or portion of a roster, of a team in your league based on username and portion specified.')
    async def roster(self, ctx, username: str, roster_portion: str):
        if roster_portion == 'starters' or roster_portion == 'bench' or roster_portion == 'all':
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if existing_league["league"]:
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
                            for i in users_roster["starters"]:
                                if i == '0':
                                    player = 'None'
                                    starters_string += 'None\n'
                                else:
                                    player = MONGO.players.find_one({'id': i})
                                    starters_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                            embed = functions.my_embed('Roster', f'Starting Roster for {user["display_name"]}', discord.Colour.blue(), 'Starting Roster', starters_string, False, ctx)
                            await ctx.send(embed=embed)
                        if roster_portion == 'all':
                            players_string = ''
                            for i in users_roster["players"]:
                                if i == '0':
                                    player = 'None'
                                    players_string += 'None\n'
                                else:
                                    player = MONGO.players.find_one({'id': i})
                                    players_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                            embed = functions.my_embed('Roster', f'Complete Roster for {user["display_name"]}', discord.Colour.blue(), 'Full Roster', players_string, False, ctx)
                            await ctx.send(embed=embed)
                        if roster_portion == 'bench':
                            bench_string = ''
                            bench_roster = list(set(users_roster["players"]).difference(users_roster["starters"]))
                            for i in bench_roster:
                                if i == '0':
                                    player = 'None'
                                    bench_string += 'None\n'
                                else:
                                    player = MONGO.players.find_one({'id': i})
                                    bench_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
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


# Scheduled Messages

## Get Matchups for Current Week

async def get_current_matchups():
    week = functions.get_current_week()
    servers = MONGO.servers.find(
                {})
    if servers:
        if week[1] == False:
            for server in servers:
                if server["league"]:
                    league_id = server["league"]
                    users = sleeper_wrapper.League(int(league_id)).get_users()
                    rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                    matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                    if matchups:
                        channel = await bot.fetch_channel(int(server["channel"]))
                        if channel:
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
                            embed = discord.Embed(title='Current Week Matchups', description=f'Matchups for Week {str(week[0])}', color=discord.Colour.blue())
                            embed.add_field(name='Matchups', value=matchups_string, inline=False)
                            await channel.send(f'Who is ready to rumble?! Here are the matchups for week {str(week[0])} in our league:')
                            await channel.send(embed=embed)
                    else:
                        pass
                else:
                    pass
        else:
            pass
    else:
        pass


## Get Scoreboard for Current Week

async def get_current_scoreboards():
    week = functions.get_current_week()
    servers = MONGO.servers.find(
        {})
    if servers:
        if week[1] == False:
            for server in servers:
                if server["league"] and server["score_type"]:
                    score_type = server["score_type"]
                    league_id = server["league"]
                    users = sleeper_wrapper.League(int(league_id)).get_users()
                    rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                    matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                    scoreboard = sleeper_wrapper.League(int(league_id)).get_scoreboards(rosters, matchups, users, score_type, week[0])
                    if scoreboard:
                        channel = await bot.fetch_channel(int(server["channel"]))
                        if channel:
                            scoreboard_string = ''
                            count = 0
                            for score in scoreboard:
                                count = count + 1
                                scoreboard_string += f'{str(count)}. {scoreboard[score][0][0]} - {str(scoreboard[score][0][1])} / {scoreboard[score][1][0]} - {str(scoreboard[score][1][1])}\n'
                            embed = discord.Embed(title='Current Week Scoreboard', description=f'Scoreboard for Week {str(week)}', color=discord.Colour.blue())
                            embed.add_field(name='Scoreboard', value=scoreboard_string, inline=False)
                            await channel.send(f'Another week, another round of football! Here are the results for week {str(week[0])} in our league:')
                            await channel.send(embed=embed)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        else:
            pass
    else:
        pass
        

# Bot Add Cogs

bot.add_cog(Setup(bot))
bot.add_cog(League(bot))
bot.add_cog(Players(bot))

# Bot Run

bot.run(TOKEN)