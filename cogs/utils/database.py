import json

from peewee import TextField, Model, CharField, ForeignKeyField, SqliteDatabase

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Server(BaseModel):
    server_id = CharField(unique=True)

    @classmethod
    def get_server(cls, server_id):
        try:
            s = Server.get(server_id=server_id)
        except Server.DoesNotExist:
            s = Server.create(server_id=server_id)
            s.save()

        return s


class PerServerModel(BaseModel):
    server = ForeignKeyField(Server, null=True, to_field="server_id")


class ListField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        value = json.loads(value)
        assert type(value) == list
        return value
