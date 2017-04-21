import argparse
import os
from pathlib import Path

import requests
from discord import InvalidArgument
from discord.ext import commands
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

        for sound in Sound.select():
            self._add_sound_to_bot(sound)

    def _add_sound_to_bot(self, sound):
        @commands.command(
            pass_context=True,
            no_pm=True,
            name=sound.name,
            aliases=sound.aliases,
            brief=sound.brief,
            description=sound.description
        )
        # Might need to pass self as first argument here
        async def play_sound(ctx, volume=sound.volume):
            channel = ctx.message.author.voice.voice_channel
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
                    pass

        # is this line necessary?
        # play_sound.instance = self
        self.bot.add_command(play_sound)

    def _remove_sound_from_bot(self, sound):
        removed = self.bot.remove_command(sound.name)
        sound.delete_instance()
        return removed

    @commands.group(
        description='Interact with the soundboard',
        brief='Rick Roll on demand',
        aliases=['sb']
    )
    async def soundboard(self):
        pass

    @soundboard.command(
        name='add',
        brief='Add a new sound.',
        description='Add a new sound to the soundboard.',
        aliases=['a'],
        help="""
            -name (-n)
            Required
            The name of the command to register the new sound under. Must be one word. Cannot be the same as an already existing command.
            
            -linker (-l)
            Required
            The linker to the audio file to be played. If not specified, then this command must be called through a comment on a file upload to discord.
            
            -description (-desc, -d)
            Optional
            A description of what the audio file is.
            
            -brief (-b)
            Optional
            A shorter description to be shown on the help page for the Soundboard. If not specified, the first line of the description will be used.
            
            -volume (-v)
            Optional
            The default volume (from 0 to 100) to play this sound at. Defaults to 50%.
            """,
        pass_context=True
    )
    async def add(self, ctx, *args):

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-name', '-n')
        parser.add_argument('-linker', '-l')
        parser.add_argument('-description', '-desc', '-d')
        parser.add_argument('-brief', '-b')
        parser.add_argument('-volume', '-v', type=int)
        parser.add_argument('-aliases', '-a', type=list)
        parsed = vars(parser.parse_args(args=args))

        if not parsed['linker']:
            try:
                parsed['linker'] = ctx.message.attachments[0]['url']
            except (IndexError, KeyError):
                await self.bot.say('Link or upload of sound file required.', delete_after=30)
                return

        if not parsed['name']:
            await self.bot.say('Link of sound required.', delete_after=30)
            return

        self.bot.type()

        try:
            r = requests.get(parsed['linker'], timeout=3)
        except RequestException:
            await self.bot.say('Malformed linker', delete_after=30)
            return

        if r.status_code != 200:
            await self.bot.say('Error while downloading sound.', delete_after=30)
            return

        filename = r.url.split('/')[-1]
        filepath = '{0}/{1}'.format(self.__class__.save_path, filename)

        # Check if filename already exists. Appends underscore to filename until filename is unique.
        # TODO: change this to generate random filenames
        # TODO: save hashes of files to database?
        # TODO: check if command already exists?
        while True:
            if Path(filepath).is_file():
                components = filepath.split('.')
                extension = components.pop(-1)
                name = '.'.join(components)

                filepath = '{0}_.{1}'.format(name, extension)
            else:
                break

        # Save file
        with open(filepath, 'wb') as f:
            f.write(r.content)

        # TODO: not hard code default values
        # TODO: check for uniqueness.
        sound = Sound(name=parsed['name'], filename=filename, volume=parsed['volume'] or 50,
                      aliases=parsed['aliases'] or [], brief=parsed['brief'] or '',
                      description=parsed['description'] or '')

        sound.save()

        self._add_sound_to_bot(sound)

        await self.bot.say('Added {0}'.format(parsed['name']))

    @soundboard.command(
        name='remove',
        description='Remove a sound from the soundboard.',
        brief='Remove a sound',
        pass_context=True
    )
    async def remove_sound(self, ctx, name):
        try:
            sound = Sound.get(Sound.name == name)
        except Sound.DoesNotExist:
            await self.bot.say('Sound {0} not found.'.format(name), delete_after=30)
            return

        self._remove_sound_from_bot(sound)
        await self.bot.say('Removed {0}.'.format(name))


def setup(bot):
    bot.add_cog(Soundboard(bot))
