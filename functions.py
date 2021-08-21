# Import needed libraries

import discord
import os
import pymongo
import pendulum
import constants
if os.path.exists("env.py"):
    import env


# Define Environment Variables

MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_CONN = pymongo.MongoClient(MONGO_URI)
MONGO = pymongo.MongoClient(MONGO_URI)[MONGO_DBNAME]


# Get Custom Prefixes

def get_prefix(bot, message):
    existing_prefix = MONGO.prefixes.find_one(
                {"server": str(message.guild.id)})
    MONGO_CONN.close()
    if existing_prefix:
        my_prefix = existing_prefix["prefix"]
    else:
        my_prefix = '$'
    return my_prefix


# Get Existing Server League Object from Mongo

def get_existing_league(ctx):
    existing_league = MONGO.servers.find_one(
                {"server": str(ctx.message.guild.id)})
    MONGO_CONN.close()
    return existing_league


# Get Existing Player Object from Mongo

def get_existing_player(args):
    existing_player = MONGO.players.find_one(
                {"name": f'{args[0]} {args[1]}', "team": args[2]})
    MONGO_CONN.close()
    return existing_player


# Set Embed for Discord Bot Responses

def my_embed(title, description, color, name, value, inline, ctx):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=ctx.me.display_name, icon_url=ctx.me.avatar_url)
    return embed


# Get Current Week

def get_current_week():
    today = pendulum.today(tz='America/New_York')
    starting_week = pendulum.datetime(constants.STARTING_YEAR, constants.STARTING_MONTH, constants.STARTING_DAY, tz='America/New_York')
    if starting_week.is_future():
        future = True
        week = 1
    else:
        future = False
        week = today.diff(starting_week).in_weeks() + 1
    return week, future


# Get Game Stats for a Particular Player

def get_game_stats(sportradar_id, game, args):
    statistics_string = ''
    if args[3] == 'K':
        if game["statistics"]["home"]["alias"] == args[2]:
            for player in game["statistics"]["home"]["field_goals"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Field Goals:\n{player["made"]}/{player["attempts"]}, {player["longest"]} Long\n\n'
            for player in game["statistics"]["home"]["extra_points"]["kicks"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Extra Points:\n{player["made"]}/{player["attempts"]}\n\n'
        else:
            for player in game["statistics"]["away"]["field_goals"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Field Goals:\n{player["made"]}/{player["attempts"]}, {player["longest"]} Long\n\n'
            for player in game["statistics"]["away"]["extra_points"]["kicks"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Extra Points:\n{player["made"]}/{player["attempts"]}\n\n'
    else:
        if game["statistics"]["home"]["alias"] == args[2]:
            for player in game["statistics"]["home"]["rushing"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Rushing:\n{player["avg_yards"]} ypc, {player["attempts"]} att, {player["yards"]} yds, {player["touchdowns"]} TD\n\n'
            for player in game["statistics"]["home"]["receiving"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Receiving:\n{player["receptions"]} rec, {player["yards"]} yds, {player["avg_yards"]} ypr, {player["touchdowns"]} TD\n\n'
            for player in game["statistics"]["home"]["passing"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Passing:\n{player["attempts"]} att, {player["completions"]} cmp, {player["cmp_pct"]}% cmp, {player["yards"]} yds, {player["avg_yards"]} ypa, {player["touchdowns"]} TD, {player["interceptions"]} INT, {player["sacks"]} sck\n\n'
            for player in game["statistics"]["home"]["fumbles"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Fumbles:\n{player["fumbles"]} fum, {player["lost_fumbles"]} lost fum\n\n'
        else:
            for player in game["statistics"]["away"]["rushing"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Rushing:\n{player["avg_yards"]} ypc, {player["attempts"]} att, {player["yards"]} yds, {player["touchdowns"]} TD\n\n'
            for player in game["statistics"]["away"]["receiving"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Receiving:\n{player["receptions"]} rec, {player["yards"]} yds, {player["avg_yards"]} ypr, {player["touchdowns"]} TD\n\n'
            for player in game["statistics"]["away"]["passing"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Passing:\n{player["attempts"]} att, {player["completions"]} cmp, {player["cmp_pct"]}% cmp, {player["yards"]} yds, {player["avg_yards"]} ypa, {player["touchdowns"]} TD, {player["interceptions"]} INT, {player["sacks"]} sck\n\n'
            for player in game["statistics"]["away"]["fumbles"]["players"]:
                if sportradar_id == player["id"]:
                    statistics_string += f'Fumbles:\n{player["fumbles"]} fum, {player["lost_fumbles"]} lost fum\n\n'
    
    return statistics_string


# Get Total Fantasy Points for a Particular Player

def get_ff_points(sportradar_id, league, game, args):
    total = float(0)
    if args[3] == 'K':
        if game["statistics"]["home"]["alias"] == args[2]:
            for player in game["statistics"]["home"]["field_goals"]["players"]:
                if sportradar_id == player["id"]:
                    total = total + (float(league["scoring_settings"]["fgm_0_19"]) * float(player["made_19"])) + (float(league["scoring_settings"]["fgm_20_29"]) * float(player["made_29"])) + (float(league["scoring_settings"]["fgm_30_39"]) * float(player["made_39"])) + (float(league["scoring_settings"]["fgm_40_49"]) * float(player["made_49"])) + (float(league["scoring_settings"]["fgm_50p"]) * float(player["made_50"])) - (float(league["scoring_settings"]["fgmiss"]) * float(player["missed"]))
            for player in game["statistics"]["home"]["extra_points"]["kicks"]["players"]:
                if sportradar_id == player["id"]:
                    total = total - (float(league["scoring_settings"]["xpmiss"]) * float(player["missed"])) + (float(league["scoring_settings"]["xpm"]) * float(player["made"]))
        else:
            for player in game["statistics"]["away"]["field_goals"]["players"]:
                if sportradar_id == player["id"]:
                    total = total + (float(league["scoring_settings"]["fgm_0_19"]) * float(player["made_19"])) + (float(league["scoring_settings"]["fgm_20_29"]) * float(player["made_29"])) + (float(league["scoring_settings"]["fgm_30_39"]) * float(player["made_39"])) + (float(league["scoring_settings"]["fgm_40_49"]) * float(player["made_49"])) + (float(league["scoring_settings"]["fgm_50p"]) * float(player["made_50"])) - (float(league["scoring_settings"]["fgmiss"]) * float(player["missed"]))
            for player in game["statistics"]["away"]["extra_points"]["kicks"]["players"]:
                if sportradar_id == player["id"]:
                    total = total - (float(league["scoring_settings"]["xpmiss"]) * float(player["missed"])) + (float(league["scoring_settings"]["xpm"]) * float(player["made"]))
    else:
        if game["statistics"]["home"]["alias"] == args[2]:
            for player in game["statistics"]["home"]["rushing"]["players"]:
                if sportradar_id == player["id"]:
                    total = total + (float(league["scoring_settings"]["rush_yd"]) * float(player["yards"])) + (float(league["scoring_settings"]["rush_td"]) * float(player["touchdowns"]))
            for player in game["statistics"]["home"]["receiving"]["players"]:
                if sportradar_id == player["id"]:
                   total = total + (float(league["scoring_settings"]["rec"]) * float(player["receptions"])) + (float(league["scoring_settings"]["rec_td"]) * float(player["touchdowns"])) + (float(league["scoring_settings"]["rec_yd"]) * float(player["yards"]))
            for player in game["statistics"]["home"]["passing"]["players"]:
                if sportradar_id == player["id"]:
                    total = total - (float(league["scoring_settings"]["pass_int"]) * float(player["interceptions"])) + (float(league["scoring_settings"]["pass_yd"]) * float(player["yards"])) + (float(league["scoring_settings"]["pass_td"]) * float(player["touchdowns"]))
            for player in game["statistics"]["home"]["fumbles"]["players"]:
                if sportradar_id == player["id"]:
                   total = total - (float(league["scoring_settings"]["fum_lost"]) * float(player["lost_fumbles"])) - (float(league["scoring_settings"]["fum"]) * float(player["fumbles"]))
        else:
            for player in game["statistics"]["away"]["rushing"]["players"]:
                if sportradar_id == player["id"]:
                    total = total + (float(league["scoring_settings"]["rush_yd"]) * float(player["yards"])) + (float(league["scoring_settings"]["rush_td"]) * float(player["touchdowns"]))
            for player in game["statistics"]["away"]["receiving"]["players"]:
                if sportradar_id == player["id"]:
                    total = total + (float(league["scoring_settings"]["rec"]) * float(player["receptions"])) + (float(league["scoring_settings"]["rec_td"]) * float(player["touchdowns"])) + (float(league["scoring_settings"]["rec_yd"]) * float(player["yards"]))
            for player in game["statistics"]["away"]["passing"]["players"]:
                if sportradar_id == player["id"]:
                    total = total - (float(league["scoring_settings"]["pass_int"]) * float(player["interceptions"])) + (float(league["scoring_settings"]["pass_yd"]) * float(player["yards"])) + (float(league["scoring_settings"]["pass_td"]) * float(player["touchdowns"]))
            for player in game["statistics"]["away"]["fumbles"]["players"]:
                if sportradar_id == player["id"]:
                    total = total - (float(league["scoring_settings"]["fum_lost"]) * float(player["lost_fumbles"])) - (float(league["scoring_settings"]["fum"]) * float(player["fumbles"]))                   
    
    return total