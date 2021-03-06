import discord
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
                                    roster_id = transaction["roster_ids"][0]
                                    for roster in rosters:
                                        if roster["roster_id"] == roster_id:
                                            this_roster = roster
                                            break
                                        else:
                                            continue
                                    for user in users:
                                        if this_roster["owner_id"] == user["user_id"]:
                                            username = user["display_name"]
                                            break
                                        else:
                                            continue
                                    if transaction["drops"]:
                                        transactions_string += f'{username} dropped '
                                    drop_count = 0
                                    try:
                                        for drop in transaction["drops"]:
                                            drop_count = drop_count + 1
                                            existing_player = MONGO.players.find_one({"id": str(drop)})
                                            if drop_count != 1:
                                                transactions_string += f', {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            else:
                                                transactions_string += f'{existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            MONGO_CONN.close()
                                    except:
                                        pass
                                    try:
                                        if transaction["adds"]:
                                            if transaction["drops"]:
                                                transactions_string += '\n'
                                            transactions_string += f'{username} added '
                                        add_count = 0
                                        for add in transaction["adds"]:
                                            add_count = add_count + 1
                                            existing_player = MONGO.players.find_one({"id": str(add)})
                                            if add_count != 1:
                                                transactions_string += f', {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            else:
                                                transactions_string += f'{existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            MONGO_CONN.close()
                                    except:
                                        pass
                                    transactions_string += '\n\n'
                                elif transaction["type"] == 'waiver':
                                    roster_id = transaction["roster_ids"][0]
                                    for roster in rosters:
                                        if roster["roster_id"] == roster_id:
                                            this_roster = roster
                                            break
                                        else:
                                            continue
                                    for user in users:
                                        if this_roster["owner_id"] == user["user_id"]:
                                            username = user["display_name"]
                                        else:
                                            continue
                                    if transaction["adds"]:
                                        transactions_string += f'{username} added '
                                    add_count = 0
                                    try:
                                        for add in transaction["adds"]:
                                            add_count = add_count + 1
                                            existing_player = MONGO.players.find_one({"id": str(add)})
                                            if add_count != 1:
                                                transactions_string += f', {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            else:
                                                transactions_string += f'{existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            MONGO_CONN.close()
                                    except:
                                        pass
                                    try:
                                        if transaction["drops"]:
                                            if transaction["adds"]:
                                                transactions_string += '\n'
                                            transactions_string += f'{username} dropped '
                                        drop_count = 0
                                        for drop in transaction["drops"]:
                                            drop_count = drop_count + 1
                                            existing_player = MONGO.players.find_one({"id": str(drop)})
                                            if drop_count != 1:
                                                transactions_string += f', {existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            else:
                                                transactions_string += f'{existing_player["name"]} - {existing_player["team"]} {existing_player["position"]}'
                                            MONGO_CONN.close()
                                    except:
                                        pass
                                    transactions_string += '\n\n'
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