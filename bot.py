import logging

import yaml
from discord.ext.commands import Bot
from peewee import SqliteDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open('config.yml', 'r') as f:
    config = yaml.load(f)
    logger.info('Loading config from file.')

bot = Bot(command_prefix="!")

bot.config = config
db = SqliteDatabase('database.db')


def load():
    db.connect()
    logger.info('Connecting to database.')

    extensions = config['extensions']

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
    load()
    run()
