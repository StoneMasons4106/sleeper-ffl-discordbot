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


def set_channel(message, bot, channel_id: str):
    if message.guild == None:
        embed = "This command is only available when sent in a guild rather than a DM. Try again there."
    else:
        if message.author.guild_permissions.administrator:
            if channel_id.isnumeric():
                count = 0
                found = 0
                for channel in message.guild.channels:
                    count = count + 1
                    if isinstance(channel, discord.channel.TextChannel):
                        if str(channel.id) == str(channel_id):
                            found = 1
                            existing_channel = MONGO.servers.find_one(
                                {"server": str(message.guild.id)}
                            )
                            if existing_channel:
                                newvalue = {"$set": {"channel": str(channel_id)}}
                                MONGO.servers.update_one(existing_channel, newvalue)
                                MONGO_CONN.close()
                                embed = functions.my_embed(
                                    "Channel Connection Status",
                                    "Result of Channel Connection request",
                                    discord.Colour.blue(),
                                    "Channel",
                                    "Successfully updated your channel to "
                                    + str(channel_id)
                                    + "!",
                                    False,
                                    bot,
                                )
                                break
                            else:
                                server_channel_object = {
                                    "server": str(message.guild.id),
                                    "channel": channel_id,
                                }
                                MONGO.servers.insert_one(server_channel_object)
                                MONGO_CONN.close()
                                embed = functions.my_embed(
                                    "Channel Connection Status",
                                    "Result of Channel Connection request",
                                    discord.Colour.blue(),
                                    "Channel",
                                    "Successfully updated your channel to "
                                    + str(channel_id)
                                    + "!",
                                    False,
                                    bot,
                                )
                                break
                        elif count == len(message.guild.channels):
                            if found == 0:
                                embed = functions.my_embed(
                                    "Channel Connection Status",
                                    "Result of Channel Connection request",
                                    discord.Colour.blue(),
                                    "Channel",
                                    "Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.",
                                    False,
                                    bot,
                                )
                            else:
                                pass
                        else:
                            continue
                    elif count == len(message.guild.channels):
                        embed = functions.my_embed(
                            "Channel Connection Status",
                            "Result of Channel Connection request",
                            discord.Colour.blue(),
                            "Channel",
                            "Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.",
                            False,
                            bot,
                        )
                    else:
                        continue
            else:
                embed = functions.my_embed(
                    "Channel Connection Status",
                    "Result of Channel Connection request",
                    discord.Colour.blue(),
                    "Channel",
                    "Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.",
                    False,
                    bot,
                )
        else:
            embed = functions.my_embed(
                "Channel Connection Status",
                "Result of Channel Connection request",
                discord.Colour.blue(),
                "Channel",
                "You do not have access to this command, request failed.",
                False,
                bot,
            )
    return embed


def add_league(ctx, bot, league_id: str):
    if ctx.guild == None:
        embed = "This command is only available when sent in a guild rather than a DM. Try again there."
    else:
        if ctx.author.guild_permissions.administrator:
            if league_id.isnumeric():
                league = sleeper_wrapper.League(int(league_id)).get_league()
                if hasattr(league, "response"):
                    embed = functions.my_embed(
                        "Sleeper League Connection Status",
                        "Result of connection to Sleeper League request",
                        discord.Colour.blue(),
                        "Connection Status",
                        "Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id",
                        False,
                        bot,
                    )
                else:
                    existing_league = functions.get_existing_league(ctx)
                    if existing_league:
                        newvalue = {"$set": {"league": league_id}}
                        MONGO.servers.update_one(existing_league, newvalue)
                        MONGO_CONN.close()
                        embed = functions.my_embed(
                            "Sleeper League Connection Status",
                            "Result of connection to Sleeper League request",
                            discord.Colour.blue(),
                            "Connection Status",
                            "Successfully updated your Sleeper league to "
                            + league_id
                            + "!",
                            False,
                            bot,
                        )
                    else:
                        server_league_object = {
                            "server": str(ctx.guild.id),
                            "league": league_id,
                        }
                        MONGO.servers.insert_one(server_league_object)
                        MONGO_CONN.close()
                        embed = functions.my_embed(
                            "Sleeper League Connection Status",
                            "Result of connection to Sleeper League request",
                            discord.Colour.blue(),
                            "Connection Status",
                            "Successfully updated your Sleeper league to "
                            + league_id
                            + "!",
                            False,
                            bot,
                        )
            else:
                embed = functions.my_embed(
                    "Sleeper League Connection Status",
                    "Result of connection to Sleeper League request",
                    discord.Colour.blue(),
                    "Connection Status",
                    "Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id",
                    False,
                    bot,
                )
        else:
            embed = functions.my_embed(
                "Sleeper League Connection Status",
                "Result of connection to Sleeper League request",
                discord.Colour.blue(),
                "Connection Status",
                "You do not have access to this command, request failed.",
                False,
                bot,
            )
    return embed


def set_score_type(message, bot, score_type: str):
    if message.guild == None:
        embed = "This command is only available when sent in a guild rather than a DM. Try again there."
    else:
        if message.author.guild_permissions.administrator:
            if (
                score_type == "pts_ppr"
                or score_type == "pts_half_ppr"
                or score_type == "pts_std"
            ):
                existing_league = functions.get_existing_league(message)
                if existing_league:
                    if score_type == "pts_ppr":
                        score_type_output = "PPR"
                    elif score_type == "pts_half_ppr":
                        score_type_output = "Half PPR"
                    else:
                        score_type_output = "Standard"
                    newvalue = {"$set": {"score_type": score_type}}
                    MONGO.servers.update_one(existing_league, newvalue)
                    MONGO_CONN.close()
                    embed = functions.my_embed(
                        "Sleeper League Score Type",
                        "Result of attempt to update score type for your League",
                        discord.Colour.blue(),
                        "Score Type Request Status",
                        f"Successfully updated your score type to {score_type_output}!",
                        False,
                        bot,
                    )
                else:
                    if score_type == "pts_ppr":
                        score_type_output = "PPR"
                    elif score_type == "pts_half_ppr":
                        score_type_output = "Half PPR"
                    else:
                        score_type_output = "Standard"
                    score_type_object = {
                        "server": str(message.guild.id),
                        "score_type": score_type,
                    }
                    MONGO.servers.insert_one(score_type_object)
                    MONGO_CONN.close()
                    embed = functions.my_embed(
                        "Sleeper League Score Type",
                        "Result of attempt to update score type for your League",
                        discord.Colour.blue(),
                        "Score Type Request Status",
                        f"Successfully updated your score type to {score_type_output}!",
                        False,
                        bot,
                    )
            else:
                embed = "Invalid score_type argument. Please use either pts_std, pts_ppr, or pts_half_ppr."
        else:
            embed = functions.my_embed(
                "Sleeper League Score Type",
                "Result of attempt to update score type for your League",
                discord.Colour.blue(),
                "Score Type Request Status",
                "You do not have access to this command.",
                False,
                bot,
            )
    return embed
