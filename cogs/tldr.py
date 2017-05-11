import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot, cooldown

endpoint = 'http://api.smmry.com'


class TLDR:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api_key = self.bot.config['tldr']['smmry_api_key']

    @commands.command()
    @cooldown(rate=1, per=10)
    async def tldr(self, url, sentences=3):
        payload = {
            'SM_API_KEY': self.api_key,
            'SM_LENGTH': sentences,
            'SM_QUOTE_AVOID': None,
            'SM_KEYWORD_COUNT': 5,
            'SM_URL': url
        }

        r = requests.get(endpoint, params=payload)

        if r.status_code != 200:
            await self.bot.say('Unable to retrieve tldr. Error code {0}.'.format(r.status_code))
            return

        content = r.json()

        e = discord.Embed(title=content['sm_api_title'], url=url, description=content['sm_api_content'])
        e.set_footer(text='keywords: ' + ', '.join(content['sm_api_keyword_array']))

        await self.bot.say(embed=e)


def setup(bot: Bot):
    bot.add_cog(TLDR(bot))
