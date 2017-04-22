from peewee import CharField, IntegerField

from database.models import BaseModel


class Sound(BaseModel):
    name = CharField(unique=True)
    filename = CharField(unique=True)
    volume = IntegerField(default=50)
