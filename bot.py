import logging
import os
import signal

import sys

import asyncio
import yaml
from discord.ext import commands
from discord.ext.commands import Context, CommandOnCooldown, BucketType

from cogs.utils import database
from cogs.utils.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, command_prefix, config_file, **options):
        super(Bot, self).__init__(command_prefix, **options)

        with open(config_file, 'r') as f:
            logger.info('Loading config from file.')
            self.config = yaml.load(f)

    async def send_message(self, destination, *args, **kwargs):
        # Stolen from `say` for convenience
        # TODO: remove this if transitioning to library rewrite.
        extensions = ('delete_after',)
        params = {
            k: kwargs.pop(k, None) for k in extensions
        }

        return await super(Bot, self).send_message(destination, *args, **kwargs)

    async def on_command_error(self, event, ctx: Context):
        if isinstance(event, CommandOnCooldown):
            cmd_name = ctx.invoked_with
            if event.cooldown.type is BucketType.user:
                cd_type = 'user'
            elif event.cooldown.type is BucketType.channel:
                cd_type = 'channel'
            elif event.cooldown.type is BucketType.server:
                cd_type = 'server'
            elif event.cooldown.type is BucketType.default:
                cd_type = 'global'
            else:
                cd_type = ''

            cd_duration = event.retry_after

            mins, secs = divmod(cd_duration, 60)
            hours, mins = divmod(mins, 60)

            duration_fmt = ('{0} hours '.format(hours) if hours else '',
                            '{0} minutes '.format(mins) if mins or hours else '',
                            '{0:.2f} seconds'.format(secs))

            await self.send_message(ctx.message.channel,
                                    'Command {0} on {1} cooldown. Try again in {2}{3}{4}.'
                                    .format(cmd_name, cd_type, *duration_fmt))
        else:
            super(Bot, self).on_command_error(event, ctx)


bot = Bot(command_prefix='!', config_file='config.yml')


def kill_existing():
    pidfile = '/tmp/discordion.pid'
    pid = os.getpid()

    def handle_exit(signal, stack):
        os.remove(pidfile)
        # Does this work?
        # sys.exit(0)
        bot.loop.call_soon(lambda: bot.loop.create_task(bot.logout()), loop=bot.loop)

    signal.signal(signal.SIGINT, handle_exit)

    if not os.path.isfile(pidfile):
        with open(pidfile, 'w') as f:
            f.write(str(pid))
    else:
        with open(pidfile, 'r') as f:
            pid_other = int(f.read())

        try:
            os.kill(pid_other, 0)
            os.kill(pid_other, signal.SIGINT)
        except OSError:
            os.remove(pidfile)

        while True:
            try:
                os.kill(pid_other, 0)
            except OSError:
                break

        with open(pidfile, 'w') as f:
            f.write(str(pid))


def load():
    db.connect()
    database.Server.create_table(fail_silently=True)
    logger.info('Connecting to database.')

    extensions = bot.config['extensions']

    for ext in extensions:
        try:
            logging.info('Loading extension {0}'.format(ext))
            bot.load_extension(ext)
        except Exception as e:
            logging.error('Failed to load extension {0}\n{1}:{2}'
                          .format(ext, type(e).__name__, e))


def run():
    bot.run(bot.config['discord']['token'])


if __name__ == '__main__':
    # because developing for windows is hard.
    if os.name != 'nt':
        kill_existing()
    load()
    run()
