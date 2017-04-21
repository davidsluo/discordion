from peewee import CharField, TextField, IntegerField

from database.models import ListField, BaseModel


class Sound(BaseModel):
    name = CharField(unique=True)
    filename = CharField(unique=True)
    volume = IntegerField(default=50)
    aliases = ListField(default=[])
    brief = CharField()
    description = TextField()
