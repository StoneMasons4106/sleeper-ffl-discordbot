# Import needed libraries

import discord
import os
import pendulum
import pymongo
import sleeper_wrapper
import functions
import time
import requests
if os.path.exists("env.py"):
    import env


MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Scheduled Messages/Jobs

## Get and Refresh Weekly Schedule Data from Sportradar in Mongo

def get_weekly_schedule_data():
    week = functions.get_current_week()
    if week[0] <= 17:
        if week[1] == False:
            sportradar_api_key = os.environ.get("SPORTRADAR_API_KEY")
            nfl_state = requests.get(
                'https://api.sleeper.app/v1/state/nfl'
            )
            year = nfl_state.json()["season"]
            weekly_schedule = requests.get(
                f'https://api.sportradar.us/nfl/official/trial/v6/en/games/{int(year)}/REG/{week[0]}/schedule.json?api_key={sportradar_api_key}'
            )
            weekly_schedule_id = str(weekly_schedule.json()["id"])
            existing_schedule = MONGO.weekly_schedules.find_one(
                    {"id": weekly_schedule_id})
            if existing_schedule:
                MONGO.weekly_schedules.delete_one(
                    {"id": weekly_schedule_id})
                MONGO.weekly_schedules.insert_one(weekly_schedule.json())
                MONGO_CONN.close()
            else:
                MONGO.weekly_schedules.insert_one(weekly_schedule.json())
                MONGO_CONN.close()
        else:
            pass
    else:
        pass



## Refresh Player Data in Mongo

def refresh_players():
    MONGO.players.delete_many({})
    nfl_players = sleeper_wrapper.Players().get_all_players()
    for player in nfl_players:
        full_name = nfl_players[player]["first_name"] + ' ' + nfl_players[player]["last_name"]
        position = nfl_players[player]["position"]
        team = nfl_players[player]["team"]
        try:
            status = nfl_players[player]["status"]
            injury_status = nfl_players[player]["injury_status"]
            sport_radar_id = nfl_players[player]["sportradar_id"]
            depth_chart_order = nfl_players[player]["depth_chart_order"]
            player_object = {
                "id": player,
                "name": full_name,
                "position": position,
                "team": team,
                "status": status,
                "injury_status": injury_status,
                "sportradar_id": sport_radar_id,
                "depth_chart_order": depth_chart_order
            }
        except:
            player_object = {
                "id": player,
                "name": full_name,
                "position": position,
                "team": team
            }
        MONGO.players.insert_one(player_object)
    MONGO_CONN.close()
    now = pendulum.now(tz='America/New_York')
    print(f'Completed player refresh at {now}')



## Get and Refresh Game Data for Current Week

def get_weekly_game_data():
    week = functions.get_current_week()
    if week[0] <= 17:
        if week[1] == False:
            sportradar_api_key = os.environ.get("SPORTRADAR_API_KEY")
            nfl_state = requests.get(
                'https://api.sleeper.app/v1/state/nfl'
            )
            year = nfl_state.json()["season"]
            weekly_schedule = MONGO.weekly_schedules.find_one(
                {"year": int(year), "week.title": str(week[0])})
            if weekly_schedule:
                for game in weekly_schedule["week"]["games"]:
                    if "scoring" in game:
                        time.sleep(1)
                        statistics = requests.get(
                            f'https://api.sportradar.us/nfl/official/trial/v6/en/games/{game["id"]}/statistics.json?api_key={sportradar_api_key}'
                        )
                        existing_game = MONGO.game_stats.find_one(
                            {"id": str(statistics.json()["id"])})
                        if existing_game:
                            MONGO.game_stats.delete_one(
                                {"id": str(statistics.json()["id"])})
                            MONGO.game_stats.insert_one(statistics.json())
                        else:
                            MONGO.game_stats.insert_one(statistics.json())
                    else:
                        pass
            else:
                pass
        else:
            pass
    else:
        pass
    MONGO_CONN.close()



## Get Close Games for Current Week

async def get_current_close_games(bot):
    week = functions.get_current_week()
    if week[0] <= 17:
        if week[1] == False:
            print(week[1])
            servers = MONGO.servers.find(
                {})
            MONGO_CONN.close()
            if servers:
                for server in servers:
                    if "league" in server and "score_type" in server and "channel" in server:
                        score_type = server["score_type"]
                        league_id = server["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                        scoreboard = sleeper_wrapper.League(int(league_id)).get_scoreboards(rosters, matchups, users, score_type, week[0])
                        if scoreboard:
                            close_games = sleeper_wrapper.League(int(league_id)).get_close_games(scoreboard, 5)
                            if close_games:
                                channel = await bot.fetch_channel(int(server["channel"]))
                                close_games_string = ''
                                count = 0
                                for score in close_games:
                                    count = count + 1
                                    close_games_string += f'{str(count)}. {close_games[score][0][0]} - {str(close_games[score][0][1])} / {close_games[score][1][0]} - {str(close_games[score][1][1])}\n'
                                embed = discord.Embed(title='Current Week Close Games', description=f'Close Games for Week {str(week[0])}', color=discord.Colour.blue())
                                embed.add_field(name='Close Games', value=close_games_string, inline=False)
                                await channel.send(f'Things are heating up! Here are the close games heading into tonight:')
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
    else:
        pass



## Get Matchups for Current Week

async def get_current_matchups(bot):
    week = functions.get_current_week()
    if week[0] <= 17:
        if week[1] == False:
            servers = MONGO.servers.find(
                        {})
            MONGO_CONN.close()
            if servers:
                for server in servers:
                    if "league" in server and "channel" in server:
                        league_id = server["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                        if matchups:
                            channel = await bot.fetch_channel(int(server["channel"]))
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
    else:
        pass



## Get Scoreboard for Current Week

async def get_current_scoreboards(bot):
    week = functions.get_current_week()
    if week[0] <= 17:
        if week[1] == False:
            servers = MONGO.servers.find(
                {})
            MONGO_CONN.close()
            if servers:
                for server in servers:
                    if "league" in server and "score_type" in server and "channel" in server:
                        score_type = server["score_type"]
                        league_id = server["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(week[0])
                        scoreboard = sleeper_wrapper.League(int(league_id)).get_scoreboards(rosters, matchups, users, score_type, week[0])
                        if scoreboard:
                            channel = await bot.fetch_channel(int(server["channel"]))
                            scoreboard_string = ''
                            count = 0
                            for score in scoreboard:
                                count = count + 1
                                scoreboard_string += f'{str(count)}. {scoreboard[score][0][0]} - {str(scoreboard[score][0][1])} / {scoreboard[score][1][0]} - {str(scoreboard[score][1][1])}\n'
                            embed = discord.Embed(title='Current Week Scoreboard', description=f'Scoreboard for Week {str(week[0])}', color=discord.Colour.blue())
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