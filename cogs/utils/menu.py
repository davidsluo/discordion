import asyncio
import inspect
from collections import OrderedDict
from enum import Enum
from typing import List, Dict, Tuple

import discord
from discord import User, Reaction, Emoji
from discord.ext.commands import Bot


class DefaultEmoji(Enum):
    left = '\U000025c0'
    one = '\U00000031\U000020e3'
    two = '\U00000032\U000020e3'
    three = '\U00000033\U000020e3'
    four = '\U00000034\U000020e3'
    five = '\U00000035\U000020e3'
    six = '\U00000036\U000020e3'
    seven = '\U00000037\U000020e3'
    eight = '\U00000038\U000020e3'
    nine = '\U00000039\U000020e3'
    zero = '\U00000030\U000020e3'
    right = '\U000025b6'


class Menu:
    active_menus = []

    async def send(self, destination):
        if self._sent:
            raise RuntimeError('Message already sent.')
        start = int(self._page * self.per_page)
        stop = start + self.per_page if start + self.per_page < len(self.menu_items) else len(self.menu_items) - 1
        message_text = '\n'.join(['{0} {1}'.format(emoji, text) for emoji, text in self.menu_items[start:stop]])

        message = await self.bot.send_message(destination, message_text)
        await self._process_menu(message)
        self._sent = True
        return message

    async def say(self):
        if self._sent:
            raise RuntimeError('Message already sent.')
        start = int(self._page * self.per_page)
        stop = start + self.per_page if start + self.per_page < len(self.menu_items) else len(self.menu_items) - 1
        message_text = '\n'.join(['{0} {1}'.format(emoji, text) for emoji, text in self.menu_items[start:stop]])

        message = await self.bot.say(message_text)
        await self._process_menu(message)
        self._sent = True
        return message

    def __init__(self, bot: Bot, callback, menu_items: List[Tuple[Emoji, str]], timeout=0, per_page=5):
        self.bot = bot

        if not inspect.iscoroutinefunction(callback):
            raise ValueError('Callback must be coroutine.')
        self.callback = callback

        self.menu_items = menu_items
        self.timeout = timeout
        self.per_page = per_page

        self._page = 0
        self._last_page = -1
        self._message = None
        self._sent = False

        self.bot.add_listener(self._handle_menu, 'on_reaction_add')

    @property
    def _max_page(self):
        return int(len(self.menu_items) / self.per_page) + 1

    async def _prev_page(self):
        self._last_page = self._page
        self._page = self._page - 1 if self._page - 1 >= 0 else 0
        await self._update_message()

    async def _next_page(self):
        self._last_page = self._page
        self._page = self._page + 1 if self._page + 1 <= self._max_page else self._max_page
        await self._update_message()

    async def _update_message(self):
        # TODO: change this so it doesn't make unnecessary API calls
        if self._page == self._last_page:
            return
        else:
            self.bot.clear_reactions(self._message)

        # if self._page == 0:
        #     await self.bot.remove_reaction(self._message, DefaultEmoji.left.value, self.bot.user)
        # elif self._page == self._max_page:
        #     await self.bot.remove_reaction(self._message, DefaultEmoji.right.value, self.bot.user)
        # else:
        #     await self.bot.add_reaction(self._message, DefaultEmoji.left.value)
        #     await self.bot.add_reaction(self._message, DefaultEmoji.right.value)

        if self._page != 0:
            await self.bot.add_reaction(self._message, DefaultEmoji.left.value)

        start = int(self._page * self.per_page)
        stop = start + self.per_page if start + self.per_page < len(self.menu_items) else len(self.menu_items) - 1
        message_text = '\n'.join(['{0} {1}'.format(emoji, text) for emoji, text in self.menu_items[start:stop]])

        await self.bot.edit_message(self._message, new_content=message_text)

        for emoji, text in self.menu_items[start:stop]:
            await self.bot.add_reaction(self._message, emoji)

        if self._page != self._max_page:
            await self.bot.add_reaction(self._message, DefaultEmoji.right.value)

    async def _handle_menu(self, reaction: Reaction, user: User):
        if user == self.bot.user:
            return
        if reaction.message.id in [menu._message.id for menu in self.active_menus]:
            if reaction.emoji == DefaultEmoji.left.value:
                await self._prev_page()
            elif reaction.emoji == DefaultEmoji.right.value:
                await self._next_page()
            elif reaction.emoji in [emoji for emoji, text in self.menu_items]:
                index = [emoji for emoji, text in self.menu_items].index(reaction.emoji) + self.per_page * self._page
                await self.callback(index, reaction, user)
            else:
                pass

            await asyncio.sleep(0.25)
            await self.bot.remove_reaction(reaction.message, reaction.emoji, user)

    async def _process_menu(self, message):
        self._message = message
        self.active_menus.append(self)
        if self._page != 0:
            await self.bot.add_reaction(self._message, DefaultEmoji.left.value)
        for emoji, text in self.menu_items:
            await self.bot.add_reaction(message, emoji)
        if self._page != self._max_page:
            await self.bot.add_reaction(self._message, DefaultEmoji.right.value)

        if self.timeout > 0:
            async def deactivate():
                await asyncio.sleep(self.timeout, loop=self.bot.loop)
                self.active_menus.remove(self._message)
                for e, t in self.menu_items:
                    await self.bot.remove_reaction(self._message, emoji, self.bot.user)

                discord.compat.create_task(deactivate(), loop=self.bot.loop)
