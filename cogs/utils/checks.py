from discord.ext import commands

from bot import bot


# Checks

def owner_check(ctx):
    return ctx.message.author.id == str(bot.config['discord']['owner'])


# Decorators
def is_owner():
    return commands.check(lambda ctx: owner_check(ctx))
