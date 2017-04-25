import asyncio

import discord
import inspect
from discord import User, Reaction, Emoji
from discord.ext.commands import Bot


class Menu:
    # default_emoji = [u'\u0031\u20e3', u'\u0032\u20e3', u'\u0033\u20e3', u'\u0034\u20e3', u'\u0035\u20e3',
    #                  u'\u0036\u20e3', u'\u0037\u20e3', u'\u0038\u20e3', u'\u0039\u20e3', u'\u0030\u20e3']

    menus = []

    def __init__(self, bot: Bot, text: str, delete_after: float = None):

        self.bot = bot
        self.text = text
        self.delete_after = delete_after

        self.callback_map = {}

        self.bot.add_listener(self._handle_menu, 'on_reaction_add')
        # if self.delete_after:
        #     self.bot.add_listener(self._handle_menu_delete, 'on_message_delete')

    def add_callback(self, emoji: (str, Emoji), callback):
        if not inspect.iscoroutinefunction(callback):
            raise ValueError('Callback must be coroutine.')

        self.callback_map[emoji] = callback

    def remove_callback(self, emoji: (str, Emoji)):
        return self.callback_map.pop(emoji)

    def callback(self, emoji: (str, Emoji)):
        """
        Decorator to make a coroutine a callback for the specified emoji.
        :param emoji: The Emoji
        :return: The decorator
        """

        def decorator(func):
            self.add_callback(emoji, func)
            return func

        return decorator

    async def _handle_menu(self, reaction: Reaction, user: User):
        if user == self.bot.user:
            return
        if reaction.message.id in Menu.menus:
            if reaction.emoji in self.callback_map.keys():
                await self.callback_map[reaction.emoji](reaction, user)
            # because the rate limit is this low for some reason
            # ~~TODO: not hard code this.~~
            # apparently not necessary?
            await asyncio.sleep(0.25)
            await self.bot.remove_reaction(reaction.message, reaction.emoji, user)

    async def _handle_menu_delete(self, message):
        if message in Menu.menus:
            Menu.menus.remove(message)

    async def _process_menu(self, message):
        Menu.menus.append(message.id)
        for emoji in self.callback_map.keys():
            await self.bot.add_reaction(message, emoji)

        if self.delete_after is not None:
            async def delete():
                await asyncio.sleep(self.delete_after, loop=self.bot.loop)
                await self.bot.delete_message(message)
                await self._handle_menu_delete(message)

            discord.compat.create_task(delete(), loop=self.bot.loop)

    async def send(self, destination):
        message = await self.bot.send_message(destination, self.text)
        await self._process_menu(message)
        return message

    async def say(self):
        message = await self.bot.say(self.text)
        await self._process_menu(message)
        return message
