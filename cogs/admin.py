import inspect

import requests
from discord import InvalidArgument, Game
from discord.ext import commands
from discord.ext.commands import Bot, cooldown

from cogs.utils import checks


class Admin:
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    @cooldown(rate=2, per=3600)
    async def username(self, username):
        await self.bot.edit_profile(username=username)
        await self.bot.say('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def avatar(self, url):
        r = requests.get(url)

        if r.status_code != 200:
            await self.bot.say('Got error code `{0}` while downloading avatar.'.format(r.status_code))
            return

        try:
            await self.bot.edit_profile(avatar=r.content)
        except InvalidArgument:
            await self.bot.say('Wrong format for avatar.')
        else:
            await self.bot.say('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @checks.is_owner()
    @cooldown(rate=2, per=60)
    async def presence(self, *, presence: Game):
        await self.bot.change_presence(game=presence)
        await self.bot.say('\N{THUMBS UP SIGN}')

    # Stuff below here is from Rapptz's admin cog
    # https://github.com/Rapptz/RoboDanny/blob/master/cogs/admin.py
    @commands.command(hidden=True)
    @checks.is_owner()
    async def load(self, *, module: str):
        """Loads a module."""
        if module in self.bot.extensions:
            await self.bot.say('Module already loaded.')
            return
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def unload(self, *, module: str):
        """Unloads a module."""

        lib = self.bot.extensions.get(module)
        if lib is None:
            await self.bot.say('No module found named {0}.'.format(module))
            return
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.is_owner()
    async def _reload(self, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.say(python.format(result))


def setup(bot):
    bot.add_cog(Admin(bot))
