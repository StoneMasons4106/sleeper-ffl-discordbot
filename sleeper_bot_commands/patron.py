import discord
from discord.ext import commands
from discord.utils import find
import os
import pymongo
import sleeper_wrapper
import functions
import requests
import pendulum
from bs4 import BeautifulSoup as bs4
if os.path.exists("env.py"):
    import env


MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


def starter_fantasy_points(ctx, *args):
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
                                        else:
                                            embed = 'No starters were found with this information. Please try again!'
                                    else:
                                        embed = 'There are no matchups this week, try this command again during the season!'
                                else:
                                    embed = 'No players are found with these parameters, please try again!'
                            else:
                                embed = 'Please run add-league command, no Sleeper League connected.'
                        else:
                            embed = 'You do not have access to this command, it is reserved for patrons only!'
                    else:
                        embed = 'You do not have access to this command, it is reserved for patrons only!'
                else:
                    embed = 'Please run add-league command, no Sleeper League connected.'
            else:
                embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
        else:
            embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
    else:
        embed = 'Invalid arguments. Please use the format [prefix]starter-fantasy-points [first name] [last name] [team abbreviation] [week]'
    return embed


def game_stats(ctx, *args):
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
                                embed = f'Looks like {args[0]} {args[1]} did not play on the week specified, please try again!'
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
                                    embed = f'Looks like {args[0]} {args[1]} did not play on the week specified, please try again!'
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
                                    elif existing_player["position"] == "K":
                                        long = game_data_split[9].split("</td>")[0]
                                        fg_pct = game_data_split[10].split("</td>")[0]
                                        fg = game_data_split[11].split("</td>")[0]
                                        avg = game_data_split[12].split("</td>")[0]
                                        xp = game_data_split[13].split("</td>")[0]
                                        pts = game_data_split[14].split("</td>")[0]
                                        game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                        embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for Week {args[4]}, {args[3]}', game_data_string, False, ctx)
                                    else:
                                        embed = 'Game stats unavailable for this position, please try again!'
                        else:
                            embed = 'Game stats unavailable for this player, please try again!'
                    else:
                        embed = 'No players are found with these parameters, please try again!'
                else:
                    embed = 'You do not have access to this command, it is reserved for patrons only!'
            else:
                embed = 'You do not have access to this command, it is reserved for patrons only!'    
        else:
            embed = 'Please run add-league command, no Sleeper League connected.'
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
                            elif existing_player["position"] == "K":
                                long = game_data_split[9].split("</td>")[0]
                                fg_pct = game_data_split[10].split("</td>")[0]
                                fg = game_data_split[11].split("</td>")[0]
                                avg = game_data_split[12].split("</td>")[0]
                                xp = game_data_split[13].split("</td>")[0]
                                pts = game_data_split[14].split("</td>")[0]
                                game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {args[0]} {args[1]} for the last game', game_data_string, False, ctx)
                                pass
                            else:
                                embed = 'Game stats unavailable for this position, please try again!'
                        else:
                            embed = 'Game stats unavailable for this player, please try again!'
                    else:
                        embed = 'No players are found with these parameters, please try again!'
                else:
                    embed = 'You do not have access to this command, it is reserved for patrons only!'  
            else:
                embed = 'You do not have access to this command, it is reserved for patrons only!'    
        else:
            embed = 'Please run add-league command, no Sleeper League connected.'
    else:
        embed = 'Invalid arguments. Please use the format [prefix]game-stats [first name] [last name] [team abbreviation] [year] [date in mm/dd format], or [prefix]game-stats [first name] [last name] [team abbreviation].'
    return embed


def waiver_order(ctx):
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
                else:
                    embed = 'Please run add-league command, no Sleeper League connected.'
            else:
                embed = 'You do not have access to this command, it is reserved for patrons only!'
        else:
            embed = 'You do not have access to this command, it is reserved for patrons only!'  
    else:
        embed = 'Please run add-league command, no Sleeper League connected.'
    return embed