from datetime import datetime, timedelta

from discord import Message, Forbidden
from discord.ext import commands
from discord.ext.commands import Context, Bot

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


def setup(bot):
    bot.add_cog(Admin(bot))
