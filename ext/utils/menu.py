import asyncio
import inspect

import discord
from discord import User, Reaction
from discord.ext.commands import Bot


class Menu:
    default_emoji = [u'\u0031\u20e3', u'\u0032\u20e3', u'\u0033\u20e3', u'\u0034\u20e3', u'\u0035\u20e3',
                     u'\u0036\u20e3', u'\u0037\u20e3', u'\u0038\u20e3', u'\u0039\u20e3', u'\u0030\u20e3']

    menus = []

    def __init__(self, bot: Bot, text: str, callbacks: list, emojis: list = None, delete_after: float = None):

        if len(callbacks) > 10 and emojis is None:
            raise ValueError('Default emojis parameter does not support more than 10 callbacks.')

        if not all(map(inspect.iscoroutinefunction, callbacks)):
            raise ValueError('One or more callbacks not coroutine.')

        if emojis is not None:
            if len(callbacks) != len(emojis):
                raise ValueError('Number of emoji must match number of callbacks.')
        else:
            emojis = Menu.default_emoji[:len(callbacks)]

        self.bot = bot
        self.text = text
        self.delete_after = delete_after

        self.callback_map = dict(zip(emojis, callbacks))
        pass
        self.bot.add_listener(self._handle_menu, 'on_reaction_add')
        # if self.delete_after:
        #     self.bot.add_listener(self._handle_menu_delete, 'on_message_delete')

    async def _handle_menu(self, reaction: Reaction, user: User):
        if user == self.bot.user:
            return
        if reaction.message.id in Menu.menus:
            if reaction.emoji in self.callback_map.keys():
                await self.callback_map[reaction.emoji](reaction, user)
            # because the rate limit is this low for some reason
            # ~~TODO: not hard code this.~~
            # apparently not necessary?
            # await asyncio.sleep(0.25)
            await self.bot.remove_reaction(reaction.message, reaction.emoji, user)

    # async def _handle_menu_delete(self, message):
    #     if message in Menu.menus:
    #         Menu.menus.remove(message)

    async def send(self, destination):
        message = await self.bot.send_message(destination, self.text)
        Menu.menus.append(message.id)
        for emoji in self.callback_map.keys():
            await self.bot.add_reaction(message, emoji)

        if self.delete_after is not None:
            async def delete():
                await asyncio.sleep(self.delete_after, loop=self.bot.loop)
                await self.bot.delete_message(message)
                Menu.menus.remove(message)

            discord.compat.create_task(delete(), loop=self.bot.loop)
