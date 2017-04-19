from discord.ext import commands


class Soundboard:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        description='Interact with the soundboard',
        brief='Rick Roll on demand',
        aliases=['sb']
    )
    async def soundboard(self):
        pass


def setup(bot):
    bot.add_cog(Soundboard(bot))
