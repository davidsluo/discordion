from peewee import CharField

from database.models import BaseModel


class Link(BaseModel):
    name = CharField(unique=True)
    text = CharField()
