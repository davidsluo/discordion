import inspect
from discord import Message, Forbidden
from discord.ext import commands
from discord.ext.commands import Context, Bot

import cogs.utils.checks
from cogs.utils import checks

INVITE_FORMAT = 'https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=0'

__all__ = ['Admin']


class Admin:
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        name='invitelink',
        aliases=['invite']
    )
    async def invite_link(self):
        """
        Get the invite link for this bot.
        """
        await self.bot.say(INVITE_FORMAT.format(self.bot.config['discord']['client_id']))

    @commands.command(
        aliases=['cleanup', 'purge', 'clear'],
        pass_context=True
    )
    @commands.has_permissions(manage_channels=True)
    async def clean(self, ctx: Context, commands=False):
        """
        Clean up chat.
        Deletes all messages from the bot and optionally command calls as well.
        Args:
            commands:
                Optional (Yes/No).
                Whether to clean up command calls as well.
        """

        def is_bot(message: Message):
            return message.author == ctx.message.server.me

        def is_command(message: Message):
            return (len(message.content) > 1) and (message.content[0] == self.bot.command_prefix)

        if commands:
            def check(msg):
                return is_bot(msg) or is_command(msg)
        else:
            check = is_bot

        try:
            deleted = await self.bot.purge_from(ctx.message.channel, limit=1000, check=check)
        except Forbidden:
            await self.bot.say('Bot does not have permission to delete messages.', delete_after=30)
            return

        await self.bot.say('Deleted {0} message(s).'.format(len(deleted)), delete_after=30)

    # Stuff below here is from Rapptz's admin cog
    # https://github.com/Rapptz/RoboDanny/blob/master/cogs/admin.py
    @commands.command(hidden=True)
    @checks.is_owner()
    async def load(self, *, module: str):
        """Loads a module."""
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
