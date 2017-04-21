from discord.ext import commands

INVITE_FORMAT = 'https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=0'

__all__ = ['Admin']


class Admin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='invitelink',
        aliases=['invite'],
        description='Get the invite linker for this bot.'
    )
    async def invite_link(self):
        await self.bot.say(INVITE_FORMAT.format(self.bot.config['discord']['client_id']))


def setup(bot):
    bot.add_cog(Admin(bot))
