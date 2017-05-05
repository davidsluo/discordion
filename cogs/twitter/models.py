from peewee import CharField, IntegerField

from cogs.utils.database import PerServerModel


class TwitterEcho(PerServerModel):
    user_id = IntegerField(unique=True)
    screen_name = CharField(unique=True)
    channel = CharField()
