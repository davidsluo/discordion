from discord.ext import commands
from peewee import IntegrityError

from ext.linker.models import Link


class Linker:
    def __init__(self, bot):
        self.bot = bot

        Link.create_table(fail_silently=True)

    @commands.group(
        aliases=['l'],
        invoke_without_command=True
    )
    async def link(self, name=None):
        """
        Get a link.
        :param name: The name of the link to be retrieved. 
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
            message = '\n'.join(['`{0}` - `{1}`'.format(link.name, link.text) for link in links])
            await self.bot.say('Links:')
            await self.bot.say(message)

    @link.command(
        aliases=['a']
    )
    async def add(self, name, *, text):
        """
        Add a new link.
        :param name: The name of the link.
        :param text: The text to associate with the name.
        """
        link = Link(name=name, text=text)
        try:
            link.save()
        except IntegrityError:
            await self.bot.say('`{0}` already exists.'.format(name), delete_after=30)
            return

        await self.bot.say('Added `{0}`:\n`{1}`'.format(name, text))

    @link.command(
        aliases=['d', 'del', 'remove', 'r', 'rm']
    )
    async def delete(self, name):
        """
        Delete a link.
        :param name: The link to delete. 
        """
        try:
            link = Link.get(Link.name == name)
        except Link.DoesNotExist:
            await self.bot.say('Link `{0}` not found.'.format(name), delete_after=30)
            return

        link.delete_instance()
        await self.bot.say('Deleted `{0}`.'.format(name))


def setup(bot):
    bot.add_cog(Linker(bot))
