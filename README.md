# Sleeper Fantasy Football Discord Bot

This Discord Bot is powered by the [Sleeper API Wrapper](https://github.com/SwapnikKatkoori/sleeper-api-wrapper) for providing granular information about one's Sleeper Fantasy Football league, right to Discord. If you wish to donate to the project, here's my [Patreon](https://www.patreon.com/stonemasons), or you can subscribe to our [Discord](https://discord.gg/4MSEK8cpfp).

* IMPORTANT:
    * Now that Slash Commands are deployed to the live bot, if you are having issues with seeing the commands, without kicking the bot, use the invite link below under Setup, and reinvite the bot to ensure access to the applications.commands scope.


## Features

* Bot-info command server and member counts, patron commands, and helpful links to Github, Discord, Patreon and Top.gg.

* Specific information about your league such as the names, members, trade deadline, and starting week of the playoffs.

* See your matchups and scoreboards for the current week.

* Check your current total league standings.

* See what players are trending a certain direction, such as being added or dropped.

* See your league mate's roster, or a portion of it.

* Check on a player's roster and injury status.

* Check the current weather or forecast for the area of a game based on city or zip code powered by [WeatherAPI](https://www.weatherapi.com/).

* See who has a specific player.

* Access to waiver-order, and transactions commands which will be available only to patrons on Patreon meeting the Patron Tier.

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

Use the link [here](https://discord.com/oauth2/authorize?client_id=871087848311382086&permissions=8&scope=applications.commands%20bot) to invite the bot to your Discord server.

Prefix: /

* Finish setting up by running the following commands:
    * add-league:
        * /add-league sleeper_league_id (Example: 726571239501557767)
        * This MUST be updated every season as the league ID updates every offseason.
    * set-channel:
        * /set-channel discord_channel_id (Example: 872626056258023484)
    * set-score-type
        * /set-score-type pts_ppr/pts_half_ppr/pts_std

* OPTIONAL: Currently there is no public way to access news updates via API or webhook, but it looks like the guys at Sleeper worked on something of their own that you can utilize in your server.
    * If you'd like news functionality, join [this server](https://discord.gg/5UuU85sQ9h), and follow the breaking, hype, minor, and defense channels in your desired server.


## Issues

* Please post any issues in the Issues section of this repo. Thank you.