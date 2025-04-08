import discord
import os
import pymongo
import sleeper_wrapper
import functions

if os.path.exists("env.py"):
    import env


MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


def trending_players(bot, add_drop: str):
    if add_drop == "add" or add_drop == "drop":
        trending_players = sleeper_wrapper.Players().get_trending_players(
            "nfl", add_drop, 24, 10
        )
        trending_string = ""
        count = 0
        for player in trending_players:
            count = count + 1
            player_id = player["player_id"]
            change = player["count"]
            db_player = MONGO.players.find_one({"id": str(player_id)})
            MONGO_CONN.close()
            if db_player["team"]:
                team = db_player["team"]
            else:
                team = "None"
            if add_drop == "add":
                trending_string += f'{str(count)}. {db_player["name"]} {db_player["position"]} - {team} +{str(change)}\n'
            else:
                trending_string += f'{str(count)}. {db_player["name"]} {db_player["position"]} - {team} -{str(change)}\n'
        if add_drop == "add":
            embed = functions.my_embed(
                "Trending Players",
                "Display Current Trending Added Players",
                discord.Colour.blue(),
                "Players",
                trending_string,
                False,
                bot,
            )
        else:
            embed = functions.my_embed(
                "Trending Players",
                "Display Current Trending Dropped Players",
                discord.Colour.blue(),
                "Players",
                trending_string,
                False,
                bot,
            )
    else:
        embed = "Invalid add_drop argument. Please use either add or drop to get trending players."
    return embed


def roster(ctx, bot, username: str, roster_portion: str):
    if ctx.guild is None:
        embed = "This command is only available when sent in a guild rather than a DM. Try again there."
    else:
        if (
            roster_portion == "starters"
            or roster_portion == "bench"
            or roster_portion == "all"
        ):
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
                        if roster_portion == "starters":
                            starters_string = ""
                            res = all(i == "0" for i in users_roster["starters"])
                            if res:
                                starters_string += "None\n"
                            else:
                                for i in users_roster["starters"]:
                                    if i == "0":
                                        starters_string += "None\n"
                                    else:
                                        player = MONGO.players.find_one({"id": i})
                                        starters_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                            MONGO_CONN.close()
                            embed = functions.my_embed(
                                "Roster",
                                f'Starting Roster for {user["display_name"]}',
                                discord.Colour.blue(),
                                "Starting Roster",
                                starters_string,
                                False,
                                bot,
                            )
                        if roster_portion == "all":
                            players_string = ""
                            try:
                                if len(users_roster["players"]) != 0:
                                    for i in users_roster["players"]:
                                        if i == "0":
                                            players_string += "None\n"
                                        else:
                                            player = MONGO.players.find_one({"id": i})
                                            players_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Complete Roster for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Full Roster",
                                        players_string,
                                        False,
                                        bot,
                                    )
                                else:
                                    players_string = "None"
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Complete Roster for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Full Roster",
                                        players_string,
                                        False,
                                        bot,
                                    )
                            except:
                                if users_roster["players"] is not None:
                                    for i in users_roster["players"]:
                                        if i == "0":
                                            players_string += "None\n"
                                        else:
                                            player = MONGO.players.find_one({"id": i})
                                            players_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Complete Roster for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Full Roster",
                                        players_string,
                                        False,
                                        bot,
                                    )
                                else:
                                    players_string = "None"
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Complete Roster for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Full Roster",
                                        players_string,
                                        False,
                                        bot,
                                    )
                        if roster_portion == "bench":
                            bench_string = ""
                            try:
                                if len(users_roster["players"]) != 0:
                                    bench_roster = list(
                                        set(users_roster["players"]).difference(
                                            users_roster["starters"]
                                        )
                                    )
                                    for i in bench_roster:
                                        if i == "0":
                                            bench_string += "None\n"
                                        else:
                                            player = MONGO.players.find_one({"id": i})
                                            bench_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Bench for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Bench",
                                        bench_string,
                                        False,
                                        bot,
                                    )
                                else:
                                    bench_string = "None"
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Bench for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Bench",
                                        bench_string,
                                        False,
                                        bot,
                                    )
                            except:
                                if users_roster["players"] is not None:
                                    bench_roster = list(
                                        set(users_roster["players"]).difference(
                                            users_roster["starters"]
                                        )
                                    )
                                    for i in bench_roster:
                                        if i == "0":
                                            bench_string += "None\n"
                                        else:
                                            player = MONGO.players.find_one({"id": i})
                                            bench_string += f'{player["name"]} {player["position"]} - {player["team"]}\n'
                                    MONGO_CONN.close()
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Bench for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Bench",
                                        bench_string,
                                        False,
                                        bot,
                                    )
                                else:
                                    bench_string = "None"
                                    embed = functions.my_embed(
                                        "Roster",
                                        f'Bench for {user["display_name"]}',
                                        discord.Colour.blue(),
                                        "Bench",
                                        bench_string,
                                        False,
                                        bot,
                                    )
                    else:
                        embed = "Invalid username. Double check for any typos and try again."
                else:
                    embed = (
                        "Please run add-league command, no Sleeper League connected."
                    )
            else:
                embed = "Please run add-league command, no Sleeper League connected."
        else:
            embed = (
                "Invalid roster_portion argument. Please use starters, bench, or all."
            )
    return embed


def status(bot, first_name, last_name, team_abbreviation):
    existing_player = functions.get_existing_player(
        first_name, last_name, team_abbreviation
    )
    if existing_player:
        embed = functions.my_embed(
            "Status",
            f"Roster, Injury, and Depth Chart Status for {first_name} {last_name} - {team_abbreviation}",
            discord.Colour.blue(),
            "Roster Status",
            existing_player["status"],
            False,
            bot,
        )
        embed.add_field(
            name="Depth Chart Order",
            value=existing_player["depth_chart_order"],
            inline=False,
        )
        embed.add_field(
            name="Injury Status", value=existing_player["injury_status"], inline=False
        )
    else:
        embed = "No player found with those specifications, please try again!"
    return embed


def who_has(ctx, bot, first_name, last_name, team_abbreviation):
    if ctx.guild is None:
        embed = "This command is only available when sent in a guild rather than a DM. Try again there."
    else:
        existing_player = functions.get_existing_player(
            first_name, last_name, team_abbreviation
        )
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
                        if roster["players"] is not None:
                            for player in roster["players"]:
                                if player == existing_player["id"]:
                                    for user in users:
                                        if user["user_id"] == roster["owner_id"]:
                                            embed = functions.my_embed(
                                                "Who Has...",
                                                "Command to find who currently has a particular player on their roster.",
                                                discord.Colour.blue(),
                                                f"Owner of {first_name} {last_name}",
                                                user["display_name"],
                                                False,
                                                bot,
                                            )
                                            found = True
                                            break
                                        else:
                                            pass
                                else:
                                    pass
                            if count == len(rosters):
                                if found:
                                    pass
                                else:
                                    embed = functions.my_embed(
                                        "Who Has...",
                                        "Command to find who currently has a particular player on their roster.",
                                        discord.Colour.blue(),
                                        f"Owner of {first_name} {last_name}",
                                        "None",
                                        False,
                                        bot,
                                    )
                                    break
                            else:
                                continue
                        else:
                            if count == len(rosters):
                                embed = functions.my_embed(
                                    "Who Has...",
                                    "Command to find who currently has a particular player on their roster.",
                                    discord.Colour.blue(),
                                    f"Owner of {first_name} {last_name}",
                                    "None",
                                    False,
                                    bot,
                                )
                                break
                            else:
                                continue
                else:
                    embed = "No player found with those parameters, please try again!"
            else:
                embed = "Please run add-league command, no Sleeper League connected."
        else:
            embed = "Please run add-league command, no Sleeper League connected."
    return embed
