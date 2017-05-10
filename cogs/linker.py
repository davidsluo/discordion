import difflib

from discord.ext import commands
from discord.ext.commands import Context
from peewee import CharField
from peewee import IntegrityError

from cogs.utils import checks
from cogs.utils.database import PerServerModel, Server


class Link(PerServerModel):
    name = CharField(unique=True)
    text = CharField()


class Linker:
    def __init__(self, bot):
        self.bot = bot

        Link.create_table(fail_silently=True)

    @commands.group(
        aliases=['links', 'l', 'tag', 'tags', 't'],
        invoke_without_command=True,
        pass_context=True
    )
    async def link(self, ctx: Context, name=None):
        """
        Get a link.
        Args:
            name:
                The name of the link to be retrieved. 
        """
        if name:
            try:
                link = Link.get((Link.server == ctx.message.server.id) | (Link.server == None), Link.name == name)
            except Link.DoesNotExist:
                possibilities = [l.name for l in Link.select()]
                close = difflib.get_close_matches(name, possibilities=possibilities)
                if len(close) > 0:
                    await self.bot.say('Link `{0}` not found. Did you mean:\n{1}'.format(name, '\n'.join(close)))
                else:
                    await self.bot.say('Link `{0}` not found.'.format(name))
                return

            await self.bot.say(link.text)
        else:
            links = Link.select().where((Link.server == ctx.message.server.id) | (Link.server == None))
            message = '\n'.join(['`{0}` - `{1}`'.format(
                link.name,
                link.text[:75] + (link.text[75:] and '...')
            ) for link in links])
            await self.bot.say('Links:\n{0}'.format(message))

    @link.command(
        hidden=True,
        pass_context=True
    )
    @checks.is_owner()
    async def all(self, ctx: Context, name=None):
        """
                Get a link.
                Args:
                    name:
                        The name of the link to be retrieved. 
                """
        if name:
            try:
                link = Link.get(Link.name == name)
            except Link.DoesNotExist:
                await self.bot.say('Link `{0}` not found.'.format(name), delete_after=30)
                return

            await self.bot.say(link.text)
        else:
            links = Link.select()
            message = '\n'.join(['`{0}` - `{1}`'.format(
                link.name,
                link.text[:75] + (link.text[75:] and '...')
            ) for link in links])
            await self.bot.say('Links:')
            await self.bot.say(message)

    @link.command(hidden=True)
    @checks.is_owner()
    async def globalize(self, *, name):
        try:
            link = Link.get(Link.name == name)
        except Link.DoesNotExist:
            await self.bot.say('Link `{0}` not found.'.format(name), delete_after=30)
            return

        link.server = None
        link.save()
        await self.bot.say('\N{THUMBS UP SIGN}')

    @link.command(
        aliases=['a'],
        pass_context=True
    )
    async def add(self, ctx, name, *, text):
        """
        Add a new link.
            name: 
                The name of the link.
            text: 
                The text to associate with the name.
        """
        link = Link(name=name, text=text, server=Server.get_server(ctx.message.server.id))
        try:
            link.save()
        except IntegrityError:
            await self.bot.say('`{0}` already exists.'.format(name), delete_after=30)
            return

        await self.bot.say('Added `{0}`:\n`{1}`'.format(name, text))

    @link.command(
        aliases=['d', 'del', 'remove', 'r', 'rm'],
        pass_context=True
    )
    async def delete(self, ctx, name):
        """
        Delete a link.
            name: 
                The link to delete. 
        """
        try:
            link = Link.get(Link.server == ctx.message.server.id, Link.name == name)
        except Link.DoesNotExist:
            await self.bot.say('Link `{0}` not found.'.format(name), delete_after=30)
            return

        link.delete_instance()
        await self.bot.say('Deleted `{0}`.'.format(name))


def setup(bot):
    bot.add_cog(Linker(bot))


def teardown(bot):
    # this is ghetto af.
    # TODO: make this not ghetto af
    del Link.server.rel_model._meta.reverse_rel['{0}_set'.format(Link.__name__.lower())]
