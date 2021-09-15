import discord
import os
import sleeper_wrapper
import functions
if os.path.exists("env.py"):
    import env



def my_league(ctx, bot):
    if ctx.guild == None:
        embed = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if "league" in existing_league:
                league_id = existing_league["league"]
                league = sleeper_wrapper.League(int(league_id)).get_league()
                users_object = sleeper_wrapper.League(int(league_id)).get_users()
                users = []
                for user in users_object:
                    users.append(user["display_name"])
                embed = functions.my_embed('Sleeper League Info', 'Sleeper League General Information', discord.Colour.blue(), 'Name', f'[{league["name"]}](https://sleeper.app/leagues/{league_id})', False, bot)
                embed.add_field(name='Members', value=", ".join(users), inline=False)
                embed.add_field(name='Quantity', value=len(users), inline=False)
                embed.add_field(name='Trade Deadline', value=f"Week {league['settings']['trade_deadline']}", inline=False)
                embed.add_field(name='Playoffs Start', value=f"Week {league['settings']['playoff_week_start']}", inline=False)
                if "score_type" in existing_league:
                    if existing_league["score_type"] == 'pts_ppr':
                        embed.add_field(name='Scoring Type', value='PPR', inline=False)
                    elif existing_league["score_type"] == 'pts_half_ppr':
                        embed.add_field(name='Scoring Type', value='Half PPR', inline=False)
                    elif existing_league["score_type"] == 'pts_std':
                        embed.add_field(name='Scoring Type', value='Standard', inline=False)
                else:
                    pass
            else:
                embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, bot)
        else:
            embed = functions.my_embed('Sleeper League Info', 'Sleeper League Name and Member Info', discord.Colour.blue(), 'Members', 'No league specified, run add-league command to complete setup.', False, bot)
    return embed


def my_league_standings(ctx, bot):
    if ctx.guild == None:
        embed = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:
        existing_league = functions.get_existing_league(ctx)
        if existing_league:
            if "league" in existing_league:
                league_id = existing_league["league"]
                users_object = sleeper_wrapper.League(int(league_id)).get_users()
                rosters_object = sleeper_wrapper.League(int(league_id)).get_rosters()
                filtered_roster_object = []
                for roster in rosters_object:
                    if roster["owner_id"] != None:
                        filtered_roster_object.append(roster)
                    else:
                        pass
                standings_object = sleeper_wrapper.League(int(league_id)).get_standings(filtered_roster_object, users_object)
                standings_string = ''
                count = 0
                for i in standings_object:
                    count = count + 1
                    standings_string += f'{str(count)}. {i[0]} / Record: {i[1]}-{i[2]} / Points For: {i[3]}\n'
                embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', standings_string, False, bot)
            else:
                embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', 'No league specified, run add-league command to complete setup.', False, bot)
        else:
            embed = functions.my_embed('Sleeper League Standings', 'Display Current Standings of Sleeper League', discord.Colour.blue(), 'Standings', 'No league specified, run add-league command to complete setup.', False, bot)
    return embed


def my_league_matchups(ctx, bot, week):
    if ctx.guild == None:
        embed = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        if week.isnumeric():
            if int(week) <= 18 and int(week) >= 1:
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(int(week))
                        if matchups:
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
                            embed = functions.my_embed('Current Week Matchups', f'Matchups for Week {week}', discord.Colour.blue(), 'Matchups', matchups_string, False, bot)
                        else:
                            embed = 'There are no matchups this week, try this command again during the season!'
                    else:
                        embed = 'Please run add-league command, no Sleeper League connected.'
                else:
                    embed = 'Please run add-league command, no Sleeper League connected.'
            else:
                embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
        else:
            embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
    return embed


def my_league_scoreboard(ctx, bot, week):
    if ctx.guild == None:
        embed = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:
        if week.isnumeric():
            if int(week) <= 18 and int(week) >= 1:
                existing_league = functions.get_existing_league(ctx)
                if existing_league:
                    if "league" in existing_league:
                        league_id = existing_league["league"]
                        users = sleeper_wrapper.League(int(league_id)).get_users()
                        rosters = sleeper_wrapper.League(int(league_id)).get_rosters()
                        matchups = sleeper_wrapper.League(int(league_id)).get_matchups(int(week))
                        if matchups:
                            sorted_matchups = sorted(matchups, key=lambda i: i["matchup_id"])
                            scoreboard_string = ''
                            count = 0
                            matchup_count = 1
                            for matchup in sorted_matchups:
                                count = count + 1
                                roster = next((roster for roster in rosters if roster["roster_id"] == matchup["roster_id"]), None)
                                user = next((user for user in users if user["user_id"] == roster["owner_id"]), None)
                                if (count % 2) == 0:
                                    matchup_count = matchup_count + 1
                                    scoreboard_string += f'{user["display_name"]} - {matchup["points"]}\n'
                                else:
                                    scoreboard_string += f'{str(matchup_count)}. {user["display_name"]} - {matchup["points"]} / '
                            embed = functions.my_embed(f'Week {week} Scoreboard', f'Scoreboard for Week {str(week)}', discord.Colour.blue(), 'Scoreboard', scoreboard_string, False, bot)
                        else:
                            embed = 'There are no matchups this week, try this command again during the season!'
                    else:
                        embed = 'Please run add-league command, no Sleeper League connected.'
                else:
                    embed = 'Please run add-league command, no Sleeper League connected.'
            else:
                embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
        else:
            embed = 'Invalid week number given. Choose a valid week between 1 and 18.'
    return embed