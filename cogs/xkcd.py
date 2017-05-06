import asyncio
from json import JSONDecodeError

import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, cooldown, Context
from peewee import CharField, IntegerField, TextField, fn

from cogs.utils.database import BaseModel, db


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

    async def index_comics(self):
        async def fetch(sem, url, session):
            async with sem:
                async with session.get(url) as response:
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

    @commands.command()
    @cooldown(rate=1, per=3600 * 24)
    async def index(self):
        message = await self.bot.say('Indexing comics...')
        await self.bot.type()
        await self.index_comics()
        await self.bot.edit_message(message, new_content='Comics indexed.')

    @commands.command(pass_context=True)
    async def xkcd(self, ctx: Context, *, comic=None):
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
                    await self.bot.say('Comic does not exist.', delete_after=30)
                    return

            await self.bot.say(link_fmt.format(c.num))


def setup(bot):
    bot.add_cog(XKCD(bot))
