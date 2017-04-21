import json

from peewee import TextField, Model

from bot import db


class BaseModel(Model):
    class Meta:
        database = db


class ListField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        value = json.loads(value)
        assert type(value) == list
        return value
