from peewee import CharField, IntegerField

from cogs.utils.database import BaseModel


class TwitterEcho(BaseModel):
    user_id = IntegerField(unique=True)
    screen_name = CharField(unique=True)
    channel = CharField()
