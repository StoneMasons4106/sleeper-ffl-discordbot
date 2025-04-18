# Import needed libraries

import discord
import os
import pendulum
import pymongo
import sleeper_wrapper
import functions

if os.path.exists("env.py"):
    import env


MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Scheduled Messages/Jobs


## Refresh Player Data in Mongo


def refresh_players():
    MONGO.players.delete_many({})
    nfl_players = sleeper_wrapper.Players().get_all_players()
    for player in nfl_players:
        full_name = (
            nfl_players[player]["first_name"] + " " + nfl_players[player]["last_name"]
        )
        position = nfl_players[player]["position"]
        team = nfl_players[player]["team"]
        try:
            status = nfl_players[player]["status"]
            injury_status = nfl_players[player]["injury_status"]
            depth_chart_order = nfl_players[player]["depth_chart_order"]
            espn_id = nfl_players[player]["espn_id"]
            player_object = {
                "id": player,
                "name": full_name,
                "position": position,
                "team": team,
                "status": status,
                "injury_status": injury_status,
                "depth_chart_order": depth_chart_order,
                "espn_id": espn_id,
            }
        except:
            player_object = {
                "id": player,
                "name": full_name,
                "position": position,
                "team": team,
            }
        MONGO.players.insert_one(player_object)
    MONGO_CONN.close()
    now = pendulum.now(tz="America/New_York")
    print(f"Completed player refresh at {now}")


## Get Matchups for Current Week


async def get_current_matchups(bot):
    week = functions.get_current_week()
    if week[0] <= 18:
        if not week[1]:
            servers = functions.get_all_servers().sort("patron", -1)
            if servers:
                for server in servers:
                    if "league" in server and "channel" in server:
                        league_id = server["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(
                            week[0]
                        )
                        if matchups:
                            try:
                                channel = await bot.fetch_channel(
                                    int(server["channel"])
                                )
                                sorted_matchups = sorted(
                                    matchups,
                                    key=lambda i: (
                                        i["matchup_id"] is None,
                                        i["matchup_id"],
                                    ),
                                )
                                matchups_string = ""
                                count = 0
                                matchup_count = 1
                                for matchup in sorted_matchups:
                                    if matchup["matchup_id"] is None:
                                        pass
                                    else:
                                        count = count + 1
                                        roster = next(
                                            (
                                                roster
                                                for roster in rosters
                                                if roster["roster_id"]
                                                == matchup["roster_id"]
                                            ),
                                            None,
                                        )
                                        user = next(
                                            (
                                                user
                                                for user in users
                                                if user["user_id"] == roster["owner_id"]
                                            ),
                                            None,
                                        )
                                        if (count % 2) == 0:
                                            matchup_count = matchup_count + 1
                                            matchups_string += (
                                                f'{user["display_name"]}\n'
                                            )
                                        else:
                                            matchups_string += f'{str(matchup_count)}. {user["display_name"]} vs. '
                                embed = functions.my_embed(
                                    "Current Week Matchups",
                                    f"Matchups for Week {str(week[0])}",
                                    discord.Colour.blue(),
                                    "Matchups",
                                    matchups_string,
                                    False,
                                    bot,
                                )
                                await channel.send(
                                    f"Who is ready to rumble?! Here are the matchups for week {str(week[0])} in our league:"
                                )
                                await channel.send(embed=embed)
                            except:
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


## Get Scoreboard for Current Week


async def get_current_scoreboard(bot):
    week = functions.get_current_week()
    if week[0] <= 18:
        if not week[1]:
            servers = functions.get_all_servers().sort("patron", -1)
            if servers:
                for server in servers:
                    if "league" in server and "channel" in server:
                        league_id = server["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(
                            week[0]
                        )
                        if matchups:
                            try:
                                channel = await bot.fetch_channel(
                                    int(server["channel"])
                                )
                                sorted_matchups = sorted(
                                    matchups,
                                    key=lambda i: (
                                        i["matchup_id"] is None,
                                        i["matchup_id"],
                                    ),
                                )
                                scoreboard_string = ""
                                count = 0
                                matchup_count = 1
                                for matchup in sorted_matchups:
                                    if matchup["matchup_id"] is None:
                                        pass
                                    else:
                                        count = count + 1
                                        roster = next(
                                            (
                                                roster
                                                for roster in rosters
                                                if roster["roster_id"]
                                                == matchup["roster_id"]
                                            ),
                                            None,
                                        )
                                        user = next(
                                            (
                                                user
                                                for user in users
                                                if user["user_id"] == roster["owner_id"]
                                            ),
                                            None,
                                        )
                                        if (count % 2) == 0:
                                            matchup_count = matchup_count + 1
                                            scoreboard_string += f'{user["display_name"]} - {matchup["points"]}\n'
                                        else:
                                            scoreboard_string += f'{str(matchup_count)}. {user["display_name"]} - {matchup["points"]} / '
                                filtered_roster_object = []
                                for roster in rosters:
                                    if roster["owner_id"] is not None:
                                        filtered_roster_object.append(roster)
                                    else:
                                        pass
                                standings_object = sleeper_wrapper.League(
                                    int(league_id)
                                ).get_standings(filtered_roster_object, users)
                                standings_string = ""
                                count = 0
                                for i in standings_object:
                                    count = count + 1
                                    standings_string += f"{str(count)}. {i[0]} / Record: {i[1]}-{i[2]} / Points For: {i[3]}\n"
                                embed = functions.my_embed(
                                    "Current Week Scoreboard",
                                    f"Scoreboard for Week {str(week[0])}",
                                    discord.Colour.blue(),
                                    "Scoreboard",
                                    scoreboard_string,
                                    False,
                                    bot,
                                )
                                embed_two = functions.my_embed(
                                    "Current Week Standings",
                                    f"Standings for Week {str(week[0])}",
                                    discord.Colour.blue(),
                                    "Standings",
                                    standings_string,
                                    False,
                                    bot,
                                )
                                await channel.send(
                                    f"Another week in the books! Here is the scoreboard and standings for week {str(week[0])} in our league:"
                                )
                                await channel.send(embed=embed)
                                await channel.send(embed=embed_two)
                            except:
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


## Send Waiver Clearing Messages


async def send_waiver_clear(bot):
    week = functions.get_current_week()
    if week[0] <= 18:
        if not week[1]:
            servers = functions.get_all_servers().sort("patron", -1)
            if servers:
                for server in servers:
                    if "league" in server and "channel" in server:
                        if functions.is_patron(server):
                            league_id = server["league"]
                            league = sleeper_wrapper.League(int(league_id)).get_league()
                            waiver_day = league["settings"]["waiver_day_of_week"]
                            today = pendulum.now()
                            if waiver_day == (today.day_of_week - 1):
                                try:
                                    channel = await bot.fetch_channel(
                                        int(server["channel"])
                                    )
                                    rosters = sleeper_wrapper.League(
                                        int(league_id)
                                    ).get_rosters()
                                    sorted_rosters = sorted(
                                        rosters,
                                        key=lambda i: i["settings"]["waiver_position"],
                                    )
                                    waiver_order_string = ""
                                    count = 0
                                    for roster in sorted_rosters:
                                        count = count + 1
                                        user = sleeper_wrapper.User(
                                            roster["owner_id"]
                                        ).get_user()
                                        waiver_order_string += (
                                            f'{str(count)}. {user["display_name"]}\n'
                                        )
                                    embed = functions.my_embed(
                                        "Waiver Order",
                                        "Returns the current waiver order for your league.",
                                        discord.Colour.blue(),
                                        "Current Waiver Order",
                                        waiver_order_string,
                                        False,
                                        bot,
                                    )
                                    await channel.send(
                                        "Time to check your waiver claims, looks like they cleared last night! Here is a quick look at the current waiver order after the claims went through:"
                                    )
                                    await channel.send(embed=embed)
                                except:
                                    pass
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
            else:
                pass
        else:
            pass
    else:
        pass
