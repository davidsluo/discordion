from peewee import CharField, IntegerField

from database.models import BaseModel


class TwitterEcho(BaseModel):
    user_id = IntegerField(unique=True)
    screen_name = CharField(unique=True)
    channel = CharField()
