import json

from peewee import Model, CharField, TextField, IntegerField

from bot import db


class ListField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        value = json.loads(value)
        assert type(value) == list
        return value


class Sound(Model):
    class Meta:
        database = db

    name = CharField(unique=True)
    filename = CharField(unique=True)
    volume = IntegerField(default=50)
    aliases = ListField(default=[])
    brief = CharField()
    description = TextField()
