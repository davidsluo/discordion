import asyncio
import hashlib
import os

import requests
from discord import InvalidArgument, Reaction, Member
from discord.ext import commands
from discord.ext.commands import Context, Bot
from peewee import IntegrityError, CharField, IntegerField
from requests import RequestException

from cogs.utils.database import BaseModel, Server
from cogs.utils.menu import Menu, DefaultEmoji


class Sound(BaseModel):
    name = CharField(unique=True)
    filename = CharField(unique=True)
    volume = IntegerField(default=50)


class Soundboard:
    save_path = os.getcwd() + os.path.abspath('/sounds')

    def __init__(self, bot: Bot):
        self.bot = bot

        try:
            os.mkdir(self.__class__.save_path)
        except FileExistsError:
            pass

        Sound.create_table(fail_silently=True)

        self.play_sound = asyncio.Event()
        self.sound_file = None
        self.volume = None
        self.voice = None

        self.bot.loop.create_task(self.soundboard_task())

    def _get_menu_items(self, server_id):
        emoji = [
            DefaultEmoji.one.value,
            DefaultEmoji.two.value,
            DefaultEmoji.three.value,
            DefaultEmoji.four.value,
            DefaultEmoji.five.value
        ]
        sounds = Sound.select().where(Sound.server == server_id)
        return [(emoji[i % len(emoji)], sound.name) for sound, i in zip(sounds, range(len(sounds)))]

    async def on_menu(self, index: int, reaction: Reaction, member: Member):
        try:
            self.voice = await self.bot.join_voice_channel(member.voice_channel)
        except InvalidArgument:
            await self.bot.say('This is not a voice channel.', delete_after=30)
            return

        # This feels weird
        sound_name = self._get_menu_items(reaction.message.server.id)[index][1]

        sound = Sound.get(Sound.name == sound_name)
        self.volume = sound.volume
        self.sound_file = sound.filename
        self.play_sound.set()

    async def soundboard_task(self):
        while True:
            await self.play_sound.wait()
            player = self.voice.create_ffmpeg_player(Soundboard.save_path + '/' + self.sound_file)
            player.volume = self.volume / 100
            player.start()
            player.join()
            await self.voice.disconnect()
            self.play_sound.clear()

    @commands.group(
        aliases=['sb'],
        pass_context=True,
        invoke_without_command=True
    )
    async def soundboard(self, ctx: Context, name: str = None, volume: int = None):
        """
        Play a sound from the soundboard. 
        Run this command with no arguments to list all available sounds.
        Args:
            name: 
                Optional. 
                The name of the sound to play.
            volume: 
                Optional. 
                The volume (0 to 100) to play the sound.
        """
        # Play `name`
        if name:
            try:
                sound = Sound.get(Sound.server == ctx.message.server.id, Sound.name == name)
            except Sound.DoesNotExist:
                await self.bot.say('Sound `{0}` not found.'.format(name), delete_after=30)
                return

            if volume:
                try:
                    volume = int(volume)
                except ValueError:
                    await self.bot.say('Invalid volume argument: {0}'.format(volume))
                    return
                volume = 100 if volume > 100 else volume
                volume = 0 if volume < 0 else volume
            else:
                volume = sound.volume

            channel = ctx.message.author.voice_channel
            if channel is None:
                await self.bot.say('You are not in a voice channel.')
                return

            try:
                self.voice = await ctx.bot.join_voice_channel(channel)
            except InvalidArgument:
                await self.bot.say('This is not a voice channel.', delete_after=30)
                return

            self.sound_file = sound.filename
            self.volume = volume
            self.play_sound.set()
        # List all sounds.
        else:
            sounds = Sound.select().where(Sound.server == ctx.message.server.id)
            if len(sounds) > 0:
                message = ', '.join(sorted([sound.name for sound in sounds]))
                a = message
            else:
                message = 'No sounds. Add one with !soundboard add.'
            await self.bot.say('Sounds:\n{0}'.format(message))

    @soundboard.command(
        pass_context=True
    )
    async def menu(self, ctx: Context):

        m = Menu(self.bot, self.on_menu, self._get_menu_items(ctx.message.server.id))
        await m.say()

    @soundboard.command(
        name='add',
        aliases=['a'],
        pass_context=True
    )
    async def add(self, ctx: Context, name: str, link: str = None, volume: int = 50):
        """
        Add a new sound to the soundboard.
        Args:
            name: 
                Required. 
                The name of the new sound.
            link: 
                Optional-ish. 
                A link to download the sound. If not specified, 
                this command must be run in the comment of 
                an uploaded audio file.
            volume: 
                Optional. 
                The default volume (0 to 100) for this sound. 
                Defaults to 50.
        """
        if not link:
            try:
                link = ctx.message.attachments[0]['url']
            except (IndexError, KeyError):
                await self.bot.say('Link or upload of sound file required.', delete_after=30)
                return

        await self.bot.type()

        try:
            r = requests.get(link, timeout=3)
        except RequestException:
            await self.bot.say('Malformed link.', delete_after=30)
            return

        if r.status_code != 200:
            await self.bot.say('Error while downloading sound.', delete_after=30)
            return

        filehash = hashlib.sha256(r.content).hexdigest()
        filepath = '{0}/{1}'.format(self.__class__.save_path, filehash)

        volume = 100 if volume > 100 else volume
        volume = 0 if volume < 0 else volume

        sound = Sound(server=Server.get_server(ctx.message.server.id), name=name, filename=filehash, volume=volume)

        try:
            sound.save()
        except IntegrityError as e:
            await self.bot.say('`{0}` already exists.'.format(name), delete_after=30)
            return

        # Save file
        with open(filepath, 'wb') as f:
            f.write(r.content)

        await self.bot.say('Added `{0}`'.format(name))

    @soundboard.command(
        aliases=['d', 'del', 'remove', 'r', 'rm'],
        pass_context=True
    )
    async def delete(self, ctx, name):
        """
        Delete a sound.
        Args:
            name: 
                Required. 
                The sound to delete. 
        """
        try:
            sound = Sound.get(Sound.server == ctx.message.server.id, Sound.name == name)
        except Sound.DoesNotExist:
            await self.bot.say('Sound `{0}` not found.'.format(name), delete_after=30)
            return

        filepath = '{0}/{1}'.format(self.__class__.save_path, sound.filename)
        os.remove(filepath)

        sound.delete_instance()
        await self.bot.say('Removed `{0}`.'.format(name))


def setup(bot):
    bot.add_cog(Soundboard(bot))
