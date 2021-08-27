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
import pendulum
from sleeper_bot_commands import league, setup, weather, players, help
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
    async def my_league_members(self, ctx):
        message = league.my_league_members(ctx)
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
                                games = []
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
                                    if "/" in row_split_three[0]:
                                        games.append(tr)
                                    else:
                                        continue
                                if not games:
                                    await ctx.send(f'Looks like {args[0]} {args[1]} did not play on the week specified, please try again!')
                                else:
                                    first_game = games[-1]
                                    row_split = str(first_game).split('<td class="Table__TD">')
                                    row_split_two = row_split[1].split(" ")
                                    row_split_three = row_split_two[1].split("</td>")
                                    week_one_date_month = row_split_three[0].split("/")
                                    if row_split_two[0] == "Thu":
                                        day = int(week_one_date_month[1]) + 3
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), day)
                                    elif row_split_two[0] == "Fri":
                                        day = int(week_one_date_month[1]) + 2
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), day)
                                    elif row_split_two[0] == "Sat":
                                        day = int(week_one_date_month[1]) + 1
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), day)
                                    elif row_split_two[0] == "Mon":
                                        day = int(week_one_date_month[1]) - 1
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), day)
                                    elif row_split_two[0] == "Tue":
                                        day = int(week_one_date_month[1]) - 2
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), day)
                                    else:
                                        week_one = pendulum.datetime(int(args[3]), int(week_one_date_month[0]), int(week_one_date_month[1]))
                                    for game in games:
                                        row_split = str(game).split('<td class="Table__TD">')
                                        row_split_two = row_split[1].split(" ")
                                        row_split_three = row_split_two[1].split("</td>")
                                        current_week = row_split_three[0].split("/")
                                        if current_week[0] == "1" or current_week[0] == "2":
                                            year = int(args[3]) + 1
                                            week_current = pendulum.datetime(year, int(current_week[0]), int(current_week[1]))
                                        else:
                                            week_current = pendulum.datetime(int(args[3]), int(current_week[0]), int(current_week[1]))
                                        week_num = week_current.diff(week_one).in_weeks() + 1
                                        if row_split_two[0] == "Sat" or row_split_two[0] == "Thu" or row_split_two == "Fri":
                                            if week_num == 1:
                                                if str(week_num) == str(args[4]):
                                                    game_data = game
                                                    break
                                                else:
                                                    continue 
                                            else:
                                                week_num = week_num + 1
                                                if str(week_num) == str(args[4]):
                                                    game_data = game
                                                    break
                                                else:
                                                    continue
                                        elif str(week_num) == str(args[4]):
                                            game_data = game
                                            break
                                        else:
                                            continue
                                    if game_data == None:
                                        await ctx.send(f'Looks like {args[0]} {args[1]} did not play on the week specified, please try again!')
                                    else:
                                        game_data_split = str(game_data).split('<td class="Table__TD">')
                                        if existing_player["position"] == "QB":
                                            cmp = game_data_split[4].split("</td>")[0]
                                            att = game_data_split[5].split("</td>")[0]
                                            pass_yds = game_data_split[6].split("</td>")[0]
                                            cmp_pct = game_data_split[7].split("</td>")[0]
                                            ypa = game_data_split[8].split("</td>")[0]
                                            pass_td = game_data_split[9].split("</td>")[0]
                                            intercept = game_data_split[10].split("</td>")[0]
                                            long = game_data_split[11].split("</td>")[0]
                                            sack = game_data_split[12].split("</td>")[0]
                                            rating = game_data_split[13].split("</td>")[0]
                                            qbr = game_data_split[14].split("</td>")[0]
                                            rush_att = game_data_split[15].split("</td>")[0]
                                            rush_yds = game_data_split[16].split("</td>")[0]
                                            rush_avg = game_data_split[17].split("</td>")[0]
                                            rush_td = game_data_split[18].split("</td>")[0]
                                            rush_long = game_data_split[19].split("</td>")[0]
                                            game_data_string = f'{cmp}/{att} ({cmp_pct}%), {pass_yds} yards, {ypa} yards per att, {pass_td} TD, {intercept} INT, {long} long, {sack} sacks, {rating} rating, {qbr} QBR\n\n{rush_att} rush att, {rush_yds} rush yards, {rush_avg} per carry, {rush_td} TD, {rush_long} long'
                                            embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for Week {args[4]}, {args[3]}', game_data_string, False, ctx)
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
                                            embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for Week {args[4]}, {args[3]}', game_data_string, False, ctx)
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
                                            embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for Week {args[4]}, {args[3]}', game_data_string, False, ctx)
                                            await ctx.send(embed=embed)
                                        elif existing_player["position"] == "K":
                                            long = game_data_split[9].split("</td>")[0]
                                            fg_pct = game_data_split[10].split("</td>")[0]
                                            fg = game_data_split[11].split("</td>")[0]
                                            avg = game_data_split[12].split("</td>")[0]
                                            xp = game_data_split[13].split("</td>")[0]
                                            pts = game_data_split[14].split("</td>")[0]
                                            game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                            embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for Week {args[4]}, {args[3]}', game_data_string, False, ctx)
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
        elif len(args) == 3:
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if "patron" in existing_league:
                    if existing_league["patron"] == "1":
                        existing_player = functions.get_existing_player(args)
                        if existing_player:
                            if "espn_id" in existing_player:
                                nfl_state = requests.get(
                                    'https://api.sleeper.app/v1/state/nfl'
                                )
                                if nfl_state.json()["season_type"] == "pre":
                                    res = requests.get(
                                        f'https://www.espn.com/nfl/player/gamelog/_/id/{existing_player["espn_id"]}/type/nfl/year/{nfl_state.json()["previous_season"]}'
                                    )
                                else:
                                    res = requests.get(
                                        f'https://www.espn.com/nfl/player/gamelog/_/id/{existing_player["espn_id"]}/type/nfl/year/{nfl_state.json()["season"]}'
                                    )
                                soup = bs4(res.text, 'html.parser')
                                search_data = soup.find_all('tr')
                                if not search_data:
                                    res = requests.get(
                                        f'https://www.espn.com/nfl/player/gamelog/_/id/{existing_player["espn_id"]}/type/nfl/year/{nfl_state.json()["previous_season"]}'
                                    )
                                soup = bs4(res.text, 'html.parser')
                                search_data = soup.find_all('tr')
                                games = []
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
                                    if "/" in row_split_three[0]:
                                        games.append(tr)
                                    else:
                                        continue
                                recent_game = games[0]
                                game_data_split = str(recent_game).split('<td class="Table__TD">')
                                if existing_player["position"] == "QB":
                                    cmp = game_data_split[4].split("</td>")[0]
                                    att = game_data_split[5].split("</td>")[0]
                                    pass_yds = game_data_split[6].split("</td>")[0]
                                    cmp_pct = game_data_split[7].split("</td>")[0]
                                    ypa = game_data_split[8].split("</td>")[0]
                                    pass_td = game_data_split[9].split("</td>")[0]
                                    intercept = game_data_split[10].split("</td>")[0]
                                    long = game_data_split[11].split("</td>")[0]
                                    sack = game_data_split[12].split("</td>")[0]
                                    rating = game_data_split[13].split("</td>")[0]
                                    qbr = game_data_split[14].split("</td>")[0]
                                    rush_att = game_data_split[15].split("</td>")[0]
                                    rush_yds = game_data_split[16].split("</td>")[0]
                                    rush_avg = game_data_split[17].split("</td>")[0]
                                    rush_td = game_data_split[18].split("</td>")[0]
                                    rush_long = game_data_split[19].split("</td>")[0]
                                    game_data_string = f'{cmp}/{att} ({cmp_pct}%), {pass_yds} yards, {ypa} yards per att, {pass_td} TD, {intercept} INT, {long} long, {sack} sacks, {rating} rating, {qbr} QBR\n\n{rush_att} rush att, {rush_yds} rush yards, {rush_avg} per carry, {rush_td} TD, {rush_long} long'
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for the last game', game_data_string, False, ctx)
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
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for the last game', game_data_string, False, ctx)
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
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for the last game', game_data_string, False, ctx)
                                    await ctx.send(embed=embed)
                                elif existing_player["position"] == "K":
                                    long = game_data_split[9].split("</td>")[0]
                                    fg_pct = game_data_split[10].split("</td>")[0]
                                    fg = game_data_split[11].split("</td>")[0]
                                    avg = game_data_split[12].split("</td>")[0]
                                    xp = game_data_split[13].split("</td>")[0]
                                    pts = game_data_split[14].split("</td>")[0]
                                    game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for the last game', game_data_string, False, ctx)
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
            await ctx.send('Invalid arguments. Please use the format [prefix]game-stats [first name] [last name] [team abbreviation] [year] [date in mm/dd format], or [prefix]game-stats [first name] [last name] [team abbreviation].')


    ### Waiver Order Command

    @commands.command(name='waiver-order')
    async def starter_fantasy_points(self, ctx):
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if "patron" in existing_league:
                if existing_league["patron"] == "1":
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        sorted_rosters = sorted(rosters, key=lambda i: i["settings"]["waiver_position"])
                        waiver_order_string = ''
                        count = 0
                        for roster in sorted_rosters:
                            count = count + 1
                            user = sleeper_wrapper.User(roster["owner_id"]).get_user()
                            waiver_order_string += f'{str(count)}. {user["display_name"]}\n'
                        embed = functions.my_embed('Waiver Order', f'Returns the current waiver order for your league.', discord.Colour.blue(), f'Current Waiver Order', waiver_order_string, False, ctx)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send('Please run add-league command, no Sleeper League connected.')
                else:
                    await ctx.send('You do not have access to this command, it is reserved for patrons only!')
            else:
                await ctx.send('You do not have access to this command, it is reserved for patrons only!')    
        else:
            await ctx.send('Please run add-league command, no Sleeper League connected.')



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