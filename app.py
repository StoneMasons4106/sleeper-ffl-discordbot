# Import needed libraries

import discord
from discord.ext import commands
from discord.utils import find
import os
import pymongo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
import functions
import scheduled_jobs
from sleeper_bot_commands import league, setup, weather, players, help, manage, patron
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

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=functions.get_prefix, intents=intents)
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
    trigger_four = OrTrigger([
        CronTrigger(day_of_week='tue', hour=11)
    ])
    trigger_five = OrTrigger([
        CronTrigger(day_of_week='wed', hour=11)
    ])
    trigger_six = OrTrigger([
        CronTrigger(day_of_week='thu', hour=11)
    ])
    scheduler.add_job(scheduled_jobs.get_current_matchups, trigger_one, [bot], misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.refresh_players, trigger_two, misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.get_current_scoreboard, trigger_three, [bot], misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.send_waiver_clear, trigger_four, [bot], misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.send_waiver_clear, trigger_five, [bot], misfire_grace_time=None)
    scheduler.add_job(scheduled_jobs.send_waiver_clear, trigger_six, [bot], misfire_grace_time=None)
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
        message = setup.set_prefix(ctx, prefix)
        await ctx.send(embed=message)


    ### Set Channel to Send Timed Messages in

    @commands.command(name='set-channel')
    async def set_channel(self, ctx, channel_id: str):
        message = setup.set_channel(ctx, channel_id)
        await ctx.send(embed=message)


    ### Set League ID in MongoDB

    @commands.command(name='add-league')
    async def add_league(self, ctx, league_id: str):
        message = setup.add_league(ctx, league_id)
        await ctx.send(embed=message)


    ### Set Score Type in MongoDB

    @commands.command(name='set-score-type')
    async def set_score_type(self, ctx, score_type: str):
        message = setup.set_score_type(ctx, score_type)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


## League Cog

class League(commands.Cog, name='League'):

    def __init__(self, bot):
        self.bot = bot


    ### Get League Name and Member Info

    @commands.command(name='my-league')
    async def my_league(self, ctx):
        message = league.my_league(ctx)
        await ctx.send(embed=message)
    

    ### Get League Standings Sorted by Most to Least Wins

    @commands.command(name='my-league-standings')
    async def my_league_standings(self, ctx):
        message = league.my_league_standings(ctx)
        await ctx.send(embed=message)


    ### Get Current Week Matchups

    @commands.command(name='my-league-matchups')
    async def my_league_matchups(self, ctx, week: str):
        message = league.my_league_matchups(ctx, week)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


    ### Get Current Week Scoreboard

    @commands.command(name='my-league-scoreboard')
    async def my_league_scoreboard(self, ctx, week: str):
        message = league.my_league_scoreboard(ctx, week)
        if type(message) is str:
            await ctx.send(message)
        else:
            await ctx.send(embed=message)



## Players Cog

class Players(commands.Cog, name='Players'):

    def __init__(self, bot):
        self.bot = bot


    ### Get Trending Players

    @commands.command(name='trending-players')
    async def trending_players(self, ctx, add_drop: str):
        message = players.trending_players(ctx, add_drop)
        if type(message) is str:
            await ctx.send(message)
        else:
            await ctx.send(embed=message)

    
    ### Get Roster of Team in Your League

    @commands.command(name='roster')
    async def roster(self, ctx, username: str, roster_portion: str):
        message = players.roster(ctx, username, roster_portion)
        if type(message) is str:
            await ctx.send(message)
        else:
            await ctx.send(embed=message)


    ### Get the Roster, Injury, and Depth Chart Status of a Particular Player
            
    @commands.command(name='status')
    async def status(self, ctx, *args):
        message = players.status(ctx, *args)
        if type(message) is str:
            await ctx.send(message)
        else:
            await ctx.send(embed=message)


    ### See Who Has a Particular Player

    @commands.command(name='who-has')
    async def who_has(self, ctx, *args):
        message = players.who_has(ctx, *args)
        if type(message) is str:
            await ctx.send(message)
        else:
            await ctx.send(embed=message)



## Weather Cog

class Weather(commands.Cog, name='Weather'):

    def __init__(self, bot):
        self.bot = bot

    
    ### Get Local Forecast

    @commands.command(name='forecast')
    async def forecast(self, ctx, *city: str):
        message = weather.forecast(ctx, *city)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


    ### Get Current Weather

    @commands.command(name='current-weather')
    async def current_weather(self, ctx, *city: str):
        message = weather.current_weather(ctx, *city)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)



## Manage Cog

class Manage(commands.Cog, name='Manage'):

    def __init__(self, bot):
        self.bot = bot


    ### Kick Command

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        message = await manage.kick(ctx, user, reason=None)
        await ctx.send(message)
    

    ### Ban Command

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        message = await manage.ban(ctx, user, reason=reason)
        await ctx.send(message)


    ###Unban Command

    @commands.command(name='unban')
    async def unban(self, ctx, *, member):
        message = await manage.unban(ctx, member)
        await ctx.send(message)



## Patron Cog

class Patron(commands.Cog, name='Patron'):

    def __init__(self, bot):
        self.bot = bot


    ### Starter Fantasy Points Command

    @commands.command(name='starter-fantasy-points')
    async def starter_fantasy_points(self, ctx, *args):
        message = patron.starter_fantasy_points(ctx, *args)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


    ### Game Stats Command

    @commands.command(name='game-stats')
    async def game_stats(self, ctx, *args):
        message = patron.game_stats(ctx, *args)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


    ### Waiver Order Command

    @commands.command(name='waiver-order')
    async def waiver_order(self, ctx):
        message = patron.waiver_order(ctx)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)


    ### Transactions Command

    @commands.command(name='transactions')
    async def transactions(self, ctx, week: str):
        message = patron.transactions(ctx, week)
        if type(message) is str:
           await ctx.send(message)
        else: 
            await ctx.send(embed=message)



## Help Cog

class Help(commands.Cog, name='Help'):

    def __init__(self, bot):
        self.bot = bot


    ### Help Command

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        message = help.help(ctx)
        await ctx.send(embed=message)

    
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
        embed = functions.my_embed('Game Stats', 'Returns game stats for the specified player for the specified year and week. Only available for Patrons. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>game-stats [first name] [last name] [current team abbreviation] [year] [week], use <prefix>game-stats [first name] [last name] [current team abbreviation] for most current game', False, ctx)
        await ctx.send(embed=embed)

    
    ### Waiver Order Help

    @help.command(name="waiver-order")
    async def waiver_order(self, ctx):
        embed = functions.my_embed('Waiver Order', 'Returns your current waiver order. Only available for Patrons. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>waiver-order', False, ctx)
        await ctx.send(embed=embed)


    ### Transactions Help

    @help.command(name="transactions")
    async def transactions(self, ctx):
        embed = functions.my_embed('Transactions', 'Returns the last 20 transactions for any specified week. Only available for Patrons. Must run add-league command first.', discord.Colour.blue(), '**Syntax**', '<prefix>transactions [week]', False, ctx)
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