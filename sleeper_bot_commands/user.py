import discord
from discord.ext import commands
from discord.utils import find
import os
import sleeper_wrapper
import functions
if os.path.exists("env.py"):
    import env


def user_info(ctx, display_name: str):
    existing_league = functions.get_existing_league(ctx)
    if existing_league:
        if "league" in existing_league:
            league_id = existing_league["league"]
            users = sleeper_wrapper.League(int(league_id)).get_users()
            count = 0
            for user in users:
                count = count + 1
                if user["display_name"] == display_name:
                    user_object = sleeper_wrapper.User(int(user["user_id"])).get_user()
                    embed = functions.my_embed('User Information', 'Displays information for the specified user in your league.', discord.Colour.blue(), 'User ID', user["user_id"], False, ctx)
                    embed.add_field(name='Username', value=user_object["username"], inline=False)
                    embed.add_field(name='Display Name', value=user["display_name"], inline=False)
                    if user["is_owner"] == True:
                        commissioner = 'Yes'
                    else:
                        commissioner = 'No'
                    embed.add_field(name='Commissioner?', value=commissioner, inline=False)
                    embed.set_thumbnail(url=f'https://sleepercdn.com/avatars/thumbs/{user["avatar"]}')
                    break
                elif count == len(users):
                    embed = 'No users found with this display name. Please try again!'
                else:
                    continue
        else:
            embed = 'No league specified, run add-league command to complete setup.'
    else:
        embed = 'No league specified, run add-league command to complete setup.'
    return embed 