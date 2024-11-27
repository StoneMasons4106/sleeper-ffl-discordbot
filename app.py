# Import needed libraries

import discord
from discord import option
from discord.ext import commands
from discord.utils import find
import os
import pymongo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
import scheduled_jobs
from sleeper_bot_commands import league, setup, weather, players, help, manage, patron, user
if os.path.exists("env.py"):
    import env


# Define Environment Variables

TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Define Bot/Intents

intents = discord.Intents.default()
intents.members = True
bot = discord.AutoShardedBot(intents=intents)


# Bot Events

## On Ready - Rich Presence / Schedule Jobs

@bot.event
async def on_ready():
    print('successfully finished startup')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="slash commands"))
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

## Setup Commands

### Set Channel to Send Timed Messages in

@bot.slash_command(name='set-channel', description='Sets the channel you want to use for automated messages.')
@option("channel_id", description="Please provide the ID of the channel where you'd like to receive automated messages.")
async def set_channel(ctx, channel_id: str):
    message = setup.set_channel(ctx, bot, channel_id)
    if type(message) is str:
        await ctx.respond(message, ephemeral=True)
    else: 
        await ctx.respond(embed=message, ephemeral=True)


### Set League ID in MongoDB

@bot.slash_command(name='add-league', description='Connects your Discord server to your Sleeper league.')
@option("league_id", description="Please provide the ID of your Sleeper league to retrieve information from.")
async def add_league(ctx, league_id: str):
    message = setup.add_league(ctx, bot, league_id)
    if type(message) is str:
        await ctx.respond(message, ephemeral=True)
    else: 
        await ctx.respond(embed=message, ephemeral=True)


### Set Score Type in MongoDB

@bot.slash_command(name='set-score-type', description='Sets the score type of your specific league.')
@option("score_type", description="Please provide the scoring type that your league uses.", choices=["pts_ppr", "pts_half_ppr", "pts_std"])
async def set_score_type(ctx, score_type: str):
    message = setup.set_score_type(ctx, bot, score_type)
    if type(message) is str:
        await ctx.respond(message, ephemeral=True)
    else: 
        await ctx.respond(embed=message, ephemeral=True)



## League Commands

### Get League Name and Member Info

@bot.slash_command(name='my-league', description='Returns general league information. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
async def my_league(ctx, ephemeral: bool):
    message = league.my_league(ctx, bot)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get League Standings Sorted by Most to Least Wins

@bot.slash_command(name='my-league-standings', description='Returns current league standings. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
async def my_league_standings(ctx, ephemeral: bool):
    message = league.my_league_standings(ctx, bot)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get Current Week Matchups

@bot.slash_command(name='my-league-matchups', description='Returns matchups for a specific week. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("week", description="Please enter the week number you'd like to view matchups for.")
async def my_league_matchups(ctx, ephemeral: bool, week: str):
    message = league.my_league_matchups(ctx, bot, week)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get Current Week Scoreboard

@bot.slash_command(name='my-league-scoreboard', description='Returns the scoreboard for a specific week. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("week", description="Please enter the week number you'd like to view scores for.")
async def my_league_scoreboard(ctx, ephemeral: bool, week: str):
    message = league.my_league_scoreboard(ctx, bot, week)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else:
        await ctx.respond(embed=message, ephemeral=ephemeral)



## Players Commands

### Get Trending Players

@bot.slash_command(name='trending-players', description='Returns the top 10 trending players either in being added or dropped.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("add_drop", description="Please select whether you'd like to view players being added or dropped.", choices=["add", "drop"])
async def trending_players(ctx, ephemeral: bool, add_drop: str):
    message = players.trending_players(bot, add_drop)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else:
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get Roster of Team in Your League

@bot.slash_command(name='roster', description='Returns a portion or entirety of a roster. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("username", description="Please provide the username of the leaguemate you'd like to view the roster of.")
@option("roster_portion", description="Please select the portion of the roster you'd like to view.", choices=["starters", "bench", "all"])
async def roster(ctx, ephemeral: bool, username: str, roster_portion: str):
    message = players.roster(ctx, bot, username, roster_portion)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else:
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get the Roster, Injury, and Depth Chart Status of a Particular Player
        
@bot.slash_command(name='status', description='Returns the injury and depth chart status of a given player.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("first_name", description="Please provide the first name of the player you want to view the depth chart and injury status for.")
@option("last_name", description="Please provide the last name of the player you want to view the depth chart and injury status for.")
@option("team_abbreviation", description="Please provide the team abbreviation in all caps of the player you want to view the status of.")
async def status(ctx, ephemeral: bool, first_name: str, last_name: str, team_abbreviation: str):
    message = players.status(bot, first_name, last_name, team_abbreviation)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else:
        await ctx.respond(embed=message, ephemeral=ephemeral)


### See Who Has a Particular Player

@bot.slash_command(name='who-has', description='Returns the user who has a given player. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("first_name", description="Please provide the first name of the player you want to see the owner of.")
@option("last_name", description="Please provide the last name of the player you want to see the owner of.")
@option("team_abbreviation", description="Please provide the team abbreviation in all caps of the player you want to see the owner of.")
async def who_has(ctx, ephemeral: bool, first_name: str, last_name: str, team_abbreviation: str):
    message = players.who_has(ctx, bot, first_name, last_name, team_abbreviation)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else:
        await ctx.respond(embed=message, ephemeral=ephemeral)



## Weather Commands
    
### Get Local Forecast

@bot.slash_command(name='forecast', description='Returns the 3 day forecast for a city or zip code.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("city", description="Please provide the name of the city or zipcode that you want to view the 3 day forecast for.")
async def forecast(ctx, ephemeral: bool, city: str):
    message = weather.forecast(bot, city)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Get Current Weather

@bot.slash_command(name='current-weather', description='Returns the current weather for a city or zip code.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("city", description="Please provide the name of the city or zipcode that you want to view the current weather for.")
async def current_weather(ctx, ephemeral: bool, city: str):
    message = weather.current_weather(bot, city)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)



## User Commands

### Get Specified User Info

@bot.slash_command(name='user-info', description='Returns Sleeper user information for a given user. Must run add-league first.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("display_name", description="Please enter the display name of the user you'd like to see information about.")
async def user_info(ctx, ephemeral: bool, display_name: str):
    message = user.user_info(ctx, bot, display_name)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)



## Manage Commands
    
### Kick Command

@bot.slash_command(name='kick', description='Kicks a given user.')
@commands.has_permissions(kick_members=True)
@option("user", description="Please enter the user being kicked.")
async def kick(ctx, user: discord.Member, *, reason=None):
    message = await manage.kick(ctx, user, reason=None)
    await ctx.respond(message)


### Ban Command

@bot.slash_command(name='ban', description='Bans a given user.')
@commands.has_permissions(ban_members=True)
@option("user", description="Please enter the user being banned.")
async def ban(ctx, user: discord.Member, *, reason=None):
    message = await manage.ban(ctx, user, reason=reason)
    await ctx.respond(message)


### Unban Command

@bot.slash_command(name='unban', description='Unbans a given user.')
@option("member", description="Please enter the exact username of the member being unbanned.")
async def unban(ctx, *, member):
    message = await manage.unban(ctx, member)
    await ctx.respond(message)


### Find User Command

@bot.slash_command(name='find-user', description='Finds a given user and returns their server info related to the bot.')
@option("member", description="Please enter the exact username of the member you want to find the guild ID of.")
async def find_user(ctx, *, member):
    author_id = os.environ.get('AUTHOR_ID')
    message_author_id = str(ctx.author.id)
    if message_author_id == author_id:
        if '#' in member:
            username, user_discriminator = member.split('#')
            try:
                user_id = discord.utils.get(bot.get_all_members(), name=username, discriminator=user_discriminator).id
                user = await bot.fetch_user(user_id)
                shared_guilds = [guild for guild in bot.guilds if user in guild.members]
                if shared_guilds:
                    await ctx.respond(f'{member} - {shared_guilds[0].id}', ephemeral=True)
                else:
                    await ctx.respond('No shared guilds found.', ephemeral=True)
            except:
                await ctx.respond('No shared guilds found.', ephemeral=True)
        else:
            try:
                user_id = discord.utils.get(bot.get_all_members(), name=member).id
                user = await bot.fetch_user(user_id)
                shared_guilds = [guild for guild in bot.guilds if user in guild.members]
                if shared_guilds:
                    await ctx.respond(f'{member} - {shared_guilds[0].id}', ephemeral=True)
                else:
                    await ctx.respond('No shared guilds found.', ephemeral=True)
            except:
                await ctx.respond('No shared guilds found.', ephemeral=True)
    else:
        await ctx.respond('You do not have access to this command.', ephemeral=True)
    


## Patron Commands


### Waiver Order Command

@bot.slash_command(name='waiver-order', description='Returns current waiver order. Must run add-league first. Patron only.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
async def waiver_order(ctx, ephemeral: bool):
    message = patron.waiver_order(ctx, bot)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Transactions Command

@bot.slash_command(name='transactions', description='Returns last 10 transactions for a given week. Must run add-league first. Patron only.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("week", description="Please enter the week number you'd like to view transactions for.")
async def transactions(ctx, ephemeral: bool, week: str):
    message = patron.transactions(ctx, bot, week)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### NGS Command

@bot.slash_command(name='ngs', description='Returns next gen stats given the kind of stat, player, year, and week. For yearly stats, use week 0.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("kind", description="Please select the kind of Next Gen Stats you'd like to view for this player.", choices=["passing", "rushing", "receiving"])
@option("player", description="Please enter the player name that you'd like to view Next Gen Stats for.")
@option("year", description="Please enter the year you'd like to view these stats for. Valid back through 2016.")
@option("week", description="Please enter the week you'd like to view these stats for. Use 0 for season stats.")
async def ngs(ctx, ephemeral: bool, kind: str, player: str, year: int, week: int):
    message = patron.ngs(ctx, bot, kind, player, year, week)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)


### Box Score Command

@bot.slash_command(name='box-score', description='Returns the box score given the kind of stat, player, year, and week.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
@option("kind", description="Please select the kind of stats you'd like to view for this player.", choices=["passing", "rushing", "receiving"])
@option("player", description="Please enter the player name that you'd like to view Next Gen Stats for.")
@option("year", description="Please enter the year you'd like to view these stats for. Valid back through 1999.")
@option("week", description="Please enter the week you'd like to view these stats for.")
async def box_score(ctx, ephemeral: bool, kind: str, player: str, year: int, week: int):
    message = patron.box_score(ctx, bot, kind, player, year, week)
    if type(message) is str:
        await ctx.respond(message, ephemeral=ephemeral)
    else: 
        await ctx.respond(embed=message, ephemeral=ephemeral)



## Help Commands

### Bot Info Command

@bot.slash_command(name='bot-info', description='Returns bot information and important messages.')
@option("ephemeral", description="Select whether or not you'd like the response to be viewable to just you.")
async def bot_info(ctx, ephemeral: bool):
    message = help.help(bot)
    await ctx.respond(embed=message, ephemeral=ephemeral)


# Bot Run

bot.run(TOKEN)