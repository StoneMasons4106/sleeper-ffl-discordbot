import discord

async def kick(ctx, user: discord.Member, *, reason=None):
    if ctx.guild == None:
        message = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        if ctx.author.guild_permissions.administrator:
            await user.kick(reason=reason)
            message = f"{user} has been ousted for being sassy!"
        else:
            message = 'You do not have access to this command.'
    return message


async def ban(ctx, user: discord.Member, *, reason=None):
    if ctx.guild == None:
        message = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:
        if ctx.author.guild_permissions.administrator:
            await user.ban(reason=reason)
            message = f"{user} has been exiled for treason!"
        else:
            message = 'You do not have access to this command.'
    return message


async def unban(ctx, member):
    if ctx.guild == None:
        message = 'This command is only available when sent in a guild rather than a DM. Try again there.'
    else:    
        if ctx.author.guild_permissions.administrator:
            banned_users = ctx.guild.bans()
            if '#' in member:
                member_name, member_discriminator = member.split('#')
                async for ban_entry in banned_users:
                    user = ban_entry.user
                    if (user.name, user.discriminator) == (member_name, member_discriminator):
                        await ctx.guild.unban(user)
                        message = f"{user} has been welcomed back! Shower them with gifts!"
            else:
                async for ban_entry in banned_users:
                    user = ban_entry.user
                    if user.name == member:
                        await ctx.guild.unban(user)
                        message = f"{user} has been welcomed back! Shower them with gifts!"
        else:
            message = 'You do not have access to this command.'
    return message