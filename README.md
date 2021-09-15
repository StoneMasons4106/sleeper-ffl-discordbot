# Sleeper Fantasy Football Discord Bot

This Discord Bot is powered by the [Sleeper API Wrapper](https://github.com/SwapnikKatkoori/sleeper-api-wrapper) for providing granular information about one's Sleeper Fantasy Football league, right to Discord. If you wish to donate to the project, here's my [Patreon](https://www.patreon.com/stonemasons).

* IMPORTANT:
    * Please make sure that the Permissions for Slash Commands are enabled, or recent development of the bot WON'T WORK in your server. If you already have the bot in your server, go to server settings, roles, Sleeper-FFL, and under Permissions, search Application Commands. Allow and save. If this still doesn't work, without kicking the bot, use the invite link below under setup, and reinvite the bot.


## Features

* Help command with full list of commands, categories, and helpful links to Github, Patreon and Top.gg.
    * Use the syntax (prefix)help (command) to get details on a specific command, and expected syntax.

* Specific information about your league such as the names, members, trade deadline, and starting week of the playoffs.

* See your matchups and scoreboards for the current week.

* Check your current total league standings.

* See what players are trending a certain direction, such as being added or dropped.

* See your league mate's roster, or a portion of it.

* Check on a player's roster and injury status.

* Check the current weather or forecast for the area of a game based on city or zip code powered by [WeatherAPI](https://www.weatherapi.com/).

* Custom prefixes, in case you have another bot with the same default prefix.

* See who has a specific player.

* Access to game-stats, waiver-order, and transactions commands which will be available only to patrons on Patreon meeting the Patron Tier.

* Scheduled messages to keep your league up to date and notify you of the latest information following the schedule below:


## Scheduled Messages

* Current Matchups
    * Thursdays at 15:00 EST
* Current Scoreboard
    * Tuesdays at 12:00 EST
* Waiver Clearing Notifications
    * Tuesdays, Wednesdays, or Thursdays at 11:00 EST, depending on league settings
    * Only patrons will get this message


## Setup

Use the link [here](https://discord.com/api/oauth2/authorize?client_id=871087848311382086&permissions=122340240631&scope=bot%20applications.commands) to invite the bot to your Discord server.

Default Prefix: $

* Finish setting up by running the following commands:
    * add-league:
        * $add-league sleeper_league_id (Example: 726571239501557767)
    * set-channel:
        * $set-channel discord_channel_id (Example: 872626056258023484)
    * set-score-type
        * $set-score-type pts_ppr/pts_half_ppr/pts_std


## Issues

Please post any issues in the Issues section of this repo. Thank you.