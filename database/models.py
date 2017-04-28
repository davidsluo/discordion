import json

from peewee import TextField, Model, CharField, ForeignKeyField

from bot import db


class Server(Model):
    server_id = CharField(unique=True)

    class Meta:
        database = db


class BaseModel(Model):
    server = ForeignKeyField(Server, null=True, to_field=Server.server_id)

    class Meta:
        database = db


class ListField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        value = json.loads(value)
        assert type(value) == list
        return value
