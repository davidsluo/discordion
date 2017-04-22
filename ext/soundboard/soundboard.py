import hashlib
import os

import requests
from discord import InvalidArgument
from discord.ext import commands
from discord.ext.commands import Context
from peewee import IntegrityError
from requests import RequestException

from ext.soundboard.models import Sound


class Soundboard:
    save_path = os.getcwd() + os.path.abspath('/sounds')

    def __init__(self, bot):
        self.bot = bot

        try:
            os.mkdir(self.__class__.save_path)
        except FileExistsError:
            pass

        Sound.create_table(fail_silently=True)

    @commands.group(
        description='Interact with the soundboard.',
        brief='Rick Roll on demand.',
        aliases=['sb'],
        pass_context=True,
        invoke_without_command=True
    )
    async def soundboard(self, ctx: Context, name: str = None, volume: int = None):
        """
        Play a sound from the soundboard. Run this command with no arguments to list all available sounds.
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
                sound = Sound.get(Sound.name == name)
            except Sound.DoesNotExist:
                await self.bot.say('Sound `{0}` not found.'.format(name), delete_after=30)
                return

            channel = ctx.message.author.voice.voice_channel

            if volume:
                try:
                    volume = int(volume)
                    volume = 100 if volume > 100 else volume
                    volume = 0 if volume < 0 else volume
                except ValueError:
                    await self.bot.say('Invalid volume argument: {0}'.format(volume))
                    return
            else:
                volume = sound.volume

            if channel:
                try:
                    client = await ctx.bot.join_voice_channel(channel)

                    player = client.create_ffmpeg_player(Soundboard.save_path + '/' + sound.filename)

                    player.volume = volume / 100

                    player.start()
                    player.join()

                    await client.disconnect()
                except InvalidArgument:
                    # if join_voice_channel fails.
                    # TODO: add feedback here?
                    pass
        # List all sounds.
        else:
            sounds = Sound.select()
            message = ', '.join(sorted([sound.name for sound in sounds]))
            await self.bot.say('Sounds:')
            await self.bot.say(message)

    @soundboard.command(
        name='add',
        brief='Add a new sound.',
        description='Add a new sound to the soundboard.',
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

        sound = Sound(name=name, filename=filehash, volume=volume)

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
        description='Remove a sound from the soundboard.',
        brief='Delete a sound.',
        aliases=['d', 'del', 'remove', 'r', 'rm']
    )
    async def delete(self, name):
        """
        Delete a sound.
        Args:
            name: Required. The sound to delete. 
        """
        try:
            sound = Sound.get(Sound.name == name)
        except Sound.DoesNotExist:
            await self.bot.say('Sound `{0}` not found.'.format(name), delete_after=30)
            return

        filepath = '{0}/{1}'.format(self.__class__.save_path, sound.filename)
        os.remove(filepath)

        sound.delete_instance()
        await self.bot.say('Removed `{0}`.'.format(name))


def setup(bot):
    bot.add_cog(Soundboard(bot))
