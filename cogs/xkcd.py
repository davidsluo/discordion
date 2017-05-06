import asyncio
import difflib
import logging
from json import JSONDecodeError

import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, cooldown, Context
from peewee import CharField, IntegerField, TextField, fn

from cogs.utils import checks
from cogs.utils.database import BaseModel, db

logger = logging.getLogger(__name__)


class Comic(BaseModel):
    num = IntegerField(unique=True)
    month = CharField()
    year = CharField()
    day = CharField()
    link = CharField()
    title = CharField()
    safe_title = CharField()
    img = CharField()
    alt = TextField()
    transcript = TextField()
    news = TextField()


class XKCD:
    def __init__(self, bot: Bot):
        self.bot = bot
        Comic.create_table(fail_silently=True)
        self.bot.loop.create_task(self.auto_index_task())

    async def auto_index_task(self):
        while True:
            await self.index_comics()
            self.index.reset_cooldown()
            await asyncio.sleep(60 * 60 * 24)

    async def index_comics(self):
        logger.info('Indexing xkcd comics.')

        async def fetch(sem, url, session):
            async with sem:
                async with session.get(url) as response:
                    logging.debug('Retrieving comic from {0}.'.format(url))
                    try:
                        return await response.json()
                    except JSONDecodeError:
                        return None

        latest_url = 'https://xkcd.com/info.0.json'
        url_fmt = 'https://xkcd.com/{0}/info.0.json'
        sem = asyncio.Semaphore(100)

        async with aiohttp.ClientSession() as session:

            try:
                last_archived = Comic.select().order_by(Comic.num.desc()).get().num
            except Comic.DoesNotExist:
                last_archived = 0

            latest_response = await fetch(sem, latest_url, session)
            if latest_response is not None:
                latest = latest_response['num']
            else:
                await self.bot.say('Failed to get latest comic number.', delete_after=30)
                return

            if latest > last_archived:
                tasks = []

                for i in range(last_archived + 1, latest + 1):
                    task = asyncio.ensure_future(fetch(sem, url_fmt.format(i), session))
                    tasks.append(task)

                responses = asyncio.gather(*tasks)
                new_comics = [{'month': int(r.pop('month')),
                               'day': int(r.pop('day')),
                               'year': int(r.pop('year')),
                               **r}
                              for r in await responses if r is not None]
                with db.atomic():
                    for i in range(0, len(new_comics), 100):
                        Comic.insert_many(new_comics[i:i + 100]).execute()

    @commands.command(hidden=True)
    @cooldown(rate=1, per=3600 * 12)
    @checks.is_owner()
    async def index(self):
        """
        Manually update database of comics. Automatically runs once a day.
        """
        message = await self.bot.say('Indexing comics...')
        await self.bot.type()
        await self.index_comics()
        await self.bot.edit_message(message, new_content='Comics indexed.')

    @commands.command(pass_context=True)
    async def xkcd(self, ctx: Context, *, comic=None):
        """
        Get an xkcd comic.
        Args:
            comic: The number or title of the comic to retrieve. 
        """
        link_fmt = 'https://xkcd.com/{0}'
        if comic is None:
            try:
                comic = Comic.select().order_by(Comic.num.desc()).get().num
            except Comic.DoesNotExist:
                await self.bot.say('No comics indexed. Index comics by running {0}index.'.format(ctx.prefix))
                return
        try:
            comic = int(comic)
        except ValueError:
            pass

        if isinstance(comic, int):
            try:
                c = Comic.get(Comic.num == comic)
            except Comic.DoesNotExist:
                await self.bot.say('Comic does not exist.', delete_after=30)
            else:
                await self.bot.say(link_fmt.format(c.num))
        elif isinstance(comic, str):
            try:
                c = Comic.get(Comic.title == comic)
            except Comic.DoesNotExist:
                try:
                    c = Comic.get(fn.Lower(Comic.title) == comic.lower())
                except Comic.DoesNotExist:
                    possibilities = [comic.title for comic in Comic.select()]
                    close = difflib.get_close_matches(comic, possibilities=possibilities)
                    if len(close) > 0:
                        await self.bot.say('Comic not found. Did you mean:\n{0}'.format('\n'.join(close)))
                    else:
                        await self.bot.say('Comic not found.')
                    return

            await self.bot.say(link_fmt.format(c.num))


def setup(bot):
    bot.add_cog(XKCD(bot))
