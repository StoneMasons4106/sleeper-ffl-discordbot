import discord
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



def game_stats(ctx, bot, first_name, last_name, team_abbreviation, year_played, week_played):
    if ctx.guild == None:
        embed = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if functions.is_patron(existing_league):
                existing_player = functions.get_existing_player(first_name, last_name, team_abbreviation)
                if existing_player:
                    if "espn_id" in existing_player:
                        res = requests.get(
                            f'https://www.espn.com/nfl/player/gamelog/_/id/{existing_player["espn_id"]}/type/nfl/year/{year_played}'
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
                            embed = f'Looks like {first_name} {last_name} did not play on the week specified, please try again!'
                        else:
                            res2 = res = requests.get(
                                f'https://www.espn.com/nfl/schedule/_/week/1/year/{year_played}'
                            )
                            soup2 = bs4(res2.text, 'html.parser')
                            search_data = soup2.find_all('h2', class_="table-caption")
                            for h2 in search_data:
                                h2_split = str(h2).split('<h2 class="table-caption">')
                                h2_split_two = h2_split[1].split("</h2>")
                                h2_split_three = h2_split_two[0].split(", ")
                                if h2_split_three[0] == "Sunday":
                                    h2_split_four = h2_split_three[1].split(" ")
                                    week_one = pendulum.datetime(int(year_played), 9, int(h2_split_four[1]))
                                else:
                                    continue
                            for game in games:
                                row_split = str(game).split('<td class="Table__TD">')
                                row_split_two = row_split[1].split(" ")
                                row_split_three = row_split_two[1].split("</td>")
                                current_week = row_split_three[0].split("/")
                                if current_week[0] == "1" or current_week[0] == "2":
                                    year = int(year_played) + 1
                                    week_current = pendulum.datetime(year, int(current_week[0]), int(current_week[1]))
                                else:
                                    week_current = pendulum.datetime(int(year_played), int(current_week[0]), int(current_week[1]))
                                week_num = week_current.diff(week_one).in_weeks() + 1
                                if row_split_two[0] == "Sat" or row_split_two[0] == "Thu" or row_split_two == "Fri":
                                    if week_num == 1:
                                        if str(week_num) == str(week_played):
                                            game_data = game
                                            break
                                        else:
                                            continue 
                                    else:
                                        week_num = week_num + 1
                                        if str(week_num) == str(week_played):
                                            game_data = game
                                            break
                                        else:
                                            continue
                                elif str(week_num) == str(week_played):
                                    game_data = game
                                    break
                                else:
                                    continue
                            if game_data == None:
                                embed = f'Looks like {first_name} {last_name} did not play on the week specified, please try again!'
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
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {first_name} {last_name} for Week {week_played}, {year_played}', game_data_string, False, bot)
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
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {first_name} {last_name} for Week {week_played}, {year_played}', game_data_string, False, bot)
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
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {first_name} {last_name} for Week {week_played}, {year_played}', game_data_string, False, bot)
                                elif existing_player["position"] == "K":
                                    long = game_data_split[9].split("</td>")[0]
                                    fg_pct = game_data_split[10].split("</td>")[0]
                                    fg = game_data_split[11].split("</td>")[0]
                                    avg = game_data_split[12].split("</td>")[0]
                                    xp = game_data_split[13].split("</td>")[0]
                                    pts = game_data_split[14].split("</td>")[0]
                                    game_data_string = f'{fg} FG, ({fg_pct}%), {avg} avg, {long} long, {xp} XP, {pts} points'
                                    embed = functions.my_embed('Game Stats', f'Returns the game stats for a player for the specified year and week.', discord.Colour.blue(), f'Game Stats for {first_name} {last_name} for Week {week_played}, {year_played}', game_data_string, False, bot)
                                else:
                                    embed = 'Game stats unavailable for this position, please try again!'
                    else:
                        embed = 'Game stats unavailable for this player, please try again!'
                else:
                    embed = 'No players are found with these parameters, please try again!'
            else:
                embed = 'You do not have access to this command, it is reserved for patrons only!'    
        else:
            embed = 'Please run add-league command, no Sleeper League connected.'
    return embed



def waiver_order(ctx, bot):
    if ctx.guild == None:
        embed= 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if functions.is_patron(existing_league):
                if "league" in existing_league:
                    league_id = existing_league["league"]
                    rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                    users = sleeper_wrapper.League(int(league_id)).get_users()
                    sorted_rosters = sorted(rosters, key=lambda i: i["settings"]["waiver_position"])
                    waiver_order_string = ''
                    count = 0
                    for roster in sorted_rosters:
                        count = count + 1
                        user = find(lambda u: u["user_id"] == roster["owner_id"], users)
                        waiver_order_string += f'{str(count)}. {user["display_name"]}\n'
                    embed = functions.my_embed('Waiver Order', f'Returns the current waiver order for your league.', discord.Colour.blue(), f'Current Waiver Order', waiver_order_string, False, bot)
                else:
                    embed = 'Please run add-league command, no Sleeper League connected.'
            else:
                embed = 'You do not have access to this command, it is reserved for patrons only!'  
        else:
            embed = 'Please run add-league command, no Sleeper League connected.'
    return embed



def transactions(ctx, bot, week):
    if ctx.guild == None:
        embed= 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        if week.isnumeric() and int(week) > 0 and int(week) < 19:
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if functions.is_patron(existing_league):
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        transactions = sleeper_wrapper.League(int(league_id)).get_transactions(int(week))
                        transactions_string = ''
                        count = 0
                        if len(transactions) == 0:
                            transactions_string = 'None'
                            embed = functions.my_embed('Transactions', 'Returns the last 10 transactions for any specified week.', discord.Colour.blue(), 'Recent Transactions', transactions_string, False, bot)
                        else:
                            for transaction in transactions:
                                count = count + 1
                                if count == 11:
                                    break
                                elif transaction["type"] == 'free_agent':
                                    for drop in transaction["drops"]:
                                        existing_player = MONGO.players.find_one({"id": str(drop)})
                                        roster_id = transaction["drops"][drop]
                                        for roster in rosters:
                                            if roster["roster_id"] == roster_id:
                                                this_roster = roster
                                                break
                                            else:
                                                continue
                                        for user in users:
                                            if this_roster["owner_id"] == user["user_id"]:
                                                username = user["display_name"]
                                                transactions_string += f'{username} dropped {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}\n\n'
                                            else:
                                                continue
                                        MONGO_CONN.close()
                                elif transaction["type"] == 'waiver':
                                    for add in transaction["adds"]:
                                        existing_player = MONGO.players.find_one({"id": str(add)})
                                        roster_id = transaction["adds"][add]
                                        for roster in rosters:
                                            if roster["roster_id"] == roster_id:
                                                this_roster = roster
                                                break
                                            else:
                                                continue
                                        for user in users:
                                            if this_roster["owner_id"] == user["user_id"]:
                                                username = user["display_name"]
                                                transactions_string += f'{username} added {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}\n\n'
                                            else:
                                                continue
                                        MONGO_CONN.close()
                                else:
                                    second_transactions_string = 'Trade:\n'
                                    for add in transaction["adds"]:
                                        existing_player = MONGO.players.find_one({"id": str(add)})
                                        roster_id = transaction["adds"][add]
                                        for roster in rosters:
                                            if roster["roster_id"] == roster_id:
                                                this_roster = roster
                                                break
                                            else:
                                                continue
                                        for user in users:
                                            if this_roster["owner_id"] == user["user_id"]:
                                                username = user["display_name"]
                                                second_transactions_string += f'{username} received {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}\n'
                                                break
                                            else:
                                                continue
                                        MONGO_CONN.close()
                                    if len(transaction["draft_picks"]) != 0:
                                        for draft_pick in transaction["draft_picks"]:
                                            for roster in rosters:
                                                if roster["roster_id"] == draft_pick["owner_id"]:
                                                    this_roster = roster
                                                    break
                                                else:
                                                    continue
                                            for user in users:
                                                if this_roster["owner_id"] == user["user_id"]:
                                                    username = user["display_name"]
                                                    second_transactions_string += f'{username} received a draft pick in round {draft_pick["round"]} in the {draft_pick["season"]} season\n'
                                                    break
                                                else:
                                                    continue 
                                    else:
                                        pass
                                    transactions_string += f'{second_transactions_string}\n'
                            embed = functions.my_embed('Transactions', 'Returns the last 10 transactions for any specified week.', discord.Colour.blue(), 'Recent Transactions', transactions_string, False, bot)
                    else:
                        embed = 'Please run add-league command, no Sleeper League connected.'    
                else:
                    embed = 'You do not have access to this command, it is reserved for patrons only!'  
            else:
                embed = 'Please run add-league command, no Sleeper League connected.'
        else:
            embed = 'Please use a valid week number between 1 and 18.'
    return embed