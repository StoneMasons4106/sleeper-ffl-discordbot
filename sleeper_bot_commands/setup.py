import discord
from discord.ext import commands
from discord.utils import find
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


def set_prefix(ctx, prefix: str):
    if ctx.author.guild_permissions.administrator:
        existing_prefix = MONGO.prefixes.find_one(
                {"server": str(ctx.message.guild.id)})
        if existing_prefix:
            newvalue = {"$set": {"prefix": prefix}}
            MONGO.prefixes.update_one(existing_prefix, newvalue)
            MONGO_CONN.close()
            embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
        else:
            server_prefix_object = {
                "server": str(ctx.message.guild.id),
                "prefix": prefix
            }
            MONGO.prefixes.insert_one(server_prefix_object)
            MONGO_CONN.close()
            embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'Successfully updated your prefix to '+prefix+'!', False, ctx)
    else:
        embed = functions.my_embed('Prefix Change Status', 'Result of Prefix change request', discord.Colour.blue(), 'Prefix', 'You do not have access to this command, request failed.', False, ctx)
    return embed


def set_channel(ctx, channel_id: str):
    if ctx.author.guild_permissions.administrator:
        if channel_id.isnumeric():
            count = 0
            found = 0
            for channel in ctx.message.guild.channels:
                count = count + 1
                if isinstance(channel, discord.channel.TextChannel):
                    if str(channel.id) == str(channel_id):
                        found = 1
                        existing_channel = MONGO.servers.find_one(
                                {"server": str(ctx.message.guild.id)})
                        if existing_channel:
                            newvalue = {"$set": {"channel": str(channel_id)}}
                            MONGO.servers.update_one(existing_channel, newvalue)
                            MONGO_CONN.close()
                            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                            break
                        else:
                            server_channel_object = {
                                "server": str(ctx.message.guild.id),
                                "channel": channel_id
                            }
                            MONGO.servers.insert_one(server_channel_object)
                            MONGO_CONN.close()
                            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Successfully updated your channel to '+str(channel_id)+'!', False, ctx)
                            break
                    elif count == len(ctx.message.guild.channels):
                        if found == 0:
                            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
                        else:
                            pass
                    else:
                        continue
                elif count == len(ctx.message.guild.channels):
                    embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
                else:
                    continue
        else:
            embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'Invalid channel ID. Try right clicking the Discord channel and hitting Copy ID.', False, ctx)
    else:
        embed = functions.my_embed('Channel Connection Status', 'Result of Channel Connection request', discord.Colour.blue(), 'Channel', 'You do not have access to this command, request failed.', False, ctx)
    return embed


def add_league(ctx, league_id: str):
    if ctx.author.guild_permissions.administrator:
        if league_id.isnumeric():
            league = sleeper_wrapper.League(int(league_id)).get_league()
            if hasattr(league, 'response'):
                embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id', False, ctx) 
            else:
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    newvalue = {"$set": {"league": league_id}}
                    MONGO.servers.update_one(existing_league, newvalue)
                    MONGO_CONN.close()
                    embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)                    
                else:
                    server_league_object = {
                        "server": str(ctx.message.guild.id),
                        "league": league_id
                    }
                    MONGO.servers.insert_one(server_league_object)
                    MONGO_CONN.close()
                    embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Successfully updated your Sleeper league to '+league_id+'!', False, ctx)                    
        else:
            embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'Invalid league ID. Try finding the ID using your league URL like so: https://sleeper.app/leagues/league_id', False, ctx)            
    else:
        embed = functions.my_embed('Sleeper League Connection Status', 'Result of connection to Sleeper League request', discord.Colour.blue(), 'Connection Status', 'You do not have access to this command, request failed.', False, ctx)
    return embed


def set_score_type(ctx, score_type: str):
    if ctx.author.guild_permissions.administrator:
        if score_type == 'pts_ppr' or score_type == 'pts_half_ppr' or score_type == 'pts_std': 
            existing_league = functions.get_existing_league(ctx)
            if existing_league:
                if score_type == 'pts_ppr':
                    score_type_output = 'PPR'
                elif score_type == 'pts_half_ppr':
                    score_type_output = 'Half PPR'
                else:
                    score_type_output = 'Standard' 
                newvalue = {"$set": {"score_type": score_type}}
                MONGO.servers.update_one(existing_league, newvalue)
                MONGO_CONN.close()
                embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type_output}!', False, ctx)
            else:
                if score_type == 'pts_ppr':
                    score_type_output = 'PPR'
                elif score_type == 'pts_half_ppr':
                    score_type_output = 'Half PPR'
                else:
                    score_type_output = 'Standard' 
                score_type_object = {
                    "server": str(ctx.message.guild.id),
                    "score_type": score_type
                }
                MONGO.servers.insert_one(score_type_object)
                MONGO_CONN.close()
                embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', f'Successfully updated your score type to {score_type_output}!', False, ctx)
        else:
            embed = 'Invalid score_type argument. Please use either pts_std, pts_ppr, or pts_half_ppr.'
    else:
        embed = functions.my_embed('Sleeper League Score Type', 'Result of attempt to update score type for your League', discord.Colour.blue(), 'Score Type Request Status', 'You do not have access to this command.', False, ctx)
    return embed